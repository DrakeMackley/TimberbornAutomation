# Controller API Specification

The automation controller exposes an HTTP API on port **8081** (configurable). This spec defines all endpoints, request/response formats, and behavior contracts.

> **Status:** Conceptual spec — implementation should conform to this document.

---

## Base URL

```
http://localhost:8081
```

---

## Webhook Endpoints (Game → Controller)

These endpoints receive calls from Timberborn's HTTP Adapters when in-game signals change state.

### `GET|POST /on/{name}`

**Purpose:** Notify the controller that adapter `{name}` switched ON.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Adapter name (URL-encoded). Must match the in-game adapter name. |

**Request Body:** None (ignored if present).

**Response:**
```json
{
  "status": "ok",
  "adapter": "Weather Drought",
  "state": true,
  "timestamp": "2026-03-11T20:15:30.123Z"
}
```

**Status Codes:**
| Code | Meaning |
|------|---------|
| 200 | State updated successfully |
| 500 | Internal error processing the event |

**Side Effects:**
1. Updates internal adapter state to `true`
2. Runs the rules engine against ALL rules
3. Fires any matching rule actions (lever toggles)
4. Logs event to event history

---

### `GET|POST /off/{name}`

**Purpose:** Notify the controller that adapter `{name}` switched OFF.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Adapter name (URL-encoded). |

**Response:**
```json
{
  "status": "ok",
  "adapter": "Weather Drought",
  "state": false,
  "timestamp": "2026-03-11T20:15:30.123Z"
}
```

**Status Codes:** Same as `/on/{name}`.

**Side Effects:** Same as `/on/{name}`, but sets state to `false`.

---

## State & Events API (Dashboard → Controller)

### `GET /api/state`

**Purpose:** Return current adapter states, lever states, and recent events. Primary data source for the dashboard.

**Query Parameters:** None.

**Response:**
```json
{
  "adapters": {
    "Weather Drought": {
      "state": true,
      "last_changed": "2026-03-11T20:15:30.123Z"
    },
    "Water Depth Critical": {
      "state": false,
      "last_changed": "2026-03-11T20:10:00.000Z"
    }
  },
  "levers": {
    "Pump Station": {
      "state": true,
      "last_changed": "2026-03-11T20:15:30.456Z"
    }
  },
  "events": [
    {
      "type": "adapter",
      "name": "Weather Drought",
      "state": true,
      "timestamp": "2026-03-11T20:15:30.123Z"
    },
    {
      "type": "rule",
      "name": "Drought Water Emergency",
      "triggered": true,
      "timestamp": "2026-03-11T20:15:30.200Z"
    },
    {
      "type": "lever",
      "name": "Pump Station",
      "action": "on",
      "timestamp": "2026-03-11T20:15:30.456Z"
    }
  ],
  "mode": "webhook",
  "uptime_seconds": 3600,
  "rules_evaluated": 142,
  "actions_fired": 23
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `adapters` | object | Map of adapter name → state object |
| `adapters[name].state` | boolean | Current on/off state |
| `adapters[name].last_changed` | string (ISO 8601) | When state last changed |
| `levers` | object | Map of lever name → state object |
| `levers[name].state` | boolean | Last known lever state |
| `levers[name].last_changed` | string (ISO 8601) | When lever was last toggled |
| `events` | array | Last 20 events (most recent first) |
| `events[].type` | string | `"adapter"`, `"rule"`, or `"lever"` |
| `events[].name` | string | Name of the adapter/rule/lever |
| `events[].state` | boolean | New state (adapter events) |
| `events[].triggered` | boolean | Whether rule conditions matched (rule events) |
| `events[].action` | string | `"on"` or `"off"` (lever events) |
| `events[].timestamp` | string (ISO 8601) | When the event occurred |
| `mode` | string | Operating mode: `"webhook"`, `"polling"`, or `"hybrid"` |
| `uptime_seconds` | number | Seconds since controller started |
| `rules_evaluated` | number | Total rule evaluations since startup |
| `actions_fired` | number | Total lever actions fired since startup |

---

### `GET /api/events`

**Purpose:** Return event history with configurable limit.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Number of events to return (most recent first) |

**Response:**
```json
{
  "events": [
    {
      "type": "adapter",
      "name": "Weather Drought",
      "state": true,
      "timestamp": "2026-03-11T20:15:30.123Z"
    }
  ],
  "total_stored": 100,
  "returned": 50
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `events` | array | Event objects (same schema as `/api/state` events) |
| `total_stored` | number | Total events in memory |
| `returned` | number | Number returned in this response |

---

### `GET /health`

**Purpose:** Health check endpoint for monitoring and Docker HEALTHCHECK.

**Response:**
```json
{
  "status": "healthy",
  "mode": "webhook",
  "uptime_seconds": 3600,
  "game_reachable": true,
  "adapters_tracked": 5,
  "levers_tracked": 3,
  "rules_loaded": 6
}
```

**Status Codes:**
| Code | Meaning |
|------|---------|
| 200 | Controller is running and healthy |
| 503 | Controller is degraded (e.g., game unreachable in polling mode) |

---

## Configuration Schema

### `config.yaml`

```yaml
# Required
mode: "webhook"              # "webhook" | "polling" | "hybrid"
rules: []                    # Array of rule objects (see below)

# Optional (with defaults)
webhook_port: 8081           # integer, 1024-65535
game_api_url: "http://localhost:8080"  # string, valid URL
polling_interval_seconds: 5  # integer, >= 1 (used in polling/hybrid mode)
```

### Rule Object

```yaml
- name: "Rule Name"          # string, required — used in logging and events
  conditions:                # object, required
    operator: "AND"          # "AND" | "OR" — default: "OR" if omitted
    checks:                  # array, required, min 1 item
      - adapter: "Name"     # string, required — must match in-game adapter name
        state: true          # boolean, required — expected state to match
  actions:                   # array, required, min 1 item
    - lever: "Name"          # string, required — must match in-game lever name
      action: "on"           # "on" | "off", required
```

### Validation Rules

1. `mode` must be one of: `webhook`, `polling`, `hybrid`
2. `rules` must be a non-empty array
3. Each rule must have `name`, `conditions`, and `actions`
4. Each check must have `adapter` (string) and `state` (boolean)
5. Each action must have `lever` (string) and `action` (`"on"` or `"off"`)
6. `operator` defaults to `"OR"` if omitted
7. If `mode` is `polling` or `hybrid`, `game_api_url` must be reachable (warn on startup, don't crash)

---

## Behavioral Contracts

### Webhook Processing
1. On receiving `/on/{name}` or `/off/{name}`:
   - Update adapter state immediately
   - Evaluate ALL rules (not just rules referencing that adapter)
   - For each rule where conditions match: execute all actions
   - For each rule where conditions don't match: do nothing (don't reverse previous actions — rules should have explicit "resolved" counterparts)
   - Log all state changes and rule evaluations
   - Return 200 OK to the game (fast — don't block on lever API calls)

### Polling Processing
1. On each poll interval:
   - Fetch `GET /api/adapters` from game
   - Compare to previous known state
   - For any state changes, process as if a webhook was received
   - If game unreachable, log warning and retry next interval (don't crash)

### Lever Actions
1. To switch a lever ON: `GET|POST {game_api_url}/api/switch-on/{url_encoded_name}`
2. To switch a lever OFF: `GET|POST {game_api_url}/api/switch-off/{url_encoded_name}`
3. If lever API call fails: log error, continue processing (don't crash, don't retry immediately)
4. Track lever state internally based on actions sent (optimistic)

### Startup Behavior
1. Load and validate config
2. If invalid config: exit with clear error message
3. Start webhook server (if mode is `webhook` or `hybrid`)
4. Perform initial state sync via polling `GET /api/adapters` and `GET /api/levers` (all modes)
5. If game unreachable on startup: log warning, start anyway, retry sync periodically
6. Log configured rules and webhook URLs for in-game setup reference

### Shutdown Behavior
1. On SIGINT/SIGTERM: stop accepting webhooks, finish in-progress rule evaluations, exit cleanly
2. No state persistence needed — state rebuilds from initial sync on restart

### Error Handling
1. **Never crash on runtime errors** — log and continue
2. Game unreachable → retry on next poll/webhook (don't queue retries)
3. Invalid webhook path → return 404
4. Malformed adapter name → log warning, skip

---

## CORS

The controller should include CORS headers to allow the dashboard (served from a different port) to access the API:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

---

*Spec version: 1.0 | March 2026*
