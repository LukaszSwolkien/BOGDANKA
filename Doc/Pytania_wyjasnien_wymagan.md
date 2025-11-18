# Pytania Wyjaśniające - System Sterowania Nagrzewnicami BOGDANKA Szyb 2

## 1. Architektura Systemu

### 1.1 Układ nagrzewnic
- **Pytanie**: Czy nagrzewnice N1-N8 są podłączone równolegle do głównego kanału powietrza czy szeregowo (powietrze przechodzi przez kolejne nagrzewnice)?
- **Znaczenie**: Ma wpływ na projekt hydrauliczny, dobór wentylatorów i sposób regulacji temperatury.

### 1.2 Przypisanie wentylatorów
- **Pytanie**: Które nagrzewnice są obsługiwane przez wentylator W1, a które przez W2?
  - Czy W1 obsługuje N1-N4, a W2 obsługuje N5-N8?
  - Czy oba wentylatory wspólnie obsługują wszystkie nagrzewnice?
- **Znaczenie**: Krytyczne dla określenia zależności sterowania i sekwencji uruchamiania.

### 1.3 Wymiary i przepływy
- **Pytanie**: Jakie są nominalne parametry systemu?
  - Przepływ powietrza przez jedną nagrzewnicę [m³/h]
  - Wydajność wentylatorów W1 i W2 [m³/h]
  - Moc grzewcza pojedynczej nagrzewnicy [kW]
  - Średnica kanałów powietrza [mm]
- **Znaczenie**: Niezbędne do prawidłowego doboru czujników, siłowników i obliczenia czasów reakcji.

## 2. Czujniki i Pomiary

### 2.1 Lokalizacja czujników temperatury
- **Pytanie**: Gdzie dokładnie są zamontowane czujniki temperatury?
  - Temperatura zewnętrzna (t_zewn) - lokalizacja poboru powietrza?
  - Temperatura wylotowa - czy osobny czujnik dla każdej nagrzewnicy, czy wspólny na wylocie z grupy nagrzewnic?
  - Czy są czujniki temperatury na wlocie do każdej nagrzewnicy?
- **Znaczenie**: Wpływa na logikę sterowania i algorytmy regulacji.

### 2.2 Typ i dokładność czujników
- **Pytanie**: Jakie są wymagania dla czujników?
  - Typ czujnika (PT100, PT1000, termopar, inne)?
  - Zakres pomiarowy czujników?
  - Wymagana dokładność pomiaru [°C]?
  - Czas odpowiedzi czujnika?
- **Znaczenie**: Dobór odpowiednich przetworników i modułów wejściowych PLC.

### 2.3 Monitoring przepustnic i zaworów
- **Pytanie**: Czy przepustnice i zawory posiadają:
  - Informację zwrotną o pozycji (feedback analogowy 0-100%)?
  - Krańcówki otwarte/zamknięte?
  - Moment obrotowy/siłę zamykania?
- **Znaczenie**: Wpływa na diagnostykę i obsługę awarii.

## 3. Elementy Wykonawcze

### 3.1 Przepustnice
- **Pytanie**: Jakie są parametry przepustnic?
  - Typ napędu (elektryczny 230VAC, 24VDC, pneumatyczny)?
  - Czas pełnego otwarcia/zamknięcia [s]?
  - Typ sterowania (dwupołożeniowe ON/OFF, modulujące 0-10V/4-20mA)?
  - Czy są to przepustnice przeciwpożarowe z funkcją bezpieczeństwa?
- **Znaczenie**: Określenie modułów wyjściowych PLC i logiki sterowania.

### 3.2 Zawory regulacyjne wody
- **Pytanie**: Jaki typ zaworów jest zastosowany?
  - Zawory trójdrogowe czy dwudrogowe?
  - Napęd proporcjonalny (0-10V, 4-20mA) czy krokowy?
  - Czas przejazdu zaworu z pozycji 0% do 100% [s]?
  - Charakterystyka zaworu (liniowa, równoprocentowa)?
  - Czy zawór posiada funkcję awaryjnego zamknięcia (fail-safe)?
- **Znaczenie**: Dobór odpowiedniego algorytmu PID i nastaw regulatora.

### 3.3 Wentylatory
- **Pytanie**: Jak są sterowane wentylatory?
  - Prędkość stała czy regulowana (falownik)?
  - Jeśli regulowana - zakres regulacji [Hz lub %]?
  - Pobór mocy [kW]?
  - Czy są wymagane soft-startery?
  - Informacja zwrotna o pracy (przekaźnik termiczny, przetwornik prądu)?
- **Znaczenie**: Projektowanie obwodów mocy i zabezpieczeń.

## 4. Sekwencje Sterowania

### 4.1 Czasy opóźnień
- **Pytanie**: Jakie czasy opóźnień są wymagane?
  - Czas między otwarciem przepustnic a włączeniem wentylatora?
  - Czas między włączeniem wentylatora a otwarciem zaworu wody?
  - Czas oczekiwania na stabilizację temperatury przed przejściem do regulacji PID?
- **Znaczenie**: Bezpieczeństwo i efektywność energetyczna systemu.

### 4.2 Wyłączanie nagrzewnicy
- **Pytanie**: W dokumencie jest informacja "Ustaw zawór regulacyjny wody na poziomie 20%" przy wyłączaniu. Czy to oznacza:
  - Zawór ma pozostać otwarty na 20% na stałe po wyłączeniu?
  - Czy zawór ma być stopniowo zamykany z 100% do 20% przed wyłączeniem nagrzewnicy?
  - Jak długo zawór ma pozostać na 20% przed pełnym zamknięciem?
- **Znaczenie**: Ochrona wymiennika ciepła przed zamarzaniem i termicznym uderzeniem.

### 4.3 Monitorowanie temperatury podczas wyłączania
- **Pytanie**: "Monitoruj temperaturę na wlocie i wylocie" - jakie są kryteria kontynuacji wyłączania?
  - Czy czekamy aż temperatura spadnie poniżej określonej wartości?
  - Jaka jest ta temperatura progowa?
  - Jaki jest maksymalny czas oczekiwania?
- **Znaczenie**: Bezpieczeństwo procesu wyłączania.

## 5. Regulacja PID

### 5.1 Indywidualna czy wspólna regulacja
- **Pytanie**: Czy każda nagrzewnica ma osobny regulator PID z własnymi nastawami, czy wszystkie aktywne nagrzewnice są sterowane jednym regulatorem?
- **Znaczenie**: Liczba wymaganych bloków PID w programie sterującym.

### 5.2 Nastawy PID
- **Pytanie**: Czy podane wartości PID (Kp=2.0, Ki=1, Kd=0.1) są wartościami:
  - Sprawdzonymi eksperymentalnie na istniejącej instalacji?
  - Teoretycznymi do dostrojenia podczas rozruchu?
  - Czy wymagane jest auto-tunning PID?
- **Znaczenie**: Czas wdrożenia i jakość regulacji.

### 5.3 Ograniczenia regulacji
- **Pytanie**: Czy są dodatkowe ograniczenia dla regulatora PID?
  - Maksymalna szybkość zmian wyjścia [%/s]?
  - Anti-windup dla członu całkującego?
  - Pasmo nieczułości (dead-band)?
- **Znaczenie**: Stabilność regulacji i żywotność siłowników.

## 6. Histereza i Przełączanie Stanów

### 6.1 Mechanizm histerezy
- **Pytanie**: Jak działa histereza w tabeli stanów?
  - Przykład S4: "Temp. włączenia: -8°C, Temp. wyłączenia: -6°C, Histereza: 2°C"
  - Czy to oznacza, że przy spadku z -7°C do -8,1°C włączamy N4, a wyłączamy dopiero przy wzroście do -5,9°C?
  - Czy histereza działa tylko przy wyłączaniu, czy również przy włączaniu?
- **Znaczenie**: Uniknięcie częstego przełączania (chattering) nagrzewnic.

### 6.2 Przejścia między stanami
- **Pytanie**: Co się dzieje przy przejściu między stanami (np. S3 → S4)?
  - Czy nagrzewnice N1, N2, N3 pozostają włączone bez przerwy?
  - Czy jest jakaś sekwencja stabilizacji przed włączeniem N4?
  - Jak synchronizować włączanie nowej nagrzewnicy z już pracującymi?
- **Znaczenie**: Płynność pracy systemu i unikanie skoków temperatury.

## 7. Obsługa Awarii

### 7.1 Priorytet alarmów
- **Pytanie**: Jaki jest priorytet alarmów i odpowiednie reakcje systemu?
  - Alarmy krytyczne (wymuszające bezpieczny stop całego systemu)?
  - Alarmy ostrzegawcze (kontynuacja pracy w trybie awaryjnym)?
  - Czy są alarmy, które blokują restart po obsłudze?
- **Znaczenie**: Projektowanie systemu alarmowego i bezpieczeństwa.

### 7.2 Szczegóły obsługi konkretnych awarii
- **Pytanie**: "Temperatura wylotowa < 40°C przy pracy - Zwiększ otwarcie zaworu do 100%, alarm"
  - Czy to dotyczy każdej nagrzewnicy osobno?
  - Jak długo czekać przed ogłoszeniem alarmu?
  - Czy nagrzewnica ma być wyłączona po czasie bez poprawy?
- **Znaczenie**: Logika diagnostyczna i bezpieczeństwo.

### 7.3 Awaria wentylatora
- **Pytanie**: "Wentylator nie pracuje - Wyłącz odpowiednie nagrzewnice"
  - Które dokładnie nagrzewnice mają być wyłączone przy awarii W1?
  - Które przy awarii W2?
  - Czy jest możliwość pracy w trybie awaryjnym z jednym wentylatorem?
- **Znaczenie**: Określenie zależności między wentylatorami a nagrzewnicami.

## 8. System Wizualizacji SCADA

### 8.1 Zakres wizualizacji
- **Pytanie**: Jakie są wymagania dla systemu SCADA?
  - Czy SCADA ma być na PC (Windows, Linux) czy panelu HMI?
  - Lokalne w szafie sterowniczej czy w naziemnej dyspetczerni?
  - Czy wymagany jest zdalny dostęp (VPN, web-interface)?
- **Znaczenie**: Dobór platformy SCADA i architektury sieci.

### 8.2 Funkcjonalność
- **Pytanie**: Jakie funkcje ma posiadać SCADA?
  - Prezentacja synoptyczna (podobna do dostarczonego diagramu)?
  - Trendy historyczne (czas archiwizacji)?
  - Lista alarmów z historią?
  - Możliwość zmiany nastaw (zadana temperatura, nastawy PID)?
  - Ręczne sterowanie elementami (bypass automatyki)?
  - Raporty i logi zdarzeń?
- **Znaczenie**: Zakres projektu wizualizacji.

### 8.3 Komunikacja
- **Pytanie**: Jaki protokół komunikacyjny między PLC a SCADA?
  - Modbus TCP/RTU?
  - OPC UA?
  - Proprietary (np. S7, EtherNet/IP)?
- **Znaczenie**: Dobór sterownika PLC i oprogramowania SCADA.

## 9. Sterownik i Szafa Sterownicza

### 9.1 Wymagania dla PLC
- **Pytanie**: Czy są preferencje dotyczące producenta PLC?
  - Siemens (S7-1200, S7-1500)?
  - Allen-Bradley (CompactLogix)?
  - Schneider Electric (Modicon M2xx)?
  - Inny?
- **Znaczenie**: Dostępność części zamiennych i know-how serwisu.

### 9.2 Redundancja
- **Pytanie**: Czy wymagana jest redundancja?
  - Podwójny PLC (hot-standby)?
  - Redundantne zasilanie?
  - Redundantne łącza komunikacyjne?
- **Znaczenie**: Koszty i złożoność systemu.

### 9.3 Środowisko pracy
- **Pytanie**: Jakie są warunki środowiskowe dla szafy sterowniczej?
  - Temperatura otoczenia [°C]?
  - Wilgotność [%]?
  - Zapylenie, wibracje?
  - Czy szafa będzie podziemna czy naziemna?
  - Stopień ochrony IP wymagany?
- **Znaczenie**: Dobór obudowy, klimatyzacji i filtrów.

## 10. Zasilanie i Bezpieczeństwo

### 10.1 Zasilanie elektryczne
- **Pytanie**: Jakie napięcia zasilania są dostępne?
  - Zasilanie główne (400V 3-fazowe, 230V)?
  - Czy jest UPS dla systemu sterowania?
  - Czas podtrzymania na UPS?
- **Znaczenie**: Projektowanie układów zasilania.

### 10.2 Bezpieczeństwo funkcjonalne
- **Pytanie**: Czy system wymaga zgodności z normami bezpieczeństwa?
  - Kategoria bezpieczeństwa wg EN 13849-1 (np. Cat. 3)?
  - Safety PLC dla funkcji bezpieczeństwa?
  - Przycisk STOP awaryjny (E-STOP)?
  - Blokady dostępu (door interlocks)?
- **Znaczenie**: Certyfikacja i procedury bezpieczeństwa.

### 10.3 Przepisy górnicze
- **Pytanie**: Jakie specyficzne przepisy górnicze mają zastosowanie?
  - Czy urządzenia muszą być ex-proof (zagrożenie wybuchem metanu)?
  - Czy wymagane są specjalne certyfikaty dla urządzeń podziemnych?
- **Znaczenie**: Dobór urządzeń certyfikowanych dla górnictwa.

## 11. Rozruch i Testowanie

### 11.1 FAT (Factory Acceptance Test)
- **Pytanie**: Czy wymagane są testy fabryczne przed dostawą?
  - Symulacja pracy z rzeczywistymi urządzeniami?
  - Test wizualizacji SCADA?
  - Dokumentacja z testów?
- **Znaczenie**: Harmonogram projektu i wymagane zasoby.

### 11.2 Procedury rozruchu
- **Pytanie**: Jakie są wymagania dla rozruchu na miejscu?
  - Udział projektanta przy komisjoningu?
  - Szkolenie dla operatorów i serwisu?
  - Czas na dostrojenie i optymalizację?
- **Znaczenie**: Planowanie zasobów i kosztów wdrożenia.

## 12. Dokumentacja

### 12.1 Zakres dokumentacji
- **Pytanie**: Jaki zakres dokumentacji jest wymagany?
  - Schematy elektryczne (CAD, format)?
  - Program PLC (źródło + kompilat)?
  - Projekt SCADA (źródło)?
  - Instrukcje obsługi i serwisu?
  - Dokumentacja as-built?
- **Znaczenie**: Czas potrzebny na przygotowanie dokumentacji.

### 12.2 Język dokumentacji
- **Pytanie**: W jakim języku ma być przygotowana dokumentacja?
  - Polski?
  - Angielski?
  - Dwujęzyczna?
- **Znaczenie**: Tłumaczenia i lokalizacja tekstów w SCADA.

---

## Podsumowanie

Niniejszy dokument zawiera **kluczowe pytania wymagające wyjaśnienia** przed rozpoczęciem szczegółowego projektu systemu sterowania.

**Priorytet odpowiedzi:**
- 🔴 **Krytyczne** (pytania 1.2, 2.1, 3.1-3.3, 6.2, 7.3) - bez odpowiedzi niemożliwe jest rozpoczęcie projektu
- 🟡 **Ważne** (pytania 1.1, 1.3, 4.1-4.3, 5.1-5.2, 8.1-8.3, 9.1) - wpływają na koszty i czas realizacji
- 🟢 **Opcjonalne** (pozostałe) - mogą być ustalone w trakcie projektu lub stosowane wartości typowe

**Zalecenie:** Zorganizowanie spotkania z eksploatacją i działem technicznym BOGDANKA w celu omówienia i uzyskania odpowiedzi na powyższe pytania.

