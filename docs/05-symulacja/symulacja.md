# Wyniki Symulacji - System BOGDANKA Szyb 2

**Dokument zawierający wyniki testów symulacyjnych algorytmów sterowania**

_Plik ten jest częścią dokumentacji systemu sterowania nagrzewnicami BOGDANKA Szyb 2._

[← Powrót do dokumentacji głównej](../start.md)

---

**Data wykonania testów:** 29 Listopad 2025  
**Status:** Testy zakończone pomyślnie

Nagranie z symulacji: [demo](https://drive.google.com/file/d/1bWcLUXPNtjgQYMiPeucmX759RQFLLyi5/view?usp=sharing)

---

## Spis Treści

1. [Wprowadzenie](#wprowadzenie)
2. [Metodologia Testowania](#metodologia-testowania)
3. [Wyniki Testów](#wyniki-testów)
4. [Wnioski](#wnioski)

---

## Wprowadzenie

Niniejszy dokument przedstawia wyniki symulacji systemu sterowania nagrzewnicami w szybie kopalnianym BOGDANKA Szyb 2. Celem symulacji było zweryfikowanie poprawności działania trzech współpracujących algorytmów:

- **Algorytm WS** - Automatyczny wybór scenariusza pracy
- **Algorytm RC** - Rotacja układów pracy ciągów wentylacyjnych
- **Algorytm RN** - Rotacja nagrzewnic w obrębie ciągu

### Cele Symulacji

1. **Weryfikacja logiki algorytmów** - sprawdzenie poprawności implementacji zgodnie z dokumentacją ([algorytmy.md](../03-algorytmy/algorytmy.md))
2. **Analiza równomierności zużycia** - ocena efektywności mechanizmów rotacji nagrzewnic i ciągów
3. **Wykrycie potencjalnych problemów** - identyfikacja kolizji, nieoczekiwanych zachowań, błędów logicznych

### Zakres Testów

Wykonano 5 testów symulacyjnych:

- Scenariusz S1 (minimalne ogrzewanie, 24h)
- Scenariusz S3 (3 nagrzewnice, rotacja RN, 48h)
- Scenariusz S4 (pełna moc jednego ciągu, 48h)
- Scenariusz S6 (oba ciągi aktywne, 48h)
- Przejścia S1→S3→S6→S3 (96h)

---

## Metodologia Testowania

### Platforma Symulacyjna

Symulacja została wykonana w środowisku Python z wykorzystaniem:
- **Akceleracja czasu:** 1000x (1 dzień symulacji = ~1.4 minuty rzeczywistych)
- **Interwał próbkowania:** 3 sekundy (czasu symulowanego)
- **Architektura:** Trzy współbieżne algorytmy + symulowany serwis pogodowy

### Parametry Algorytmów

Wszystkie testy zostały wykonane z następującymi parametrami:

```yaml
Algorytm WS (wybór scenariusza):
  - Monitoring temperatury: co 10s
  - Stabilizacja scenariusza: 60s
  - Histereza: 1.0°C

Algorytm RC (rotacja ciągów):
  - Okres rotacji: 4 godziny

Algorytm RN (rotacja nagrzewnic):
  - Okres rotacji: 1 godzina
```

### Metryki Jakości

System mierzy następujące metryki:

1. **Balans nagrzewnic** - stosunek czasu pracy najdłużej pracującej do najkrótszej nagrzewnicy w ciągu
   ```
   balance_ratio = max(operating_time) / min(operating_time)
   ```
   - Ideał: 1.0 (wszystkie nagrzewnice pracują dokładnie tyle samo)
   - Akceptowalne: < 1.3-1.5
   - Krytyczne: > 1.5

2. **Balans ciągów RC** - stosunek czasu pracy ciągu 1 do ciągu 2
   ```
   rc_balance_ratio = time_in_primary / time_in_limited
   ```
   - Ideał: 1.0 (oba ciągi pracują tyle samo)
   - Akceptowalne: 0.9 - 1.1

3. **Liczba rotacji** - ilość wykonanych zmian układów i nagrzewnic
4. **Kolizje algorytmów** - przypadki gdy RN i RC próbowały działać jednocześnie

---

## Wyniki Testów

### Podsumowanie Zbiorcze

**Status:** **5/5 testów zakończonych pomyślnie (100%)**

| Test ID | Nazwa | Czas sym. | Status | Balans C1 | Balans C2 | RC Balance | Rotacje RN |
|---------|-------|-----------|--------|-----------|-----------|------------|------------|
| TEST_S1 | S1 minimalne ogrzewanie | 24h | ✅ PASSED | **1.036** | **1.018** | 0.991 | 18 |
| TEST_S3 | S3 stałe warunki | 48h | ✅ PASSED | **1.002** | **1.004** | 0.997 | 36 |
| TEST_S4 | S4 pełna moc | 48h | ✅ PASSED | **1.000** | **1.000** | 1.000 | 0 |
| TEST_S6 | S6 oba ciągi | 48h | ✅ PASSED | **1.000** | **1.020** | N/A* | 47 |
| TEST_TRANSITIONS | S1→S3→S6→S3 | 96h | ✅ PASSED | **1.003** | **1.006** | 1.661** | 77 |

**Legenda:**
- Balans C1/C2: stosunek max/min czasu pracy nagrzewnic w ciągu (ideał: 1.0)
- RC Balance: stosunek czasu pracy C1/C2 (ideał: 1.0)
- \* W S6 nie ma rotacji RC (oba ciągi pracują jednocześnie)
- \** W TEST_TRANSITIONS balans RC = 1.662 jest poprawny (więcej czasu w S6 z obu ciągów)

**Kluczowe obserwacje:**
1. **Wszystkie testy PASSED** - 100% sukcesu
2. **Balans nagrzewnic doskonały** - wszystkie wyniki 1.000-1.029 (znacznie lepiej niż próg 1.3-1.5)
3. **Balans ciągów bardzo dobry** - w testach stałych (S1, S3, S4) praktycznie idealny (~1.0)
4. **Brak rotacji w S4** - poprawne zachowanie (wszystkie 4 nagrzewnice pracują, brak rezerwowej)
5. **Przejścia scenariuszowe działają** - TEST_TRANSITIONS potwierdza poprawność algorytmu WS

---

### TEST_S1 - S1 Minimalne Ogrzewanie

**Czas symulacji:** 24 godziny  
**Temperatura:** 0.0°C (stała)  
**Scenariusz:** S1 (99.93% czasu)

**Wyniki:**

| Metryka | Wartość | Status |
|---------|---------|--------|
| Balans C1 (N1-N4) | **1.036** | ✅ PASS |
| Balans C2 (N5-N8) | **1.018** | ✅ PASS |
| Balans RC (ciągi) | **0.991** | ✅ PASS |
| Rotacje RC | 6 | ✅ |
| Rotacje RN | 18 | ✅ |

**Rozkład czasu pracy nagrzewnic:**
- **Ciąg C1:** N1=12.57%, N2=12.45%, N3=12.58%, N4=12.14% (różnica max-min: 0.44%)
- **Ciąg C2:** N5=12.63%, N6=12.50%, N7=12.64%, N8=12.42% (różnica max-min: 0.22%)

**Wnioski:**
- Scenariusz S1 z 1 nagrzewnicą pokazuje doskonałe działanie rotacji
- System równomiernie wykorzystał wszystkie 8 nagrzewnic (każda ~12.5% czasu)
- Rotacja ciągów zapewniła idealny balans C1 vs C2 (różnica 0.9%)

---

### TEST_S3 - S3 Rotacja RN w Jednym Ciągu

**Czas symulacji:** 48 godzin  
**Temperatura:** -5.0°C (stała)  
**Scenariusz:** S3 (99.96% czasu)

**Wyniki:**

| Metryka | Wartość | Status |
|---------|---------|--------|
| Balans C1 (N1-N4) | **1.002** | ✅ PASS |
| Balans C2 (N5-N8) | **1.004** | ✅ PASS |
| Balans RC (ciągi) | **0.997** | ✅ PASS |
| Rotacje RC | 11 | ✅ |
| Rotacje RN | 36 | ✅ |

**Rozkład czasu pracy nagrzewnic:**
- **Ciąg C1:** N1=37.49%, N2=37.42%, N3=37.40%, N4=37.42% (różnica max-min: 0.09%)
- **Ciąg C2:** N5=37.63%, N6=37.47%, N7=37.56%, N8=37.49% (różnica max-min: 0.16%)

**Wnioski:**
- Scenariusz S3 (3 nagrzewnice) pokazuje doskonałe działanie algorytmu RN
- Rotacja nagrzewnic zapewniła niemal perfekcyjne wyrównanie (różnica < 0.2%)
- Balans RC idealny (0.997) - oba ciągi pracowały praktycznie tyle samo

---

### TEST_S4 - S4 Pełna Moc Jednego Ciągu

**Czas symulacji:** 48 godzin  
**Temperatura:** -9.0°C (stała)  
**Scenariusz:** S4 (99.96% czasu)

**Wyniki:**

| Metryka | Wartość | Status |
|---------|---------|--------|
| Balans C1 (N1-N4) | **1.000** | ✅ PASS |
| Balans C2 (N5-N8) | **1.000** | ✅ PASS |
| Balans RC (ciągi) | **1.000** | ✅ PASS |
| Rotacje RC | 11 | ✅ |
| Rotacje RN | **0** | ✅ POPRAWNE |

**Rozkład czasu pracy nagrzewnic:**
- **Ciąg C1:** Wszystkie N1-N4 = 49.97% (identyczny czas pracy)
- **Ciąg C2:** Wszystkie N5-N8 = 49.98% (identyczny czas pracy)

**Wnioski:**
- Scenariusz S4 potwierdza **poprawne wyłączenie algorytmu RN**
- Wszystkie 4 nagrzewnice ciągu pracują jednocześnie (brak rezerwowej)
- Algorytm RN nie próbuje rotować gdy nie ma nagrzewnic rezerwowych
- Balans = 1.000 (idealnie równe czasy pracy)

---

### TEST_S6 - S6 Oba Ciągi Aktywne

**Czas symulacji:** 48 godzin  
**Temperatura:** -16.0°C (stała)  
**Scenariusz:** S6 (99.96% czasu)

**Wyniki:**

| Metryka | Wartość | Status |
|---------|---------|--------|
| Balans C1 (N1-N4) | **1.000** | ✅ PASS |
| Balans C2 (N5-N8) | **1.020** | ✅ PASS |
| Balans RC (ciągi) | N/A | N/A (oba ciągi zawsze aktywne) |
| Rotacje RC | **0** | ✅ POPRAWNE |
| Rotacje RN | 47 | ✅ (tylko w C2) |

**Rozkład czasu pracy nagrzewnic:**
- **Ciąg C1:** Wszystkie N1-N4 = 99.95% (brak rotacji, wszystkie potrzebne)
- **Ciąg C2:** N5=49.47%, N6=50.48%, N7=50.48%, N8=49.47% (różnica max-min: 1.01%)

**Wnioski:**
- W S6 algorytm RC nie działa (oba ciągi pracują jednocześnie, układ zawsze Podstawowy)
- Algorytm RN działa tylko w C2 gdzie są nagrzewnice rezerwowe (2 z 4 pracują)
- C1 pracuje na pełnej mocy bez rotacji (wszystkie N1-N4 potrzebne)
- Asymetria obciążenia między ciągami jest naturalna i poprawna

---

### TEST_SCENARIO_TRANSITIONS - Przejścia Scenariuszowe

**Czas symulacji:** 96 godzin (4 dni)  
**Profil temperatury:** Stepped - S1→S3→S6→S3

| Dzień | Temperatura | Scenariusz |
|-------|-------------|------------|
| 0-1 | 0.0°C | S1 (24h) |
| 1-2 | -5.0°C | S3 (24h) |
| 2-3 | -16.0°C | S6 (24h) |
| 3-4 | -5.0°C | S3 (24h) |

**Wyniki:**

| Metryka | Wartość | Status |
|---------|---------|--------|
| Balans C1 (N1-N4) | **1.003** | ✅ PASS |
| Balans C2 (N5-N8) | **1.006** | ✅ PASS |
| Balans RC (ciągi) | 1.661* | ✅ (poprawne) |
| Przejścia scenariuszowe | 7 | ✅ |
| Rotacje RC | 18 | ✅ |
| Rotacje RN | 77 | ✅ |

\* Balans RC = 1.661 jest poprawny - C1 pracował więcej z powodu więcej czasu w S6 gdzie C1 na MAX

**Rozkład scenariuszy:**
- S1: 23.99h (24.99%)
- S2: 0.09h (0.09%) - przejście
- S3: 47.88h (49.88%) - łącznie 2 dni
- S4: 0.02h (0.02%) - przejście
- S5: 0.02h (0.02%) - przejście
- S6: 23.99h (24.99%)

**Rozkład czasu pracy nagrzewnic:**
- **Ciąg C1:** N1=46.85%, N2=46.84%, N3=46.79%, N4=46.72% (różnica max-min: 0.13%)
- **Ciąg C2:** N5=34.31%, N6=34.52%, N7=34.46%, N8=34.32% (różnica max-min: 0.21%)

**Wnioski:**
- Test potwierdza poprawność algorytmu WS w dynamicznych warunkach
- Wszystkie 7 przejść scenariuszowych wykonane prawidłowo
- Balans nagrzewnic doskonały mimo zmian scenariuszy
- Asymetria C1 vs C2 wynika z więcej czasu w S6 (C1 pracuje 100%, C2 ~50%)

---

## Wnioski

### Potwierdzenie Poprawności Algorytmów

**Algorytm WS (Wybór Scenariusza):**
- Poprawnie wybiera scenariusz na podstawie temperatury zewnętrznej
- Prawidłowo wykonuje przejścia między scenariuszami (TEST_TRANSITIONS: 7 przejść)
- Histereza działa poprawnie (zapobiega częstym przełączeniom)

**Algorytm RC (Rotacja Ciągów):**
- Zapewnia równomierne wykorzystanie ciągów C1 i C2
- Balans ciągów w testach stałych: 0.994-1.000 (praktycznie idealny)
- Poprawnie wyłącza się w scenariuszach gdzie oba ciągi pracują (S6)
- Brak konfliktów z algorytmem RN (0 kolizji we wszystkich testach)

**Algorytm RN (Rotacja Nagrzewnic):**
- Zapewnia doskonały balans nagrzewnic: 1.000-1.029 we wszystkich testach
- Różnice czasów pracy nagrzewnic < 1.2% (wyjątkowo dobry wynik)
- Poprawnie wyłącza się gdy brak nagrzewnic rezerwowych (TEST_S4: 0 rotacji)
- Adaptuje się do różnych scenariuszy (S1: 1 nagrzewnica, S3: 3 nagrzewnice, S6: 2+4 nagrzewnice)

### Statystyki Łączne

**Łączny czas testów:** 264 godziny (11 dni) symulacji  
**Łączny czas rzeczywisty:** ~16 minut  

| Metryka | Wartość |
|---------|---------|
| Przejścia scenariuszowe (WS) | 11 |
| Rotacje ciągów (RC) | 46 |
| Rotacje nagrzewnic (RN) | 178 |

### Kluczowe Osiągnięcia

1. **100% testów zakończonych sukcesem** - wszystkie algorytmy działają zgodnie z dokumentacją
2. **Doskonała równomierność zużycia nagrzewnic** - balans 1.000-1.036 (próg 1.3-1.5)
3. **Idealny balans ciągów** - stosunek 0.991-1.000 w scenariuszach stałych
5. **Poprawna logika warunkowa** - algorytmy wyłączają się gdy nie są potrzebne
6. **Odporność na zmiany** - TEST_TRANSITIONS potwierdza stabilność w dynamicznych warunkach

### Obserwacje

1. **Parametry rotacji są agresywne:**
   - OKRES_ROTACJI_NAGRZEWNIC = 1h (bardzo często)
   - OKRES_ROTACJI_UKŁADÓW = 4h (bardzo często)
   - Zapewniają doskonały balans, ale mogą przyspieszyć zużycie zaworów i przepustnic, ustawienia do symulacji
   - W rzeczywistej instalacji zaleca się dłuższe okresy

2. **Asymetria na końcu symulacji:**
   - Nagrzewnice aktywne na koniec testu mają nieznacznie mniej czasu (-0.5% do -2.7%)
   - Efekt graniczny - testy zakończyły się podczas ich pracy
   - W testach długoterminowych (30 dni) efekt będzie pomijalny

3. **Balans RC w TEST_TRANSITIONS = 1.661:**
   - Wartość powyżej standardowego progu 0.9-1.1
   - To **NIE jest błąd** - naturalna konsekwencja więcej czasu w S6
   - W S6 oba ciągi pracują, ale C1 na MAX (100%), C2 częściowo (~50%)

---

## Załączniki

### Szczegółowe Wyniki

**Lokalizacja plików:**
- Katalog wyników: `src/simulation/scenarios/test_results/`
- Katalog logów: `src/simulation/logs/`

| Test | Plik wyników | Plik logu |
|------|--------------|-----------|
| Wszystkie | test_results_20251129_122602.yaml | Oddzielne dla każdego profilu |

### Parametry Algorytmów

**Parametry WS (Wybór Scenariusza):**
```yaml
CYKL_MONITORINGU_TEMP: 10s
CZAS_STABILIZACJI_SCENARIUSZA: 60s
HISTEREZA: 1.0°C
```

**Parametry RC (Rotacja Ciągów):**
```yaml
OKRES_ROTACJI_UKŁADÓW: 4h (14400s)
HISTEREZA_CZASOWA: 300s
CYKL_PĘTLI_ALGORYTMÓW: 60s
```

**Parametry RN (Rotacja Nagrzewnic):**
```yaml
OKRES_ROTACJI_NAGRZEWNIC: 1h (3600s)
MIN_DELTA_CZASU: 60s
ODSTĘP_PO_ZMIANIE_UKŁADU: 3600s (1h)
ODSTĘP_MIĘDZY_ROTACJAMI: 900s (15min)
```

### Środowisko Testowe

**Platforma:**
- OS: macOS 25.0.0
- Python: 3.x (venv)
- Symulator: custom algo_service.py

**Komponenty:**
- Weather Service
- Algo Service: Main control loop
- Display: Terminal UI
- Metrics: OpenTelemetry

---

## Powiązane Dokumenty

- **[Algorytmy sterowania](../03-algorytmy/algorytmy.md)** - szczegółowy opis algorytmów WS, RC, RN
- **[Pseudokod algorytmów](../03-algorytmy/algo_pseudokod.md)** - implementacja algorytmów

---

**Ostatnia aktualizacja:** 29 Listopad 2025  
