# Algorytmy Sterowania - System BOGDANKA Szyb 2

**Dokument szczegółowy zawierający algorytmy automatycznego sterowania i rotacji**

_Plik ten jest częścią dokumentacji systemu sterowania nagrzewnicami BOGDANKA Szyb 2._

[← Powrót do dokumentacji głównej](../start.md)

---

**Ostatnia aktualizacja:** 25 Listopad 2025  
**Status:** Algorytmy do implementacji w PLC  
**Zatwierdzenie:** Wymaga akceptacji technologa

---

## Spis Treści - Nawigacja

### Przegląd
- [Wprowadzenie](#wprowadzenie)
- [Kontekst: Relacja PARTPG/PARTS ↔ Algorytmy](#kontekst-relacja-partpgparts--algorytmy)

### Algorytmy (szczegółowe)
- **[Algorytm WS - Automatyczny Wybór Scenariusza](#algorytm-ws-automatyczny-wybór-scenariusza-pracy)**
  - [Cel algorytmu](#1-cel-algorytmu)
  - [Tabela scenariuszy](#3-tabela-scenariuszy---referencja)
  - [Pseudokod](#5-algorytm-krok-po-kroku)
  - [Koordynacja z RC/RN](#6-koordynacja-z-algorytmami-rc-i-rn)
  - [Szczegółowe sekwencje](#10-szczegółowe-sekwencje-zmian-scenariuszy)

- **[Algorytm RC - Rotacja Układów Pracy Ciągów](#algorytm-rc-cykliczna-rotacja-układów-pracy-ciągów)**
  - [Cel algorytmu](#1-cel-algorytmu-1)
  - [Pseudokod](#5-algorytm-rotacji-krok-po-kroku)
  - [Przykład działania](#8-przykład-działania-1)

- **[Algorytm RN - Rotacja Nagrzewnic](#algorytm-rn-cykliczna-rotacja-nagrzewnic-w-obrębie-ciągu)**
  - [Cel algorytmu](#1-cel-algorytmu-2)
  - [Pseudokod](#5-algorytm-rotacji-nagrzewnic-krok-po-kroku)
  - [Integracja z RC](#10-integracja-z-rotacją-układów-sekcja-rc)
  - [Wizualizacja koordynacji RC↔RN](#rn11-wizualizacja-koordynacji-algorytmów-rc-i-rn)


---

## Wprowadzenie

System sterowania BOGDANKA Szyb 2 wykorzystuje **trzy współpracujące algorytmy** zapewniające automatyczne sterowanie i równomierne rozłożenie eksploatacji urządzeń:

### **Algorytm WS: Automatyczny Wybór Scenariusza Pracy**
- **Cel:** Automatyczny dobór ilości nagrzewnic i konfiguracji systemu w zależności od temperatury zewnętrznej
- **Zakres:** Przełączanie między scenariuszami S0-S8
- **Częstotliwość:** Ciągły monitoring temperatury
- **Dotyczy:** Całego systemu - fundament sterowania

### **Algorytm RC: Rotacja Układów Pracy Ciągów**
- **Cel:** Wyrównanie eksploatacji między ciągiem 1 (W1) a ciągiem 2 (W2)
- **Zakres:** Zmiana między układem Podstawowym a Ograniczonym
- **Okres:** dni/tygodnie/miesiące (definiowany przez technologa)
- **Dotyczy:** Scenariuszy S1-S4

### **Algorytm RN: Rotacja Nagrzewnic w Ciągu**
- **Cel:** Wyrównanie eksploatacji nagrzewnic w obrębie jednego ciągu
- **Zakres:** Wymiana pracującej nagrzewnicy na rezerwową w tym samym ciągu
- **Okres:** godziny/dni/tygodnie (definiowany przez technologa)
- **Dotyczy:** Wszystkich nagrzewnic N1-N8

### **Hierarchia i Koordynacja Algorytmów**

```
┌────────────────────────────────────────────┐
│ Algorytm WS: Wybór Scenariusza (S0-S8)     │
│ └─ Decyduje: ile nagrzewnic, który układ   │
└─────────────────────┬──────────────────────┘
                      │
            ┌─────────┴─────────┐
            │                   │
            ▼                   ▼
     ┌──────────────┐    ┌──────────────┐
     │ Algorytm RC  │    │ Algorytm RN  │
     │ Rotacja      │◄───┤ Rotacja      │
     │ Układów      │───►│ Nagrzewnic   │
     │ (C1 ↔ C2)    │    │ (N1-N8)      │
     └──────────────┘    └──────────────┘
```

Algorytmy są **skoordynowane** i działają współbieżnie, zapewniając:
- Automatyczną adaptację do warunków atmosferycznych (Alg. WS)
- Równomierność zużycia ciągów wentylacyjnych C1, C2 i wentylatorów W1, W2 (Alg. RC)
- Równomierność zużycia wszystkich 8 nagrzewnic N1-N8 (Alg. RN)

---

## Kontekst: Relacja PARTPG/PARTS ↔ Algorytmy

System automatycznej regulacji (SAR) ma **dwuwarstwową architekturę**:

![Architektura SAR](../01-system/schematy/architektura_SAR_system.svg)

*Rys. Dwuwarstwowa architektura systemu SAR z podziałem na warstwy regulacji i zarządzania.*

📖 **[Opis architektury → system.md](../01-system/system.md#2-architektura-sterowania-sar)**

### Kluczowe Różnice Między Warstwami

**Warstwa Regulacji = Funkcja Podstawowa**
- Utrzymanie zadanych temperatur (Tz=50°C, Ts=2°C)
- Praca ciągła, realizacja w czasie rzeczywistym
- Regulatory PID (8 zaworów + 2 wentylatory)
- **Niezbędna** dla działania systemu

**Warstwa Zarządzania = Funkcja Optymalizująca** (Algorytmy WS, RC, RN)
- Równomierne wykorzystanie urządzeń
- Minimalizacja zużycia pojedynczych komponentów
- Maksymalizacja niezawodności i żywotności systemu
- Automatyczna adaptacja do warunków zewnętrznych

**Kluczowa obserwacja:**
- Bez warstwy **regulacji** (PID) → system nie utrzyma temperatury
- Bez warstwy **zarządzania** (algorytmy) → system działa, ale nierównomierne zużycie → awarie

**Ten dokument** opisuje szczegółowo **warstwę zarządzania** (algorytmy WS, RC, RN).  
**Warstwa regulacji** (UAR, PID) jest opisana w [system.md](../01-system/system.md) i [projekt-instalacji.md](../02-projekt-instalacji/projekt-instalacji.md).

# Algorytm WS: Automatyczny Wybór Scenariusza Pracy

**Powiązane algorytmy:** Algorytm RC, Algorytm RN

## 1. Cel Algorytmu

Algorytm realizuje **automatyczny dobór scenariusza pracy systemu (S0-S8)** w zależności od temperatury zewnętrznej w celu:
- Utrzymania temperatury szybu na poziomie 2°C (na głębokości -30m)
- Optymalnego wykorzystania mocy grzewczej (tylko tyle nagrzewnic ile potrzeba)
- Automatycznej adaptacji do zmian warunków atmosferycznych
- Zapewnienia bezpiecznego i stabilnego ogrzewania szybu

## 2. Problem do Rozwiązania

**Wyzwanie:**
- Temperatura zewnętrzna zmienia się dynamicznie (dobowe wahania, fronty atmosferyczne)
- Zapotrzebowanie na moc grzewczą zależy od temperatury zewnętrznej
- Zbyt mało nagrzewnic → przemarzanie szybu (niebezpieczne)
- Zbyt dużo nagrzewnic → marnowanie energii, nadmierne zużycie urządzeń

**Rozwiązanie:**
- Ciągły monitoring temperatury zewnętrznej
- Automatyczny dobór ilości nagrzewnic według tabeli scenariuszy
- Histereza przy wyłączaniu (zapobiega częstym przełączeniom)
- Bezpieczne sekwencje przejść między scenariuszami

## 3. Tabela Scenariuszy - Referencja

Szczegółowa tabela scenariuszy znajduje się w [dokumentacji głównej - Sekcja 4](../01-system/system.md#4-scenariusze-pracy-s0-s8).

**Podsumowanie:**

| Scenariusz | Zakres Temp. | Nagrzewnice | W1 | W2 | Temp. Wyłączenia | Histereza |
|------------|-------------|-------------|----|----|--------------------|-----------|
| S0 | t ≥ 3°C | - | OFF | OFF | - | - |
| S1 | -1°C < t ≤ 2°C | 1 | PID | OFF | t ≥ 3°C | 1°C |
| S2 | -4°C < t ≤ -1°C | 2 | PID | OFF | t ≥ 0°C | 1°C |
| S3 | -8°C < t ≤ -4°C | 3 | PID | OFF | t ≥ -3°C | 1°C |
| S4 | -11°C < t ≤ -8°C | 4 | PID/MAX | OFF | t ≥ -6°C | 2°C |
| S5 | -15°C < t ≤ -11°C | 5 | MAX | PID | t ≥ -10°C | 1°C |
| S6 | -18°C < t ≤ -15°C | 6 | MAX | PID | t ≥ -13°C | 2°C |
| S7 | -21°C < t ≤ -18°C | 7 | MAX | PID | t ≥ -15°C | 3°C |
| S8 | t ≤ -21°C | 8 | MAX | PID | t ≥ -20°C | 1°C |

## 4. Parametry Konfiguracyjne

**Parametry monitoringu temperatury:**

| Parametr | Wartość domyślna | Jednostka | Zakres | Opis |
|----------|-----------------|-----------|--------|------|
| **CYKL_MONITORINGU_TEMP** | 10 | sekundy | 5-60 | Częstotliwość odczytu temperatury zewnętrznej |
| **CZAS_UTRZYMANIA_PRZY_AWARII** | 300 | sekundy | 60-1800 | Czas utrzymania ostatniego scenariusza przy awarii czujnika |
| **FILTR_UŚREDNIANIA** | 3 | próbki | 1-10 | Liczba próbek do uśrednienia (filtr antyfluktuacyjny) |
| **CZAS_STABILIZACJI_SCENARIUSZA** | 60 | sekundy | 30-300 | Min. czas w scenariuszu przed kolejną zmianą |

**Parametry przejść między scenariuszami:**

| Parametr | Wartość domyślna | Jednostka | Opis |
|----------|-----------------|-----------|------|
| **CZAS_MIĘDZY_ZAŁĄCZENIAMI** | 300 | sekundy | Odstęp między załączaniem kolejnych nagrzewnic (5 minut) |
| **CZAS_MIĘDZY_WYŁĄCZENIAMI** | 180 | sekundy | Odstęp między wyłączaniem kolejnych nagrzewnic (3 minuty) |
| **TIMEOUT_ZMIANY_SCENARIUSZA** | 3600 | sekundy | Max. czas na zmianę scenariusza (1 godzina, alarm po przekroczeniu) |

### 4.1. Parametry Czasowe Sprzętu

**WAŻNE:** Wartości podane poniżej są **SZACUNKOWE** dla przemysłowych wentylatorów i nagrzewnic w szybie kopalnianym. Muszą być **zweryfikowane i dostosowane podczas rozruchu** na podstawie rzeczywistych pomiarów czasu operacji sprzętu na obiekcie.

#### Nagrzewnice

Wodne wymienniki ciepła o dużej mocy z dużą bezwładnością termiczną.

| Parametr | Wartość domyślna | Opis |
|----------|-----------------|------|
| **CZAS_USTAWIENIA_ZAWORU** | 10s | Czas ustawienia zaworu na pozycję startową (20%) - duże zawory regulacyjne wody grzewczej, siłowniki hydrauliczne/elektryczne |
| **CZAS_OTWARCIA_PRZEPUSTNICY_NAGRZEWNICY** | 30s | Czas otwarcia **przepustnicy dolotowej powietrza przy nagrzewnicy** (N1-N8) |
| **CZAS_KROKU_ZAWORU** | 5s | Czas na jeden krok zmiany pozycji zaworu (10%) - powolne otwieranie dla uniknięcia uderzenia hydraulicznego |
| **CZAS_AKTYWACJI_PID** | 60s | Czas aktywacji regulatora PID po uruchomieniu - czekamy aż system się ustabilizuje |
| **CZAS_STABILIZACJI_NAGRZEWNICY** | 300s | Czas stabilizacji termicznej (5 minut) - wymiennik potrzebuje czasu na osiągnięcie temp. roboczej |
| **CZAS_OSIĄGNIĘCIA_PEŁNEJ_MOCY** | 600s | Czas osiągnięcia pełnej mocy grzewczej (10 minut) od zimnego startu do stabilnej pracy |
| **CZAS_ZAMKNIĘCIA_ZAWORU** | 30s | Czas zamknięcia zaworu do pozycji 20% - powolne zamykanie dla płynnego wyłączenia |
| **CZAS_ZAMKNIĘCIA_PRZEPUSTNICY_NAGRZEWNICY** | 20s | Czas zamknięcia **przepustnicy dolotowej przy nagrzewnicy** |
| **CZAS_CHŁODZENIA_NAGRZEWNICY** | 180s | Czas chłodzenia po wyłączeniu (3 minuty) - wymiennik oddaje ciepło |

#### Wentylatory

Duże maszyny przemysłowe z dużą bezwładnością wirnika.

| Parametr | Wartość domyślna | Opis |
|----------|-----------------|------|
| **CZAS_ROZRUCHU_WENTYLATORA** | 120s | Czas rozruchu wentylatora (soft-start, 2 minuty) - zabezpieczenie przed przeciążeniem silnika |
| **CZAS_DO_OBROTÓW_NOMINALNYCH** | 180s | Czas przyspieszenia do obrotów nominalnych (3 minuty) od startu do pełnych obrotów |
| **CZAS_ZATRZYMANIA_WENTYLATORA** | 300s | Czas bezpiecznego zatrzymania wentylatora (5 minut) - bezwładność wirnika |
| **CZAS_ZMIANY_PRĘDKOŚCI** | 60s | Czas zmiany prędkości obrotowej (np. 25Hz → 50Hz) przez przemiennik częstotliwości |

#### Przepustnice Główne Systemu

Duże klapy wentylacyjne w głównej instalacji wentylacyjnej (kolektory, wyrzutnie, spinka ciągów).  
**Uwaga:** To są inne przepustnice niż małe przepustnice dolotowe przy nagrzewnicach (patrz sekcja Nagrzewnice powyżej).

| Parametr | Wartość domyślna | Opis |
|----------|-----------------|------|
| **CZAS_OPERACJI_PRZEPUSTNICY** | 30s | Czas operacji **przepustnic głównych** (kolektory C1/C2, wyrzutnie -4,30m/-7,90m) - siłowniki elektryczne/pneumatyczne |
| **CZAS_OPERACJI_SPINKA** | 45s | Czas operacji **przepustnicy na spince ciągów** - największa przepustnica, najbardziej krytyczna |
| **CZAS_WERYFIKACJI_PRZEPUSTNICY** | 15s | Czas weryfikacji pozycji końcowej po operacji |

#### Stabilizacja Systemu

| Parametr | Wartość domyślna | Opis |
|----------|-----------------|------|
| **CZAS_STABILIZACJI_PRZEPŁYWU** | 300s | Czas stabilizacji przepływu powietrza po zmianie układu (5 minut) |
| **CZAS_WERYFIKACJI_TEMPERATURY** | 180s | Czas weryfikacji temperatury nagrzewnicy (3 minuty) |
| **CZAS_SPRAWDZENIA_STABILNOŚCI** | 600s | Czas sprawdzenia stabilności systemu (10 minut) przed krytycznymi operacjami |


## 5. Algorytm Krok po Kroku

**Diagram przepływu algorytmu:**

![Algorytm WS - Wybór Scenariusza](./schematy/algorytm-WS-wybor-scenariusza-flowchart.svg)

**Pełny pseudokod algorytmu WS:**  
**[→ src/algo_pseudokod.md - Algorytm WS](../../src/algo_pseudokod.md)**

Pseudokod zawiera:
- Zmienne globalne i parametry (CYKL_MONITORINGU_TEMP, FILTR_UŚREDNIANIA, timeouty)
- Główną pętlę monitoringu temperatury 
- Funkcję `Określ_Scenariusz_Dla_Temperatury()` - logika dla wszystkich scenariuszy
- Funkcję `Wykonaj_Zmianę_Scenariusza()` - kompletne sekwencje zmian
- Funkcje pomocnicze: `Załącz_Nagrzewnicę()`, `Wyłącz_Nagrzewnicę()`, `Konfiguruj_Wentylator()`
- **Wszystkie parametry czasowe** (wartości przemysłowe  do zweryfikowania podczas testowania na obiekcie)

## 6. Koordynacja z Algorytmami RC i RN

**Hierarchia działania:**

1. **Algorytm WS**  - określa **ILE** nagrzewnic potrzeba (S0-S8)
2. **Algorytm RC** - określa **KTÓRY CIĄG** w S1-S4 (Podstawowy: C1, Ograniczony: C2)
3. **Algorytm RN** - określa **KTÓRE KONKRETNIE** nagrzewnice w ciągu (rotacja)

**Zasady koordynacji:**

- **S0:** Brak nagrzewnic - algorytmy RC i RN nieaktywne
- **S1-S4:** 
  - Algorytm RC wybiera układ (C1 lub C2)
  - Algorytm RN wybiera konkretne nagrzewnice w aktywnym ciągu
  - Algorytm WS wywołuje funkcje pomocnicze które respektują wybory RC i RN
- **S5-S8:**
  - Algorytm RC nieaktywny (zawsze układ Podstawowy)
  - Algorytm RN aktywny tylko dla C2 (jeśli są nagrzewnice rezerwowe)
  - C1 pracuje zawsze w pełnej konfiguracji (N1-N4)

**Blokady:**

```
JEŻELI zmiana_układu_w_toku = PRAWDA (Algorytm RC) WTEDY
  // Odrocz zmianę scenariusza do zakończenia rotacji układów
  Czekaj(...)
KONIEC JEŻELI

JEŻELI rotacja_nagrzewnic_w_toku = PRAWDA (Algorytm RN) WTEDY
  // Odrocz zmianę scenariusza do zakończenia rotacji nagrzewnic
  Czekaj(...)
KONIEC JEŻELI
```

## 7. Obsługa Stanów Awaryjnych

| Stan Awaryjny | Reakcja Systemu |
|---------------|-----------------|
| Brak odczytu T_zewn | Utrzymaj ostatni scenariusz przez CZAS_UTRZYMANIA_PRZY_AWARII (300s), potem alarm krytyczny i tryb MANUAL |
| Nagrzewnica nie załącza się | Pomiń nagrzewnicę, kontynuuj z mniejszą ilością, alarm informacyjny |
| Wentylator nie uruchamia się | Przerwij zmianę scenariusza, alarm krytyczny, tryb MANUAL |
| Przekroczenie czasu zmiany | Przerwij zmianę, alarm, powrót do poprzedniego scenariusza lub tryb MANUAL |
| Temperatura szybu poza zakresem | Przyspieszenie/opóźnienie zmiany scenariusza, alarm ostrzegawczy |
| Oscylacje temperatury zewnętrznej | Zwiększenie CZAS_STABILIZACJI_SCENARIUSZA, filtrowanie odczytów |

## 8. Przykład Działania

**Scenariusz: Ochłodzenie nocne**

```
Dzień 1, godz. 18:00 - Temperatura: +5°C
  Scenariusz: S0
  Stan: Wszystkie nagrzewnice wyłączone
  
Dzień 1, godz. 20:00 - Temperatura: +1°C (spadek)
  Algorytm wykrywa: t=1°C → wymagany S1
  Scenariusz: S0 → S1
  Akcja:
    - Uruchom wentylator W1 (PID, 25 Hz)
    - Załącz nagrzewnicę N1 (zgodnie z Algorytmem RC/RN)
    - Czas zmiany: ~50 sekund
  
Dzień 1, godz. 22:00 - Temperatura: -2°C (dalszy spadek)
  Algorytm wykrywa: t=-2°C → wymagany S2
  Scenariusz: S1 → S2
  Akcja:
    - Wentylator W1 już pracuje (zwiększenie częstotliwości przez PID)
    - Załącz nagrzewnicę N2
    - Czas zmiany: ~40 sekund (mniej bo wentylator już pracuje)
  
Dzień 2, godz. 02:00 - Temperatura: -6°C (mróz nocny)
  Algorytm wykrywa: t=-6°C → wymagany S3
  Scenariusz: S2 → S3
  Akcja:
    - Załącz nagrzewnicę N3
    - Czas zmiany: ~40 sekund
  
Dzień 2, godz. 08:00 - Temperatura: -3°C (ocieplenie poranne)
  Algorytm wykrywa: t=-3°C
  Histereza S3: wyłączenie dopiero przy t≥-3°C
  Scenariusz: S3 → S2
  Akcja:
    - Wyłącz nagrzewnicę N3
    - Czas zmiany: ~40 sekund
  
Dzień 2, godz. 14:00 - Temperatura: +1°C (dzień)
  Algorytm wykrywa: t=1°C
  Histereza S2: wyłączenie dopiero przy t≥0°C → jeszcze nie
  Scenariusz: S2 (utrzymany)
  
Dzień 2, godz. 16:00 - Temperatura: +4°C (ocieplenie)
  Algorytm wykrywa: t=4°C
  Histereza S1: wyłączenie przy t≥3°C
  Scenariusz: S1 → S0
  Akcja:
    - Wyłącz nagrzewnicę N1
    - Zatrzymaj wentylator W1
    - Czas zmiany: ~50 sekund
```

**Obserwacje:**
- Histereza zapobiega częstym przełączeniom przy temperaturach granicznych
- System reaguje szybko na spadki temperatury
- System wolniej reaguje na wzrosty (oszczędzanie energii z bezpieczeństwem)

## 9. Szczegółowe Sekwencje Zmian Scenariuszy

Każda zmiana scenariusza wymaga **skoordynowanej sekwencji** operacji na:
- Zaworach regulacyjnych wody grzewczej (20-100%)
- Przepustnicach dolotowych nagrzewnic (otwarte/zamknięte)
- Przepustnicach głównych systemu (kolektory, spinka, wyrzutnie)
- Wentylatorach (start/stop, tryb PID)

**Hierarchia sterowania:**

System ma **trzy poziomy sterowania**:

1. **Algorytm WS (Nadzorca scenariuszy)** ← monitoruje **T_zewn**
   - Decyduje ILE nagrzewnic potrzeba
   - WŁĄCZA i WYŁĄCZA nagrzewnice
   - Zarządza przejściami między scenariuszami

2. **PID Nagrzewnicy (UAR temperatury powietrza)** ← monitoruje **T_wylot**
   - Utrzymuje 50°C na wylocie z nagrzewnicy
   - Reguluje zawór wody (20-100%)

3. **PID Wentylatora (UAR temperatury szybu)** ← monitoruje **T_szyb**
   - Utrzymuje 2°C w szybie na -30m
   - Reguluje prędkość wentylatora (25-50Hz)
   - Dostosowuje się do ilości nagrzewnic

**Przykład interakcji:**
```
T_zewn = 3°C (wzrost)
  ↓
Algorytm WS: "Nie potrzebuję już nagrzewnic" → decyzja o przejściu S1→S0
  ↓
Sekwencja wyłączania:
  1. Przełącz PID nagrzewnicy: AUTO → MANUAL
  2. Zamknij zawór ręcznie: aktualna_pozycja → 20%
  3. Zamknij przepustnicę
  4. Zatrzymaj wentylator
```

#### 9.1 Typy Przejść

System rozróżnia 4 typy przejść między scenariuszami:

| Typ | Opis | Przykłady | Złożoność |
|-----|------|-----------|-----------|
| **A** | Wyłączenie systemu | S1→S0 | Niska |
| **B** | Uruchomienie systemu | S0→S1 | Średnia |
| **C** | Zmiana w obrębie jednego ciągu | S1→S2, S2→S3, S3→S4 | Średnia |
| **D** | Uruchomienie drugiego ciągu | S4→S5 | **Wysoka** |
| **E** | Zatrzymanie drugiego ciągu | S5→S4 | **Wysoka** |
| **F** | Zmiana w obrębie dwóch ciągów | S5→S6, S6→S7, S7→S8 | Niska |

#### 9.2 Procedury elementarne


| Procedura | Wejście | Opis |
|-----------|--------|------|
| **STOP_HEATER(N)** | aktywna nagrzewnica | PID → MANUAL → zawór do 20% (krok 10% / 2 s) → zamknięcie przepustnicy dolotowej → log zdarzenia |
| **START_HEATER(N)** | nagrzewnica gotowa | zawór 20% → przepustnica OTWARTA → PID AUTO 50 °C → weryfikacja T_wylot ≥ 30 °C |
| **STOP_FAN(W)** | pracujący wentylator | redukcja do 25 Hz → STOP → zamknięcie przepustnic ciągu |
| **START_FAN(W)** | wentylator w postoju | otwarcie przepustnic ciągu → start 25 Hz → przekazanie do PID (jeśli wymagane) |
| **SWITCH_LINE(to)** | docelowy układ | zestaw CLOSE_LINE / OPEN_LINE wg tabeli przepustnic (sekcja 10.10) |
| **VERIFY_SCENARIO(Sx)** | docelowy scenariusz | kontrola aktywnych nagrzewnic, pracy wentylatorów, temperatury szybu, log |

Każdy typ przejścia korzysta z tych samych procedur, różni się tylko kolejnością oraz tym, które ciągi i wentylatory biorą udział.

#### 9.3 Sekwencja TYP A: Wyłączenie Systemu (S1→S0)

- **Warunki:** T_zewn ≥ 3 °C, aktywny tylko ciąg 1.
- **Przebieg skrócony:** STOP_HEATER (dla wszystkich aktywnych nagrzewnic) → STOP_FAN(W1) → CLOSE_LINE(C1) → VERIFY_SCENARIO(S0).
- **Uwagi:** jeśli czujnik T_szyb nadal raportuje <2 °C, WS opóźnia przejście do czasu stabilizacji.

#### 9.4 Sekwencja TYP B: Uruchomienie Systemu (S0→S1)

- **Warunki:** T_zewn ≤ 2 °C, oba ciągi w postoju.
- **Przebieg:** OPEN_LINE(C1) → START_FAN(W1) → START_HEATER(N wybrana przez RC/RN) → VERIFY_SCENARIO(S1).
- **Uwagi:** tylko jedna nagrzewnica w ciągu, więc RN wskazuje element z najdłuższym postojem.

#### 9.5 Sekwencja TYP C: Dodanie Nagrzewnicy w Tym Samym Ciągu (S1→S4)

- **Warunki:** Ciąg aktywny (C1 lub C2) ma rezerwową nagrzewnicę.
- **Przebieg:** START_HEATER(N_now) → VERIFY_SCENARIO(Sx). Wentylator automatycznie dostosowuje PID, brak dodatkowych działań.
- **Uwagi:** przy redukcji scenariusza (np. S3→S2) wykonujemy odwrotność, tj. STOP_HEATER dla ostatniej nagrzewnicy wskazanej przez RN.

#### 9.6 Sekwencja TYP D: Uruchomienie Drugiego Ciągu (S4→S5)

- **Warunki:** T_zewn ≤ -11 °C, C1 pracuje na pełnej mocy.
- **Przebieg:** VERIFY linię C1 (4 nagrzewnice) → OPEN_LINE(C2) + START_FAN(W2) + W1→MAX → START_HEATER (pierwsza nagrzewnica C2) → SWITCH_LINE(to=dual) → VERIFY_SCENARIO(S5).
- **Uwagi krytyczne:** pierwszy raz otwierana wyrzutnia -7,90 m, konieczne logi prądowe obu wentylatorów; w razie błędu natychmiastowy fallback do S4.

#### 9.7 Sekwencja TYP E: Zatrzymanie Drugiego Ciągu (S5→S4)

- **Warunki:** T_zewn ≥ -10 °C, oba ciągi pracują.
- **Przebieg:** STOP_HEATER (nagrzewnice C2) → STOP_FAN(W2) → CLOSE_LINE(C2) → ustaw W1 na PID → VERIFY_SCENARIO(S4).
- **Uwagi:** monitoruj T_szyb ±1 °C; jeśli niestabilna, WS cofnie zmianę.

#### 9.8 Sekwencja TYP F: Dodanie Nagrzewnicy w Drugim Ciągu (S5→S8)

- **Warunki:** Ciąg 2 posiada rezerwową nagrzewnicę (np. N6–N8).
- **Przebieg:** START_HEATER(N wybrana przez RN) przy pracującym fanie W2 → VERIFY_SCENARIO(Sx).
- **Uwagi:** analogiczne zasady jak w typie C, ale obowiązuje blokada „15 min od ostatniej rotacji” wynikająca z koordynacji RC↔RN.

#### 9.9 Tabela Czasów Sekwencji

| Przejście | Typ | Czas [s] | Uwagi |
|-----------|-----|----------|-------|
| S0→S1 | B | ~70 | Uruchomienie systemu od zera |
| S1→S0 | A | ~60 | Wyłączenie systemu |
| S1→S2, S2→S3, S3→S4 | C | ~45 | Dodanie nagrzewnicy w C1 |
| S4→S3, S3→S2, S2→S1 | C | ~50 | Usunięcie nagrzewnicy z C1 |
| **S4→S5** | **D** | **~100** | **uruchomienie C2 !** |
| **S5→S4** | **E** | **~70** | **zatrzymanie C2 !** |
| S5→S6, S6→S7, S7→S8 | F | ~45 | Dodanie nagrzewnicy w C2 |
| S8→S7, S7→S6, S6→S5 | F | ~50 | Usunięcie nagrzewnicy z C2 |

#### 9.10 Koordynacja Przepustnic - Stany dla Wszystkich Scenariuszy

| Element | S0 | S1-S4 Podst. | S1-S4 Ogr. | S5-S8 |
|---------|----|--------------|-----------| ------|
| **Ciąg 1:** | | | | |
| Przepustnica C1 | Z | **O** | **Z** | **O** |
| Kolektor C1 | Z | **O** | **Z** | **O** |
| Wyrzutnia -4,30m | Z | **O** | Z | **O** |
| **Ciąg 2:** | | | | |
| Przepustnica C2 | Z | Z | **O** | **O** |
| Kolektor C2 | Z | Z | **O** | **O** |
| Wyrzutnia -7,90m | Z | Z | Z | **O** |
| **Spinka:** | | | | |
| Przepustnica spinka | Z | Z | **O** | Z |

**Legenda:** O = Otwarta, Z = Zamknięta

**Kluczowe przejścia przepustnic:**
- **S4→S5:** Otwieramy wyrzutnię -7,90m po raz pierwszy
- **S5→S4:** Zamykamy wyrzutnię -7,90m
- **Układ Podst.→Ogr.:** Zamykamy C1, otwieramy spinę i C2
- **Układ Ogr.→Podst.:** Zamykamy spinę i C2, otwieramy C1

#### 9.11 Zarządzanie Zaworami - Strategia Bezpieczeństwa

**Zasady zarządzania zaworami wody grzewczej:**

1. **Nigdy nie zamykaj zaworu poniżej 20%** (ochrona antyzamrożeniowa)
2. **Stopniowe zamykanie:** krok 10%, przerwa 2s (zapobiega uderzeniom hydraulicznym)
3. **Stopniowe otwieranie:** krok 10%, przerwa 2s (stopniowe ogrzewanie)
4. **Stabilizacja PID:** min. 30s po aktywacji regulatora
5. **Weryfikacja temperatury:** przed uznaniem nagrzewnicy za aktywną

**Stany zaworu podczas pracy:**

| Stan nagrzewnicy | Pozycja zaworu | Tryb regulatora | Uwagi |
|------------------|----------------|-----------------|-------|
| **OFF** (postój) | 20% stała | MANUAL | Ochrona przed zamrożeniem |
| **STARTING** | 20% → AUTO | MANUAL → AUTO | Przejście do pracy |
| **RUNNING** | 20-100% PID | AUTO | Praca normalna |
| **STOPPING** | AUTO → 20% | AUTO → MANUAL | Przejście do postoju |

# Globalne Parametry Rotacyjne (RC/RN)

| Parametr | Wartość domyślna | Jednostka | Zakres | Stosowanie |
|----------|-----------------|-----------|--------|------------|
| **CYKL_PĘTLI_ALGORYTMÓW** | 60 | sekundy | 10‑600 | Częstość wywołania głównej pętli RC i RN (aktualizacja liczników, warunków) |
| **HISTEREZA_CZASOWA** | 300 | sekundy | 60‑900 | Bufor czasowy przed uznaniem, że upłynął okres rotacji układów (RC) |
| **MIN_DELTA_CZASU** | 3600 | sekundy | 1800‑7200 | Minimalna różnica czasów pracy nagrzewnic, aby RN wykonał zamianę |
| **ODSTĘP_PO_ZMIANIE_UKŁADU** | 3600 | sekundy | 1800‑7200 | Czas blokujący RN po zakończeniu RC (`czas_ostatniej_zmiany_układu`) |
| **ODSTĘP_MIĘDZY_ROTACJAMI** | 900 | sekundy | 600‑1800 | Globalny odstęp pomiędzy rotacjami RN w różnych ciągach |

Parametry te są deklarowane w jednym miejscu konfiguracji systemu i wykorzystywane przez obydwa algorytmy rotacyjne. Szczegółowe wartości (np. `OKRES_ROTACJI_UKŁADÓW`, `OKRES_ROTACJI_NAGRZEWNIC`) pozostają w sekcjach konkretnych algorytmów.

# Algorytm RC: Cykliczna Rotacja Układów Pracy Ciągów


**Powiązane algorytmy:** Algorytm WS, Algorytm RN

## 1. Cel Algorytmu

Algorytm realizuje **cykliczną zmianę układów pracy ciągów grzewczych** w celu:
- Wyrównania czasów eksploatacji ciągów grzewczych (W1 vs W2)
- Uniknięcia nadmiernej eksploatacji ciągu pierwszego
- Zwiększenia niezawodności i równomiernego zużycia urządzeń

## 2. Problem do Rozwiązania

**Bez rotacji układów:**
- Ciąg 1 (N1-N4 + W1) pracuje zawsze w scenariuszach S1-S4 (temp. od 2°C do -11°C)
- Ciąg 2 (N5-N8 + W2) włącza się dopiero w S5-S8 (temp. < -11°C)
- **Rezultat:** Ciąg 1 jest eksploatowany znacznie częściej i intensywniej niż ciąg 2

**Z rotacją układów:**
- System okresowo zmienia układ: Podstawowy → Ograniczony → Podstawowy
- Oba ciągi mają równomierne czasy pracy

## 3. Parametr Konfiguracyjny

**OKRES_ROTACJI_UKŁADÓW** - parametr definiowany przez **technologa podczas rozruchu**

| Parametr | Wartość domyślna | Jednostka | Zakres | Opis |
|----------|-----------------|-----------|--------|------|
| OKRES_ROTACJI_UKŁADÓW | Do ustalenia* | godziny lub dni | 24h - 30 dni | Czas po którym następuje zmiana układu pracy |

*Wartość zostanie ustalona podczas testowania pracy układu na obiekcie i może być modyfikowana w zależności od warunków eksploatacyjnych.

**Przykładowe wartości:**
- **168h (7 dni)** - typowa wartość dla równomiernego rozłożenia eksploatacji
- **720h (30 dni)** - dla zmniejszenia częstotliwości przełączeń
- **24h (1 dzień)** - dla testów i weryfikacji działania

`CYKL_PĘTLI_ALGORYTMÓW` oraz pozostałe ograniczenia czasowe opisano w sekcji „Globalne parametry rotacyjne”.

## 4. Warunki Aktywacji Rotacji

Rotacja układów jest możliwa **TYLKO** gdy spełnione są **WSZYSTKIE** warunki:

1. **Warunek temperaturowy:**
   - Aktualny scenariusz: S1, S2, S3 lub S4
   - Temperatura zewnętrzna: -11°C < t ≤ 2°C
   - Wymagana ilość nagrzewnic ≤ 4

2. **Warunek gotowości ciągu 2:**
   - Ilość sprawnych nagrzewnic ciągu 2 (N5-N8) ≥ wymagana ilość nagrzewnic
   - Wentylator W2 sprawny i w gotowości operacyjnej
   - Przepustnica na spince ciągów sprawna

3. **Warunek czasowy:**
   - Upłynął OKRES_ROTACJI_UKŁADÓW od ostatniej zmiany układu
   - System pracuje w trybie AUTO

4. **Warunek stabilności:**
   - Brak aktywnych alarmów krytycznych
   - Parametry wody grzewczej w normie
   - System SAR stabilny (brak oscylacji temperatury)

### Zachowanie w Scenariuszach S5-S8

**W scenariuszach S5-S8 algorytm RC NIE wykonuje rotacji**, ponieważ:
- Oba ciągi pracują jednocześnie (układ zawsze "Podstawowy")
- Nie ma co rotować ciagow - system pracuje w pełnej konfiguracji (dwuliniowo)

**JEDNAK licznik czasu pracy nadal działa:**
- Czas w S5-S8 liczy się jako `czas_pracy_układu_podstawowego`
- Licznik `czas_ostatniej_zmiany` **NIE jest resetowany** przy przejściu do/z S5-S8

**Przykład praktyczny:**
```
Dzień 1-2: S3, Układ Podstawowy (C1 pracuje)
  czas_pracy_układu_podstawowego = 48h

Dzień 2: S5 przez 6 godzin (temperatura spadła do -12°C)
  czas_pracy_układu_podstawowego = 54h
  czas_ostatniej_zmiany NIEZMIENIONY
  
Dzień 2: Powrót do S3, Układ Podstawowy
  czas_pracy_układu_podstawowego = 54h + dalej rośnie
  
Dzień 5 (120h od ostatniej rotacji):
  Nastąpi rotacja: Podstawowy → Ograniczony
```

**Uzasadnienie:** Ciąg C1 faktycznie pracuje w S5, więc jego czas pracy jest prawidłowo liczony, a równowaga między ciągami nie jest zaburzona przez krótkotrwałe przejścia do S5-S8.

## 5. Algorytm Rotacji Krok po Kroku

**Diagram przepływu algorytmu:**

![Algorytm RC - Diagram przepływu](./schematy/algorytm-RC-rotacja-ciagow-flowchart.svg)

**Pełny pseudokod algorytmu RC:**  
**[→ src/algo_pseudokod.md - Algorytm RC](../../src/algo_pseudokod.md)**

Pseudokod zawiera:
- Zmienne globalne (współdzielone z RN) i lokalne dla RC
- Parametry rotacji (OKRES_ROTACJI_UKŁADÓW, HISTEREZA_CZASOWA, CYKL_PĘTLI_ALGORYTMÓW)
- Główną pętlę sprawdzania warunków rotacji
- Funkcję `Wykonaj_Zmianę_Układu()` - kompletne sekwencje dla przejść Podstawowy ↔ Ograniczony
- **Wszystkie parametry czasowe** dla nagrzewnic, wentylatorów, przepustnic
- Koordynację z algorytmem RN (blokady `zmiana_układu_w_toku`, `rotacja_nagrzewnic_w_toku`)
- Obsługę czasu w scenariuszach S5-S8 (liczony jako czas układu Podstawowego)

## 6. Obsługa Stanów Awaryjnych Podczas Rotacji

| Stan Awaryjny | Reakcja Systemu |
|---------------|-----------------|
| Awaria nagrzewnicy podczas zmiany | Kontynuuj zmianę z pominiętą nagrzewnicą, alarm informacyjny |
| Awaria wentylatora podczas zmiany | Natychmiastowy powrót do poprzedniego układu, alarm krytyczny |
| Przekroczenie czasu zmiany (>10 min) | Przerwij zmianę, powrót do układu podstawowego, alarm |
| Oscylacje temperatury podczas zmiany | Zwiększ czas stabilizacji (60s zamiast 30s), kontynuuj |
| Brak przepływu wody grzewczej | Natychmiastowe zatrzymanie zmiany, wyłączenie wszystkich nagrzewnic, alarm krytyczny |

## 7. Przykład Działania

**Warunki początkowe:**
- Temperatura zewnętrzna: -5°C
- Scenariusz: S3 (3 nagrzewnice)
- OKRES_ROTACJI_UKŁADÓW = 168h (7 dni)
- Aktualny układ: Podstawowy
- Czas od ostatniej zmiany: 169h

**Przebieg:**

1. **Dzień 0, godz. 00:00** - System w układzie Podstawowym
   - Pracują: N1, N2, N3 + W1 (PID)
   - Nawiew na -4,30m

2. **Dzień 7, godz. 01:00** - Upłynął OKRES_ROTACJI_UKŁADÓW
   - Warunki rotacji spełnione 
   - Algorytm rozpoczyna zmianę: Podstawowy → Ograniczony

3. **Dzień 7, godz. 01:05** - Zmiana zakończona
   - Pracują: N5, N6, N7 + W2 (PID)
   - Nawiew na -4,30m przez spinę ciągów
   - Zarejestrowano zdarzenie w dzienniku

4. **Dzień 14, godz. 01:00** - Kolejna rotacja
   - Zmiana: Ograniczony → Podstawowy
   - Powrót do N1, N2, N3 + W1

**Rezultat po miesiącu:**
- Ciąg 1: ~360h pracy (50%)
- Ciąg 2: ~360h pracy (50%)
- Stosunek eksploatacji: 1.0 (Idealne wyrównanie)

# Algorytm RN: Cykliczna Rotacja Nagrzewnic w Obrębie Ciągu

**Powiązane algorytmy:** Algorytm WS, Algorytm RC

## 1. Cel Algorytmu

Algorytm realizuje **cykliczną rotację nagrzewnic pracujących w jednym ciągu wentylacyjnym** w celu:
- Wyrównania czasów eksploatacji poszczególnych nagrzewnic w ciągu
- Zmniejszenia zużycia pojedynczej nagrzewnicy
- Zwiększenia niezawodności systemu przez równomierne zużycie urządzeń

## 2. Problem do Rozwiązania

**Bez rotacji nagrzewnic (przykład dla S3 - 3 nagrzewnice):**
- N1 pracuje ZAWSZE (najdłuższy czas pracy)
- N2 pracuje często (średni czas pracy)
- N3 pracuje rzadziej (krótszy czas pracy)
- N4 NIE pracuje (brak zużycia)
- **Rezultat:** Nierównomierne zużycie nagrzewnic → N1 będzie wymagać konserwacji znacznie wcześniej niż N4

**Z rotacją nagrzewnic:**
```
Dzień 1-7:   N1, N2, N3 pracują
Dzień 8-14:  N2, N3, N4 pracują  (N1 odpoczynek, N4 wchodzi)
Dzień 15-21: N3, N4, N1 pracują  (N2 odpoczynek, N1 wchodzi)
Dzień 22-28: N4, N1, N2 pracują  (N3 odpoczynek, N2 wchodzi)
```
- **Rezultat:** Równomierne zużycie wszystkich 4 nagrzewnic ciągu

## 3. Parametry Konfiguracyjne

Parametry definiowane przez **technologa podczas rozruchu**:

| Parametr | Wartość domyślna | Jednostka | Zakres | Opis |
|----------|-----------------|-----------|--------|------|
| **OKRES_ROTACJI_NAGRZEWNIC** | Do ustalenia* | godziny | 24h - 720h | Czas po którym następuje zmiana nagrzewnicy w ciągu |
| **MIN_DELTA_CZASU** | 3600 | sekundy | 1800 - 7200 | Minimalna różnica czasu pracy dla wykonania rotacji |

*Wartości zostaną ustalone podczas testowania pracy układu na obiekcie (zgodnie z sekcją 1.4 projektu).

**Przykładowe wartości OKRES_ROTACJI_NAGRZEWNIC:**
- **168h (7 dni)** - typowa wartość dla równomiernego rozłożenia eksploatacji
- **720h (30 dni)** - dla zmniejszenia częstotliwości przełączeń
- **48h (2 dni)** - dla intensywnej rotacji i szybszego wyrównania

**Uzasadnienie MIN_DELTA_CZASU:**
- **3600s (1h)** - wartość domyślna, zapobiega częstym rotacjom przy niewielkich różnicach
- **7200s (2h)** - dla bardziej konserwatywnego podejścia
- **1800s (30min)** - dla agresywniejszego wyrównywania w scenariuszach dynamicznych
- Jeśli różnica czasu pracy jest mniejsza niż MIN_DELTA_CZASU, rotacja nie ma sensu (zmiana dla zmiany)

Parametr **CYKL_PĘTLI_ALGORYTMÓW** jest wspólny z algorytmem RC – opis szczegółowy znajduje się w sekcji RC.3. RN korzysta z tej samej wartości do aktualizacji liczników `czas_pracy[N]` i `czas_postoju[N]`.

## 4. Warunki Aktywacji Rotacji Nagrzewnic

Rotacja nagrzewnic jest możliwa **TYLKO** gdy spełnione są **WSZYSTKIE** warunki:

1. **Warunek konfiguracji ciągu:**
   - Ilość sprawnych nagrzewnic ciągu > ilość aktualnie pracujących nagrzewnic
   - Co najmniej 1 nagrzewnica musi pozostać aktywna podczas zmiany
   - Maksymalnie 4 nagrzewnice w ciągu

2. **Warunek czasowy:**
   - Upłynął OKRES_ROTACJI_NAGRZEWNIC od ostatniej rotacji w tym ciągu
   - System pracuje w trybie AUTO

3. **Warunek stabilności:**
   - Brak aktywnych alarmów dla nagrzewnic w ciągu
   - Parametry wody grzewczej w normie
   - Temperatura w szybie stabilna (brak oscylacji > ±0.5°C)
   - Wentylator ciągu sprawny i pracujący

4. **Warunek dostępności:**
   - Nagrzewnica zastępcza w gotowości operacyjnej
   - Zawór regulacyjny sprawny
   - Przepustnice sprawne

## 5. Algorytm Rotacji Nagrzewnic Krok po Kroku

**WAŻNE - Algorytm RN jako serwis dla innych algorytmów:**

Algorytm RN pełni **podwójną funkcję**:

1. **Funkcja aktywna** - Wykonuje cykliczną rotację nagrzewnic (wymiana najdłużej pracującej → najdłużej w postoju)
2. **Funkcja serwisowa** - Dostarcza funkcje wyboru nagrzewnic wywoływane przez:
   - **Algorytm WS** (wybór scenariusza) - wywołuje `Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy(ciąg, ilość)`
   - **Algorytm RC** (rotacja układów) - wywołuje `Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy(ciąg, ilość)`
   - **Sekwencje zmian scenariuszy** - wywołują `Algorytm_RN_Wybierz_Nagrzewnicę(ciąg, ilość)`

**Zasada:** NIGDY nie zakładamy sekwencyjnego wyboru nagrzewnic (N1→N2→N3...). Zawsze delegujemy wybór do Algorytmu RC, który:
- Śledzi czasy pracy i postoju każdej nagrzewnicy
- Wybiera nagrzewnice na podstawie historii eksploatacji
- Zapewnia równomierne zużycie wszystkich nagrzewnic N1-N8

**Diagram wizualizujący algorytm:**

![Algorytm RN Flowchart](./schematy/algorytm-RN-rotacja-nagrzewnic-flowchart.svg)

**Pełny pseudokod algorytmu RN:**  
**[→ src/algo_pseudokod.md - Algorytm RN](../../src/algo_pseudokod.md)**

Pseudokod zawiera:
- Zmienne globalne (współdzielone z RC) i lokalne (dla każdego ciągu osobno)
- Parametry rotacji (OKRES_ROTACJI_NAGRZEWNIC per scenariusz, MIN_DELTA_CZASU)
- Główną pętlę dla każdego ciągu z aktualizacją liczników czasu pracy/postoju
- **Obsługa zmiany scenariusza** - rozróżnienie zmian STRUKTURALNYCH vs ILOŚCIOWYCH
- Funkcję `Wykonaj_Rotację_Nagrzewnicy()` - bezpieczna sekwencja (załącz PRZED wyłącz)
- **Wszystkie parametry czasowe** dla rotacji nagrzewnic
- Koordynację z algorytmem RC (blokady, odstęp czasowy po zmianie układu, odstęp czasowy między rotacjami)
- Funkcje serwisowe dla WS i RC: `Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy()`

## 6. Priorytety Rotacji

**Aktywność ciągów w zależności od scenariusza:**

| Scenariusz | Aktywne ciągi | Układ | Uwaga |
|------------|---------------|-------|-------|
| **S1-S4** | **TYLKO JEDEN ciąg** na raz | Układ Podstawowy: **C1** (W1 PID)<br>Układ Ograniczony: **C2** (W2 PID) | Algorytm RC przełącza między układami → rotacja RN dotyczy ciągu który **aktualnie pracuje** |
| **S5-S8** | **OBA ciągi** jednocześnie | C1 MAX + C2 PID/MAX | Oba ciągi aktywne, ale tylko C2 może rotować (C1 niemożliwa - brak rezerwowej) |

Gdy wiele ciągów wymaga rotacji jednocześnie, stosuje się następujące priorytety:

| Priorytet | Ciąg | Warunek | Uzasadnienie |
|-----------|------|---------|--------------|
| 1 | **Ciąg aktywny w S1-S4** | **C1 (Układ Podstawowy)** ALBO **C2 (Układ Ograniczony)** - pracuje SOLO | Najwyższe zużycie - całe obciążenie grzewcze na jednym ciągu, priorytetowa rotacja |
| 2 | Ciąg 2 (S5-S7) | C1 MAX + C2 PID | C2 reguluje temperaturę PID - rotacja **MOŻLIWA** i ważna dla stabilności (są nagrzewnice rezerwowe) |
| 3 | Ciąg 1 (S5-S8) | C1 MAX + C2 PID/MAX | C1 pracuje na MAX - rotacja **NIEMOŻLIWA*** (wszystkie N1-N4 pracują, brak rezerwowej) |

**Ograniczenia rotacji:**
- *W **S5-S8**: rotacja RN w **C1 jest NIEMOŻLIWA** - wszystkie nagrzewnice N1-N4 muszą pracować (brak nagrzewnicy rezerwowej)
- W **S5-S7**: rotacja RN w **C2 jest MOŻLIWA** - są nagrzewnice rezerwowe (N8 w S7, N7-N8 w S6, N6-N8 w S5)
- W **S8**: rotacja RN w **C2 jest NIEMOŻLIWA** - wszystkie nagrzewnice N5-N8 muszą pracować (brak nagrzewnicy rezerwowej)

**Koordynacja z Algorytmem RC (Rotacja Układów):**

**WAŻNE - W S1-S4 pracuje TYLKO JEDEN ciąg na raz (nie oba jednocześnie!):**
- Gdy aktywny jest **Układ Podstawowy**: pracuje **TYLKO C1**, rotacja RN dotyczy **C1** (priorytet 1)
- Gdy aktywny jest **Układ Ograniczony**: pracuje **TYLKO C2**, rotacja RN dotyczy **C2** (priorytet 1)
- Algorytm RC przełącza między układami → zmiana który ciąg pracuje

**Zasady koordynacji:**
- Po zmianie układu (RC) poczekaj min. **1 godzinę** przed rotacją nagrzewnic (RN)
- Priorytet ma zawsze **ciąg aktualnie pracujący** (w S1-S4 to jeden ciąg, w S5-S8 to oba ciągi, ale C2 ma priorytet rotacji bo C1 nie może rotować)

**Zasada odstępu:** Nie wykonuj rotacji w dwóch ciągach jednocześnie - zachowaj min. 15 minut odstępu między rotacjami.

**Uzasadnienie odstępu 15 minut:**
- Stabilność systemu (uniknięcie podwójnych perturbacji temperatury)
- Łatwiejsza diagnostyka problemów (wiadomo który ciąg jest przyczyną)
- Czas na reakcję operatora/SCADA w przypadku nieprawidłowości

## 7. Obsługa Stanów Awaryjnych

| Stan Awaryjny | Reakcja Systemu |
|---------------|-----------------|
| Nagrzewnica nowa nie osiąga temperatury | Wycofaj zmianę, przywróć N_starą, alarm |
| Awaria zaworu podczas rotacji | Zatrzymaj rotację, utrzymaj aktualny stan, alarm krytyczny |
| Wentylator zatrzymał się podczas rotacji | Natychmiastowe wyłączenie obu nagrzewnic, alarm krytyczny |
| Temperatura szybu spadła o >1°C | Przerwij rotację, przywróć N_starą, zwiększ moc |
| Przekroczenie czasu rotacji (>5 min) | Przerwij rotację, alarm, przejście na tryb MANUAL |

## 9. Przykłady Działania

#### **Przykład 1: Scenariusz S3 (3 nagrzewnice)**

**Warunki początkowe:**
- Temperatura: -6°C → Scenariusz S3
- Ciąg 1: 4 nagrzewnice sprawne
- Aktualnie pracują: N1, N2, N3
- OKRES_ROTACJI_NAGRZEWNIC = 168h (7 dni)
- Moment: System po pierwszym tygodniu pracy, przed pierwszą rotacją
- Czasy pracy: N1=168h, N2=168h, N3=168h, N4=0h

**Przebieg rotacji:**

1. **Dzień 0** - System w konfiguracji początkowej
   ```
   Czasy: N1=168h, N2=168h, N3=168h, N4=0h
   Pracują: [N1, N2, N3]  ← 3 nagrzewnice
   Postój:  [N4]
   ```

2. **Dzień 7** - Pierwsza rotacja (upłynęło 168h)
   ```
   Analiza:
   - Najdłużej pracująca: N1, N2, N3 (wszystkie 336h) - wybór N1 (najwcześniejszy timestamp załączenia)
   - Najdłużej postój: N4 (168h postoju)
   - Delta: 336h - 0h = 336h > MIN_DELTA_CZASU
   
   Akcja: Wymiana N1 → N4
   
   Sekwencja czasowa:
   t=0s:   Pracują: [N1, N2, N3]           ← 3 nagrzewnice
   t=5s:   Załączanie N4...
   t=35s:  Pracują: [N1, N2, N3, N4]       ← 4 nagrzewnice (WIĘCEJ!)
           PID wentylatora kompensuje (zmniejsza prędkość)
   t=65s:  N4 zweryfikowana (50°C) 
   t=65s:  Rozpoczęcie wyłączania N1...
   t=95s:  Pracują: [N2, N3, N4]           ← 3 nagrzewnice
   
   Po rotacji:
   Czasy: N1=336h, N2=336h, N3=336h, N4=0h
   Pracują: [N2, N3, N4]
   Postój:  [N1]
   ```

**Kluczowa obserwacja:**
- Przez ~30 sekund (t=35s do t=65s) pracują 4 nagrzewnice zamiast 3
- To jest **zamierzone** dla bezpieczeństwa
- PID wentylatora automatycznie redukuje prędkość 
- Gdyby N4 nie zadziałała, N1 nadal pracuje - system bezpieczny

3. **Dzień 14** - Druga rotacja
   ```
   Czasy pracy: N1=336h (postój 168h), N2=504h, N3=504h, N4=168h
   
   Analiza:
   - Najdłużej pracująca: N2, N3 (obie 504h) - wybór N2 (wcześniejszy timestamp załączenia niż N3)
   - Najdłużej postój: N1 (168h postoju)
   
   Akcja: Wyłącz N2, załącz N1
   
   Po rotacji:
   Czasy: N1=336h, N2=504h, N3=504h, N4=168h
   Pracują: [N3, N4, N1]
   Postój:  [N2]
   ```

4. **Dzień 21** - Trzecia rotacja
   ```
   Czasy pracy: N1=504h, N2=504h (postój 168h), N3=672h, N4=336h
   
   Analiza:
   - Najdłużej pracująca: N3 (672h)
   - Najdłużej postój: N2 (168h postoju)
   
   Akcja: Wyłącz N3, załącz N2
   
   Po rotacji:
   Czasy: N1=504h, N2=504h, N3=672h, N4=336h
   Pracują: [N4, N1, N2]
   Postój:  [N3]
   ```

5. **Dzień 28** - Czwarta rotacja
   ```
   Czasy pracy: N1=672h, N2=672h, N3=672h (postój 168h), N4=504h
   
   Analiza:
   - Najdłużej pracująca: N1, N2 (obie 672h) - wybór wg timestamp (ta załączona wcześniej)
   - Najdłużej postój: N3 (168h postoju)
   
   Akcja: Wyłącz N1, załącz N3
   
   Po rotacji:
   Czasy: N1=672h, N2=672h, N3=672h, N4=504h
   Pracują: [N4, N2, N3]
   Postój:  [N1]
   ```

**Rezultat po 4 tygodniach:**
- N1: 672h pracy ≈ 26.7% (ideał: 25%) → odchylenie +1.7%
- N2: 672h pracy ≈ 26.7% (ideał: 25%) → odchylenie +1.7%
- N3: 672h pracy ≈ 26.7% (ideał: 25%) → odchylenie +1.7%
- N4: 504h pracy ≈ 20.0% (ideał: 25%) → odchylenie -5.0%
- **Suma:** 2520h
- **Różnica max-min:** 672h - 504h = 168h (1 okres rotacji)
- **Wyrównanie:** ~93% (max odchylenie od średniej 630h to tylko 6.7%)

**Po 3 miesiącach** (12 tygodni = 2016h):
- Wszystkie nagrzewnice: ~1512h ± 50h
- **Różnica max-min:** ~84h (0.5 okresu rotacji)
- **Wyrównanie:** > 95% 

#### **Przykład 2: Dynamiczna zmiana scenariuszy**

**Sytuacja:** Temperatura oscyluje między S2 a S3

```
Dzień 1-3: S3 (N1, N2, N3) - 72h
Dzień 4-5: S2 (N1, N2) - 48h     → N3 idzie w postój
Dzień 6-7: S3 (N1, N2, N3) - 48h → N3 wraca do pracy
```

**Algorytm dostosowuje się:**
- Licznik czasu pracy N3: 72h + 48h = 120h (postój nie jest liczony podwójnie)
- Licznik postoju N3: 48h
- N4 cały czas w postoju: 168h
- Po tygodniu: rotacja N1 → N4 (N1 ma najwięcej godzin)

## 10. Integracja z Rotacją Układów (Sekcja RC)

**Koordynacja dwóch algorytmów rotacji:**

1. **Rotacja układów** (RC) - zmienia CIĄG (C1 ↔ C2)
   - Okres: tygodnie/miesiące
   - Dotyczy wyboru: C1 vs C2

2. **Rotacja nagrzewnic** (RN) - zmienia NAGRZEWNICĘ w ciągu
   - Okres: dni/tygodnie
   - Dotyczy wyboru: N1/N2/N3/N4 w C1 lub N5/N6/N7/N8 w C2

**Zasady koordynacji:**
- Nie wykonuj rotacji nagrzewnic w ciągu, który jest w trakcie zmiany układu
- Po zmianie układu (RC) poczekaj min. 1h przed rotacją nagrzewnic (RN)
- Jeśli zbiegły się oba okresy rotacji → najpierw rotacja układów (RC), potem nagrzewnic (RN) z odstępem min. 1h

**WAŻNE - Przesunięcie faz rotacji:**

Jeśli oba algorytmy (RC i RN) mają ten sam okres (np. 168h), NIE MOGĄ wykonać rotacji w tym samym momencie. System musi zapewnić przesunięcie faz aby uniknąć:
- Podwójnej perturbacji systemu (zmiana układu + zmiana nagrzewnicy)
- Trudności w diagnostyce (niejednoznaczność przyczyny zmian temperatury)

**Rozwiązania:**
1. **Różne okresy rotacji** - np. RC: 10 dni, RN: 7 dni
2. **Przesunięcie fazy startowej** - np. RC start w dniu 0, RN start w dniu 3
3. **Logika zapobiegania kolizji** - jeśli obie rotacje przypadają tego samego dnia, wykonaj tylko RC, a RN przełóż o 1 dzień

**Przykład (zakłada przesunięcie faz):**
```
Dzień 0:  Układ Podstawowy, C1: N1, N2, N3
Dzień 7:  Rotacja nagrzewnic (RN) → C1: N2, N3, N4
Dzień 14: Rotacja układów (RC) → Układ Ograniczony, C2: N5, N6, N7
Dzień 21: Rotacja nagrzewnic (RN) → C2: N6, N7, N8
Dzień 28: Rotacja układów (RC) → Układ Podstawowy, C1: N2, N3, N4
```
*Uwaga: W tym przykładzie okresy są różne lub fazy przesunięte, więc rotacje nie kolidują.*

**Efekt końcowy:**
- Równomierne zużycie wszystkich 8 nagrzewnic
- Równomierne zużycie obu ciągów (W1, W2)
- Maksymalna niezawodność systemu

UWAGA: Powyzsze wyliczenia trzeba potwierdzic w symulacji z roznymi scenariuszami i okresami rotacji

## RN.11 Wizualizacja Koordynacji Algorytmów RC i RN

**Diagram Timeline - Przykładowy Scenariusz S3:**

![Koordynacja RC ↔ RN](./schematy/koordynacja-RC-RN-timeline.svg)

Diagram timeline pokazuje praktyczny przykład koordynacji między algorytmami w scenariuszu S3:

**Kluczowe elementy wizualizacji:**
1. **Timeline zdarzeń** (0h → 410h):
   - T=0h: System w układzie Podstawowym, C1 aktywny
   - T=168h: Algorytm RN rotuje nagrzewnice w C1 (N1 → N4)
   - T=168h+2min: Algorytm RC próbuje zmienić układ → **BLOKADA** (RN rotuje)
   - T=168h+5min: RN kończy, RC wykonuje zmianę układu
   - T=169h: Układ Ograniczony, C2 aktywny
   - T=169h+15min: RN próbuje rotować w C2 → **ODROCZONE** (odstęp 1h)
   - T=170h: RN może rotować w C2 (upłynęła 1h od zmiany układu)

2. **Blokady (Mutex)**:
   - `zmiana_układu_w_toku`: chroni przed rotacją nagrzewnic podczas zmiany układu
   - `rotacja_nagrzewnic_w_toku`: chroni przed zmianą układu podczas rotacji nagrzewnic

3. **Odstępy czasowe**:
   - **1 godzina**: po zmianie układu (RC) przed rotacją nagrzewnic (RN)
   - **15 minut**: między rotacjami w różnych ciągach

**Wnioski z diagramu:**
- System **NIGDY** nie wykonuje dwóch operacji jednocześnie
- Wszystkie blokady są dwukierunkowe (RC ↔ RN)
- Odstępy czasowe zapewniają stabilność temperatury
- Mechanizmy są zaimplementowane w pseudokodzie (KROK 0, KROK 2, KROK 4)

---

## Powiązane Dokumenty

- **[System sterowania](../01-system/system.md)** - przegląd systemu, architektura SAR, tabela scenariuszy
- **[Projekt instalacji](../02-projekt-instalacji/projekt-instalacji.md)** - schematy instalacji, UAR, scenariusze z diagramami
- **[System SCADA/HMI](../04-scada-hmi/scada-hmi.md)** - interfejs operatorski, wizualizacja, alarmy, trendy
- **[Dokumentacja wejściowa](../01-system/dokumentacja-wejsciowa/Projekt%20instalacji%20ogrzewania%20szybu.md)** - pliki otrzymane od zleceniodawcy

---

**Ostatnia aktualizacja:** 25 Listopad 2025  
**Wersja dokumentu:** 2.1 - Dodano parametry czasowe sprzętu (Equipment Timing)
