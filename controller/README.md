# Timberborn Automation Controller

Event-driven automation bridge between Timberborn's HTTP Adapters (sensors) and HTTP Levers (actuators).

## Features

- ✅ **Event-driven webhook server** — instant reaction to adapter state changes
- ✅ Polling fallback mode for simple setups
- ✅ Config-driven rules engine (YAML)
- ✅ AND/OR condition logic across multiple adapters
- ✅ State and event history API for dashboard integration
- ✅ Graceful handling when game isn't running
- ✅ Detailed logging of state changes and actions
- ✅ No crashes, just retry logic

## Architecture Modes

The controller supports three operating modes:

### 1. Webhook Mode (Recommended)
**Event-driven, instant reaction**

The game pushes webhook calls to the controller when adapters change state. Zero polling delay.

**In-game setup required:** Configure each HTTP Adapter with webhook URLs:
- ON: `http://localhost:8081/on/{AdapterName}`
- OFF: `http://localhost:8081/off/{AdapterName}`

**Config:**
```yaml
mode: "webhook"
webhook_port: 8081
```

### 2. Polling Mode
**Traditional polling, no in-game config needed**

Controller polls `/api/adapters` periodically to check for state changes.

**No in-game setup required** — just run the controller.

**Config:**
```yaml
mode: "polling"
polling_interval_seconds: 5
```

### 3. Hybrid Mode
**Best of both worlds**

Webhook server for instant events + periodic polling for state sync/recovery.

**Config:**
```yaml
mode: "hybrid"
webhook_port: 8081
polling_interval_seconds: 10
```

## Setup

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Create your config:**
   ```bash
   cp config.example.yaml config.yaml
   ```

3. **Edit `config.yaml`:**
   - Set `mode` (webhook / polling / hybrid)
   - Configure `webhook_port` and/or `polling_interval_seconds`
   - Define your automation rules (adapter/lever names must match in-game exactly)

4. **Run:**
   ```bash
   python3 controller.py
   ```

   For webhook/hybrid mode, the controller will print webhook URLs to configure in-game.

## In-Game Webhook Configuration

If using webhook or hybrid mode, configure your HTTP Adapters:

1. Open each HTTP Adapter's configuration panel in-game
2. Set **"Call when switched on"** to:
   ```
   http://localhost:8081/on/{AdapterName}
   ```
3. Set **"Call when switched off"** to:
   ```
   http://localhost:8081/off/{AdapterName}
   ```
4. Replace `{AdapterName}` with the actual adapter name (e.g., `Weather Drought`)
5. Choose GET or POST method (both supported)

**The adapter name in the webhook URL must match the name used in your config.yaml rules.**

## Configuration

### Basic Structure

```yaml
mode: "webhook"  # "webhook", "polling", or "hybrid"
webhook_port: 8081
game_api_url: http://localhost:8080
polling_interval_seconds: 5  # used in polling/hybrid mode

rules:
  - name: "Rule Name"
    conditions:
      operator: AND  # or OR (default)
      checks:
        - adapter: "Adapter Name"
          state: true  # or false
    actions:
      - lever: "Lever Name"
        action: "on"  # or "off"
```

### Example: Drought Response

```yaml
rules:
  - name: "Drought Water Emergency"
    conditions:
      operator: AND
      checks:
        - adapter: "Weather Drought"
          state: true
        - adapter: "Water Depth Critical"
          state: true
    actions:
      - lever: "Pump Station"
        action: "on"
      - lever: "Main Floodgate"
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
      - lever: "Pump Station"
        action: "off"
      - lever: "Floodgate Main"
        action: "on"
```

These rules react instantly (webhook mode) or within the polling interval to manage water during droughts.

## API Endpoints

The controller exposes an HTTP API on the webhook port for dashboard integration:

### `GET /api/state`
Returns current system state:
```json
{
  "adapters": {"Weather Drought": true, "Water Level": false},
  "levers": {"Pump Station": true, "Floodgate": false},
  "events": [...],  // last 20 events
  "timestamp": 1234567890.123
}
```

### `GET /api/events?limit=50`
Returns event history (default 50, configurable):
```json
{
  "events": [
    {
      "timestamp": 1234567890.123,
      "type": "adapter",
      "name": "Weather Drought",
      "state": true,
      "details": "Changed from False to True"
    },
    ...
  ]
}
```

### `GET /health`
Health check endpoint:
```json
{
  "status": "ok",
  "mode": "webhook",
  "adapters_count": 5,
  "levers_count": 3
}
```

### Webhook Endpoints (Game → Controller)

- `GET|POST /on/{adapter_name}` — Adapter switched ON
- `GET|POST /off/{adapter_name}` — Adapter switched OFF

These are called by the game when adapters change state.

## Usage

```bash
python3 controller.py
```

Or specify a custom config:
```bash
python3 controller.py --config my-rules.yaml
```

**Webhook mode** will:
1. Start HTTP server on configured port
2. Wait for adapter webhook calls from the game
3. Update internal state when webhooks arrive
4. Evaluate rules and trigger levers instantly
5. Log all events to console + `controller.log`

**Polling mode** will:
1. Poll `/api/adapters` at the configured interval
2. Evaluate all rules against current adapter states
3. Trigger lever actions when conditions match
4. Log all state changes and actions

**Hybrid mode** does both.

Press `Ctrl+C` to stop.

## Tips

- **Exact names:** Adapter and lever names must match exactly (case-sensitive)
- **Webhook testing:** Visit `http://localhost:8081/on/TestAdapter` in a browser to simulate an adapter turning on
- **Dashboard integration:** Point the dashboard to the controller's URL to see rich event history
- **Polling interval:** In hybrid mode, use a longer interval (10-30s) — webhooks handle instant reactions
- **Logging:** Check `controller.log` for detailed history
- **Game offline:** Controller will keep retrying API calls until the game starts

## Troubleshooting

### "Port already in use"
Another process is using port 8081. Either:
- Stop the other process
- Change `webhook_port` in config.yaml
- Update in-game webhook URLs to match new port

### Webhooks not triggering
- Check controller logs for incoming webhook calls
- Verify webhook URLs in-game match controller endpoint exactly
- Test manually: `curl http://localhost:8081/on/TestAdapter`
- Ensure adapter names match between webhook URL and config rules

### "Game not reachable"
- Make sure Timberborn is running
- Verify the HTTP API mod is enabled
- Check that `game_api_url` in config matches the game's API port (default: 8080)
- Test: `curl http://localhost:8080/api/adapters`

### Rule not triggering
- Check adapter names match exactly (including spaces/capitalization)
- In webhook mode, ensure webhooks are configured in-game
- In polling mode, verify polling is active (check logs)
- Check logs for condition evaluation and rule firing

### Lever not responding
- Verify lever name is correct
- Check that the lever exists in-game
- Ensure the lever isn't controlled by in-game logic that overrides it
- Test manually: `curl -X POST http://localhost:8080/api/switch-on/{LeverName}`

## Mode Comparison

| Feature | Webhook | Polling | Hybrid |
|---------|---------|---------|--------|
| Reaction time | Instant | 5s (configurable) | Instant |
| In-game setup | Configure webhooks on each adapter | None | Configure webhooks |
| State sync | On startup only | Continuous | Both |
| Best for | Real-time automation | Simple setups, testing | Production (redundancy) |
| Dashboard events | ✅ Rich history | ✅ Rich history | ✅ Rich history |

## Event Types

The controller tracks three event types:

- **adapter** — Adapter state changed (on/off)
- **lever** — Lever toggled by automation
- **rule** — Automation rule triggered (conditions met)

All events include timestamp, name, state (where applicable), and details. View via `/api/events` or the dashboard.
