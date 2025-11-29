# Uruchamianie Testów Symulacyjnych

Ten katalog zawiera profile testowe oraz narzędzia do uruchamiania testów symulacyjnych algorytmów sterowania.

## Struktura

- **`test_profiles.yaml`** - definicje profili testowych
- **`test_results/`** - katalog z wynikami testów (pliki YAML)
- **`../run_test_scenarios.py`** - główny skrypt uruchamiający testy
- **`generate_report.py`** - generator raportów markdown z wyników

## Szybki Start

### 1. Uruchomienie Wszystkich Testów

```bash
cd src/simulation

# Wszystkie testy z domyślnymi parametrami
uv run python run_test_scenarios.py
```

### 2. Szybki Test (Smoke Test)

```bash
cd src/simulation

# Wszystkie testy z 1 dniem symulacji i 10000x akceleracją
uv run python run_test_scenarios.py --smoke
```

### 3. Uruchomienie Wybranych Profili

```bash
cd src/simulation

# Pojedynczy profil (użyj ID lub nazwy profilu z test_profiles.yaml)
uv run python run_test_scenarios.py --profiles profile_s1

# Wiele profili
uv run python run_test_scenarios.py --profiles profile_s1 profile_s3 profile_s4
```

### 4. Testy Równoległe

```bash
cd src/simulation

# 4 testy jednocześnie
uv run python run_test_scenarios.py --parallel 4

# Smoke test z maksymalną równoległością
uv run python run_test_scenarios.py --smoke --parallel 7
```

## Parametry `run_test_scenarios.py`

### Opcje Podstawowe

| Parametr | Opis | Przykład |
|----------|------|----------|
| `--smoke` | Tryb szybkich testów (1 dzień, 10000x akceleracja) | `--smoke` |
| `--profiles` | Lista profili do uruchomienia | `--profiles profile_s1 profile_s3` |
| `--days` | Nadpisz czas trwania (w dniach symulacji) | `--days 2` |
| `--acceleration` | Nadpisz akcelerację | `--acceleration 5000` |
| `--parallel N` | Uruchom N testów jednocześnie | `--parallel 4` |

### Przykłady Użycia

```bash
# Test pojedynczego profilu z niestandardowymi parametrami
uv run python run_test_scenarios.py --profiles profile_s3 --days 10 --acceleration 2000

# Szybki test wybranych profili
uv run python run_test_scenarios.py --smoke --profiles profile_s1 profile_s3

# Wszystkie testy równolegle z niestandardową akceleracją
uv run python run_test_scenarios.py --parallel 5 --acceleration 1000
```

## Wyniki Testów

### Lokalizacja

Wyniki są zapisywane w katalogu `test_results/`:

- `test_results_YYYYMMDD_HHMMSS.yaml` - surowe dane w formacie YAML

### Format YAML

Plik wynikowy zawiera:
- Metadane testu (timestamp, liczba testów, status)
- Lista wyników dla każdego profilu:
  - Status: PASSED / FAILED / ERROR
  - Czas wykonania
  - Rzeczywiste metryki (simulation_time, rotacje RC/RN, balans, czasy pracy nagrzewnic)
  - Wyniki walidacji (porównanie z oczekiwaniami)

## Generowanie Raportów Markdown

### Automatyczne Generowanie

Raporty markdown są generowane automatycznie podczas uruchamiania testów.

### Ręczne Generowanie

Możesz wygenerować raport z istniejącego pliku YAML:

```bash
cd src/simulation

# Wygeneruj raport z konkretnego pliku
uv run python scenarios/generate_report.py scenarios/test_results/test_results_20251129_122602.yaml
```

Raport zostanie zapisany jako `test_results_YYYYMMDD_HHMMSS_report.md` w tym samym katalogu.

### Zawartość Raportu

Raport markdown zawiera:
- Podsumowanie wykonawcze (liczba testów, sukces/porażka)
- Szczegółowe wyniki dla każdego profilu
- Tabele walidacji (oczekiwane vs rzeczywiste wartości)
- Szczegółowe metryki (w sekcjach rozwijanych)
- Rekomendacje dalszych kroków

## Tryby Pracy

### 1. Tryb Sekwencyjny (Domyślny)

```bash
uv run python run_test_scenarios.py
```

- Testy wykonywane jeden po drugim
- Wyświetlany jest pasek postępu
- Logowanie do konsoli i plików
- **Dla pojedynczego testu:** włączony display (wizualizacja czasu rzeczywistego)

### 2. Tryb Równoległy

```bash
uv run python run_test_scenarios.py --parallel 4
```

- Testy wykonywane jednocześnie (wiele wątków)
- Każdy test na osobnym porcie (8080, 8081, 8082...)
- Logowanie tylko do plików (osobny plik na test)
- Display wyłączony (konflikt przy równoległym wykonywaniu)
- Znaczne przyspieszenie (np. 5 minut → 1.5 minuty dla 4 workerów)

## Konfiguracja Testów

### Definicje Profili

Profile testowe są zdefiniowane w pliku **`test_profiles.yaml`**:

```yaml
test_profiles:
  - id: profile_id
    name: TEST_NAME
    priority: HIGH | MEDIUM
    description: "Opis testu"
    duration_days: 30
    acceleration: 1000  # opcjonalne (domyślnie z config.yaml)
    profile_type: constant | stepped
    temperature_c: -5.0  # dla constant
    steps: [...]  # dla stepped
    expected_results:
      rc_rotations: {min: 14, max: 16}
      heater_balance_c1: {max: 1.5}
      # ... inne metryki
```

### Parametry Akceleracji

**Rekomendowane wartości:**

| Akceleracja | Czas 1 dnia | Zastosowanie |
|-------------|-------------|--------------|
| **100x** | ~14 min | Szczegółowa diagnostyka |
| **1000x** | ~1.5 min | Development, standardowe testy |
| **10000x** | ~10 s | Smoke tests (może być niestabilne) |

## Logowanie

### Pliki Logów

Każdy test generuje osobny plik logu:

```
logs/test_profile_id.log
```

### Poziomy Logowania

W plikach logów znajdziesz:
- Zdarzenia algorytmów (rotacje, zmiany scenariuszy)
- Ostrzeżenia i błędy
- Szczegółową chronologię symulacji

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

# Lub użyj innego portu przez edycję config.yaml
```

### Problem: Test trwa zbyt długo

```bash
# Użyj większej akceleracji
uv run python run_test_scenarios.py --acceleration 5000

# Lub skróć czas symulacji
uv run python run_test_scenarios.py --days 1

# Lub użyj trybu smoke
uv run python run_test_scenarios.py --smoke
```

### Problem: Testy kończą się błędem

1. Sprawdź logi w `logs/test_profile_id.log`
2. Sprawdź konfigurację w `config.yaml`
3. Sprawdź definicje profili w `test_profiles.yaml`
4. Upewnij się, że serwisy nie są już uruchomione

### Problem: Niestabilne wyniki przy wysokiej akceleracji

```bash
# Zmniejsz akcelerację do stabilnej wartości
uv run python run_test_scenarios.py --acceleration 1000

# Lub użyj trybu równoległego z niższą akceleracją
uv run python run_test_scenarios.py --parallel 4 --acceleration 1000
```

## Pomoc

### Wyświetl pomoc

```bash
cd src/simulation
uv run python run_test_scenarios.py --help
```

### Dokumentacja

- **Pseudokod algorytmów:** `docs/03-algorytmy/algo_pseudokod.md`
- **Dokumentacja wyników:** `docs/05-symulacja/symulacja.md`
- **Konfiguracja systemu:** `config.yaml`

## Workflow Testowy

### 1. Development

```bash
# Szybki test pojedynczego profilu z display
uv run python run_test_scenarios.py --profiles profile_s1 --days 1
```

### 2. Weryfikacja Zmian

```bash
# Smoke test wszystkich profili
uv run python run_test_scenarios.py --smoke --parallel 7
```

### 3. Pełna Walidacja

```bash
# Wszystkie testy z pełnym czasem
uv run python run_test_scenarios.py --parallel 4
```

### 4. Analiza Wyników

```bash
# Wygeneruj raport markdown
uv run python scenarios/generate_report.py scenarios/test_results/test_results_YYYYMMDD_HHMMSS.yaml

# Przejrzyj wyniki
cat scenarios/test_results/test_results_YYYYMMDD_HHMMSS_report.md
```

## Uwagi Końcowe

- **Parametry algorytmów** są w czasie SYMULACJI, nie rzeczywistym
- System automatycznie skaluje czasy przez akcelerację
- Display działa tylko dla pojedynczego testu (tryb sekwencyjny)
- Tryb równoległy znacznie przyspiesza wykonanie testów
- Zawsze sprawdzaj logi przy niepowodzeniu testów
