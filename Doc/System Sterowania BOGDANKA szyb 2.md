# System Sterowania Nagrzewnicami BOGDANKA Szyb 2

## 1. Tabela Stanów

| ID | Zakres Temperatury Zewnętrznej | Nagrzewnice Aktywne | Wentylatory Aktywne | Temp. Docelowa | Temp. Wyłączenia Dodatkowej Nagrzewnicy | Histereza |
|----|-------------------------------|---------------------|---------------------|----------------|----------------------------------------|-----------|
| R1 | t ≥ 3°C |  |  | 50°C |  |  |
| R2 | -1°C < t ≤ 2°C | N1 | W1 | 50°C | t ≥ 3°C | 1°C |
| R3 | -4°C < t ≤ -1°C | N1, N2 | W1 | 50°C | t ≥ 0°C | 1°C |
| R4 | -8°C < t ≤ -4°C | N1, N2, N3 | W1 | 50°C | t ≥ -3°C | 1°C |
| R5 | -11°C < t ≤ -8°C | N1, N2, N3, N4 | W1 | 50°C | t ≥ -6°C | 2°C |
| R6 | -15°C < t ≤ -11°C | N1, N2, N3, N4, N5 | W1, W2 | 50°C | t ≥ -10°C | 1°C |
| R7 | -18°C < t ≤ -15°C | N1, N2, N3, N4, N5, N6, | W1, W2 | 50°C | t ≥ -13°C | 2°C |
| R8 | -21°C < t ≤ -18°C | N1, N2, N3, N4, N5, N6, N7 | W1, W2 | 50°C | t ≥ -15°C | 3°C |
| R9 | t ≤ -21°C | N1, N2, N3, N4, N5, N6, N7, N8 | W1, W2 | 50°C | t ≥ -20°C | 1°C |

## 2. Tabela Decyzyjna

| Warunek / Akcja | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 |
|----------------|----|----|----|----|----|----|----|----|----|
| **WARUNKI WEJŚCIOWE** |
| t > 3°C | TAK | NIE | NIE | NIE | NIE | NIE | NIE | NIE | NIE |
| -1°C < t ≤ 2°C | NIE | TAK | NIE | NIE | NIE | NIE | NIE | NIE |NIE |
| -4°C < t ≤ -1°C | NIE | NIE | TAK | NIE | NIE | NIE | NIE | NIE |NIE |
| -8°C < t ≤ -4°C | NIE | NIE | NIE | TAK | NIE | NIE | NIE | NIE |NIE |
| -11°C < t ≤ -8°C | NIE | NIE | NIE | NIE | TAK | NIE | NIE | NIE |NIE |
| -15°C < t ≤ -11°C | NIE | NIE | NIE | NIE | NIE | TAK | NIE | NIE |NIE |
| -18°C < t ≤ -15°C | NIE | NIE | NIE | NIE | NIE | NIE | TAK | NIE |NIE |
| -21°C < t ≤ -18°C | NIE | NIE | NIE | NIE | NIE | NIE | NIE | TAK |NIE |
| t ≤ -21°C | NIE | NIE | NIE | NIE | NIE | NIE | NIE | NIE | TAK |
| **AKCJE - NAGRZEWNICE** |
| Włącz N1 | NIE | TAK | TAK | TAK | TAK | TAK | TAK | TAK | TAK |
| Włącz N2 | NIE | TAK | TAK | TAK | TAK | TAK | TAK | TAK | TAK |
| Włącz N3 | NIE | NIE | TAK | TAK | TAK | TAK | TAK | TAK | TAK |
| Włącz N4 | NIE | NIE | NIE | TAK | TAK | TAK | TAK | TAK | TAK |
| Włącz N5 | NIE | NIE | NIE | NIE | TAK | TAK | TAK | TAK | TAK |
| Włącz N6 | NIE | NIE | NIE | NIE | NIE | TAK | TAK | TAK | TAK |
| Włącz N7 | NIE | NIE | NIE | NIE | NIE | NIE | TAK | TAK | TAK |
| Włącz N8 | NIE | NIE | NIE | NIE | NIE | NIE | NIE | NIE | TAK |
| **AKCJE - WENTYLATORY** |
| Włącz W1 | TAK | TAK | TAK | TAK | TAK | TAK | TAK | TAK | TAK |
| Włącz W2 | NIE | NIE | NIE | NIE | TAK | TAK | TAK | TAK | TAK |
| **AKCJE - PRZEPUSTNICE** |
| Otworz przepustnice wylot i wlot N1 | NIE | TAK | TAK | TAK | TAK | TAK | TAK | TAK | TAK |
| Otworz przepustnice wylot i wlot N2 | NIE | TAK | TAK | TAK | TAK | TAK | TAK | TAK | TAK |
| Otworz przepustnice wylot i wlot N3 | NIE | NIE | TAK | TAK | TAK | TAK | TAK | TAK | TAK |
| Otworz przepustnice wylot i wlot N4 | NIE | NIE | NIE | TAK | TAK | TAK | TAK | TAK | TAK |
| Otworz przepustnice wylot i wlot N5 | NIE | NIE | NIE | NIE | TAK | TAK | TAK | TAK | TAK |
| Otworz przepustnice wylot i wlot N6 | NIE | NIE | NIE | NIE | NIE | TAK | TAK | TAK | TAK |
| Otworz przepustnice wylot i wlot N7 | NIE | NIE | NIE | NIE | NIE | NIE | TAK | TAK | TAK |
| Otworz przepustnice wylot i wlot N8 | NIE | NIE | NIE | NIE | NIE | NIE | NIE | NIE | TAK |
| **PARAMETRY REGULACJI** |
| Temperatura docelowa (°C) | 50 | 50 | 50 | 50 | 50 | 50 | 50 | 50 | 50 |
| Temp. włączenia dodatkowej nagrzewnicy (°C) | 2 | -1 | -4 | -8 | -11 | -15 | -18 | -21 |
| Zawór regulacyjny przy włączeniu (%) | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| Temp. wyłączenia dodatkowej nagrzewnicy (°C) | 3 | 0 | -3 | -6 | -10 | -13 | -15 | -20 |
| Zawór regulacyjny przy wyłączeniu (%) | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |

## 3. Sekwencja Operacji

### 3.1 Włączanie Nagrzewnicy
1. Otwórz przepustnicę na wlocie (100%)
2. Otwórz przepustnicę na wylocie (100%)
3. Włącz wentylator(y)
4. Otwórz zawór regulacyjny wody (regulacja PID dla utrzymania 50°C)

### 3.2 Wyłączanie Nagrzewnicy
1. Ustaw zawór regulacyjny wody na poziomie 20%
2. Monitoruj temperaturę na włocie i wylocie
3. Zamknij przepustnicę na włocie (0%)
4. Zamknij przepustnicę na wylocie (0%)
5. Wyłącz nagrzewnicę
6. Pozostaw wentylator włączony jeśli potrzebny dla innych nagrzewnic lub wyłacz (wg. tabeli decyzyjnej)


## 4. Parametry Systemowe

| Parameter | Wartość | Jednostka | Opis |
|-----------|---------|-----------|------|
| Temperatura docelowa | 50 | °C | Temperatura wyjściowa z nagrzewnicy |
| Pozycja zaworu przy stop | 20 | % | Otwarcie zaworu przed kolejnym startem |
| Czas stabilizacji | 5 | s | Czas na stabilizację przed odczytem |
| Okres próbkowania | 1 | s | Częstotliwość odczytu temperatury |
| Max pozycja zaworu | 100 | % | Maksymalne otwarcie zaworu |
| Min pozycja zaworu | 0 | % | Minimalne otwarcie zaworu |
| PID - Kp | 2.0 | - | Człon proporcjonalny |
| PID - Ki | 1 | - | Człon całkujący |
| PID - Kd | 0.1 | - | Człon różniczkujący |

## 5. Obsługa Awarii

| Warunek Awarii | Akcja |
|----------------|-------|
| Brak odczytu temperatury zewnętrznej | Zachowaj ostatni stan, alarm |
| Brak odczytu temperatury wylotowej | Ustaw zawór na 30%, alarm |
| Temperatura wylotowa > 60°C | Zamknij zawór do 20%, alarm |
| Temperatura wylotowa < 30°C przy pracy | Zwiększ otwarcie zaworu, sprawdź zasilanie |
| Wentylator nie pracuje | Wyłącz odpowiednie nagrzewnice, alarm |
| Przepustnica nie reaguje | Alarm, kontynuuj pracę |


