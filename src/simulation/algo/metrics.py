"""Telemetry and metrics for algo service."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from opentelemetry.metrics import CallbackOptions, Observation

from common.domain import Scenario
from common.telemetry import TelemetryManager
from .state import AlgoState

if TYPE_CHECKING:
    from .algorithm_rn import AlgorithmRN

LOGGER = logging.getLogger("algo-service.metrics")


@dataclass
class AlgoMetrics:
    """
    Metrics manager for algo service.
    
    Implements required metrics from simulation.md specification.
    """
    
    telemetry: TelemetryManager
    metrics_prefix: str
    default_dimensions: dict[str, str]
    state: AlgoState
    algorithm_rn: AlgorithmRN
    
    def __post_init__(self) -> None:
        meter = self.telemetry.meter("bogdanka.algo")
        
        # ═══════════════════════════════════════════════════════════════
        # WS METRICS (Scenario Selection)
        # ═══════════════════════════════════════════════════════════════
        
        # Current scenario (gauge, 0-8)
        self._current_scenario_gauge = meter.create_observable_gauge(
            f"{self.metrics_prefix}.ws.scenario",
            callbacks=[self._observe_current_scenario],
            description="Current active scenario (0-8)",
        )
        
        # External temperature (gauge, °C)
        self._external_temp_gauge = meter.create_observable_gauge(
            f"{self.metrics_prefix}.ws.temperature_external",
            callbacks=[self._observe_external_temp],
            description="External temperature in °C",
            unit="Cel",
        )
        
        # Simulation time (gauge, seconds since start)
        self._simulation_time_gauge = meter.create_observable_gauge(
            f"{self.metrics_prefix}.simulation_time_s",
            callbacks=[self._observe_simulation_time],
            description="Current simulation time in seconds",
            unit="s",
        )
        
        # Time spent in each scenario (counter by scenario dimension)
        self._scenario_time_counter = meter.create_counter(
            f"{self.metrics_prefix}.ws.scenario_time_s",
            description="Time spent in each scenario",
            unit="s",
        )
        
        # Scenario transitions (counter with from/to dimensions)
        self._scenario_changes_counter = meter.create_counter(
            f"{self.metrics_prefix}.ws.scenario_changes",
            description="Count of scenario transitions",
        )
        
        # ═══════════════════════════════════════════════════════════════
        # RC METRICS (Configuration Rotation)
        # ═══════════════════════════════════════════════════════════════
        
        # Current configuration (gauge, 0=Primary, 1=Limited)
        self._current_config_gauge = meter.create_observable_gauge(
            f"{self.metrics_prefix}.rc.current_config",
            callbacks=[self._observe_current_config],
            description="Current configuration (0=Primary, 1=Limited)",
        )
        
        # Time spent in each configuration (counter by config dimension)
        self._config_time_counter = meter.create_counter(
            f"{self.metrics_prefix}.rc.config_time_s",
            description="Time spent in each configuration",
            unit="s",
        )
        
        # Configuration rotations (counter with from/to dimensions)
        self._rotation_counter = meter.create_counter(
            f"{self.metrics_prefix}.rc.rotation_count",
            description="Count of configuration rotations",
        )
        
        # Rotation duration (histogram)
        self._rotation_duration_histogram = meter.create_histogram(
            f"{self.metrics_prefix}.rc.rotation_duration_s",
            description="Duration of configuration rotations",
            unit="s",
        )
        
        # ═══════════════════════════════════════════════════════════════
        # RN METRICS (Heater Rotation)
        # ═══════════════════════════════════════════════════════════════
        
        # Heater rotations (counter with line/from/to dimensions)
        self._heater_rotation_counter = meter.create_counter(
            f"{self.metrics_prefix}.rn.rotation_count",
            description="Count of heater rotations",
        )
        
        # Heater rotation duration (histogram)
        self._heater_rotation_duration_histogram = meter.create_histogram(
            f"{self.metrics_prefix}.rn.rotation_duration_s",
            description="Duration of heater rotations",
            unit="s",
        )
        
        # Heater operating time (observable gauge per heater)
        self._heater_operating_time_gauge = meter.create_observable_gauge(
            f"{self.metrics_prefix}.rn.heater_operating_time_s",
            callbacks=[self._observe_heater_operating_time],
            description="Heater operating time in seconds",
            unit="s",
        )
        
        # Heater state (observable gauge per heater: 0=idle, 1=active, 2=faulty)
        self._heater_state_gauge = meter.create_observable_gauge(
            f"{self.metrics_prefix}.rn.heater_state",
            callbacks=[self._observe_heater_state],
            description="Heater state (0=idle, 1=active, 2=faulty)",
        )
        
        # Track last update time for incrementing counters
        self._last_update_time = 0.0
        self._last_update_scenario = Scenario.S0
        self._last_update_config = "Primary"
        
        LOGGER.info(f"Algo metrics initialized with prefix: {self.metrics_prefix}")
    
    def _observe_current_scenario(self, options: CallbackOptions):
        """Callback for current scenario gauge."""
        yield Observation(
            self.state.current_scenario.value,
            {**self.default_dimensions}
        )
    
    def _observe_external_temp(self, options: CallbackOptions):
        """Callback for external temperature gauge."""
        # Use last valid reading if we have one
        temp = self.state.last_valid_reading if self.state.last_valid_reading else 0.0
        yield Observation(temp, {**self.default_dimensions})
    
    def _observe_simulation_time(self, options: CallbackOptions):
        """Callback for simulation time gauge."""
        yield Observation(
            self.state.simulation_time,
            {**self.default_dimensions}
        )
    
    def _observe_current_config(self, options: CallbackOptions):
        """Callback for current configuration gauge."""
        # 0 = Primary, 1 = Limited
        value = 0 if self.state.current_config == "Primary" else 1
        yield Observation(value, {**self.default_dimensions})
    
    def _observe_heater_operating_time(self, options: CallbackOptions):
        """Callback for heater operating time gauge."""
        from common.domain import Heater
        for heater in Heater:
            op_time = self.algorithm_rn.get_heater_operating_time(heater)
            # Determine line based on heater name (N1-N4 = C1, N5-N8 = C2)
            line = "C1" if heater.name in ["N1", "N2", "N3", "N4"] else "C2"
            yield Observation(
                op_time,
                {
                    **self.default_dimensions,
                    "heater": heater.name,
                    "line": line,
                }
            )
    
    def _observe_heater_state(self, options: CallbackOptions):
        """Callback for heater state gauge."""
        from common.domain import Heater
        for heater in Heater:
            state = self.algorithm_rn.get_heater_state(heater)
            # Map HeaterState enum to numeric: IDLE=0, ACTIVE=1, FAULTY=2
            state_value = 0 if state.value == "idle" else (1 if state.value == "active" else 2)
            # Determine line based on heater name (N1-N4 = C1, N5-N8 = C2)
            line = "C1" if heater.name in ["N1", "N2", "N3", "N4"] else "C2"
            yield Observation(
                state_value,
                {
                    **self.default_dimensions,
                    "heater": heater.name,
                    "line": line,
                }
            )
    
    def update(self) -> None:
        """
        Update counters based on current state.
        
        Should be called every simulation step to increment time counters.
        """
        # Calculate time delta since last update
        if self._last_update_time == 0.0:
            self._last_update_time = self.state.simulation_time
            self._last_update_scenario = self.state.current_scenario
            return
        
        time_delta = self.state.simulation_time - self._last_update_time
        
        if time_delta > 0:
            # Increment scenario time counter
            self._scenario_time_counter.add(
                time_delta,
                {
                    **self.default_dimensions,
                    "scenario": self.state.current_scenario.name,
                }
            )
            
            # Increment configuration time counter
            self._config_time_counter.add(
                time_delta,
                {
                    **self.default_dimensions,
                    "config": self.state.current_config,
                }
            )
            
            self._last_update_time = self.state.simulation_time
            self._last_update_config = self.state.current_config
    
    def record_scenario_change(self, from_scenario: Scenario, to_scenario: Scenario) -> None:
        """Record a scenario transition."""
        self._scenario_changes_counter.add(
            1,
            {
                **self.default_dimensions,
                "from_scenario": from_scenario.name,
                "to_scenario": to_scenario.name,
            }
        )
        LOGGER.info(
            f"Scenario change recorded: {from_scenario.name} → {to_scenario.name} "
            f"(sim_time={self.state.simulation_time:.1f}s)"
        )
    
    def record_config_change(self, from_config: str, to_config: str, duration_s: float = 0.0) -> None:
        """Record a configuration rotation."""
        self._rotation_counter.add(
            1,
            {
                **self.default_dimensions,
                "from_config": from_config,
                "to_config": to_config,
            }
        )
        
        if duration_s > 0:
            self._rotation_duration_histogram.record(
                duration_s,
                {**self.default_dimensions}
            )
        
        LOGGER.info(
            f"Config change recorded: {from_config} → {to_config} "
            f"(duration={duration_s:.1f}s, sim_time={self.state.simulation_time:.1f}s)"
        )
    
    def record_heater_rotation(
        self, line: str, heater_off: str, heater_on: str, duration_s: float = 0.0
    ) -> None:
        """Record a heater rotation."""
        self._heater_rotation_counter.add(
            1,
            {
                **self.default_dimensions,
                "line": line,
                "heater_off": heater_off,
                "heater_on": heater_on,
            }
        )
        
        if duration_s > 0:
            self._heater_rotation_duration_histogram.record(
                duration_s,
                {**self.default_dimensions, "line": line}
            )
        
        LOGGER.info(
            f"Heater rotation recorded: {line} {heater_off} → {heater_on} "
            f"(duration={duration_s:.1f}s, sim_time={self.state.simulation_time:.1f}s)"
        )

