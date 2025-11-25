"""Tests for Algorithm RC (configuration rotation)."""

import pytest

from algo.algorithm_rc import AlgorithmRC, RCConfig
from algo.state import AlgoState
from common.domain import Scenario


@pytest.fixture
def state():
    """Create fresh algo state for each test."""
    return AlgoState()


@pytest.fixture
def rc_config():
    """Create RC configuration with shorter periods for testing."""
    return RCConfig(
        rotation_period_hours=1,  # 1 hour for faster testing
        algorithm_loop_cycle_s=60,
        min_operating_time_s=600,  # 10 minutes
    )


@pytest.fixture
def algorithm_rc(rc_config, state):
    """Create Algorithm RC instance."""
    return AlgorithmRC(config=rc_config, state=state)


def test_rc_initialization(algorithm_rc):
    """Test that RC initializes correctly."""
    assert algorithm_rc.get_time_in_primary() == 0.0
    assert algorithm_rc.get_time_in_limited() == 0.0


def test_rotation_not_possible_in_s0(algorithm_rc, state):
    """Test that rotation is not possible in S0 (no heating)."""
    state.current_scenario = Scenario.S0
    state.mode = "AUTO"
    
    rotated, message = algorithm_rc.process()
    assert not rotated
    assert "not possible" in message.lower()


def test_rotation_not_possible_in_s5_s8(algorithm_rc, state):
    """Test that rotation is not possible in S5-S8 (both lines work)."""
    for scenario in [Scenario.S5, Scenario.S6, Scenario.S7, Scenario.S8]:
        state.current_scenario = scenario
        state.mode = "AUTO"
        state.simulation_time += 1.0
        
        rotated, message = algorithm_rc.process()
        assert not rotated


def test_rotation_possible_in_s1_s4(algorithm_rc, state):
    """Test that rotation is possible in S1-S4."""
    state.current_scenario = Scenario.S3
    state.mode = "AUTO"
    
    # Rotation should be theoretically possible (but period not elapsed yet)
    assert algorithm_rc._rotation_possible()


def test_rotation_blocked_by_manual_mode(algorithm_rc, state):
    """Test that rotation is blocked in MANUAL mode."""
    state.current_scenario = Scenario.S3
    state.mode = "MANUAL"
    
    assert not algorithm_rc._rotation_possible()


def test_rotation_period_not_elapsed(algorithm_rc, state):
    """Test that rotation doesn't occur if period not elapsed."""
    state.current_scenario = Scenario.S3
    state.mode = "AUTO"
    state.simulation_time = 1000.0
    state.timestamp_last_config_change = 500.0  # 500s ago, need 3600s
    
    rotated, message = algorithm_rc.process()
    assert not rotated
    assert "not elapsed" in message.lower()


def test_rotation_occurs_after_period(algorithm_rc, state):
    """Test that rotation occurs after period elapses."""
    state.current_scenario = Scenario.S3
    state.mode = "AUTO"
    state.current_config = "Primary"
    state.simulation_time = 4000.0  # 4000s
    state.timestamp_last_config_change = 0.0  # 4000s ago (> 1 hour = 3600s)
    
    rotated, message = algorithm_rc.process()
    assert rotated
    assert state.current_config == "Limited"


def test_rotation_alternates_configs(algorithm_rc, state):
    """Test that rotation alternates between Primary and Limited."""
    state.current_scenario = Scenario.S2
    state.mode = "AUTO"
    
    # Start in Primary
    state.current_config = "Primary"
    state.simulation_time = 4000.0
    state.timestamp_last_config_change = 0.0
    
    # First rotation: Primary → Limited
    rotated, _ = algorithm_rc.process()
    assert rotated
    assert state.current_config == "Limited"
    
    # Advance time for second rotation
    state.simulation_time = 8000.0
    state.timestamp_last_config_change = 4000.0
    
    # Second rotation: Limited → Primary
    rotated, _ = algorithm_rc.process()
    assert rotated
    assert state.current_config == "Primary"


def test_rotation_blocked_by_rn(algorithm_rc, state):
    """Test that RC rotation is blocked when RN is rotating."""
    state.current_scenario = Scenario.S3
    state.mode = "AUTO"
    state.simulation_time = 4000.0
    state.timestamp_last_config_change = 0.0
    state.heater_rotation_in_progress = True  # RN is rotating
    
    rotated, message = algorithm_rc.process()
    assert not rotated
    assert "RN" in message or "heater rotation" in message.lower()


def test_time_tracking_primary(algorithm_rc, state):
    """Test that time in Primary is tracked correctly."""
    state.current_config = "Primary"
    state.simulation_time = 0.0
    algorithm_rc.process()  # Initialize
    
    state.simulation_time = 100.0
    algorithm_rc.process()
    
    assert algorithm_rc.get_time_in_primary() == pytest.approx(100.0)
    assert algorithm_rc.get_time_in_limited() == 0.0


def test_time_tracking_limited(algorithm_rc, state):
    """Test that time in Limited is tracked correctly."""
    state.current_config = "Limited"
    state.simulation_time = 0.0
    algorithm_rc.process()  # Initialize
    
    state.simulation_time = 150.0
    algorithm_rc.process()
    
    assert algorithm_rc.get_time_in_limited() == pytest.approx(150.0)
    assert algorithm_rc.get_time_in_primary() == 0.0


def test_balance_ratio(algorithm_rc, state):
    """Test balance ratio calculation."""
    state.simulation_time = 0.0
    algorithm_rc.process()
    
    # Primary for 100s
    state.current_config = "Primary"
    state.simulation_time = 100.0
    algorithm_rc.process()
    
    # Limited for 100s
    state.current_config = "Limited"
    state.simulation_time = 200.0
    algorithm_rc.process()
    
    # Should be balanced (ratio = 1.0)
    assert algorithm_rc.get_balance_ratio() == pytest.approx(1.0)


def test_force_primary_in_s5(algorithm_rc, state):
    """Test that S5-S8 force Primary configuration."""
    state.current_scenario = Scenario.S5
    state.mode = "AUTO"
    state.current_config = "Limited"  # Wrong config for S5
    state.simulation_time = 0.0
    
    # Should force switch to Primary
    assert algorithm_rc._should_force_primary()
    
    rotated, message = algorithm_rc.process()
    assert rotated
    assert state.current_config == "Primary"

