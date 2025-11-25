"""Tests for domain models."""

from common.domain import Heater, Line, Scenario, WeatherSnapshot


def test_scenario_enum():
    """Test that Scenario enum contains all scenarios S0-S8."""
    assert Scenario.S0.value == 0
    assert Scenario.S1.value == 1
    assert Scenario.S2.value == 2
    assert Scenario.S3.value == 3
    assert Scenario.S4.value == 4
    assert Scenario.S5.value == 5
    assert Scenario.S6.value == 6
    assert Scenario.S7.value == 7
    assert Scenario.S8.value == 8
    
    # Verify all 9 scenarios exist
    assert len(Scenario) == 9


def test_line_enum():
    """Test that Line enum contains C1 and C2."""
    assert Line.C1.value == "C1"
    assert Line.C2.value == "C2"
    assert len(Line) == 2


def test_heater_enum():
    """Test that Heater enum contains N1-N8."""
    assert Heater.N1.value == "N1"
    assert Heater.N2.value == "N2"
    assert Heater.N3.value == "N3"
    assert Heater.N4.value == "N4"
    assert Heater.N5.value == "N5"
    assert Heater.N6.value == "N6"
    assert Heater.N7.value == "N7"
    assert Heater.N8.value == "N8"
    
    # Verify all 8 heaters exist
    assert len(Heater) == 8


def test_weather_snapshot_creation():
    """Test WeatherSnapshot creation and serialization."""
    snapshot = WeatherSnapshot(
        simulation_time=86400.0,
        temperature_c=-12.4,
        simulation_day=1.0,
        profile={"initial_temp": 5.0, "min_temp": -25.0, "final_temp": 3.0},
    )
    
    assert snapshot.simulation_time == 86400.0
    assert snapshot.temperature_c == -12.4
    assert snapshot.simulation_day == 1.0
    assert snapshot.profile["min_temp"] == -25.0


def test_weather_snapshot_to_dict():
    """Test WeatherSnapshot serialization to dictionary."""
    snapshot = WeatherSnapshot(
        simulation_time=86400.5,
        temperature_c=-12.456,
        simulation_day=1.001,
        profile={"initial_temp": 5.0, "min_temp": -25.0, "final_temp": 3.0},
    )
    
    data = snapshot.to_dict()
    
    assert "timestamp" in data
    assert "t_zewn" in data
    assert "simulation_time" in data
    assert "simulation_day" in data
    assert "profile" in data
    
    # Check rounding
    assert data["t_zewn"] == -12.456
    assert data["simulation_time"] == 86400.5
    assert data["simulation_day"] == 1.001
    
    # Timestamp should be ISO format
    assert "T" in data["timestamp"]
    assert "Z" in data["timestamp"] or "+" in data["timestamp"]

