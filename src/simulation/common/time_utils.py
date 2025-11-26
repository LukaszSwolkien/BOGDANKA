"""Time utilities for accelerated simulations."""

from __future__ import annotations

import time
from typing import Protocol


class Clock(Protocol):
    def now(self) -> float:
        """Return current simulation time in seconds."""

    def sleep_sim_seconds(self, sim_seconds: float) -> None:
        """Sleep for the given number of simulation seconds."""


class AcceleratedClock:
    """Maps real time to accelerated simulation time."""

    def __init__(self, acceleration: float = 1.0) -> None:
        if acceleration <= 0:
            raise ValueError("Acceleration must be positive")
        self._acceleration = acceleration
        self._start_real = time.time()
        self._start_sim = 0.0

    @property
    def acceleration(self) -> float:
        return self._acceleration

    def now(self) -> float:
        elapsed_real = time.time() - self._start_real
        return self._start_sim + elapsed_real * self._acceleration

    def sleep_sim_seconds(self, sim_seconds: float) -> None:
        if sim_seconds <= 0:
            return
        time.sleep(sim_seconds / self._acceleration)

    def reset(self) -> None:
        self._start_real = time.time()
        self._start_sim = 0.0


