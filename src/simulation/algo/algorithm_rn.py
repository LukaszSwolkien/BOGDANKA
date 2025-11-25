"""Algorithm RN: Heater Rotation within Line."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from common.domain import Heater, Line, Scenario
from .state import AlgoState

LOGGER = logging.getLogger("algo-service.rn")


class HeaterState(Enum):
    """Heater state."""
    ACTIVE = "active"      # Working in current scenario
    IDLE = "idle"          # Healthy but not in use
    FAULTY = "faulty"      # Not available due to fault


@dataclass
class RNConfig:
    """Configuration for Algorithm RN."""
    # Rotation period for each scenario (seconds)
    rotation_period_s: dict[Scenario, int]
    min_delta_time_s: int = 3600  # 1 hour minimum time difference
    stabilization_time_s: int = 30
    algorithm_loop_cycle_s: int = 60
    min_time_since_config_change_s: int = 3600  # 1 hour after RC change
    min_time_between_rotations_s: int = 900  # 15 minutes


@dataclass
class HeaterTracking:
    """Track heater operating time."""
    operating_time_s: float = 0.0
    idle_time_s: float = 0.0
    first_activation_timestamp: float = 0.0
    state: HeaterState = HeaterState.IDLE


class AlgorithmRN:
    """
    Algorithm RN: Heater Rotation within Line.
    
    Rotates heaters within each ventilation line to balance operating time
    and extend equipment lifetime.
    
    Follows pseudocode from algo_pseudokod.md exactly.
    """
    
    def __init__(self, config: RNConfig, state: AlgoState):
        self.config = config
        self.state = state
        
        # Track time for each heater (8 heaters total: N1-N4 in Line 1, N5-N8 in Line 2)
        self._heater_tracking: dict[Heater, HeaterTracking] = {
            heater: HeaterTracking() for heater in Heater
        }
        
        # Track last rotation per line
        self._last_rotation_per_line: dict[Line, float] = {
            Line.C1: 0.0,
            Line.C2: 0.0,
        }
        
        # Global last rotation (for 15min spacing)
        self._last_rotation_global: float = 0.0
        
        # Track last update time for incremental counting
        self._last_update_time: Optional[float] = None
        
        # Track total number of heater rotations
        self._rotation_count = 0
        
        # Track number of times rotation was blocked
        self._blocked_count = 0
        
        # Detailed blocking statistics
        self._blocked_by_reason: dict[str, int] = {
            "rc_rotation_in_progress": 0,     # RC config change blocking RN
            "too_soon_after_rc": 0,           # Gap after RC not elapsed
            "period_not_elapsed": 0,          # Rotation period for line not elapsed
            "global_spacing_not_met": 0,      # 15min global spacing between any rotations
            "no_suitable_heaters": 0,         # No heaters available for rotation
            "line_not_active": 0,             # Line not active in current scenario
        }
        
        # Track previous scenario to detect transitions from S0
        self._previous_scenario: Optional[Scenario] = None
        
        LOGGER.info(
            f"Algorithm RN initialized: rotation_periods={config.rotation_period_s}, "
            f"min_delta_time={config.min_delta_time_s}s"
        )
    
    def process(self) -> tuple[bool, str]:
        """
        Process RN algorithm - check if heater rotation is needed.
        
        Should be called every algorithm_loop_cycle_s (e.g., 60s).
        
        Returns:
            (rotation_occurred: bool, message: str)
        """
        # Update time counters (ALWAYS)
        self._update_time_counters()
        
        # Check if we need to adjust heater states due to scenario change
        # Use different strategies based on the type of transition
        if self._previous_scenario is not None and self._previous_scenario != self.state.current_scenario:
            should_sync = self._should_sync_heater_states(self._previous_scenario, self.state.current_scenario)
            
            if should_sync:
                # Major transition: full sync needed
                LOGGER.info(
                    f"RN: Major scenario transition {self._previous_scenario.name} → {self.state.current_scenario.name}, "
                    f"syncing heater states"
                )
                self._sync_heater_states_with_scenario()
                
                # Reset rotation timestamps when transitioning from S0 (warm-up period)
                if self._previous_scenario == Scenario.S0:
                    self._last_rotation_per_line[Line.C1] = self.state.simulation_time
                    self._last_rotation_per_line[Line.C2] = self.state.simulation_time
                    self._last_rotation_global = self.state.simulation_time
            else:
                # Minor transition within S1-S4 or S5-S8: adjust heater count intelligently
                LOGGER.debug(
                    f"RN: Minor scenario transition {self._previous_scenario.name} → {self.state.current_scenario.name}, "
                    f"adjusting heater count"
                )
                self._adjust_heater_count()
        
        # Update previous scenario for next iteration
        self._previous_scenario = self.state.current_scenario
        
        # Check each line for potential rotation
        for line in [Line.C1, Line.C2]:
            # STEP 0: Check if line is active
            is_active = self._is_line_active(line)
            
            # Log line status in S5-S8 for visibility
            if self.state.current_scenario in [Scenario.S5, Scenario.S6, Scenario.S7, Scenario.S8]:
                if int(self.state.simulation_time % 3600) < 60:  # Every simulated hour
                    active_heaters = self._get_active_heaters_for_line(line)
                    healthy_heaters = self._get_healthy_heaters_for_line(line)
                    LOGGER.info(
                        f"RN: {line.name} in {self.state.current_scenario.name}: "
                        f"active={is_active}, "
                        f"active_heaters={len(active_heaters)}, "
                        f"healthy_heaters={len(healthy_heaters)}"
                    )
            
            if not is_active:
                # Track as blocked (line not active in this scenario)
                self._blocked_count += 1
                self._blocked_by_reason["line_not_active"] = self._blocked_by_reason.get("line_not_active", 0) + 1
                continue
            
            # STEP 2: Check rotation conditions
            can_rotate, reason_text, reason_key = self._can_rotate(line)
            if not can_rotate:
                # Count this as a blocked rotation attempt
                self._blocked_count += 1
                if reason_key:
                    self._blocked_by_reason[reason_key] = self._blocked_by_reason.get(reason_key, 0) + 1
                
                # Log blocking reasons at INFO level for visibility
                # Log coordination blocks always
                if "RC configuration change" in reason_text or "Too soon after config change" in reason_text:
                    LOGGER.info(f"⏸️  RN: {line.name} rotation BLOCKED - {reason_text}")
                # Log other blocks periodically (every hour of sim time)
                elif int(self.state.simulation_time % 3600) < 60:
                    LOGGER.info(f"⏸️  RN: {line.name} rotation not ready - {reason_text}")
                # Also log for C2 in S5-S8 to diagnose the issue
                elif line == Line.C2 and self.state.current_scenario in [Scenario.S5, Scenario.S6, Scenario.S7]:
                    LOGGER.debug(f"RN: {line.name} cannot rotate in {self.state.current_scenario.name} - {reason_text}")
                continue
            
            # STEP 3: Select heaters to swap
            heater_off, heater_on, delta_time = self._select_heaters_for_rotation(line)
            
            if heater_off is None or heater_on is None:
                LOGGER.debug(f"RN: {line.name} no suitable heaters for rotation")
                continue
            
            if delta_time < self.config.min_delta_time_s:
                LOGGER.debug(
                    f"RN: {line.name} time delta too small "
                    f"({delta_time:.0f}s < {self.config.min_delta_time_s}s)"
                )
                continue
            
            # STEP 4: Execute rotation
            LOGGER.info(
                f"RN: Rotation ready for {line.name}, will rotate {heater_off.name} → {heater_on.name} "
                f"(delta={delta_time:.0f}s, sim_time={self.state.simulation_time:.1f}s)"
            )
            return self._execute_rotation(line, heater_off, heater_on)
        
        # No rotation occurred
        return False, "No rotation needed"
    
    def _update_time_counters(self) -> None:
        """Update operating and idle time for all heaters."""
        if self._last_update_time is None:
            self._last_update_time = self.state.simulation_time
            # Initialize heater states based on current scenario
            self._sync_heater_states_with_scenario()
            return
        
        time_delta = self.state.simulation_time - self._last_update_time
        
        if time_delta > 0:
            for heater in Heater:
                tracking = self._heater_tracking[heater]
                
                if tracking.state == HeaterState.ACTIVE:
                    tracking.operating_time_s += time_delta
                    if tracking.first_activation_timestamp == 0.0:
                        tracking.first_activation_timestamp = self.state.simulation_time
                elif tracking.state == HeaterState.IDLE:
                    tracking.idle_time_s += time_delta
                # FAULTY heaters don't accumulate time
            
            self._last_update_time = self.state.simulation_time
    
    def _should_sync_heater_states(self, old_scenario: Scenario, new_scenario: Scenario) -> bool:
        """
        Determine if heater states should be synced due to scenario change.
        
        Syncing is ONLY needed for major structural transitions:
        - Transitions from/to S0 (system shutdown/startup)
        - Transitions between single-line (S1-S4) and dual-line (S5-S8) operation
        - First transition to any scenario (initialization)
        
        For minor transitions (e.g., S6→S7), we use _adjust_heater_count() instead,
        which preserves rotation state.
        """
        # Always sync when transitioning from or to S0
        if old_scenario == Scenario.S0 or new_scenario == Scenario.S0:
            return True
        
        # Sync when transitioning between single-line and dual-line operation
        single_line_scenarios = {Scenario.S1, Scenario.S2, Scenario.S3, Scenario.S4}
        
        old_is_single = old_scenario in single_line_scenarios
        new_is_single = new_scenario in single_line_scenarios
        
        # If one is single-line and the other is dual-line, sync is needed
        if old_is_single != new_is_single:
            return True
        
        # For transitions within S1-S4 or within S5-S8, DON'T sync
        # Instead, use _adjust_heater_count() which preserves rotation state
        return False
    
    def _adjust_heater_count(self) -> None:
        """
        Adjust active heater count for minor scenario transitions (e.g., S3→S2→S3).
        
        This method intelligently adds or removes heaters while preserving rotation state:
        - When adding heaters: activates heaters with LEAST operating time (fairness!)
        - When removing heaters: deactivates heaters with MOST operating time
        
        Example: S3→S2→S3
        - S3: N1, N2, N3 active
        - S3→S2: Deactivate N3 (most used)
        - S2→S3: Activate N4 (least used), NOT N3!
        
        This preserves rotation fairness unlike _sync_heater_states_with_scenario().
        """
        # Get currently active heaters from tracking (not from _get_active_heaters()!)
        currently_active_c1 = []
        currently_active_c2 = []
        for heater, tracking in self._heater_tracking.items():
            if tracking.state == HeaterState.ACTIVE:
                if heater in {Heater.N1, Heater.N2, Heater.N3, Heater.N4}:
                    currently_active_c1.append(heater)
                else:
                    currently_active_c2.append(heater)
        
        # Get all healthy heaters per line
        healthy_c1 = self._get_healthy_heaters_for_line(Line.C1)
        healthy_c2 = self._get_healthy_heaters_for_line(Line.C2)
        
        # Determine how many we SHOULD have based on scenario
        scenario = self.state.current_scenario
        
        if scenario == Scenario.S0:
            required_c1, required_c2 = 0, 0
        elif scenario in [Scenario.S1, Scenario.S2, Scenario.S3, Scenario.S4]:
            # Single line operation - depends on config
            heater_count = {
                Scenario.S1: 1,
                Scenario.S2: 2,
                Scenario.S3: 3,
                Scenario.S4: 4,
            }[scenario]
            
            if self.state.current_config == "Primary":
                required_c1 = heater_count
                required_c2 = 0
            else:  # Limited
                required_c1 = 0
                required_c2 = heater_count
        else:  # S5-S8: dual line
            heater_count_line2 = {
                Scenario.S5: 1,
                Scenario.S6: 2,
                Scenario.S7: 3,
                Scenario.S8: 4,
            }[scenario]
            required_c1 = 4  # Always all 4 for C1
            required_c2 = heater_count_line2
        
        # Adjust Line C1
        self._adjust_line_heaters(Line.C1, currently_active_c1, healthy_c1, len(currently_active_c1), required_c1)
        
        # Adjust Line C2
        self._adjust_line_heaters(Line.C2, currently_active_c2, healthy_c2, len(currently_active_c2), required_c2)
    
    def _adjust_line_heaters(
        self, 
        line: Line, 
        active: list[Heater], 
        healthy: list[Heater],
        current_count: int,
        required_count: int
    ) -> None:
        """
        Adjust heater count for a specific line.
        
        Args:
            line: Which line (C1 or C2)
            active: Currently active heaters in this line
            healthy: All healthy heaters in this line
            current_count: How many are currently active
            required_count: How many we need
        """
        delta = required_count - current_count
        
        if delta == 0:
            return  # No change needed
        
        if delta > 0:
            # Need to ADD heaters - choose ones with LEAST operating time
            idle_heaters = [h for h in healthy if h not in active]
            
            # Sort by operating time (ascending)
            idle_sorted = sorted(
                idle_heaters,
                key=lambda h: self._heater_tracking[h].operating_time_s
            )
            
            # Activate the ones with least operating time
            for i in range(min(delta, len(idle_sorted))):
                heater = idle_sorted[i]
                LOGGER.info(
                    f"RN: Adding heater {heater.name} for scenario {self.state.current_scenario.name} "
                    f"(operating_time={self._heater_tracking[heater].operating_time_s:.1f}s)"
                )
                self._heater_tracking[heater].state = HeaterState.ACTIVE
                self._heater_tracking[heater].first_activation_timestamp = self.state.simulation_time
        
        else:  # delta < 0
            # Need to REMOVE heaters - choose ones with MOST operating time
            to_remove = abs(delta)
            
            # Sort by operating time (descending)
            active_sorted = sorted(
                active,
                key=lambda h: self._heater_tracking[h].operating_time_s,
                reverse=True
            )
            
            # Deactivate the ones with most operating time
            for i in range(min(to_remove, len(active_sorted))):
                heater = active_sorted[i]
                LOGGER.info(
                    f"RN: Removing heater {heater.name} for scenario {self.state.current_scenario.name} "
                    f"(operating_time={self._heater_tracking[heater].operating_time_s:.1f}s)"
                )
                self._heater_tracking[heater].state = HeaterState.IDLE
    
    def _sync_heater_states_with_scenario(self) -> None:
        """
        Synchronize heater states with current scenario and configuration.
        
        WARNING: This forcibly sets heater states based on scenario, overriding rotation history.
        Only call during initialization or when explicitly needed (e.g., after major scenario change).
        For normal operation, heater states are managed by rotation logic.
        """
        # Get active heaters for current scenario/config
        active_heaters = self._get_active_heaters()
        active_names = [h.name for h in active_heaters]
        
        LOGGER.info(
            f"RN: Syncing heater states with scenario {self.state.current_scenario.name}, "
            f"config={self.state.current_config}, active_heaters={active_names}"
        )
        
        # Update all heater states
        for heater in Heater:
            tracking = self._heater_tracking[heater]
            
            # In simulation, all heaters are healthy (no faults)
            if heater in active_heaters:
                tracking.state = HeaterState.ACTIVE
            else:
                tracking.state = HeaterState.IDLE
    
    def _get_active_heaters(self) -> list[Heater]:
        """Get list of currently active heaters based on scenario and configuration."""
        scenario = self.state.current_scenario
        config = self.state.current_config
        
        # S0: No heaters
        if scenario == Scenario.S0:
            return []
        
        # S1-S4: Single line operation (depends on Primary/Limited config)
        if scenario in [Scenario.S1, Scenario.S2, Scenario.S3, Scenario.S4]:
            heater_count = {
                Scenario.S1: 1,
                Scenario.S2: 2,
                Scenario.S3: 3,
                Scenario.S4: 4,
            }[scenario]
            
            if config == "Primary":
                # Line 1 (upper) - N1, N2, N3, N4
                return [Heater.N1, Heater.N2, Heater.N3, Heater.N4][:heater_count]
            else:  # Limited
                # Line 2 (lower) - N5, N6, N7, N8
                return [Heater.N5, Heater.N6, Heater.N7, Heater.N8][:heater_count]
        
        # S5-S8: Both lines active
        # Line 1: all 4 heaters (N1-N4)
        # Line 2: variable count (N5-N8)
        heater_count_line2 = {
            Scenario.S5: 1,  # 4+1=5 total
            Scenario.S6: 2,  # 4+2=6 total
            Scenario.S7: 3,  # 4+3=7 total
            Scenario.S8: 4,  # 4+4=8 total
        }[scenario]
        
        active = [Heater.N1, Heater.N2, Heater.N3, Heater.N4]  # Line 1: all
        active.extend([Heater.N5, Heater.N6, Heater.N7, Heater.N8][:heater_count_line2])
        
        return active
    
    def _is_line_active(self, line: Line) -> bool:
        """Check if given line is active in current scenario/configuration."""
        scenario = self.state.current_scenario
        config = self.state.current_config
        
        if scenario == Scenario.S0:
            return False
        
        # S1-S4: Only ONE line active
        if scenario in [Scenario.S1, Scenario.S2, Scenario.S3, Scenario.S4]:
            if config == "Primary" and line == Line.C2:
                return False  # C2 disabled in Primary
            if config == "Limited" and line == Line.C1:
                return False  # C1 disabled in Limited
        
        # S5-S8: Line C1 cannot rotate (all 4 heaters N1-N4 must work, no reserve)
        if scenario in [Scenario.S5, Scenario.S6, Scenario.S7, Scenario.S8]:
            if line == Line.C1:
                return False  # Rotation impossible - all heaters must work
        
        return True
    
    def _can_rotate(self, line: Line) -> tuple[bool, str, Optional[str]]:
        """
        Check if rotation is possible for given line.
        
        Returns:
            (can_rotate, reason_text, reason_key) where reason_key is for statistics tracking
        """
        # Check coordination with RC
        if self.state.config_change_in_progress:
            return False, "RC configuration change in progress", "rc_rotation_in_progress"
        
        # In S1-S4, check if enough time passed since RC config change
        if self.state.current_scenario in [Scenario.S1, Scenario.S2, Scenario.S3, Scenario.S4]:
            time_since_config_change = self.state.simulation_time - self.state.timestamp_last_config_change
            if time_since_config_change < self.config.min_time_since_config_change_s:
                return False, f"Too soon after config change ({time_since_config_change:.0f}s < 1h)", "too_soon_after_rc"
        
        # Check global 15-minute spacing
        time_since_last_global = self.state.simulation_time - self._last_rotation_global
        if time_since_last_global < self.config.min_time_between_rotations_s:
            return False, f"Too soon since last rotation ({time_since_last_global:.0f}s < 15min)", "global_spacing_not_met"
        
        # Check if enough heaters available (need reserve)
        active_heaters_in_line = self._get_active_heaters_for_line(line)
        healthy_heaters_in_line = self._get_healthy_heaters_for_line(line)
        
        if len(healthy_heaters_in_line) <= len(active_heaters_in_line):
            return False, "No reserve heaters available", "no_suitable_heaters"
        
        # Check rotation period for this line
        time_since_last_rotation = self.state.simulation_time - self._last_rotation_per_line[line]
        rotation_period = self.config.rotation_period_s.get(self.state.current_scenario, float('inf'))
        
        if time_since_last_rotation < rotation_period:
            return False, f"Rotation period not elapsed ({time_since_last_rotation:.0f}s / {rotation_period}s)", "period_not_elapsed"
        
        # In simulation, we don't check stability conditions (temperature, flow, etc.)
        # In real system, would check if system is stable
        
        return True, "Can rotate", None
    
    def _get_active_heaters_for_line(self, line: Line) -> list[Heater]:
        """Get active heaters for specific line."""
        active_heaters = self._get_active_heaters()
        line_c1_heaters = {Heater.N1, Heater.N2, Heater.N3, Heater.N4}
        if line == Line.C1:
            return [h for h in active_heaters if h in line_c1_heaters]  # N1-N4
        else:
            return [h for h in active_heaters if h not in line_c1_heaters]   # N5-N8
    
    def _get_healthy_heaters_for_line(self, line: Line) -> list[Heater]:
        """Get all healthy heaters for specific line."""
        if line == Line.C1:
            heaters = [Heater.N1, Heater.N2, Heater.N3, Heater.N4]
        else:
            heaters = [Heater.N5, Heater.N6, Heater.N7, Heater.N8]
        
        # In simulation, all heaters are healthy
        return [h for h in heaters if self._heater_tracking[h].state != HeaterState.FAULTY]
    
    def _select_heaters_for_rotation(self, line: Line) -> tuple[Optional[Heater], Optional[Heater], float]:
        """
        Select heater to turn off and heater to turn on.
        
        Returns:
            (heater_to_turn_off, heater_to_turn_on, time_delta)
        """
        active_heaters = self._get_active_heaters_for_line(line)
        all_heaters = self._get_healthy_heaters_for_line(line)
        idle_heaters = [h for h in all_heaters if h not in active_heaters]
        
        if not active_heaters or not idle_heaters:
            return None, None, 0.0
        
        # Find heater with longest operating time (to turn off)
        heater_off = None
        max_operating_time = 0.0
        earliest_activation = float('inf')
        
        for heater in active_heaters:
            tracking = self._heater_tracking[heater]
            if tracking.operating_time_s > max_operating_time:
                max_operating_time = tracking.operating_time_s
                heater_off = heater
                earliest_activation = tracking.first_activation_timestamp
            elif tracking.operating_time_s == max_operating_time:
                # If equal, choose the one activated first
                if tracking.first_activation_timestamp < earliest_activation:
                    heater_off = heater
                    earliest_activation = tracking.first_activation_timestamp
        
        # Find heater with shortest operating time (to turn on)
        # We want to balance operating times, not compare operating vs idle time
        heater_on = None
        min_operating_time = float('inf')
        
        for heater in idle_heaters:
            tracking = self._heater_tracking[heater]
            if tracking.operating_time_s < min_operating_time:
                min_operating_time = tracking.operating_time_s
                heater_on = heater
        
        # Delta is difference in OPERATING times (not operating vs idle)
        # This ensures we rotate when there's significant imbalance in usage
        delta_time = max_operating_time - min_operating_time
        
        return heater_off, heater_on, delta_time
    
    def _execute_rotation(self, line: Line, heater_off: Heater, heater_on: Heater) -> tuple[bool, str]:
        """
        Execute heater rotation.
        
        In simulation, we don't control physical equipment, just update state.
        In real system, this would:
        1. Turn on new heater first (safety)
        2. Verify it's working
        3. Turn off old heater
        4. Wait for stabilization
        """
        LOGGER.info(
            f"🔄 RN: Heater rotation starting in {line.name}: {heater_off.name} → {heater_on.name} "
            f"(sim_time={self.state.simulation_time:.1f}s, "
            f"scenario={self.state.current_scenario.name}, "
            f"{heater_off.name}_operating={self._heater_tracking[heater_off].operating_time_s:.1f}s, "
            f"{heater_on.name}_idle={self._heater_tracking[heater_on].idle_time_s:.1f}s, "
            f"delta={self._heater_tracking[heater_off].operating_time_s - self._heater_tracking[heater_on].idle_time_s:.1f}s)"
        )
        
        # Set lock to prevent RC from changing config
        self.state.heater_rotation_in_progress = True
        
        # Simulate rotation (in real system this would take time)
        # Update heater states
        self._heater_tracking[heater_off].state = HeaterState.IDLE
        self._heater_tracking[heater_on].state = HeaterState.ACTIVE
        self._heater_tracking[heater_on].first_activation_timestamp = self.state.simulation_time
        
        # Update rotation timestamps
        self._last_rotation_per_line[line] = self.state.simulation_time
        self._last_rotation_global = self.state.simulation_time
        
        # Increment rotation counter
        self._rotation_count += 1
        
        # Release lock
        self.state.heater_rotation_in_progress = False
        
        LOGGER.info(
            f"✅ RN: Heater rotation complete in {line.name}: {heater_off.name} → {heater_on.name} "
            f"({heater_off.name} now IDLE, {heater_on.name} now ACTIVE)"
        )
        
        return True, f"Heater rotated in {line.name}: {heater_off.name} → {heater_on.name}"
    
    def get_heater_operating_time(self, heater: Heater) -> float:
        """Get total operating time for a heater."""
        return self._heater_tracking[heater].operating_time_s
    
    def get_heater_idle_time(self, heater: Heater) -> float:
        """Get total idle time for a heater."""
        return self._heater_tracking[heater].idle_time_s
    
    def get_heater_state(self, heater: Heater) -> HeaterState:
        """Get current state of a heater."""
        return self._heater_tracking[heater].state

    def get_rotation_count(self) -> int:
        """Get total number of heater rotations performed."""
        return self._rotation_count
    
    def get_blocked_count(self) -> int:
        """Get total number of times rotation was blocked."""
        return self._blocked_count
    
    def get_blocked_by_reason(self) -> dict[str, int]:
        """Get detailed blocking statistics by reason."""
        return self._blocked_by_reason.copy()
    
    def get_time_to_next_rotation(self) -> dict[Line, float]:
        """
        Get time remaining until next rotation is possible for each line (seconds).
        
        Returns:
            Dictionary mapping Line to time in seconds (0.0 if rotation already possible, -1.0 if not applicable).
        """
        result = {}
        
        for line in [Line.C1, Line.C2]:
            # Check if line is active in current scenario
            if not self._is_line_active(line):
                # Return -1 to indicate rotation is not applicable for this line
                result[line] = -1.0
                continue
            
            # Get rotation period for current scenario
            rotation_period_s = self.config.rotation_period_s.get(
                self.state.current_scenario,
                86400  # Default 24h
            )
            
            # Time since last rotation for this line
            time_since_last = self.state.simulation_time - self._last_rotation_per_line[line]
            
            # Time remaining
            time_remaining = rotation_period_s - time_since_last
            
            result[line] = max(0.0, time_remaining)
        
        return result

