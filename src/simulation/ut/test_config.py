"""Tests for configuration loading and validation."""

import tempfile
from pathlib import Path

import pytest
import yaml

from common.config import (
    AppConfig,
    ConfigError,
    SimulationSettings,
    TelemetryConfig,
    load_config,
)


def test_load_config_from_existing_file(tmp_path):
    """Test loading configuration from a valid YAML file."""
    config_file = tmp_path / "test_config.yaml"
    config_data = {
        "simulation": {"acceleration": 1000, "duration_days": 90},
        "telemetry": {
            "exporter_type": "console",
            "endpoints": {"metrics": "http://localhost:4318/v1/metrics"},
            "headers": {"X-Test": "value"},
            "resource_attributes": {"service.name": "test"},
            "default_dimensions": {"site": "test"},
            "log_level": "DEBUG",
        },
        "services": {
            "algo": {
                "service_name": "test-algo",
                "metrics_prefix": "test.algo",
                "weather_endpoint": "http://localhost:8080/temperature",
                "otlp_timeout_ms": 1000,
                "algorithms": {
                    "ws": {
                        "temp_monitoring_cycle_s": 10,
                        "scenario_stabilization_time_s": 60,
                        "hysteresis_delta_c": 1.0,
                    },
                    "rc": {
                        "rotation_period_hours": 168,
                        "algorithm_loop_cycle_s": 60,
                        "min_operating_time_s": 3600,
                    },
                    "rn": {
                        "rotation_period_hours": 168,
                        "min_time_delta_s": 3600,
                        "gap_after_rc_s": 3600,
                        "global_gap_between_rotations_s": 900,
                    },
                },
            },
            "weather": {
                "host": "localhost",
                "port": 8080,
                "service_name": "test-weather",
                "metrics_prefix": "test.weather",
                "winter_profile": {
                    "simulation_days": 90,
                    "initial_temp_c": 5.0,
                    "min_temp_c": -25.0,
                    "final_temp_c": 3.0,
                    "cooling_days": 15,
                    "warming_days": 15,
                    "daily_variation_c": 3.0,
                    "noise_sigma_c": 0.5,
                },
            },
        },
    }
    
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)
    
    config = load_config(config_file)
    
    assert isinstance(config, AppConfig)
    assert config.simulation.acceleration == 1000
    assert config.simulation.duration_days == 90
    assert config.simulation.duration_seconds == 90 * 24 * 3600
    assert config.telemetry.exporter_type == "console"
    assert config.telemetry.log_level == "DEBUG"
    assert config.services.weather.port == 8080
    assert config.services.algo.algorithms.ws.temp_monitoring_cycle_s == 10


def test_load_config_missing_file():
    """Test that loading a non-existent config file raises ConfigError."""
    with pytest.raises(ConfigError, match="not found"):
        load_config("nonexistent.yaml")


def test_simulation_settings_duration_calculation():
    """Test that duration in seconds is calculated correctly."""
    settings = SimulationSettings(duration_days=30)
    assert settings.duration_seconds == 30 * 24 * 3600


def test_config_with_defaults(tmp_path):
    """Test that defaults are applied when optional fields are missing."""
    config_file = tmp_path / "minimal_config.yaml"
    minimal_data = {
        "simulation": {},
        "telemetry": {
            "endpoints": {"metrics": "http://localhost:4318"},
            "headers": {},
            "resource_attributes": {},
            "default_dimensions": {},
        },
        "services": {"algo": {}, "weather": {}},
    }
    
    with open(config_file, "w") as f:
        yaml.dump(minimal_data, f)
    
    config = load_config(config_file)
    
    # Verify defaults are applied
    assert config.simulation.acceleration == 1000.0
    assert config.simulation.duration_days == 90
    assert config.telemetry.exporter_type == "otlp"
    assert config.services.weather.port == 8080
    assert config.services.algo.algorithms.ws.temp_monitoring_cycle_s == 10

