# System Sterowania Nagrzewnicami BOGDANKA Szyb 2

## 1. Dokumentacja od zleceniodawcy

### 1.1 Projekt instalacji ogrzewania szybu

Dokument otrzymany 19 listopad 2025:

[Projekt instalacji ogrzewania szybu - skan dokumentacji](Projekt%20instalacji%20ogrzewania%20szybu.pdf)

### 1.2 Diagram

Dokument otrzymany 17 listopada 2025:
![Algorytm sterowania - BOGDANKA - Szyb 2](assets/Algortym%20sterowania%20-%20BOGDANKA%20-%20Szyb%202%20v2.jpg)


# Opracowanie specyfikacji

**UWAGA** 
```Dokumentacja robocza - aktualizowana na podstawie otrzymywanych wymagan od zleceniodawcy```

Ostatnia aktualizacja: 18 Listopad 2025

## 2. Stany nagrzewnicy

```
- STARTING (uruchamianie - otwieranie przepustnic i zaworu do 100%)
- ON 🟢 (praca - regulacja zaworu wody)
- STOPPING (zatrzymywanie - zamykanie zaworu do 20%)
- OFF 🔴 (wyłączona - zamykanie przepustnic)
```

## 3. Tabela Stanów

Tabela definiująca stan systemu sterowania uzalezniony od temperatury zewnetrznej (tz)

| ID | Zakres Temperatury Zewnętrznej | Nagrzewnice Aktywne | Wentylatory Aktywne | Temp. Docelowa | Temp. Wyłączenia Dodatkowej Nagrzewnicy | Histereza |
|----|-------------------------------|---------------------|---------------------|----------------|----------------------------------------|-----------|
| S0 | t ≥ 3°C | brak  | brak | brak | brak | brak |
| S1 | -1°C < t ≤ 2°C | N1 | W1 | 50°C | t ≥ 3°C | 1°C |
| S2 | -4°C < t ≤ -1°C | N1, N2 | W1 | 50°C | t ≥ 0°C | 1°C |
| S3 | -8°C < t ≤ -4°C | N1, N2, N3 | W1 | 50°C | t ≥ -3°C | 1°C |
| S4 | -11°C < t ≤ -8°C | N1, N2, N3, N4 | W1 | 50°C | t ≥ -6°C | 2°C |
| S5 | -15°C < t ≤ -11°C | N1, N2, N3, N4, N5 | W1, W2 | 50°C | t ≥ -10°C | 1°C |
| S6 | -18°C < t ≤ -15°C | N1, N2, N3, N4, N5, N6, | W1, W2 | 50°C | t ≥ -13°C | 2°C |
| S7 | -21°C < t ≤ -18°C | N1, N2, N3, N4, N5, N6, N7 | W1, W2 | 50°C | t ≥ -15°C | 3°C |
| S8 | t ≤ -21°C | N1, N2, N3, N4, N5, N6, N7, N8 | W1, W2 | 50°C | t ≥ -20°C | 1°C |

## 4. Tabela Decyzyjna
Tabela definiujaca akcje na sterowanym elemencie w zaleznosci od warunku (zadanego stanu systemu sterowania). 

| Sterowany element \ Warunek | S0 | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
|----------------|----|----|----|----|----|----|----|----|----|
| **NAGRZEWNICE** |
| N1 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| N2 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| N3 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| N4 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| N5 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 |
| N6 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 |
| N7 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 |
| N8 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 |
| **WENTYLATORY** |
| W1 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| W2 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 |
| **PARAMETRY REGULACJI** |
| Temperatura docelowa (°C) | | 50 | 50 | 50 | 50 | 50 | 50 | 50 | 50 |
| Temp. włączenia dodatkowej nagrzewnicy (°C) | | 2 | -1 | -4 | -8 | -11 | -15 | -18 | -21 |
| Temp. wyłączenia dodatkowej nagrzewnicy (°C) | | 3 | 0 | -3 | -6 | -10 | -13 | -15 | -20 |
| Zawór regulacyjny przy wyłączeniu (%) | | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |


- Sterowanie (załączania/wyłączania) nagrzewnic
- Sterowanie zaworami regulacyjnymi ciepla woda (8 nagrzewnic)
- Sterowanie przepustnicami
- Sterowanie prędkością obrotową wentylatorów W1, W2 (25-50 Hz)

## 5. Parametry Systemowe

| Parameter | Wartość | Jednostka | Opis |
|-----------|---------|-----------|------|
| Temperatura docelowa | 50 | °C | Temperatura wyjściowa z nagrzewnicy |
| Pozycja zaworu przy stop | 20 | % | Otwarcie zaworu przed kolejnym startem |
| Czas stabilizacji | 5 | s | Czas na stabilizację przed odczytem |
| Okres próbkowania | 1 | s | Częstotliwość odczytu temperatury |
| Max pozycja zaworu | 100 | % | Maksymalne otwarcie zaworu |
| Min pozycja zaworu | 20 | % | Minimalne otwarcie zaworu, ochrona przed zamarzaniem |

## 6. Obsługa Awarii

| Warunek Awarii | Akcja |
|----------------|-------|
| Brak odczytu temperatury zewnętrznej | Zachowaj ostatni stan, alarm |
| Brak odczytu temperatury wylotowej | Ustaw zawór na 50%, alarm |
| Temperatura wylotowa > 60°C | Zamknij zawór do 20%, alarm |
| Temperatura wylotowa < 40°C przy pracy | Zwiększ otwarcie zaworu do 100%, alarm  |
| Wentylator nie pracuje | Wyłącz odpowiednie nagrzewnice, alarm |
| Przepustnica nie reaguje | Kontynuuj pracę, alarm |

## 7. Parametry Techniczne - Podsumowanie

| Parameter | Wartość | Uwagi |
|-----------|---------|-------|
| Liczba nagrzewnic | 8 (N1-N8) | Po 4 na ciąg |
| Liczba wentylatorów | 2 (W1, W2) | Sterowanie częstotliwościowe |
| Temperatura zadana Tz | 50°C | Powietrze na wylocie z nagrzewnicy |
| Temperatura zadana Ts | 2°C | Temperatura w szybie na -30m |
| Zakres częstotliwości wentylatorów | 25-50 Hz | NWmin - NWmax |
| Zakres otwarcia zaworu | 20-100% | Pzmin - Pzmax |
| Liczba poziomów wyrzutni | 2 | +4,30m i +7,90m |
| Sterowanie | PLC | Z regulatorami PID |

## 9. System SCADA/HMI - Wymagania Projektowe (na podstawie [Projekt instalacji ogrzewania szybu - skan dokumentacji](Projekt%20instalacji%20ogrzewania%20szybu.pdf) - do potwierdzenia!)

### 9.1 Architektura systemu monitoringu

System SCADA/HMI powinien zapewnić:

#### Poziom sterowania (PLC):
- Realizacja algorytmów regulacji PARTPG i PARTS
- Sterowanie regulatorami PID
- Sterowanie zaworami regulacyjnymi i przepustnicami
- Monitoring czujników temperatury
- Generowanie sygnałów alarmowych

#### Poziom wizualizacji (HMI/SCADA):
- Ekrany synoptyczne układu ogrzewania
- Trendy temperatury (czasu rzeczywistego i historyczne)
- Alarmy i zdarzenia
- Możliwość przełączania trybu pracy (AUTO/MANUAL)
- Ustawianie parametrów regulacji (Tz, Ts, Kp, Ti, Td)

### 9.2 Sygnały wejściowe (do PLC):
- Temperatury na wylocie z nagrzewnic N1-N8
- Temperatura w szybie na poziomie -30m
- Temperatura zewnętrzna
- Parametry wody grzewczej (temperatura, przepływ)
- Pozycje zaworów regulacyjnych
- Pozycje przepustnic
- Prędkości obrotowe wentylatorów W1, W2
- Stany gotowości urządzeń

### 9.3 Sygnały wyjściowe (z PLC):
- Sterowanie zaworami regulacyjnymi (8 nagrzewnic)
- Sterowanie przepustnicami
- Sterowanie prędkością obrotową wentylatorów W1, W2 (25-50 Hz)
- Sygnały załączania/wyłączania nagrzewnic
- Sygnały alarmowe

### 9.4 Funkcje systemu:

#### Regulacja automatyczna:
- UAR temperatury powietrza z nagrzewnic (8 pętli PID)
- UAR temperatury w szybie (2 pętle PID dla wentylatorów)
- Automatyczne załączanie/wyłączanie nagrzewnic wg Tabel 1 i 2
- Cykliczna rotacja nagrzewnic
- Cykliczna zmiana układów pracy ciągów

#### Sterowanie ręczne:
- Zdalne sterowanie zaworami regulacyjnymi
- Zdalne sterowanie przepustnicami
- Zdalne ustawianie prędkości wentylatorów
- Ręczne załączanie/wyłączanie nagrzewnic

#### Zabezpieczenia:
- Ochrona przed zamrożeniem nagrzewnic
- Monitorowanie parametrów wody grzewczej
- Sygnalizacja stanów awaryjnych
- Procedura skwitowania alarmów
- Automatyczne przełączenie AUTO→MANUAL w przypadku zakłóceń

#### Monitoring i diagnostyka:
- Archiwizacja danych procesowych
- Trendy temperatur
- Raporty pracy nagrzewnic (czasy pracy, liczba załączeń)
- Dziennik zdarzeń i alarmów
- Statystyki eksploatacyjne

---

## 10. Parametry Techniczne - Podsumowanie

| Parameter | Wartość | Uwagi |
|-----------|---------|-------|
| Liczba nagrzewnic | 8 (N1-N8) | Po 4 na ciąg |
| Liczba wentylatorów | 2 (W1, W2) | Sterowanie częstotliwościowe |
| Temperatura zadana Tz | 50°C | Powietrze na wylocie z nagrzewnicy |
| Temperatura zadana Ts | 2°C | Temperatura w szybie na -30m |
| Zakres częstotliwości wentylatorów | 25-50 Hz | NWmin - NWmax |
| Zakres otwarcia zaworu | 20-100% | Pzmin - Pzmax |
| Liczba poziomów wyrzutni | 2 | +4,30m i +7,90m |
| Sterowanie | PLC | Z regulatorami PID |


## Pytania wyjasniające

[Szczegółowe pytania wyjaśniające dotyczące wymagań systemu](Pytania_wyjasnien_wymagan.md)

Wybrane pytania potrzebne do zaimplementowania algorytmu i symulacji:

### 1 Układ nagrzewnic
- **Pytanie**: Czy nagrzewnice N1-N8 są podłączone równolegle do głównego kanału powietrza czy szeregowo (powietrze przechodzi przez kolejne nagrzewnice)?
- **Odpowiedz**: Szeregowo, po 4 w kazdym ciagu

### 2 Przypisanie wentylatorów
- **Pytanie**: Które nagrzewnice są obsługiwane przez wentylator W1, a które przez W2?
  - Czy W1 obsługuje N1-N4, a W2 obsługuje N5-N8?
  - Czy oba wentylatory wspólnie obsługują wszystkie nagrzewnice?
- **Odpowiedz**: W1 obsługuje N1-N4, a W2 obsługuje N5-N8 

### 3 Lokalizacja czujników temperatury
- **Pytanie**: Gdzie dokładnie są zamontowane czujniki temperatury?
  - Temperatura zewnętrzna (t_zewn) - lokalizacja poboru powietrza?
  - Temperatura wylotowa - czy osobny czujnik dla każdej nagrzewnicy, czy wspólny na wylocie z grupy nagrzewnic?
  - Czy są czujniki temperatury na wlocie do każdej nagrzewnicy?
- **Znaczenie**: Wpływa na logikę sterowania i algorytmy regulacji.

### 4 Zawory regulacyjne wody
- **Pytanie**: Jaki typ zaworów jest zastosowany?
  - Czas przejazdu zaworu z pozycji 0% do 100% [s]?
  - Charakterystyka zaworu (liniowa, równoprocentowa)?
- **Znaczenie**: Dobór odpowiedniego algorytmu PID i nastaw regulatora.

### 5 Wyłączanie nagrzewnicy
- **Pytanie**: W dokumencie jest informacja "Ustaw zawór regulacyjny wody na poziomie 20%" przy wyłączaniu. Czy to oznacza:
  - Czy zawór ma być stopniowo zamykany z 100% do 20% przed wyłączeniem nagrzewnicy?
  - Jak długo zawór ma pozostać na 20% przed pełnym zamknięciem?

### 6 Indywidualna czy wspólna regulacja
- **Pytanie**: Czy każda nagrzewnica ma osobny regulator PID z własnymi nastawami, czy wszystkie aktywne nagrzewnice są sterowane jednym regulatorem?
- **Znaczenie**: Liczba wymaganych bloków PID w programie sterującym.

### 7 Mechanizm histerezy
- **Pytanie**: Jak działa histereza w tabeli stanów?
  - Przykład S4: "Temp. włączenia: -8°C, Temp. wyłączenia: -6°C, Histereza: 2°C"
  - Czy to oznacza, że przy spadku z -7°C do -8,1°C włączamy N4, a wyłączamy dopiero przy wzroście do -5,9°C?
  - Czy histereza działa tylko przy wyłączaniu, czy również przy włączaniu?
- **Znaczenie**: Uniknięcie częstego przełączania (chattering) nagrzewnic.

### 8 Zakres wizualizacji
- **Pytanie**: Jakie są wymagania dla systemu SCADA?
  - Czy SCADA ma być na PC (Windows, Linux) czy panelu HMI?
  - Czy wymagany jest zdalny dostęp (VPN, web-interface)?
- **Znaczenie**: Dobór platformy SCADA i architektury oprogramowania.

### 9 Funkcjonalność
- **Pytanie**: Jakie funkcje ma posiadać SCADA?
  - Prezentacja synoptyczna (podobna do dostarczonego diagramu)?
  - Trendy historyczne (czas archiwizacji)?
  - Możliwość zmiany nastaw (zadana temperatura, nastawy PID)?
  - Ręczne sterowanie elementami (bypass automatyki)?
  - Raporty i logi zdarzeń?
- **Znaczenie**: Zakres projektu wizualizacji.

### 10 Komunikacja
- **Pytanie**: Jaki protokół komunikacyjny między PLC a SCADA?
  - Modbus TCP/RTU?
  - OPC UA?
  - Proprietary (np. S7, EtherNet/IP)?
- **Znaczenie**: Wazne dla przygotowania algorypmu pod wpiecie w rzeczywisty system