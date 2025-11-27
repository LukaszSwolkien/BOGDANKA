"""HTTP client for polling weather service."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from common.domain import WeatherSnapshot

LOGGER = logging.getLogger("algo-service.weather-client")


@dataclass
class WeatherClient:
    """HTTP client to poll weather service for temperature and simulation time."""
    
    endpoint_url: str
    timeout_seconds: float = 5.0
    max_retries: int = 3
    backoff_factor: float = 0.5
    
    def __post_init__(self) -> None:
        self._session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def poll(self) -> Optional[WeatherSnapshot]:
        """
        Poll weather service for current temperature and simulation time.
        
        Returns:
            WeatherSnapshot with simulation_time (authoritative), temperature, etc.
            None if connection fails after retries.
        """
        try:
            response = self._session.get(self.endpoint_url, timeout=self.timeout_seconds)
            response.raise_for_status()
            data = response.json()
            
            # Parse response into WeatherSnapshot
            snapshot = WeatherSnapshot(
                simulation_time=data["simulation_time"],  # ← Authoritative time from weather service
                temperature_c=data["t_zewn"],
                simulation_day=data["simulation_day"],
                profile=data["profile"],
                timestamp=data.get("timestamp", ""),
            )
            
            LOGGER.debug(
                f"Weather polled: t={snapshot.simulation_time:.1f}s, "
                f"T_zewn={snapshot.temperature_c:.1f}°C, day={snapshot.simulation_day:.2f}"
            )
            
            return snapshot
            
        except requests.exceptions.RequestException as exc:
            LOGGER.error(f"Failed to poll weather service: {exc}")
            return None
    
    def wait_for_service(self, max_wait_seconds: float = 30.0) -> bool:
        """
        Wait for weather service to become available.
        
        Args:
            max_wait_seconds: Maximum time to wait for service
            
        Returns:
            True if service is available, False if timeout
        """
        start_time = time.time()
        retry_count = 0
        
        while (time.time() - start_time) < max_wait_seconds:
            try:
                response = self._session.get(self.endpoint_url, timeout=2.0)
                response.raise_for_status()
                LOGGER.info(f"Weather service is available at {self.endpoint_url}")
                return True
            except requests.exceptions.RequestException:
                retry_count += 1
                wait_time = min(self.backoff_factor * (2 ** retry_count), 5.0)
                LOGGER.info(
                    f"Weather service not ready, retrying in {wait_time:.1f}s "
                    f"({retry_count} attempts)"
                )
                time.sleep(wait_time)
        
        LOGGER.error(f"Weather service did not become available after {max_wait_seconds}s")
        return False

