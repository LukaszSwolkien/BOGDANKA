# AI Prompt - BOGDANKA PLC Code Generation

**Goal:** Generate PLC code for BOGDANKA Shaft 2 heating control system (Siemens S7-1500/1200)

---

## 📋 Instructions for AI (ChatGPT, Claude, etc.)

### Context

You have access to **complete documentation of three cooperating control algorithms** for shaft heating system:
- **Algorithm WS** - automatic scenario selection (S0-S8) based on external temperature
- **Algorithm RC** - rotation of heating line configurations (Primary ↔ Limited)
- **Algorithm RN** - rotation of heaters within a heating line

📖 **Documentation:** [../../docs/03-algorytmy/algorytmy.md](../../docs/03-algorytmy/algorytmy.md)

---

## 🎯 Task for AI

Generate **complete PLC code** in **Structured Text (ST)** or **Ladder Diagram (LAD)** that:

### 1. Implements Function Blocks (FB):
- **FB_AlgorithmWS** - scenario selection S0-S8
- **FB_AlgorithmRC** - configuration rotation Primary ↔ Limited
- **FB_AlgorithmRN** - heater rotation within line
- **FB_PID_Heater** - heater temperature control (Tz = 50°C)
- **FB_PID_Fan** - shaft temperature control (Ts = 2°C)
- **FB_Heater** - single heater control (valve, damper, interlocks)
- **FB_Fan** - fan control (VFD frequency 25-50 Hz)

### 2. Global Data Blocks (DB):
- **DB_SystemState** - system state variables (scenario, config, locks)
- **DB_Heaters** - array of 8 heater data structures
- **DB_Fans** - array of 2 fan data structures
- **DB_Timers** - operating time counters
- **DB_Alarms** - alarm flags and messages
- **DB_Parameters** - configurable parameters (rotation periods, PID tuning)

### 3. Ensures coordination:
- Mutex implementation for RC ↔ RN coordination
- Time synchronization (1h gap after RC, 15 min between RN)
- Priority handling: WS → RC → RN → PID
- Safe state on error/manual mode

### 4. Safety features:
- Watchdog timers
- Sensor validation (range check, plausibility)
- Valve anti-freeze protection (min 20%)
- Emergency stop sequences
- Automatic transition to MANUAL mode on critical errors

### 5. HMI/SCADA Integration:
- OPC UA or S7 communication tags
- Status visualization variables
- Parameter adjustment interface
- Alarm acknowledgment
- Manual override controls

---

## 📦 Technical Requirements

### Target Platform:
- **PLC:** Siemens S7-1500 or S7-1200
- **Programming Standard:** IEC 61131-3
- **Languages:** Structured Text (ST) preferred, Ladder (LAD) acceptable
- **TIA Portal:** Version 17 or higher

### Code Structure:

```
Project: BOGDANKA_Szyb2
│
├── PLC_1 (Main CPU)
│   ├── Program blocks
│   │   ├── OB1 (Main cycle - 100ms)
│   │   ├── OB35 (Cyclic interrupt - 1s for algorithms)
│   │   └── OB82 (Diagnostic interrupt)
│   │
│   ├── Function Blocks (FB)
│   │   ├── FB_AlgorithmWS
│   │   ├── FB_AlgorithmRC
│   │   ├── FB_AlgorithmRN
│   │   ├── FB_PID_Heater (x8)
│   │   ├── FB_PID_Fan (x2)
│   │   ├── FB_Heater (x8)
│   │   └── FB_Fan (x2)
│   │
│   ├── Functions (FC)
│   │   ├── FC_ScenarioSelection
│   │   ├── FC_ValidateTemperature
│   │   ├── FC_EmergencyStop
│   │   └── FC_AlarmHandler
│   │
│   └── Data Blocks (DB)
│       ├── DB_SystemState (Global)
│       ├── DB_Heaters (Array[1..8])
│       ├── DB_Fans (Array[1..2])
│       ├── DB_Timers
│       ├── DB_Alarms
│       └── DB_Parameters
│
└── HMI Tags (for OPC UA/S7 Comm)
    ├── Process Values
    ├── Setpoints
    ├── Status
    └── Alarms
```

---

## 🔍 Key Data Structures

### User-Defined Types (UDT):

```st
TYPE UDT_Heater
    // Status
    bActive : BOOL;              // Heater is running
    bOperational : BOOL;         // Heater is operational (not faulty)
    bAlarm : BOOL;               // Alarm flag
    
    // Timers
    tOperatingTime : TIME;       // Total operating time
    tIdleTime : TIME;            // Total idle time
    dtActivationTime : DTL;      // Last activation timestamp
    
    // Measurements
    rTemperature : REAL;         // Outlet temperature [°C]
    rValvePosition : REAL;       // Valve position [%] 20-100
    
    // Control
    bDamperOpen : BOOL;          // Inlet damper state
    bEnablePID : BOOL;           // PID controller enable
END_TYPE

TYPE UDT_Fan
    // Status
    bRunning : BOOL;             // Fan is running
    bOperational : BOOL;         // Fan is operational
    bAlarm : BOOL;               // Alarm flag
    
    // Control
    rFrequency : REAL;           // VFD frequency [Hz] 25-50
    eMode : INT;                 // 0=OFF, 1=MANUAL, 2=PID, 3=MAX
    
    // Measurements
    rCurrent : REAL;             // Motor current [A]
    tOperatingTime : TIME;       // Total operating time
END_TYPE

TYPE UDT_SystemState
    // Current state
    eScenario : INT;             // S0-S8 (0-8)
    eConfig : INT;               // 0=Primary, 1=Limited
    
    // Coordination locks
    bConfigChangeInProgress : BOOL;
    bHeaterRotationInProgress : BOOL;
    
    // Timestamps
    tLastConfigChange : TIME;
    tLastRotationGlobal : TIME;
    
    // Mode
    eMode : INT;                 // 0=MANUAL, 1=AUTO
    bEmergencyStop : BOOL;
END_TYPE
```

### Global DB Example:

```st
DATA_BLOCK DB_SystemState
    STRUCT
        State : UDT_SystemState;
        
        // Algorithm timers
        tWSCycle : TIME := T#10s;
        tRCCycle : TIME := T#1m;
        tRNCycle : TIME := T#1m;
        
        // Rotation periods (configurable by technologist)
        tConfigRotationPeriod : TIME := T#168h;  // 7 days
        tHeaterRotationPeriod : TIME := T#168h;  // 7 days
        
        // Operating time counters
        tPrimaryConfigTime : TIME;
        tLimitedConfigTime : TIME;
    END_STRUCT
END_DATA_BLOCK

DATA_BLOCK DB_Heaters
    STRUCT
        Heater : ARRAY[1..8] OF UDT_Heater;
    END_STRUCT
END_DATA_BLOCK
```

---

## 🛠️ Algorithm Implementation Examples

### Example 1: FB_AlgorithmWS (Structured Text)

```st
FUNCTION_BLOCK FB_AlgorithmWS
VAR_INPUT
    rT_extern : REAL;                    // External temperature [°C]
    bEnable : BOOL;                      // Enable algorithm
    eMode : INT;                         // 0=MANUAL, 1=AUTO
END_VAR

VAR_OUTPUT
    eRequiredScenario : INT;             // S0-S8 (0-8)
    bScenarioChanged : BOOL;             // Flag: scenario changed
    bAlarm : BOOL;                       // Algorithm alarm
END_VAR

VAR
    eCurrentScenario : INT := 0;         // Current scenario
    tLastChange : TIME;                  // Time since last change
    tStabilization : TIME := T#60s;      // Stabilization time
    rTempBuffer : ARRAY[1..3] OF REAL;   // Temperature filter buffer
    iBufferIndex : INT := 0;
END_VAR

VAR_TEMP
    rTempAvg : REAL;
    i : INT;
    bChangeAllowed : BOOL;
END_VAR

// Main logic
IF NOT bEnable OR eMode <> 1 THEN
    RETURN;
END_IF;

// Step 1: Filter temperature (moving average)
iBufferIndex := iBufferIndex + 1;
IF iBufferIndex > 3 THEN
    iBufferIndex := 1;
END_IF;
rTempBuffer[iBufferIndex] := rT_extern;

rTempAvg := 0.0;
FOR i := 1 TO 3 DO
    rTempAvg := rTempAvg + rTempBuffer[i];
END_FOR;
rTempAvg := rTempAvg / 3.0;

// Step 2: Determine required scenario with hysteresis
eRequiredScenario := DetermineScenario(rTempAvg, eCurrentScenario);

// Step 3: Check if change is allowed (stabilization time)
bChangeAllowed := (tLastChange >= tStabilization);

// Step 4: Execute scenario change
IF eRequiredScenario <> eCurrentScenario AND bChangeAllowed THEN
    // TODO: Call FC_ExecuteScenarioChange
    eCurrentScenario := eRequiredScenario;
    bScenarioChanged := TRUE;
    tLastChange := T#0s;
ELSE
    bScenarioChanged := FALSE;
END_IF;

END_FUNCTION_BLOCK
```

### Example 2: FB_AlgorithmRC (Structured Text)

```st
FUNCTION_BLOCK FB_AlgorithmRC
VAR_INPUT
    bEnable : BOOL;
    eCurrentScenario : INT;              // S0-S8
    tRotationPeriod : TIME;              // Configurable period
END_VAR

VAR_OUTPUT
    eConfig : INT;                       // 0=Primary, 1=Limited
    bConfigChanged : BOOL;
    bAlarm : BOOL;
END_VAR

VAR
    tTimeSinceLastRotation : TIME;
    bRotationRequired : BOOL;
END_VAR

VAR_IN_OUT
    stSystemState : UDT_SystemState;
END_VAR

// Main logic
IF NOT bEnable THEN
    RETURN;
END_IF;

// Check if rotation is applicable (only S1-S4)
IF eCurrentScenario < 1 OR eCurrentScenario > 4 THEN
    // Force Primary config in S0 or S5-S8
    IF eConfig <> 0 THEN
        eConfig := 0;  // Primary
        bConfigChanged := TRUE;
    END_IF;
    RETURN;
END_IF;

// Check coordination lock (RN in progress)
IF stSystemState.bHeaterRotationInProgress THEN
    RETURN;  // Defer rotation
END_IF;

// Check rotation period
tTimeSinceLastRotation := TIME() - stSystemState.tLastConfigChange;
bRotationRequired := (tTimeSinceLastRotation >= tRotationPeriod);

// Execute rotation
IF bRotationRequired THEN
    // Set lock
    stSystemState.bConfigChangeInProgress := TRUE;
    
    // Toggle configuration
    IF eConfig = 0 THEN
        eConfig := 1;  // Primary → Limited
    ELSE
        eConfig := 0;  // Limited → Primary
    END_IF;
    
    // TODO: Call FC_ExecuteConfigChange
    
    // Update timestamp
    stSystemState.tLastConfigChange := TIME();
    bConfigChanged := TRUE;
    
    // Release lock
    stSystemState.bConfigChangeInProgress := FALSE;
ELSE
    bConfigChanged := FALSE;
END_IF;

END_FUNCTION_BLOCK
```

---

## 🔒 Safety and Error Handling

### Critical Safety Features:

1. **Sensor Validation:**
```st
FUNCTION FC_ValidateTemperature : BOOL
VAR_INPUT
    rTemp : REAL;
    rMin : REAL := -40.0;
    rMax : REAL := 50.0;
END_VAR

FC_ValidateTemperature := (rTemp >= rMin) AND (rTemp <= rMax);
END_FUNCTION
```

2. **Valve Anti-Freeze Protection:**
```st
// In FB_Heater
IF NOT bActive THEN
    rValvePosition := 20.0;  // Minimum 20% always
END_IF;
```

3. **Watchdog Timer:**
```st
// In OB1
IF tWatchdog >= T#5s THEN
    bAlarm := TRUE;
    // Transition to safe state
END_IF;
```

4. **Emergency Stop Sequence:**
```st
FUNCTION FC_EmergencyStop : VOID
// Close all valves to 20%
FOR i := 1 TO 8 DO
    DB_Heaters.Heater[i].rValvePosition := 20.0;
    DB_Heaters.Heater[i].bDamperOpen := FALSE;
END_FOR;

// Stop fans safely
FOR i := 1 TO 2 DO
    DB_Fans.Fan[i].rFrequency := 25.0;  // Reduce to minimum
    // Wait, then stop
END_FOR;

// Set MANUAL mode
DB_SystemState.State.eMode := 0;
END_FUNCTION
```

---

## 📡 HMI/SCADA Integration

### OPC UA Tag Structure:

```
BOGDANKA_Szyb2/
├── ProcessValues/
│   ├── T_extern                 (REAL, Read)
│   ├── T_shaft                  (REAL, Read)
│   ├── T_heaters[1..8]          (ARRAY[REAL], Read)
│   ├── Scenario                 (INT, Read)
│   └── Config                   (INT, Read)
│
├── Setpoints/
│   ├── Tz_setpoint              (REAL, Read/Write) = 50°C
│   ├── Ts_setpoint              (REAL, Read/Write) = 2°C
│   ├── ConfigRotationPeriod     (TIME, Read/Write)
│   └── HeaterRotationPeriod     (TIME, Read/Write)
│
├── Control/
│   ├── Mode                     (INT, Read/Write) 0=MANUAL, 1=AUTO
│   ├── EmergencyStop            (BOOL, Write)
│   ├── ResetAlarms              (BOOL, Write)
│   └── ManualOverride[1..8]     (ARRAY[BOOL], Write)
│
├── Status/
│   ├── HeatersActive[1..8]      (ARRAY[BOOL], Read)
│   ├── FansRunning[1..2]        (ARRAY[BOOL], Read)
│   ├── OperatingTime_C1         (TIME, Read)
│   ├── OperatingTime_C2         (TIME, Read)
│   └── HeaterOperatingTime[1..8] (ARRAY[TIME], Read)
│
└── Alarms/
    ├── AlarmActive              (BOOL, Read)
    ├── AlarmCount               (INT, Read)
    └── AlarmList[1..50]         (ARRAY[STRING], Read)
```

---

## ⏱️ Cyclic Organization Blocks

### OB1 - Main Cycle (100ms):
```st
ORGANIZATION_BLOCK OB1
// Fast loop - PID control, I/O refresh
CALL FB_PID_Heater[1] (DB_Heaters.Heater[1]);
CALL FB_PID_Heater[2] (DB_Heaters.Heater[2]);
// ... for all 8 heaters

CALL FB_PID_Fan[1] (DB_Fans.Fan[1]);
CALL FB_PID_Fan[2] (DB_Fans.Fan[2]);

// Update watchdog
tWatchdog := tWatchdog + T#100ms;
END_ORGANIZATION_BLOCK
```

### OB35 - Cyclic Interrupt (1s):
```st
ORGANIZATION_BLOCK OB35
// Slow loop - algorithms, timers
CALL FB_AlgorithmWS (DB_AlgorithmWS);
CALL FB_AlgorithmRC (DB_AlgorithmRC);
CALL FB_AlgorithmRN (DB_AlgorithmRN);

// Update operating time counters
UpdateOperatingTimeCounters();

// Reset watchdog
tWatchdog := T#0s;
END_ORGANIZATION_BLOCK
```

---

## ✅ PLC Code Success Criteria

1. **Functional Requirements:**
   - All three algorithms (WS, RC, RN) implemented and tested
   - PID controllers for heaters and fans tuned and stable
   - Coordination locks prevent simultaneous operations
   - Safe state on power loss/restart

2. **Safety Requirements:**
   - Anti-freeze protection (valves min 20%)
   - Sensor validation and plausibility checks
   - Emergency stop sequence < 5s
   - Automatic transition to MANUAL on critical errors

3. **Performance Requirements:**
   - Main cycle time < 100ms (scan time)
   - Algorithm cycle time = 1s (acceptable)
   - Response time to temperature change < 10s
   - No PLC CPU overload (< 30% average)

4. **Code Quality:**
   - IEC 61131-3 compliant
   - Clear naming conventions (English)
   - Comprehensive comments (bilingual acceptable)
   - Modular structure (FB reusability)

5. **Documentation:**
   - Variable list with descriptions
   - FB interface documentation
   - Wiring diagrams (I/O allocation)
   - Commissioning checklist

---

## 📝 Code Style Requirements

### Naming Conventions (IEC 61131-3):

**Variables:**
- `b` prefix for BOOL (bEnable, bAlarm)
- `i` prefix for INT (iCount, iIndex)
- `r` prefix for REAL (rTemperature, rSetpoint)
- `t` prefix for TIME (tCycleTime, tOperatingTime)
- `e` prefix for ENUM/INT state (eScenario, eMode)
- `st` prefix for STRUCT (stSystemState)

**Function Blocks:**
- `FB_` prefix for Function Blocks
- `FC_` prefix for Functions
- `DB_` prefix for Data Blocks
- `UDT_` prefix for User-Defined Types

**Example:**
```st
VAR
    bHeaterActive : BOOL;
    rValvePosition : REAL;
    tOperatingTime : TIME;
    eCurrentScenario : INT;
END_VAR
```

---

## 📄 Source Documentation

**Full algorithm documentation:** [../../docs/03-algorytmy/algorytmy.md](../../docs/03-algorytmy/algorytmy.md)

**System structure:** [../../docs/01-system/system.md](../../docs/01-system/system.md)

**Installation project:** [../../docs/02-projekt-instalacji/projekt-instalacji.md](../../docs/02-projekt-instalacji/projekt-instalacji.md)

**SCADA/HMI requirements:** [../../docs/04-scada-hmi/scada-hmi.md](../../docs/04-scada-hmi/scada-hmi.md)

---

## 🚀 Deployment Steps

1. **Development Phase:**
   - Implement FB blocks in TIA Portal
   - Create simulation test bench (PLCSIM Advanced)
   - Unit test each algorithm

2. **Integration Phase:**
   - Integrate with I/O configuration
   - Connect to SCADA/HMI
   - System integration tests

3. **Commissioning Phase:**
   - On-site PID tuning (Kp, Ti, Td)
   - Set rotation periods (technologist decision)
   - Verify safety interlocks
   - 72h stability test

4. **Validation Phase:**
   - Performance verification (balance, response time)
   - Alarm testing
   - Documentation handover

---

**Last update:** November 24, 2025  
**Version:** 1.0

