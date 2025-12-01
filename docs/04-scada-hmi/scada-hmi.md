# System SCADA/HMI - BOGDANKA Szyb 2

**Interfejs operatorski, wizualizacja i wymagania techniczne platformy SCADA**

_Plik ten jest częścią dokumentacji systemu sterowania nagrzewnicami BOGDANKA Szyb 2._

[← Powrót do dokumentacji głównej](../start.md)

---

## 1. Wymagania Podstawowe

System sterowania realizowany na sterowniku PLC z regulatorami PID.

**Poziom sterowania (PLC):**
- Realizacja algorytmów regulacji PARTPG i PARTS
- Bloki funkcyjne regulatorów PID dla:
  - UAR temperatury powietrza z nagrzewnic (8 pętli PID)
  - UAR temperatury w szybie (2 pętle PID dla wentylatorów W1 i W2)
- Sterowanie zaworami regulacyjnymi i przepustnicami
- Monitoring czujników temperatury
- Generowanie sygnałów alarmowych

**Funkcje automatyczne:**
- Automatyczne załączanie/wyłączanie nagrzewnic według scenariuszy S0-S8
- Cykliczna rotacja nagrzewnic w jednym ciągu wentylacyjnym (Algorytm RN)
- Cykliczna zmiana układów pracy ciągów grzewczych (Algorytm RC)

**Parametry do ustawienia przez technologa:**
- Wartości zadane: Tz (50°C), Ts (2°C)
- Nastawy regulatorów PID: Kp, Ti, Td (dobierane doświadczalnie podczas rozruchu)
- Okres rotacji nagrzewnic
- Okres zmiany układów pracy ciągów

---

## 2. Panel Główny - Elementy Wizualizacji

### Kolory i Konwencje Wizualne:

**Stan Elementów:**
- 🟢 **Zielony** - Element aktywny, pracujący
- ⚪ **Szary** - Element nieaktywny, wyłączony
- 🔴 **Czerwony** - Awaria, alarm
- 🟡 **Żółty** - Ostrzeżenie, tryb przejściowy

**Przepływy:**
- **Linie ciągłe** (grube) - Aktywny przepływ
- **Linie przerywane** (cienkie) - Brak przepływu lub przepływ minimalny
- 🔴 **Czerwony** - Woda grzewcza (zasilanie, gorąca)
- 🔵 **Niebieski** - Woda powrotna (chłodniejsza)
- 🟢 **Ciemnozielony** - Sygnały sterujące/pomiarowe PID
- ⚪ **Szary** - Powietrze

**Zawory:**
- **Z** - Zamknięty
- **O** - Otwarty
- **%** - Pozycja w procentach (dla zaworów regulacyjnych)

## 3. Główne Wskaźniki na Panelu HMI

**Temperatury:**
- **T_zewn** - Temperatura zewnętrzna [°C]
- **Tz** - Temperatura zadana na wylocie z nagrzewnicy (50°C)
- **T_N1...T_N8** - Temperatury rzeczywiste na wylotach z nagrzewnic [°C]
- **Ts** - Temperatura zadana w szybie (2°C)
- **T_szyb** - Temperatura rzeczywista w szybie na poziomie -30m [°C]

**Parametry Wentylatorów:**
- **W1_f** - Częstotliwość wentylatora W1 [Hz] (25-50)
- **W2_f** - Częstotliwość wentylatora W2 [Hz] (25-50)
- **W1_I** - Prąd silnika W1 [A]
- **W2_I** - Prąd silnika W2 [A]

**Zawory Regulacyjne:**
- **Z_N1...Z_N8** - Pozycje zaworów regulacyjnych [%] (20-100)

**Statusy:**
- **Scenariusz** - Aktualny scenariusz pracy (S0-S8)
- **Układ Pracy** - Podstawowy / Ograniczony
- **Tryb** - AUTO / MANUAL
- **Alarmy** - Lista aktywnych alarmów

**Rotacje (Algorytmy RC i RN):**
- **Czas do rotacji układów (RC)** - Pozostały czas do zmiany układu [h]
- **Aktualny układ** - Podstawowy / Ograniczony
- **Czas pracy C1** - Łączny czas pracy ciągu 1 [h]
- **Czas pracy C2** - Łączny czas pracy ciągu 2 [h]
- **Stosunek C1/C2** - Proporcja eksploatacji (cel: ~1.0)
- **Czas do rotacji nagrzewnic (RN)** - Pozostały czas do wymiany nagrzewnicy [h]
- **Czasy pracy N1-N8** - Łączne czasy pracy poszczególnych nagrzewnic [h]
- **Liczba załączeń N1-N8** - Liczniki startów nagrzewnic

## 4. Tryby Pracy Systemu

**Tryb AUTO (Automatyczny):**
- System automatycznie wybiera scenariusz na podstawie T_zewn
- Regulatory PID aktywnie kontrolują:
  - Temperaturę powietrza (zawory N1-N8)
  - Temperaturę w szybie (wentylatory W1-W2)
- Automatyczne włączanie/wyłączanie nagrzewnic
- Automatyczna regulacja prędkości wentylatorów

**Tryb MANUAL (Ręczny):**
- Operator ma pełną kontrolę nad systemem
- Możliwość ręcznego ustawienia:
  - Pozycji zaworów (20-100%)
  - Częstotliwości wentylatorów (25-50 Hz)
  - Włączenia/wyłączenia poszczególnych nagrzewnic
- Zabezpieczenia nadal aktywne (min. 20% zaworu, limity temperatur)

## 5. System Alarmów

**Alarmy Krytyczne (Czerwone):**
- 🔴 **Brak odczytu T_zewn** - Utrzymanie ostatniego stanu
- 🔴 **Temperatura > 60°C** - Zamknięcie zaworu do 20%
- 🔴 **Wentylator nie pracuje** - Wyłączenie odpowiednich nagrzewnic
- 🔴 **Temp. wody < 5°C** - Ryzyko zamrożenia

**Alarmy Ostrzegawcze (Żółte):**
- 🟡 **Temperatura < 40°C** przy pracy - Zwiększenie otwarcia zaworu
- 🟡 **Przepustnica nie reaguje** - Kontynuacja pracy
- 🟡 **Zbyt długi czas nagrzewania** - Sprawdzenie parametrów PID

**Informacje (Niebieskie):**
- 🔵 **Zmiana scenariusza** - Automatyczne przełączenie
- 🔵 **Przełączenie AUTO/MANUAL** - Zmiana trybu przez operatora
- 🔵 **Zmiana parametrów PID** - Modyfikacja nastaw

## 6. Trendy Historyczne

Panel HMI umożliwia wyświetlanie trendów:
- Temperatura zewnętrzna (24h)
- Temperatura w szybie (24h)
- Temperatury na wylotach z nagrzewnic (8 krzywych)
- Pozycje zaworów regulacyjnych (8 krzywych)
- Częstotliwości wentylatorów (2 krzywe)
- Pobór mocy całkowity [kW]

## 7. Ekrany Dostępne w Systemie

1. **Ekran Główny** - Synoptyka z aktualnym scenariuszem i układem pracy
2. **Szczegóły Nagrzewnic** - Parametry N1-N8, czasy pracy, liczba załączeń
3. **Szczegóły Wentylatorów** - Parametry W1-W2, czasy pracy ciągów
4. **Trendy** - Wykresy historyczne
5. **Alarmy** - Historia i aktywne alarmy
6. **Nastawy** - Parametry PID, temperatury zadane, okresy rotacji
7. **Diagnostyka** - Stan urządzeń i statystyki
8. **Rotacja RC** - Historia zmian układów, stosunek eksploatacji C1/C2
9. **Rotacja RN** - Czasy pracy nagrzewnic, predykcja następnej rotacji

## 8. Monitoring i Statystyki (Matryca WS/RC/RN)

| Metryka | WS | RC | RN | Opis / Użycie |
|---------|:--:|:--:|:--:|---------------|
| Historia temperatury zewnętrznej | ✅ | – | – | Bufor 24 h, kroki wg `CYKL_MONITORINGU_TEMP` |
| Timeline scenariuszy S0‑S8 | ✅ | – | – | Kontekst wszystkich zdarzeń (zaznacza decyzje WS) |
| Liczba zmian + średni czas zmiany scenariusza | ✅ | – | – | KPI responsywności WS |
| Odroczenia zmian (stabilizacja / blokady) | ✅ | – | – | Diagnostyka współdziałania WS↔RC↔RN |
| Łączny czas w każdym scenariuszu | ✅ | – | – | Analiza energetyczna i raporty miesięczne |
| Awarie czujników temperatury | ✅ | – | – | Bezpieczeństwo pomiarowe / SLA czujników |
| Łączny czas pracy C1 / C2 | – | ✅ | – | Balans układów podstawowy/ograniczony |
| Liczba i średni czas rotacji układów | – | ✅ | – | Skuteczność RC, średni czas procedury |
| Nieudane/odrzucone rotacje układów | – | ✅ | – | Wskaźnik problemów wentylatorów / blokad |
| Stosunek eksploatacji C1/C2 | – | ✅ | – | Cel ≈1.0; alarm gdy >1.2 lub <0.8 |
| Czas pracy każdego N1‑N8 | – | – | ✅ | Podstawa równomiernej eksploatacji |
| Czas postoju każdego N1‑N8 | – | – | ✅ | Używane przez RN przy wyborze kandydatów |
| Liczba uruchomień nagrzewnic | – | – | ✅ | Statystyka serwisowa, B10d |
| Historia rotacji nagrzewnic + różnica max‑min | – | – | ✅ | KPI – różnica <10% po 30 dniach |
| Średnia temperatura wylotu nagrzewnic | – | – | ✅ | Ocena zdrowia wymienników |

**Widoki rekomendowane:**
- Wykres temperatury zewnętrznej z nałożoną timeline scenariuszy.
- Histogram czasu pracy C1 vs C2 oraz wskaźnik C1/C2.
- Słupki czasu pracy i postoju N1‑N8 + wykres różnicy max‑min.
- Lista zdarzeń (WS/RC/RN) z czasem i rezultatem (sukces/odroczenie/błąd).
- Dashboard KPI (liczba zmian scenariusza, rotacje RC/RN, alarmy krytyczne).

## 9. Parametry Nastaw PID

**UAR Temperatury Nagrzewnic (N1-N8):**
```
Kp = [do określenia podczas rozruchu]
Ti = [do określenia podczas rozruchu]
Td = [do określenia podczas rozruchu]
Tz = 50°C (stała)
CV_min = 20% (ochrona antyzamrożeniowa)
CV_max = 100%
```

**UAR Prędkości Wentylatorów (W1, W2):**
```
Kp = [do określenia podczas rozruchu]
Ti = [do określenia podczas rozruchu]
Td = [do określenia podczas rozruchu]
Ts = 2°C (stała)
f_min = 25 Hz (minimalna prędkość)
f_max = 50 Hz (maksymalna prędkość)
```

## 10. Wymagania Techniczne

**Platforma SCADA:** iFix, WinCC, Wonderware, Ignition lub podobna  
**Komunikacja PLC:** Modbus TCP/RTU, OPC UA lub protokół właścicielski  
**Czas odświeżania:** 1s dla parametrów procesowych  
**Archiwizacja:** min. 1 rok danych historycznych  
**Rozdzielczość:** min. 1920x1080 dla pełnej wizualizacji

**Poziomy dostępu:**
- **Operator:** monitoring, kwitowanie alarmów
- **Inżynier:** zmiana trybu AUTO/MANUAL, ręczne sterowanie
- **Administrator:** zmiana nastaw PID, konfiguracja systemu

**Bezpieczeństwo:**
- Logi wszystkich akcji operatora
- Codzienne kopie bezpieczeństwa bazy danych

---

## Powiązane Dokumenty

- [System Sterowania](../01-system/system.md) - kompletna architektura systemu SAR
- [Projekt Instalacji](../02-projekt-instalacji/projekt-instalacji.md) - schematy instalacji i scenariusze
- [Algorytmy WS, RC, RN](../03-algorytmy/algorytmy.md) - szczegółowe opisy logiki sterowania

---

**Ostatnia aktualizacja:** 1 Grudzień 2025  
**Wersja dokumentu:** 1.0

