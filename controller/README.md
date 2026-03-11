# Timberborn Automation Controller

Smart automation bridge between Timberborn's HTTP Adapters (sensors) and HTTP Levers (actuators).

## Features

- ✅ Config-driven rules engine (YAML)
- ✅ AND/OR condition logic across multiple adapters
- ✅ Polling loop with configurable interval
- ✅ Graceful handling when game isn't running
- ✅ Detailed logging of state changes and actions
- ✅ No crashes, just retry logic

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
   - Set your adapter names (match exactly what's in-game)
   - Set your lever names (match exactly what's in-game)
   - Define conditions and actions

## Usage

```bash
python3 controller.py
```

Or specify a custom config:
```bash
python3 controller.py --config my-rules.yaml
```

The controller will:
1. Poll `/api/adapters` at the configured interval
2. Evaluate all rules against current adapter states
3. Trigger lever actions when conditions match
4. Log all state changes and actions to console + `controller.log`

Press `Ctrl+C` to stop.

## Configuration

### Structure

```yaml
api_base: http://localhost:8080
polling_interval_seconds: 2

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
```

This rule activates the pump station AND closes the main floodgate when both drought is active AND water is critically low.

## Tips

- **Exact names:** Adapter and lever names must match exactly (case-sensitive)
- **Polling interval:** Lower = more responsive, but more API load. 2-5 seconds is a good balance.
- **Logging:** Check `controller.log` for detailed history
- **Testing:** Use `config.example.yaml` as a starting template
- **Game offline:** Controller will keep retrying until the game starts

## Troubleshooting

**"Game not reachable"**
- Make sure Timberborn is running
- Verify the HTTP API mod is enabled
- Check that `api_base` in config matches the game's API port (default: 8080)

**Rule not triggering**
- Check adapter names match exactly (including spaces/capitalization)
- Verify adapter states with `curl http://localhost:8080/api/adapters`
- Check logs for condition evaluation

**Lever not responding**
- Verify lever name is correct
- Check that the lever exists in-game
- Ensure the lever isn't controlled by in-game logic that overrides it
