# Timberborn Automation Reference

A comprehensive catalog of all automation buildings, their capabilities, and configurable options.

> **Note:** This reference was compiled from the 1.0 release. Signal buildings output binary (on/off) states. Sequential components (Timer, Memory) update once per game tick.

---

## Building Categories

| Category | Count | Purpose |
|----------|-------|---------|
| **Signal** | 1 | Manual input — player-controlled signals |
| **Sensor** | 9 | Environmental/game state detection — automatic input based on thresholds |
| **Logic** | 3 | Signal processing — transform, combine, and sequence signals |
| **Display** | 5 | Output — visual alerts, sound, webhooks, and destructive actions |

---

## Signal Buildings

### Lever

> *Sends a manually controlled signal. A great first step toward automating a settlement.*

| Property | Detail |
|----------|--------|
| **Type** | Signal |
| **Output** | On/Off |

**Configurable Options:**
- **Button:** Switch on / Switch off (manual toggle)
- **Spring-return** ☐ — automatically returns to off after activation
- **Pinned** ☐ — pins the lever state in the UI

---

## Sensor Buildings

All sensors output a binary signal based on a player-defined threshold and comparison operator.

### Flow Sensor

> *Measures water flow below its arm.*

| Property | Detail |
|----------|--------|
| **Type** | Sensor |
| **Placement** | Must be positioned above water |
| **Output** | On when condition is met |

**Configurable Options:**
- **Operator:** `>`, `<`, `>=`, `<=`, `=`, `!=`
- **Threshold:** Slider from 0.00 to 2.00 cubic meters per second

---

### Depth Sensor

> *Measures water depth below its arm.*

| Property | Detail |
|----------|--------|
| **Type** | Sensor |
| **Placement** | Must be positioned above water |
| **Output** | On when condition is met |

**Configurable Options:**
- **Operator:** `>`, `<`, `>=`, `<=`, `=`, `!=`
- **Threshold:** Slider from 0m to height of sensor placement

**Notes:**
- Maximum measurable depth is determined by how high the sensor is placed — a sensor at height 4 can measure up to ~4m depth.

---

### Contamination Sensor

> *Measures water contamination below its arm.*

| Property | Detail |
|----------|--------|
| **Type** | Sensor |
| **Placement** | Must be positioned above water |
| **Output** | On when condition is met |

**Configurable Options:**
- **Operator:** `>`, `<`, `>=`, `<=`, `=`, `!=`
- **Threshold:** Slider from 0% to 100%

---

### Chronometer

> *Sends a signal based on time of the day.*

| Property | Detail |
|----------|--------|
| **Type** | Sensor |
| **Output** | On during selected time window |

**Configurable Options:**
- **Mode** (single-select):
  - **Time range** — custom start and end time
  - **Working hours** — active during work shift
  - **Non-working hours** — active outside work shift

---

### Weather Station

> *Sends a signal based on the weather.*

| Property | Detail |
|----------|--------|
| **Type** | Sensor |
| **Output** | On during selected weather condition |

**Configurable Options:**
- **Active during** (single-select):
  - **Temperate weather**
  - **Drought**
  - **Badtide**
- **Activate early** ☐ — triggers the signal before the weather event fully begins

**Notes:**
- "Activate early" is valuable for drought preparation — gives your automation a head start on emergency protocols.

---

### Power Meter

> *Monitors power network parameters.*

| Property | Detail |
|----------|--------|
| **Type** | Sensor |
| **Output** | On when condition is met |

**Configurable Options:**
- **Metric** (dropdown): Supply, Demand, Surplus, or Battery Charge
- **Operator:** `>`, `<`, `>=`, `<=`, `=`, `!=`
- **Threshold:** Integer input

---

### Population Counter

> *Monitors various population, housing, and workforce metrics.*

| Property | Detail |
|----------|--------|
| **Type** | Sensor |
| **Output** | On when condition is met |

**Configurable Options:**
- **Scope** (single-select): District mode or Global mode
- **Metric** (dropdown):
  - **Population:** Total population, total beavers, adults, children, bots
  - **Housing:** Occupied beds, free beds, homeless
  - **Workforce:** Jobs, employed, unemployed, vacancies, total workers, healthy workers, unhealthy workers
  - **Health:** Contaminated total, contaminated adults, contaminated children
- **Operator:** `>`, `<`, `>=`, `<=`, `=`, `!=`
- **Threshold:** Integer input

**Notes:**
- District vs Global mode is significant — district mode scopes to the counter's district, global aggregates across all districts.
- 19 different metrics make this one of the most versatile sensors in the game.

---

### Resource Counter

> *Sends a signal based on stock level or storage fill rate of a specified good.*

| Property | Detail |
|----------|--------|
| **Type** | Sensor |
| **Output** | On when condition is met |

**Configurable Options:**
- **Mode** (single-select):
  - **Percent (%)** — storage fill rate
  - **Quantity** — absolute stock count
- **Resource** (dropdown): Any in-game resource (Logs, Planks, Gears, Food types, etc.)
- **Operator:** `>`, `<`, `>=`, `<=`, `=`, `!=`
- **Threshold:** Value based on mode (% or integer)
- **Include inputs** ☐ *(quantity mode only)* — includes items currently being transported to storage

**Notes:**
- Percent mode measures against total storage capacity for that resource.
- "Include inputs" is useful when you want to account for in-transit goods, not just what's already stored.

---

### Science Counter

> *Sends a signal based on Science Points.*

| Property | Detail |
|----------|--------|
| **Type** | Sensor |
| **Output** | On when condition is met |

**Configurable Options:**
- **Operator:** `>`, `<`, `>=`, `<=`, `=`, `!=`
- **Threshold:** Integer input

---

### HTTP Lever

> *An API-controlled lever. Humans left a lot of those lying around.*

| Property | Detail |
|----------|--------|
| **Type** | Signal (API-controlled) |
| **Output** | On/Off (controlled via HTTP API) |
| **API Port** | 8080 (game's built-in API server) |

**Configurable Options:**
- **Button:** Switch on (manual toggle)
- **Spring-return** ☐ — automatically returns to off
- **Pinned** ☐ — pins state in UI
- **Switch-on URL:** `http://localhost:8080/api/switch-on/{encoded-name}` (modifiable)
- **Switch-off URL:** `http://localhost:8080/api/switch-off/{encoded-name}` (modifiable)

**API Endpoints:**
```
GET /api/levers                    → List all HTTP Levers
GET /api/levers/{name}             → Get specific lever state
GET|POST /api/switch-on/{name}     → Activate lever
GET|POST /api/switch-off/{name}    → Deactivate lever
GET /api/color/{name}/{RRGGBB}     → Set lever color
```

**Notes:**
- Names must be URL-encoded (`HTTP Lever 1` → `HTTP%20Lever%201`).
- API binds to localhost only. Use a tunnel (ngrok, cloudflare, etc.) for remote access.
- This is the primary **input** mechanism for external automation — code controls the game through these.

---

## Logic Buildings

### Relay

> *Performs simple logical operations on its input signals.*

| Property | Detail |
|----------|--------|
| **Type** | Logic |
| **Inputs** | A (required), B (optional, for two-input operations) |
| **Output** | On/Off based on logic operation |

**Configurable Options:**
- **Operation** (dropdown):
  - **Passthrough** — output = A
  - **NOT** — output = inverse of A
  - **AND** — output = A AND B
  - **OR** — output = A OR B
  - **XOR** — output = A XOR B

**Notes:**
- Single-input operations (NOT, Passthrough) only use input A.
- Two-input operations (AND, OR, XOR) require both A and B.
- Relays update immediately (not sequential).

---

### Timer

> *Applies time-based processing to its input signal. Sequential: Updates once per tick.*

| Property | Detail |
|----------|--------|
| **Type** | Logic (Sequential) |
| **Inputs** | A (required), RST (optional reset signal) |
| **Output** | On/Off based on timer mode |
| **Update Rate** | Once per tick |

**Configurable Options:**
- **Mode** (dropdown):
  - **Delay** — delays signal by T1 (on-delay) and T2 (off-delay)
  - **Pulse** — outputs a pulse of duration T1 when triggered
  - **Oscillator** — alternates on (T1 duration) and off (T2 duration) while input is active
  - **Accumulator** — counts up to T1 while input is active, fires when reached
- **T1:** Integer + unit (ticks, hours, days)
- **T2:** Integer + unit (ticks, hours, days) *(used by Delay and Oscillator)*
- **Buttons:** Reset, Reset circuit

**Notes:**
- Sequential component — updates once per game tick, introducing a minimum 1-tick latency.
- RST input allows another signal to reset the timer mid-operation.
- Oscillator is especially useful for cyclic production control (run factory for X hours, pause for Y hours).

---

### Memory

> *Changes and holds its state in response to specific input sequences. A cornerstone of advanced automation. Sequential: Updates once per tick.*

| Property | Detail |
|----------|--------|
| **Type** | Logic (Sequential) |
| **Inputs** | A (required), RST (optional reset signal) |
| **Output** | On/Off based on stored state |
| **Update Rate** | Once per tick |

**Configurable Options:**
- **Mode** (dropdown):
  - **Set-Reset** — A sets output on; stays on until reset
  - **Toggle** — each A pulse flips the output
  - **Latch** — output follows A while enabled, holds last value when disabled
  - **Flip-flop** — alternates state on each A pulse (similar to Toggle but with edge detection)
- **Buttons:** Reset, Reset circuit

**Notes:**
- Sequential component — updates once per game tick.
- Memory is essential for automation patterns that need to "remember" — e.g., a drought response that stays active even after the drought sensor flickers.
- Set-Reset is the simplest and most common pattern for persistent state.

---

## Display Buildings

### Indicator

> *An indicator light with alerting capabilities.*

| Property | Detail |
|----------|--------|
| **Type** | Display |
| **Input** | One signal input |

**Configurable Options:**
- **Pinned when on** ☐ — pins to UI when active
- **Pinned always** ☐ — always visible in UI
- **Show warning when switched on** ☐ — displays a warning notification
- **Add journal entry when switched on** ☐ — logs to the game journal
- **Replicate input color** ☐ — matches the color of the input signal

**Notes:**
- Pure output — no signal forwarding. Use for visual monitoring.
- "Add journal entry" is useful for debugging automation — creates a game log when triggered.
- Can also serve as a debugging tool when wiring complex logic chains.

---

### Speaker

> *Makes noises.*

| Property | Detail |
|----------|--------|
| **Type** | Display |
| **Input** | One signal input |

**Configurable Options:**
- **Play mode** (single-select): Play once, Play continuously
- **Audio mode** (single-select): Spatial (3D positioned), Non-spatial (global)
- **Sound** (dropdown): 4 default sounds + support for custom audio file drop-ins to a game directory

**Notes:**
- Custom sounds open up creative possibilities — alarm sirens, music, notification tones.
- Spatial mode means the sound comes from the speaker's location in-game; non-spatial plays everywhere.

---

### Firework Launcher

> *Shoots out celebratory fireworks.*

| Property | Detail |
|----------|--------|
| **Type** | Display |
| **Input** | One signal input |

**Configurable Options:**
- **Firework type** (dropdown): Comet (blue/red/white), Fish, Kamuro (blue/orange/pink/red/white), Palm (blue/gold/green), Peony (red & blue/violet/yellow & green), Sparks, Willow
- **Heading:** Slider from -180° to 180°
- **Pitch:** Slider from -30° to 30°
- **Flight distance:** Slider from 10m to 40m
- **Continuous launch** ☐ — keeps firing while signal is active

**Notes:**
- 17 firework varieties with full directional control.
- Wire to a milestone sensor for automated celebrations (e.g., population hits 100 → fireworks).

---

### Detonator

> *Arms the dynamite underneath it.*

| Property | Detail |
|----------|--------|
| **Type** | Display |
| **Input** | One signal input |

**Configurable Options:**
- None — the detonator simply arms when it receives a signal.

**Notes:**
- ⚠️ **Destructive and irreversible.** Use with extreme caution in automated systems.
- Requires dynamite to be placed beneath it.
- Useful for automated terrain modification, dam breaking, or controlled demolition sequences.

---

### HTTP Adapter

> *Turns its input signal into an API endpoint and webhook calls, whatever that means.*

| Property | Detail |
|----------|--------|
| **Type** | Display (API bridge) |
| **Input** | One signal input |
| **Default Webhook Port** | 8081 (configurable) |

**Configurable Options:**
- **Call when switched on** ☐ + URL textbox (default: `http://localhost:8081/on/{name}`)
- **Call when switched off** ☐ + URL textbox (default: `http://localhost:8081/off/{name}`)
- **Method** (dropdown): GET, POST

**API Endpoints (passive — game exposes these):**
```
GET /api/adapters              → List all HTTP Adapters
GET /api/adapters/{name}       → Get specific adapter state
```

**Webhook Behavior (active — game calls out):**
- When input signal turns ON and "Call when switched on" is checked → game calls the configured URL
- When input signal turns OFF and "Call when switched off" is checked → game calls the configured URL
- Each direction is independently toggleable
- URL is fully customizable (can point to any endpoint)

**Notes:**
- This is the primary **output** mechanism for external automation — the game pushes state changes to your code.
- Supports both passive polling (via `/api/adapters`) and active webhooks (via configured URLs).
- The webhook approach is preferred for automation controllers — instant response vs polling delay.

---

## System Summary

### Signal Flow
```
Sensors/Levers (Input) → Logic (Processing) → Display/Actuators (Output)
     ↓                        ↓                         ↓
  9 sensor types         Relay (instant)          Indicator (visual)
  1 manual lever         Timer (sequential)       Speaker (audio)
  1 HTTP lever           Memory (sequential)      Firework (visual)
                                                  Detonator (destructive)
                                                  HTTP Adapter (external)
```

### All Buildings At a Glance

| Building | Type | Inputs | Key Capability |
|----------|------|--------|----------------|
| Lever | Signal | 0 | Manual on/off toggle |
| Flow Sensor | Sensor | 0 | Water movement detection |
| Depth Sensor | Sensor | 0 | Water level detection |
| Contamination Sensor | Sensor | 0 | Badwater detection |
| Chronometer | Sensor | 0 | Time-of-day triggers |
| Weather Station | Sensor | 0 | Drought/badtide detection (with early warning) |
| Power Meter | Sensor | 0 | Power grid monitoring (supply/demand/surplus/battery) |
| Population Counter | Sensor | 0 | 19 population/housing/workforce metrics |
| Resource Counter | Sensor | 0 | Per-resource stock level or fill % |
| Science Counter | Sensor | 0 | Science point tracking |
| HTTP Lever | Signal | 0 | External API control input |
| Relay | Logic | 1-2 | Boolean logic (NOT/AND/OR/XOR/Pass) |
| Timer | Logic | 1-2 | Time-based signal processing (delay/pulse/oscillate/accumulate) |
| Memory | Logic | 1-2 | State persistence (set-reset/toggle/latch/flip-flop) |
| Indicator | Display | 1 | Visual alert + journal logging |
| Speaker | Display | 1 | Audio alerts (custom sounds supported) |
| Firework Launcher | Display | 1 | 17 firework types with directional control |
| Detonator | Display | 1 | ⚠️ Arms dynamite (irreversible) |
| HTTP Adapter | Display | 1 | External webhook calls + API endpoint |

### Actuatable Buildings (Non-Automation)
All of the following building types can be toggled on/off by automation signals:
- All **workplaces** (factories, farms, foresters, etc.)
- All **housing**
- All **power generators** and **power consumers**
- **Gates** (floodgates, etc.)
- **Fill valves**
- **Throttling valves**

---

**Faction availability:** All factions have access to all automation buildings.

> Construction costs, tile footprints, and research unlocks are omitted intentionally — players can adapt to those easily. This reference focuses on **capabilities and use cases**, which benefit from study and experience.

*Last updated: March 2026 | Timberborn 1.0*
