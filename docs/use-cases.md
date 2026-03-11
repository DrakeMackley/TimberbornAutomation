# Timberborn Automation Use Cases

50 practical automation patterns organized by challenge. Each pattern lists the buildings involved and the wiring logic.

> **Convention:** `→` means "signal feeds into." `+` means "combined via relay."

> **Difficulty:** `🟢 Beginner` — 1-2 buildings, direct wiring | `⚡ Intermediate` — 3+ buildings, relay logic or timers | `🔴 Advanced` — memory cells, multi-stage logic, or external controller

---

## 🌊 Water Management

### 1. Drought Emergency Response `⚡ Intermediate`
**Challenge:** When drought hits and water levels drop, activate pumps and close floodgates before reservoirs dry out.

**Buildings:** Weather Station (drought) + Depth Sensor (< critical) + Relay (AND)

**Wiring:**
```
Weather Station [drought] ──→ Relay (AND) ──→ Close floodgates
Depth Sensor [< 0.5m]     ──→            ──→ Activate pumps
```

**Why AND?** You don't want pumps running just because water is low during temperate weather (it might be filling). You want the emergency response only when drought is active AND water is critically low.

**Enhancement:** Use the Weather Station's "Activate early" checkbox to start closing gates before the drought fully hits.

---

### 2. Floodgate Auto-Fill `🟢 Beginner`
**Challenge:** Keep reservoirs topped off during temperate weather without overflowing.

**Buildings:** Weather Station (temperate) + Depth Sensor (< max) + Relay (AND)

**Wiring:**
```
Weather Station [temperate] ──→ Relay (AND) ──→ Open fill gates
Depth Sensor [< 3.0m]      ──→
```

**Logic:** Only fill when it's temperate (water is flowing) AND reservoir isn't full yet.

---

### 3. Contamination Isolation `🟢 Beginner`
**Challenge:** When badwater contamination is detected, isolate affected water systems.

**Buildings:** Contamination Sensor (> 0%) + Weather Station (badtide, optional)

**Wiring:**
```
Contamination Sensor [> 0%] ──→ Close isolation gates
                            ──→ Activate water treatment (if available)
```

**Enhancement:** Wire a Weather Station with "Activate early" + badtide mode to pre-isolate before contamination actually arrives.

---

### 4. Water Level Cascade `⚡ Intermediate`
**Challenge:** Manage a multi-tier reservoir system where upper reservoirs feed lower ones.

**Buildings:** Multiple Depth Sensors + Relays + Fill valves

**Wiring:**
```
Depth Sensor [upper tier < 2m] ──→ Relay (NOT) ──→ Close valve to lower tier
                                                    (don't drain upper if it's low)
Depth Sensor [lower tier < 1m] ──→ Relay (AND) ──→ Open valve from upper tier
                                                    (only fill lower if upper has surplus)
```

---

### 5. Flow-Based Irrigation Control `🟢 Beginner`
**Challenge:** Manage irrigation channels based on actual water flow, not just depth.

**Buildings:** Flow Sensor (< threshold) + Fill valves

**Wiring:**
```
Flow Sensor [< 0.5 m³/s] ──→ Open upstream valve to increase flow
Flow Sensor [> 1.5 m³/s] ──→ Throttle valve to prevent erosion/overflow
```

**When to use over Depth Sensor:** Flow matters more than depth for irrigation channels — a deep but stagnant pool isn't irrigating anything.

---

### 6. Reservoir Overflow Protection `🟢 Beginner`
**Challenge:** Prevent reservoirs from overflowing during heavy temperate rain/flow.

**Buildings:** Depth Sensor (> near-max) + Floodgates/drain valves

**Wiring:**
```
Depth Sensor [> 4.5m] ──→ Open overflow drain gates
```

**Enhancement:** Add a Timer (delay, T1: 1 hour) to avoid opening drains for brief wave surges.

---

### 7. Badtide Water Purge `🔴 Advanced`
**Challenge:** After a badtide ends, flush contaminated water from reservoirs before reopening.

**Buildings:** Weather Station (badtide) + Contamination Sensor + Relay (logic) + Memory (set-reset)

**Wiring:**
```
Weather Station [badtide]       ──→ Memory (Set-Reset) SET     ──→ Keep isolation gates closed
Contamination Sensor [= 0%]    ──→ Timer (Accum, 2h)          ──→ Memory RESET (safe to reopen)
```

**Logic:** Locks down when badtide starts. Stays locked even after badtide ends. Only reopens after contamination has been at 0% for 2 continuous hours (safe confirmation).

---

### 8. Drought Water Rationing `⚡ Intermediate`
**Challenge:** During drought, reduce water consumption by throttling non-essential water users.

**Buildings:** Weather Station (drought) + Depth Sensor (< medium threshold) + Relay (AND)

**Wiring:**
```
Weather Station [drought] ──→ Relay (AND) ──→ Throttle decorative fountains
Depth Sensor [< 2.0m]    ──→             ──→ Reduce irrigation flow
                                          ──→ Shut down baths/leisure water
```

**Tiered version:** Use multiple Depth Sensors at different thresholds for escalating rationing.

---

## 📦 Resource Management

### 9. Low Stock Auto-Boost `🟢 Beginner`
**Challenge:** When a critical resource drops below threshold, boost production.

**Buildings:** Resource Counter (quantity < threshold) + Workplace (actuated)

**Wiring:**
```
Resource Counter [Logs < 50] ──→ Activate extra Forester hut
```

**Scaling:** One counter per resource, each controlling its production building.

---

### 10. Storage Overflow Prevention `🟢 Beginner`
**Challenge:** Pause production when storage is nearly full to avoid wasted labor.

**Buildings:** Resource Counter (percent > 90%) + Relay (NOT) + Workplace

**Wiring:**
```
Resource Counter [Planks > 90%] ──→ Relay (NOT) ──→ Deactivate Lumber Mill
```

---

### 11. Production Chain Balancing `⚡ Intermediate`
**Challenge:** Balance upstream and downstream production (e.g., logs → planks → gears).

**Buildings:** Resource Counter × 3 + Relays + Workplaces

**Wiring:**
```
Resource Counter [Logs < 30]    ──→ Boost Foresters + Pause Lumber Mill
Resource Counter [Planks < 20]  ──→ Boost Lumber Mill + Pause Gear Workshop
Resource Counter [Gears < 10]   ──→ Boost Gear Workshop
```

**Key insight:** Use NOT relays to create inverse relationships — when logs are low, shut down the consumer while boosting the producer.

---

### 12. Seasonal Resource Stockpiling `⚡ Intermediate`
**Challenge:** Stockpile critical resources before drought.

**Buildings:** Weather Station (temperate) + Resource Counter + Relay (AND)

**Wiring:**
```
Weather Station [temperate] ──→ Relay (AND) ──→ Activate all farms at full capacity
Resource Counter [Food < 100] ──→
```

---

### 13. Food Diversity Monitor `⚡ Intermediate`
**Challenge:** Ensure multiple food types are stocked, not just one.

**Buildings:** Multiple Resource Counters (one per food type) + Relay (OR) + Indicator

**Wiring:**
```
Resource Counter [Berries < 10]  ──→ Relay (OR) ──→ Indicator [Food Diversity Warning]
Resource Counter [Bread < 10]    ──→
Resource Counter [Potatoes < 10] ──→
```

**Advanced version:** Use individual indicators per food type for the in-game dashboard, plus an OR relay feeding a master "food diversity critical" alert.

---

### 14. Construction Material Reserve `🟢 Beginner`
**Challenge:** Keep a minimum reserve of construction materials so building projects aren't stalled.

**Buildings:** Resource Counter (Logs, Planks, or Gears in quantity mode, "include inputs" unchecked)

**Wiring:**
```
Resource Counter [Planks < 20, exclude inputs] ──→ Activate extra Lumber Mill
```

**Why "exclude inputs"?** You want to know what's actually *in storage*, not what's being carried. If 15 planks are in transit but storage is empty, you still can't build.

---

### 15. Surplus Export Control `🟢 Beginner`
**Challenge:** Only export resources to other districts when you have a healthy surplus.

**Buildings:** Resource Counter (percent > 60%) + Relay (AND) + Distribution buildings

**Wiring:**
```
Resource Counter [Logs > 60%] ──→ Activate log distribution post
```

**Logic:** Only share resources when storage is comfortably above half. Below that, keep everything local.

---

### 16. Drought Food Emergency `⚡ Intermediate`
**Challenge:** When drought depletes water-dependent food sources, switch to drought-resistant production.

**Buildings:** Weather Station (drought) + Resource Counter (food) + Relay (AND) + Workplaces

**Wiring:**
```
Weather Station [drought]         ──→ Deactivate irrigated farms
                                  ──→ Relay (AND) ──→ Activate dried food processing
Resource Counter [Food < 60]      ──→
```

**Logic:** Always shut down irrigated farms in drought (no water). Only activate emergency food processing if food is also getting low.

---

## ⚡ Power Management

### 17. Load Shedding `⚡ Intermediate`
**Challenge:** When power demand exceeds supply, shed non-essential loads.

**Buildings:** Power Meter (surplus < 0)

**Wiring (priority tiers):**
```
Power Meter [Surplus < 0]    ──→ Shed tier 3 (luxury)
Power Meter [Surplus < -50]  ──→ Shed tier 2 (secondary production)
Power Meter [Surplus < -100] ──→ Shed tier 1 (keep only food + water)
```

---

### 18. Battery Conservation `⚡ Intermediate`
**Challenge:** Preserve battery charge for nighttime or drought.

**Buildings:** Power Meter (battery < 50) + Chronometer (night) + Relay (AND)

**Wiring:**
```
Power Meter [Battery < 50%] ──→ Relay (AND) ──→ Only run essentials at night when battery low
Chronometer [night hours]   ──→
```

---

### 19. Drought Power Switch `🟢 Beginner`
**Challenge:** Switch from water-based power to alternative power during drought.

**Buildings:** Weather Station (drought) + Power generators

**Wiring:**
```
Weather Station [drought] ──→ Deactivate water wheels (no water flow)
                          ──→ Activate treadmills / engines
```

---

### 20. Peak Demand Scheduling `⚡ Intermediate`
**Challenge:** Stagger power-hungry buildings to avoid simultaneous demand spikes.

**Buildings:** Timer (oscillator) × multiple + Power-heavy workplaces

**Wiring:**
```
Timer A (Oscillator, T1: 4h ON, T2: 4h OFF, offset 0h)  ──→ Smelter #1
Timer B (Oscillator, T1: 4h ON, T2: 4h OFF, offset 4h)  ──→ Smelter #2
```

**Logic:** Stagger oscillators so heavy consumers never run simultaneously. Halves your peak power demand.

---

### 21. Renewable Priority `⚡ Intermediate`
**Challenge:** Prefer renewable power sources and only use engines when renewables fall short.

**Buildings:** Power Meter (supply < demand) + Relay (AND) + Engines

**Wiring:**
```
Power Meter [Surplus < 0]   ──→ Activate backup engines
Power Meter [Surplus >= 20] ──→ Relay (NOT) ──→ Deactivate engines (renewables sufficient)
```

**Use hysteresis** (see pattern #42) to prevent engine flicker when supply hovers near demand.

---

## 🏠 Population & Workforce

### 22. Housing Alert `🟢 Beginner`
**Challenge:** Know when you need more housing before beavers become homeless.

**Buildings:** Population Counter (free beds < 5) + Indicator (pinned, warning)

**Wiring:**
```
Population Counter [Free beds < 5] ──→ Indicator [warning ON, journal entry]
```

---

### 23. Unemployment Response `🟢 Beginner`
**Challenge:** Automatically adjust production capacity based on available workforce.

**Buildings:** Population Counter (unemployed > 5) + Dormant workplaces

**Wiring:**
```
Population Counter [Unemployed > 5] ──→ Activate expansion workplace
```

**Inverse:**
```
Population Counter [Vacancies > 10] ──→ Relay (NOT) ──→ Pause luxury production
```

---

### 24. Contamination Workforce Compensation `⚡ Intermediate`
**Challenge:** When workers get contaminated, boost essential production to compensate.

**Buildings:** Population Counter (contaminated adults > 3) + Workplaces

**Wiring:**
```
Population Counter [Contaminated > 3] ──→ Pause non-essentials
                                       ──→ Indicator [contamination warning]
```

---

### 25. Population Growth Control `⚡ Intermediate`
**Challenge:** Manage population growth by controlling housing availability.

**Buildings:** Population Counter (total population) + Resource Counter (food) + Relay (AND) + Housing

**Wiring:**
```
Population Counter [Population > 80] ──→ Relay (AND) ──→ Deactivate extra housing
Resource Counter [Food < 100]        ──→
```

**Logic:** If population is high AND food reserves are low, stop providing new housing. Population stabilizes naturally.

---

### 26. Child-to-Adult Ratio Workforce Planning `⚡ Intermediate`
**Challenge:** Anticipate future workforce by monitoring children who will become workers.

**Buildings:** Population Counter (children > threshold) + Timer (delay) + Expansion workplaces

**Wiring:**
```
Population Counter [Children > 10] ──→ Timer (Delay, T1: several days) ──→ Pre-activate workplaces
```

**Logic:** A large cohort of children means a workforce boom is coming. Start building capacity now so there are jobs waiting when they grow up.

---

### 27. Bot Workforce Expansion `🟢 Beginner`
**Challenge:** Supplement beaver workforce with bots when organic workers are insufficient.

**Buildings:** Population Counter (vacancies > threshold) + Bot-related workplaces

**Wiring:**
```
Population Counter [Vacancies > 15] ──→ Activate bot assembly
Population Counter [Vacancies < 3]  ──→ Relay (NOT) ──→ Pause bot assembly
```

---

## ⏰ Time-Based Automation

### 28. Day/Night Production Cycling `🟢 Beginner`
**Challenge:** Run power-hungry production only during work hours.

**Buildings:** Chronometer (working hours) + Workplaces

**Wiring:**
```
Chronometer [working hours] ──→ Activate factory production
```

---

### 29. Periodic Maintenance Cycles `🟢 Beginner`
**Challenge:** Run a pump or valve on a duty cycle.

**Buildings:** Timer (oscillator) + Lever (trigger) + Pump/valve

**Wiring:**
```
Lever [ON] ──→ Timer (Oscillator, T1: 6h ON, T2: 2h OFF) ──→ Pump
```

---

### 30. Delayed Emergency Escalation `⚡ Intermediate`
**Challenge:** Don't overreact to brief sensor blips — only escalate if a condition persists.

**Buildings:** Sensor + Timer (accumulator) + Emergency buildings

**Wiring:**
```
Depth Sensor [< 0.3m] ──→ Timer (Accumulator, T1: 2 hours) ──→ EMERGENCY: all pumps ON
```

**Logic:** Only fires after low-water has persisted for 2 continuous hours. Brief dips don't trigger false alarms.

---

### 31. Nighttime Security Lockdown `🟢 Beginner`
**Challenge:** Close district gates at night to keep beavers safe.

**Buildings:** Chronometer (non-working hours) + Gates

**Wiring:**
```
Chronometer [non-working hours] ──→ Close outer district gates
```

---

### 32. Seasonal Work Schedule `⚡ Intermediate`
**Challenge:** Shift production focus based on season — farm-heavy in temperate, processing-heavy in drought.

**Buildings:** Weather Station + Chronometer + Workplaces

**Wiring:**
```
Weather Station [temperate] ──→ Activate farms, foresters, gathering
Weather Station [drought]   ──→ Activate processing (bakeries, mills, workshops)
                            ──→ Deactivate farms (nothing grows anyway)
```

**Logic:** Don't waste drought labor on farms that can't produce. Shift the workforce to processing stored raw materials.

---

### 33. Timed Breeding Pulse `⚡ Intermediate`
**Challenge:** Control population growth by enabling housing in timed bursts.

**Buildings:** Timer (pulse, T1: 2 days) + Lever (manual trigger) + Housing

**Wiring:**
```
Lever [manual ON] ──→ Timer (Pulse, T1: 2 days) ──→ Activate breeding pods/extra housing
```

**Logic:** Manual lever trigger allows exactly one 2-day breeding pulse. Housing deactivates automatically after the pulse. Precise population control.

---

## 🔔 Monitoring & Alerts

### 34. Colony Health Dashboard (In-Game) `🟢 Beginner`
**Challenge:** See colony status at a glance without clicking through buildings.

**Buildings:** Multiple sensors + Indicators (pinned, color-coded)

**Wiring:**
```
Resource Counter [Food < 50]       ──→ Indicator [RED, pinned, warning]
Depth Sensor [Water < 1m]          ──→ Indicator [RED, pinned, warning]
Population Counter [Homeless > 0]  ──→ Indicator [YELLOW, pinned, warning]
Power Meter [Surplus < 0]          ──→ Indicator [RED, pinned, warning]
```

---

### 35. External Dashboard via HTTP `⚡ Intermediate`
**Challenge:** Monitor colony from a web browser (second monitor setup).

**Buildings:** Sensors → HTTP Adapters

**Wiring:**
```
Resource Counter [Food < 50]  ──→ HTTP Adapter "Food Low"
                                  ON:  http://localhost:8081/on/Food%20Low
                                  OFF: http://localhost:8081/off/Food%20Low

Depth Sensor [Water < 1m]    ──→ HTTP Adapter "Water Critical"
                                  ...same pattern...
```

---

### 36. Audio Alerts for Critical Events `🟢 Beginner`
**Challenge:** Get an audible warning for urgent situations (useful when zoomed elsewhere on the map).

**Buildings:** Critical sensor → Speaker (non-spatial, play once)

**Wiring:**
```
Weather Station [drought] ──→ Speaker [non-spatial, play once, alarm sound]
```

---

### 37. Multi-Level Warning System `⚡ Intermediate`
**Challenge:** Escalating alerts — yellow warning, then red alarm, then audio.

**Buildings:** Multiple sensors at different thresholds + Indicators + Speaker

**Wiring:**
```
Resource Counter [Food < 80]  ──→ Indicator [YELLOW, pinned]         (advisory)
Resource Counter [Food < 40]  ──→ Indicator [RED, pinned, warning]   (warning)
Resource Counter [Food < 15]  ──→ Speaker [alarm, non-spatial]       (critical)
                              ──→ Indicator [RED, journal entry]
```

---

### 38. Automation System Health Monitor `🟢 Beginner`
**Challenge:** Verify that your automation is working correctly.

**Buildings:** Lever (test signal) + Relay (passthrough chain) + Indicator (end of chain)

**Wiring:**
```
Lever [test] ──→ Relay (Pass) ──→ Relay (Pass) ──→ ... ──→ Indicator [system OK]
```

**Logic:** Toggle the test lever. If the indicator at the end of the chain lights up, your entire logic chain is wired correctly. A debugging tool for complex setups.

---

### 39. District Status Beacons `⚡ Intermediate`
**Challenge:** Monitor multiple districts from your main base.

**Buildings:** Per-district sensors + Indicators (pinned always, replicate color)

**Wiring (per district):**
```
Population Counter [district, homeless > 0]  ──→ Indicator "District A Housing"
Resource Counter [district, food < 20]       ──→ Indicator "District A Food"
Depth Sensor [district reservoir]            ──→ Indicator "District A Water"
```

**Enhancement:** Use color replication on indicators — green means OK, red means alert, visible from anywhere on the map.

---

## 🎆 Fun & Celebrations

### 40. Population Milestone Fireworks `🟢 Beginner`
**Challenge:** Celebrate when your colony hits a population milestone.

**Buildings:** Population Counter (> milestone) + Firework Launchers

**Wiring:**
```
Population Counter [Population > 100] ──→ Firework Launcher [Kamuro gold, continuous]
```

---

### 41. Automated Dam Break `⚡ Intermediate`
**Challenge:** Controlled demolition of a temporary dam when water levels are sufficient.

**Buildings:** Depth Sensor + Timer (delay) + Detonator

**Wiring:**
```
Depth Sensor [> 4m] ──→ Timer (Delay, T1: 30 seconds) ──→ Detonator ──→ 💥
```

**⚠️ IRREVERSIBLE.** Add a manual Lever as a safety interlock (AND with sensor so both must be active).

---

### 42. Drought Survival Celebration `🔴 Advanced`
**Challenge:** Automatically celebrate when the colony survives a drought.

**Buildings:** Weather Station (temperate) + Memory (toggle) + Timer (pulse) + Fireworks + Speaker

**Wiring:**
```
Weather Station [drought]   ──→ Memory (Set-Reset) SET
Weather Station [temperate] ──→ Memory RESET ──→ Timer (Pulse, T1: 30 ticks) ──→ Fireworks!
                                                                              ──→ Speaker [fanfare]
```

**Logic:** Memory tracks that a drought happened. When temperate returns and resets the memory, the pulse fires a one-time celebration. No celebration if there was no drought to survive.

---

### 43. Science Milestone Announcements `🟢 Beginner`
**Challenge:** Mark research progress with in-game fanfare.

**Buildings:** Science Counter (> milestones) + Firework Launchers + Speaker

**Wiring:**
```
Science Counter [> 500]  ──→ Timer (Pulse, T1: 10 ticks) ──→ Firework [Peony violet]
Science Counter [> 1000] ──→ Timer (Pulse, T1: 20 ticks) ──→ Firework [Palm gold] × 3
```

---

## 🧠 Advanced Patterns

### 44. Priority System `🔴 Advanced`
**Challenge:** When multiple resources are low, prioritize the most critical.

**Pattern:** Use layered NOT gates to create priority tiers:
```
Resource Counter [Food < 20]   ──→ Priority 1: ALL non-food production stops
Resource Counter [Water < 1m]  ──→ Priority 1: Emergency pumps activate
Resource Counter [Logs < 30]   ──→ Priority 2: Boost forestry (only if food OK)
Resource Counter [Gears < 10]  ──→ Priority 3: Boost gears (only if food + logs OK)
```

Wire higher-priority signals through NOT relays to suppress lower-priority actions.

---

### 45. Hysteresis (Anti-Flicker) `🔴 Advanced`
**Challenge:** A sensor at its threshold causes rapid on/off toggling.

**Pattern:** Use Memory (Set-Reset) with two sensors at different thresholds:
```
Resource Counter [Logs < 30]  ──→ Memory (Set-Reset) SET    ──→ Activate Forester
Resource Counter [Logs > 60]  ──→ Memory (Set-Reset) RESET
```

**Logic:** Creates a dead zone between 30–60 that prevents flicker. Production starts at 30, doesn't stop until 60.

---

### 46. Timed Drought Response Escalation `🔴 Advanced`
**Challenge:** Escalate emergency measures the longer a drought persists.

**Pattern:** Chain accumulators:
```
Weather Station [drought] ──→ Timer (Accum, 0h)  ──→ Phase 1: Close outer gates
                          ──→ Timer (Accum, 6h)  ──→ Phase 2: Activate pumps, reduce power
                          ──→ Timer (Accum, 12h) ──→ Phase 3: Shut down all non-essential
                          ──→ Timer (Accum, 24h) ──→ Phase 4: Emergency rations mode
```

---

### 47. External Multi-Condition Logic `🔴 Advanced`
**Challenge:** Rules too complex for in-game relay chains.

**Pattern:** Bridge to external controller:
```
Sensors ──→ HTTP Adapters ──→ External Controller (Python) ──→ HTTP Levers ──→ Buildings
```

The controller's YAML config can express arbitrarily complex rules that would require dozens of in-game relays.

---

### 48. State Machine Colony Manager `🔴 Advanced`
**Challenge:** Colony operates in distinct modes (Growth, Maintenance, Drought Prep, Emergency) with different building configurations per mode.

**Pattern:** Use Memory cells to define states, with transition logic:
```
                    ┌─── Memory A (Growth Mode) ──→ All production ON, extra housing ON
                    │
Sensor inputs ──→ Logic ─── Memory B (Maintenance) ──→ Balanced production, normal housing
                    │
                    └─── Memory C (Emergency) ──→ Essentials only, all reserves open
```

**Transitions:**
- Growth → Maintenance: Population Counter [> 80] flips state
- Maintenance → Emergency: Weather Station [drought] + Depth Sensor [< 1m]
- Emergency → Maintenance: Weather Station [temperate] + Timer (delay, ensure stability)

**This is the most complex in-game automation pattern** — essentially a finite state machine built from Memory cells and relays. For extreme complexity, offload to the external controller.

---

### 49. Adaptive Production Optimizer `🔴 Advanced`
**Challenge:** Automatically optimize resource production ratios based on real-time consumption.

**Pattern:** Use oscillating timers to create sampling windows:
```
Timer (Oscillator, T1: 1 day, T2: 1 tick) ──→ "Sample" trigger

On each sample:
  Resource Counter [Logs] state ──→ Memory (Latch) ──→ "Logs snapshot"
  Compare snapshot to previous via relay chain
  If declining: boost production
  If stable/growing: maintain or reduce
```

**Reality check:** This pushes in-game logic to its limits. Easier to implement via external controller reading adapter states over time and computing trends. The controller can track adapter state history and make trend-based decisions that pure binary signals can't express.

---

### 50. Full Colony Autopilot `🔴 Advanced`
**Challenge:** A comprehensive automation system that handles water, resources, power, and population with minimal player intervention.

**Pattern:** Combines patterns from this guide into a layered system:

**Layer 1 — Monitoring (always on):**
- All sensors → Indicators (colony dashboard, pattern #34)
- All sensors → HTTP Adapters (external dashboard, pattern #35)

**Layer 2 — Reactive (event-driven):**
- Weather Station → drought/badtide response (patterns #1, #3, #19)
- Resource Counters → production balancing (pattern #11)
- Power Meter → load shedding (pattern #17)

**Layer 3 — Proactive (time-based):**
- Chronometer → day/night cycling (pattern #28)
- Timer oscillators → maintenance cycles (pattern #29)
- Seasonal work schedule (pattern #32)

**Layer 4 — Strategic (external controller):**
- HTTP bridge → complex multi-condition logic (pattern #47)
- State machine mode management (pattern #48)
- Trend analysis and adaptive optimization (pattern #49)

**Layer 5 — Safety (override):**
- Hysteresis on all thresholds (pattern #45)
- Delayed escalation to prevent false alarms (pattern #30)
- Priority system ensures critical needs override everything (pattern #44)
- Manual lever safety interlocks on all destructive actions

**The goal isn't to remove the player — it's to free the player to focus on design, expansion, and creativity while the colony runs itself smoothly.**

---

*50 patterns | Last updated: March 2026 | Timberborn 1.0*
