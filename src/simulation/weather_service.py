"""Weather service entrypoint."""

from __future__ import annotations

import argparse
import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from flask import Flask, jsonify
from opentelemetry.metrics import CallbackOptions, Observation

from common.config import AppConfig, SimulationSettings, WeatherServiceConfig, load_config
from common.domain import WeatherSnapshot
from common.telemetry import TelemetryManager
from common.time_utils import AcceleratedClock, Clock
from weather.profile import SECONDS_PER_DAY, WinterProfileCalculator

LOGGER = logging.getLogger("weather-service")


@dataclass
class WeatherMetrics:
    meter_provider: TelemetryManager
    metrics_prefix: str
    default_dimensions: dict[str, str]

    def __post_init__(self) -> None:
        meter = self.meter_provider.meter("bogdanka.weather")
        self._temperature_value = 0.0
        self._day_value = 0.0
        self._temperature_gauge = meter.create_observable_gauge(
            f"{self.metrics_prefix}.external_temperature",
            callbacks=[self._observe_temperature],
        )
        self._day_gauge = meter.create_observable_gauge(
            f"{self.metrics_prefix}.simulation_day",
            callbacks=[self._observe_day],
        )
        self._requests_counter = meter.create_counter(f"{self.metrics_prefix}.requests_total")
        self._errors_counter = meter.create_counter(f"{self.metrics_prefix}.errors_total")

    def record_snapshot(self, snapshot: WeatherSnapshot) -> None:
        self._temperature_value = snapshot.temperature_c
        self._day_value = snapshot.simulation_day

    def record_request(self) -> None:
        self._requests_counter.add(1, attributes=self.default_dimensions)

    def record_error(self) -> None:
        self._errors_counter.add(1, attributes=self.default_dimensions)

    def _observe_temperature(self, options: CallbackOptions):
        yield Observation(self._temperature_value, self.default_dimensions)

    def _observe_day(self, options: CallbackOptions):
        yield Observation(self._day_value, self.default_dimensions)


class WeatherSimulator:
    """Maintains the weather state in the background."""

    def __init__(
        self,
        simulation: SimulationSettings,
        config: WeatherServiceConfig,
        metrics: WeatherMetrics,
        clock: Optional[Clock] = None,
        profile: Optional[WinterProfileCalculator] = None,
        poll_interval_sim_s: float = 60.0,
        enable_background: bool = True,
    ) -> None:
        self._simulation = simulation
        self._config = config
        self._metrics = metrics
        self._clock = clock or AcceleratedClock(simulation.acceleration)
        self._profile = profile or WinterProfileCalculator(
            config.winter_profile,
            simulation_days=simulation.duration_days,  # Pass duration from top-level config
        )
        self._poll_interval = poll_interval_sim_s
        self._latest = self._build_snapshot(0.0)
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        if enable_background:
            self.start()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def get_snapshot(self) -> WeatherSnapshot:
        with self._lock:
            snapshot = self._latest
        # Ensure we don't drift too far without recomputing.
        if self._clock.now() - snapshot.simulation_time >= self._poll_interval:
            snapshot = self.update_state()
        return snapshot

    def update_state(self) -> WeatherSnapshot:
        sim_time = min(self._clock.now(), self._simulation.duration_seconds)
        temperature = self._profile.temperature_at(sim_time)
        snapshot = WeatherSnapshot(
            simulation_time=sim_time,
            temperature_c=temperature,
            simulation_day=sim_time / SECONDS_PER_DAY,
            profile=self._profile.profile_metadata(),
        )
        with self._lock:
            self._latest = snapshot
        self._metrics.record_snapshot(snapshot)
        return snapshot

    def _run_loop(self) -> None:
        LOGGER.info("Weather simulator loop started (duration=%s seconds)", self._simulation.duration_seconds)
        while not self._stop_event.is_set():
            self.update_state()
            self._clock.sleep_sim_seconds(self._poll_interval)
        LOGGER.info("Weather simulator loop stopped")

    def _build_snapshot(self, sim_time: float) -> WeatherSnapshot:
        return WeatherSnapshot(
            simulation_time=sim_time,
            temperature_c=self._profile.temperature_at(sim_time),
            simulation_day=sim_time / SECONDS_PER_DAY,
            profile=self._profile.profile_metadata(),
        )


class WeatherApplication:
    """Flask application wrapper."""

    def __init__(
        self,
        app_config: AppConfig,
        *,
        clock: Optional[Clock] = None,
        enable_background: bool = True,
    ) -> None:
        self.config = app_config
        self.telemetry = TelemetryManager(app_config.telemetry)
        self.metrics = WeatherMetrics(
            self.telemetry,
            metrics_prefix=app_config.services.weather.metrics_prefix,
            default_dimensions=dict(app_config.telemetry.default_dimensions),
        )
        self.simulator = WeatherSimulator(
            simulation=app_config.simulation,
            config=app_config.services.weather,
            metrics=self.metrics,
            clock=clock,
            enable_background=enable_background,
        )
        self.app = Flask("bogdanka-weather")
        self._register_routes()

    def _register_routes(self) -> None:
        @self.app.route("/temperature", methods=["GET"])
        def temperature():
            try:
                snapshot = self.simulator.get_snapshot()
                self.metrics.record_request()
                return jsonify(snapshot.to_dict())
            except Exception as exc:  # pragma: no cover - defensive
                LOGGER.exception("temperature endpoint failed: %s", exc)
                self.metrics.record_error()
                return jsonify({"error": "internal_error"}), 500

    def shutdown(self) -> None:
        self.simulator.stop()
        self.telemetry.shutdown()


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def build_application(config_path: Path, *, enable_background: bool = True) -> WeatherApplication:
    app_config = load_config(config_path)
    configure_logging(app_config.telemetry.log_level)
    return WeatherApplication(app_config, enable_background=enable_background)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bogdanka Weather Service")
    default_config = Path(__file__).with_name("config.yaml")
    parser.add_argument("--config", type=Path, default=default_config, help="Path to config.yaml")
    parser.add_argument("--host", type=str, default=None, help="Override host from config")
    parser.add_argument("--port", type=int, default=None, help="Override port from config")
    args = parser.parse_args()

    application = build_application(args.config)
    weather_cfg = application.config.services.weather
    host = args.host or weather_cfg.host
    port = args.port or weather_cfg.port

    try:
        application.app.run(host=host, port=port)
    finally:
        application.shutdown()


if __name__ == "__main__":
    main()

