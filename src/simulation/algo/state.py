"""Global state management for algo service - minimal for WS algorithm."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from common.domain import Scenario


@dataclass
class AlgoState:
    """
    Global state for algo service algorithms.
    
    Time Source: simulation_time is set from weather service responses.
    NO independent clock - weather service is authoritative time source.
    """
    
    # ═══════════════════════════════════════════════════════════════
    # SIMULATION TIME (from weather service - authoritative)
    # ═══════════════════════════════════════════════════════════════
    simulation_time: float = 0.0  # Current simulation time [seconds] - SET FROM WEATHER SERVICE
    
    # ═══════════════════════════════════════════════════════════════
    # ALGORITHM WS STATE (Scenario Selection)
    # ═══════════════════════════════════════════════════════════════
    current_scenario: Scenario = Scenario.S0
    t_zewn_buffer: list[float] = field(default_factory=list)  # Temperature moving average buffer
    last_valid_reading: float = 0.0  # Last valid temperature reading
    timestamp_last_scenario_change: float = 0.0  # When scenario last changed
    timestamp_last_reading: float = 0.0  # For detecting sensor failure
    sensor_alarm: bool = False  # Temperature sensor alarm flag
    
    # System mode
    mode: str = "AUTO"  # AUTO or MANUAL
    
    # ═══════════════════════════════════════════════════════════════
    # ALGORITHM RC STATE (Configuration Rotation) - Placeholder for Phase 2
    # ═══════════════════════════════════════════════════════════════
    current_config: str = "Primary"  # "Primary" or "Limited"
    config_change_in_progress: bool = False  # Lock for RN coordination
    config_rotation_end_time: float = 0.0  # When current RC rotation will finish
    timestamp_last_config_change: float = 0.0  # For RN coordination
    
    # ═══════════════════════════════════════════════════════════════
    # ALGORITHM RN STATE (Heater Rotation) - Placeholder for Phase 2
    # ═══════════════════════════════════════════════════════════════
    heater_rotation_in_progress: bool = False  # Lock for RC coordination
    heater_rotation_end_time: float = 0.0  # When current RN rotation will finish
    
    def time_since_scenario_change(self) -> float:
        """Calculate time since last scenario change using weather's simulation_time."""
        return self.simulation_time - self.timestamp_last_scenario_change
    
    def time_since_last_reading(self) -> float:
        """Calculate time since last valid sensor reading."""
        return self.simulation_time - self.timestamp_last_reading
    
    def can_change_scenario(self, min_stabilization_time_s: float) -> bool:
        """
        Check if enough time has passed to allow scenario change.
        
        Args:
            min_stabilization_time_s: Minimum time in scenario before change allowed
            
        Returns:
            True if scenario change is allowed
        """
        if self.mode != "AUTO":
            return False
        
        if self.config_change_in_progress or self.heater_rotation_in_progress:
            return False
        
        if self.time_since_scenario_change() < min_stabilization_time_s:
            return False
        
        return True
    
    def update_simulation_time(self, new_time: float) -> None:
        """
        Update simulation time from weather service response.
        
        This is the ONLY way simulation_time should be updated.
        Weather service is the authoritative time source.
        """
        self.simulation_time = new_time
    
    def add_temperature_reading(self, t_zewn: float, buffer_size: int = 3) -> float:
        """
        Add temperature reading to buffer and return moving average.
        
        Args:
            t_zewn: Temperature reading in °C
            buffer_size: Size of moving average buffer
            
        Returns:
            Moving average temperature
        """
        self.t_zewn_buffer.append(t_zewn)
        
        # Keep only last N readings
        if len(self.t_zewn_buffer) > buffer_size:
            self.t_zewn_buffer = self.t_zewn_buffer[-buffer_size:]
        
        # Return average
        return sum(self.t_zewn_buffer) / len(self.t_zewn_buffer)

