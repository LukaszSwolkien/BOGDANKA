# Simulation Services Implementation Plan

Reference specification: `src/simulation/simulation.md`

---

## Phase 0 – Shared Foundation
1. **Config loader & validation**
   - Implement shared module to load `config.yaml`, expose typed dataclasses.
   - Support subset defined in spec (telemetry, acceleration, durations, endpoints); log TODOs for unsupported knobs.
2. **Telemetry bootstrap**
   - Create helper to configure OTLP metric exporter with placeholder headers.
   - Ensure metrics go to Splunk, logs remain local.
3. **Time acceleration helper**
   - Provide utility class that converts real-time seconds into accelerated simulation time.
   - No cross-service sync required.
4. **Domain models**
   - Define enums/structs for scenarios (S0-S8), lines (C1/C2), heater identifiers, lock states.
5. **Testing harness setup**
   - Choose pytest; configure structure for unit/integration tests shared by both services.

---

## Phase 1 – Weather Service
1. **HTTP API skeleton**
   - Flask/FastAPI app with `GET /temperature`.
   - Include simulation timestamp, temperature, profile metadata in response.
2. **Temperature generator**
   - Implement 90-day winter curve (cooling to min, warming to final) with daily sine variation and Gaussian noise.
   - Parameters driven by config defaults; allow overriding.
3. **Simulation scheduler**
   - Loop advancing accelerated time; recompute temperature each poll.
   - Ensure default duration = 90 days (configurable).
4. **Telemetry emission**
   - Metrics: `external_temperature`, `simulation_day`, `requests_total`, `errors_total`.
   - Log local JSON events for service start, config load, errors.
5. **Configuration exposure**
   - Provide CLI/options to point to weather config section; document usage in README.
6. **Unit tests**
   - Verify temperature profile hits required ranges (S0-S8) across 90-day span.
   - Test endpoint response structure and simulation time progression.

---

## Phase 2 – Algo Service
1. **Client integration**
   - HTTP client polling weather endpoint every `temp_monitoring_cycle_s`.
   - Handle retries/backoff per spec.
2. **State engine**
   - Implement data structures mirroring pseudocode global variables (scenarios, locks, timers, counters).
3. **Algorithm WS implementation**
   - Translate pseudocode line-by-line, including hysteresis, awaria handling, coordination locks, scenario execution workflow.
4. **Algorithm RC implementation**
   - Implement rotation logic, timers, lock coordination with RN.
5. **Algorithm RN implementation**
   - Implement per-line rotation logic, delta checks, prioritization.
6. **Console dashboard (MVP requirement)**
   - ANSI two-zone view (status header + event log) updated each loop.
7. **Telemetry**
   - Emit all required metrics (WS, RC, RN, heaters, locks, rotation durations).
   - Local structured logs for scenario changes, rotations, lock waits.
8. **Unit tests for algorithms**
   - WS tests covering temperature bands, hysteresis, lock handling.
   - RC tests for rotation timing, lock coordination with RN.
   - RN tests for heater selection, delta thresholds, lock respect.
   - Mock time advancement to cover accelerated scheduling.
9. **Integration harness**
   - Provide CLI to run full 90-day accelerated simulation with configurable duration.

---

## Phase 3 – Verification & Documentation
1. **End-to-end dry run**
   - Run both services locally with acceleration; verify metrics reach Splunk (placeholder credentials).
2. **Console verification**
   - Capture sample output matching spec’s Expected Console Output section.
3. **Testing report**
   - Summarize unit/integration coverage for WS/RC/RN.
4. **Documentation updates**
   - Update `src/simulation/README.md` with run instructions, config examples, known limitations.
5. **Backlog tracking**
   - Log unsupported config knobs and future enhancements (e.g., Splunk log export, broader profile tuning).

