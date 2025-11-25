# BOGDANKA Simulation Services

This directory contains the simulation services for BOGDANKA Shaft 2 heating control algorithms.

**Status:** ✅ Phase 0, Phase 1, and Phase 2 MVP Complete  
**Tests:** 31/31 passing ✅  
**Services:** Weather + Algo (WS algorithm)

## Prerequisites

- Python 3.10 or higher
- `uv` package manager (install from https://github.com/astral-sh/uv)

## Project Structure

```
simulation/
├── common/           # Shared modules (config, domain, telemetry, time utils)
├── weather/          # Weather profile generation
├── tests/            # Unit tests
├── config.yaml       # Main configuration file
├── weather_service.py # Weather service entrypoint
├── pyproject.toml    # Python project configuration
└── README.md         # This file
```

## Setup

First, sync the dependencies to create a virtual environment:

```bash
cd src/simulation
uv sync
```

This will:
- Create a `.venv` virtual environment in the `simulation/` directory
- Install all required dependencies
- Install the `bogdanka-simulation` package in development mode

## Running the Services

### 1. Start Weather Service

```bash
cd src/simulation
uv run weather-service --config config.yaml
```

The service will start on `http://localhost:8080` (configurable in `config.yaml`).

### 2. Start Algo Service

```bash
# In another terminal
cd src/simulation
uv run algo-service --config config.yaml --days 1
```

**Options:**
- `--config PATH` - Configuration file path
- `--days N` - Simulation duration in days (1-90)

**Example Output:**
```
INFO algo-service - Weather service is ready - starting main loop
INFO algo-service - Loop 0: sim_time=19446.5s (0.23 days), T_zewn=7.5°C, scenario=S0
INFO algo-service - Loop 10: sim_time=19575.3s (0.23 days), T_zewn=7.2°C, scenario=S0
```

### Test the service:

```bash
curl http://localhost:8080/temperature
```

Expected response:
```json
{
  "profile": {
    "final_temp": 3.0,
    "initial_temp": 5.0,
    "min_temp": -25.0
  },
  "simulation_day": 0.182,
  "simulation_time": 15705.744,
  "t_zewn": 6.222,
  "timestamp": "2025-11-25T10:45:07.931391+00:00"
}
```

### Command-line options:

```bash
# Use custom config file
uv run weather-service --config path/to/config.yaml

# Override host and port
uv run weather-service --host 0.0.0.0 --port 9000
```

## Running Tests

Run all tests:

```bash
cd src/simulation
uv run pytest
```

Run specific test file:

```bash
uv run pytest tests/test_winter_profile.py
```

Run with verbose output:

```bash
uv run pytest -v
```

## Configuration

The service configuration is in `config.yaml`. Key sections:

### Simulation Settings
```yaml
simulation:
  duration_days: 90      # Total simulation duration
  acceleration: 1000.0   # Time acceleration factor
```

### Weather Service
```yaml
services:
  weather:
    host: localhost
    port: 8080
    metrics_prefix: bogdanka.weather
    winter_profile:
      simulation_days: 90
      initial_temp_c: 5.0
      min_temp_c: -25.0
      final_temp_c: 3.0
      cooling_days: 30
      warming_days: 30
      daily_variation_c: 3.0
      noise_sigma_c: 1.5
```

### Telemetry
```yaml
telemetry:
  log_level: INFO
  exporter_type: otlp  # or 'console' for debugging
  default_dimensions:
    environment: development
    service: bogdanka-simulation
```

## Development

### Adding Dependencies

To add a new dependency:

```bash
uv add package-name
```

For development-only dependencies:

```bash
uv add --dev package-name
```

### Code Structure

- **`weather_service.py`** - Main Flask application for weather simulation
- **`common/config.py`** - Configuration loading and validation
- **`common/domain.py`** - Domain models (WeatherSnapshot, etc.)
- **`common/telemetry.py`** - OpenTelemetry integration
- **`common/time_utils.py`** - Accelerated clock implementation
- **`weather/profile.py`** - Winter temperature profile calculator

## Troubleshooting

### Import Errors

All imports within the simulation package use relative imports (without the `simulation.` prefix):

```python
# Correct
from common.config import AppConfig
from weather.profile import WinterProfileCalculator

# Incorrect (old style)
from simulation.common.config import AppConfig
from simulation.weather.profile import WinterProfileCalculator
```

### Running from Wrong Directory

Always run commands from the `src/simulation/` directory:

```bash
# ✅ Correct
cd src/simulation
uv run weather-service --config config.yaml

# ❌ Wrong - will fail with ModuleNotFoundError
cd src
uv run simulation/weather_service.py
```

### Virtual Environment Issues

If you encounter issues with the virtual environment, recreate it:

```bash
cd src/simulation
rm -rf .venv
uv sync
```

## API Endpoints

### GET /temperature

Returns the current weather snapshot.

**Response:**
```json
{
  "timestamp": "2025-11-25T10:45:07.931391+00:00",
  "t_zewn": 6.222,
  "simulation_time": 15705.744,
  "simulation_day": 0.182,
  "profile": {
    "initial_temp": 5.0,
    "min_temp": -25.0,
    "final_temp": 3.0
  }
}
```

**Fields:**
- `timestamp` - ISO 8601 timestamp of the response
- `t_zewn` - Current external temperature in °C (Polish: temperatura zewnętrzna)
- `simulation_time` - Current simulation time in seconds
- `simulation_day` - Current simulation day (float)
- `profile` - Weather profile metadata

## License

Part of the BOGDANKA project.

