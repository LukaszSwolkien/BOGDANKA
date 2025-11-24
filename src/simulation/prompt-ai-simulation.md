# AI Prompt - BOGDANKA System Simulation Generation

**Goal:** Generate simulation code for BOGDANKA Shaft 2 heating control system in Python

---

## 📋 Instructions for AI (ChatGPT, Claude, etc.)

### Context

You have access to **complete documentation of three cooperating control algorithms** for shaft heating system:
- **Algorithm WS** - automatic scenario selection (S0-S8) based on external temperature
- **Algorithm RC** - rotation of heating line configurations (Primary ↔ Limited)
- **Algorithm RN** - rotation of heaters within a heating line

📖 **Documentation:** [../../docs/03-algorytmy/algorytmy.md](../../docs/03-algorytmy/algorytmy.md)

> Simulation-specific helper data (global variables, signals, config parameters) was intentionally removed from the general documentation. Use this prompt as the single source of truth for everything the simulator needs beyond the algorithm descriptions.

---

## 🎯 Task for AI

Generate **complete system simulation** in **Python** that:

### 1. Models physical components:
- 8 heaters (N1-N8): 2 lines with 4 heaters each
- 2 fans (W1, W2): variable frequency drive 25-50 Hz
- 2 outlet levels: -4.30m and -7.90m
- Control valves: 8 valves (20-100%)
- Temperature sensors: T_zewn, T_szyb, T_N1-N8

### 2. Implements three algorithms:
- **WS:** Automatic scenario selection S0-S8 based on T_zewn
- **RC:** Configuration rotation every ROTATION_PERIOD_CONFIGS (e.g., 7 days)
- **RN:** Heater rotation every ROTATION_PERIOD_HEATERS (e.g., 7 days)

### 3. Ensures coordination:
- Shared global variables (see **Simulation Global Variables** below)
- Locks: `config_change_in_progress`, `heater_rotation_in_progress`
- Time synchronization: 1h gap after RC, 15 min gap between RN rotations
- Hierarchy: WS → RC → RN → PID

### 4. Simulates time:
- Accelerated time: 1 simulation second = X real minutes
- Timeline: ability to simulate 30 days in a few minutes
- Event logs: scenario change, config rotation, heater rotation

### 5. Generates results:
- External and shaft temperature charts
- Scenario timeline (S0-S8)
- Heater operating times N1-N8 (balance verification)
- Line operating times C1 vs C2 (balance verification)
- Statistics: number of changes, time in each scenario

---

## 📦 Technical Requirements

### Python Libraries:
```python
import numpy as np           # numerical computations
import matplotlib.pyplot as plt  # charts
import pandas as pd          # tabular data
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
```

### Code Structure:

```python
# 1. Model Classes
class Heater:
    """Heater model with PID, valve, state"""
    
class Fan:
    """Fan model with frequency, PID"""

class SystemState:
    """Complete system state - global variables"""

# 2. Algorithms
class AlgorithmWS:
    """Scenario selection S0-S8"""
    def select_scenario(self, T_extern):
        # Implementation from documentation
        
class AlgorithmRC:
    """Configuration rotation Primary ↔ Limited"""
    def check_rotation(self, time_since_last):
        # Implementation from documentation

class AlgorithmRN:
    """Heater rotation within line"""
    def execute_rotation(self, line):
        # Implementation from documentation

# 3. Simulator
class BogdankaSystem:
    """Main simulator integrating everything"""
    def __init__(self):
        self.state = SystemState()
        self.ws = AlgorithmWS()
        self.rc = AlgorithmRC()
        self.rn = AlgorithmRN()
    
    def simulation_step(self, dt):
        """Single time step of simulation"""
        # 1. Algorithm WS
        # 2. Algorithm RC (if time)
        # 3. Algorithm RN (if time)
        # 4. Update counters
        
    def simulate(self, days=30):
        """Simulate N days"""

# 4. Test Scenarios
def winter_scenario():
    """Winter simulation: T_extern from +5°C to -25°C"""
    
def oscillation_scenario():
    """Temperature oscillation simulation"""

# 5. Visualization
def plot_results(history):
    """Generate analysis charts"""
```

---

## 🔍 Key Elements from Documentation

### Simulation Global Variables (moved from documentation):
```python
# System state and scenario
current_scenario = "S0"                      # S0-S8
current_config = "Primary"                   # "Primary" or "Limited"

# Coordination locks (mutexes)
config_change_in_progress = False            # Algorithm RC executing rotation
heater_rotation_in_progress = False          # Algorithm RN executing rotation

# Time synchronization
time_last_config_change = 0                  # timestamp [s] - for RN
time_last_rotation_global = 0                # timestamp [s] - 15 min gap between rotations

# Heater state (8 elements)
operating_time = [0, 0, 0, 0, 0, 0, 0, 0]   # N1-N8 [seconds]
idle_time = [0, 0, 0, 0, 0, 0, 0, 0]        # N1-N8 [seconds]
activation_timestamp = [0, 0, 0, 0, 0, 0, 0, 0]  # N1-N8 [timestamp]
active_heaters = {"LINE1": [], "LINE2": []}  # Lists of active heaters

# Line state
operating_time_primary_config = 0            # [seconds]
operating_time_limited_config = 0            # [seconds]
```

### Configuration Parameters (defined by technologist):
```python
# Algorithm WS
TEMP_MONITORING_CYCLE = 10                   # [s] T_extern reading frequency
SCENARIO_STABILIZATION_TIME = 60             # [s] min. time in scenario

# Algorithm RC
CONFIG_ROTATION_PERIOD = 168 * 3600          # [s] e.g., 7 days (168h)
ALGORITHM_LOOP_CYCLE = 60                    # [s] RC/RN check frequency

# Algorithm RN
HEATER_ROTATION_PERIOD = 168 * 3600          # [s] e.g., 7 days
MIN_TIME_DELTA = 3600                        # [s] min. difference for rotation
```

### Input Signals for Simulation:
```python
T_extern = 0.0            # [°C] External temperature (-40 to +50)
T_shaft = 2.0             # [°C] Shaft temperature (-30m depth)
T_N = [50, 50, ...]       # [°C] Outlet temperatures N1-N8
operational_N = [True] * 8  # Bool heater operational status
operational_W = [True, True]  # Bool fan operational status
mode = "AUTO"             # "AUTO" or "MANUAL"
```

### Scenario Table (from documentation, section 3):
```python
SCENARIOS = {
    "S0": {"temp_min": 3, "heaters": 0, "W1": "OFF", "W2": "OFF"},
    "S1": {"temp_min": 2, "temp_max": -1, "heaters": 1, "W1": "PID", "W2": "OFF"},
    "S2": {"temp_min": -1, "temp_max": -4, "heaters": 2, "W1": "PID", "W2": "OFF"},
    "S3": {"temp_min": -4, "temp_max": -8, "heaters": 3, "W1": "PID", "W2": "OFF"},
    "S4": {"temp_min": -8, "temp_max": -11, "heaters": 4, "W1": "PID/MAX", "W2": "OFF"},
    "S5": {"temp_min": -11, "temp_max": -15, "heaters": 5, "W1": "MAX", "W2": "PID"},
    "S6": {"temp_min": -15, "temp_max": -18, "heaters": 6, "W1": "MAX", "W2": "PID"},
    "S7": {"temp_min": -18, "temp_max": -21, "heaters": 7, "W1": "MAX", "W2": "PID"},
    "S8": {"temp_min": -21, "heaters": 8, "W1": "MAX", "W2": "MAX"},
}
```

### Lock Coordination (from pseudocode):
```python
# Algorithm RC before rotation:
if heater_rotation_in_progress:
    return  # defer config rotation

config_change_in_progress = True
# ... execute rotation ...
config_change_in_progress = False

# Algorithm RN before rotation:
if config_change_in_progress:
    return  # defer heater rotation

# Check 1h gap from RC:
if (time - time_last_config_change) < 3600:
    return

# Check 15 min gap from last RN rotation:
if (time - time_last_rotation_global) < 900:
    return

heater_rotation_in_progress = True
# ... execute rotation ...
heater_rotation_in_progress = False
```

---

## 📊 Expected Simulation Results

### 1. Algorithm WS Verification:
- Do scenarios change according to table?
- Does hysteresis work correctly?
- Scenario timeline S0-S8 over time

### 2. Algorithm RC Verification:
- Do both lines have balanced operating times? (C1/C2 ratio ≈ 1.0)
- Does rotation occur every CONFIG_ROTATION_PERIOD?
- Histogram of operating time C1 vs C2

### 3. Algorithm RN Verification:
- Do all heaters have balanced operating times?
- Is difference max-min < 10% after one month?
- Operating time chart N1-N8

### 4. Coordination Verification:
- Do locks work? (RC and RN never execute simultaneously)
- Are time gaps preserved? (1h, 15 min)
- RC↔RN coordination timeline

---

## 🚀 Example Usage of Generated Code

```python
# Simulate 30 days of winter
simulator = BogdankaSystem()
simulator.params.CONFIG_ROTATION_PERIOD = 7 * 24 * 3600  # 7 days
simulator.params.HEATER_ROTATION_PERIOD = 7 * 24 * 3600  # 7 days

# Scenario: temperature drops from +5 to -25°C
external_temperature = lambda day: 5 - day  # simple decrease

history = simulator.simulate(
    days=30,
    T_extern_func=external_temperature,
    acceleration=1000  # 1s simulation = 1000s real time
)

# Results analysis
print(f"Heater balance: {history.heater_balance():.1%}")
print(f"Line balance: {history.line_balance():.1%}")
print(f"Scenario changes: {history.ws_change_count}")
print(f"RC rotations: {history.rc_rotation_count}")
print(f"RN rotations: {history.rn_rotation_count}")

# Charts
history.plot_timeline()
history.plot_operating_times()
```

---

## ✅ Simulation Success Criteria

1. **Algorithm WS works correctly:**
   - Scenarios change according to T_extern
   - Hysteresis prevents oscillations

2. **Algorithm RC works correctly:**
   - C1/C2 ratio close to 1.0 after one month (±5%)
   - Rotation every ~7 days

3. **Algorithm RN works correctly:**
   - Difference max(N1-N8) - min(N1-N8) < 10% after one month
   - Rotation every ~7 days in each line

4. **Coordination works correctly:**
   - RC and RN NEVER execute rotation simultaneously
   - Time gaps preserved (1h after RC, 15 min between RN)

5. **Code is readable and documented:**
   - Docstrings for classes and methods
   - Comments at key fragments
   - Easy parameter adjustment capability

---

## 📝 Code Style Requirements

### Variable Naming (English):
```python
# States
current_scenario      # not: aktualny_scenariusz
current_config        # not: aktualny_uklad
config_change_in_progress  # not: zmiana_ukladu_w_toku

# Times
operating_time        # not: czas_pracy
idle_time            # not: czas_postoju
activation_timestamp  # not: timestamp_zalaczenia

# Temperatures
T_extern             # not: T_zewn (but keep in comments: external temp)
T_shaft              # not: T_szyb
T_heater_outlet      # not: T_wylot_nagrzewnicy

# Components
heaters              # not: nagrzewnice
fans                 # not: wentylatory
lines                # not: ciagi
valves               # not: zawory

# Scenarios
scenario_table       # not: tabela_scenariuszy
PRIMARY_CONFIG       # not: UKLAD_PODSTAWOWY
LIMITED_CONFIG       # not: UKLAD_OGRANICZONY
```

### Class and Function Names:
```python
class BogdankaSystem:           # Main simulator
class AlgorithmWS:              # Scenario selection
class AlgorithmRC:              # Configuration rotation
class AlgorithmRN:              # Heater rotation
class Heater:                   # Single heater model
class Fan:                      # Single fan model
class SystemState:              # Global state

def select_scenario()           # not: wybierz_scenariusz
def execute_rotation()          # not: wykonaj_rotacje
def check_balance()             # not: sprawdz_rownomiernosc
def plot_results()              # not: rysuj_wyniki
```

### Comments (bilingual acceptable):
```python
# Read external temperature (Odczyt temperatury zewnętrznej)
T_extern = read_sensor()

# Check if rotation is needed (Sprawdź czy potrzebna rotacja)
if should_rotate():
    execute_rotation()
```

---

## 📄 Source Documentation

**Full algorithm documentation:** [../../docs/03-algorytmy/algorytmy.md](../../docs/03-algorytmy/algorytmy.md)

**System structure:** [../../docs/01-system/system.md](../../docs/01-system/system.md)

**Installation project:** [../../docs/02-projekt-instalacji/projekt-instalacji.md](../../docs/02-projekt-instalacji/projekt-instalacji.md)

---

**Last update:** November 24, 2025  
**Version:** 1.0

