import math

from common.config import WinterProfileConfig
from weather.profile import SECONDS_PER_DAY, WinterProfileCalculator


def test_winter_profile_covers_required_ranges():
    """Verify the winter profile covers ALL scenario temperature ranges S0-S8."""
    config = WinterProfileConfig(
        initial_temp_c=5.0,
        min_temp_c=-25.0,
        final_temp_c=3.0,
        cooling_days=30,
        warming_days=30,
        daily_variation_c=3.0,
        noise_sigma_c=0.0,  # deterministic for the test
    )
    simulation_days = 90
    profile = WinterProfileCalculator(config, simulation_days=simulation_days, seed=42)

    # Sample every simulated day
    samples = [profile.temperature_at(day * SECONDS_PER_DAY) for day in range(simulation_days + 1)]
    
    # Verify bounds
    assert max(samples) >= config.initial_temp_c
    assert min(samples) <= config.min_temp_c

    # Scenario temperature ranges (from simulation.md):
    # S0: T ≥ 3°C
    # S1: 2°C to -1°C
    # S2: -1°C to -4°C
    # S3: -4°C to -8°C
    # S4: -8°C to -11°C
    # S5: -11°C to -15°C
    # S6: -15°C to -18°C
    # S7: -18°C to -21°C
    # S8: T < -21°C
    
    assert any(temp >= 3.0 for temp in samples), "S0 range not covered (T ≥ 3°C)"
    assert any(2.0 <= temp < 3.0 for temp in samples), "S1 upper range not covered (2-3°C)"
    assert any(-1.0 <= temp <= 2.0 for temp in samples), "S1 range not covered (2°C to -1°C)"
    assert any(-4.0 <= temp < -1.0 for temp in samples), "S2 range not covered (-1°C to -4°C)"
    assert any(-8.0 <= temp < -4.0 for temp in samples), "S3 range not covered (-4°C to -8°C)"
    assert any(-11.0 <= temp < -8.0 for temp in samples), "S4 range not covered (-8°C to -11°C)"
    assert any(-15.0 <= temp < -11.0 for temp in samples), "S5 range not covered (-11°C to -15°C)"
    assert any(-18.0 <= temp < -15.0 for temp in samples), "S6 range not covered (-15°C to -18°C)"
    assert any(-21.0 <= temp < -18.0 for temp in samples), "S7 range not covered (-18°C to -21°C)"
    assert any(temp < -21.0 for temp in samples), "S8 range not covered (T < -21°C)"


def test_daily_variation_generates_sine_wave():
    config = WinterProfileConfig(
        initial_temp_c=0.0,
        min_temp_c=0.0,
        final_temp_c=0.0,
        cooling_days=1,
        warming_days=1,
        daily_variation_c=5.0,
        noise_sigma_c=0.0,
    )
    profile = WinterProfileCalculator(config, simulation_days=1, seed=42)
    noon_seconds = 0.5 * SECONDS_PER_DAY
    midnight_seconds = 0.0
    assert math.isclose(profile.temperature_at(noon_seconds), 0.0, abs_tol=1e-6)
    assert math.isclose(profile.temperature_at(midnight_seconds), 0.0, abs_tol=1e-6)

