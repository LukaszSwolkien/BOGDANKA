"""Winter temperature profile generator."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Optional

from common.config import WinterProfileConfig


SECONDS_PER_DAY = 24 * 3600


@dataclass
class WinterProfileCalculator:
    """Generates realistic winter temperatures for the simulation."""

    config: WinterProfileConfig
    simulation_days: int  # Total simulation duration (from top-level config)
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def temperature_at(self, simulation_seconds: float) -> float:
        day = min(simulation_seconds / SECONDS_PER_DAY, self.simulation_days)
        trend = self._trend_temperature(day)
        daily_cycle = self._daily_variation(day)
        noise = self._rng.gauss(0, self.config.noise_sigma_c)
        return trend + daily_cycle + noise

    def _trend_temperature(self, day: float) -> float:
        if day <= 0:
            return self.config.initial_temp_c

        if day <= self.config.cooling_days:
            progress = day / max(self.config.cooling_days, 1)
            return self.config.initial_temp_c - (
                (self.config.initial_temp_c - self.config.min_temp_c) * progress
            )

        warming_start = self.config.cooling_days
        if day <= warming_start + self.config.warming_days:
            progress = (day - warming_start) / max(self.config.warming_days, 1)
            return self.config.min_temp_c + (
                (self.config.final_temp_c - self.config.min_temp_c) * progress
            )

        return self.config.final_temp_c

    def _daily_variation(self, day: float) -> float:
        fractional_day = day - math.floor(day)
        angle = fractional_day * 2 * math.pi
        return self.config.daily_variation_c * math.sin(angle)

    def profile_metadata(self) -> dict[str, float]:
        return {
            "initial_temp": self.config.initial_temp_c,
            "min_temp": self.config.min_temp_c,
            "final_temp": self.config.final_temp_c,
        }

