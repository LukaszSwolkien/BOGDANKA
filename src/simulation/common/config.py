"""Configuration loader for simulation services."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping

import yaml


class ConfigError(RuntimeError):
    """Raised when the configuration file is invalid or missing required fields."""


@dataclass
class SimulationSettings:
    acceleration: float = 1000.0
    duration_days: int = 90

    @property
    def duration_seconds(self) -> float:
        return float(self.duration_days) * 24 * 3600


@dataclass
class TelemetryConfig:
    exporter_type: str
    endpoints: Mapping[str, str]
    headers: Mapping[str, str]
    resource_attributes: Mapping[str, str]
    default_dimensions: Mapping[str, str]
    log_level: str = "INFO"
    log_output: str = "console"  # "console", "file", or "both"
    log_file: str = "logs/algo_service.log"


@dataclass
class WSConfig:
    temp_monitoring_cycle_s: int
    scenario_stabilization_time_s: int
    hysteresis_delta_c: float


@dataclass
class RCConfig:
    rotation_period_hours: int
    rotation_duration_s: int
    algorithm_loop_cycle_s: int
    min_operating_time_s: int


@dataclass
class RNConfig:
    """RN algorithm configuration."""
    rotation_period_hours: int      # [h] rotation period (same for all scenarios)
    rotation_duration_s: int        # [s] time for heater rotation to complete
    min_delta_time_s: int          # [s] minimum time difference for rotation
    algorithm_loop_cycle_s: int    # [s] RN check frequency


@dataclass
class DisplayConfig:
    enabled: bool = True
    refresh_rate_s: float = 1.0


@dataclass
class AlgoAlgorithmsConfig:
    ws: WSConfig
    rc: RCConfig
    rn: RNConfig


@dataclass
class AlgoServiceConfig:
    service_name: str
    metrics_prefix: str
    weather_endpoint: str
    otlp_timeout_ms: int
    display: DisplayConfig
    algorithms: AlgoAlgorithmsConfig


@dataclass
class WinterProfileConfig:
    initial_temp_c: float
    min_temp_c: float
    final_temp_c: float
    cooling_days: int
    warming_days: int
    daily_variation_c: float
    noise_sigma_c: float


@dataclass
class ConstantProfileConfig:
    temperature_c: float


@dataclass
class SteppedProfileConfig:
    steps: list[dict[str, float]]


@dataclass
class WeatherServiceConfig:
    host: str
    port: int
    service_name: str
    metrics_prefix: str
    profile_type: str  # "winter", "constant", or "stepped"
    winter_profile: WinterProfileConfig
    constant_profile: ConstantProfileConfig | None = None
    stepped_profile: SteppedProfileConfig | None = None


@dataclass
class ServicesConfig:
    algo: AlgoServiceConfig
    weather: WeatherServiceConfig


@dataclass
class AppConfig:
    simulation: SimulationSettings
    telemetry: TelemetryConfig
    services: ServicesConfig


def load_config(path: str | Path) -> AppConfig:
    """Load and validate configuration from YAML."""
    path = Path(path)
    if not path.exists():
        raise ConfigError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data: MutableMapping[str, Any] = yaml.safe_load(handle) or {}

    simulation_section = data.get("simulation", {})
    simulation = SimulationSettings(
        acceleration=float(simulation_section.get("acceleration", 1000.0)),
        duration_days=int(simulation_section.get("duration_days", 90)),
    )

    telemetry_data = data.get("telemetry", {})
    telemetry = TelemetryConfig(
        exporter_type=str(telemetry_data.get("exporter_type", "otlp")),
        endpoints=_require_mapping(telemetry_data, "endpoints"),
        headers=_require_mapping(telemetry_data, "headers"),
        resource_attributes=_require_mapping(telemetry_data, "resource_attributes"),
        default_dimensions=_require_mapping(telemetry_data, "default_dimensions"),
        log_level=str(telemetry_data.get("log_level", "INFO")),
        log_output=str(telemetry_data.get("log_output", "console")),
        log_file=str(telemetry_data.get("log_file", "logs/algo_service.log")),
    )

    services_data = data.get("services", {})
    algo = _load_algo_service(services_data.get("algo", {}))
    weather = _load_weather_service(services_data.get("weather", {}))

    services = ServicesConfig(algo=algo, weather=weather)
    return AppConfig(simulation=simulation, telemetry=telemetry, services=services)


def _load_algo_service(data: Mapping[str, Any]) -> AlgoServiceConfig:
    algorithms = data.get("algorithms", {})
    display_data = data.get("display", {})

    ws = algorithms.get("ws", {})
    rc = algorithms.get("rc", {})
    rn = algorithms.get("rn", {})

    return AlgoServiceConfig(
        service_name=str(data.get("service_name", "bogdanka-algo")),
        metrics_prefix=str(data.get("metrics_prefix", "bogdanka.algo")),
        weather_endpoint=str(data.get("weather_endpoint", "http://localhost:8080/temperature")),
        otlp_timeout_ms=int(data.get("otlp_timeout_ms", 1000)),
        display=DisplayConfig(
            enabled=bool(display_data.get("enabled", True)),
            refresh_rate_s=float(display_data.get("refresh_rate_s", 1.0)),
        ),
        algorithms=AlgoAlgorithmsConfig(
            ws=WSConfig(
                temp_monitoring_cycle_s=int(ws.get("temp_monitoring_cycle_s", 10)),
                scenario_stabilization_time_s=int(ws.get("scenario_stabilization_time_s", 60)),
                hysteresis_delta_c=float(ws.get("hysteresis_delta_c", 1.0)),
            ),
            rc=RCConfig(
                rotation_period_hours=int(rc.get("rotation_period_hours", 168)),
                rotation_duration_s=int(rc.get("rotation_duration_s", 300)),
                algorithm_loop_cycle_s=int(rc.get("algorithm_loop_cycle_s", 60)),
                min_operating_time_s=int(rc.get("min_operating_time_s", 3600)),
            ),
            rn=RNConfig(
                rotation_period_hours=int(rn.get("rotation_period_hours", 24)),
                rotation_duration_s=int(rn.get("rotation_duration_s", 180)),
                min_delta_time_s=int(rn.get("min_delta_time_s", 3600)),
                algorithm_loop_cycle_s=int(rn.get("algorithm_loop_cycle_s", 60)),
            ),
        ),
    )


def _load_weather_service(data: Mapping[str, Any]) -> WeatherServiceConfig:
    winter_profile = data.get("winter_profile", {})
    constant_profile_data = data.get("constant_profile", {})
    stepped_profile_data = data.get("stepped_profile", {})
    
    # Parse constant profile if present
    constant_profile = None
    if constant_profile_data:
        constant_profile = ConstantProfileConfig(
            temperature_c=float(constant_profile_data.get("temperature_c", -5.0)),
        )
    
    # Parse stepped profile if present
    stepped_profile = None
    if stepped_profile_data and "steps" in stepped_profile_data:
        stepped_profile = SteppedProfileConfig(
            steps=list(stepped_profile_data["steps"]),
        )
    
    return WeatherServiceConfig(
        host=str(data.get("host", "localhost")),
        port=int(data.get("port", 8080)),
        service_name=str(data.get("service_name", "bogdanka-weather")),
        metrics_prefix=str(data.get("metrics_prefix", "bogdanka.weather")),
        profile_type=str(data.get("profile_type", "winter")),
        winter_profile=WinterProfileConfig(
            initial_temp_c=float(winter_profile.get("initial_temp_c", 5.0)),
            min_temp_c=float(winter_profile.get("min_temp_c", -25.0)),
            final_temp_c=float(winter_profile.get("final_temp_c", 3.0)),
            cooling_days=int(winter_profile.get("cooling_days", 15)),
            warming_days=int(winter_profile.get("warming_days", 15)),
            daily_variation_c=float(winter_profile.get("daily_variation_c", 3.0)),
            noise_sigma_c=float(winter_profile.get("noise_sigma_c", 0.5)),
        ),
        constant_profile=constant_profile,
        stepped_profile=stepped_profile,
    )


def _require_mapping(data: Mapping[str, Any], field: str) -> Dict[str, str]:
    value = data.get(field, {})
    if not isinstance(value, Mapping):
        raise ConfigError(f"Expected mapping for telemetry.{field}")
    return {str(key): str(val) for key, val in value.items()}

