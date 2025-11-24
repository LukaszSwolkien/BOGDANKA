# BOGDANKA System Simulation Implementation

**Goal:** Generate Python microservices for simulating BOGDANKA Shaft 2 heating control algorithms with Splunk Observability

---

## 📋 Instructions for the implementation

### Context

This prompt provides **implementation specifications** for building a simulation system. 

**Algorithm logic is documented separately:**
📖 **Complete algorithm documentation:** [../../docs/03-algorytmy/algorytmy.md](../../docs/03-algorytmy/algorytmy.md)

**This file contains ONLY:**
- 🏗️ Service architecture (2 microservices)
- 🔧 Tech stack and libraries
- 📊 Telemetry specifications for Splunk Observability
- ⚙️ Configuration structure
- 📝 Coding standards
- 🌡️ Temperature profile generator (simulation-specific)

---

## 🧱 Service Architecture

### Overview

The simulation consists of **two independent microservices** that communicate via HTTP and send telemetry to **Splunk Observability Cloud** via OTLP:

```
┌─────────────────────┐         HTTP GET          ┌─────────────────────┐
│                     │ /temperature              │                     │
│  Weather Service    ├──────────────────────────►│   Algo Service      │
│  (Port 8080)        │                           │                     │
│                     │                           │                     │
│ • T_zewn generator  │                           │ • Algorithm WS      │
│ • Winter profile    │                           │ • Algorithm RC      │
│ • Sine wave + noise │                           │ • Algorithm RN      │
└──────────┬──────────┘                           └──────────┬──────────┘
           │                                                 │
           │ OTLP Metrics/Logs                               │ OTLP Metrics/Logs
           │ bogdanka.weather.*                              │ bogdanka.algo.*
           │                                                 │
           └────────────────────┬────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Splunk Observability │
                    │  (OTLP Endpoint)      │
                    └───────────────────────┘
```

### Service 1: Weather Service

**Responsibility:** Simulate realistic external temperature for comprehensive winter testing

**Key Features:**
- Generates realistic winter temperature profile that tests **ALL scenarios S0-S8**
- Temperature progression: +5°C (autumn) → -25°C (harsh winter) → +3°C (spring)
- Daily temperature variations (day/night cycle)
- Gaussian noise for realistic fluctuations
- REST API endpoint: `GET /temperature`
- Time acceleration support from config

**Telemetry to Splunk:**
- Metric: `bogdanka.weather.external_temperature` (gauge, °C)
- Metric: `bogdanka.weather.simulation_day` (gauge, days, 0-30)
- Metric: `bogdanka.weather.requests_total` (counter)
- Log: Profile initialization, parameter changes

### Service 2: Algo Service

**Responsibility:** Implement and test control algorithms WS, RC, RN

**Key Features:**
- Polls weather service for `T_zewn` every 10s (configurable)
- Implements three algorithms from documentation:
  - **WS:** Scenario selection S0-S8
  - **RC:** Configuration rotation (Primary ↔ Limited)
  - **RN:** Heater rotation within lines
- Maintains global system state (scenarios, locks, counters)
- Time acceleration support (synchronized with weather service)

**Telemetry to Splunk:**
- Metrics for scenario changes, rotations, operating times
- Structured JSON logs for key events
- All analysis performed in Splunk (no local CSV/PNG files)

### Configuration File

Both services use **single shared configuration file**: `src/simulation/config.yaml`

Key sections:
- `simulation.acceleration` - Common time acceleration (e.g., 1000x)
- `telemetry.*` - OTLP endpoints, headers, dimensions, log level
- `services.weather.*` - Weather service settings, port, profile parameters
- `services.algo.*` - Algo service settings, weather endpoint
- `services.algo.algorithms.*` - Algorithm parameters (WS, RC, RN) for tuning

### Time Acceleration

Both services support **time acceleration** for fast testing:
- **acceleration = 1000** means: 1 second of simulation = 1000 seconds (~16.7 minutes) of real time
- 30 days of operation can be simulated in ~43 minutes
- Read from `simulation.acceleration` in config
- All timing parameters (rotation periods, gaps, cycles) are in simulation time

---

## 🎯 Implementation Requirements

### Service 1: Weather Service (`weather_service.py`)

**HTTP Server:**
- Flask/FastAPI server on configurable port (default: 8080)
- Endpoint: `GET /temperature` returns JSON:
  ```json
  {
    "timestamp": "2025-11-24T10:30:00Z",
    "t_zewn": -12.4,
    "simulation_time": 86400,
    "profile": {
      "initial_temp": 5.0,
      "min_temp": -25.0,
      "final_temp": 3.0
    }
  }
  ```

**Temperature Generator:**
- Realistic winter profile: cooling (15 days) + warming (15 days)
- Must test ALL scenarios S0-S8 over 30-day period
- Daily variation: ±3°C day/night cycle
- Gaussian noise (sigma from config)

**Telemetry:**
- Initialize OTLP exporter from `telemetry.*` config
- Emit metrics to Splunk Observability
- Resource attributes: `service.name=bogdanka-weather`, `environment=dev`

### Service 2: Algo Service (`algo_service.py`)

**Algorithm Implementation:**
- Read algorithm pseudocode from [../../docs/03-algorytmy/algorytmy.md](../../docs/03-algorytmy/algorytmy.md)
- Implement WS, RC, RN exactly as documented
- Use all coordination mechanisms (locks, time gaps)

**Weather Integration:**
- Poll `GET {weather_endpoint}/temperature` every `services.algo.algorithms.ws.temp_monitoring_cycle_s`
- Handle connection errors (retry with backoff)

**Telemetry:**
- Emit comprehensive metrics (see specifications below)
- Structured JSON logs for all events
- NO CSV exports, NO PNG charts - all analysis in Splunk

---

## 📊 Telemetry Specifications for Splunk Observability

### OTLP Configuration

Both services read telemetry configuration from `config.yaml`:

```yaml
telemetry:
  exporter_type: "otlp"  # or "console" for testing
  endpoints:
    metrics: "https://ingest.signalfx.com/v2/datapoint/otlp"
  headers:
    X-SF-Token: "<YOUR_SF_TOKEN>"
    Content-Type: "application/x-protobuf"
  resource_attributes:
    environment: "dev"
    project: "bogdanka-simulation"
  default_dimensions:
    site: "Szyb-2"
  log_level: "INFO"
```

**Implementation:**
- Use OpenTelemetry Python SDK
- For `exporter_type: "otlp"`: configure `OTLPMetricExporter` with endpoints/headers
- For `exporter_type: "console"`: use `ConsoleMetricExporter` for local testing
- Apply `resource_attributes` to all telemetry
- Add `default_dimensions` to all metrics

### Weather Service Metrics

| Metric Name | Type | Unit | Dimensions | Description |
|------------|------|------|------------|-------------|
| `bogdanka.weather.external_temperature` | Gauge | °C | site | Current external temperature |
| `bogdanka.weather.simulation_day` | Gauge | days | site | Current simulation day (0-30) |
| `bogdanka.weather.requests_total` | Counter | count | site | Total API requests served |
| `bogdanka.weather.errors_total` | Counter | count | site, error_type | Total errors encountered |

### Algo Service Metrics

**⚠️ CRITICAL: These metrics enable ALL analysis in Splunk - no local files needed**

| Metric Name | Type | Unit | Dimensions | Description | Use in Splunk |
|------------|------|------|------------|-------------|---------------|
| `bogdanka.algo.ws.scenario` | Gauge | 0-8 | site | Current active scenario | Chart current scenario over time |
| `bogdanka.algo.ws.scenario_time_s` | Counter | seconds | site, scenario | **Time spent in each scenario** | Calculate % time in S0-S8 |
| `bogdanka.algo.ws.scenario_changes` | Counter | count | site, from_scenario, to_scenario | Scenario transitions | Count transitions, analyze patterns |
| `bogdanka.algo.ws.temperature_external` | Gauge | °C | site | External temperature | Correlate temp with scenario changes |
| `bogdanka.algo.rc.current_config` | Gauge | 0/1 | site | Current config (0=Primary, 1=Limited) | Chart config over time |
| `bogdanka.algo.rc.config_time_s` | Counter | seconds | site, config | **Time in each config** | Calculate Primary/Limited balance |
| `bogdanka.algo.rc.rotation_count` | Counter | count | site, from_config, to_config | Config rotations | Count RC events |
| `bogdanka.algo.rc.rotation_duration_s` | Histogram | seconds | site | RC rotation duration | Analyze rotation performance |
| `bogdanka.algo.heater.active` | Gauge | 0/1 | site, heater | **Current heater state** | Monitor real-time heater status |
| `bogdanka.algo.heater.operating_time_s` | Counter | seconds | site, heater | **Cumulative operating time per heater** | Calculate balance N1-N8, time % |
| `bogdanka.algo.heater.idle_time_s` | Counter | seconds | site, heater | **Cumulative idle time per heater** | Calculate idle %, verify balance |
| `bogdanka.algo.rn.rotation_count` | Counter | count | site, line, heater_from, heater_to | Heater rotations | Count RN events, analyze patterns |
| `bogdanka.algo.rn.rotation_duration_s` | Histogram | seconds | site, line | RN rotation duration | Analyze rotation performance |
| `bogdanka.algo.locks.wait_events` | Counter | count | site, lock_type, requesting_algo | Lock wait occurrences | Detect coordination issues |
| `bogdanka.algo.locks.wait_duration_s` | Histogram | seconds | site, lock_type | Lock wait duration | Analyze coordination delays |

**Metric Update Frequency:**
- Update counters every simulation step (every 10s)
- This ensures accurate time tracking for all calculations in Splunk

### Structured Logging

All logs should be JSON-formatted with these fields:

**Common Fields:**
```json
{
  "timestamp": "2025-11-24T10:30:00Z",
  "service": "bogdanka-algo",
  "level": "INFO",
  "simulation_time": 86400,
  "message": "...",
  "event_type": "..."
}
```

**Event Types:**

1. **Scenario Change:**
```json
{
  "event_type": "scenario_change",
  "from_scenario": "S3",
  "to_scenario": "S4",
  "t_zewn": -9.2
}
```

2. **RC Rotation:**
```json
{
  "event_type": "rc_rotation",
  "from_config": "Primary",
  "to_config": "Limited",
  "duration_s": 45
}
```

3. **RN Rotation:**
```json
{
  "event_type": "rn_rotation",
  "line": "C1",
  "heaters_activated": ["N2"],
  "heaters_deactivated": ["N1"]
}
```

4. **Lock Conflict:**
```json
{
  "event_type": "lock_wait",
  "lock_type": "config_change_in_progress",
  "wait_s": 15
}
```

### Example Splunk Queries

```python
# Heater operating time (seconds) - bar chart
data('bogdanka.algo.heater.operating_time_s', rollup='latest').sum(by=['heater']).publish(label='Operating Time')

# Heater operating percentage calculation
A = data('bogdanka.algo.heater.operating_time_s', rollup='latest').sum(by=['heater'])
B = data('bogdanka.algo.heater.idle_time_s', rollup='latest').sum(by=['heater'])
C = (A / (A + B) * 100).publish(label='Operating %')

# Time in each scenario - pie chart
data('bogdanka.algo.ws.scenario_time_s', rollup='latest').sum(by=['scenario']).publish(label='Scenario Distribution')

# Configuration balance ratio
A = data('bogdanka.algo.rc.config_time_s', filter=filter('config', 'Primary'), rollup='latest').sum()
B = data('bogdanka.algo.rc.config_time_s', filter=filter('config', 'Limited'), rollup='latest').sum()
(A / B).publish(label='Primary/Limited Ratio')

# Heater balance metric (max-min difference %)
A = data('bogdanka.algo.heater.operating_time_s', rollup='latest').max(by=['heater'])
B = data('bogdanka.algo.heater.operating_time_s', rollup='latest').min(by=['heater'])
C = data('bogdanka.algo.heater.operating_time_s', rollup='latest').mean(by=['heater'])
((A - B) / C * 100).publish(label='Heater Balance %')
```

---

## 🌡️ Realistic Temperature Profile - Testing All Scenarios

### Requirement

The weather service **must generate a realistic winter temperature profile** that ensures all 9 scenarios (S0-S8) are tested during the 30-day simulation.

### Temperature Ranges for Scenarios

| Scenario | Temperature Range | Description |
|----------|------------------|-------------|
| **S0** | T ≥ 3°C | No heating needed (autumn/spring) |
| **S1** | 2°C to -1°C | Minimal heating (1 heater) |
| **S2** | -1°C to -4°C | Light cold (2 heaters) |
| **S3** | -4°C to -8°C | Moderate cold (3 heaters) |
| **S4** | -8°C to -11°C | Cold (4 heaters) |
| **S5** | -11°C to -15°C | Severe cold (5 heaters) |
| **S6** | -15°C to -18°C | Extreme cold (6 heaters) |
| **S7** | -18°C to -21°C | Harsh cold (7 heaters) |
| **S8** | T < -21°C | Maximum cold (8 heaters) |

### Recommended Profile: 30-Day Winter Cycle

```python
# Realistic winter temperature profile (30 days)
# Days 1-15: Autumn → Harsh Winter (cooling phase)
# Days 16-30: Harsh Winter → Early Spring (warming phase)

Day  | Avg Temp | Scenarios Expected
-----|----------|-------------------
1-2  | +4°C     | S0 (no heating)
3-4  | +1°C     | S1 (1 heater)
5-6  | -2°C     | S2 (2 heaters)
7-8  | -6°C     | S3 (3 heaters)
9-10 | -9°C     | S4 (4 heaters)
11-12| -13°C    | S5 (5 heaters)
13-14| -16°C    | S6 (6 heaters)
15-16| -19°C    | S7 (7 heaters)
17-18| -23°C    | S8 (8 heaters) ← PEAK WINTER
19-20| -19°C    | S7 (7 heaters)
21-22| -16°C    | S6 (6 heaters)
23-24| -13°C    | S5 (5 heaters)
25-26| -9°C     | S4 (4 heaters)
27-28| -5°C     | S3 (3 heaters)
29-30| +2°C     | S0-S1 (warming up)
```

### Implementation Formula

```python
def calculate_temperature(day, hour):
    """
    Generate realistic temperature that tests all scenarios.
    
    Args:
        day: Simulation day (0-29)
        hour: Hour of day (0-23)
    
    Returns:
        Temperature in °C
    """
    # Configuration from config.yaml
    initial_temp = 5.0      # Starting temperature (autumn)
    min_temp = -25.0        # Coldest point (harsh winter)
    final_temp = 3.0        # Ending temperature (spring)
    cooling_days = 15       # Days to reach minimum
    warming_days = 15       # Days to warm up
    daily_variation = 3.0   # Day/night temperature swing
    noise_sigma = 0.5       # Random fluctuations
    
    # Main trend: cooling then warming
    if day <= cooling_days:
        # Cooling phase: smooth transition from initial to minimum
        progress = day / cooling_days
        trend_temp = initial_temp - (initial_temp - min_temp) * progress
    else:
        # Warming phase: smooth transition from minimum to final
        progress = (day - cooling_days) / warming_days
        trend_temp = min_temp + (final_temp - min_temp) * progress
    
    # Daily variation (day is warmer, night is colder)
    daily_cycle = daily_variation * math.sin(2 * math.pi * hour / 24)
    
    # Random noise for realism
    noise = random.gauss(0, noise_sigma)
    
    # Final temperature
    T_zewn = trend_temp + daily_cycle + noise
    
    # Emit metrics:
    # - bogdanka.weather.external_temperature = T_zewn
    # - bogdanka.weather.simulation_day = day
    
    return T_zewn
```

---

## 📦 Technical Requirements

### Python Libraries

```python
# Standard library
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import time                  # time acceleration
import logging               # structured logging
import json                  # JSON logs
import math                  # temperature calculations
import random                # noise generation

# External dependencies
import yaml                  # configuration
import requests              # HTTP client
from flask import Flask, jsonify  # HTTP server (weather service)

# OpenTelemetry
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
```

### File Structure

```
src/simulation/
├── config.yaml                 # Shared configuration
├── weather_service.py          # Weather service implementation
├── algo_service.py             # Algo service implementation
├── telemetry_config.py         # Shared telemetry setup (OTLP)
├── pyproject.toml              # Python dependencies (uv)
├── uv.lock                     # Lock file (auto-generated)
└── README.md                   # Setup and usage instructions

Note: No local output files - all results in Splunk Observability
```

---

## 📝 Coding Standards

**Code Language:** All code (variables, functions, classes) must be written in **English**.

**Logging:** Use structured JSON logs for all events (see examples in Structured Logging section above).

**Metric Names:** Follow OpenTelemetry conventions - hierarchical, snake_case (see Telemetry Specifications section above).

---

## ⏱️ Time Acceleration Implementation

### Concept

Time acceleration allows simulating long periods (30 days) in short real time (~43 minutes):

```
acceleration = 1000
├─ 1 second real time = 1000 seconds simulation time (~16.7 minutes)
├─ 1 minute real time = 60,000 seconds simulation time (~16.7 hours)
└─ 43 minutes real time = 2,592,000 seconds simulation time (30 days)
```

### Implementation Requirements

**Both services must use the same acceleration value from config:**

```yaml
simulation:
  acceleration: 1000
```

### Weather Service Time Handling

```python
class WeatherService:
    def __init__(self, config):
        self.acceleration = config['simulation']['acceleration']
        self.start_time_real = time.time()  # Real time
        
    def get_simulation_time(self):
        """Calculate current simulation time"""
        elapsed_real = time.time() - self.start_time_real
        return elapsed_real * self.acceleration
    
    def get_temperature(self):
        sim_time = self.get_simulation_time()
        t_zewn = self.profile.calculate_temp(sim_time)
        return {
            "timestamp": datetime.now().isoformat(),
            "t_zewn": t_zewn,
            "simulation_time": sim_time  # Include for sync
        }
```

### Algo Service Time Handling

```python
class AlgoService:
    def __init__(self, config):
        self.acceleration = config['simulation']['acceleration']
        self.start_time_real = time.time()
        
    def get_simulation_time(self):
        """Calculate current simulation time"""
        elapsed_real = time.time() - self.start_time_real
        return elapsed_real * self.acceleration
    
    def simulate(self, days=30):
        """Main simulation loop"""
        total_sim_seconds = days * 24 * 3600
        poll_interval_sim = self.config['services']['algo']['algorithms']['ws']['temp_monitoring_cycle_s']
        poll_interval_real = poll_interval_sim / self.acceleration
        
        while self.get_simulation_time() < total_sim_seconds:
            self.simulation_step()
            time.sleep(poll_interval_real)  # Sleep in real time
```

### Key Points

1. **Internal Clocks:** Both services maintain `start_time_real` and calculate `simulation_time`
2. **Synchronization:** Weather service returns `simulation_time` in API response
3. **Sleep Intervals:** Convert simulation time to real time for `time.sleep()`
4. **Metric Timestamps:** Use real wall-clock time for OTLP (Splunk requirement)
5. **Log Timestamps:** Include both real and simulation time for debugging

---

## 🚀 Running the Simulation

### Setup

```bash
# Install uv if not already installed
# https://github.com/astral-sh/uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
cd src/simulation
uv sync
```

### Terminal 1 - Start Weather Service

```bash
cd src/simulation
uv run weather_service.py
# Service starts on http://localhost:8080
# Metrics sent to Splunk Observability
```

### Terminal 2 - Start Algo Service

```bash
cd src/simulation
uv run algo_service.py --days 30
# Polls weather service every 10s
# Runs WS, RC, RN algorithms
# Sends metrics to Splunk Observability
# After 30 days (~43 min real time), completes
```

### Expected Console Output

**Weather Service:**
```
[2025-11-24 10:30:00] INFO: Weather service starting
[2025-11-24 10:30:00] INFO: Configuration loaded from config.yaml
[2025-11-24 10:30:00] INFO: Winter profile: +5°C → -25°C → +3°C
[2025-11-24 10:30:00] INFO: Time acceleration: 1000x (1s = 16.7 min)
[2025-11-24 10:30:00] INFO: OTLP exporter initialized
[2025-11-24 10:30:00] INFO: Starting HTTP server on localhost:8080
```

**Algo Service:**
```
[2025-11-24 10:30:05] INFO: Algo service starting
[2025-11-24 10:30:05] INFO: Configuration loaded from config.yaml
[2025-11-24 10:30:05] INFO: Connecting to weather service: http://localhost:8080
[2025-11-24 10:30:05] INFO: Time acceleration: 1000x
[2025-11-24 10:30:05] INFO: OTLP exporter initialized
[2025-11-24 10:30:05] INFO: Starting simulation: 30 days
[2025-11-24 10:30:15] INFO: {"event_type": "scenario_change", "from": "S0", "to": "S1", "t_zewn": -2.3}
...
[2025-11-24 11:13:00] INFO: Simulation complete (30 days simulated in 43 minutes)
[2025-11-24 11:13:00] INFO: All telemetry sent to Splunk Observability Cloud
[2025-11-24 11:13:00] INFO: Analysis available at: https://app.signalfx.com
```

---

## ✅ Success Criteria

After running simulation for 30 days, verify in Splunk Observability:

1. **Heater balance:** 
   - Query: `(max - min) / avg * 100` of `bogdanka.algo.heater.operating_time_s`
   - Expected: < 10%

2. **Line balance:** 
   - Query: `Primary / Limited` ratio from `bogdanka.algo.rc.config_time_s`
   - Expected: 0.95-1.05

3. **All scenarios tested:**
   - Query: `sum(bogdanka.algo.ws.scenario_time_s) by scenario`
   - Expected: All S0-S8 have non-zero values

4. **No coordination issues:**
   - Query: `bogdanka.algo.locks.wait_events`
   - Expected: < 10 total events

5. **Metrics completeness:**
   - All 15 algo metrics present and updating
   - All 4 weather metrics present and updating

---

## 📄 Algorithm Documentation Reference

**⚠️ IMPORTANT:** This file contains ONLY implementation specifications.

**For algorithm logic, read:**
- **Complete algorithms:** [../../docs/03-algorytmy/algorytmy.md](../../docs/03-algorytmy/algorytmy.md)
  - Algorithm WS: Scenario selection with hysteresis
  - Algorithm RC: Configuration rotation (Primary ↔ Limited)
  - Algorithm RN: Heater rotation within lines
  - Coordination: locks, time gaps, hierarchy

**For system context:**
- **System architecture:** [../../docs/01-system/system.md](../../docs/01-system/system.md)
- **Installation project:** [../../docs/02-projekt-instalacji/projekt-instalacji.md](../../docs/02-projekt-instalacji/projekt-instalacji.md)

---

**Last update:** November 24, 2025  
**Version:** 1.0  
**Focus:** Implementation specifications for simulation microservices
