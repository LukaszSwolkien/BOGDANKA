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


@dataclass
class ConstantProfileCalculator:
    """
    Generates constant temperature for controlled algorithm testing.
    
    This profile is useful for:
    - Verifying rotation algorithms work correctly in stable conditions
    - Testing specific scenarios without temperature variations
    - Debugging algorithm behavior
    """

    temperature_c: float
    simulation_days: int  # Not used, but kept for API consistency

    def temperature_at(self, simulation_seconds: float) -> float:
        """Return constant temperature regardless of time."""
        return self.temperature_c

    def profile_metadata(self) -> dict[str, float]:
        return {
            "constant_temp": self.temperature_c,
        }


@dataclass
class SteppedProfileCalculator:
    """
    Generates temperature profile with controlled step changes.
    
    This profile is useful for:
    - Testing scenario transitions (S1→S3→S6→S3)
    - Verifying algorithm behavior during step changes
    - Simulating specific real-world sequences
    
    Steps are defined as list of dicts with:
    - day_start: Start day (inclusive)
    - day_end: End day (exclusive)
    - temperature_c: Temperature for this period
    
    Example:
        steps = [
            {"day_start": 0, "day_end": 5, "temperature_c": 0.0},    # S1 for days 0-5
            {"day_start": 5, "day_end": 10, "temperature_c": -5.0},  # S3 for days 5-10
            {"day_start": 10, "day_end": 15, "temperature_c": -16.0}, # S6 for days 10-15
            {"day_start": 15, "day_end": 20, "temperature_c": -5.0},  # S3 for days 15-20
        ]
    """

    steps: list[dict[str, float]]
    simulation_days: int
    
    def __post_init__(self) -> None:
        """Validate steps configuration."""
        if not self.steps:
            raise ValueError("SteppedProfile requires at least one step")
        
        # Sort steps by day_start
        self.steps = sorted(self.steps, key=lambda s: s["day_start"])
        
        # Validate steps
        for i, step in enumerate(self.steps):
            if "day_start" not in step or "day_end" not in step or "temperature_c" not in step:
                raise ValueError(f"Step {i} missing required fields (day_start, day_end, temperature_c)")
            
            if step["day_start"] >= step["day_end"]:
                raise ValueError(f"Step {i}: day_start must be < day_end")
            
            # Check for gaps/overlaps
            if i > 0:
                prev_end = self.steps[i-1]["day_end"]
                curr_start = step["day_start"]
                if curr_start != prev_end:
                    raise ValueError(
                        f"Gap/overlap between step {i-1} and {i}: "
                        f"prev ends at {prev_end}, current starts at {curr_start}"
                    )
    
    def temperature_at(self, simulation_seconds: float) -> float:
        """Return temperature for current simulation time based on step."""
        day = simulation_seconds / SECONDS_PER_DAY
        
        # Find matching step
        for step in self.steps:
            if step["day_start"] <= day < step["day_end"]:
                return step["temperature_c"]
        
        # If beyond last step, return last temperature
        if day >= self.steps[-1]["day_end"]:
            return self.steps[-1]["temperature_c"]
        
        # If before first step, return first temperature
        return self.steps[0]["temperature_c"]
    
    def profile_metadata(self) -> dict[str, any]:
        return {
            "type": "stepped",
            "num_steps": len(self.steps),
            "steps": self.steps,
        }

