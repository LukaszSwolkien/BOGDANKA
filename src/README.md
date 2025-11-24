# BOGDANKA Shaft 2 System Implementation

This directory contains materials for system control implementation and simulation.

## Structure

### `simulation/`
Materials for generating simulation code:
- **[prompt-ai-simulation.md](./simulation/prompt-ai-simulation.md)** - AI prompt (ChatGPT/Claude) to generate complete Python system simulation

### `plc/`
Materials for generating PLC code:
- **[prompt-ai-plc.md](./plc/prompt-ai-plc.md)** - AI prompt (ChatGPT/Claude) to generate Siemens S7-1500/1200 PLC code in Structured Text (ST)

## How to Use

### 1. **Simulation (development & verification):**
   - Open file `simulation/prompt-ai-simulation.md`
   - Copy its content to ChatGPT or Claude
   - AI will generate Python code with simulation of three algorithms (WS, RC, RN)
   - Run the code to verify logic, test scenarios, analyze balance

### 2. **PLC Implementation (production):**
   - Open file `plc/prompt-ai-plc.md`
   - Copy its content to ChatGPT or Claude
   - AI will generate Siemens S7-1500/1200 PLC code in Structured Text (ST)
   - Import to TIA Portal v17+
   - Integrate with I/O configuration and SCADA/HMI
   - Commission on-site with PID tuning

## Code Convention

- **Language:** English (variable names, functions, classes)
- **Comments:** Bilingual acceptable (English + Polish)
- **Documentation:** Polish (in `../docs/`)

---

**Documentation:** [../docs/start.md](../docs/start.md)
