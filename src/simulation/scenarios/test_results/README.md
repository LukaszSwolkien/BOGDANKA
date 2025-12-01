# Test Results - BOGDANKA Szyb 2

Ten katalog zawiera wyniki testów symulacyjnych algorytmów sterowania (WS, RC, RN).

## Aktualne Wyniki

**Data ostatnich testów:** 29 Listopad 2025  
**Plik wyników:** `test_results_20251129_122602.yaml`  
**Status:** ✅ **5/5 testów PASSED (100% sukcesu)**

### Wykonane Testy

| Test ID | Scenariusz | Czas sym. | Balans C1 | Balans C2 | RC Balance | Status |
|---------|------------|-----------|-----------|-----------|------------|--------|
| TEST_S1 | S1 (1 nagrzewnica) | 24h | 1.036 | 1.018 | 0.991 | ✅ PASSED |
| TEST_S3 | S3 (3 nagrzewnice) | 48h | 1.002 | 1.004 | 0.997 | ✅ PASSED |
| TEST_S4 | S4 (4 nagrzewnice) | 48h | 1.000 | 1.000 | 1.000 | ✅ PASSED |
| TEST_S6 | S6 (oba ciągi) | 48h | 1.000 | 1.020 | N/A | ✅ PASSED |
| TEST_TRANSITIONS | S1→S3→S6→S3 | 96h | 1.003 | 1.006 | 1.661 | ✅ PASSED |

**Łączna statystyka:**
- Łączny czas symulacji: 264h (11 dni)
- Rotacje ciągów (RC): 46
- Rotacje nagrzewnic (RN): 178
- Kolizje RC↔RN: **0**

## Format Plików

### YAML Files

Pliki `test_results_YYYYMMDD_HHMMSS.yaml` zawierają surowe dane:

```yaml
timestamp: '2025-11-29T12:26:02'
total_tests: 5
passed: 5
failed: 0
results:
  - profile_id: profile_s1
    status: PASSED
    actual_metrics:
      heater_operating_times: {...}
      rc_balance_ratio: 0.991
      rn_heater_rotations: 18
    validation_results: [...]
```

## Interpretacja Wyników

### Metryki Kluczowe

1. **Balans nagrzewnic (heater_balance_c1/c2)**
   - Stosunek: max(czas_pracy) / min(czas_pracy) dla nagrzewnic w ciągu
   - Ideał: 1.0 (wszystkie nagrzewnice pracują tyle samo)
   - Próg akceptowalny: < 1.3-1.5
   - **Wynik:** 1.000-1.036 ✅ (doskonały)

2. **Balans ciągów (rc_balance_ratio)**
   - Stosunek: time_in_primary / time_in_limited
   - Ideał: 1.0 (oba ciągi pracują tyle samo)
   - Próg akceptowalny: 0.9-1.1
   - **Wynik:** 0.991-1.000 ✅ (idealny)

3. **Rotacje nagrzewnic (rn_heater_rotations)**
   - Liczba wykonanych rotacji nagrzewnic
   - Zależy od: OKRES_ROTACJI_NAGRZEWNIC, czasu trwania testu
   - **Wynik:** 0-77 rotacji (zgodnie z oczekiwaniami)

4. **Rotacje ciągów (rc_line_changes)**
   - Liczba zmian układu Podstawowy↔Ograniczony
   - Zależy od: OKRES_ROTACJI_UKŁADÓW, czasu trwania testu
   - **Wynik:** 0-18 rotacji (zgodnie z oczekiwaniami)

### Kryteria Sukcesu

✅ Test uznawany za **PASSED** gdy:
- Balans nagrzewnic < 1.5 (dla każdego ciągu osobno)
- Balans ciągów w zakresie 0.9-1.1 (dla scenariuszy stałych)
- Brak kolizji RC↔RN (mutex działa poprawnie)
- Liczba rotacji zgodna z oczekiwaniami (±10%)

## Konfiguracja Testów

Testy zostały wykonane z następującymi parametrami:

```yaml
Akceleracja: 1000x
Algorytm RC:
  - Okres rotacji układów: 4h (14400s)
  - Cykl pętli: 60s

Algorytm RN:
  - Okres rotacji nagrzewnic: 1h (3600s)
  - Min. delta czasu: 60s
  - Cykl pętli: 60s
```

## Historia Testów

| Data | Pliki | Testy | Passed | Failed | Uwagi |
|------|-------|-------|--------|--------|-------|
| 2025-11-29 12:26 | test_results_20251129_122602.yaml | 5 | 5 | 0 | Testy po zmianach w implementacji ✅ |

## Szczegółowa Dokumentacja

Pełna analiza wyników testów znajduje się w:

📊 **[docs/05-symulacja/symulacja.md](../../../../docs/05-symulacja/symulacja.md)**

Zawiera:
- Szczegółowe opisy każdego testu
- Analizę mechanizmów rotacji
- Wnioski i rekomendacje
- Koordynację algorytmów RC↔RN

## Uruchomienie Testów

Aby wykonać testy ponownie:

```bash
cd src/simulation

# Wszystkie testy
uv run python run_test_scenarios.py --profiles profile_s1 profile_s3 profile_s4 profile_s6 profile_s1363

# Pojedynczy test
uv run python run_test_scenarios.py --profiles profile_s1
```

## Troubleshooting

### Niezgodne wyniki

1. Sprawdź parametry w `config.yaml`
2. Porównaj z oczekiwaniami w `test_profiles.yaml`
3. Przejrzyj logi w `logs/`

### Regeneracja raportu

```bash
# Wygeneruj raport markdown z pliku YAML
uv run python scenarios/generate_report.py scenarios/test_results/test_results_20251129_122602.yaml
```

## Kontakt

W razie pytań dotyczących wyników testów:
- Sprawdź dokumentację: `docs/05-symulacja/symulacja.md`
- Sprawdź pseudokod: `docs/03-algorytmy/algo_pseudokod.md`
- Sprawdź konfigurację: `src/simulation/config.yaml`



