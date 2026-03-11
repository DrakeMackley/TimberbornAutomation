# Timberborn Automation

Smart automation companion for Timberborn — augmenting colony management through the game's HTTP API.

## Vision

Two pillars:
1. **Smart Automation** — an event-driven controller that reacts to in-game sensor webhooks and toggles levers to handle complex multi-condition logic that's painful to wire with in-game gates alone.
2. **Colony Dashboard** — a web dashboard that displays real-time colony status, manual lever control, and automation event history.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        TIMBERBORN                                 │
│                                                                   │
│  Sensors ──→ In-Game Logic ──→ Actuators                          │
│    │              │                │                               │
│    ▼              ▼                ▼                               │
│  HTTP Adapters  Relays/Timers   HTTP Levers                       │
│  (state out)    (simple rules)  (control in)                      │
└────┬──────────────────────────────────┬──────────────────────────┘
     │           localhost:8080          │
     │                                   │
     │ WEBHOOK (adapter state changes)   │ API (lever control)
     ▼                                   ▲
┌────────────────────────────────────────────────────────────────┐
│              AUTOMATION CONTROLLER (port 8081)                   │
│                                                                  │
│  • Receives webhook events when adapters change                 │
│  • Evaluates complex AND/OR rule conditions                      │
│  • Triggers levers instantly (no polling delay)                  │
│  • Maintains state + event log                                   │
│  • Exposes /api/state and /api/events for dashboard              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ HTTP (state/events API)
                     ▼
┌────────────────────────────────────────────────────────────────┐
│              WEB DASHBOARD (localhost:8000)                      │
│                                                                  │
│  • Polls controller for state + events (rich data)               │
│  • Falls back to game API if controller offline                  │
│  • Displays adapters, levers, and automation event feed          │
│  • Manual lever control                                          │
└────────────────────────────────────────────────────────────────┘
```

## Event-Driven Architecture

**The Game Pushes Events to the Controller**

Timberborn's HTTP Adapters aren't just passive state endpoints — they actively **push webhook calls** when their signal changes. In the in-game adapter configuration UI, you set:

- **"Call when switched on"** → `http://localhost:8081/on/{adapter_name}`
- **"Call when switched off"** → `http://localhost:8081/off/{adapter_name}`
- **HTTP method:** GET or POST (both supported)

When an adapter's state changes, the game immediately notifies the controller. The controller updates its internal state and runs the rules engine — no polling delay, instant reaction.

### Operating Modes

The controller supports three modes:

1. **`webhook`** (recommended) — Pure event-driven. Controller waits for adapter webhook calls. Fastest response time.
2. **`polling`** — Traditional polling of `/api/adapters` every N seconds. Use if you don't want to configure webhooks on every adapter.
3. **`hybrid`** — Webhook primary + periodic polling for state sync. Best of both worlds.

Configure via `mode:` in `config.yaml`.

## Game API

Timberborn exposes a local API at `http://localhost:8080`:

- `GET /api/levers` — list all HTTP Levers
- `GET /api/levers/{name}` — get lever state
- `GET|POST /api/switch-on/{name}` — activate lever
- `GET|POST /api/switch-off/{name}` — deactivate lever
- `GET /api/color/{name}/{RRGGBB}` — set lever color
- `GET /api/adapters` — list all HTTP Adapters
- `GET /api/adapters/{name}` — get adapter state

Names must be URL-encoded (e.g., `HTTP%20Lever%201`).

API binds to localhost only. For remote access, use a tunnel (ngrok, cloudflare, etc.).

## In-Game Sensor Catalog

All sensors output binary signals (on/off based on player-defined thresholds):

| Sensor | Measures |
|--------|----------|
| Depth Sensor | Water level at a point (>, < threshold) |
| Flow Sensor | Water movement |
| Contamination Sensor | Badwater presence |
| Time Sensor | Time of day / season |
| Weather Sensor | Drought active/inactive |
| Power Sensor | Grid status |
| Population Counter | Beaver count vs threshold |
| Resource Counter | Stock level or storage fill % vs threshold (per resource) |
| Science Sensor | Research status |

## In-Game Logic Components

- **Relays:** Passthrough, NOT, AND, OR, XOR
- **Memory:** Set/Reset, Toggle, Latch, Flip-Flop
- **Timers:** Pulse, Accumulator, Delay, Oscillator

## Actuatable Buildings

All workplaces, housing, power generators/consumers, gates, fill valves, and throttling valves support automation on/off.

## Components

### 1. [Controller](controller/) — Smart Automation Engine
Python-based rules engine that processes webhook events from HTTP Adapters and triggers HTTP Levers based on complex multi-condition logic.

**Features:**
- Event-driven webhook server (instant reaction)
- Polling fallback mode
- Config-driven YAML rules
- AND/OR condition logic
- Auto-retry when game offline
- Event history tracking
- State API for dashboard integration
- Zero-crash operation

[→ Controller Documentation](controller/README.md)

### 2. [Dashboard](dashboard/) — Colony Status Monitor
Browser-based real-time monitoring dashboard with manual lever control and automation event feed.

**Features:**
- Live adapter state monitoring
- Manual lever toggles
- Automation event history (when controller is connected)
- Dual-source data: controller (rich) or game API (fallback)
- Filter/search by name
- Connection status indicators (game + controller)
- Pause/resume polling
- Pure HTML/CSS/JS (no build step)

[→ Dashboard Documentation](dashboard/README.md)

## Quick Start

### Prerequisites
- Timberborn with HTTP API mod installed and enabled
- Python 3.7+ (for controller)
- Any modern browser (for dashboard)

### Controller Setup

1. **Install dependencies:**
   ```bash
   cd controller
   pip3 install -r requirements.txt
   ```

2. **Create your config:**
   ```bash
   cp config.example.yaml config.yaml
   ```

3. **Edit `config.yaml`:**
   - Set `mode: "webhook"` (or `"polling"` / `"hybrid"`)
   - Configure your automation rules (match in-game adapter/lever names)

4. **Run:**
   ```bash
   python3 controller.py
   ```

   The controller will log webhook URLs to configure in-game:
   ```
   Configure in-game adapters to call:
     ON:  http://localhost:8081/on/{adapter_name}
     OFF: http://localhost:8081/off/{adapter_name}
   ```

### In-Game Webhook Configuration

For each HTTP Adapter you want to automate:

1. Open the adapter's configuration panel
2. Set **"Call when switched on"** to: `http://localhost:8081/on/{YourAdapterName}`
3. Set **"Call when switched off"** to: `http://localhost:8081/off/{YourAdapterName}`
4. Choose GET or POST method (both work)
5. Replace `{YourAdapterName}` with the actual adapter name (e.g., `Weather Drought`)

The adapter name in the URL should match the name you use in your `config.yaml` rules.

### Dashboard Setup

1. **Start a web server:**
   ```bash
   cd dashboard
   python3 -m http.server 8000
   ```

2. **Open in browser:**
   ```
   http://localhost:8000
   ```

3. **Configure URLs (optional):**
   - Game API URL: `http://localhost:8080` (default)
   - Controller URL: `http://localhost:8081` (default)

The dashboard will:
- Show adapter/lever state from the controller (if running)
- Fall back to direct game API polling if controller is offline
- Display automation event history (controller only)

## Configuration

### Controller Rules

Rules define automation logic. Each rule has:
- **name** — descriptive label for logging
- **conditions** — adapter checks with AND/OR operator
- **actions** — levers to trigger when conditions match

Example:
```yaml
mode: "webhook"  # or "polling" or "hybrid"
webhook_port: 8081
game_api_url: http://localhost:8080
polling_interval_seconds: 5  # used in polling/hybrid mode

rules:
  - name: "Drought Emergency Response"
    conditions:
      operator: AND
      checks:
        - adapter: "Weather Drought"
          state: true
        - adapter: "Water Depth Critical"
          state: true
    actions:
      - lever: "Emergency Pumps"
        action: "on"
      - lever: "Floodgate Main"
        action: "off"

  - name: "Crisis Resolved"
    conditions:
      operator: AND
      checks:
        - adapter: "Weather Drought"
          state: false
        - adapter: "Water Depth Critical"
          state: false
    actions:
      - lever: "Emergency Pumps"
        action: "off"
      - lever: "Floodgate Main"
        action: "on"
```

See [config.example.yaml](controller/config.example.yaml) for more examples.

### Operating Mode Comparison

| Mode | Latency | Setup Effort | Use Case |
|------|---------|--------------|----------|
| **webhook** | Instant | Configure webhook URLs on each adapter | Best for real-time automation |
| **polling** | 5s (configurable) | Zero in-game config | Quick testing, simple setups |
| **hybrid** | Instant (webhook) + periodic sync | Configure webhooks | Redundancy + state recovery |

### Dashboard Customization

The dashboard auto-detects controller availability:
- **Controller connected:** Shows adapter/lever state + rich event history
- **Controller offline:** Falls back to direct game API polling

Edit the URL fields in the dashboard UI to change endpoints (saved to browser localStorage).

## Troubleshooting

### Webhooks Not Working
- Check controller logs for incoming webhook calls
- Verify adapter webhook URLs match controller endpoint (case-sensitive names)
- Ensure no firewall blocking port 8081
- Test with a browser: `http://localhost:8081/on/TestAdapter` (should return `{"status":"ok"}`)

### Controller Can't Reach Game
- Verify game is running and HTTP API is enabled
- Check `game_api_url` in config matches game's API endpoint
- Test manually: `curl http://localhost:8080/api/adapters`

### Dashboard Shows "Disconnected"
- Verify URLs in dashboard config panel
- Check browser console for CORS errors
- If controller offline, dashboard falls back to game API (this is normal)

### Port Already in Use
- Another process is using port 8081
- Change `webhook_port` in config.yaml
- Update in-game webhook URLs to match new port

## Advanced Usage

### Remote Access
The game API binds to localhost only. For remote dashboard/control:

1. Use SSH tunnel: `ssh -L 8080:localhost:8080 game-server`
2. Or reverse proxy (nginx, caddy) with proper security
3. Or ngrok/cloudflare tunnel (exposes publicly — secure it!)

### Event History API
The controller exposes event data:

- `GET /api/state` — current adapter/lever state + last 20 events
- `GET /api/events?limit=100` — event history (default 50, max determined by controller's maxlen)

Use these for custom dashboards or integrations.

### Multiple Controllers
Run multiple controllers for different rule sets:
```bash
python3 controller.py --config water-rules.yaml
python3 controller.py --config power-rules.yaml
```

Use different `webhook_port` values and configure adapter webhooks accordingly.

## License

MIT
