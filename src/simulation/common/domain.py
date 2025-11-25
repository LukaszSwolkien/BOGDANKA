"""Domain models shared across simulation services."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict


class Scenario(enum.Enum):
    S0 = 0
    S1 = 1
    S2 = 2
    S3 = 3
    S4 = 4
    S5 = 5
    S6 = 6
    S7 = 7
    S8 = 8


class Line(enum.Enum):
    C1 = "C1"
    C2 = "C2"


class Heater(enum.Enum):
    N1 = "N1"
    N2 = "N2"
    N3 = "N3"
    N4 = "N4"
    N5 = "N5"
    N6 = "N6"
    N7 = "N7"
    N8 = "N8"


@dataclass(slots=True)
class WeatherSnapshot:
    """Serializable snapshot returned by the weather API."""

    simulation_time: float
    temperature_c: float
    simulation_day: float
    profile: Dict[str, float]
    timestamp: str = field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, float | str | Dict[str, float]]:
        return {
            "timestamp": self.timestamp,
            "t_zewn": round(self.temperature_c, 3),
            "simulation_time": round(self.simulation_time, 3),
            "simulation_day": round(self.simulation_day, 3),
            "profile": self.profile,
        }

