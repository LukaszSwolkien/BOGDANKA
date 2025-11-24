# System Sterowania Nagrzewnicami BOGDANKA Szyb 2

Ostatnia aktualizacja: 24 Listopad 2025

## 📄 Dokumentacja Wejściowa

### Projekt instalacji ogrzewania szybu

Dokumenty otrzymane 19 listopad 2025:

- [Projekt instalacji ogrzewania szybu - skan PDF](./dokumentacja-wejsciowa/Projekt%20instalacji%20ogrzewania%20szybu.pdf)
- [Projekt instalacji ogrzewania szybu - dokumentacja](./dokumentacja-wejsciowa/Projekt%20instalacji%20ogrzewania%20szybu.md)

---

## 1. Architektura Systemu Automatycznej Regulacji (SAR)

System automatycznej regulacji (SAR) temperatury szybu składa się z dwóch podsystemów, z których każdy ma **dwuwarstwową architekturę**:
- **Warstwa regulacji** - podstawowa funkcja utrzymania temperatury (PID)
- **Warstwa zarządzania** - funkcja optymalizująca wykorzystanie urządzeń (algorytmy)

![Architektura SAR](./architektura_SAR_system.svg)

*Rys. Dwuwarstwowa architektura systemu SAR pokazująca relacje między podsystemami PARTS i PARTPG oraz algorytmami WS, RC i RN.*

### 1.1 PARTPG - Podsystem Automatycznej Regulacji Temperatur Powietrza Grzewczego

**Zadanie:** Stabilizacja temperatury powietrza grzewczego używanego przez PARTS.

#### Warstwa Regulacji (podstawowa funkcja systemu)

**Składa się z:**
- 8 układów automatycznej regulacji (UAR) temperatury powietrza - po jednym dla każdej nagrzewnicy
- Każdy UAR kontroluje temperaturę na wylocie z nagrzewnicy (Tz = 50°C)
- Realizuje załączanie/wyłączanie nagrzewnic do/z ruchu
- Zabezpiecza nagrzewnice przed przemarzaniem (min. 20% otwarcia zaworu)

**Struktura UAR nagrzewnicy:**
- Regulator PID kontroluje zawór regulacyjny wody grzewczej
- Zakres pracy zaworu: 20-100%
- Tryby pracy: AUTO (regulacja PID) i MANUAL (sterowanie ręczne)
- Bezuderzeniowe (bumpless) przejście między trybami

#### Warstwa Zarządzania (optymalizacja użycia urządzeń)

**Algorytm RN - Rotacja Nagrzewnic w Ciągu:**
- Cykliczna wymiana pracujących nagrzewnic na rezerwowe w obrębie ciągu
- Równomierne rozłożenie czasu pracy wszystkich 8 nagrzewnic (N1-N8)
- Maksymalizacja niezawodności przez równomierne zużycie
- Wybór nagrzewnic na podstawie historii pracy/postoju

📖 **[Szczegółowy opis → Algorytm RN](../02-algorytmy/algorytmy.md#algorytm-rn-cykliczna-rotacja-nagrzewnic-w-obrębie-ciągu)**

### 1.2 PARTS - Podsystem Automatycznej Regulacji Temperatury Szybu

**Zadanie:** Utrzymanie temperatury szybu na zadanym poziomie (Ts = 2°C na poziomie -30m).

#### Warstwa Regulacji (podstawowa funkcja systemu)

**Składa się z:**
- 2 układów automatycznej regulacji (UAR) prędkości wentylatorów W1 i W2
- Regulatory PID kontrolują częstotliwość pracy wentylatorów (25-50 Hz)

**Struktura UAR wentylatorów:**
- Regulator PID kontroluje przetwornicę częstotliwości (falownik)
- Zakres częstotliwości: NWmin = 25 Hz, NWmax = 50 Hz
- NWmax zależy od ilości nagrzewnic w gotowości operacyjnej (dla 4 nagrzewnic: 50 Hz)
- Tryby pracy: AUTO i MANUAL

#### Warstwa Zarządzania (optymalizacja użycia urządzeń)

**Algorytm WS - Automatyczny Wybór Scenariusza Pracy:**
- Automatyczny dobór ilości nagrzewnic (S0-S8) w zależności od temperatury zewnętrznej
- Optymalne wykorzystanie mocy grzewczej (tylko tyle nagrzewnic ile potrzeba)
- Automatyczna adaptacja do zmian warunków atmosferycznych
- Histereza temperaturowa zapobiegająca częstym przełączeniom

**Algorytm RC - Rotacja Układów Pracy Ciągów:**
- Cykliczna zmiana między układem Podstawowym (C1) a Ograniczonym (C2)
- Równomierne rozłożenie czasu pracy ciągów wentylacyjnych i wentylatorów (W1, W2)
- Dotyczy scenariuszy S1-S4 (temperatura -11°C < t ≤ 2°C)
- Maksymalizacja niezawodności przez równomierne zużycie

📖 **[Szczegółowy opis algorytmów](../02-algorytmy/algorytmy.md)** | [Algorytm WS](../02-algorytmy/algorytmy.md#algorytm-ws-automatyczny-wybór-scenariusza-pracy) | [Algorytm RC](../02-algorytmy/algorytmy.md#algorytm-rc-cykliczna-rotacja-układów-pracy-ciągów)

### 1.3 Zależności między Podsystemami

**Hierarchia działania:**
- PARTS wymaga stabilnych parametrów powietrza grzewczego od PARTPG
- Brak stabilnych parametrów → pogorszenie jakości regulacji lub wyłączenie SAR szybu
- Warstwa zarządzania PARTS (Alg. WS, RC) określa **ILE** i **KTÓRE CIĄGI** nagrzewnic
- Warstwa zarządzania PARTPG (Alg. RN) określa **KTÓRE KONKRETNIE** nagrzewnice w ciągu
- Warstwa regulacji obu podsystemów utrzymuje zadane temperatury (50°C, 2°C)

---

## 2. Załączanie i Wyłączanie Nagrzewnic

### 2.1 Warunki Startowe Załączenia Nagrzewnicy

**Nagrzewnica może być załączona gdy spełnione są wszystkie warunki:**

1. Zawór regulacyjny sprawny, gotowość operacyjna przepustnicy dolotowej
2. Zawór i przepustnica pracują w trybie sterowania zdalnego
3. Parametry wody grzewczej powyżej dolnej dopuszczalnej granicy
4. Przepustnica na wylocie powietrza z nagrzewnicy otwarta
5. Sygnał żądania załączenia nagrzewnicy związany z osiągnięciem określonej granicy ujemnej temperatury zewnętrznej (według Tab. 1)
6. LUB sygnał programowego załączenia nagrzewnicy przy rotacji nagrzewnic

**Sekwencja załączania:**
- Otwarcie przepustnicy na dolocie zimnego powietrza do nagrzewnicy
- Rozpoczęcie procesu regulacji (AUTO lub MANUAL)

📖 **[Szczegółowe sekwencje dla wszystkich przejść](../02-algorytmy/algorytmy.md#algorytm-ws-automatyczny-wybór-scenariusza-pracy)**

### 2.2 Wyłączenie Nagrzewnicy z Ruchu

**Nagrzewnica jest wyłączana gdy:**
- Parametry wody grzewczej osiągną wartości poniżej dolnej dopuszczalnej granicy
- Nastąpi zamknięcie przepustnicy na wylocie powietrza z nagrzewnicy
- Wystąpi sygnał żądania wyłączenia nagrzewnicy związany z osiągnięciem określonej temperatury zewnętrznej (według Tab. 1 - temperatura Tzw)
- Wystąpi sygnał programowego wyłączenia nagrzewnicy przy rotacji nagrzewnic

**Sekwencja wyłączania:**
- Ustawienie zaworu regulacyjnego w pozycji minimalnego otwarcia (20%)
- Zamknięcie przepustnicy dolotowej powietrza zimnego

**⚠️ Każde awaryjne wyłączenie nagrzewnicy powoduje załączenie sygnalizacji alarmowej systemu, co wymaga dokonania operacji skwitowania przez obsługę.**

---

## 3. Układy Pracy Ciągów Grzewczych

System może pracować w dwóch stabilnych układach pracy:

### 3.1 Układ PODSTAWOWY

**Charakterystyka:**
- Wyrzutnie poziomu +4,30m zasilane z ciągu pierwszego (wentylator W1)
- Wyrzutnie poziomu +7,90m zasilane z ciągu drugiego (wentylator W2)
- Przepustnica na spince ciągów wentylacyjnych: **ZAMKNIĘTA**
- Przepustnice w ciągach: **OTWARTE**
- Oba ciągi pracują niezależnie

**Sterowanie wentylatorami w układzie podstawowym:**
- **W1 pracuje z maksymalną prędkością** (NWmax, zazwyczaj 50 Hz)
- **W2 jest wentylatorem regulacyjnym** - zmienia prędkość według regulatora PID
- Taka konfiguracja zapewnia pełną moc ciągu pierwszego (priorytet +4,30m)

**Warunki aktywacji:**
- Temperatura zewnętrzna < -11°C (wymagane > 4 nagrzewnice)
- LUB świadoma decyzja operatora w trybie MANUAL
- LUB rotacja układów pracy ciągów (cykliczna zmiana)

### 3.2 Układ OGRANICZONY

**Charakterystyka:**
- Wyrzutnie poziomu +4,30m zasilane z ciągu drugiego (wentylator W2) przez spinę ciągów
- Wyrzutnie poziomu +7,90m: **NIE ZASILANE**
- Przepustnica na spince ciągów wentylacyjnych: **OTWARTA**
- Przepustnica na kolektorze ciepłego powietrza ciągu pierwszego: **ZAMKNIĘTA**
- Przepustnica na zasilaniu wyrzutni poziomu +7,90m: **ZAMKNIĘTA**
- Pozostałe przepustnice: **OTWARTE**

**Sterowanie wentylatorami w układzie ograniczonym:**
- W1: **WYŁĄCZONY**
- W2: pracuje z regulacją PID (25-50 Hz)

**Warunki aktywacji:**
- Ilość wymaganych nagrzewnic ≤ ilość nagrzewnic ciągu drugiego w gotowości operacyjnej
- Dla 4 sprawnych nagrzewnic C2: zakres temperatur do **-11°C**
- Dla 3 sprawnych nagrzewnic C2: zakres temperatur do **-8°C**
- Dla 2 sprawnych nagrzewnic C2: zakres temperatur do **-4°C**
- Dla 1 sprawnej nagrzewnicy C2: zakres temperatur do **-1°C**

**Ograniczenia:**
- Spadek temperatury zewnętrznej poniżej dopuszczalnej → automatyczne przejście do układu podstawowego

### 3.3 Układy Przejściowe

W trybie AUTO, układy pracy różne od Podstawowego i Ograniczonego są **układami przejściowymi**.
Występują podczas przechodzenia z jednego trybu stabilnego do drugiego.

W trybie MANUAL operator może dowolnie kształtować układ zasilania.

---

## 4. Scenariusze i Algorytm Automatycznego Sterowania

### 4.1 Algorytm Automatycznego Wyboru Scenariusza

System wykorzystuje **Algorytm WS** do automatycznego doboru scenariusza pracy (S0-S8) w zależności od temperatury zewnętrznej.

**Kluczowe cechy algorytmu:**
- Ciągły monitoring temperatury zewnętrznej
- Automatyczny dobór ilości nagrzewnic według tabeli poniżej
- Histereza przy wyłączaniu (zapobiega częstym przełączeniom)
- Bezpieczne sekwencje przejść między scenariuszami
- Koordynacja z algorytmami rotacji RC i RN

📖 **[Szczegółowy algorytm WS](../02-algorytmy/algorytmy.md#algorytm-ws-automatyczny-wybór-scenariusza-pracy)** | **[Flowchart](../02-algorytmy/schematy/algorytm-WS-wybor-scenariusza-flowchart.svg)**

### 4.2 Tabela Scenariuszy

Tabela 1: Stan systemu sterowania w zależności od temperatury zewnętrznej (t_zewn)

| ID | Zakres Temp. | Nagrzewnice | Ciąg 1 (W1) | Ciąg 2 (W2) | Układ Pracy | Nawiew | Temp. Wył. | Hist. |
|----|-------------|-------------|-------------|-------------|-------------|--------|-----------|-------|
| S0 | t ≥ 3°C | - | OFF | OFF | - | - | - | - |
| S1 | -1<t≤2 | N1 | PID | OFF | Podstawowy | +4,30m | t≥3 | 1°C |
| S2 | -4<t≤-1 | N1-N2 | PID | OFF | Podstawowy | +4,30m | t≥0 | 1°C |
| S3 | -8<t≤-4 | N1-N3 | PID | OFF | Podstawowy | +4,30m | t≥-3 | 1°C |
| S4 | -11<t≤-8 | N1-N4 | PID lub MAX | OFF | Podstawowy | +4,30m | t≥-6 | 2°C |
| S5 | -15<t≤-11 | N1-N5 | MAX | PID | Podstawowy | +4,30m +7,90m | t≥-10 | 1°C |
| S6 | -18<t≤-15 | N1-N6 | MAX | PID | Podstawowy | +4,30m +7,90m | t≥-13 | 2°C |
| S7 | -21<t≤-18 | N1-N7 | MAX | PID | Podstawowy | +4,30m +7,90m | t≥-15 | 3°C |
| S8 | t≤-21 | N1-N8 | MAX | PID | Podstawowy | +4,30m +7,90m | t≥-20 | 1°C |

**Uwagi do tabeli stanów:**

**Układy pracy w poszczególnych scenariuszach:**
- **S0:** System wyłączony - brak ogrzewania
- **S1-S4:** Układ **Podstawowy** - tylko ciąg 1 pracuje (priorytet +4,30m)
  - Nagrzewnice N1-N4 z ciągu 1
  - Wentylator W1 sterowany PID
  - Wentylator W2 wyłączony
  - Nawiew TYLKO na +4,30m
- **S5-S8:** Układ **Podstawowy** - oba ciągi pracują
  - Ciąg 1: N1-N4 (zawsze pełne 4 nagrzewnice)
  - Ciąg 2: N5-N8 (tyle ile potrzeba)
  - W1 pracuje z MAX (50 Hz)
  - W2 sterowany PID (wentylatorem regulacyjnym)
  - Nawiew na +4,30m I +7,90m

**Układ Ograniczony (alternatywny):**
- Może być użyty w S1-S4 podczas **cyklicznej rotacji układów** (Algorytm RC)
- W2 przez spinę ciągów zasila +4,30m zamiast W1
- W1 wyłączony, W2 sterowany PID
- Cel: wyrównanie eksploatacji ciągów
- Nagrzewnice: N5-N8 (z ciągu 2)

**Sterowanie wentylatorami:**
- **PID** = sterowanie regulatorem PID (25-50 Hz) - zmienia prędkość dla utrzymania Ts=2°C w szybie
- **MAX** = stała maksymalna prędkość (50 Hz) - pełna moc
- **OFF** = wentylator wyłączony

**Parametry stałe:**
- Temperatura docelowa na wylocie z nagrzewnicy: **50°C**
- Otwarcie zaworu przy wyłączeniu: **20%** (ochrona antyzamrożeniowa)

### 4.3 Hierarchia Algorytmów

System wykorzystuje **trzy współpracujące algorytmy** do sterowania:

1. **Algorytm WS: Automatyczny Wybór Scenariusza**
   - Określa **ILE nagrzewnic** potrzeba (S0-S8) na podstawie t_zewn
   - Tabela powyżej definiuje scenariusze
   - Ciągły monitoring i histereza

2. **Algorytm RC: Rotacja Układów Pracy Ciągów**
   - Określa **KTÓRY CIĄG** pracuje w S1-S4 (Podstawowy: C1, Ograniczony: C2)
   - Wyrównuje eksploatację W1 i W2
   - 📖 [Szczegóły](../02-algorytmy/algorytmy.md#algorytm-rc-cykliczna-rotacja-układów-pracy-ciągów)

3. **Algorytm RN: Rotacja Nagrzewnic w Ciągu**
   - Określa **KTÓRE KONKRETNIE** nagrzewnice pracują w ciągu
   - Wyrównuje eksploatację N1-N8
   - 📖 [Szczegóły](../02-algorytmy/algorytmy.md#algorytm-rn-cykliczna-rotacja-nagrzewnic-w-obrębie-ciągu)

**Tabela scenariuszy określa ILOŚĆ wymaganych nagrzewnic, ale nie konkretne numery.**
**KTÓRE nagrzewnice** pracują jest określane dynamicznie przez algorytmy RC i RN.

**Przykład dla S3 (3 nagrzewnice):**
- Tydzień 1: mogą pracować N1, N2, N3 (ciąg 1)
- Tydzień 2: mogą pracować N2, N3, N4 (ciąg 1, po rotacji RN)
- Tydzień 3: mogą pracować N5, N6, N7 (ciąg 2, po rotacji RC)
- Tydzień 4: mogą pracować N6, N7, N8 (ciąg 2, po rotacji RN)

---

## 5. Parametry Systemowe

Tabela 2: Parametry konfiguracyjne systemu

| Parameter | Wartość | Jednostka | Opis |
|-----------|---------|-----------|------|
| Temperatura docelowa Tz | 50 | °C | Temperatura wyjściowa z nagrzewnicy |
| Temperatura docelowa Ts | 2 | °C | Temperatura w szybie na poziomie -30m |
| Min pozycja zaworu (Pzmin) | 20 | % | Minimalne otwarcie zaworu, ochrona przed zamarzaniem |
| Max pozycja zaworu (Pzmax) | 100 | % | Maksymalne otwarcie zaworu |
| Min częstotliwość wentylatorów (NWmin) | 25 | Hz | Minimalna prędkość obrotowa |
| Max częstotliwość wentylatorów (NWmax) | 50 | Hz | Maksymalna prędkość (dla 4 nagrzewnic) |

**Uwaga:** Nastawy regulatorów PID (Kp, Ti, Td) będą dobrane doświadczalnie podczas procesu uruchomienia UAR na obiekcie.

## 6. Parametry Techniczne - Podsumowanie

Tabela 3: Zestawienie głównych parametrów technicznych

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

---

## 7. Schematy

![Schemat nawiewu powietrza](../03-projekt-instalacji/schematy/nawiew_z_dolnego_ciagu_wentylacyjnego.svg)

📊 **Więcej schematów:** [Projekt instalacji](../03-projekt-instalacji/projekt-instalacji.md)

---

## 8. Monitoring i Diagnostyka

Wszystkie wejściowe sygnały pomiarowe systemu są testowane na poziomie sterownika PLC:

**Testowanie torów pomiarowych:**
- Sprawdzanie ciągłości torów pomiarowych (wykrywanie przerw i zwarć)
- Programowe filtrowanie i uśrednianie sygnałów
- Kontrola czy dany pomiar mieści się w dopuszczalnym zakresie

**Cel:** Wzrost bezpieczeństwa działania systemu.

**⚠️ Uwaga:** Każde zakłócenie spowodowane niedotrzymaniem warunków (sprawność układów pomiarowych, sprawność sterowanych urządzeń, odpowiedni poziom mocy cieplnej czynnika grzewczego) może skutkować **utratą stabilności SAR i przełączeniem systemu na sterowanie ręczne.**

---

## 9. System SCADA/HMI - Wymagania Podstawowe

System sterowania realizowany na sterowniku PLC z regulatorami PID.

**Poziom sterowania (PLC):**
- Realizacja algorytmów regulacji PARTPG i PARTS
- Bloki funkcyjne regulatorów PID dla:
  - UAR temperatury powietrza z nagrzewnic (8 pętli PID)
  - UAR temperatury w szybie (2 pętle PID dla wentylatorów W1 i W2)
- Sterowanie zaworami regulacyjnymi i przepustnicami
- Monitoring czujników temperatury
- Generowanie sygnałów alarmowych

**Tryby pracy:**
- **AUTO** - praca w trybie automatycznym (regulacja PID)
- **MANUAL** - sterowanie ręczne zdalne
- Bezuderzeniowe (bumpless) przejście między trybami sterowania

**Funkcje automatyczne:**
- Automatyczne załączanie/wyłączanie nagrzewnic według Tab. 1
- Cykliczna rotacja nagrzewnic w jednym ciągu wentylacyjnym (Algorytm RN)
- Cykliczna zmiana układów pracy ciągów grzewczych (Algorytm RC)

**Parametry do ustawienia przez technologa:**
- Wartości zadane: Tz (50°C), Ts (2°C)
- Nastawy regulatorów PID: Kp, Ti, Td (dobierane doświadczalnie podczas rozruchu)
- Okres rotacji nagrzewnic
- Okres zmiany układów pracy ciągów

---

## 10. Wizualizacja Systemu

📊 **[Pełna wizualizacja systemu z osadzonymi diagramami](../03-projekt-instalacji/projekt-instalacji.md)**

Dokument zawiera:
- Wszystkie scenariusze S0-S8 z diagramami
- Przykłady rotacji układów i nagrzewnic
- Schematy UAR
- Monitoring i diagnostyka

---

## 🔗 Powiązane Dokumenty

- [Algorytmy WS, RC, RN](../02-algorytmy/algorytmy.md) - szczegółowe opisy algorytmów sterowania
- [Projekt instalacji](../03-projekt-instalacji/projekt-instalacji.md) - schematy instalacji grzewczej
- [Dokumentacja wejściowa](./dokumentacja-wejsciowa/) - pliki otrzymane od zleceniodawcy

---

**Czas czytania:** ~60-90 minut  
**Dla kogo:** wszyscy użytkownicy systemu, technolodzy, programiści PLC, operatorzy
