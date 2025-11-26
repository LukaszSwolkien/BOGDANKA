# Test Suite - Quick Start Guide

## Przegląd

System testowy składa się z:
- **7 profili testowych** (scenarios/test_profiles.yaml)
- **Test runner** (run_test_scenarios.py) - uruchamia wszystkie testy automatycznie z opcją `--smoke`
- **Report generator** (scenarios/generate_report.py) - generuje raporty markdown

## Szybki Start - Smoke Test

### Single Profile Test (S3 Baseline) - ~8 sekund

```bash
cd src/simulation

# Smoke test: 1 profil, 1 dzień @ 10000x acceleration
uv run python run_test_scenarios.py --smoke --profiles profile_1_s3_baseline
```

### Wszystkie Profile Smoke Test - ~60 sekund

```bash
cd src/simulation

# Smoke test: wszystkie 7 profili @ 10000x acceleration
uv run python run_test_scenarios.py --smoke
```

## Pełny Test Suite - Wszystkie 7 Profili

### Uruchomienie (~10-15 minut)

```bash
cd src/simulation

# Uruchom wszystkie testy (z katalogu src/simulation)
uv run python run_test_scenarios.py
```

### Wyniki

Wyniki zapisywane są w `test_results/`:
- `test_results_YYYYMMDD_HHMMSS.yaml` - surowe dane YAML
- `test_results_YYYYMMDD_HHMMSS_report.md` - czytelny raport markdown

### Generowanie raportu ręcznie

```bash
# Wygeneruj raport z istniejących wyników (z katalogu src/simulation)
uv run python scenarios/generate_report.py scenarios/test_results/test_results_20251126_120000.yaml
```

## Profile Testowe

### Profil 1: TEST_S3_BASELINE ⭐ (HIGH)
- Temp: -5°C (stała)
- Czas: 30 dni
- Test: RC + RN, balansowanie

### Profil 2: TEST_S6_DUAL_LINE ⭐ (HIGH)
- Temp: -16°C (stała)
- Czas: 30 dni
- Test: Tryb dwuliniowy, asymetria

### Profil 3: TEST_S1_MINIMAL (MEDIUM)
- Temp: 0°C (stała)
- Czas: 30 dni
- Test: RC minimalny, brak RN

### Profil 4: TEST_S4_MAXIMAL (MEDIUM)
- Temp: -9°C (stała)
- Czas: 30 dni
- Test: RC maksymalny jednoliniowy

### Profil 5: TEST_SCENARIO_TRANSITIONS ⭐ (HIGH)
- Temp: Kroki (0°C → -5°C → -16°C → -5°C)
- Czas: 20 dni
- Test: Przejścia scenariuszowe, synchronizacja

### Profil 6: TEST_S0_WARMUP (MEDIUM)
- Temp: Kroki (5°C → -5°C)
- Czas: 10 dni
- Test: Rozruch z S0

### Profil 7: UNSTABLE_WINTER (MEDIUM)
- Temp: 14 kroków (symulacja niestabilnej zimy)
- Czas: 14 dni
- Test: Złożony scenariusz z przejściem przez S5

## Interpretacja Wyników

### Status testów:
- ✅ **PASSED** - wszystkie warunki spełnione
- ❌ **FAILED** - niektóre warunki nie spełnione
- ⚠️ **ERROR** - błąd wykonania testu

### Kluczowe metryki:
- **RC Rotations** - liczba rotacji ciągów Primary↔Limited
- **RN Rotations** - liczba rotacji nagrzewnic
- **Balance Ratio** - stosunek max/min czasu pracy (≤1.5 = dobry)
- **Primary/Limited Balance** - stosunek czasu P/L (~1.0 = idealny)

### Kryteria sukcesu:
- ✅ RC rotacje: ±1 od oczekiwanych
- ✅ RN rotacje: ±2 od oczekiwanych
- ✅ Balans nagrzewnic: max/min ≤ 1.5
- ✅ Balans P/L: 0.9-1.1

## Troubleshooting

### Problem: "ModuleNotFoundError"
```bash
# Upewnij się, że jesteś w właściwym katalogu
cd src/simulation

# Zainstaluj zależności
uv sync
```

### Problem: "Port already in use"
```bash
# Znajdź i zabij proces na porcie 8080
lsof -ti:8080 | xargs kill -9
```

### Problem: Test trwa zbyt długo
```bash
# Zwiększ acceleration w config.yaml
simulation:
  acceleration: 2000  # Przyspiesza 2x
```

### Problem: Wyniki niezgodne z oczekiwaniami
1. Sprawdź logi w `logs/algo_service.log`
2. Sprawdź console output dla błędów
3. Porównaj z oczekiwanymi wynikami w `test_profiles.yaml`

## Konfiguracja Testów

### Dostosowanie profili testowych

Edytuj `test_profiles.yaml`:

```yaml
test_profiles:
  - id: profile_1_s3_baseline
    name: TEST_S3_BASELINE
    priority: HIGH
    description: Podstawowy test RC i RN
    duration_days: 30
    profile_type: constant
    temperature_c: -5.0
    expected_scenario: S3
    expected_results:
      rc_rotations: {min: 14, max: 16, target: 15}
      rn_rotations: {min: 26, max: 29, target: 27}
  "id": "my_test",
  "name": "MY_CUSTOM_TEST",
  "duration_days": 10,
  "profile_type": "constant",
  "temperature_c": -7.0,
  "expected_results": {
    "rc_rotations": {"min": 4, "max": 6},
    "rn_rotations": {"min": 8, "max": 10}
  }
}
```

### Tworzenie własnego profilu STEPPED

```yaml
- id: my_custom_profile
  name: MY_CUSTOM_TEST
  priority: HIGH
  description: Custom stepped temperature profile
  duration_days: 10
  profile_type: stepped
  steps:
    - {day_start: 0, day_end: 5, temperature_c: 0.0}
    - {day_start: 5, day_end: 10, temperature_c: -5.0}
  expected_results:
    scenario_changes: {min: 1, max: 2, target: 1}
```

## Następne Kroki

Po udanych testach:
1. Przejrzyj wygenerowany raport markdown
2. Sprawdź czy wszystkie HIGH priority testy przeszły
3. Jeśli wszystko OK → rozpocznij implementację PLC
4. Jeśli są problemy → przeanalizuj logi i zaktualizuj pseudokod

## Pliki i Dokumentacja

- `scenarios/test_profiles.yaml` - definicje profili testowych (7 scenariuszy)
- `run_test_scenarios.py` - główny runner testów z opcją `--smoke` (w głównym katalogu simulation)
- `scenarios/generate_report.py` - generator raportów markdown
- `../algo_pseudokod.md` - pseudokod algorytmów (SOURCE OF TRUTH dla PLC)
- `scenarios/README.md` - ten dokument (instrukcje testowania)

## Pomoc

W razie problemów:
1. Sprawdź logi: `logs/algo_service.log`
2. Sprawdź oczekiwane wyniki: `scenarios/test_profiles.yaml`
3. Zweryfikuj config: `config.yaml`
4. Uruchom smoke test: `uv run python run_test_scenarios.py --smoke`

