# OpenTelemetry Metrics - Dokumentacja

> **Wersja:** 1.0  
> **Data:** 2025-11-28  
> **Projekt:** BOGDANKA - System Ogrzewania Szybu

## Spis Treści

1. [Wprowadzenie](#wprowadzenie)
2. [Metryki Emitowane](#metryki-emitowane)
   - [Weather Service](#weather-service-metrics)
   - [Algo Service - WS Algorithm](#ws-algorithm-metrics)
   - [Algo Service - RC Algorithm](#rc-algorithm-metrics)
   - [Algo Service - RN Algorithm](#rn-algorithm-metrics)
3. [Dashboardy Splunk Observability](#dashboardy-splunk-observability)
   - [Dashboard 1: Przegląd Systemu](#dashboard-1-przeglad-systemu)
   - [Dashboard 2: Status Nagrzewnic](#dashboard-2-status-nagrzewnic)
   - [Dashboard 3: Status Ciągów](#dashboard-3-status-ciagow)
   - [Dashboard 4: Analiza Rotacji](#dashboard-4-analiza-rotacji)
   - [Dashboard 5: Walidacja Testów](#dashboard-5-walidacja-testow)
4. [SignalFlow Queries](#signalflow-queries)
5. [Alerts](#alerts)

---

## Wprowadzenie

System BOGDANKA emituje metryki OpenTelemetry do Splunk Observability Cloud. Wszystkie metryki są wysyłane przez OTLP exporter z prefiksem `bogdanka.*`.

**Konfiguracja:**
- **Resource Attributes:** `environment`, `project`
- **Default Dimensions:** `site` (np. "Szyb-2")
- **Export Interval:** 10 sekund
- **Endpoint:** `https://ingest.signalfx.com/v2/datapoint/otlp`

---

## Metryki Emitowane

### Weather Service Metrics

Usługa pogodowa emituje metryki związane z profilem temperaturowym.

| Nazwa Metryki | Typ | Jednostka | Wymiary | Opis | Źródło |
|--------------|-----|-----------|---------|------|--------|
| `bogdanka.weather.external_temperature` | Gauge | °C | `site` | Aktualna temperatura zewnętrzna | `weather_service.py:39-42` |
| `bogdanka.weather.simulation_day` | Gauge | days | `site` | Aktualny dzień symulacji (0-30) | `weather_service.py:43-46` |
| `bogdanka.weather.requests_total` | Counter | count | `site` | Całkowita liczba obsłużonych żądań API | `weather_service.py:47` |
| `bogdanka.weather.errors_total` | Counter | count | `site`, `error_type` | Całkowita liczba błędów | `weather_service.py:48` |

---

### WS Algorithm Metrics

Algorytm WS (Wybór Scenariusza) - wybiera scenariusz S0-S8 na podstawie temperatury.

| Nazwa Metryki | Typ | Jednostka | Wymiary | Opis | Źródło |
|--------------|-----|-----------|---------|------|--------|
| `bogdanka.algo.ws.scenario` | Gauge | enum (0-8) | `site` | Aktualny scenariusz (S0=0, S1=1, ..., S8=8) | `algo/metrics.py:38-42` |
| `bogdanka.algo.ws.temperature_external` | Gauge | °C | `site` | Temperatura zewnętrzna (kopiowana z weather service) | `algo/metrics.py:45-50` |
| `bogdanka.algo.ws.scenario_time_s` | Counter | seconds | `site`, `scenario` | Całkowity czas spędzony w każdym scenariuszu (S0-S8) | `algo/metrics.py:53-57` |
| `bogdanka.algo.ws.scenario_changes` | Counter | count | `site`, `from_scenario`, `to_scenario` | Liczba przejść między scenariuszami (np. S1→S3) | `algo/metrics.py:60-63` |

**Kluczowe zastosowania:**
- **Dystrybucja czasu:** Ile % czasu system spędził w S0, S1, ..., S8
- **Analiza przejść:** Jakie przejścia są najczęstsze (S3↔S6, S1→S3, itd.)
- **Korelacja:** Temperatura vs wybór scenariusza

---

### RC Algorithm Metrics

Algorytm RC (Rotacja Ciągów) - rotuje między konfiguracją Primary (C1) a Limited (C2) w scenariuszach S1-S4.

| Nazwa Metryki | Typ | Jednostka | Wymiary | Opis | Źródło |
|--------------|-----|-----------|---------|------|--------|
| `bogdanka.algo.rc.current_config` | Gauge | enum (0/1) | `site` | Aktualna konfiguracja (0=Primary/C1, 1=Limited/C2) | `algo/metrics.py:70-74` |
| `bogdanka.algo.rc.config_time_s` | Counter | seconds | `site`, `config` | Całkowity czas pracy w każdej konfiguracji (Primary/Limited) | `algo/metrics.py:77-81` |
| `bogdanka.algo.rc.rotation_count` | Counter | count | `site`, `from_config`, `to_config` | Liczba rotacji ciągów (Primary↔Limited) | `algo/metrics.py:84-87` |
| `bogdanka.algo.rc.rotation_duration_s` | Histogram | seconds | `site` | Histogram czasów trwania rotacji RC | `algo/metrics.py:90-94` |

**Kluczowe zastosowania:**
- **Balans ciągów:** Czy Primary i Limited mają zbliżony czas pracy?
- **Częstotliwość rotacji:** Czy rotacje następują co ~2 dni (168h)?
- **Czas rotacji:** Jak długo trwa zmiana konfiguracji?

---

### RN Algorithm Metrics

Algorytm RN (Rotacja Nagrzewnic) - rotuje nagrzewnice w ramach każdego ciągu, aby zbalansować czas pracy.

| Nazwa Metryki | Typ | Jednostka | Wymiary | Opis | Źródło |
|--------------|-----|-----------|---------|------|--------|
| `bogdanka.algo.rn.rotation_count` | Counter | count | `site`, `line`, `heater_off`, `heater_on` | Liczba rotacji nagrzewnic (np. N1→N2 w C1) | `algo/metrics.py:106-109` |
| `bogdanka.algo.rn.rotation_duration_s` | Histogram | seconds | `site`, `line` | Histogram czasów trwania rotacji RN | `algo/metrics.py:112-116` |
| `bogdanka.algo.rn.heater_operating_time_s` | Gauge | seconds | `site`, `heater`, `line` | Całkowity czas pracy każdej nagrzewnicy | `algo/metrics.py:119-124` |
| `bogdanka.algo.rn.heater_state` | Gauge | enum (0-2) | `site`, `heater`, `line` | Stan nagrzewnicy (0=idle, 1=active, 2=faulty) | `algo/metrics.py:127-131` |

**Kluczowe zastosowania:**
- **Balans nagrzewnic:** Monitorowanie równomiernego rozłożenia czasu pracy
- **Status real-time:** Bieżący stan każdej nagrzewnicy (aktywna/bezczynna/awaria)
- **Analiza rotacji:** Częstotliwość i czas trwania rotacji nagrzewnic

---

## Dashboardy Splunk Observability

### Dashboard 1: Przegląd Systemu

**Cel:** Widok wysokopoziomowy na stan systemu (podobny do sekcji "Symulacja" w `display.py`)

#### Wykresy:

1. **Current Scenario (Single Value)**
   - Metryka: `bogdanka.algo.ws.scenario`
   - Typ: Single Value
   - Mapowanie: 0→S0, 1→S1, ..., 8→S8
   - Color coding: S0=green, S1-S4=yellow, S5-S8=red

2. **External Temperature (Line Chart)**
   - Metryka: `bogdanka.algo.ws.temperature_external`
   - Typ: Line Chart
   - Timeframe: Last 24h

3. **Scenario Timeline (Area Chart)**
   - Metryka: `bogdanka.algo.ws.scenario`
   - Typ: Area Chart (stacked)
   - Timeframe: Last 7d
   - Pokazuje historię przejść scenariuszy

4. **Scenario Distribution (Pie Chart)**
   - Metryka: `bogdanka.algo.ws.scenario_time_s` (counter)
   - Typ: Pie Chart
   - Agregacja: Sum over last 30d
   - Pokazuje % czasu w każdym scenariuszu (zgodnie z `expected_results`)

**SignalFlow:**

```python
# Current Scenario
data('bogdanka.algo.ws.scenario', filter=filter('site', 'Szyb-2')).publish(label='Current Scenario')

# Scenario Distribution (% time in each scenario)
A = data('bogdanka.algo.ws.scenario_time_s', filter=filter('site', 'Szyb-2'), rollup='rate').sum(by=['scenario']).publish(label='A', enable=False)
B = A.sum().publish(label='Total', enable=False)
(A / B * 100).publish(label='Scenario %')
```

---

### Dashboard 2: Status Nagrzewnic

**Cel:** Real-time monitoring nagrzewnic (zgodnie z sekcją "Nagrzewnice" i "Statystyki Nagrzewnic" w `display.py`)

#### Wykresy:

1. **Heater States - C1 (Status Indicator)**
   - ✅ **METRYKA:** `bogdanka.algo.rn.heater_state` z wymiarem `heater`
   - Typ: List (4 rows: N1, N2, N3, N4)
   - Wartość: 0=IDLE (gray ✖), 1=ACTIVE (green ✔), 2=FAULTY (red ✗)

2. **Heater States - C2 (Status Indicator)**
   - ✅ **METRYKA:** `bogdanka.algo.rn.heater_state` z wymiarem `heater`
   - Typ: List (4 rows: N5, N6, N7, N8)
   - Wartość: 0=IDLE, 1=ACTIVE, 2=FAULTY

3. **Heater Operating Time - C1 (Bar Chart)**
   - ✅ **METRYKA:** `bogdanka.algo.rn.heater_operating_time_s` z wymiarem `heater`
   - Typ: Bar Chart (horizontal)
   - Filtr: `heater` IN [N1, N2, N3, N4]
   - Jednostka: hours (divide by 3600)

4. **Heater Operating Time - C2 (Bar Chart)**
   - ✅ **METRYKA:** `bogdanka.algo.rn.heater_operating_time_s` z wymiarem `heater`
   - Typ: Bar Chart (horizontal)
   - Filtr: `heater` IN [N5, N6, N7, N8]
   - Jednostka: hours

5. **Heater Balance Ratio - C1 (Single Value)**
   - Metryka: `bogdanka.algo.rn.heater_operating_time_s`
   - Typ: Single Value
   - Kalkulacja: `max(N1,N2,N3,N4) / min(N1,N2,N3,N4)`
   - Alert: > 1.5 (zgodnie z `expected_results.heater_balance_ratio`)

6. **Heater Balance Ratio - C2 (Single Value)**
   - Metryka: `bogdanka.algo.rn.heater_operating_time_s`
   - Typ: Single Value
   - Kalkulacja: `max(N5,N6,N7,N8) / min(N5,N6,N7,N8)`
   - Alert: > 1.3 (zgodnie z `expected_results.heater_balance_ratio_c2`)

7. **Total RN Rotations (Single Value)**
   - Metryka: `bogdanka.algo.rn.rotation_count`
   - Typ: Single Value
   - Agregacja: Sum (all dimensions)
   - Timeframe: Last 30d

**SignalFlow:**

```python
# Heater Operating Time (C1)
data('bogdanka.algo.rn.heater_operating_time_s', 
     filter=filter('site', 'Szyb-2') and filter('heater', 'N1', 'N2', 'N3', 'N4')
).publish(label='C1 Operating Time (s)')

# Heater Balance Ratio (C1)
A = data('bogdanka.algo.rn.heater_operating_time_s', 
         filter=filter('site', 'Szyb-2') and filter('heater', 'N1', 'N2', 'N3', 'N4'))
max_time = A.max(by=['site']).publish(label='Max', enable=False)
min_time = A.min(by=['site']).publish(label='Min', enable=False)
(max_time / min_time).publish(label='Heater Balance Ratio C1')

# Total RN Rotations (last 30d)
data('bogdanka.algo.rn.rotation_count', 
     filter=filter('site', 'Szyb-2'), 
     rollup='sum'
).sum().publish(label='Total RN Rotations')
```

---

### Dashboard 3: Status Ciągów

**Cel:** Monitoring konfiguracji i rotacji ciągów (zgodnie z sekcją "Status Ciągów" w `display.py`)

#### Wykresy:

1. **Current Configuration (Single Value)**
   - Metryka: `bogdanka.algo.rc.current_config`
   - Typ: Single Value
   - Mapowanie: 0→"C1 (Primary)", 1→"C2 (Limited)"

2. **Configuration Timeline (Area Chart)**
   - Metryka: `bogdanka.algo.rc.current_config`
   - Typ: Area Chart
   - Timeframe: Last 7d
   - Pokazuje przełączenia Primary↔Limited

3. **Configuration Time Distribution (Pie Chart)**
   - Metryka: `bogdanka.algo.rc.config_time_s`
   - Typ: Pie Chart
   - Agregacja: Sum over last 30d
   - Pokazuje balans Primary vs Limited

4. **Primary/Limited Balance Ratio (Single Value)**
   - Metryka: `bogdanka.algo.rc.config_time_s`
   - Typ: Single Value
   - Kalkulacja: `time(Primary) / time(Limited)`
   - Alert: < 0.9 lub > 1.1 (zgodnie z `expected_results.primary_limited_balance`)

5. **RC Rotation Count (Single Value)**
   - Metryka: `bogdanka.algo.rc.rotation_count`
   - Typ: Single Value
   - Agregacja: Sum over last 30d
   - Target: ~15 dla 30 dni (rotation co 2 dni)

6. **RC Rotation Duration (Histogram)**
   - Metryka: `bogdanka.algo.rc.rotation_duration_s`
   - Typ: Histogram
   - Timeframe: Last 7d
   - Pokazuje ile czasu trwa rotacja RC

**SignalFlow:**

```python
# Configuration Balance
A = data('bogdanka.algo.rc.config_time_s', 
         filter=filter('site', 'Szyb-2') and filter('config', 'Primary')
).sum().publish(label='Primary Time', enable=False)

B = data('bogdanka.algo.rc.config_time_s', 
         filter=filter('site', 'Szyb-2') and filter('config', 'Limited')
).sum().publish(label='Limited Time', enable=False)

(A / B).publish(label='Primary/Limited Balance')

# RC Rotations (last 30d)
data('bogdanka.algo.rc.rotation_count', 
     filter=filter('site', 'Szyb-2'), 
     rollup='sum'
).sum().publish(label='RC Rotations (30d)')
```

---

### Dashboard 4: Analiza Rotacji

**Cel:** Szczegółowa analiza rotacji RC i RN (zgodnie z sekcją "Następne rotacje i blokady" w `display.py`)

#### Wykresy:

1. **RC Rotation Frequency (Heatmap)**
   - Metryka: `bogdanka.algo.rc.rotation_count`
   - Typ: Heatmap (day of week × hour of day)
   - Timeframe: Last 30d
   - Pokazuje wzorce rotacji

2. **RN Rotation Frequency - C1 (Line Chart)**
   - Metryka: `bogdanka.algo.rn.rotation_count`
   - Typ: Line Chart
   - Filtr: `line='C1'`
   - Agregacja: Count per day
   - Target: ~1 rotation/day (zgodnie z `expected_results.rn_rotations`)

3. **RN Rotation Frequency - C2 (Line Chart)**
   - Metryka: `bogdanka.algo.rn.rotation_count`
   - Typ: Line Chart
   - Filtr: `line='C2'`
   - Agregacja: Count per day

4. **Most Common Heater Rotations (Table)**
   - Metryka: `bogdanka.algo.rn.rotation_count`
   - Typ: Table
   - Kolumny: `line`, `heater_off`, `heater_on`, `count`
   - Sort: By count DESC
   - Top 10

5. **Rotation Duration Comparison (Box Plot)**
   - Metryki: `bogdanka.algo.rc.rotation_duration_s`, `bogdanka.algo.rn.rotation_duration_s`
   - Typ: Box Plot
   - Porównanie RC vs RN duration

**SignalFlow:**

```python
# RN Rotations per day (C1)
data('bogdanka.algo.rn.rotation_count', 
     filter=filter('site', 'Szyb-2') and filter('line', 'C1'),
     rollup='sum'
).sum().timeshift('1d').publish(label='C1 Rotations/day')

# Most common heater rotations
data('bogdanka.algo.rn.rotation_count', 
     filter=filter('site', 'Szyb-2'),
     rollup='sum'
).sum(by=['line', 'heater_off', 'heater_on']).top(count=10).publish(label='Top Rotations')
```

---

### Dashboard 5: Walidacja Testów

**Cel:** Metryki zgodne z `expected_results` w `test_profiles.yaml` - superset wszystkich walidacji

#### Wykresy:

**Profile 1 (S3 Baseline):**

1. **RC Rotations (15d) - Gauge**
   - Metryka: `bogdanka.algo.rc.rotation_count`
   - Target: 7 ± 1 (zgodnie z `profile_1_s3_baseline.expected_results.rc_rotations`)
   - Color: Green jeśli 7-8, Red jeśli poza zakresem

2. **RN Rotations (15d) - Gauge**
   - Metryka: `bogdanka.algo.rn.rotation_count`
   - Target: 14 ± 1 (zgodnie z `profile_1_s3_baseline.expected_results.rn_rotations`)

3. **Primary/Limited Balance - Gauge**
   - Metryka: `bogdanka.algo.rc.config_time_s`
   - Target: 1.0 ± 0.1 (zgodnie z `profile_1_s3_baseline.expected_results.primary_limited_balance`)

4. **Heater Balance Ratio - Gauge**
   - ✅ **METRYKA:** `bogdanka.algo.rn.heater_operating_time_s`
   - Target: < 1.5 (zgodnie z `profile_1_s3_baseline.expected_results.heater_balance_ratio`)

5. **Heater Usage % - Gauge**
   - ✅ **METRYKA:** `bogdanka.algo.rn.heater_operating_time_s`
   - Target: 12.5% ± 2.5% (zgodnie z `profile_1_s3_baseline.expected_results.heater_usage_percent`)

**Profile 2 (S6 Dual-Line):**

6. **RN Rotations C1 (15d) - Gauge**
   - Metryka: `bogdanka.algo.rn.rotation_count` (filter: `line='C1'`)
   - Target: 0 (zgodnie z `profile_2_s6_dual_line.expected_results.rn_rotations_c1`)
   - Wyjaśnienie: C1 ma 4/4 nagrzewnic aktywnych, brak rezerwy

7. **RN Rotations C2 (15d) - Gauge**
   - Metryka: `bogdanka.algo.rn.rotation_count` (filter: `line='C2'`)
   - Target: 14 ± 1 (zgodnie z `profile_2_s6_dual_line.expected_results.rn_rotations_c2`)

8. **N1-N4 Operating Hours - Bar Chart**
   - ✅ **METRYKA:** `bogdanka.algo.rn.heater_operating_time_s`
   - Target: 360h każda ± 15h (zgodnie z `profile_2_s6_dual_line.expected_results.n1_n4_operating_hours`)

9. **N5-N6 Operating Hours - Bar Chart**
   - ✅ **METRYKA:** `bogdanka.algo.rn.heater_operating_time_s`
   - Target: 180h każda ± 10h (zgodnie z `profile_2_s6_dual_line.expected_results.n5_n6_operating_hours`)

**Profile 3 (S1 Minimal):**

10. **N1 Operating Hours - Gauge**
    - ✅ **METRYKA:** `bogdanka.algo.rn.heater_operating_time_s` (filter: `heater='N1'`)
    - Target: 45h ± 5h (zgodnie z `profile_3_s1_minimal.expected_results.n1_operating_hours`)

11. **N5 Operating Hours - Gauge**
    - ✅ **METRYKA:** `bogdanka.algo.rn.heater_operating_time_s` (filter: `heater='N5'`)
    - Target: 45h ± 5h (zgodnie z `profile_3_s1_minimal.expected_results.n5_operating_hours`)

**Profile 5 (Transitions):**

12. **Scenario Changes - Gauge**
    - Metryka: `bogdanka.algo.ws.scenario_changes`
    - Target: 3 (zgodnie z `profile_5_transitions.expected_results.scenario_changes`)
    - Oczekiwane: S1→S3, S3→S6, S6→S3

13. **Structural Changes - Gauge**
    - Metryka: `bogdanka.algo.ws.scenario_changes` (filter: structural changes tylko)
    - Target: 2 (zgodnie z `profile_5_transitions.expected_results.structural_changes`)
    - Oczekiwane: S3↔S6 (dual-line mode)

14. **Scenarios Visited - List**
    - Metryka: `bogdanka.algo.ws.scenario_time_s` (unique scenarios with time > 0)
    - Target: [S1, S3, S6] (zgodnie z `profile_5_transitions.expected_results.scenarios_visited`)

**Profile 6 (S0 Warmup):**

15. **S0 Detection - Boolean**
    - Metryka: `bogdanka.algo.ws.scenario_time_s` (filter: `scenario='S0'`)
    - Target: > 0 (zgodnie z `profile_6_s0_warmup.expected_results.s0_detection`)

**Profile 7 (Unstable Winter):**

16. **Scenarios Visited - List**
    - Metryka: `bogdanka.algo.ws.scenario_time_s` (unique scenarios)
    - Target: [S0, S1, S2, S3, S4, S5] (zgodnie z `profile_7_unstable_winter.expected_results.scenarios_visited`)

**SignalFlow (Validation):**

```python
# RC Rotations (30d) - should be ~15 for constant scenario
A = data('bogdanka.algo.rc.rotation_count', 
         filter=filter('site', 'Szyb-2'), 
         rollup='sum'
).sum()

# Check if in range [14, 16]
const(14).publish(label='Min Expected', enable=False)
const(16).publish(label='Max Expected', enable=False)
A.publish(label='Actual RC Rotations')

# RN Rotations per line (30d)
data('bogdanka.algo.rn.rotation_count', 
     filter=filter('site', 'Szyb-2'),
     rollup='sum'
).sum(by=['line']).publish(label='RN Rotations by Line')

# Primary/Limited Balance
primary_time = data('bogdanka.algo.rc.config_time_s', 
                    filter=filter('site', 'Szyb-2') and filter('config', 'Primary')
).sum().publish(label='Primary Time', enable=False)

limited_time = data('bogdanka.algo.rc.config_time_s', 
                    filter=filter('site', 'Szyb-2') and filter('config', 'Limited')
).sum().publish(label='Limited Time', enable=False)

balance = (primary_time / limited_time).publish(label='Balance Ratio')

# Alert if outside [0.9, 1.1]
when(balance < 0.9 or balance > 1.1, lasting='5m').publish(label='Balance Alert')
```

---

## SignalFlow Queries

### Query 1: Real-Time System Overview

```python
# Current Scenario with color coding
scenario = data('bogdanka.algo.ws.scenario', filter=filter('site', 'Szyb-2'))

# Map to scenario names
scenario.publish(label='Current Scenario (0-8)')

# Temperature correlation
temp = data('bogdanka.algo.ws.temperature_external', filter=filter('site', 'Szyb-2'))
temp.publish(label='External Temperature (°C)')
```

### Query 2: Heater Operating Time Balance

```python
# C1 heaters (N1-N4)
c1_time = data('bogdanka.algo.rn.heater_operating_time_s', 
               filter=filter('site', 'Szyb-2') and filter('heater', 'N1', 'N2', 'N3', 'N4'))

# Convert to hours
c1_hours = (c1_time / 3600).publish(label='C1 Operating Time (h)')

# Balance ratio
c1_max = c1_time.max(by=['site'])
c1_min = c1_time.min(by=['site'])
c1_balance = (c1_max / c1_min).publish(label='C1 Balance Ratio')

# Alert if > 1.5
when(c1_balance > 1.5, lasting='10m').publish(label='C1 Imbalance Alert')
```

### Query 3: Scenario Distribution (% time)

```python
# Time in each scenario (counter)
scenario_time = data('bogdanka.algo.ws.scenario_time_s', 
                     filter=filter('site', 'Szyb-2'),
                     rollup='rate')

# Total time
total_time = scenario_time.sum()

# Percentage per scenario
(scenario_time / total_time * 100).publish(label='Scenario Distribution (%)')
```

### Query 4: RC Rotation Frequency

```python
# RC rotations per day
rc_rotations = data('bogdanka.algo.rc.rotation_count', 
                    filter=filter('site', 'Szyb-2'),
                    rollup='sum')

# Rate (rotations per day)
rc_rate = rc_rotations.mean(over='1d').publish(label='RC Rotations/day')

# Expected: 1 rotation per 2 days = 0.5 rotations/day
const(0.5).publish(label='Expected Rate')
```

### Query 5: RN Rotation Rate by Line

```python
# RN rotations per line per day
rn_rotations = data('bogdanka.algo.rn.rotation_count', 
                    filter=filter('site', 'Szyb-2'),
                    rollup='sum').sum(by=['line'])

# Rate (rotations per day)
rn_rate = rn_rotations.mean(over='1d').publish(label='RN Rotations/day by Line')

# Expected: ~1 rotation/day per line (if scenario has reserve heaters)
const(1.0).publish(label='Expected Rate')
```

### Query 6: Heater Usage Percentage

```python
# Total operating time across all heaters
total_op_time = data('bogdanka.algo.rn.heater_operating_time_s', 
                     filter=filter('site', 'Szyb-2')).sum()

# Operating time per heater
heater_time = data('bogdanka.algo.rn.heater_operating_time_s', 
                   filter=filter('site', 'Szyb-2'))

# Percentage per heater
usage_pct = (heater_time / total_op_time * 100).publish(label='Heater Usage %')

# Expected: 12.5% per heater if balanced (8 heaters)
const(12.5).publish(label='Expected Usage %')
```

---

## Alerts

### Alert 1: Heater Imbalance (C1)

**Trigger:** `bogdanka.algo.rn.heater_operating_time_s` (C1) - max/min > 1.5

```python
c1_time = data('bogdanka.algo.rn.heater_operating_time_s', 
               filter=filter('site', 'Szyb-2') and filter('heater', 'N1', 'N2', 'N3', 'N4'))
c1_max = c1_time.max(by=['site'])
c1_min = c1_time.min(by=['site'])
c1_balance = c1_max / c1_min

detect(when(c1_balance > 1.5, lasting='30m')).publish('C1 Heater Imbalance')
```

**Severity:** Warning  
**Notification:** Email/Slack

### Alert 2: Missing RC Rotations

**Trigger:** `bogdanka.algo.rc.rotation_count` < expected (for given time period)

```python
# Expected: 1 rotation per 2 days
# For 7 days: expected = 3-4 rotations

rc_count = data('bogdanka.algo.rc.rotation_count', 
                filter=filter('site', 'Szyb-2'),
                rollup='sum').sum()

# Over last 7 days
rc_7d = rc_count.sum(over='7d')

detect(when(rc_7d < 3, lasting='1h')).publish('Missing RC Rotations')
```

**Severity:** Critical  
**Notification:** PagerDuty

### Alert 3: Primary/Limited Imbalance

**Trigger:** `bogdanka.algo.rc.config_time_s` - Primary/Limited ratio outside [0.9, 1.1]

```python
primary_time = data('bogdanka.algo.rc.config_time_s', 
                    filter=filter('site', 'Szyb-2') and filter('config', 'Primary')).sum()

limited_time = data('bogdanka.algo.rc.config_time_s', 
                    filter=filter('site', 'Szyb-2') and filter('config', 'Limited')).sum()

balance = primary_time / limited_time

detect(when(balance < 0.9 or balance > 1.1, lasting='1h')).publish('Config Imbalance')
```

**Severity:** Warning  
**Notification:** Email

### Alert 4: Scenario Stuck

**Trigger:** `bogdanka.algo.ws.scenario` - nie zmienia się przez >7 dni (w testach z transitions)

```python
scenario = data('bogdanka.algo.ws.scenario', filter=filter('site', 'Szyb-2'))

# Check if scenario hasn't changed in last 7 days
scenario_changes = data('bogdanka.algo.ws.scenario_changes', 
                       filter=filter('site', 'Szyb-2'),
                       rollup='sum').sum()

changes_7d = scenario_changes.sum(over='7d')

detect(when(changes_7d == 0, lasting='1h')).publish('Scenario Stuck')
```

**Severity:** Warning  
**Notification:** Email

### Alert 5: Temperature Sensor Failure

**Trigger:** `bogdanka.weather.external_temperature` - brak danych przez >10 min

```python
temp = data('bogdanka.weather.external_temperature', filter=filter('site', 'Szyb-2'))

detect(when(missing(temp), lasting='10m')).publish('Temperature Sensor Offline')
```

**Severity:** Critical  
**Notification:** PagerDuty

---

## Podsumowanie

### Metryki Aktualnie Emitowane (✅)

- ✅ `bogdanka.weather.*` (4 metryki)
- ✅ `bogdanka.algo.ws.*` (4 metryki)
- ✅ `bogdanka.algo.rc.*` (4 metryki)
- ✅ `bogdanka.algo.rn.*` (4 metryki)
  - ✅ `rotation_count` - liczba rotacji
  - ✅ `rotation_duration_s` - czas trwania rotacji
  - ✅ `heater_operating_time_s` - czas pracy nagrzewnic (**DODANE**)
  - ✅ `heater_state` - stan nagrzewnic (**DODANE**)

**Razem:** 16 metryk

### Dashboardy Do Stworzenia

1. ✅ **Dashboard 1: Przegląd Systemu** (4 wykresy) - **gotowe, wszystkie metryki dostępne**
2. ✅ **Dashboard 2: Status Nagrzewnic** (7 wykresów) - **gotowe, wszystkie metryki dostępne**
3. ✅ **Dashboard 3: Status Ciągów** (6 wykresów) - **gotowe, wszystkie metryki dostępne**
4. ✅ **Dashboard 4: Analiza Rotacji** (5 wykresów) - **gotowe, wszystkie metryki dostępne**
5. ✅ **Dashboard 5: Walidacja Testów** (16 wykresów) - **gotowe, wszystkie metryki dostępne**

### Alerty Do Skonfigurowania

1. ✅ **Heater Imbalance** - dostępne (`heater_operating_time_s`)
2. ✅ **Missing RC Rotations** - dostępne
3. ✅ **Primary/Limited Imbalance** - dostępne
4. ✅ **Scenario Stuck** - dostępne
5. ✅ **Temperature Sensor Failure** - dostępne

---

## Następne Kroki

### ✅ Faza 1: Dodanie Brakujących Metryk - ZAKOŃCZONA

Metryki zostały dodane w następujących plikach:

1. **`src/simulation/algo/metrics.py`**:
   - Dodano pole `algorithm_rn: AlgorithmRN` do dataclass `AlgoMetrics`
   - Dodano gauge `heater_operating_time_s` (linia 119-124)
   - Dodano gauge `heater_state` (linia 127-131)
   - Dodano callback `_observe_heater_operating_time()` (linia 159-171)
   - Dodano callback `_observe_heater_state()` (linia 173-187)

2. **`src/simulation/algo_service.py`**:
   - Przeniesiono inicjalizację `AlgoMetrics` po `AlgorithmRN` (linia 88-95)
   - Przekazano `algorithm_rn=self.algorithm_rn` do konstruktora (linia 94)

**Weryfikacja:**
- ✅ Moduł importuje się poprawnie
- ✅ Wszystkie testy jednostkowe przechodzą (40 testów)

### Faza 2: Stworzenie Dashboardów w Splunk

1. Zaloguj się do Splunk Observability Cloud
2. Przejdź do **Dashboards** → **New Dashboard**
3. Stwórz 5 dashboardów zgodnie z opisem powyżej
4. Użyj SignalFlow queries z sekcji [SignalFlow Queries](#signalflow-queries)

**Priorytet dashboardów:**
- **HIGH:** Dashboard 1 (Przegląd) i Dashboard 2 (Status Nagrzewnic)
- **MEDIUM:** Dashboard 3 (Status Ciągów) i Dashboard 5 (Walidacja)
- **LOW:** Dashboard 4 (Analiza Rotacji)

### Faza 3: Konfiguracja Alertów

1. Przejdź do **Alerts** → **New Detector**
2. Stwórz 5 alertów zgodnie z opisem w sekcji [Alerts](#alerts)
3. Skonfiguruj notification channels (Email, Slack, PagerDuty)

**Priorytet alertów:**
- **CRITICAL:** Alert 2 (Missing RC Rotations), Alert 5 (Temperature Sensor)
- **WARNING:** Alert 1 (Heater Imbalance), Alert 3 (Config Imbalance), Alert 4 (Scenario Stuck)

### Faza 4: Walidacja

1. Uruchom testy z `run_test_scenarios.py`
   ```bash
   cd src/simulation
   uv run python run_test_scenarios.py --profile profile_1_s3_baseline
   ```

2. Otwórz Splunk Observability i sprawdź czy metryki płyną
   - Przejdź do **Metrics** → **Metric Finder**
   - Wyszukaj `bogdanka.algo.rn.heater_operating_time_s`
   - Sprawdź czy widoczne są wszystkie 8 nagrzewnic (N1-N8)

3. Zweryfikuj czy wartości w Splunk odpowiadają `expected_results`
   - Porównaj wartości z Dashboard 5 z wartościami z testów

4. Sprawdź czy alerty triggering są correct
   - Przetestuj każdy alert poprzez symulację warunków

### Faza 5: Dokumentacja dla Operatorów (opcjonalne)

Stwórz dokumentację dla operatorów systemu:
- **Runbook:** Co robić gdy alert się uruchomi
- **Troubleshooting Guide:** Typowe problemy i rozwiązania
- **Dashboard Guide:** Jak interpretować wykresy

---

## Referencje

- **Dokumentacja symulacji:** `src/simulation/docs/simulation.md`
- **Test profiles:** `src/simulation/scenarios/test_profiles.yaml`
- **Display implementation:** `src/simulation/algo/display.py`
- **Metrics implementation:** `src/simulation/algo/metrics.py`
- **Telemetry config:** `src/simulation/common/telemetry.py`

---

**Koniec dokumentu**

