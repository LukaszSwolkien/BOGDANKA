"""Telemetry helper for configuring OpenTelemetry metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import Meter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource

from .config import TelemetryConfig


@dataclass
class TelemetryManager:
    """Initializes the OpenTelemetry meter provider based on configuration."""

    config: TelemetryConfig
    reader_interval_s: float = 10.0
    _meter_provider: Optional[MeterProvider] = None

    def __post_init__(self) -> None:
        resource = Resource.create(attributes=dict(self.config.resource_attributes))
        exporter = self._build_exporter()
        reader = PeriodicExportingMetricReader(
            exporter=exporter, export_interval_millis=int(self.reader_interval_s * 1000)
        )
        self._meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(self._meter_provider)

    def _build_exporter(self):
        exporter_type = self.config.exporter_type.lower()
        if exporter_type == "otlp":
            return OTLPMetricExporter(
                endpoint=self.config.endpoints.get("metrics"),
                headers=dict(self.config.headers),
            )
        if exporter_type == "console":
            return ConsoleMetricExporter()
        raise ValueError(f"Unsupported telemetry exporter_type: {self.config.exporter_type}")

    def meter(self, instrumentation_name: str) -> Meter:
        if not self._meter_provider:
            raise RuntimeError("TelemetryManager not initialized")
        return self._meter_provider.get_meter(instrumentation_name)

    def shutdown(self) -> None:
        if self._meter_provider:
            self._meter_provider.shutdown()


