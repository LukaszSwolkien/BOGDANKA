"""Algorithm RC: Configuration Rotation (Primary ↔ Limited)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from common.domain import Scenario
from .state import AlgoState

LOGGER = logging.getLogger("algo-service.rc")


@dataclass
class RCConfig:
    """Configuration for Algorithm RC."""
    rotation_period_hours: int = 168  # 7 days
    algorithm_loop_cycle_s: int = 60
    min_operating_time_s: int = 3600  # 1 hour minimum before rotation


class AlgorithmRC:
    """
    Algorithm RC: Configuration Rotation.
    
    Rotates between Primary (C1) and Limited (C2) configurations in scenarios S1-S4
    to balance operating time between the two ventilation lines.
    
    Follows pseudocode from algo_pseudokod.md exactly.
    """
    
    def __init__(self, config: RCConfig, state: AlgoState):
        self.config = config
        self.state = state
        
        # Local state tracking
        self._time_in_primary = 0.0
        self._time_in_limited = 0.0
        self._last_update_time = None  # Use None to track if initialized
        self._rotation_count = 0  # Track number of configuration changes
        self._blocked_count = 0  # Track number of times rotation was blocked
        self._previous_scenario: Optional[Scenario] = None  # Track scenario transitions
        
        # Detailed blocking statistics
        self._blocked_by_reason: dict[str, int] = {
            "rn_rotation_in_progress": 0,    # RN heater rotation blocking RC
            "scenario_not_suitable": 0,       # Wrong scenario (S0, S5-S8)
            "mode_not_auto": 0,               # Mode is not AUTO
            "period_not_elapsed": 0,          # Rotation period not yet elapsed
        }
        
        LOGGER.info(
            f"Algorithm RC initialized: rotation_period={config.rotation_period_hours}h, "
            f"min_operating_time={config.min_operating_time_s}s"
        )
    
    def process(self) -> tuple[bool, str]:
        """
        Process RC algorithm - check if configuration rotation is needed.
        
        Should be called every algorithm_loop_cycle_s (e.g., 60s).
        
        Returns:
            (rotation_occurred: bool, message: str)
        """
        # Update time counters (ALWAYS, even if rotation not possible)
        self._update_time_counters()
        
        # Check if we're transitioning from S0 to S1-S4
        # Reset the config change timestamp to prevent immediate rotation
        if self._previous_scenario == Scenario.S0 and self.state.current_scenario in [
            Scenario.S1, Scenario.S2, Scenario.S3, Scenario.S4
        ]:
            LOGGER.info(
                f"RC: Detected transition from S0 to {self.state.current_scenario.name}, "
                f"resetting config change timestamp to allow warm-up period"
            )
            self.state.timestamp_last_config_change = self.state.simulation_time
        
        # Update previous scenario for next iteration
        self._previous_scenario = self.state.current_scenario
        
        # Step 1: Check if rotation is possible
        rotation_possible, block_reason = self._check_rotation_possible()
        if not rotation_possible:
            # Track the specific blocking reason
            if block_reason:
                self._blocked_by_reason[block_reason] = self._blocked_by_reason.get(block_reason, 0) + 1
                self._blocked_count += 1
            
            # If we're in scenario that requires Primary but we're in Limited,
            # force switch back to Primary
            if self._should_force_primary():
                return self._execute_configuration_change("Primary")
            # Log why rotation is not possible periodically
            if self.state.simulation_time % 600 == 0:  # Every 10 minutes
                LOGGER.debug(f"RC: Rotation not possible (scenario={self.state.current_scenario.name}, mode={self.state.mode})")
            return False, f"Rotation not possible (scenario={self.state.current_scenario.name})"
        
        # Step 2: Check if rotation period has elapsed
        if not self._rotation_period_elapsed():
            self._blocked_by_reason["period_not_elapsed"] += 1
            self._blocked_count += 1
            
            time_since = self.state.simulation_time - self.state.timestamp_last_config_change
            period_s = self.config.rotation_period_hours * 3600
            remaining_s = period_s - time_since
            # Log progress periodically (every simulated hour, allowing 60s tolerance)
            hours_elapsed = int(time_since / 3600)
            if hours_elapsed > 0 and time_since % 3600 < 60:
                LOGGER.info(
                    f"RC: In {self.state.current_config} config for {hours_elapsed:.0f}h "
                    f"(rotation in {remaining_s/3600:.0f}h)"
                )
            return False, (
                f"Rotation period not elapsed "
                f"({time_since:.0f}s / {period_s}s)"
            )
        
        # Step 3: Determine new configuration
        new_config = "Limited" if self.state.current_config == "Primary" else "Primary"
        
        LOGGER.info(
            f"RC: Rotation period elapsed, preparing to rotate: {self.state.current_config} → {new_config} "
            f"(sim_time={self.state.simulation_time:.1f}s, {self.state.simulation_time/3600:.1f}h)"
        )
        
        # Step 4: Check coordination with RN
        if self.state.heater_rotation_in_progress:
            self._blocked_by_reason["rn_rotation_in_progress"] += 1
            self._blocked_count += 1
            LOGGER.info(
                f"⏸️  RC: Configuration rotation BLOCKED - RN heater rotation in progress "
                f"(current={self.state.current_config}, sim_time={self.state.simulation_time:.1f}s)"
            )
            return False, "RC rotation deferred - RN heater rotation in progress"
        
        # Step 5: Execute rotation
        return self._execute_configuration_change(new_config)
    
    def _update_time_counters(self) -> None:
        """Update time spent in each configuration."""
        if self._last_update_time is None:
            self._last_update_time = self.state.simulation_time
            return
        
        time_delta = self.state.simulation_time - self._last_update_time
        
        if time_delta > 0:
            if self.state.current_config == "Primary":
                self._time_in_primary += time_delta
            else:
                self._time_in_limited += time_delta
            
            self._last_update_time = self.state.simulation_time
    
    def _check_rotation_possible(self) -> tuple[bool, Optional[str]]:
        """
        Check if rotation is possible based on scenario and system state.
        
        Rotation is only possible in scenarios S1-S4 (single line operation).
        In S5-S8, both lines work in parallel (Primary configuration by definition).
        
        Returns:
            (is_possible, block_reason) where block_reason is the key for _blocked_by_reason dict
        """
        # Must be in AUTO mode
        if self.state.mode != "AUTO":
            return False, "mode_not_auto"
        
        # Only rotate in S1-S4 (single line scenarios)
        if self.state.current_scenario not in [Scenario.S1, Scenario.S2, Scenario.S3, Scenario.S4]:
            return False, "scenario_not_suitable"
        
        # In simulation, we don't check physical equipment health
        # In real system, would check:
        # - All C2 heaters operational
        # - W2 fan operational  
        # - No critical alarms
        
        return True, None
    
    def _should_force_primary(self) -> bool:
        """
        Check if we should force switch to Primary configuration.
        
        This handles the case where we're in S5-S8 (which require Primary)
        but somehow we're in Limited configuration.
        """
        # S5-S8 always use Primary (both lines in parallel)
        if self.state.current_scenario in [Scenario.S5, Scenario.S6, Scenario.S7, Scenario.S8]:
            if self.state.current_config != "Primary":
                LOGGER.warning(
                    f"Forcing Primary config for scenario {self.state.current_scenario.name} "
                    f"(was in {self.state.current_config})"
                )
                return True
        return False
    
    def _rotation_period_elapsed(self) -> bool:
        """Check if enough time has passed since last rotation."""
        # Calculate rotation period in seconds
        rotation_period_s = self.config.rotation_period_hours * 3600
        
        # Add hysteresis (5 minutes = 300s per pseudocode global params)
        hysteresis_s = 300
        
        # Time since last configuration change
        time_since_change = self.state.simulation_time - self.state.timestamp_last_config_change
        
        # Must exceed period minus hysteresis
        required_time = rotation_period_s - hysteresis_s
        
        return time_since_change >= required_time
    
    def _execute_configuration_change(self, target_config: str) -> tuple[bool, str]:
        """
        Execute configuration change.
        
        In simulation, we don't actually control physical equipment.
        We just update state and log the change.
        
        In real system, this would:
        1. Stop current line gradually
        2. Reconfigure dampers
        3. Start target line gradually
        """
        old_config = self.state.current_config
        
        if old_config == target_config:
            return False, f"Already in {target_config} configuration"
        
        LOGGER.info(
            f"🔄 RC: Configuration rotation starting: {old_config} → {target_config} "
            f"(sim_time={self.state.simulation_time:.1f}s, "
            f"scenario={self.state.current_scenario.name}, "
            f"time_in_primary={self._time_in_primary:.1f}s, "
            f"time_in_limited={self._time_in_limited:.1f}s)"
        )
        
        # Set lock to prevent RN from rotating during this change
        self.state.config_change_in_progress = True
        
        # Simulate configuration change (in real system this would take time)
        # For simulation, we just update state
        
        # Update state
        self.state.current_config = target_config
        self.state.timestamp_last_config_change = self.state.simulation_time
        
        # Increment rotation counter
        self._rotation_count += 1
        
        # Release lock
        self.state.config_change_in_progress = False
        
        balance = self.get_balance_ratio()
        balance_str = f"{balance:.2f}" if balance != float('inf') else "∞"
        LOGGER.info(
            f"✅ RC: Configuration rotation complete: now in {target_config} "
            f"(balance P/L={balance_str})"
        )
        
        return True, f"Configuration changed: {old_config} → {target_config}"
    
    def get_time_in_primary(self) -> float:
        """Get total time spent in Primary configuration."""
        return self._time_in_primary
    
    def get_time_in_limited(self) -> float:
        """Get total time spent in Limited configuration."""
        return self._time_in_limited
    
    def get_balance_ratio(self) -> float:
        """
        Get Primary/Limited time balance ratio.
        
        Returns:
            Ratio of Primary time to Limited time.
            Values close to 1.0 indicate good balance.
            Returns 0.0 if no time in Limited yet.
        """
        if self._time_in_limited == 0:
            return 0.0 if self._time_in_primary == 0 else float('inf')
        return self._time_in_primary / self._time_in_limited
    
    def get_rotation_count(self) -> int:
        """Get total number of configuration rotations performed."""
        return self._rotation_count
    
    def get_blocked_count(self) -> int:
        """Get total number of times rotation was blocked."""
        return self._blocked_count
    
    def get_blocked_by_reason(self) -> dict[str, int]:
        """Get detailed blocking statistics by reason."""
        return self._blocked_by_reason.copy()
    
    def get_time_to_next_rotation(self) -> float:
        """
        Get time remaining until next rotation is possible (seconds).
        
        Returns:
            Time in seconds, 0.0 if rotation is already possible, or -1.0 if not applicable.
        """
        # Check if rotation is possible in current scenario
        is_possible, _ = self._check_rotation_possible()
        if not is_possible:
            # Return -1 to indicate rotation is not applicable in this scenario
            return -1.0
        
        # Calculate time in current config
        time_in_current = self.state.simulation_time - self.state.timestamp_last_config_change
        
        # Rotation period in seconds
        rotation_period_s = self.config.rotation_period_hours * 3600
        
        # Time remaining
        time_remaining = rotation_period_s - time_in_current
        
        return max(0.0, time_remaining)

