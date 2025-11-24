# System Sterowania Nagrzewnicami BOGDANKA Szyb 2

**Dokument główny - przegląd systemu**

_Plik ten jest częścią dokumentacji systemu sterowania nagrzewnicami BOGDANKA Szyb 2._

[← Powrót do dokumentacji głównej](../start.md)

---

## Wprowadzenie

System automatycznej regulacji (SAR) temperatury szybu BOGDANKA Szyb 2 zapewnia:
- **Ochronę przed przemarzaniem** - utrzymanie temperatury w szybie na poziomie **2°C** (na głębokości -30m)
- **Automatyczną adaptację** do warunków atmosferycznych (temperatura zewnętrzna od +3°C do -21°C)
- **Równomierne zużycie urządzeń** - algorytmy rotacji nagrzewnic i ciągów wentylacyjnych
- **Optymalizację energetyczną** - tylko tyle mocy grzewczej ile potrzeba (9 scenariuszy pracy)

**Dokumentacja wejściowa:** [Projekt instalacji (PDF)](./dokumentacja-wejsciowa/Projekt%20instalacji%20ogrzewania%20szybu.pdf) | [Projekt instalacji (MD)](./dokumentacja-wejsciowa/Projekt%20instalacji%20ogrzewania%20szybu.md)


## 1. Komponenty Systemu

**Układ fizyczny:**
- **8 nagrzewnic** (N1-N8) - 2 ciągi po 4 nagrzewnice
- **2 wentylatory** (W1, W2) - sterowanie częstotliwościowe 25-50 Hz
- **2 poziomy wyrzutni** - -4,30m i -7,90m
- **Zawory regulacyjne** - 8 zaworów wody grzewczej (20-100%)
- **Przepustnice** - sterowanie przepływem powietrza i konfiguracją ciągów


## 2. Architektura Sterowania (SAR)

System ma **dwuwarstwową architekturę** składającą się z dwóch podsystemów:

![Architektura SAR](./schematy/architektura_SAR_system.svg)

*Rys. Dwuwarstwowa architektura systemu SAR pokazująca relacje między podsystemami PARTS i PARTPG oraz algorytmami WS, RC i RN.*

### 2.1 PARTPG - Podsystem Regulacji Temperatury Powietrza Grzewczego

**Cel:** Stabilizacja temperatury powietrza grzewczego na poziomie **Tz = 50°C** (na wylocie z nagrzewnic)

| Warstwa | Funkcja | Realizacja |
|---------|---------|------------|
| **Regulacja** | Utrzymanie 50°C na wylocie | 8 × regulatorów PID (zawory wody grzewczej 20-100%) |
| **Zarządzanie** | Równomierne zużycie nagrzewnic | **Algorytm RN** - rotacja N1-N8 |

📖 **[Schematy UAR nagrzewnic](../02-projekt-instalacji/projekt-instalacji.md#2-schematy-regulacji-uar)** | **[Algorytm RN](../03-algorytmy/algorytmy.md#algorytm-rn-cykliczna-rotacja-nagrzewnic-w-obrębie-ciągu)**

### 2.2 PARTS - Podsystem Regulacji Temperatury Szybu

**Cel:** Utrzymanie temperatury w szybie na poziomie **Ts = 2°C** (na głębokości -30m)

| Warstwa | Funkcja | Realizacja |
|---------|---------|------------|
| **Regulacja** | Utrzymanie 2°C w szybie | 2 × regulatory PID (prędkość wentylatorów W1, W2: 25-50 Hz) |
| **Zarządzanie** | Dobór scenariusza i równomierne zużycie ciągów | **Algorytm WS** - wybór S0-S8<br>**Algorytm RC** - rotacja C1↔C2 |

📖 **[Schematy UAR wentylatorów](../02-projekt-instalacji/projekt-instalacji.md#2-schematy-regulacji-uar)** | **[Algorytmy WS i RC](../03-algorytmy/algorytmy.md)**

### 2.3 Hierarchia Sterowania

```
Algorytm WS → określa ILE nagrzewnic (S0-S8) na podstawie T_zewn
     ↓
Algorytm RC → określa KTÓRY CIĄG (C1 lub C2) w S1-S4
     ↓
Algorytm RN → określa KTÓRE nagrzewnice (N1-N8)
     ↓
Regulatory PID → utrzymują temperatury (50°C, 2°C)
```

**Przykład dla S3 (3 nagrzewnice, T_zewn = -6°C):**
- WS: potrzebne 3 nagrzewnice
- RC: układ Podstawowy → ciąg C1
- RN: wybiera N1, N2, N3 (lub inne, zależnie od historii pracy)
- PID: reguluje zawory i wentylator W1

---

## 3. Układy Pracy

System może pracować w dwóch układach:

| Układ | Ciągi aktywne | Wentylatory | Nawiew | Zastosowanie |
|-------|---------------|-------------|--------|--------------|
| **Podstawowy** | C1, C2 (niezależne) | W1, W2 | -4,30m, -7,90m | S5-S8 (t < -11°C)<br>ORAZ S1-S4 podczas rotacji RC |
| **Ograniczony** | C2 przez spinę | W2 (PID) | -4,30m | S1-S4 (t > -11°C) podczas rotacji RC |

**Kluczowe różnice:**
- **Podstawowy:** Oba ciągi pracują niezależnie, spinka **ZAMKNIĘTA**
- **Ograniczony:** Tylko C2 pracuje, C1 wyłączony, spinka **OTWARTA**, nawiew przez spinę do -4,30m

📖 **[Szczegółowe opisy układów i schematy](../02-projekt-instalacji/projekt-instalacji.md#3-układy-pracy)**

---

## 4. Scenariusze Pracy (S0-S8)

System automatycznie przełącza się między 9 scenariuszami w zależności od temperatury zewnętrznej:

| ID | Zakres Temp. | Ilość Nagrzewnic | Ciąg 1 (W1) | Ciąg 2 (W2) | Nawiew | Temp. Wył. | Hist. |
|----|-------------|------------------|-------------|-------------|--------|-----------|-------|
| S0 | t ≥ 3°C | 0 | OFF | OFF | - | - | - |
| S1 | -1<t≤2 | 1 | PID | OFF | -4,30m | t≥3 | 1°C |
| S2 | -4<t≤-1 | 2 | PID | OFF | -4,30m | t≥0 | 1°C |
| S3 | -8<t≤-4 | 3 | PID | OFF | -4,30m | t≥-3 | 1°C |
| S4 | -11<t≤-8 | 4 | PID lub MAX | OFF | -4,30m | t≥-6 | 2°C |
| S5 | -15<t≤-11 | 5 | MAX | PID | -4,30m -7,90m | t≥-10 | 1°C |
| S6 | -18<t≤-15 | 6 | MAX | PID | -4,30m -7,90m | t≥-13 | 2°C |
| S7 | -21<t≤-18 | 7 | MAX | PID | -4,30m -7,90m | t≥-15 | 3°C |
| S8 | t≤-21 | 8 | MAX | PID | -4,30m -7,90m | t≥-20 | 1°C |

**Legenda:**
- **PID** = sterowanie regulatorem PID (25-50 Hz, zmienna prędkość)
- **MAX** = stała maksymalna prędkość (50 Hz)
- **OFF** = wentylator wyłączony

**Uwagi:**
- **S0:** System wyłączony, oszczędzanie energii
- **S1-S4:** Układ **Podstawowy** LUB **Ograniczony** (zależy od algorytmu RC)
  - Konkretne nagrzewnice wybiera algorytm RN
  - Wentylator W1 lub W2 sterowany PID
  - Nawiew TYLKO na -4,30m
- **S5-S8:** Układ **Podstawowy** (zawsze)
  - W1 pracuje z MAX (50 Hz)
  - W2 sterowany PID
  - Nawiew na **OBA poziomy** (-4,30m i -7,90m)

📖 **[Szczegółowe opisy scenariuszy z diagramami](../02-projekt-instalacji/projekt-instalacji.md#5-scenariusze-pracy-systemu)** | **[Algorytm WS](../03-algorytmy/algorytmy.md#algorytm-ws-automatyczny-wybór-scenariusza-pracy)**

---

## 5. Algorytmy Sterowania

System wykorzystuje trzy współpracujące algorytmy:

### 5.1 Algorytm WS - Automatyczny Wybór Scenariusza

**Cel:** Dobór scenariusza (S0-S8) w zależności od T_zewn

**Funkcje:**
- Ciągły monitoring temperatury zewnętrznej (co 10s)
- Automatyczny wybór ilości nagrzewnic
- Histereza przy wyłączaniu (zapobiega oscylacjom)
- Bezpieczne sekwencje przejść między scenariuszami

📖 **[Szczegóły algorytmu WS](../03-algorytmy/algorytmy.md#algorytm-ws-automatyczny-wybór-scenariusza-pracy)**

### 5.2 Algorytm RC - Rotacja Układów Pracy Ciągów

**Cel:** Wyrównanie eksploatacji ciągów C1 i C2 (wentylatorów W1 i W2)

**Funkcje:**
- Cykliczna zmiana: Podstawowy ↔ Ograniczony
- Dotyczy tylko S1-S4 (temperatura -11°C < t ≤ 2°C)
- Okres rotacji: dni/tygodnie (definiowany przez technologa)

📖 **[Szczegóły algorytmu RC](../03-algorytmy/algorytmy.md#algorytm-rc-cykliczna-rotacja-układów-pracy-ciągów)**

### 5.3 Algorytm RN - Rotacja Nagrzewnic w Ciągu

**Cel:** Wyrównanie eksploatacji nagrzewnic N1-N8

**Funkcje:**
- Cykliczna wymiana: najdłużej pracująca → najdłużej w postoju
- Działa w obrębie jednego ciągu (C1 lub C2)
- Okres rotacji: godziny/dni/tygodnie (definiowany przez technologa)

📖 **[Szczegóły algorytmu RN](../03-algorytmy/algorytmy.md#algorytm-rn-cykliczna-rotacja-nagrzewnic-w-obrębie-ciągu)**

### 5.4 Implementacja Algorytmów - Zasady

**⚠️ KLUCZOWA ZASADA IMPLEMENTACJI:**

Wszystkie algorytmy (WS, RC, RN) muszą być zaimplementowane **DOKŁADNIE** według pseudokodu zawartego w [algorytmy.md](../03-algorytmy/algorytmy.md).

**Pseudokod = Źródło Prawdy (Single Source of Truth)**

- ✅ Implementacja w PLC/symulacji musi **1:1** odzwierciedlać pseudokod
- ✅ Każda linia pseudokodu ma swoją implementację w kodzie
- ✅ Testy jednostkowe weryfikują zgodność z pseudokodem
- ❌ **NIE wolno** wprowadzać zmian w implementacji bez aktualizacji pseudokodu

**Proces wykrywania problemów:**

1. **Podczas testów jednostkowych** - jeśli test wykryje problem:
   - Analiza: czy błąd jest w implementacji czy w logice pseudokodu?
   - Jeśli w pseudokodzie → aktualizacja [algorytmy.md](../03-algorytmy/algorytmy.md)
   - Jeśli w implementacji → poprawka kodu do zgodności z pseudokodem

2. **Podczas symulacji** - jeśli symulacja wykryje problem:
   - Analiza wyników w Splunk Observability
   - Identyfikacja błędnej logiki w pseudokodzie
   - Aktualizacja [algorytmy.md](../03-algorytmy/algorytmy.md) + re-implementacja

**Uzasadnienie:**

- Dokumentacja (pseudokod) jest **specyfikacją** - musi być zawsze aktualna
- Implementacja jest **realizacją** specyfikacji
- Synchronizacja: kod ↔ dokumentacja zapewnia spójność projektu
- Łatwiejsza weryfikacja i audyt systemu

**Narzędzia weryfikacji:**

- Testy jednostkowe algorytmów (simulation))
- Symulacja 30-dniowa z metrykami Splunk

---

## 6. Parametry Systemowe

**Temperatury docelowe:**
- **Tz = 50°C** - temperatura na wylocie z nagrzewnicy
- **Ts = 2°C** - temperatura w szybie (poziom -30m)

**Zawory regulacyjne:**
- Zakres: 20-100%
- Min. 20% = ochrona antyzamrożeniowa

**Wentylatory:**
- Zakres częstotliwości: 25-50 Hz
- Sterowanie: PLC z regulatorami PID

**Tryby pracy:**
- **AUTO** - regulacja PID
- **MANUAL** - sterowanie ręczne

**Uwaga:** Parametry PID (Kp, Ti, Td) i okresy rotacji (RC, RN) będą dobrane doświadczalnie podczas rozruchu na obiekcie.

---

## 7. System SCADA/HMI

System sterowania realizowany na sterowniku PLC z interfejsem operatorskim SCADA/HMI.

**Funkcje podstawowe:**
- Monitoring temperatury szybu, nagrzewnic i zewnętrznej
- Wizualizacja aktualnego scenariusza i układu pracy
- System alarmów (krytyczne, ostrzegawcze, informacyjne)
- Trendy historyczne (24h, 7 dni, 30 dni)
- Przełączanie AUTO/MANUAL
- Nastawy PID i parametrów rotacji

**Poziomy dostępu:**
- **Operator:** monitoring, kwitowanie alarmów
- **Inżynier:** zmiana trybu, ręczne sterowanie
- **Administrator:** zmiana nastaw PID, konfiguracja

📖 **[Szczegóły SCADA/HMI](../04-scada-hmi/scada-hmi.md)**

---

## Powiązane Dokumenty

- **[Projekt instalacji](../02-projekt-instalacji/projekt-instalacji.md)** - schematy instalacji, UAR, scenariusze z diagramami
- **[Algorytmy WS, RC, RN](../03-algorytmy/algorytmy.md)** - szczegółowe pseudokody, flowcharty, przykłady
- **[System SCADA/HMI](../04-scada-hmi/scada-hmi.md)** - interfejs operatorski, wizualizacja, alarmy, trendy
- **[Dokumentacja wejściowa](./dokumentacja-wejsciowa/Projekt%20instalacji%20ogrzewania%20szybu.md)** - pliki otrzymane od zleceniodawcy

---

**Ostatnia aktualizacja:** 24 Listopad 2025  
**Wersja dokumentu:** 1.0
