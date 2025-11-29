# BOGDANKA Shaft 2 System Implementation

This directory contains system control implementation and simulation.

## Structure

- **[`algo_pseudokod.md`](../docs/03-algorytmy/algo_pseudokod.md)** - **SINGLE SOURCE OF TRUTH** - Pseudocode for algorithms WS, RC, RN
- `simulation/` - Simulation code for control algorithms
  - See: [simulation/simulation.md](simulation/simulation.md)
- `plc/` - PLC controller code (to be developed)

## KEY IMPLEMENTATION PRINCIPLE

**Pseudocode in [`algo_pseudokod.md`](../docs/03-algorytmy/algo_pseudokod.md) is the single source of truth for algorithm logic!**

- Every implementation (simulation) must **exactly** match the pseudocode
- If you find issues in tests/simulation → update pseudocode FIRST, then code
- DO NOT modify logic without updating pseudocode

---

**Documentation:** [../docs/start.md](../docs/start.md)
