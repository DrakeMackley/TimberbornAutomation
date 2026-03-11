#!/usr/bin/env python3
"""
Timberborn Automation Controller

Reads HTTP Adapters (sensors) and triggers HTTP Levers (actuators)
based on configurable rules with AND/OR conditions.
"""

import time
import logging
import sys
from urllib.parse import quote
from typing import Dict, List, Any
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


class TimberbornController:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the controller with a config file."""
        self.config = self._load_config(config_path)
        self.api_base = self.config.get('api_base', 'http://localhost:8080')
        self.polling_interval = self.config.get('polling_interval_seconds', 2)
        self.rules = self.config.get('rules', [])
        self.last_adapter_state: Dict[str, bool] = {}
        self.last_lever_state: Dict[str, bool] = {}
        
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
    
    def _get_adapters(self) -> List[Dict[str, Any]]:
        """Fetch current adapter states from the game API."""
        try:
            response = requests.get(f"{self.api_base}/api/adapters", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.debug(f"Failed to fetch adapters: {e}")
            return []
    
    def _get_levers(self) -> List[Dict[str, Any]]:
        """Fetch current lever states from the game API."""
        try:
            response = requests.get(f"{self.api_base}/api/levers", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.debug(f"Failed to fetch levers: {e}")
            return []
    
    def _trigger_lever(self, lever_name: str, action: str) -> bool:
        """Trigger a lever action (on/off)."""
        encoded_name = quote(lever_name)
        endpoint = f"switch-{action}"
        url = f"{self.api_base}/api/{endpoint}/{encoded_name}"
        
        try:
            response = requests.post(url, timeout=5)
            response.raise_for_status()
            logger.info(f"✓ Lever '{lever_name}' switched {action.upper()}")
            return True
        except requests.RequestException as e:
            logger.warning(f"Failed to trigger lever '{lever_name}': {e}")
            return False
    
    def _evaluate_conditions(self, conditions: dict, adapter_states: Dict[str, bool]) -> bool:
        """Evaluate rule conditions against current adapter states."""
        checks = conditions.get('checks', [])
        operator = conditions.get('operator', 'OR').upper()
        
        if not checks:
            return False
        
        results = []
        for check in checks:
            adapter_name = check.get('adapter')
            expected_state = check.get('state', True)
            
            # Get current state (default to False if adapter not found)
            current_state = adapter_states.get(adapter_name, False)
            results.append(current_state == expected_state)
        
        if operator == 'AND':
            return all(results)
        else:  # OR
            return any(results)
    
    def _process_rules(self, adapter_states: Dict[str, bool]):
        """Process all rules and trigger actions as needed."""
        for rule in self.rules:
            rule_name = rule.get('name', 'Unnamed Rule')
            conditions = rule.get('conditions', {})
            actions = rule.get('actions', [])
            
            if self._evaluate_conditions(conditions, adapter_states):
                logger.info(f"⚡ Rule triggered: {rule_name}")
                
                for action in actions:
                    lever_name = action.get('lever')
                    lever_action = action.get('action', 'on')
                    
                    if lever_name:
                        self._trigger_lever(lever_name, lever_action)
    
    def run(self):
        """Main control loop."""
        logger.info("🚀 Timberborn Controller starting...")
        logger.info(f"Polling interval: {self.polling_interval}s")
        logger.info(f"Loaded {len(self.rules)} rules")
        
        connection_lost = False
        
        while True:
            try:
                # Fetch current adapter states
                adapters = self._get_adapters()
                
                if not adapters and not connection_lost:
                    logger.warning("⚠️  Game not reachable - waiting for connection...")
                    connection_lost = True
                    time.sleep(self.polling_interval * 2)
                    continue
                
                if adapters and connection_lost:
                    logger.info("✓ Connection restored")
                    connection_lost = False
                
                # Build state dictionary
                adapter_states = {a['name']: a['state'] for a in adapters}
                
                # Log state changes
                for name, state in adapter_states.items():
                    if name not in self.last_adapter_state:
                        logger.debug(f"Adapter detected: {name} = {state}")
                    elif self.last_adapter_state[name] != state:
                        logger.info(f"📊 Adapter changed: {name} = {state}")
                
                self.last_adapter_state = adapter_states
                
                # Process rules
                self._process_rules(adapter_states)
                
                # Sleep until next poll
                time.sleep(self.polling_interval)
                
            except KeyboardInterrupt:
                logger.info("\n👋 Controller shutting down...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                time.sleep(self.polling_interval * 2)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Timberborn Automation Controller')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    args = parser.parse_args()
    
    controller = TimberbornController(args.config)
    controller.run()
