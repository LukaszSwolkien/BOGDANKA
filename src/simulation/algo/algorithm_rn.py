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
    rotation_period_hours: int              # [h] rotation period (same for all scenarios)
    rotation_duration_s: int = 180          # [s] time for heater rotation to complete (3 minutes)
    min_delta_time_s: int = 3600            # [s] minimum time difference for rotation
    stabilization_time_s: int = 30          # [s] stabilization time after scenario change
    algorithm_loop_cycle_s: int = 60        # [s] RN check frequency
    min_time_since_config_change_s: int = 3000  # [s] 50 minutes gap BEFORE and AFTER RC rotation
    min_time_between_rotations_s: int = 900     # [s] 15 minutes between rotations


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
    
    def __init__(self, config: RNConfig, state: AlgoState, algorithm_rc=None):
        self.config = config
        self.state = state
        self.algorithm_rc = algorithm_rc  # Reference to RC for coordination
        
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
            "too_close_before_rc": 0,         # Too close to next RC rotation
            "period_not_elapsed": 0,          # Rotation period for line not elapsed
            "global_spacing_not_met": 0,      # 15min global spacing between any rotations
            "no_suitable_heaters": 0,         # No heaters available for rotation
            "line_not_active": 0,             # Line not active in current scenario
        }
        
        # Track previous scenario to detect transitions from S0
        self._previous_scenario: Optional[Scenario] = None
        
        # Track previous configuration to detect RC changes (C1↔C2)
        # Initialize to current config to detect changes from the start
        self._previous_config: str = state.current_config
        
        LOGGER.info(
            f"Algorithm RN initialized: rotation_period={config.rotation_period_hours}h, "
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
        
        # Check if ongoing rotation has finished
        if self.state.heater_rotation_in_progress:
            if self.state.simulation_time >= self.state.heater_rotation_end_time:
                # Rotation complete!
                self.state.heater_rotation_in_progress = False
                LOGGER.info(f"✅ RN: Heater rotation complete (duration={self.config.rotation_duration_s}s)")
            else:
                # Still rotating
                remaining = self.state.heater_rotation_end_time - self.state.simulation_time
                return False, f"RN rotation in progress ({remaining:.0f}s remaining)"
        
        # Check if configuration changed (RC rotation C1↔C2)
        # This must be handled BEFORE scenario transitions to ensure correct heater states
        if self._previous_config != self.state.current_config:
            LOGGER.info(
                f"RN: Configuration change detected: {self._previous_config} → {self.state.current_config}, "
                f"syncing heater states for scenario {self.state.current_scenario.name}"
            )
            self._sync_heater_states_with_scenario()
            
            # Reset rotation timestamps to allow warm-up period in new configuration
            self._last_rotation_per_line[Line.C1] = self.state.simulation_time
            self._last_rotation_per_line[Line.C2] = self.state.simulation_time
            self._last_rotation_global = self.state.simulation_time
        
        # Update previous config for next iteration
        self._previous_config = self.state.current_config
        
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
                # Line not active - don't count this (not a rotation attempt)
                continue
            
            # STEP 2: Check rotation conditions (excluding RC coordination)
            # First check if rotation would be ready WITHOUT RC blocking
            can_rotate_without_rc, reason_text, reason_key = self._can_rotate_ignoring_rc(line)
            
            if not can_rotate_without_rc:
                # Rotation not ready yet (period not elapsed, no heaters, etc.)
                # Don't count this - it's not a collision, just not ready
                if int(self.state.simulation_time % 3600) < 60:  # Log periodically
                    LOGGER.debug(f"RN: {line.name} rotation not ready - {reason_text}")
                continue
            
            # Rotation IS ready! Now check RC coordination
            # This is the ONLY place we count collisions
            if self.state.config_change_in_progress:
                if self.state.simulation_time < self.state.config_rotation_end_time:
                    # COLLISION: RN ready to rotate but RC is rotating
                    self._blocked_by_reason["rc_rotation_in_progress"] += 1
                    self._blocked_count += 1
                    remaining = self.state.config_rotation_end_time - self.state.simulation_time
                    LOGGER.info(
                        f"⚠️  RN: {line.name} rotation COLLISION - RC rotation in progress "
                        f"(remaining={remaining:.0f}s, sim_time={self.state.simulation_time:.1f}s)"
                    )
                    continue
                else:
                    # Rotation finished but flag not cleared yet
                    self.state.config_change_in_progress = False
            
            # Check post-RC coordination (50min stabilization AFTER and BEFORE RC rotation)
            if self.state.current_scenario in [Scenario.S1, Scenario.S2, Scenario.S3, Scenario.S4]:
                time_since_config_change = self.state.simulation_time - self.state.timestamp_last_config_change
                if time_since_config_change < self.config.min_time_since_config_change_s:
                    # COORDINATION: RN waiting for stabilization AFTER RC
                    self._blocked_by_reason["too_soon_after_rc"] += 1
                    self._blocked_count += 1
                    LOGGER.info(
                        f"⏸️  RN: {line.name} rotation COORDINATION - waiting {self.config.min_time_since_config_change_s/60:.0f}min AFTER RC "
                        f"({time_since_config_change:.0f}s / {self.config.min_time_since_config_change_s}s)"
                    )
                    continue
                
                # Check time UNTIL next RC rotation (if algorithm_rc available)
                if self.algorithm_rc is not None:
                    time_until_next_rc = self.algorithm_rc.get_time_until_next_rotation()
                    if time_until_next_rc < self.config.min_time_since_config_change_s:
                        # COORDINATION: RN avoiding rotation too close BEFORE RC
                        self._blocked_by_reason["too_close_before_rc"] += 1
                        self._blocked_count += 1
                        LOGGER.info(
                            f"⏸️  RN: {line.name} rotation COORDINATION - next RC rotation in {time_until_next_rc/60:.0f}min, "
                            f"need {self.config.min_time_since_config_change_s/60:.0f}min gap BEFORE RC"
                        )
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
        
        IMPORTANT: This method updates _last_update_time to prevent incorrect time accumulation
        for heaters that are being activated/deactivated during sync.
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
        
        # CRITICAL: Update _last_update_time to current simulation time
        # This prevents newly activated heaters from accumulating time from before they were active
        self._last_update_time = self.state.simulation_time
    
    def _get_active_heaters(self) -> list[Heater]:
        """
        Get list of heaters that SHOULD BE active based on scenario and configuration.
        
        IMPORTANT: This uses INTELLIGENT SELECTION based on operating/idle times,
        not just a simple slice [N1, N2, N3].
        
        This implements the pseudocode function:
            Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy(ciąg, ilość)
        
        Returns:
            List of heaters sorted by priority (longest idle time, shortest operating time)
        """
        scenario = self.state.current_scenario
        config = self.state.current_config
        
        # S0: No heaters
        if scenario == Scenario.S0:
            return []
        
        # Determine how many heaters we need
        if scenario in [Scenario.S1, Scenario.S2, Scenario.S3, Scenario.S4]:
            heater_count = {
                Scenario.S1: 1,
                Scenario.S2: 2,
                Scenario.S3: 3,
                Scenario.S4: 4,
            }[scenario]
            
            if config == "Primary":
                # Line C1 (N1-N4) - select by operating time
                return self._select_heaters_by_usage(Line.C1, heater_count)
            else:  # Limited
                # Line C2 (N5-N8) - select by operating time
                return self._select_heaters_by_usage(Line.C2, heater_count)
        
        # S5-S8: Both lines active
        # Line 1: all 4 heaters (N1-N4) - no choice, all must work
        # Line 2: variable count (N5-N8) - select by operating time
        heater_count_line2 = {
            Scenario.S5: 1,  # 4+1=5 total
            Scenario.S6: 2,  # 4+2=6 total
            Scenario.S7: 3,  # 4+3=7 total
            Scenario.S8: 4,  # 4+4=8 total
        }[scenario]
        
        # C1: all 4 (no selection needed)
        active = [Heater.N1, Heater.N2, Heater.N3, Heater.N4]
        
        # C2: select by usage
        active.extend(self._select_heaters_by_usage(Line.C2, heater_count_line2))
        
        return active
    
    def _select_heaters_by_usage(self, line: Line, count: int) -> list[Heater]:
        """
        Select heaters for a line based on operating/idle time.
        
        Implements pseudocode: Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy()
        
        Sorting priority:
        1. Longest idle time (DESC) - heaters that have been off longest
        2. Shortest operating time (ASC) - least used heaters
        3. Earliest first_activation_timestamp (ASC) - tiebreaker
        
        Args:
            line: Which line (C1 or C2)
            count: How many heaters to select
        
        Returns:
            List of selected heaters (sorted by priority)
        """
        healthy_heaters = self._get_healthy_heaters_for_line(line)
        
        # Sort by: idle_time DESC, operating_time ASC, first_activation ASC
        sorted_heaters = sorted(
            healthy_heaters,
            key=lambda h: (
                -self._heater_tracking[h].idle_time_s,  # Longest idle first (negative for DESC)
                self._heater_tracking[h].operating_time_s,  # Shortest operating first
                self._heater_tracking[h].first_activation_timestamp or float('inf'),  # Earliest activation
            )
        )
        
        return sorted_heaters[:count]
    
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
    
    def is_line_operating(self, line: Line) -> bool:
        """
        Check if given line is currently operating (has active heaters).
        
        Public method for external use (e.g., display).
        
        Returns:
            True if line is operating (has power, heaters active)
        """
        scenario = self.state.current_scenario
        config = self.state.current_config
        
        if scenario == Scenario.S0:
            return False  # System off
        
        # S1-S4: Only ONE line operating at a time
        if scenario in [Scenario.S1, Scenario.S2, Scenario.S3, Scenario.S4]:
            if config == "Primary":
                return line == Line.C1  # C1 operating, C2 off
            else:  # Limited
                return line == Line.C2  # C2 operating, C1 off
        
        # S5-S8: BOTH lines operating (dual-line mode)
        if scenario in [Scenario.S5, Scenario.S6, Scenario.S7, Scenario.S8]:
            return True  # Both C1 and C2 operating
        
        return False
    
    def _can_rotate_ignoring_rc(self, line: Line) -> tuple[bool, str, Optional[str]]:
        """
        Check if rotation would be possible ignoring RC coordination.
        
        This checks:
        - Global 15-minute spacing
        - Reserve heaters availability
        - Rotation period elapsed
        
        But IGNORES:
        - RC rotation in progress
        - Post-RC stabilization period
        
        Used to determine if RN is "ready to rotate" before checking RC coordination.
        
        Returns:
            (can_rotate, reason_text, reason_key)
        """
        # Check global 15-minute spacing
        time_since_last_global = self.state.simulation_time - self._last_rotation_global
        if time_since_last_global < self.config.min_time_between_rotations_s:
            return False, f"Too soon since last rotation ({time_since_last_global:.0f}s < 15min)", "global_spacing_not_met"
        
        # Check if enough heaters available (need reserve)
        all_active_heaters = self._get_active_heaters()
        line_c1_heaters = {Heater.N1, Heater.N2, Heater.N3, Heater.N4}
        
        if line == Line.C1:
            required_active_count = len([h for h in all_active_heaters if h in line_c1_heaters])
        else:
            required_active_count = len([h for h in all_active_heaters if h not in line_c1_heaters])
        
        healthy_heaters_in_line = self._get_healthy_heaters_for_line(line)
        
        if len(healthy_heaters_in_line) <= required_active_count:
            return False, "No reserve heaters available", "no_suitable_heaters"
        
        # Check rotation period for this line
        time_since_last_rotation = self.state.simulation_time - self._last_rotation_per_line[line]
        rotation_period_s = self.config.rotation_period_hours * 3600
        
        if time_since_last_rotation < rotation_period_s:
            return False, f"Rotation period not elapsed ({time_since_last_rotation:.0f}s / {rotation_period_s}s)", "period_not_elapsed"
        
        return True, "Can rotate", None
    
    def _can_rotate(self, line: Line) -> tuple[bool, str, Optional[str]]:
        """
        Check if rotation is possible for given line.
        
        Returns:
            (can_rotate, reason_text, reason_key) where reason_key is for statistics tracking
        """
        # Check coordination with RC
        if self.state.config_change_in_progress:
            # Check if rotation is still in progress (simulation_time < end_time)
            if self.state.simulation_time < self.state.config_rotation_end_time:
                remaining = self.state.config_rotation_end_time - self.state.simulation_time
                return False, f"RC configuration change in progress ({remaining:.0f}s remaining)", "rc_rotation_in_progress"
            else:
                # Rotation finished but flag not cleared yet
                self.state.config_change_in_progress = False
        
        # In S1-S4, check if enough time passed since RC config change
        if self.state.current_scenario in [Scenario.S1, Scenario.S2, Scenario.S3, Scenario.S4]:
            time_since_config_change = self.state.simulation_time - self.state.timestamp_last_config_change
            if time_since_config_change < self.config.min_time_since_config_change_s:
                return False, f"Too soon after config change ({time_since_config_change:.0f}s < {self.config.min_time_since_config_change_s/60:.0f}min)", "too_soon_after_rc"
            
            # Check time UNTIL next RC rotation (if algorithm_rc available)
            if self.algorithm_rc is not None:
                time_until_next_rc = self.algorithm_rc.get_time_until_next_rotation()
                if time_until_next_rc < self.config.min_time_since_config_change_s:
                    return False, f"Too close to next RC rotation ({time_until_next_rc/60:.0f}min < {self.config.min_time_since_config_change_s/60:.0f}min)", "too_close_before_rc"
        
        # Check global 15-minute spacing
        time_since_last_global = self.state.simulation_time - self._last_rotation_global
        if time_since_last_global < self.config.min_time_between_rotations_s:
            return False, f"Too soon since last rotation ({time_since_last_global:.0f}s < 15min)", "global_spacing_not_met"
        
        # Check if enough heaters available (need reserve)
        # Use theoretical active count from scenario (not actual tracking state)
        # because we want to know if rotation is POSSIBLE given the scenario requirements
        all_active_heaters = self._get_active_heaters()  # Theoretical from scenario
        line_c1_heaters = {Heater.N1, Heater.N2, Heater.N3, Heater.N4}
        
        if line == Line.C1:
            required_active_count = len([h for h in all_active_heaters if h in line_c1_heaters])
        else:
            required_active_count = len([h for h in all_active_heaters if h not in line_c1_heaters])
        
        healthy_heaters_in_line = self._get_healthy_heaters_for_line(line)
        
        if len(healthy_heaters_in_line) <= required_active_count:
            return False, "No reserve heaters available", "no_suitable_heaters"
        
        # Check rotation period for this line
        time_since_last_rotation = self.state.simulation_time - self._last_rotation_per_line[line]
        rotation_period_s = self.config.rotation_period_hours * 3600  # Convert hours to seconds
        
        if time_since_last_rotation < rotation_period_s:
            return False, f"Rotation period not elapsed ({time_since_last_rotation:.0f}s / {rotation_period_s}s)", "period_not_elapsed"
        
        # In simulation, we don't check stability conditions (temperature, flow, etc.)
        # In real system, would check if system is stable
        
        return True, "Can rotate", None
    
    def _get_active_heaters_for_line(self, line: Line) -> list[Heater]:
        """
        Get ACTUALLY ACTIVE heaters for specific line based on current tracking state.
        
        IMPORTANT: Returns heaters that are ACTUALLY active in _heater_tracking,
        not the theoretical list from _get_active_heaters() which is based on scenario.
        
        This is critical for rotation selection - we must know which heaters are
        really running NOW, not which should be running according to scenario.
        """
        line_c1_heaters = {Heater.N1, Heater.N2, Heater.N3, Heater.N4}
        
        # Get heaters for this line
        if line == Line.C1:
            line_heaters = line_c1_heaters
        else:
            line_heaters = {Heater.N5, Heater.N6, Heater.N7, Heater.N8}
        
        # Return only those that are ACTUALLY ACTIVE in tracking state
        return [
            heater for heater in line_heaters
            if self._heater_tracking[heater].state == HeaterState.ACTIVE
        ]
    
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
        self.state.heater_rotation_end_time = self.state.simulation_time + self.config.rotation_duration_s
        
        # Simulate rotation (in real system this would take time)
        # We don't change simulation_time - weather service controls that
        # We just track when rotation will end
        
        # Update heater states
        self._heater_tracking[heater_off].state = HeaterState.IDLE
        self._heater_tracking[heater_on].state = HeaterState.ACTIVE
        self._heater_tracking[heater_on].first_activation_timestamp = self.state.simulation_time
        
        # Update rotation timestamps
        self._last_rotation_per_line[line] = self.state.simulation_time
        self._last_rotation_global = self.state.simulation_time
        
        # Increment rotation counter
        self._rotation_count += 1
        
        LOGGER.info(
            f"🔄 RN: Heater rotation in progress in {line.name}: {heater_off.name} → {heater_on.name} "
            f"(duration={self.config.rotation_duration_s}s, will complete at t={self.state.heater_rotation_end_time:.1f}s)"
        )
        
        # Note: Lock will be released when simulation_time >= heater_rotation_end_time
        # This happens in next process() call
        
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
            
            # Get rotation period (convert hours to seconds)
            rotation_period_s = self.config.rotation_period_hours * 3600
            
            # Time since last rotation for this line
            time_since_last = self.state.simulation_time - self._last_rotation_per_line[line]
            
            # Time remaining
            time_remaining = rotation_period_s - time_since_last
            
            result[line] = max(0.0, time_remaining)
        
        return result

