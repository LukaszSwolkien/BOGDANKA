from dataclasses import replace

import pytest

from common.config import AppConfig, SimulationSettings, load_config
from common.time_utils import Clock
from weather_service import WeatherApplication


class FakeClock(Clock):
    def __init__(self) -> None:
        self._now = 0.0

    def now(self) -> float:
        return self._now

    def sleep_sim_seconds(self, sim_seconds: float) -> None:
        self._now += sim_seconds

    def set_time(self, seconds: float) -> None:
        self._now = seconds


@pytest.fixture()
def app_config(tmp_path) -> AppConfig:
    config = load_config("config.yaml")
    config.simulation = SimulationSettings(acceleration=1000.0, duration_days=1)
    config.telemetry.exporter_type = "console"
    return config


def test_temperature_endpoint_returns_snapshot(app_config):
    clock = FakeClock()
    clock.set_time(12 * 3600)  # noon
    application = WeatherApplication(app_config, clock=clock, enable_background=False)

    # Force single snapshot update manually
    application.simulator.update_state()
    client = application.app.test_client()

    response = client.get("/temperature")
    assert response.status_code == 200
    payload = response.get_json()
    assert {"timestamp", "t_zewn", "simulation_time", "simulation_day", "profile"} <= payload.keys()
    assert payload["simulation_time"] == pytest.approx(12 * 3600, rel=1e-3)
    application.shutdown()

