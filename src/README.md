# BOGDANKA Shaft 2 System Implementation

This directory contains system control implementation and simulation.

## KEY IMPLEMENTATION PRINCIPLE

**Pseudocode in [`algo_pseudokod.md`](../docs/03-algorytmy/algo_pseudokod.md) is the single source of truth for algorithm logic!**

- Every implementation (simulation) must **exactly** match the pseudocode
- DO NOT modify logic without updating pseudocode

---

## Konfiguracja

System wykorzystuje plik konfiguracyjny `simulation/config.yaml`, który zawiera:

- **Parametry symulacji**: przyspieszenie czasu (`acceleration`), czas trwania (`duration_days`)
- **Telemetrię**: eksport metryk do Splunk Observability Cloud (OTLP), poziom logowania
- **Algorytmy**: parametry dla WS (wybór scenariusza), RC (rotacja ciągów), RN (rotacja nagrzewnic)
- **Profile temperatury**: `winter` (profil zimowy), `constant` (stała temperatura), `stepped` (temperatura schodkowa)
- **Serwisy**: porty, endpointy dla `weather_service` i `algo_service`

Szczegółowe informacje o parametrach znajdują się w pliku `simulation/config.yaml`.

## Uruchamianie serwisów

System używa `uv` do zarządzania zależnościami i uruchamiania serwisów.

### 1. Weather Service

Serwis pogodowy dostarcza dane o temperaturze zewnętrznej.

```bash
# Uruchomienie z domyślną konfiguracją
cd simulation
uv run weather-service

# Uruchomienie z niestandardowym plikiem konfiguracyjnym
uv run weather-service --config custom_config.yaml

# Nadpisanie hosta i portu
uv run weather-service --host 0.0.0.0 --port 8081
```

**Endpoint**: `http://localhost:8080/temperature` (GET) - zwraca aktualne dane pogodowe w formacie JSON.

### 2. Algo Service

Główny serwis algorytmów sterowania (WS, RC, RN). **Wymaga uruchomionego Weather Service**.

```bash
# Uruchomienie z domyślną konfiguracją
cd simulation
uv run algo-service

# Uruchomienie z niestandardowym plikiem konfiguracyjnym
uv run algo-service --config custom_config.yaml

# Nadpisanie czasu trwania symulacji
uv run algo-service --days 7
```

Serwis automatycznie:
- Łączy się z Weather Service (endpoint z `config.yaml`)
- Uruchamia algorytmy WS, RC, RN zgodnie z pseudokodem
- Wyświetla status w konsoli (jeśli `display.enabled: true`)
- Eksportuje metryki do Splunk Observability Cloud

### 3. Uruchomienie scenariuszy testowych

System zawiera zestaw predefiniowanych scenariuszy testowych:

```bash
cd simulation
uv run python run_test_scenarios.py
```

Wyniki zapisywane są w katalogu `scenarios/test_results/`.

---

**Documentation:** [../docs/start.md](../docs/start.md)
