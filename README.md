# Timberborn Automation

Smart automation companion for Timberborn — augmenting colony management through the game's HTTP API.

## Vision

Two pillars:
1. **Smart Automation** — an external controller that reads in-game sensor state (via HTTP Adapters) and toggles levers (via HTTP Levers) to handle complex multi-condition logic that's painful to wire with in-game gates alone.
2. **Colony Dashboard** — a web dashboard that polls adapter state and renders colony status at a glance: food, water, materials, power, population.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  TIMBERBORN                       │
│                                                   │
│  Sensors ──→ In-Game Logic ──→ Actuators          │
│    │              │                │               │
│    ▼              ▼                ▼               │
│  HTTP Adapters  Relays/Timers   HTTP Levers       │
│  (state out)    (simple rules)  (control in)      │
└────┬──────────────────────────────────┬───────────┘
     │           localhost:8080          │
     ▼                                  ▲
┌────────────────────────────────────────────────────┐
│              EXTERNAL CONTROLLER                    │
│                                                     │
│  Reads adapter states → Applies complex logic →     │
│  Toggles levers for multi-condition responses       │
└────────────────────┬───────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────┐
│              WEB DASHBOARD                          │
│                                                     │
│  Polls adapter API → Renders colony status          │
│  Traffic-light panels per category                  │
└────────────────────────────────────────────────────┘
```

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

## Phases

1. **External Controller** — Python script that polls adapters and toggles levers for complex automation rules
2. **Web Dashboard** — Browser-based colony status panel
3. **Expand** — More rules, richer dashboard, community-shared configurations

## Components

### 1. [Controller](controller/) — Smart Automation Engine
Python-based rules engine that polls HTTP Adapters (sensors) and triggers HTTP Levers (actuators) based on complex multi-condition logic.

**Features:**
- Config-driven YAML rules
- AND/OR condition logic
- Auto-retry when game offline
- Detailed logging
- Zero-crash operation

[→ Controller Documentation](controller/README.md)

### 2. [Dashboard](dashboard/) — Colony Status Monitor
Browser-based real-time monitoring dashboard with manual lever control.

**Features:**
- Live adapter state monitoring
- Manual lever toggles
- Filter/search by name
- Connection status indicator
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

3. **Edit `config.yaml`** to match your in-game adapter and lever names

4. **Run:**
   ```bash
   python3 controller.py
   ```

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

That's it! The dashboard will auto-poll and display your colony status.

## Configuration

### Controller Rules

Rules define automation logic. Each rule has:
- **name** — descriptive label for logging
- **conditions** — adapter checks with AND/OR operator
- **actions** — levers to trigger when conditions match

Example:
```yaml
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
```

See [config.example.yaml](controller/config.example.yaml) for more examples.

### Dashboard Customization

Edit `index.html` to change:
- `API_BASE` — game API endpoint (default: `http://localhost:8080`)
- `POLL_INTERVAL` — refresh frequency in milliseconds (default: 5000)

Use the built-in filter boxes to focus on specific adapter/lever categories.

## License

MIT
