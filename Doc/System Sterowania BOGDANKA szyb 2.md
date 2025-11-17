# System Sterowania Nagrzewnicami BOGDANKA Szyb 2

## 1. Diagram
![Algorytm sterowania - BOGDANKA - Szyb 2](Algortym%20sterowania%20-%20BOGDANKA%20-%20Szyb%202%20v2.jpg)


## 2. Stany nagrzewnicy

```
- STARTING (uruchamianie - otwieranie przepustnic i zaworu do 100%)
- ON 🟢 (praca - regulacja zaworu wody)
- STOPPING (zatrzymywanie - zamykanie zaworu do 20%)
- OFF 🔴 (wyłączona - zamykanie przepustnic)
```

## 2. Tabela Stanów

| ID | Zakres Temperatury Zewnętrznej | Nagrzewnice Aktywne | Wentylatory Aktywne | Temp. Docelowa | Temp. Wyłączenia Dodatkowej Nagrzewnicy | Histereza |
|----|-------------------------------|---------------------|---------------------|----------------|----------------------------------------|-----------|
| S1 | t ≥ 3°C |  |  |  |  |  |
| S2 | -1°C < t ≤ 2°C | N1 | W1 | 50°C | t ≥ 3°C | 1°C |
| S3 | -4°C < t ≤ -1°C | N1, N2 | W1 | 50°C | t ≥ 0°C | 1°C |
| S4 | -8°C < t ≤ -4°C | N1, N2, N3 | W1 | 50°C | t ≥ -3°C | 1°C |
| S5 | -11°C < t ≤ -8°C | N1, N2, N3, N4 | W1 | 50°C | t ≥ -6°C | 2°C |
| S6 | -15°C < t ≤ -11°C | N1, N2, N3, N4, N5 | W1, W2 | 50°C | t ≥ -10°C | 1°C |
| S7 | -18°C < t ≤ -15°C | N1, N2, N3, N4, N5, N6, | W1, W2 | 50°C | t ≥ -13°C | 2°C |
| S8 | -21°C < t ≤ -18°C | N1, N2, N3, N4, N5, N6, N7 | W1, W2 | 50°C | t ≥ -15°C | 3°C |
| S9 | t ≤ -21°C | N1, N2, N3, N4, N5, N6, N7, N8 | W1, W2 | 50°C | t ≥ -20°C | 1°C |

## 3. Tabela Decyzyjna

| Sterowany element | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 |
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
| W2 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| **PRZEPUSTNICE** |
| N1 przepustnice wylot i wlot | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| N2 przepustnice wylot i wlot | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| N3 przepustnice wylot i wlot | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| N4 przepustnice wylot i wlot | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| N5 przepustnice wylot i wlot | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | 🟢 |
| N6 przepustnice wylot i wlot | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 |
| N7 przepustnice wylot i wlot | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 |
| N8 przepustnice wylot i wlot | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | 🟢 |
| **PARAMETRY REGULACJI** |
| Temperatura docelowa (°C) | | 50 | 50 | 50 | 50 | 50 | 50 | 50 | 50 |
| Temp. włączenia dodatkowej nagrzewnicy (°C) | | 2 | -1 | -4 | -8 | -11 | -15 | -18 | -21 |
| Zawór regulacyjny przy włączeniu (%) | | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| Temp. wyłączenia dodatkowej nagrzewnicy (°C) | | 3 | 0 | -3 | -6 | -10 | -13 | -15 | -20 |
| Zawór regulacyjny przy wyłączeniu (%) | | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |

## 4. Sekwencja Operacji

### 4.1 Włączanie Nagrzewnicy
1. Otwórz przepustnicę na wlocie (100%)
2. Otwórz przepustnicę na wylocie (100%)
3. Włącz wentylator(y)
4. Otwórz zawór regulacyjny wody (regulacja PID dla utrzymania 50°C)

### 4.2 Wyłączanie Nagrzewnicy
1. Ustaw zawór regulacyjny wody na poziomie 20%
2. Monitoruj temperaturę na wlocie i wylocie
3. Zamknij przepustnicę na wlocie (0%)
4. Zamknij przepustnicę na wylocie (0%)
5. Wyłącz nagrzewnicę
6. Pozostaw wentylator włączony jeśli potrzebny dla innych nagrzewnic lub wyłacz (wg. tabeli decyzyjnej)


## 5. Parametry Systemowe

| Parameter | Wartość | Jednostka | Opis |
|-----------|---------|-----------|------|
| Temperatura docelowa | 50 | °C | Temperatura wyjściowa z nagrzewnicy |
| Pozycja zaworu przy stop | 20 | % | Otwarcie zaworu przed kolejnym startem |
| Czas stabilizacji | 5 | s | Czas na stabilizację przed odczytem |
| Okres próbkowania | 1 | s | Częstotliwość odczytu temperatury |
| Max pozycja zaworu | 100 | % | Maksymalne otwarcie zaworu |
| Min pozycja zaworu | 0 | % | Minimalne otwarcie zaworu |
| PID - Kp | 2.0 | - | Człon proporcjonalny (zawor wody) |
| PID - Ki | 1 | - | Człon całkujący (zawor wody) |
| PID - Kd | 0.1 | - | Człon różniczkujący (zawor wody) |

## 6. Obsługa Awarii

| Warunek Awarii | Akcja |
|----------------|-------|
| Brak odczytu temperatury zewnętrznej | Zachowaj ostatni stan, alarm |
| Brak odczytu temperatury wylotowej | Ustaw zawór na 50%, alarm |
| Temperatura wylotowa > 60°C | Zamknij zawór do 20%, alarm |
| Temperatura wylotowa < 40°C przy pracy | Zwiększ otwarcie zaworu do 100%, alarm  |
| Wentylator nie pracuje | Wyłącz odpowiednie nagrzewnice, alarm |
| Przepustnica nie reaguje | Kontynuuj pracę, alarm |

