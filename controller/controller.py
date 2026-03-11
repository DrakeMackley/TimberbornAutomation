#!/usr/bin/env python3
"""
Timberborn Automation Controller

Event-driven automation that reacts to HTTP Adapter webhooks
and toggles HTTP Levers based on configurable rules.
"""

import time
import logging
import sys
import json
import threading
from urllib.parse import quote, unquote
from typing import Dict, List, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import deque
import yaml
import requests


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('controller.log')
    ]
)
logger = logging.getLogger(__name__)


class AutomationEvent:
    """Represents an automation event for logging/display."""
    def __init__(self, event_type: str, name: str, state: bool = None, details: str = None):
        self.timestamp = time.time()
        self.type = event_type  # "adapter", "lever", "rule"
        self.name = name
        self.state = state
        self.details = details
    
    def to_dict(self):
        from datetime import datetime
        event_dict = {
            "type": self.type,
            "name": self.name,
            "timestamp": datetime.fromtimestamp(self.timestamp).isoformat() + 'Z'
        }
        
        if self.type == "adapter":
            event_dict["state"] = self.state
        elif self.type == "rule":
            event_dict["triggered"] = bool(self.state)
        elif self.type == "lever":
            event_dict["action"] = "on" if self.state else "off"
        
        return event_dict


class TimberbornController:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the controller with a config file."""
        self.config = self._load_config(config_path)
        self.mode = self.config.get('mode', 'webhook')
        self.api_base = self.config.get('game_api_url', 'http://localhost:8080')
        self.webhook_port = self.config.get('webhook_port', 8081)
        self.polling_interval = self.config.get('polling_interval_seconds', 5)
        self.rules = self.config.get('rules', [])
        
        # State tracking
        self.adapter_states: Dict[str, dict] = {}  # {name: {state: bool, last_changed: timestamp}}
        self.lever_states: Dict[str, dict] = {}    # {name: {state: bool, last_changed: timestamp}}
        self.events = deque(maxlen=100)  # Keep last 100 events
        self.state_lock = threading.Lock()
        
        # Statistics
        self.start_time = time.time()
        self.rules_evaluated_count = 0
        self.actions_fired_count = 0
        
        # Server reference
        self.http_server = None
        self.server_thread = None
        
    def _load_config(self, path: str) -> dict:
        """Load YAML configuration file."""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in config: {e}")
            sys.exit(1)
    
    def _log_event(self, event: AutomationEvent):
        """Log and store an event."""
        with self.state_lock:
            self.events.append(event)
    
    def _get_adapters_from_api(self) -> List[Dict[str, Any]]:
        """Fetch current adapter states from the game API."""
        try:
            response = requests.get(f"{self.api_base}/api/adapters", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.debug(f"Failed to fetch adapters: {e}")
            return []
    
    def _get_levers_from_api(self) -> List[Dict[str, Any]]:
        """Fetch current lever states from the game API."""
        try:
            response = requests.get(f"{self.api_base}/api/levers", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.debug(f"Failed to fetch levers: {e}")
            return []
    
    def _sync_state_from_api(self):
        """Sync adapter and lever states from game API."""
        adapters = self._get_adapters_from_api()
        levers = self._get_levers_from_api()
        
        now = time.time()
        with self.state_lock:
            if adapters:
                for a in adapters:
                    # Preserve last_changed if state hasn't changed
                    if a['name'] in self.adapter_states and self.adapter_states[a['name']]['state'] == a['state']:
                        continue
                    self.adapter_states[a['name']] = {
                        'state': a['state'],
                        'last_changed': now
                    }
                logger.info(f"Synced {len(adapters)} adapters from API")
            
            if levers:
                for l in levers:
                    if l['name'] in self.lever_states and self.lever_states[l['name']]['state'] == l['state']:
                        continue
                    self.lever_states[l['name']] = {
                        'state': l['state'],
                        'last_changed': now
                    }
                logger.info(f"Synced {len(levers)} levers from API")
    
    def _trigger_lever(self, lever_name: str, action: str) -> bool:
        """Trigger a lever action (on/off)."""
        encoded_name = quote(lever_name)
        endpoint = f"switch-{action}"
        url = f"{self.api_base}/api/{endpoint}/{encoded_name}"
        
        try:
            response = requests.post(url, timeout=5)
            response.raise_for_status()
            
            # Update local state
            new_state = (action == "on")
            now = time.time()
            with self.state_lock:
                self.lever_states[lever_name] = {
                    'state': new_state,
                    'last_changed': now
                }
                self.actions_fired_count += 1
            
            logger.info(f"✓ Lever '{lever_name}' switched {action.upper()}")
            
            # Log event
            event = AutomationEvent("lever", lever_name, new_state, f"Toggled {action}")
            self._log_event(event)
            
            return True
        except requests.RequestException as e:
            logger.warning(f"Failed to trigger lever '{lever_name}': {e}")
            return False
    
    def _evaluate_conditions(self, conditions: dict) -> bool:
        """Evaluate rule conditions against current adapter states."""
        checks = conditions.get('checks', [])
        operator = conditions.get('operator', 'OR').upper()
        
        if not checks:
            return False
        
        results = []
        with self.state_lock:
            for check in checks:
                adapter_name = check.get('adapter')
                expected_state = check.get('state', True)
                adapter_data = self.adapter_states.get(adapter_name, {'state': False})
                current_state = adapter_data.get('state', False)
                results.append(current_state == expected_state)
        
        if operator == 'AND':
            return all(results)
        else:  # OR
            return any(results)
    
    def _process_rules(self):
        """Process all rules and trigger actions as needed."""
        with self.state_lock:
            self.rules_evaluated_count += len(self.rules)
        
        for rule in self.rules:
            rule_name = rule.get('name', 'Unnamed Rule')
            conditions = rule.get('conditions', {})
            actions = rule.get('actions', [])
            
            if self._evaluate_conditions(conditions):
                logger.info(f"⚡ Rule triggered: {rule_name}")
                
                # Log rule event
                event = AutomationEvent("rule", rule_name, True, "Conditions met")
                self._log_event(event)
                
                for action in actions:
                    lever_name = action.get('lever')
                    lever_action = action.get('action', 'on')
                    
                    if lever_name:
                        self._trigger_lever(lever_name, lever_action)
    
    def update_adapter_state(self, adapter_name: str, new_state: bool):
        """Update adapter state and process rules."""
        old_data = self.adapter_states.get(adapter_name)
        old_state = old_data.get('state') if old_data else None
        
        now = time.time()
        with self.state_lock:
            self.adapter_states[adapter_name] = {
                'state': new_state,
                'last_changed': now
            }
        
        # Log state change
        if old_state != new_state or old_state is None:
            logger.info(f"📊 Adapter updated: {adapter_name} = {new_state}")
            event = AutomationEvent("adapter", adapter_name, new_state, 
                                   f"Changed from {old_state} to {new_state}")
            self._log_event(event)
        
        # Process rules with new state
        self._process_rules()
    
    def get_state_snapshot(self) -> dict:
        """Get current system state for API queries."""
        from datetime import datetime
        
        with self.state_lock:
            # Convert adapter states to spec format
            adapters_dict = {}
            for name, data in self.adapter_states.items():
                adapters_dict[name] = {
                    "state": data['state'],
                    "last_changed": datetime.fromtimestamp(data['last_changed']).isoformat() + 'Z'
                }
            
            # Convert lever states to spec format
            levers_dict = {}
            for name, data in self.lever_states.items():
                levers_dict[name] = {
                    "state": data['state'],
                    "last_changed": datetime.fromtimestamp(data['last_changed']).isoformat() + 'Z'
                }
            
            return {
                "adapters": adapters_dict,
                "levers": levers_dict,
                "events": [e.to_dict() for e in list(self.events)[-20:]],  # Last 20 events
                "mode": self.mode,
                "uptime_seconds": int(time.time() - self.start_time),
                "rules_evaluated": self.rules_evaluated_count,
                "actions_fired": self.actions_fired_count
            }
    
    def get_events(self, limit: int = 50) -> dict:
        """Get recent events."""
        with self.state_lock:
            events_list = list(self.events)
            total = len(events_list)
            recent_events = events_list[-limit:]
            return {
                "events": [e.to_dict() for e in recent_events],
                "total_stored": total,
                "returned": len(recent_events)
            }
    
    def run_webhook_server(self):
        """Run webhook server to receive adapter events."""
        controller = self
        
        class WebhookHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                """Suppress default HTTP logging."""
                pass
            
            def _send_json_response(self, data: dict, status: int = 200):
                """Send JSON response."""
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            
            def do_OPTIONS(self):
                """Handle CORS preflight."""
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
            
            def do_GET(self):
                """Handle GET requests."""
                self._handle_request()
            
            def do_POST(self):
                """Handle POST requests."""
                self._handle_request()
            
            def _handle_request(self):
                """Handle webhook calls and API queries."""
                from datetime import datetime
                path = self.path
                
                # Adapter webhooks: /on/{name} or /off/{name}
                if path.startswith('/on/'):
                    adapter_name = unquote(path[4:])
                    controller.update_adapter_state(adapter_name, True)
                    self._send_json_response({
                        "status": "ok",
                        "adapter": adapter_name,
                        "state": True,
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    })
                    return
                
                elif path.startswith('/off/'):
                    adapter_name = unquote(path[5:])
                    controller.update_adapter_state(adapter_name, False)
                    self._send_json_response({
                        "status": "ok",
                        "adapter": adapter_name,
                        "state": False,
                        "timestamp": datetime.utcnow().isoformat() + 'Z'
                    })
                    return
                
                # State API: /api/state
                elif path == '/api/state':
                    state = controller.get_state_snapshot()
                    self._send_json_response(state)
                    return
                
                # Events API: /api/events or /api/events?limit=N
                elif path.startswith('/api/events'):
                    limit = 50
                    if '?limit=' in path:
                        try:
                            limit = int(path.split('?limit=')[1].split('&')[0])
                        except (ValueError, IndexError):
                            pass
                    
                    events_data = controller.get_events(limit)
                    self._send_json_response(events_data)
                    return
                
                # Health check
                elif path == '/health':
                    # Check if game is reachable
                    game_reachable = False
                    try:
                        response = requests.get(f"{controller.api_base}/api/adapters", timeout=2)
                        game_reachable = response.status_code == 200
                    except Exception:
                        pass
                    
                    health_status = "healthy" if game_reachable or controller.mode == "webhook" else "degraded"
                    status_code = 200 if health_status == "healthy" else 503
                    
                    self._send_json_response({
                        "status": health_status,
                        "mode": controller.mode,
                        "uptime_seconds": int(time.time() - controller.start_time),
                        "game_reachable": game_reachable,
                        "adapters_tracked": len(controller.adapter_states),
                        "levers_tracked": len(controller.lever_states),
                        "rules_loaded": len(controller.rules)
                    }, status=status_code)
                    return
                
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b'Not Found')
        
        try:
            self.http_server = HTTPServer(('0.0.0.0', self.webhook_port), WebhookHandler)
            logger.info(f"🌐 Webhook server listening on port {self.webhook_port}")
            logger.info(f"Configure in-game adapters to call:")
            logger.info(f"  ON:  http://localhost:{self.webhook_port}/on/{{adapter_name}}")
            logger.info(f"  OFF: http://localhost:{self.webhook_port}/off/{{adapter_name}}")
            self.http_server.serve_forever()
        except OSError as e:
            logger.error(f"Failed to start webhook server: {e}")
            logger.error(f"Port {self.webhook_port} may already be in use")
            sys.exit(1)
    
    def run_polling_loop(self):
        """Run polling loop for adapter state sync."""
        logger.info(f"🔄 Polling mode active (interval: {self.polling_interval}s)")
        connection_lost = False
        
        while True:
            try:
                # Fetch current adapter states
                adapters = self._get_adapters_from_api()
                
                if not adapters and not connection_lost:
                    logger.warning("⚠️  Game not reachable - waiting for connection...")
                    connection_lost = True
                    time.sleep(self.polling_interval * 2)
                    continue
                
                if adapters and connection_lost:
                    logger.info("✓ Connection restored")
                    connection_lost = False
                
                # Update adapter states
                for adapter in adapters:
                    self.update_adapter_state(adapter['name'], adapter['state'])
                
                # Sync lever states
                levers = self._get_levers_from_api()
                if levers:
                    now = time.time()
                    with self.state_lock:
                        for l in levers:
                            if l['name'] in self.lever_states and self.lever_states[l['name']]['state'] == l['state']:
                                continue
                            self.lever_states[l['name']] = {
                                'state': l['state'],
                                'last_changed': now
                            }
                
                # Sleep until next poll
                time.sleep(self.polling_interval)
                
            except Exception as e:
                logger.error(f"Polling error: {e}", exc_info=True)
                time.sleep(self.polling_interval * 2)
    
    def run(self):
        """Main controller entry point."""
        logger.info("🚀 Timberborn Controller starting...")
        logger.info(f"Mode: {self.mode}")
        logger.info(f"Loaded {len(self.rules)} rules")
        
        # Initial state sync from API
        logger.info("Syncing initial state from game API...")
        self._sync_state_from_api()
        
        try:
            if self.mode == 'webhook':
                # Webhook-only mode
                self.run_webhook_server()
            
            elif self.mode == 'polling':
                # Polling-only mode
                self.run_polling_loop()
            
            elif self.mode == 'hybrid':
                # Both webhook and polling
                # Start webhook server in background thread
                self.server_thread = threading.Thread(target=self.run_webhook_server, daemon=True)
                self.server_thread.start()
                
                # Run polling in main thread
                self.run_polling_loop()
            
            else:
                logger.error(f"Invalid mode: {self.mode}. Use 'webhook', 'polling', or 'hybrid'")
                sys.exit(1)
        
        except KeyboardInterrupt:
            logger.info("\n👋 Controller shutting down...")
            if self.http_server:
                self.http_server.shutdown()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Timberborn Automation Controller')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    args = parser.parse_args()
    
    controller = TimberbornController(args.config)
    controller.run()
