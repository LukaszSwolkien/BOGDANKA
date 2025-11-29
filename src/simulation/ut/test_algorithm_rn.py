"""Tests for Algorithm RN (heater rotation)."""

import pytest

from algo.algorithm_rn import AlgorithmRN, HeaterState, RNConfig
from algo.state import AlgoState
from common.domain import Heater, Line, Scenario


@pytest.fixture
def state():
    """Create fresh algo state for each test."""
    return AlgoState()


@pytest.fixture
def rn_config():
    """Create RN configuration with shorter periods for testing."""
    return RNConfig(
        rotation_period_hours=1,  # 1 hour for testing
        rotation_duration_s=10,  # 10 seconds for testing
        min_delta_time_s=600,  # 10 minutes
        algorithm_loop_cycle_s=60,
    )


@pytest.fixture
def algorithm_rn(rn_config, state):
    """Create Algorithm RN instance."""
    return AlgorithmRN(config=rn_config, state=state)


def test_rn_initialization(algorithm_rn):
    """Test that RN initializes correctly."""
    # All heaters should start in IDLE state
    for heater in Heater:
        assert algorithm_rn.get_heater_operating_time(heater) == 0.0
        assert algorithm_rn.get_heater_idle_time(heater) == 0.0
        assert algorithm_rn.get_heater_state(heater) == HeaterState.IDLE


def test_heater_state_updates_in_s3_primary(algorithm_rn, state):
    """Test that heater states update correctly in S3 Primary."""
    state.current_scenario = Scenario.S3
    state.current_config = "Primary"
    state.simulation_time = 0.0
    
    algorithm_rn.process()  # Initialize
    
    # In S3 Primary: N1, N2, N3 should be active
    assert algorithm_rn.get_heater_state(Heater.N1) == HeaterState.ACTIVE
    assert algorithm_rn.get_heater_state(Heater.N2) == HeaterState.ACTIVE
    assert algorithm_rn.get_heater_state(Heater.N3) == HeaterState.ACTIVE
    assert algorithm_rn.get_heater_state(Heater.N4) == HeaterState.IDLE
    
    # Line 2 heaters should be idle
    assert algorithm_rn.get_heater_state(Heater.N5) == HeaterState.IDLE
    assert algorithm_rn.get_heater_state(Heater.N6) == HeaterState.IDLE


def test_heater_state_updates_in_s3_limited(algorithm_rn, state):
    """Test that heater states update correctly in S3 Limited."""
    state.current_scenario = Scenario.S3
    state.current_config = "Limited"
    state.simulation_time = 0.0
    
    algorithm_rn.process()  # Initialize
    
    # In S3 Limited: N5, N6, N7 should be active
    # Line 1 heaters should be idle
    assert algorithm_rn.get_heater_state(Heater.N1) == HeaterState.IDLE
    assert algorithm_rn.get_heater_state(Heater.N2) == HeaterState.IDLE
    
    assert algorithm_rn.get_heater_state(Heater.N5) == HeaterState.ACTIVE
    assert algorithm_rn.get_heater_state(Heater.N6) == HeaterState.ACTIVE
    assert algorithm_rn.get_heater_state(Heater.N7) == HeaterState.ACTIVE
    assert algorithm_rn.get_heater_state(Heater.N8) == HeaterState.IDLE


def test_operating_time_tracking(algorithm_rn, state):
    """Test that operating time is tracked correctly."""
    state.current_scenario = Scenario.S1
    state.current_config = "Primary"
    state.simulation_time = 0.0
    
    algorithm_rn.process()  # Initialize
    
    # Advance time
    state.simulation_time = 100.0
    algorithm_rn.process()
    
    # N1 should have 100s operating time
    assert algorithm_rn.get_heater_operating_time(Heater.N1) == pytest.approx(100.0)
    # N2-N4 should have 100s idle time (Line 1 but not active)
    assert algorithm_rn.get_heater_idle_time(Heater.N2) == pytest.approx(100.0)
    # N5-N8 should have 100s idle time (Line 2, not active in Primary)
    assert algorithm_rn.get_heater_idle_time(Heater.N5) == pytest.approx(100.0)


def test_line1_not_active_in_limited(algorithm_rn, state):
    """Test that Line C1 is not active in Limited config (S1-S4)."""
    state.current_scenario = Scenario.S3
    state.current_config = "Limited"
    
    assert not algorithm_rn._is_line_active(Line.C1)
    assert algorithm_rn._is_line_active(Line.C2)


def test_line2_not_active_in_primary(algorithm_rn, state):
    """Test that Line C2 is not active in Primary config (S1-S4)."""
    state.current_scenario = Scenario.S3
    state.current_config = "Primary"
    
    assert algorithm_rn._is_line_active(Line.C1)
    assert not algorithm_rn._is_line_active(Line.C2)


def test_line1_cannot_rotate_in_s5_s8(algorithm_rn, state):
    """Test that Line C1 cannot rotate in S5-S8 (all heaters needed)."""
    state.current_scenario = Scenario.S6
    
    # Line C1 has all 4 heaters active in S5-S8, no reserve
    assert not algorithm_rn._is_line_active(Line.C1)
    # Line C2 can still rotate (has reserve heaters)
    assert algorithm_rn._is_line_active(Line.C2)


def test_rotation_blocked_by_rc(algorithm_rn, state):
    """Test that rotation is blocked when RC is changing config."""
    state.current_scenario = Scenario.S3
    state.current_config = "Primary"
    state.config_change_in_progress = True
    state.config_rotation_end_time = 300.0  # RC rotation will complete at t=300s
    
    can_rotate, reason, reason_key = algorithm_rn._can_rotate(Line.C1)
    assert not can_rotate
    assert "RC" in reason or "config" in reason.lower()
    assert reason_key == "rc_rotation_in_progress"


def test_rotation_blocked_too_soon_after_rc_change(algorithm_rn, state):
    """Test that rotation is blocked too soon after RC config change."""
    state.current_scenario = Scenario.S3
    state.current_config = "Primary"
    state.simulation_time = 2000.0
    state.timestamp_last_config_change = 1000.0  # 1000s ago, need 3600s
    
    can_rotate, reason, reason_key = algorithm_rn._can_rotate(Line.C1)
    assert not can_rotate
    assert "config change" in reason.lower()
    assert reason_key == "too_soon_after_rc"


def test_rotation_requires_reserve_heater(algorithm_rn, state):
    """Test that rotation requires a reserve heater."""
    state.current_scenario = Scenario.S4
    state.current_config = "Primary"
    state.simulation_time = 4000.0
    
    # S4 Primary uses all 4 heaters in Line C1 (N1-N4), no reserve
    can_rotate, reason, reason_key = algorithm_rn._can_rotate(Line.C1)
    assert not can_rotate
    assert "reserve" in reason.lower()
    assert reason_key == "no_suitable_heaters"


def test_rotation_period_not_elapsed(algorithm_rn, state):
    """Test that rotation doesn't occur if period not elapsed."""
    state.current_scenario = Scenario.S3
    state.current_config = "Primary"
    state.simulation_time = 4000.0  # Long enough after config change
    state.timestamp_last_config_change = 0.0  # 4000s ago > 3600s
    
    # But rotation period for line not elapsed
    algorithm_rn._last_rotation_per_line[Line.C1] = 3000.0  # 1000s ago, need 1800s
    algorithm_rn._last_rotation_global = 0.0  # Long ago
    
    can_rotate, reason, reason_key = algorithm_rn._can_rotate(Line.C1)
    assert not can_rotate
    assert "period not elapsed" in reason.lower()
    assert reason_key == "period_not_elapsed"


def test_heater_selection_for_rotation(algorithm_rn, state):
    """Test heater selection logic."""
    state.current_scenario = Scenario.S3
    state.current_config = "Primary"
    state.simulation_time = 0.0
    
    algorithm_rn.process()  # Initialize (N1, N2, N3 active)
    
    # Simulate N1 operating longer than others
    algorithm_rn._heater_tracking[Heater.N1].operating_time_s = 2000.0
    algorithm_rn._heater_tracking[Heater.N2].operating_time_s = 1500.0
    algorithm_rn._heater_tracking[Heater.N3].operating_time_s = 1500.0
    algorithm_rn._heater_tracking[Heater.N4].operating_time_s = 0.0  # Idle heater, no operating time
    
    heater_off, heater_on, delta = algorithm_rn._select_heaters_for_rotation(Line.C1)
    
    assert heater_off == Heater.N1  # Longest operating
    assert heater_on == Heater.N4   # Shortest operating time (among idle heaters)
    assert delta == pytest.approx(2000.0 - 0.0)  # max_operating - min_operating


def test_rotation_requires_min_delta_time(algorithm_rn, state):
    """Test that rotation requires minimum time difference."""
    state.current_scenario = Scenario.S3
    state.current_config = "Primary"
    state.simulation_time = 2000.0  # Enough time for rotation period
    
    algorithm_rn.process()  # Initialize
    
    # Set all heaters to similar times (delta < min_delta_time_s)
    for heater in [Heater.N1, Heater.N2, Heater.N3]:
        algorithm_rn._heater_tracking[heater].operating_time_s = 500.0
    algorithm_rn._heater_tracking[Heater.N4].operating_time_s = 0.0  # delta = 500s (500 - 0)
    
    algorithm_rn._last_rotation_per_line[Line.C1] = 0.0
    algorithm_rn._last_rotation_global = 0.0
    state.timestamp_last_config_change = 0.0
    
    rotated, message = algorithm_rn.process()
    assert not rotated  # Delta is 500s, need 600s


def test_full_rotation_flow(algorithm_rn, state):
    """Test a full rotation flow in S3 Primary."""
    state.current_scenario = Scenario.S3
    state.current_config = "Primary"
    state.mode = "AUTO"
    state.simulation_time = 7200.0  # Start at a time long after config change
    state.timestamp_last_config_change = 0.0  # 2 hours ago
    
    algorithm_rn.process()  # Initialize (N1, N2, N3 active)
    
    # Set heater times AFTER initialization to avoid them being overwritten
    algorithm_rn._heater_tracking[Heater.N1].operating_time_s = 3000.0
    algorithm_rn._heater_tracking[Heater.N1].first_activation_timestamp = 0.0
    algorithm_rn._heater_tracking[Heater.N2].operating_time_s = 1000.0
    algorithm_rn._heater_tracking[Heater.N3].operating_time_s = 1000.0
    algorithm_rn._heater_tracking[Heater.N4].operating_time_s = 0.0  # Idle heater, no operating time
    
    # Set timestamps to allow rotation
    algorithm_rn._last_rotation_per_line[Line.C1] = 0.0  # Last rotated long ago
    algorithm_rn._last_rotation_global = 0.0  # No recent global rotation
    
    # Execute rotation
    rotated, message = algorithm_rn.process()
    
    assert rotated, f"Expected rotation but got: {message}"
    assert "N1" in message and "N4" in message
    assert algorithm_rn.get_heater_state(Heater.N1) == HeaterState.IDLE
    assert algorithm_rn.get_heater_state(Heater.N4) == HeaterState.ACTIVE


def test_15min_global_spacing(algorithm_rn, state):
    """Test that rotations are spaced by at least 15 minutes globally."""
    state.current_scenario = Scenario.S6  # Both lines active
    state.simulation_time = 5000.0
    algorithm_rn._last_rotation_global = 4500.0  # 500s ago (< 900s)
    
    can_rotate, reason, reason_key = algorithm_rn._can_rotate(Line.C2)
    assert not can_rotate
    assert "last rotation" in reason.lower()
    assert reason_key == "global_spacing_not_met"

