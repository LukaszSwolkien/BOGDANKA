"""Algorithm WS: Scenario Selection based on external temperature."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from common.domain import Scenario
from .state import AlgoState

LOGGER = logging.getLogger("algo-service.ws")


@dataclass
class WSConfig:
    """Configuration for Algorithm WS."""
    temp_monitoring_cycle_s: int = 10
    scenario_stabilization_time_s: int = 60
    hysteresis_delta_c: float = 1.0
    filter_averaging: int = 3
    sensor_failure_timeout_s: int = 300


class AlgorithmWS:
    """
    Algorithm WS: Automatic Scenario Selection.
    
    Implements scenario selection based on external temperature with hysteresis.
    Follows pseudocode from algo_pseudokod.md exactly.
    """
    
    def __init__(self, config: WSConfig, state: AlgoState):
        self.config = config
        self.state = state
        LOGGER.info(
            f"Algorithm WS initialized: stabilization={config.scenario_stabilization_time_s}s, "
            f"hysteresis={config.hysteresis_delta_c}°C"
        )
    
    def process_temperature(self, t_zewn_raw: float) -> tuple[bool, str]:
        """
        Process temperature reading and potentially change scenario.
        
        Args:
            t_zewn_raw: Raw temperature reading from weather service
            
        Returns:
            (scenario_changed: bool, message: str)
        """
        # Step 1: Validate temperature reading
        if not self._validate_temperature(t_zewn_raw):
            return self._handle_sensor_failure()
        
        # Valid reading - update state
        self.state.sensor_alarm = False
        self.state.last_valid_reading = t_zewn_raw
        self.state.timestamp_last_reading = self.state.simulation_time
        
        # Add to buffer and get moving average
        t_zewn = self.state.add_temperature_reading(t_zewn_raw, self.config.filter_averaging)
        
        # Step 2: Determine required scenario
        required_scenario = self._determine_scenario(t_zewn)
        
        # Step 3: Check if change needed
        if required_scenario == self.state.current_scenario:
            # No change needed
            return False, f"Scenario {self.state.current_scenario.name} maintained (T={t_zewn:.1f}°C)"
        
        # Step 4: Check if change is allowed
        if not self.state.can_change_scenario(self.config.scenario_stabilization_time_s):
            time_since = self.state.time_since_scenario_change()
            return False, (
                f"Scenario change {self.state.current_scenario.name}→{required_scenario.name} "
                f"deferred (stabilization: {time_since:.0f}s/{self.config.scenario_stabilization_time_s}s)"
            )
        
        # Step 5: Execute scenario change
        return self._change_scenario(required_scenario, t_zewn)
    
    def _validate_temperature(self, t_zewn: float) -> bool:
        """Validate temperature reading is within reasonable range."""
        if t_zewn is None:
            return False
        if t_zewn < -40.0 or t_zewn > 50.0:
            return False
        return True
    
    def _handle_sensor_failure(self) -> tuple[bool, str]:
        """Handle sensor failure - use last valid reading or switch to manual."""
        self.state.sensor_alarm = True
        time_since_reading = self.state.time_since_last_reading()
        
        if time_since_reading < self.config.sensor_failure_timeout_s:
            # Use last valid reading
            t_zewn = self.state.last_valid_reading
            return False, (
                f"Sensor failure detected - using last valid reading ({t_zewn:.1f}°C), "
                f"time since last reading: {time_since_reading:.0f}s"
            )
        else:
            # Too long without reading - switch to manual mode
            self.state.mode = "MANUAL"
            LOGGER.error(
                f"CRITICAL: Sensor failure > {self.config.sensor_failure_timeout_s}s - "
                f"switching to MANUAL mode"
            )
            return False, "CRITICAL: Sensor failure - switched to MANUAL mode"
    
    def _determine_scenario(self, t_zewn: float) -> Scenario:
        """
        Determine required scenario based on temperature with hysteresis.
        
        Implements exact logic from algo_pseudokod.md.
        """
        current = self.state.current_scenario
        
        # S0: T ≥ 3°C
        if t_zewn >= 3.0:
            return Scenario.S0
        
        # Hysteresis zone between S0 and S1
        if t_zewn > 2.0:
            return Scenario.S1 if current == Scenario.S1 else Scenario.S0
        
        # S1: -1°C < t ≤ 2°C (turn off at t ≥ 3°C)
        if t_zewn > -1.0:
            return Scenario.S1
        
        # S2: -4°C < t ≤ -1°C (turn off at t ≥ 0°C with hysteresis)
        if t_zewn > -4.0:
            return Scenario.S2
        
        # Hysteresis S2→S1
        if t_zewn >= 0.0 and current == Scenario.S2:
            return Scenario.S1
        
        # S3: -8°C < t ≤ -4°C (turn off at t ≥ -3°C with hysteresis)
        if t_zewn > -8.0:
            return Scenario.S3
        
        # Hysteresis S3→S2
        if t_zewn >= -3.0 and current == Scenario.S3:
            return Scenario.S2
        
        # S4: -11°C < t ≤ -8°C (turn off at t ≥ -6°C with 2°C hysteresis)
        if t_zewn > -11.0:
            return Scenario.S4
        
        # Hysteresis S4→S3
        if t_zewn >= -6.0 and current == Scenario.S4:
            return Scenario.S3
        
        # S5: -15°C < t ≤ -11°C (turn off at t ≥ -10°C)
        if t_zewn > -15.0:
            return Scenario.S5
        
        # Hysteresis S5→S4
        if t_zewn >= -10.0 and current == Scenario.S5:
            return Scenario.S4
        
        # S6: -18°C < t ≤ -15°C (turn off at t ≥ -13°C with 2°C hysteresis)
        if t_zewn > -18.0:
            return Scenario.S6
        
        # Hysteresis S6→S5
        if t_zewn >= -13.0 and current == Scenario.S6:
            return Scenario.S5
        
        # S7: -21°C < t ≤ -18°C (turn off at t ≥ -15°C with 3°C hysteresis)
        if t_zewn > -21.0:
            return Scenario.S7
        
        # Hysteresis S7→S6
        if t_zewn >= -15.0 and current == Scenario.S7:
            return Scenario.S6
        
        # S8: t ≤ -21°C (turn off at t ≥ -20°C)
        if t_zewn <= -21.0:
            return Scenario.S8
        
        # Hysteresis S8→S7
        if t_zewn >= -20.0 and current == Scenario.S8:
            return Scenario.S7
        
        # Default: maintain current scenario
        return current
    
    def _change_scenario(self, new_scenario: Scenario, t_zewn: float) -> tuple[bool, str]:
        """
        Execute scenario change.
        
        In simulation, we don't actually control physical equipment,
        so we just update state and log the change.
        """
        old_scenario = self.state.current_scenario
        
        LOGGER.info(
            f"Scenario change: {old_scenario.name} → {new_scenario.name} "
            f"(T_zewn={t_zewn:.1f}°C, sim_time={self.state.simulation_time:.1f}s)"
        )
        
        # Update state
        self.state.current_scenario = new_scenario
        self.state.timestamp_last_scenario_change = self.state.simulation_time
        
        return True, f"Scenario changed: {old_scenario.name} → {new_scenario.name} (T={t_zewn:.1f}°C)"
    
    def get_scenario_config(self, scenario: Scenario) -> dict:
        """
        Get configuration for a scenario.
        
        Returns number of heaters, fan modes, etc.
        This matches Pobierz_Konfigurację_Scenariusza from pseudocode.
        """
        configs = {
            Scenario.S0: {"heaters": 0, "w1_mode": "OFF", "w2_mode": "OFF", "config": None},
            Scenario.S1: {"heaters": 1, "w1_mode": "PID", "w2_mode": "OFF", "config": "Primary or Limited"},
            Scenario.S2: {"heaters": 2, "w1_mode": "PID", "w2_mode": "OFF", "config": "Primary or Limited"},
            Scenario.S3: {"heaters": 3, "w1_mode": "PID", "w2_mode": "OFF", "config": "Primary or Limited"},
            Scenario.S4: {"heaters": 4, "w1_mode": "PID", "w2_mode": "OFF", "config": "Primary or Limited"},
            Scenario.S5: {"heaters": 5, "w1_mode": "MAX", "w2_mode": "PID", "config": "Primary"},
            Scenario.S6: {"heaters": 6, "w1_mode": "MAX", "w2_mode": "PID", "config": "Primary"},
            Scenario.S7: {"heaters": 7, "w1_mode": "MAX", "w2_mode": "PID", "config": "Primary"},
            Scenario.S8: {"heaters": 8, "w1_mode": "MAX", "w2_mode": "PID", "config": "Primary"},
        }
        return configs.get(scenario, configs[Scenario.S0])

