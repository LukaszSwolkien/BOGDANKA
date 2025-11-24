# Symulacja Sterowania Nagrzewnicami BOGDANKA Szyb 2

## Prezentacja Wizualizacji Systemu SCADA/HMI

Ten dokument przedstawia symulację interfejsu operatorskiego (HMI) dla systemu sterowania nagrzewnicami i wentylatorami w szybie kopalnianym. System wizualizuje działanie układów automatycznej regulacji (UAR) w zależności od temperatury zewnętrznej.

[Wymagania dla systemu sterowania](../01-system/system.md)

---

## Panel Główny - Ekran Synoptyczny

### Schemat Bazowy Instalacji

![Nawiew z dwóch ciągów wentylacyjnych](./schematy/nawiew_z_dwoch_ciagow_wentylacyjnych.svg)

Rys. Nawiew powietrza ogrzanego z wykorzystaniem dwóch ciągów wentylacyjnych.

![Nawiew z dolnego ciągu wentylacyjnego](./schematy/nawiew_z_dolnego_ciagu_wentylacyjnego.svg)

Rys. Nawiew powietrza ogrzanego do wyrzutni poziomu 4,30 m z wykorzystaniem drugiego ciągu wentylacyjnego.


**Opis:**
- Schemat przedstawia kompletny układ nawiewu powietrza ogrzanego
- 8 nagrzewnic (N1-N8) w dwóch ciągach wentylacyjnych
- 2 wentylatory (W1, W2) z silnikami elektrycznymi
- System przepustnic i zaworów regulacyjnych
- Dwa poziomy wyrzutni: +4,30m i +7,90m

---

## Scenariusze Pracy Systemu

System automatycznie przełącza się między scenariuszami pracy w zależności od temperatury zewnętrznej (t_zewn) oraz algorytmów rotacji:

**Scenariusze bazowe (S0-S8):** 9 scenariuszy zależnych od temperatury  
**Algorytm RC:** Rotacja układów pracy ciągów (Podstawowy ↔ Ograniczony)  
**Algorytm RN:** Rotacja nagrzewnic w obrębie ciągu

### Scenariusz S0: Brak Ogrzewania
**Warunki:** t ≥ 3°C | **Nagrzewnice:** Brak | **Wentylatory:** Brak

![Scenariusz S0](../01-system/scenariusze/S0-brak-ogrzewania.svg)

**Stan systemu:**
- Wszystkie nagrzewnice wyłączone
- Wszystkie wentylatory wyłączone
- Wszystkie zawory zamknięte (Z)
- Brak przepływu powietrza (przepustnice zamknięte)
- System w trybie czuwania - oszczędzanie energii

---

### Scenariusz S1: Minimalne Ogrzewanie
**Warunki:** -1°C < t ≤ 2°C | **Nagrzewnice:** N1 | **Wentylatory:** W1

![Scenariusz S1](../01-system/scenariusze/S1-minimalne-ogrzewanie.svg)

**Stan systemu:**
- Nagrzewnica N1 aktywna (zielona)
- Wentylator W1 pracuje
- Nawiew do wyrzutni poziom 4,30m
- Temp. docelowa: 50°C na wylocie z N1

---

### Scenariusz S2: Dwie Nagrzewnice
**Warunki:** -4°C < t ≤ -1°C | **Nagrzewnice:** N1-N2 | **Wentylatory:** W1

![Scenariusz S2](../01-system/scenariusze/S2-dwie-nagrzewnice.svg)

**Stan systemu:**
- Nagrzewnice N1, N2 aktywne
- Wentylator W1 pracuje
- Nawiew do wyrzutni poziom 4,30m
- Zwiększona moc grzewcza przy spadku temperatury

---

### Scenariusz S3: Trzy Nagrzewnice
**Warunki:** -8°C < t ≤ -4°C | **Nagrzewnice:** N1-N3 | **Wentylatory:** W1

![Scenariusz S3](../01-system/scenariusze/S3-trzy-nagrzewnice.svg)

**Stan systemu:**
- Nagrzewnice N1, N2, N3 aktywne
- Wentylator W1 pracuje na wyższej mocy
- Nawiew do wyrzutni poziom +4,30m
- Stopniowe zwiększanie mocy grzewczej

---

### Scenariusz S4: Pełny Górny Ciąg
**Warunki:** -11°C < t ≤ -8°C | **Nagrzewnice:** N1-N4 | **Wentylatory:** W1

![Scenariusz S4](../01-system/scenariusze/S4-pelny-gorny-ciag.svg)

**Stan systemu:**
- Wszystkie nagrzewnice górnego ciągu (N1-N4) aktywne
- Wentylator W1 w pełnej mocy
- Nawiew do wyrzutni poziom +4,30m
- Maksymalna moc górnego ciągu

---

### Scenariusz S5: Uruchomienie Dolnego Ciągu
**Warunki:** -15°C < t ≤ -11°C | **Nagrzewnice:** N1-N5 | **Wentylatory:** W1 (MAX), W2 (PID)

![Scenariusz S5](../01-system/scenariusze/S5-uruchomienie-dolnego-ciagu.svg)

**Stan systemu:**
- Nagrzewnice N1-N5 aktywne (wszystkie z ciągu 1 + jedna z ciągu 2)
- Wentylator W1 pracuje z maksymalną prędkością (50 Hz)
- Wentylator W2 sterowany regulatorem PID (25-50 Hz)
- **Nawiew na OBA poziomy: +4,30m i +7,90m**
- Uruchomienie drugiego ciągu wentylacyjnego
- Znaczące zwiększenie mocy grzewczej

---

### Scenariusz S6: Sześć Nagrzewnic
**Warunki:** -18°C < t ≤ -15°C | **Nagrzewnice:** N1-N6 | **Wentylatory:** W1 (MAX), W2 (PID)

![Scenariusz S6](../01-system/scenariusze/S6-szesc-nagrzewnic.svg)

**Stan systemu:**
- Nagrzewnice N1-N6 aktywne (cały ciąg 1 + dwie z ciągu 2)
- Wentylator W1 pracuje z maksymalną prędkością (50 Hz)
- Wentylator W2 sterowany regulatorem PID (25-50 Hz)
- **Nawiew na OBA poziomy: +4,30m i +7,90m**
- Zwiększona moc dolnego ciągu (N5-N6)

---

### Scenariusz S7: Siedem Nagrzewnic
**Warunki:** -21°C < t ≤ -18°C | **Nagrzewnice:** N1-N7 | **Wentylatory:** W1 (MAX), W2 (PID)

![Scenariusz S7](../01-system/scenariusze/S7-siedem-nagrzewnic.svg)

**Stan systemu:**
- Nagrzewnice N1-N7 aktywne (cały ciąg 1 + trzy z ciągu 2)
- Wentylator W1 pracuje z maksymalną prędkością (50 Hz)
- Wentylator W2 sterowany regulatorem PID (25-50 Hz)
- **Nawiew na OBA poziomy: +4,30m i +7,90m**
- Bardzo niskie temperatury zewnętrzne

---

### Scenariusz S8: Maksymalne Obciążenie
**Warunki:** t ≤ -21°C | **Nagrzewnice:** N1-N8 | **Wentylatory:** W1 (MAX), W2 (PID)

![Scenariusz S8](../01-system/scenariusze/S8-maksymalne-obciazenie.svg)

**Stan systemu:**
- WSZYSTKIE nagrzewnice N1-N8 aktywne (wszystkie z obu ciągów)
- Wentylator W1 pracuje z maksymalną prędkością (50 Hz)
- Wentylator W2 sterowany regulatorem PID (25-50 Hz)
- **Nawiew na OBA poziomy: +4,30m i +7,90m**
- System działa na maksymalnym obciążeniu - pełna moc obu ciągów

---

## Algorytmy Sterowania - Wizualizacje

System wykorzystuje **trzy współpracujące algorytmy** zapewniające automatyczne sterowanie i równomierne rozłożenie eksploatacji urządzeń:
- **Algorytm WS:** Automatyczny Wybór Scenariusza Pracy (S0-S8) - fundament sterowania
- **Algorytm RC:** Rotacja Układów Pracy Ciągów (C1 ↔ C2)
- **Algorytm RN:** Rotacja Nagrzewnic w Obrębie Ciągu

### Algorytm WS: Automatyczny Wybór Scenariusza

**Cel algorytmu:**
- Automatyczny dobór scenariusza (S0-S8) w zależności od temperatury zewnętrznej
- Określa ILE nagrzewnic potrzeba do utrzymania 2°C w szybie
- Ciągły monitoring temperatury z histerezą przy wyłączaniu
- Bezpieczne sekwencje przejść między scenariuszami

**Kluczowe elementy:**
- Odczyt i walidacja temperatury zewnętrznej (z filtrem uśredniania)
- Drzewo decyzyjne wyboru scenariusza (z histerezami)
- Sprawdzenie warunków stabilności i trybu pracy (AUTO/MANUAL)
- Wykonanie sekwencji zmiany scenariusza
- Koordynacja z algorytmami 5A i 5B

#### Diagram Przepływu Algorytmu 5

![Algorytm 5 - Wybór Scenariusza](../02-algorytmy/schematy/algorytm-WS-wybor-scenariusza-flowchart.svg)

**Opis flowchartu:**
- **KROK 1:** Odczyt czujnika t_zewn z filtrem uśredniania (3 próbki)
- **KROK 2:** Określenie wymaganego scenariusza na podstawie drzewa decyzyjnego
  - t ≥ 3°C → S0 (brak ogrzewania)
  - -1°C < t ≤ 2°C → S1 (1 nagrzewnica)
  - -4°C < t ≤ -1°C → S2 (2 nagrzewnice)
  - ... itd. aż do S8 (8 nagrzewnic przy t ≤ -21°C)
- **KROK 3:** Sprawdzenie czy wymagana zmiana scenariusza
  - Uwzględnienie czasu stabilizacji (60s)
  - Sprawdzenie trybu AUTO/MANUAL
- **KROK 4:** Wykonanie zmiany scenariusza (sekwencja bezpieczna)
  - Zatrzymanie zbędnych nagrzewnic
  - Konfiguracja wentylatorów (PID/MAX/OFF)
  - Uruchomienie dodatkowych nagrzewnic
- **KROK 5:** Aktualizacja statystyk i monitoringu

**Obsługa awarii czujnika:**
- Przy braku odczytu → utrzymanie ostatniego scenariusza przez 300s
- Po przekroczeniu czasu → alarm krytyczny i przełączenie na tryb MANUAL

**Histereza temperaturowa:**
- Różne progi dla włączania i wyłączania (zapobiega oscylacjom)
- Przykład S3: włączenie przy -4°C, wyłączenie dopiero przy -3°C (1°C histerezy)

**Sekwencje zmian scenariuszy:**
- Każda zmiana (np. S4→S5) wymaga skoordynowanej sekwencji operacji
- Zarządzanie zaworami wody (20-100%), przepustnicami, wentylatorami
- Przejście S4→S5 jest najbardziej złożone (uruchomienie drugiego ciągu)

📖 **[Szczegółowy algorytm → Algorytmy_rotacji.md - Sekcja 5](Doc/Algorytmy_rotacji.md#5-algorytm-automatycznego-wyboru-scenariusza-pracy)**

📖 **[Sekwencje zmian scenariuszy → Algorytmy_rotacji.md - Sekcja 5.10](Doc/Algorytmy_rotacji.md#510-szczegółowe-sekwencje-zmian-scenariuszy)**

---

### Rotacja 5A: Układ Podstawowy vs Układ Ograniczony

System okresowo zmienia układ pracy między **Podstawowym** a **Ograniczonym** w scenariuszach S1-S4 w celu wyrównania eksploatacji ciągów.

**Cel rotacji 5A:**
- Wyrównanie eksploatacji W1 i W2
- Okres rotacji: definiowany przez technologa (np. 168h / 7 dni)
- Po upływie okresu system przełącza się: Podstawowy → Ograniczony → Podstawowy

**Zasada działania:**
- **Układ Podstawowy:** Ciąg 1 (N1-N4) + W1 → nawiew na +4,30m
- **Układ Ograniczony:** Ciąg 2 (N5-N8) + W2 → nawiew przez **spinę ciągów** na +4,30m

#### Diagram Przepływu Algorytmu 5A

![Algorytm RC - Flowchart](../02-algorytmy/schematy/algorytm-RC-rotacja-ciagow-flowchart.svg)

**Opis algorytmu:**
- **Główna pętla:** Wykonywana co CYKL_PĘTLI_ALGORYTMÓW (domyślnie 60s = 1 minuta, zakres 10-600s)
- **Krok 1:** Sprawdzenie warunków rotacji (scenariusz S1-S4, gotowość C2, tryb AUTO)
- **Krok 2:** Sprawdzenie czy upłynął okres rotacji (OKRES_ROTACJI_UKŁADÓW)
- **Krok 3:** Określenie nowego układu (Podstawowy ↔ Ograniczony)
- **Krok 4:** Wykonanie sekwencji zmiany układu (z koordynacją z Algorytmem 5B)
- **Krok 5:** Aktualizacja liczników czasu pracy

---

#### S1: Rotacja przy minimalnym ogrzewaniu (1 nagrzewnica)

**Zakres temperatur:** -1°C < t ≤ 2°C

| Układ | Nagrzewnice | Wentylator | Wizualizacja |
|-------|-------------|------------|--------------|
| **Podstawowy** | N1 | W1 PID | ![S1 Podstawowy](../01-system/scenariusze/S1-minimalne-ogrzewanie.svg) |
| **Ograniczony** | N5 | W2 PID | ![S1 Ograniczony](../02-algorytmy/schematy/RC-uklad-ograniczony-S1.svg) |

**Charakterystyka układu ograniczonego:**
- Spinka ciągów: **OTWARTA**
- Przepustnica C1: **ZAMKNIĘTA**
- Nawiew przez spinę na +4,30m

---

#### S2: Rotacja przy umiarkowanym ogrzewaniu (2 nagrzewnice)

**Zakres temperatur:** -4°C < t ≤ -1°C

| Układ | Nagrzewnice | Wentylator | Wizualizacja |
|-------|-------------|------------|--------------|
| **Podstawowy** | N1, N2 | W1 PID | ![S2 Podstawowy](../01-system/scenariusze/S2-dwie-nagrzewnice.svg) |
| **Ograniczony** | N5, N6 | W2 PID | ![S2 Ograniczony](../02-algorytmy/schematy/RC-uklad-ograniczony-S2.svg) |

**Charakterystyka układu ograniczonego:**
- Spinka ciągów: **OTWARTA**
- Przepustnica C1: **ZAMKNIĘTA**
- Nawiew przez spinę na +4,30m

---

#### S3: Rotacja przy średnim ogrzewaniu (3 nagrzewnice)

**Zakres temperatur:** -8°C < t ≤ -4°C

| Układ | Nagrzewnice | Wentylator | Wizualizacja |
|-------|-------------|------------|--------------|
| **Podstawowy** | N1, N2, N3 | W1 PID | ![S3 Podstawowy](../01-system/scenariusze/S3-trzy-nagrzewnice.svg) |
| **Ograniczony** | N5, N6, N7 | W2 PID | ![S3 Ograniczony](../02-algorytmy/schematy/RC-uklad-ograniczony-S3.svg) |

**Charakterystyka układu ograniczonego:**
- Spinka ciągów: **OTWARTA**
- Przepustnica C1: **ZAMKNIĘTA**
- Nawiew przez spinę na +4,30m

---

#### S4: Rotacja przy wysokim ogrzewaniu (4 nagrzewnice)

**Zakres temperatur:** -11°C < t ≤ -8°C

| Układ | Nagrzewnice | Wentylator | Wizualizacja |
|-------|-------------|------------|--------------|
| **Podstawowy** | N1-N4 | W1 PID | ![S4 Podstawowy](../01-system/scenariusze/S4-pelny-gorny-ciag.svg) |
| **Ograniczony** | N5-N8 | W2 PID | ![S4 Ograniczony](../02-algorytmy/schematy/RC-uklad-ograniczony-S4.svg) |

**Charakterystyka układu ograniczonego:**
- Spinka ciągów: **OTWARTA**
- Przepustnica C1: **ZAMKNIĘTA**
- Nawiew przez spinę na +4,30m
- **Uwaga:** Cały ciąg 2 aktywny (wszystkie 4 nagrzewnice)

---

**Uwagi do rotacji 5A:**
- Rotacja działa **tylko** w scenariuszach S1-S4 (temperatury umiarkowane)
- W scenariuszach S5-S8 rotacja **nie jest stosowana** - system zawsze pracuje w układzie Podstawowym z możliwością dogrz ewania przez ciąg 2
- Przełączenie między układami odbywa się **automatycznie** po upływie `OKRES_ROTACJI_UKŁADÓW`
- Warunkiem przełączenia jest gotowość ciągu 2 i stabilność systemu

---

### Rotacja 5B: Wymiana Nagrzewnic w Ciągu

**Diagram algorytmu rotacji nagrzewnic:**

![Algorytm RN Flowchart](../02-algorytmy/schematy/algorytm-RN-rotacja-nagrzewnic-flowchart.svg)

**Przykład zastosowania algorytmu dla S3 (3 nagrzewnice w ciągu):**

#### Tydzień 1: N1, N2, N3
![S3 Rotacja - Tydzień 1](../01-system/scenariusze/S3-trzy-nagrzewnice.svg)

**Pracują:** N1 (najstarsza), N2, N3  
**Postój:** N4

#### Tydzień 2: N2, N3, N4

![Rotacja 5B - Tydzień 2](../02-algorytmy/schematy/RN-rotacja-tydzien2-S3.svg)

**Pracują:** N2, N3, N4 (najnowsza)  
**Postój:** N1 (odpoczynek po najdłuższym czasie pracy)  
**Akcja:** Wyłączono N1, załączono N4

#### Tydzień 3: N3, N4, N1

![Rotacja 5B - Tydzień 3](../02-algorytmy/schematy/RN-rotacja-tydzien3-S3.svg)

**Pracują:** N3, N4, N1  
**Postój:** N2 (odpoczynek)  
**Akcja:** Wyłączono N2, załączono N1

#### Tydzień 4: N4, N1, N2

![Rotacja 5B - Tydzień 4](../02-algorytmy/schematy/RN-rotacja-tydzien4-S3.svg)

**Pracują:** N4, N1, N2  
**Postój:** N3 (odpoczynek)  
**Akcja:** Wyłączono N3, załączono N2

**Cel rotacji 5B:**
- Równomierne zużycie wszystkich nagrzewnic w ciągu
- Okres rotacji: definiowany przez technologa (np. 168h / 7 dni)
- Po 3 miesiącach: > 90% wyrównania czasu pracy wszystkich nagrzewnic

**Zasada:** Najdłużej pracująca → Postój, Najdłużej w postoju → Praca

---

## Układy Automatycznej Regulacji (UAR)

### 1. UAR Temperatury Powietrza - Schemat Ogólny

![Schemat UAR temperatury](./schematy/uar-nagrzewnica.svg)

**Opis działania:**
- **Regulator PID** porównuje temperaturę zadaną (Tz=50°C) z temperaturą mierzoną
- **Sygnał sterujący (CV)** kontroluje zawór regulacyjny wody grzewczej (20-100%)
- **Zawór regulacyjny** zmienia przepływ gorącej wody przez nagrzewnicę
- **Czujnik temperatury** mierzy temperaturę powietrza na wylocie
- **Pętla sprzężenia zwrotnego** zapewnia automatyczną regulację
- 🔴 Woda grzewcza (zasilanie) - czerwona linia
- 🔵 Woda powrotna - niebieska linia
- 🟢 Sygnały sterujące/pomiarowe - ciemnozielone przerywane linie

---

### 2. UAR Nagrzewnicy - Stan Aktywny


**Stan - Nagrzewnica w pracy:**
- **Regulator PID w trybie REGULACJA**
  - SP (setpoint) = 50°C
  - PV (process variable) = temperatura mierzona
  - CV (control variable) = 20-100% (zmienne)

- **Zawór regulacyjny**
  - Regulowany w zakresie 20-100%

- **Przepustnice otwarte**
  - Pełny przepływ powietrza przez nagrzewnicę

- **Pętla sprzężenia zwrotnego**
  - Ciągła korekta temperatury
  - Automatyczna kompensacja zaburzeń

---

### 3. UAR Nagrzewnicy - Stan Nieaktywny


**Stan - Nagrzewnica wyłączona:**
- **Regulator PID w trybie UTRZYMANIE**
  - Utrzymuje zawór na stałej pozycji 20%
  - SP = CV = 20% (stałe)
  - PV = ignorowane (temperatura nie jest używana)

- **Zawór regulacyjny**
  - Utrzymywany na stałej pozycji 20%
  - Ochrona przed zamrożeniem

- **Przepustnice zamknięte**
  - Brak przepływu powietrza
  - Nagrzewnica nie oddaje ciepła

- **Sekwencja wyłączania (STOPPING → OFF):**
  1. PID zamyka zawór z aktualnej pozycji do 20%
  2. Zawór ustabilizowany na 20%
  3. Zamykanie przepustnic

---

### 4. UAR Prędkości Wentylatora

![UAR Prędkość Wentylatora](./schematy/uar-wentylator.svg)

**Opis działania:**
- **Regulator PID** utrzymuje temperaturę w szybie (Ts=2°C na poziomie -30m)
- **Sygnał sterujący (CV)** kontroluje częstotliwość (25-50 Hz)
- **Przetwornica częstotliwości (Falownik)**
  - Konwertuje sygnał PID na zmienną częstotliwość
  - Wyjście: 400V 3~ o częstotliwości 25-50 Hz
  
- **Wentylator (W1/W2)**
  - W1 obsługuje nagrzewnice N1-N4 (poziom 4,30m)
  - W2 obsługuje nagrzewnice N5-N8 (poziom 7,90m)
  - Wydajność zależy od prędkości obrotowej

- **Czujnik temperatury w szybie**
  - Poziom -30m
  - Sprzężenie zwrotne do regulatora w kazdym ciągu

**Logika regulacji:**
- 🔻 T_szyb ↓ (za zimno) → PID ↑ częstotliwość → silnik szybciej → więcej ciepłego powietrza
- 🔺 T_szyb ↑ (za ciepło) → PID ↓ częstotliwość → silnik wolniej → mniej ciepłego powietrza

---

## Panel HMI - Elementy Wizualizacji

### Kolory i Konwencje Wizualne

#### Stan Elementów:
- 🟢 **Zielony** - Element aktywny, pracujący
- ⚪ **Szary** - Element nieaktywny, wyłączony
- 🔴 **Czerwony** - Awaria, alarm
- 🟡 **Żółty** - Ostrzeżenie, tryb przejściowy

#### Przepływy:
- **Linie ciągłe** (grube) - Aktywny przepływ
- **Linie przerywane** (cienkie) - Brak przepływu lub przepływ minimalny
- 🔴 **Czerwony** - Woda grzewcza (zasilanie, gorąca)
- 🔵 **Niebieski** - Woda powrotna (chłodniejsza)
- 🟢 **Ciemnozielony** - Sygnały sterujące/pomiarowe PID
- ⚪ **Szary** - Powietrze

#### Zawory:
- **Z** - Zamknięty
- **O** - Otwarty
- **%** - Pozycja w procentach (dla zaworów regulacyjnych)

---

## Główne Wskaźniki na Panelu HMI

### Temperatury:
- **t_zewn** - Temperatura zewnętrzna [°C]
- **Tz** - Temperatura zadana na wylocie z nagrzewnicy (50°C)
- **T_N1...T_N8** - Temperatury rzeczywiste na wylotach z nagrzewnic [°C]
- **Ts** - Temperatura zadana w szybie (2°C)
- **T_szyb** - Temperatura rzeczywista w szybie na poziomie -30m [°C]

### Parametry Wentylatorów:
- **W1_f** - Częstotliwość wentylatora W1 [Hz] (25-50)
- **W2_f** - Częstotliwość wentylatora W2 [Hz] (25-50)
- **W1_I** - Prąd silnika W1 [A]
- **W2_I** - Prąd silnika W2 [A]

### Zawory Regulacyjne:
- **Z_N1...Z_N8** - Pozycje zaworów regulacyjnych [%] (20-100)

### Statusy:
- **Scenariusz** - Aktualny scenariusz pracy (S0-S8)
- **Układ Pracy** - Podstawowy / Ograniczony
- **Tryb** - AUTO / MANUAL
- **Alarmy** - Lista aktywnych alarmów

### Rotacje (Algorytmy 5A i 5B):
- **Czas do rotacji układów (5A)** - Pozostały czas do zmiany układu [h]
- **Aktualny układ** - Podstawowy / Ograniczony
- **Czas pracy C1** - Łączny czas pracy ciągu 1 [h]
- **Czas pracy C2** - Łączny czas pracy ciągu 2 [h]
- **Stosunek C1/C2** - Proporcja eksploatacji (cel: ~1.0)
- **Czas do rotacji nagrzewnic (5B)** - Pozostały czas do wymiany nagrzewnicy [h]
- **Czasy pracy N1-N8** - Łączne czasy pracy poszczególnych nagrzewnic [h]
- **Liczba załączeń N1-N8** - Liczniki startów nagrzewnic

---

## Tryby Pracy Systemu

### Tryb AUTO (Automatyczny)
- System automatycznie wybiera scenariusz na podstawie t_zewn
- Regulatory PID aktywnie kontrolują:
  - Temperaturę powietrza (zawory N1-N8)
  - Temperaturę w szybie (wentylatory W1-W2)
- Automatyczne włączanie/wyłączanie nagrzewnic
- Automatyczna regulacja prędkości wentylatorów

### Tryb MANUAL (Ręczny)
- Operator ma pełną kontrolę nad systemem
- Możliwość ręcznego ustawienia:
  - Pozycji zaworów (20-100%)
  - Częstotliwości wentylatorów (25-50 Hz)
  - Włączenia/wyłączenia poszczególnych nagrzewnic
- Zabezpieczenia nadal aktywne (min. 20% zaworu, limity temperatur)

---

## System Alarmów

### Alarmy Krytyczne (Czerwone):
- 🔴 **Brak odczytu t_zewn** - Utrzymanie ostatniego stanu
- 🔴 **Temperatura > 60°C** - Zamknięcie zaworu do 20%
- 🔴 **Wentylator nie pracuje** - Wyłączenie odpowiednich nagrzewnic
- 🔴 **Temp. wody < 5°C** - Ryzyko zamrożenia

### Alarmy Ostrzegawcze (Żółte):
- 🟡 **Temperatura < 40°C** przy pracy - Zwiększenie otwarcia zaworu
- 🟡 **Przepustnica nie reaguje** - Kontynuacja pracy
- 🟡 **Zbyt długi czas nagrzewania** - Sprawdzenie parametrów PID

### Informacje (Niebieskie):
- 🔵 **Zmiana scenariusza** - Automatyczne przełączenie
- 🔵 **Przełączenie AUTO/MANUAL** - Zmiana trybu przez operatora
- 🔵 **Zmiana parametrów PID** - Modyfikacja nastaw

---

## Trendy Historyczne

Panel HMI umożliwia wyświetlanie trendów:
- Temperatura zewnętrzna (24h)
- Temperatura w szybie (24h)
- Temperatury na wylotach z nagrzewnic (8 krzywych)
- Pozycje zaworów regulacyjnych (8 krzywych)
- Częstotliwości wentylatorów (2 krzywe)
- Pobór mocy całkowity [kW]

---

## Parametry Nastaw PID

### UAR Temperatury Nagrzewnic (N1-N8):
```
Kp = [do określenia podczas rozruchu]
Ti = [do określenia podczas rozruchu]
Td = [do określenia podczas rozruchu]
Tz = 50°C (stała)
CV_min = 20% (ochrona antyzamrożeniowa)
CV_max = 100%
```

### UAR Prędkości Wentylatorów (W1, W2):
```
Kp = [do określenia podczas rozruchu]
Ti = [do określenia podczas rozruchu]
Td = [do określenia podczas rozruchu]
Ts = 2°C (stała)
f_min = 25 Hz (minimalna prędkość)
f_max = 50 Hz (maksymalna prędkość)
```

---

## Podsumowanie Funkcjonalności HMI

### Ekrany Dostępne w Systemie:
1. **Ekran Główny** - Synoptyka z aktualnym scenariuszem i układem pracy
2. **Szczegóły Nagrzewnic** - Parametry N1-N8, czasy pracy, liczba załączeń
3. **Szczegóły Wentylatorów** - Parametry W1-W2, czasy pracy ciągów
4. **Trendy** - Wykresy historyczne
5. **Alarmy** - Historia i aktywne alarmy
6. **Nastawy** - Parametry PID, temperatury zadane, okresy rotacji
7. **Diagnostyka** - Stan urządzeń i statystyki
8. **Rotacja 5A** - Historia zmian układów, stosunek eksploatacji C1/C2
9. **Rotacja 5B** - Czasy pracy nagrzewnic, predykcja następnej rotacji

### Możliwości Operatora:
- Monitoring wszystkich parametrów w czasie rzeczywistym
- Przełączanie trybu AUTO/MANUAL
- Ręczne sterowanie w trybie MANUAL
- Zmiana parametrów PID (z odpowiednimi uprawnieniami)
- Przeglądanie trendów historycznych
- Kwituowanie alarmów
- Export danych do raportów

---

## Notatki Implementacyjne

### Wymagania Techniczne:
- **Platforma SCADA**: iFix, WinCC, Wonderware, Ignition lub podobna
- **Komunikacja PLC**: Modbus TCP/RTU, OPC UA lub protokół właścicielski
- **Czas odświeżania**: 1s dla parametrów procesowych
- **Archiwizacja**: min. 1 rok danych historycznych
- **Rozdzielczość**: min. 1920x1080 dla pełnej wizualizacji

### Bezpieczeństwo:
- **Poziomy dostępu**:
  - Operator: monitoring, kwitowanie alarmów
  - Inżynier: zmiana trybu AUTO/MANUAL, ręczne sterowanie
  - Administrator: zmiana nastaw PID, konfiguracja systemu
- **Logi**: Zapis wszystkich akcji operatora
- **Backup**: Codzienne kopie bezpieczeństwa bazy danych

---

---

## Wizualizacje SVG

### Podsumowanie:
- **Łącznie plików SVG:** 23
- **Scenariusze podstawowe (S0-S8):** 9 plików
- **Schematy UAR:** 3 pliki
- **Rotacja 5A (Układy Ograniczone S1-S4):** 4 pliki
- **Rotacja 5B (Cykl nagrzewnic):** 3 pliki
- **Diagramy algorytmów:** 4 pliki
  - `algorytm_wybor_scenariusza_flowchart.svg` flowchart algorytmu 5 (wybór scenariusza)
  - `algorytm_5A_flowchart.svg` - flowchart algorytmu 5A (rotacja układów, z koordynacją 5B)
  - `algorytm_5B_flowchart.svg` - flowchart algorytmu 5B (rotacja nagrzewnic, z koordynacją 5A)
  - `algorytm_5A_5B_koordynacja.svg` - timeline diagram koordynacji 5A ↔ 5B

### Diagram Koordynacji Algorytmów 5A i 5B

![Koordynacja 5A ↔ 5B](../02-algorytmy/schematy/koordynacja-RC-RN-timeline.svg)

**Diagram timeline** pokazuje przykładową sekwencję zdarzeń dla scenariusza S3:
- Blokady (mutex) między algorytmami
- Odstępy czasowe (1h po zmianie układu, 15min między rotacjami)
- Mechanizmy zapobiegania konfliktom
- 10 kluczowych wydarzeń w czasie (0h → 410h)

**Uwaga:** 
- Rotacja 5A pokazana dla wszystkich scenariuszy S1-S4
- Rotacja 5B pokazana przykładowo dla S3
- Flowcharty 5A i 5B zaktualizowane z pełną koordynacją (KROK 0, blokady, odstępy)

---

**Ostatnia aktualizacja:** 2025-11-23  
**Wersja dokumentu:** 3.1  
**Status:** Kompletna dokumentacja z wizualizacjami algorytmów sterowania (5, 5A, 5B), sekwencjami zmian scenariuszy oraz diagramem koordynacji

