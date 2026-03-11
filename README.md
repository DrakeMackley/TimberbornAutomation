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

## Setup

_Coming soon — Phase 1 in progress._

## License

MIT
