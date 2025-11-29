# Test Suite - Quick Start Guide

## ⚠️ Ważne - Akceleracja

**Akceleracja działa automatycznie - parametry algorytmów są w czasie SYMULACJI**

Wszystkie parametry w `config.yaml` (cykle, okresy rotacji) są wyrażone w **czasie symulacji**, nie rzeczywistym. System automatycznie skaluje `poll_interval_real` przez acceleration:

```python
poll_interval_real = temp_monitoring_cycle_s / acceleration
# 10s / 1000 = 0.01s = 10ms real time
```

Możesz bezpiecznie używać **dowolnej** akceleracji - ograniczenie to tylko **wydajność systemu** (Python overhead, HTTP latency).

## Przegląd

System testowy składa się z:
- **profili testowych** (scenarios/test_profiles.yaml)
- **Test runner** (run_test_scenarios.py) - uruchamia wszystkie testy automatycznie z opcją `--smoke`
- **Report generator** (scenarios/generate_report.py) - generuje raporty markdown

## Równoległe Wykonywanie Testów

```bash
cd src/simulation

# Wszystkie 7 profili równolegle @ 1000x acceleration (domyślne)
uv run python run_test_scenarios.py --smoke --parallel 7
```

## Szybki Start - Smoke Test (Sekwencyjny)


```bash
cd src/simulation

# Smoke test: 1 profil, 1 dzień @ 10000x acceleration (~10 sekund!)
uv run python run_test_scenarios.py --smoke --profiles profile_1_s3_baseline
```

## Pełny Test Suite - Wszystkie 7 Profili


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

### ⚠️ Problem: Zbyt duża akceleracja vs. Precyzja Rotacji

**Symptom:** Liczba rotacji w testach jest niższa niż oczekiwana

**Przyczyna:** Granularność sprawdzania algorytmów vs. okresy rotacji

#### ✅ Jak działa akceleracja i sprawdzanie algorytmów

**KLUCZOWE: Parametry algorytmów są w czasie SYMULACJI, nie rzeczywistym!**

```python
# config.yaml - wartości w SIMULATION TIME
algorithms:
  ws:
    temp_monitoring_cycle_s: 10   # Pętla główna co 10s SYMULACJI
  rc:
    algorithm_loop_cycle_s: 60    # RC sprawdzany co 60s SYMULACJI
    rotation_period_hours: 48     # Rotacja co 48h SYMULACJI
  rn:
    algorithm_loop_cycle_s: 60    # RN sprawdzany co 60s SYMULACJI
    rotation_period_s: 86400      # Rotacja co 24h SYMULACJI

# System automatycznie skaluje real time:
poll_interval_real = temp_monitoring_cycle_s / acceleration

@ 1000x:  10s / 1000 = 0.01s = 10ms real time
@ 10000x: 10s / 10000 = 0.001s = 1ms real time
```

#### Granularność vs. Precyzja

**Problem polega na granularności sprawdzania:**

```
RN sprawdzany co: 60s SYMULACJI
Rotation period: 86400s (24h)

Liczba sprawdzeń w okresie rotacji:
86400s / 60s = 1440 sprawdzeń

Max opóźnienie rotacji:
60s przy 86400s = 0.07% błędu ✅
```

**Przykład - czy przegapimy rotacje?**

```
Czas:         Sprawdzenie RN:     Czy rotacja?
86340s        TAK (60s*1439)      NIE (< 86400s)
86400s        -                   - (nie sprawdzamy)
86460s        TAK (60s*1441)      TAK! (>= 86400s)

Opóźnienie: 60s = 0.07% ✅
```

#### Limit akceleracji - Overhead systemu

**Faktyczny limit to overhead systemu:**

```
Overhead na pętlę (real time):
- Python processing: ~2-5ms
- HTTP request: ~5-10ms  
- Algorithm logic: ~1-2ms
- Display refresh: ~1-2ms (co 1s real)
TOTAL: ~10-20ms (średnio)

Bezpieczna akceleracja:
poll_interval_real >> overhead

@ 1000x:  10s/1000 = 10ms  ≈ overhead  → ⚠️ Graniczne
@ 10000x: 10s/10000 = 1ms  << overhead → ❌ Nie nadąży
```

**Bezpieczne wartości akceleracji:**

| Acceleration | poll_interval_real | Overhead | Margin | Status |
|--------------|-------------------|----------|---------|---------|
| **100x** | 100ms | 10-20ms | 5-10x | ✅ **Bardzo bezpieczne** |
| **1000x** | 10ms | 10-20ms | ~1x | ⚠️ **Graniczne, ale OK** |
| **10000x** | 1ms | 10-20ms | 0.05-0.1x | ❌ **Nie działa** |

#### Wpływ na precyzję rotacji

**Kluczowa obserwacja: Precyzja zależy od `algorithm_loop_cycle_s`, NIE od `acceleration`!**

```
Max opóźnienie rotacji = algorithm_loop_cycle_s

Przykłady:
- RC: cycle=60s, period=48h → opóźnienie max 60s = 0.035%
- RN: cycle=60s, period=24h → opóźnienie max 60s = 0.07%

✅ Precyzja NIE ZALEŻY od acceleration!
✅ Przy 1000x i 10000x precyzja TAKA SAMA (0.07%)
```

#### Rozwiązania:

**1. Użyj stabilnej akceleracji (100-1000x):**
   ```bash
   # Domyślne 1000x - stabilne, akceptowalne
   uv run python run_test_scenarios.py
   
   # Najbezpieczniejsze 100x
   uv run python run_test_scenarios.py --acceleration 100
   ```

**2. Dla smoke testów: zwiększ granularność sprawdzania:**
   
   Edytuj `config.yaml` dla smoke testów:
   ```yaml
   algorithms:
     rc:
       algorithm_loop_cycle_s: 600   # 10 min zamiast 1 min
     rn:
       algorithm_loop_cycle_s: 600   # 10 min zamiast 1 min
   ```
   
   Teraz:
   - poll_interval = 10s → max 100000x teoretycznie
   - Ale overhead nadal ogranicza do ~1000x
   - Max opóźnienie rotacji: 600s = 0.7% (nadal OK)

**3. Dla szybkich testów: skróć duration:**
   ```bash
   # 1 dzień @ 1000x = ~1.5 min
   uv run python run_test_scenarios.py --profiles profile_1 --days 1
   ```

#### Rekomendacje:

| Przypadek użycia | Acceleration | Duration | Czas real | Precyzja |
|-----------------|--------------|----------|-----------|----------|
| **Development** | 1000x | 1-5 dni | 1-7 min | 0.07% |
| **Smoke tests** | 1000x | 1 dzień | ~1.5 min | 0.07% |
| **Full tests** | 1000x | 30 dni | ~43 min | 0.07% |
| **❌ Nie używaj** | 10000x | - | - | Niestabilne |

#### Dlaczego NIE trzeba zmieniać cykli dla większej akceleracji:

❌ **BŁĘDNE myślenie:**
> "Przy 10000x muszę zwiększyć temp_monitoring_cycle_s, żeby nie przegapić rotacji"

✅ **POPRAWNE:**
> "Precyzja rotacji zależy TYLKO od algorithm_loop_cycle_s (60s). Przy 24h rotacji, 60s opóźnienie to 0.07%. Akceleracja NIE WPŁYWA na precyzję, tylko na overhead!"

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
  acceleration: 1000  # lub 10000 dla smoke testów
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
- `../../../docs/03-algorytmy/algo_pseudokod.md` - pseudokod algorytmów (SOURCE OF TRUTH dla PLC)

## Pomoc

W razie problemów:
1. Sprawdź logi: `logs/algo_service.log`
2. Sprawdź oczekiwane wyniki: `scenarios/test_profiles.yaml`
3. Zweryfikuj config: `config.yaml`
4. Uruchom smoke test: `uv run python run_test_scenarios.py --smoke`

