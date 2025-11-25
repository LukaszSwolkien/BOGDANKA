"""Tests for accelerated time utilities."""

import time

import pytest

from common.time_utils import AcceleratedClock


def test_accelerated_clock_initialization():
    """Test that AcceleratedClock initializes with proper acceleration."""
    clock = AcceleratedClock(acceleration=1000.0)
    assert clock.acceleration == 1000.0


def test_accelerated_clock_invalid_acceleration():
    """Test that invalid acceleration raises ValueError."""
    with pytest.raises(ValueError, match="must be positive"):
        AcceleratedClock(acceleration=0)
    
    with pytest.raises(ValueError, match="must be positive"):
        AcceleratedClock(acceleration=-100)


def test_accelerated_clock_time_progression():
    """Test that simulation time advances according to acceleration."""
    clock = AcceleratedClock(acceleration=1000.0)
    
    start_sim = clock.now()
    time.sleep(0.1)  # 0.1 seconds real time
    end_sim = clock.now()
    
    # With 1000x acceleration, 0.1s real time = 100s simulation time
    elapsed_sim = end_sim - start_sim
    assert 90 <= elapsed_sim <= 110  # Allow some tolerance


def test_accelerated_clock_sleep():
    """Test that sleep_sim_seconds sleeps the correct real time."""
    clock = AcceleratedClock(acceleration=1000.0)
    
    start_real = time.time()
    clock.sleep_sim_seconds(1000)  # 1000 simulation seconds
    end_real = time.time()
    
    # With 1000x acceleration, 1000 sim seconds = 1 real second
    elapsed_real = end_real - start_real
    assert 0.9 <= elapsed_real <= 1.1  # Allow some tolerance


def test_accelerated_clock_zero_sleep():
    """Test that zero or negative sleep doesn't cause issues."""
    clock = AcceleratedClock(acceleration=1000.0)
    
    start = time.time()
    clock.sleep_sim_seconds(0)
    clock.sleep_sim_seconds(-10)
    end = time.time()
    
    # Should complete almost instantly
    assert end - start < 0.1


def test_accelerated_clock_reset():
    """Test that reset() resets the simulation time."""
    clock = AcceleratedClock(acceleration=1000.0)
    
    time.sleep(0.1)
    assert clock.now() > 0
    
    clock.reset()
    # After reset, time should be close to 0
    assert clock.now() < 10  # Allow small tolerance for execution time


def test_accelerated_clock_different_accelerations():
    """Test multiple clocks with different acceleration factors."""
    clock_1x = AcceleratedClock(acceleration=1.0)
    clock_1000x = AcceleratedClock(acceleration=1000.0)
    
    time.sleep(0.1)
    
    time_1x = clock_1x.now()
    time_1000x = clock_1000x.now()
    
    # 1000x should be ~1000 times faster than 1x
    assert 900 <= time_1000x / time_1x <= 1100

