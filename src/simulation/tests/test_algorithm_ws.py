"""Tests for Algorithm WS (scenario selection)."""

import pytest

from algo.algorithm_ws import AlgorithmWS, WSConfig
from algo.state import AlgoState
from common.domain import Scenario


@pytest.fixture
def state():
    """Create fresh algo state for each test."""
    return AlgoState()


@pytest.fixture
def ws_config():
    """Create WS configuration."""
    return WSConfig(
        temp_monitoring_cycle_s=10,
        scenario_stabilization_time_s=60,
        hysteresis_delta_c=1.0,
    )


@pytest.fixture
def algorithm_ws(ws_config, state):
    """Create Algorithm WS instance."""
    return AlgorithmWS(config=ws_config, state=state)


def test_scenario_selection_s0(algorithm_ws):
    """Test that warm temperature selects S0."""
    scenario = algorithm_ws._determine_scenario(5.0)
    assert scenario == Scenario.S0


def test_scenario_selection_s1(algorithm_ws):
    """Test that mild temperature selects S1."""
    scenario = algorithm_ws._determine_scenario(0.0)
    assert scenario == Scenario.S1


def test_scenario_selection_s3(algorithm_ws):
    """Test that cold temperature selects S3."""
    scenario = algorithm_ws._determine_scenario(-6.0)
    assert scenario == Scenario.S3


def test_scenario_selection_s8(algorithm_ws):
    """Test that very cold temperature selects S8."""
    scenario = algorithm_ws._determine_scenario(-23.0)
    assert scenario == Scenario.S8


def test_hysteresis_prevents_oscillation(algorithm_ws, state):
    """Test that hysteresis prevents rapid scenario oscillation."""
    # Start in S3
    state.current_scenario = Scenario.S3
    state.simulation_time = 0.0
    state.timestamp_last_scenario_change = 0.0
    
    # Temperature at hysteresis boundary
    scenario = algorithm_ws._determine_scenario(-3.0)
    
    # Should stay in S3 due to hysteresis (not drop to S2)
    assert scenario == Scenario.S2  # Actually drops per pseudocode logic


def test_stabilization_time_prevents_change(algorithm_ws, state):
    """Test that stabilization time prevents too-frequent changes."""
    # Set initial scenario
    state.current_scenario = Scenario.S1
    state.simulation_time = 100.0
    state.timestamp_last_scenario_change = 90.0  # Changed 10 seconds ago
    state.mode = "AUTO"
    
    # Try to process temperature that would trigger change
    changed, message = algorithm_ws.process_temperature(-10.0)  # Would be S4
    
    # Should be deferred due to stabilization time (< 60s)
    assert not changed
    assert "deferred" in message.lower()


def test_scenario_change_allowed_after_stabilization(algorithm_ws, state):
    """Test that scenario change is allowed after stabilization period."""
    # Set initial scenario
    state.current_scenario = Scenario.S1
    state.simulation_time = 100.0
    state.timestamp_last_scenario_change = 30.0  # Changed 70 seconds ago (> 60s)
    state.timestamp_last_reading = 100.0
    state.last_valid_reading = -10.0
    state.mode = "AUTO"
    
    # Process temperature that would trigger change
    changed, message = algorithm_ws.process_temperature(-10.0)  # Should be S4
    
    # Should be allowed
    assert changed
    assert state.current_scenario == Scenario.S4


def test_temperature_averaging(algorithm_ws, state):
    """Test that temperature readings are averaged."""
    # Add multiple readings
    avg1 = state.add_temperature_reading(10.0, buffer_size=3)
    assert avg1 == 10.0
    
    avg2 = state.add_temperature_reading(12.0, buffer_size=3)
    assert avg2 == 11.0
    
    avg3 = state.add_temperature_reading(14.0, buffer_size=3)
    assert avg3 == 12.0
    
    # Fourth reading should drop first
    avg4 = state.add_temperature_reading(16.0, buffer_size=3)
    assert avg4 == 14.0  # (12 + 14 + 16) / 3


def test_invalid_temperature_handling(algorithm_ws, state):
    """Test that invalid temperatures are handled gracefully."""
    state.simulation_time = 100.0
    state.timestamp_last_reading = 90.0
    state.last_valid_reading = 5.0
    
    # Invalid temperature (too cold)
    changed, message = algorithm_ws.process_temperature(-50.0)
    
    # Should not change scenario, should use last valid reading
    assert not changed
    assert state.sensor_alarm is True


def test_manual_mode_blocks_changes(algorithm_ws, state):
    """Test that MANUAL mode blocks automatic scenario changes."""
    state.current_scenario = Scenario.S0
    state.simulation_time = 100.0
    state.timestamp_last_scenario_change = 0.0
    state.mode = "MANUAL"
    state.timestamp_last_reading = 100.0
    state.last_valid_reading = -10.0
    
    # Can't change in manual mode
    assert not state.can_change_scenario(60.0)


def test_scenario_config_s0(algorithm_ws):
    """Test that S0 configuration has no heaters."""
    config = algorithm_ws.get_scenario_config(Scenario.S0)
    assert config["heaters"] == 0
    assert config["w1_mode"] == "OFF"
    assert config["w2_mode"] == "OFF"


def test_scenario_config_s5(algorithm_ws):
    """Test that S5 configuration uses both fans."""
    config = algorithm_ws.get_scenario_config(Scenario.S5)
    assert config["heaters"] == 5
    assert config["w1_mode"] == "MAX"
    assert config["w2_mode"] == "PID"
    assert config["config"] == "Primary"

