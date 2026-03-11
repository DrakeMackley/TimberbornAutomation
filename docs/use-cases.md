# Timberborn Automation Use Cases

Practical automation patterns organized by challenge. Each pattern lists the buildings involved and the wiring logic.

> **Convention:** `→` means "signal feeds into." `+` means "combined via relay."

---

## 🌊 Water Management

### Drought Emergency Response
**Challenge:** When drought hits and water levels drop, you need to activate pumps and close floodgates before reservoirs dry out.

**Buildings:**
- Weather Station (active during: drought)
- Depth Sensor (water level < critical threshold)
- Relay (AND)
- Floodgates, pumps (actuated)

**Wiring:**
```
Weather Station [drought] ──→ Relay (AND) ──→ Close floodgates
Depth Sensor [< 0.5m]     ──→            ──→ Activate pumps
```

**Why AND?** You don't want pumps running just because water is low during temperate weather (it might be filling). You want the emergency response only when drought is active AND water is critically low.

**Enhancement:** Use the Weather Station's "Activate early" checkbox to start closing gates before the drought fully hits.

---

### Floodgate Auto-Fill
**Challenge:** Keep reservoirs topped off during temperate weather without overflowing.

**Buildings:**
- Weather Station (active during: temperate weather)
- Depth Sensor (water level < desired max)
- Relay (AND)
- Floodgates (actuated)

**Wiring:**
```
Weather Station [temperate] ──→ Relay (AND) ──→ Open fill gates
Depth Sensor [< 3.0m]      ──→
```

**Logic:** Only fill when it's temperate (water is flowing) AND reservoir isn't full yet.

---

### Contamination Isolation
**Challenge:** When badwater contamination is detected, isolate affected water systems.

**Buildings:**
- Contamination Sensor (contamination > 0%)
- Weather Station (active during: badtide) *(optional, for early warning)*
- Floodgates, valves (actuated)

**Wiring:**
```
Contamination Sensor [> 0%] ──→ Close isolation gates
                            ──→ Activate water treatment (if available)
```

**Enhancement:** Wire a Weather Station with "Activate early" + badtide mode to pre-isolate before contamination actually arrives.

---

### Water Level Cascade
**Challenge:** Manage a multi-tier reservoir system where upper reservoirs feed lower ones.

**Buildings:**
- Multiple Depth Sensors (one per tier)
- Relays (priority logic)
- Fill valves between tiers (actuated)

**Wiring:**
```
Depth Sensor [upper tier < 2m] ──→ Relay (NOT) ──→ Close valve to lower tier
                                                    (don't drain upper if it's low)
Depth Sensor [lower tier < 1m] ──→ Relay (AND) ──→ Open valve from upper tier
                                                    (only fill lower if upper has surplus)
```

---

## 📦 Resource Management

### Low Stock Auto-Boost
**Challenge:** When a critical resource drops below threshold, boost production.

**Buildings:**
- Resource Counter (resource: Logs, mode: quantity, < 50)
- Workplace: Forester/Lumberjack (actuated)

**Wiring:**
```
Resource Counter [Logs < 50] ──→ Activate extra Forester hut
```

**Scaling:** Place multiple Resource Counters for different resources, each controlling a different workplace:
```
Resource Counter [Planks < 30]  ──→ Activate Lumber Mill #2
Resource Counter [Gears < 20]  ──→ Activate Gear Workshop #2
Resource Counter [Bread < 40]  ──→ Activate Bakery #2
```

---

### Storage Overflow Prevention
**Challenge:** Pause production when storage is nearly full to avoid wasted labor.

**Buildings:**
- Resource Counter (resource: Planks, mode: percent, > 90%)
- Relay (NOT)
- Workplace: Lumber Mill (actuated)

**Wiring:**
```
Resource Counter [Planks > 90%] ──→ Relay (NOT) ──→ Deactivate Lumber Mill
```

**Logic:** When storage is over 90% full, the NOT relay inverts the signal to shut down production. When it drops back below 90%, production resumes automatically.

---

### Production Chain Balancing
**Challenge:** Balance upstream and downstream production (e.g., logs → planks → gears).

**Buildings:**
- Resource Counter × 3 (Logs, Planks, Gears)
- Relays (logic chain)
- Workplaces (actuated)

**Wiring:**
```
Resource Counter [Logs < 30]    ──→ Boost Foresters + Pause Lumber Mill
Resource Counter [Planks < 20]  ──→ Boost Lumber Mill + Pause Gear Workshop
Resource Counter [Gears < 10]   ──→ Boost Gear Workshop
```

**Key insight:** Use the NOT relay to create inverse relationships — when logs are low, shut down the thing that consumes logs (Lumber Mill) while boosting the thing that produces logs (Forester).

---

### Seasonal Resource Strategy
**Challenge:** Stockpile critical resources before drought.

**Buildings:**
- Weather Station (active during: temperate, with "Activate early" for drought prep)
- Resource Counter (food < 100)
- Relay (AND)
- Farms, gathering (actuated)

**Wiring:**
```
Weather Station [temperate] ──→ Relay (AND) ──→ Activate all farms at full capacity
Resource Counter [Food < 100] ──→
```

**Enhancement:** Use a Timer (accumulator) to track how long drought has been active, escalating response intensity over time.

---

## ⚡ Power Management

### Load Shedding
**Challenge:** When power demand exceeds supply, shed non-essential loads.

**Buildings:**
- Power Meter (metric: surplus, < 0)
- Non-essential workplaces (actuated)

**Wiring:**
```
Power Meter [Surplus < 0] ──→ Deactivate non-essential buildings
                              (decorative, secondary production, etc.)
```

**Priority tiers:** Wire multiple Power Meters at different thresholds:
```
Power Meter [Surplus < 0]    ──→ Shed tier 3 (luxury)
Power Meter [Surplus < -50]  ──→ Shed tier 2 (secondary production)
Power Meter [Surplus < -100] ──→ Shed tier 1 (keep only food + water)
```

---

### Battery Conservation
**Challenge:** Preserve battery charge for nighttime or drought.

**Buildings:**
- Power Meter (metric: battery charge, < 50)
- Chronometer (active during: non-working hours)
- Relay (AND/OR logic)
- Power consumers (actuated)

**Wiring:**
```
Power Meter [Battery < 50%] ──→ Reduce non-essential power consumers
Chronometer [night hours]   ──→ Relay (AND) ──→ Only run essentials at night when battery is low
```

---

### Drought Power Switch
**Challenge:** Switch from water-based power (waterwheels) to alternative power during drought.

**Buildings:**
- Weather Station (active during: drought)
- Power generators (actuated)

**Wiring:**
```
Weather Station [drought] ──→ Deactivate water wheels (no water flow)
                          ──→ Activate treadmills / engines
```

---

## 🏠 Population & Workforce

### Housing Alert
**Challenge:** Know when you need more housing before beavers become homeless.

**Buildings:**
- Population Counter (metric: free beds, < 5)
- Indicator (pinned, show warning)

**Wiring:**
```
Population Counter [Free beds < 5] ──→ Indicator [warning ON]
```

**Enhancement:** Add journal entry logging to track when housing pressure starts.

---

### Unemployment Response
**Challenge:** Automatically adjust production capacity based on available workforce.

**Buildings:**
- Population Counter (metric: unemployed, > 5)
- Dormant workplaces (actuated)

**Wiring:**
```
Population Counter [Unemployed > 5] ──→ Activate expansion workplace
```

**Inverse:** If vacancies are high, pause low-priority workplaces:
```
Population Counter [Vacancies > 10] ──→ Relay (NOT) ──→ Pause luxury production
```

---

### Contamination Workforce Compensation
**Challenge:** When workers get contaminated, boost essential production to compensate for reduced workforce.

**Buildings:**
- Population Counter (metric: contaminated adults, > 3)
- Essential workplaces (actuated — boost priority)
- Non-essential workplaces (actuated — pause)

**Wiring:**
```
Population Counter [Contaminated > 3] ──→ Pause non-essentials
                                       ──→ Indicator [contamination warning]
```

---

## ⏰ Time-Based Automation

### Day/Night Production Cycling
**Challenge:** Run noisy or power-hungry production only during work hours.

**Buildings:**
- Chronometer (active during: working hours)
- Workplaces (actuated)

**Wiring:**
```
Chronometer [working hours] ──→ Activate factory production
```

---

### Periodic Maintenance Cycles
**Challenge:** Run a pump or valve for X hours, then pause for Y hours.

**Buildings:**
- Timer (oscillator mode, T1: run duration, T2: pause duration)
- Lever or sensor (trigger input)
- Workplace/valve (actuated)

**Wiring:**
```
Lever [ON] ──→ Timer (Oscillator, T1: 6 hours ON, T2: 2 hours OFF) ──→ Pump
```

---

### Delayed Emergency Escalation
**Challenge:** Don't overreact to brief sensor blips — only escalate if a condition persists.

**Buildings:**
- Any sensor (trigger)
- Timer (accumulator, T1: threshold duration)
- Emergency response buildings (actuated)

**Wiring:**
```
Depth Sensor [< 0.3m] ──→ Timer (Accumulator, T1: 2 hours) ──→ EMERGENCY: activate all pumps
```

**Logic:** The accumulator only fires after the low-water condition has persisted for 2 continuous hours. Brief dips won't trigger a false alarm.

---

## 🔔 Monitoring & Alerts

### Colony Health Dashboard (In-Game)
**Challenge:** See colony status at a glance without clicking through buildings.

**Buildings:**
- Multiple sensors (one per metric)
- Indicators (pinned, color-coded)

**Wiring:**
```
Resource Counter [Food < 50]       ──→ Indicator [RED, pinned, warning]
Depth Sensor [Water < 1m]          ──→ Indicator [RED, pinned, warning]
Population Counter [Homeless > 0]  ──→ Indicator [YELLOW, pinned, warning]
Power Meter [Surplus < 0]          ──→ Indicator [RED, pinned, warning]
```

**With "replicate input color":** If your input signals carry color data, indicators can match them for richer visual feedback.

---

### External Dashboard via HTTP
**Challenge:** Monitor colony from a web browser while playing (or on a second monitor).

**Buildings:**
- Any sensors you want to monitor → HTTP Adapters (one per metric)

**Wiring:**
```
Resource Counter [Food < 50]  ──→ HTTP Adapter "Food Low"
                                  Call when switched on:  http://localhost:8081/on/Food%20Low
                                  Call when switched off: http://localhost:8081/off/Food%20Low

Depth Sensor [Water < 1m]    ──→ HTTP Adapter "Water Critical"
                                  ...same pattern...
```

**Result:** External dashboard receives real-time push notifications of state changes.

---

### Audio Alerts for Critical Events
**Challenge:** Get an audible warning when something needs immediate attention (useful when zoomed in elsewhere on the map).

**Buildings:**
- Critical sensor → Speaker (non-spatial, play once)

**Wiring:**
```
Weather Station [drought] ──→ Speaker [non-spatial, play once, alarm sound]
```

---

## 🎆 Fun & Celebrations

### Population Milestone Fireworks
**Challenge:** Celebrate when your colony hits a population milestone.

**Buildings:**
- Population Counter (total population > milestone)
- Firework Launcher(s)

**Wiring:**
```
Population Counter [Population > 100] ──→ Firework Launcher [Kamuro gold, continuous]
```

---

### Automated Dam Break
**Challenge:** Controlled demolition of a temporary dam when water levels are sufficient.

**Buildings:**
- Depth Sensor (water > target level)
- Timer (delay — give yourself time to save!)
- Detonator

**Wiring:**
```
Depth Sensor [> 4m] ──→ Timer (Delay, T1: 30 seconds) ──→ Detonator ──→ 💥
```

**⚠️ IRREVERSIBLE.** Test your wiring thoroughly before connecting a detonator. Consider adding a manual Lever as a safety interlock (AND with the sensor so both must be active).

---

## 🧠 Advanced Patterns

### Priority System
**Challenge:** When multiple resources are low, prioritize the most critical.

**Pattern:** Use layered NOT gates to create priority tiers:
```
Resource Counter [Food < 20]   ──→ Priority 1: ALL non-food production stops
Resource Counter [Water < 1m]  ──→ Priority 1: Emergency pumps activate
Resource Counter [Logs < 30]   ──→ Priority 2: Boost forestry (only if food is OK)
Resource Counter [Gears < 10]  ──→ Priority 3: Boost gears (only if food + logs OK)
```

Wire higher-priority signals through NOT relays to suppress lower-priority actions when critical resources need attention.

---

### Hysteresis (Anti-Flicker)
**Challenge:** A sensor right at its threshold causes rapid on/off toggling, which is annoying and wasteful.

**Pattern:** Use Memory (Set-Reset) with two sensors at different thresholds:
```
Resource Counter [Logs < 30]  ──→ Memory (Set-Reset) SET    ──→ Activate Forester
Resource Counter [Logs > 60]  ──→ Memory (Set-Reset) RESET
```

**Logic:** Production activates when logs drop below 30, and doesn't deactivate until logs exceed 60. This creates a dead zone that prevents flicker.

---

### Timed Drought Response Escalation
**Challenge:** Escalate emergency measures the longer a drought persists.

**Pattern:** Chain multiple timers with increasing durations:
```
Weather Station [drought] ──→ Timer (Accum, 0h)  ──→ Phase 1: Close outer gates
                          ──→ Timer (Accum, 6h)  ──→ Phase 2: Activate pumps, reduce power
                          ──→ Timer (Accum, 12h) ──→ Phase 3: Shut down all non-essential
                          ──→ Timer (Accum, 24h) ──→ Phase 4: Emergency rations mode
```

---

### External Multi-Condition Logic
**Challenge:** Rules too complex for in-game relay chains (e.g., "if food < 50 AND population > 80 AND drought active AND power surplus > 0, THEN ...").

**Pattern:** Wire each sensor to an HTTP Adapter. Let the external controller handle the complex logic:
```
Sensors ──→ HTTP Adapters ──→ External Controller (Python) ──→ HTTP Levers ──→ Actuate buildings
```

The controller's YAML config can express arbitrarily complex rules that would require dozens of in-game relays.

---

*Last updated: March 2026 | Timberborn 1.0*
