# Algorytm WS: Automatyczny Wybór Scenariusza Pracy

> **Część dokumentacji:** Algorytmy Sterowania  
> **Powiązane algorytmy:** [Algorytm RC](./algorytm-RC-rotacja-ciagow.md), [Algorytm RN](./algorytm-RN-rotacja-nagrzewnic.md)  
> **Wizualizacja:** [Flowchart](./schematy/algorytm-WS-wybor-scenariusza-flowchart.svg)

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

Szczegółowa tabela scenariuszy znajduje się w [dokumentacji głównej - Sekcja 5](../01-system/system.md#5-scenariusze).

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
| **CZAS_MIĘDZY_ZAŁĄCZENIAMI** | 30 | sekundy | Odstęp między załączaniem kolejnych nagrzewnic |
| **CZAS_MIĘDZY_WYŁĄCZENIAMI** | 30 | sekundy | Odstęp między wyłączaniem kolejnych nagrzewnic |
| **TIMEOUT_ZMIANY_SCENARIUSZA** | 600 | sekundy | Max. czas na zmianę scenariusza (alarm po przekroczeniu) |

**Uzasadnienie wartości:**
- **CYKL_MONITORINGU_TEMP** - szybka reakcja na zmiany pogody, niewielkie obciążenie PLC
- **300s** dla CZAS_UTRZYMANIA_PRZY_AWARII - 5 minut to czas wystarczający na diagnostykę/naprawę czujnika
- **3 próbki** dla filtru - eliminacja pojedynczych skoków (zakłócenia), zachowanie responsywności
- **60s** dla stabilizacji - zapobiega oscylacjom przy temperaturach granicznych

## 5. Algorytm Krok po Kroku

**Diagram przepływu algorytmu:**

![Algorytm WS - Wybór Scenariusza](./schematy/algorytm-WS-wybor-scenariusza-flowchart.svg)

**Pseudokod:**

```
ZMIENNE GLOBALNE:
  - aktualny_scenariusz = S0                    // Scenariusz (S0-S8)
  - t_zewn_bufor[FILTR_UŚREDNIANIA] = []       // Bufor pomiarów temp.
  - ostatni_poprawny_odczyt = 0                 // Ostatni prawidłowy odczyt temp.
  - timestamp_ostatniej_zmiany = 0              // Timestamp ostatniej zmiany scenariusza
  - timestamp_ostatniego_odczytu = 0            // Dla wykrywania awarii czujnika
  - alarm_czujnik_temp = FAŁSZ                  // Flaga awarii czujnika

PARAMETRY:
  - CYKL_MONITORINGU_TEMP = 10                  // [sekundy]
  - CZAS_UTRZYMANIA_PRZY_AWARII = 300           // [sekundy]
  - FILTR_UŚREDNIANIA = 3                       // [próbki]
  - CZAS_STABILIZACJI_SCENARIUSZA = 60          // [sekundy]
  - CZAS_MIĘDZY_ZAŁĄCZENIAMI = 30               // [sekundy]
  - CZAS_MIĘDZY_WYŁĄCZENIAMI = 30               // [sekundy]
  - TIMEOUT_ZMIANY_SCENARIUSZA = 600            // [sekundy]

GŁÓWNA PĘTLA (co CYKL_MONITORINGU_TEMP sekund):
  
  KROK 1: Odczyt i walidacja temperatury zewnętrznej
    t_zewn_raw = Odczytaj_Czujnik_Temperatury_Zewnętrznej()
    
    // Walidacja odczytu
    JEŻELI t_zewn_raw = NULL LUB 
           t_zewn_raw < -40°C LUB 
           t_zewn_raw > 50°C WTEDY
      
      // Awaria czujnika
      alarm_czujnik_temp = PRAWDA
      Rejestruj_Alarm("Awaria czujnika temperatury zewnętrznej")
      
      czas_od_ostatniego_odczytu = czas_systemowy - timestamp_ostatniego_odczytu
      
      JEŻELI czas_od_ostatniego_odczytu < CZAS_UTRZYMANIA_PRZY_AWARII WTEDY
        // Utrzymaj ostatni scenariusz
        t_zewn = ostatni_poprawny_odczyt
        Rejestruj_Zdarzenie("Utrzymanie scenariusza " + aktualny_scenariusz + 
                           " (awaria czujnika, t=" + t_zewn + "°C)")
      W PRZECIWNYM RAZIE:
        // Za długi czas bez odczytu - przejdź na tryb bezpieczny (S4 lub aktualny)
        Rejestruj_Alarm("KRYTYCZNE: Brak odczytu > " + CZAS_UTRZYMANIA_PRZY_AWARII + "s")
        Przełącz_Na_Tryb_Manual()
        PRZEJDŹ DO KOŃCA PĘTLI
      KONIEC JEŻELI
    
    W PRZECIWNYM RAZIE:
      // Odczyt prawidłowy
      alarm_czujnik_temp = FAŁSZ
      ostatni_poprawny_odczyt = t_zewn_raw
      timestamp_ostatniego_odczytu = czas_systemowy
      
      // Dodaj do bufora i oblicz średnią (filtr antyfluktuacyjny)
      Dodaj_Do_Bufora(t_zewn_bufor, t_zewn_raw)
      t_zewn = Średnia(t_zewn_bufor)
    
    KONIEC JEŻELI
  
  KROK 2: Określ wymagany scenariusz na podstawie temperatury
    wymagany_scenariusz = Określ_Scenariusz_Dla_Temperatury(t_zewn, aktualny_scenariusz)
  
  KROK 3: Sprawdź czy wymagana zmiana scenariusza
    JEŻELI wymagany_scenariusz = aktualny_scenariusz WTEDY
      // Brak zmiany - kontynuuj w aktualnym scenariuszu
      PRZEJDŹ DO KOŃCA PĘTLI
    KONIEC JEŻELI
    
    // Sprawdź czas stabilizacji (zapobieganie oscylacjom)
    czas_od_ostatniej_zmiany = czas_systemowy - timestamp_ostatniej_zmiany
    
    JEŻELI czas_od_ostatniej_zmiany < CZAS_STABILIZACJI_SCENARIUSZA WTEDY
      // Za krótki czas od ostatniej zmiany
      Rejestruj_Zdarzenie("Zmiana scenariusza odroczona (stabilizacja)")
      PRZEJDŹ DO KOŃCA PĘTLI
    KONIEC JEŻELI
  
  KROK 4: Sprawdź tryb pracy
    JEŻELI tryb_pracy ≠ AUTO WTEDY
      // W trybie MANUAL operator kontroluje system
      Rejestruj_Zdarzenie("Scenariusz " + wymagany_scenariusz + 
                         " wymagany, ale tryb=MANUAL")
      PRZEJDŹ DO KOŃCA PĘTLI
    KONIEC JEŻELI
  
  KROK 5: Wykonaj zmianę scenariusza
    Rejestruj_Zdarzenie("Zmiana scenariusza: " + aktualny_scenariusz + 
                       " → " + wymagany_scenariusz + " (t=" + t_zewn + "°C)")
    
    timestamp_start_zmiany = czas_systemowy
    
    wynik = Wykonaj_Zmianę_Scenariusza(aktualny_scenariusz, wymagany_scenariusz)
    
    JEŻELI wynik = SUKCES WTEDY
      aktualny_scenariusz = wymagany_scenariusz
      timestamp_ostatniej_zmiany = czas_systemowy
      
      czas_zmiany = czas_systemowy - timestamp_start_zmiany
      Rejestruj_Zdarzenie("Scenariusz " + aktualny_scenariusz + 
                         " aktywny (zmiana: " + czas_zmiany + "s)")
    
    W PRZECIWNYM RAZIE:
      Rejestruj_Alarm("BŁĄD zmiany scenariusza " + aktualny_scenariusz + 
                     " → " + wymagany_scenariusz)
      
      // Próba powrotu do bezpiecznego stanu
      JEŻELI aktualny_scenariusz ≠ S0 WTEDY
        // Zostań w aktualnym scenariuszu i zgłoś alarm
        Przełącz_Na_Tryb_Manual()
      KONIEC JEŻELI
    
    KONIEC JEŻELI

KONIEC PĘTLI

//=============================================================================
// FUNKCJA: Określenie wymaganego scenariusza z histerezą
//=============================================================================

FUNKCJA Określ_Scenariusz_Dla_Temperatury(t_zewn, aktualny_scenariusz):
  
  // Progi włączania (temperatura spada - dodajemy nagrzewnice)
  JEŻELI t_zewn ≥ 3.0 WTEDY
    ZWRÓĆ S0
  
  JEŻELI t_zewn > 2.0 LUB (t_zewn > -1.0 ORAZ aktualny_scenariusz = S0) WTEDY
    // Histereza: S0→S1 przy 2°C, ale S1→S0 dopiero przy 3°C
    JEŻELI aktualny_scenariusz = S0 WTEDY
      ZWRÓĆ S0  // Zostań w S0
    W PRZECIWNYM RAZIE:
      ZWRÓĆ S1  // Utrzymuj S1
    KONIEC JEŻELI
  KONIEC JEŻELI
  
  // S1: -1°C < t ≤ 2°C (wyłączenie: t ≥ 3°C)
  JEŻELI t_zewn > -1.0 WTEDY
    ZWRÓĆ S1
  KONIEC JEŻELI
  
  // Histereza S1→S0
  JEŻELI t_zewn > 0.0 ORAZ aktualny_scenariusz = S1 WTEDY
    ZWRÓĆ S0
  KONIEC JEŻELI
  
  // S2: -4°C < t ≤ -1°C (wyłączenie: t ≥ 0°C)
  JEŻELI t_zewn > -4.0 WTEDY
    ZWRÓĆ S2
  KONIEC JEŻELI
  
  // Histereza S2→S1
  JEŻELI t_zewn ≥ 0.0 ORAZ aktualny_scenariusz = S2 WTEDY
    ZWRÓĆ S1
  KONIEC JEŻELI
  
  // S3: -8°C < t ≤ -4°C (wyłączenie: t ≥ -3°C)
  JEŻELI t_zewn > -8.0 WTEDY
    ZWRÓĆ S3
  KONIEC JEŻELI
  
  // Histereza S3→S2
  JEŻELI t_zewn ≥ -3.0 ORAZ aktualny_scenariusz = S3 WTEDY
    ZWRÓĆ S2
  KONIEC JEŻELI
  
  // S4: -11°C < t ≤ -8°C (wyłączenie: t ≥ -6°C, histereza 2°C)
  JEŻELI t_zewn > -11.0 WTEDY
    ZWRÓĆ S4
  KONIEC JEŻELI
  
  // Histereza S4→S3
  JEŻELI t_zewn ≥ -6.0 ORAZ aktualny_scenariusz = S4 WTEDY
    ZWRÓĆ S3
  KONIEC JEŻELI
  
  // S5: -15°C < t ≤ -11°C (wyłączenie: t ≥ -10°C)
  JEŻELI t_zewn > -15.0 WTEDY
    ZWRÓĆ S5
  KONIEC JEŻELI
  
  // Histereza S5→S4
  JEŻELI t_zewn ≥ -10.0 ORAZ aktualny_scenariusz = S5 WTEDY
    ZWRÓĆ S4
  KONIEC JEŻELI
  
  // S6: -18°C < t ≤ -15°C (wyłączenie: t ≥ -13°C, histereza 2°C)
  JEŻELI t_zewn > -18.0 WTEDY
    ZWRÓĆ S6
  KONIEC JEŻELI
  
  // Histereza S6→S5
  JEŻELI t_zewn ≥ -13.0 ORAZ aktualny_scenariusz = S6 WTEDY
    ZWRÓĆ S5
  KONIEC JEŻELI
  
  // S7: -21°C < t ≤ -18°C (wyłączenie: t ≥ -15°C, histereza 3°C)
  JEŻELI t_zewn > -21.0 WTEDY
    ZWRÓĆ S7
  KONIEC JEŻELI
  
  // Histereza S7→S6
  JEŻELI t_zewn ≥ -15.0 ORAZ aktualny_scenariusz = S7 WTEDY
    ZWRÓĆ S6
  KONIEC JEŻELI
  
  // S8: t ≤ -21°C (wyłączenie: t ≥ -20°C)
  JEŻELI t_zewn ≤ -21.0 WTEDY
    ZWRÓĆ S8
  KONIEC JEŻELI
  
  // Histereza S8→S7
  JEŻELI t_zewn ≥ -20.0 ORAZ aktualny_scenariusz = S8 WTEDY
    ZWRÓĆ S7
  KONIEC JEŻELI
  
  // Domyślnie zwróć aktualny scenariusz (nie powinno wystąpić)
  ZWRÓĆ aktualny_scenariusz

KONIEC FUNKCJI

//=============================================================================
// FUNKCJA: Wykonanie zmiany scenariusza
//=============================================================================

FUNKCJA Wykonaj_Zmianę_Scenariusza(scenariusz_stary, scenariusz_nowy):
  
  timestamp_start = czas_systemowy
  
  // Pobierz konfiguracje scenariuszy
  config_stara = Pobierz_Konfigurację_Scenariusza(scenariusz_stary)
  config_nowa = Pobierz_Konfigurację_Scenariusza(scenariusz_nowy)
  
  // Sprawdź timeout
  PODCZAS (czas_systemowy - timestamp_start) < TIMEOUT_ZMIANY_SCENARIUSZA:
    
    // KROK 1: Zatrzymaj zbędne nagrzewnice (jeśli przechodzimy na niższy scenariusz)
    JEŻELI config_nowa.ilość_nagrzewnic < config_stara.ilość_nagrzewnic WTEDY
      
      ilość_do_wyłączenia = config_stara.ilość_nagrzewnic - config_nowa.ilość_nagrzewnic
      
      // Pobierz listę nagrzewnic do wyłączenia (koordynacja z Algorytmem RC i RN)
      nagrzewnice_do_wyłączenia = Pobierz_Nagrzewnice_Do_Wyłączenia(
                                    config_stara, 
                                    ilość_do_wyłączenia)
      
      // Wyłączaj stopniowo
      DLA KAŻDEJ N w nagrzewnice_do_wyłączenia:
        wynik = Wyłącz_Nagrzewnicę(N)
        JEŻELI wynik ≠ SUKCES WTEDY
          Rejestruj_Alarm("Błąd wyłączenia " + N)
          // Kontynuuj mimo błędu (nie przerywaj sekwencji)
        KONIEC JEŻELI
        Czekaj(CZAS_MIĘDZY_WYŁĄCZENIAMI sekund)
      KONIEC DLA
    
    KONIEC JEŻELI
    
    // KROK 2: Skonfiguruj wentylatory
    wynik_W1 = Konfiguruj_Wentylator(W1, config_nowa.tryb_W1, config_nowa.freq_W1)
    wynik_W2 = Konfiguruj_Wentylator(W2, config_nowa.tryb_W2, config_nowa.freq_W2)
    
    JEŻELI wynik_W1 ≠ SUKCES LUB wynik_W2 ≠ SUKCES WTEDY
      Rejestruj_Alarm("Błąd konfiguracji wentylatorów")
      ZWRÓĆ BŁĄD
    KONIEC JEŻELI
    
    Czekaj(10 sekund)  // Stabilizacja wentylatorów
    
    // KROK 3: Skonfiguruj przepustnice (układ podstawowy/ograniczony)
    wynik_przepustnice = Konfiguruj_Przepustnice(config_nowa.układ_pracy)
    
    JEŻELI wynik_przepustnice ≠ SUKCES WTEDY
      Rejestruj_Alarm("Błąd konfiguracji przepustnic")
      ZWRÓĆ BŁĄD
    KONIEC JEŻELI
    
    Czekaj(5 sekund)
    
    // KROK 4: Uruchom dodatkowe nagrzewnice (jeśli przechodzimy na wyższy scenariusz)
    JEŻELI config_nowa.ilość_nagrzewnic > config_stara.ilość_nagrzewnic WTEDY
      
      ilość_do_załączenia = config_nowa.ilość_nagrzewnic - config_stara.ilość_nagrzewnic
      
      // Pobierz listę nagrzewnic do załączenia (koordynacja z Algorytmem RC i RN)
      nagrzewnice_do_załączenia = Pobierz_Nagrzewnice_Do_Załączenia(
                                     config_nowa, 
                                     ilość_do_załączenia)
      
      // Załączaj stopniowo
      DLA KAŻDEJ N w nagrzewnice_do_załączenia:
        wynik = Załącz_Nagrzewnicę(N)
        JEŻELI wynik ≠ SUKCES WTEDY
          Rejestruj_Alarm("Błąd załączenia " + N)
          // Kontynuuj (system może działać z mniejszą ilością nagrzewnic)
        KONIEC JEŻELI
        Czekaj(CZAS_MIĘDZY_ZAŁĄCZENIAMI sekund)
      KONIEC DLA
    
    KONIEC JEŻELI
    
    // KROK 5: Weryfikacja stanu końcowego
    czas_weryfikacji = 30  // sekundy
    Czekaj(czas_weryfikacji sekund)
    
    JEŻELI Weryfikuj_Scenariusz(scenariusz_nowy) = PRAWDA WTEDY
      ZWRÓĆ SUKCES
    W PRZECIWNYM RAZIE:
      Rejestruj_Alarm("Weryfikacja scenariusza " + scenariusz_nowy + " NIEPOWODZENIE")
      ZWRÓĆ BŁĄD
    KONIEC JEŻELI
  
  KONIEC PODCZAS
  
  // Przekroczono timeout
  Rejestruj_Alarm("TIMEOUT zmiany scenariusza (>" + TIMEOUT_ZMIANY_SCENARIUSZA + "s)")
  ZWRÓĆ BŁĄD

KONIEC FUNKCJI

//=============================================================================
// FUNKCJA: Pobranie konfiguracji scenariusza
//=============================================================================

FUNKCJA Pobierz_Konfigurację_Scenariusza(scenariusz):
  
  PRZYPADEK scenariusz:
    
    S0:
      ZWRÓĆ {
        ilość_nagrzewnic: 0,
        tryb_W1: OFF,
        tryb_W2: OFF,
        freq_W1: 0,
        freq_W2: 0,
        układ_pracy: NULL,
        nawiew: NULL
      }
    
    S1:
      ZWRÓĆ {
        ilość_nagrzewnic: 1,
        tryb_W1: PID,
        tryb_W2: OFF,
        freq_W1: 25-50,  // Regulacja PID
        freq_W2: 0,
        układ_pracy: "Podstawowy lub Ograniczony",  // Zależy od Algorytmu RC
        nawiew: "+4,30m"
      }
    
    S2:
      ZWRÓĆ {
        ilość_nagrzewnic: 2,
        tryb_W1: PID,
        tryb_W2: OFF,
        freq_W1: 25-50,
        freq_W2: 0,
        układ_pracy: "Podstawowy lub Ograniczony",
        nawiew: "+4,30m"
      }
    
    S3:
      ZWRÓĆ {
        ilość_nagrzewnic: 3,
        tryb_W1: PID,
        tryb_W2: OFF,
        freq_W1: 25-50,
        freq_W2: 0,
        układ_pracy: "Podstawowy lub Ograniczony",
        nawiew: "+4,30m"
      }
    
    S4:
      ZWRÓĆ {
        ilość_nagrzewnic: 4,
        tryb_W1: PID,  // Lub MAX jeśli temp. bardzo niska
        tryb_W2: OFF,
        freq_W1: 25-50,
        freq_W2: 0,
        układ_pracy: "Podstawowy lub Ograniczony",
        nawiew: "+4,30m"
      }
    
    S5:
      ZWRÓĆ {
        ilość_nagrzewnic: 5,
        tryb_W1: MAX,
        tryb_W2: PID,
        freq_W1: 50,    // Stała maksymalna częstotliwość
        freq_W2: 25-50, // Regulacja PID
        układ_pracy: "Podstawowy",  // ZAWSZE podstawowy w S5-S8
        nawiew: "+4,30m +7,90m"
      }
    
    S6:
      ZWRÓĆ {
        ilość_nagrzewnic: 6,
        tryb_W1: MAX,
        tryb_W2: PID,
        freq_W1: 50,
        freq_W2: 25-50,
        układ_pracy: "Podstawowy",
        nawiew: "+4,30m +7,90m"
      }
    
    S7:
      ZWRÓĆ {
        ilość_nagrzewnic: 7,
        tryb_W1: MAX,
        tryb_W2: PID,
        freq_W1: 50,
        freq_W2: 25-50,
        układ_pracy: "Podstawowy",
        nawiew: "+4,30m +7,90m"
      }
    
    S8:
      ZWRÓĆ {
        ilość_nagrzewnic: 8,
        tryb_W1: MAX,
        tryb_W2: PID,
        freq_W1: 50,
        freq_W2: 25-50,
        układ_pracy: "Podstawowy",
        nawiew: "+4,30m +7,90m"
      }
  
  KONIEC PRZYPADEK

KONIEC FUNKCJI

//=============================================================================
// FUNKCJA: Pobranie nagrzewnic do załączenia/wyłączenia
//=============================================================================

FUNKCJA Pobierz_Nagrzewnice_Do_Załączenia(config, ilość):
  
  // KOORDYNACJA z Algorytmem RC i RN
  // Algorytm RC decyduje o układzie (Podstawowy: C1, Ograniczony: C2)
  // Algorytm RN decyduje które nagrzewnice w ciągu (rotacja N1-N4 lub N5-N8)
  
  aktualny_układ = Pobierz_Aktualny_Układ()  // Od Algorytmu RC
  
  JEŻELI config.układ_pracy = "Podstawowy lub Ograniczony" WTEDY
    // Scenariusze S1-S4 - decyduje Algorytm RC
    
    JEŻELI aktualny_układ = "Podstawowy" WTEDY
      // Użyj ciągu 1 (N1-N4)
      ciąg = CIĄG1
    W PRZECIWNYM RAZIE:
      // Użyj ciągu 2 (N5-N8)
      ciąg = CIĄG2
    KONIEC JEŻELI
    
    // Pobierz nagrzewnice z Algorytmu RC (uwzględnia rotację)
    nagrzewnice = Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy(ciąg, ilość)
  
  W PRZECIWNYM RAZIE:  // Układ Podstawowy (S5-S8)
    // W S5-S8 zawsze:
    // - C1 pracuje w całości (N1-N4) - WSZYSTKIE nagrzewnice C1 muszą pracować
    // - C2 pracuje z N5, N6, N7, N8 w zależności od scenariusza
    
    JEŻELI ilość ≤ 4 WTEDY
      // Tylko C1 - Deleguj wybór do RN (śledzi czasy pracy dla statystyk)
      nagrzewnice = Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy(CIĄG1, ilość)
      // Uwaga: W S1-S4 wybór jest dynamiczny (rotacja RN aktywna)
      // W praktyce przy braku awarii to będą N1-N4 w S4, ale 5B decyduje
    W PRZECIWNYM RAZIE:
      // C1 cały + częściowo C2
      // W S5-S8 wszystkie N1-N4 MUSZĄ pracować (brak rezerwowej w C1)
      nagrzewnice_C1 = Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy(CIĄG1, 4)
      ilość_C2 = ilość - 4
      
      // W C2 może działać Algorytm RN (jeśli są nagrzewnice rezerwowe)
      nagrzewnice_C2 = Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy(CIĄG2, ilość_C2)
      
      nagrzewnice = nagrzewnice_C1 + nagrzewnice_C2
    KONIEC JEŻELI
  
  KONIEC JEŻELI
  
  ZWRÓĆ nagrzewnice

KONIEC FUNKCJI

FUNKCJA Pobierz_Nagrzewnice_Do_Wyłączenia(config, ilość):
  
  // Wyłączaj w odwrotnej kolejności niż załączanie
  // Najpierw z C2, potem z C1
  
  aktualnie_pracujące = Pobierz_Listę_Aktywnych_Nagrzewnic()
  
  // Sortuj: najpierw C2 (N5-N8), potem C1 (N1-N4)
  // W ramach ciągu: od najwyższego numeru do najniższego
  posortowane = Sortuj_Descending(aktualnie_pracujące)
  
  nagrzewnice_do_wyłączenia = posortowane[0:ilość]
  
  ZWRÓĆ nagrzewnice_do_wyłączenia

KONIEC FUNKCJI

//=============================================================================
// FUNKCJE POMOCNICZE
//=============================================================================

FUNKCJA Załącz_Nagrzewnicę(N):
  
  Rejestruj_Zdarzenie("Załączanie nagrzewnicy " + N)
  
  // Sprawdź gotowość
  JEŻELI NIE Sprawdź_Gotowość_Nagrzewnicy(N) WTEDY
    Rejestruj_Alarm("Nagrzewnica " + N + " nie jest gotowa")
    ZWRÓĆ BŁĄD
  KONIEC JEŻELI
  
  // Sekwencja załączania (zgodnie z sekcją 3.1 dokumentacji głównej)
  
  // 1. Ustaw zawór na pozycję minimalną (20%)
  Ustaw_Zawór(N, 20%)
  Czekaj(3 sekundy)
  
  // 2. Otwórz przepustnicę dolotową
  Ustaw_Przepustnicę_Dolot(N, OTWARTA)
  Czekaj(5 sekund)
  
  // 3. Aktywuj regulator PID
  Ustaw_Regulator_PID(N, tryb=AUTO, setpoint=50°C)
  Czekaj(10 sekund)
  
  // 4. Weryfikacja
  temp = Odczytaj_Temperaturę(N)
  JEŻELI temp > 30°C WTEDY  // Nagrzewnica zaczyna działać
    Rejestruj_Zdarzenie("Nagrzewnica " + N + " załączona (T=" + temp + "°C)")
    ZWRÓĆ SUKCES
  W PRZECIWNYM RAZIE:
    Rejestruj_Alarm("Nagrzewnica " + N + " nie osiąga temperatury")
    ZWRÓĆ BŁĄD
  KONIEC JEŻELI

KONIEC FUNKCJI

FUNKCJA Wyłącz_Nagrzewnicę(N):
  
  Rejestruj_Zdarzenie("Wyłączanie nagrzewnicy " + N)
  
  // Sekwencja wyłączania (zgodnie z sekcją 3.2 dokumentacji głównej)
  
  // 1. Zatrzymaj regulator PID, ustaw zawór na 20%
  Ustaw_Regulator_PID(N, tryb=MANUAL)
  Ustaw_Zawór(N, 20%)
  Czekaj(10 sekund)
  
  // 2. Zamknij przepustnicę dolotową
  Ustaw_Przepustnicę_Dolot(N, ZAMKNIĘTA)
  Czekaj(3 sekundy)
  
  Rejestruj_Zdarzenie("Nagrzewnica " + N + " wyłączona")
  ZWRÓĆ SUKCES

KONIEC FUNKCJI

FUNKCJA Konfiguruj_Wentylator(W, tryb, częstotliwość):
  
  JEŻELI tryb = OFF WTEDY
    Zatrzymaj_Wentylator(W)
    ZWRÓĆ SUKCES
  KONIEC JEŻELI
  
  JEŻELI tryb = MAX WTEDY
    Ustaw_Wentylator(W, tryb=MANUAL, częstotliwość=50 Hz)
    ZWRÓĆ SUKCES
  KONIEC JEŻELI
  
  JEŻELI tryb = PID WTEDY
    Ustaw_Wentylator(W, tryb=AUTO, setpoint=2°C)
    ZWRÓĆ SUKCES
  KONIEC JEŻELI
  
  ZWRÓĆ BŁĄD

KONIEC FUNKCJI

FUNKCJA Weryfikuj_Scenariusz(scenariusz):
  
  config = Pobierz_Konfigurację_Scenariusza(scenariusz)
  
  // Sprawdź ilość aktywnych nagrzewnic
  aktywne = Policz_Aktywne_Nagrzewnice()
  JEŻELI aktywne ≠ config.ilość_nagrzewnic WTEDY
    Rejestruj_Alarm("Weryfikacja: nieprawidłowa ilość nagrzewnic")
    ZWRÓĆ FAŁSZ
  KONIEC JEŻELI
  
  // Sprawdź wentylatory
  JEŻELI config.tryb_W1 = OFF ORAZ Wentylator_Pracuje(W1) WTEDY
    Rejestruj_Alarm("Weryfikacja: W1 powinien być wyłączony")
    ZWRÓĆ FAŁSZ
  KONIEC JEŻELI
  
  JEŻELI config.tryb_W2 = OFF ORAZ Wentylator_Pracuje(W2) WTEDY
    Rejestruj_Alarm("Weryfikacja: W2 powinien być wyłączony")
    ZWRÓĆ FAŁSZ
  KONIEC JEŻELI
  
  // Wszystko OK
  ZWRÓĆ PRAWDA

KONIEC FUNKCJI
```

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
  - Algorytm 5 wywołuje funkcje pomocnicze które respektują wybory RC i RN
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
| Brak odczytu t_zewn | Utrzymaj ostatni scenariusz przez CZAS_UTRZYMANIA_PRZY_AWARII (300s), potem alarm krytyczny i tryb MANUAL |
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

## 9. Monitoring i Statystyki

System rejestruje następujące dane:

| Parametr | Opis |
|----------|------|
| Historia temperatury zewnętrznej | Bufor 24h z rozdzielczością co CYKL_MONITORINGU_TEMP |
| Historia scenariuszy | Timestampy zmian S0↔S1↔...↔S8 |
| Liczba zmian scenariusza | Licznik przejść (dziennie/miesięcznie) |
| Średni czas zmiany | Średni czas trwania sekwencji zmiany scenariusza |
| Liczba odroczeń | Ile razy zmiana została odroczona (stabilizacja/koordynacja) |
| Czas w każdym scenariuszu | Łączny czas pracy w S0, S1, ..., S8 [h] |
| Awarie czujnika | Licznik i czas trwania awarii odczytu temperatury |

**Raport dostępny w HMI:**
- Wykres temperatury zewnętrznej (24h/7dni/30dni)
- Timeline scenariuszy (wizualizacja kiedy system był w S0-S8)
- Statystyki zużycia energii w poszczególnych scenariuszach
- Analiza efektywności (czy scenariusze dobierały się optymalnie)

## 10. Szczegółowe Sekwencje Zmian Scenariuszy

Każda zmiana scenariusza wymaga **skoordynowanej sekwencji** operacji na:
- Zaworach regulacyjnych wody grzewczej (20-100%)
- Przepustnicach dolotowych nagrzewnic (otwarte/zamknięte)
- Przepustnicach głównych systemu (kolektory, spinka, wyrzutnie)
- Wentylatorach (start/stop, tryb PID)

**Hierarchia sterowania:**

System ma **trzy poziomy sterowania**:

1. **Algorytm 5 (Nadzorca scenariuszy)** ← monitoruje **t_zewn**
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
t_zewn = 3°C (wzrost)
  ↓
Algorytm WS: "Nie potrzebuję już nagrzewnic" → decyzja o przejściu S1→S0
  ↓
Sekwencja wyłączania:
  1. Przełącz PID nagrzewnicy: AUTO → MANUAL
  2. Zamknij zawór ręcznie: aktualna_pozycja → 20%
  3. Zamknij przepustnicę
  4. Zatrzymaj wentylator
```

#### 5.10.1 Typy Przejść

System rozróżnia 4 typy przejść między scenariuszami:

| Typ | Opis | Przykłady | Złożoność |
|-----|------|-----------|-----------|
| **A** | Wyłączenie systemu | S1→S0 | Niska |
| **B** | Uruchomienie systemu | S0→S1 | Średnia |
| **C** | Zmiana w obrębie jednego ciągu | S1→S2, S2→S3, S3→S4 | Średnia |
| **D** | Uruchomienie drugiego ciągu | S4→S5 | **Wysoka** |
| **E** | Zatrzymanie drugiego ciągu | S5→S4 | **Wysoka** |
| **F** | Zmiana w obrębie dwóch ciągów | S5→S6, S6→S7, S7→S8 | Niska |

#### 5.10.2 Sekwencja TYP A: Wyłączenie Systemu (S1→S0)

**Warunki:** Temperatura wzrosła do t ≥ 3°C

```
SEKWENCJA S1→S0 (Wyłączenie systemu):

UWAGA: Algorytm 5 decyduje o wyłączeniu na podstawie t_zewn ≥ 3°C

KROK 1: Przełącz PID nagrzewnicy w tryb MANUAL
  Ustaw_Regulator_PID(N_aktywna, tryb=MANUAL)
  // PID przestaje regulować, zawór "zamrażany" w aktualnej pozycji

KROK 2: Zamknij zawór wody grzewczej stopniowo do 20%
  aktualna_pozycja = Odczytaj_Pozycję_Zaworu(N_aktywna)
  Dla pozycja = aktualna_pozycja DO 20 KROK -10:
    Ustaw_Zawór(N_aktywna, pozycja)
    Czekaj(2 sekundy)
  KONIEC DLA
  Czekaj(10 sekund)  // Stabilizacja

KROK 3: Zamknij przepustnicę dolotową nagrzewnicy
  Ustaw_Przepustnicę_Dolot(N_aktywna, ZAMKNIĘTA)
  Czekaj(5 sekund)

KROK 4: Zatrzymaj wentylator W1
  Zmniejsz_Częstotliwość(W1, od_aktualnej DO 25Hz, krok=5Hz, czas=2s)
  Czekaj(5 sekund)
  Zatrzymaj_Wentylator(W1)
  
KROK 5: Zamknij przepustnice główne ciągu 1
  Ustaw_Przepustnicę_Kolektor_C1(ZAMKNIĘTA)
  Ustaw_Przepustnicę_Ciąg_C1(ZAMKNIĘTA)

KROK 6: Rejestracja
  Rejestruj_Zdarzenie("Scenariusz S0 aktywny - system wyłączony")
  
Czas sekwencji: ~60 sekund
```

#### 5.10.3 Sekwencja TYP B: Uruchomienie Systemu (S0→S1)

**Warunki:** Temperatura spadła do t ≤ 2°C

```
SEKWENCJA S0→S1 (Uruchomienie systemu):

KROK 1: Otwórz przepustnice główne ciągu 1
  Ustaw_Przepustnicę_Ciąg_C1(OTWARTA)
  Ustaw_Przepustnicę_Kolektor_C1(OTWARTA)
  Ustaw_Przepustnicę_Wyrzutnia_430(OTWARTA)
  Czekaj(10 sekund)  // Stabilizacja ciśnienia

KROK 2: Uruchom wentylator W1
  Uruchom_Wentylator(W1, częstotliwość=25Hz)
  Czekaj(10 sekund)  // Stabilizacja obrotów
  Sprawdź_Prąd_Silnika(W1)  // Weryfikacja pracy

KROK 3: Przygotuj nagrzewnicę N (wybrana przez Algorytm RC/5B)
  Ustaw_Zawór(N, 20%)  // Pozycja startowa
  Czekaj(5 sekund)

KROK 4: Otwórz przepustnicę dolotową nagrzewnicy
  Ustaw_Przepustnicę_Dolot(N, OTWARTA)
  Czekaj(5 sekund)  // Przepływ powietrza przez nagrzewnicę

KROK 5: Aktywuj regulację PID nagrzewnicy
  Ustaw_Regulator_PID(N, tryb=AUTO, setpoint=50°C)
  // Zawór zacznie się otwierać zgodnie z potrzebami
  Czekaj(30 sekund)  // Stabilizacja temperatury

KROK 6: Aktywuj regulację PID wentylatora
  Ustaw_Wentylator(W1, tryb=AUTO, setpoint=2°C)
  // Wentylator zacznie regulować prędkość

KROK 7: Weryfikacja
  temp_N = Odczytaj_Temperaturę(N)
  JEŻELI temp_N < 30°C WTEDY
    Alarm("Nagrzewnica nie osiąga temperatury")
    PRZERWIJ
  KONIEC JEŻELI
  
  Rejestruj_Zdarzenie("Scenariusz S1 aktywny")
  
Czas sekwencji: ~70 sekund
```

#### 5.10.4 Sekwencja TYP C: Dodanie Nagrzewnicy w Tym Samym Ciągu (S1→S2, S2→S3, S3→S4)

**Przykład: S2→S3** (2 nagrzewnice → 3 nagrzewnice)

```
SEKWENCJA S2→S3 (Dodanie trzeciej nagrzewnicy):

UWAGA: Wentylator W1 i nagrzewnice N1, N2 już pracują

KROK 1: Wybierz nagrzewnicę do załączenia
  N_nowa = Algorytm_RN_Wybierz_Nagrzewnicę(CIĄG1, ilość=3)
  // Algorytm RN wybiera na podstawie czasu postoju (najdłużej nieużywana)

KROK 2: Przygotuj nagrzewnicę N_nowa
  Ustaw_Zawór(N_nowa, 20%)
  Czekaj(3 sekundy)

KROK 3: Otwórz przepustnicę dolotową
  Ustaw_Przepustnicę_Dolot(N_nowa, OTWARTA)
  Czekaj(5 sekund)

KROK 4: Aktywuj regulację PID
  Ustaw_Regulator_PID(N_nowa, tryb=AUTO, setpoint=50°C)
  Czekaj(30 sekund)

KROK 5: Weryfikacja i dostrojenie wentylatora
  // PID wentylatora automatycznie dostosuje prędkość
  // do zwiększonego zapotrzebowania (3 nagrzewnice zamiast 2)
  
KROK 6: Sprawdź stabilność
  temp_N_nowa = Odczytaj_Temperaturę(N_nowa)
  JEŻELI |temp_N_nowa - 50°C| > 5°C WTEDY
    Alarm("N_nowa nie osiąga temperatury docelowej")
  KONIEC JEŻELI
  
  Rejestruj_Zdarzenie("Scenariusz S3 aktywny")

Czas sekwencji: ~45 sekund
```

#### 5.10.5 Sekwencja TYP D: Uruchomienie Drugiego Ciągu (S4→S5) 

**Warunki:** Temperatura spadła do t ≤ -11°C  
**Złożoność:** WYSOKA - uruchomienie drugiego poziomu wyrzutni

```
SEKWENCJA S4→S5 (Uruchomienie drugiego ciągu):

UWAGA: Ciąg 1 (N1-N4 + W1) już pracuje w pełnej mocy

KROK 0: Weryfikacja stanu początkowego
  // Sprawdź czy C1 ma 4 aktywne nagrzewnice (wymagane w S4)
  ilość_aktywnych_C1 = Policz_Aktywne_Nagrzewnice(CIĄG1)
  JEŻELI ilość_aktywnych_C1 ≠ 4 WTEDY
    Alarm("S4→S5: Ciąg 1 niekompletny (" + ilość_aktywnych_C1 + "/4)")
    PRZERWIJ
  KONIEC JEŻELI

KROK 1: Przygotuj przepustnice dla układu dwuciągowego
  // Przepustnice ciągu 1 pozostają OTWARTE
  // Otwieramy przepustnice ciągu 2
  Ustaw_Przepustnicę_Ciąg_C2(OTWARTA)
  Ustaw_Przepustnicę_Wyrzutnia_790(OTWARTA)  // DRUGI poziom wyrzutni!
  Czekaj(10 sekund)  // Stabilizacja ciśnienia w systemie

KROK 2: Przełącz W1 na tryb MAX (pełna moc)
  // W1 będzie teraz pracował z maksymalną częstotliwością
  Ustaw_Wentylator(W1, tryb=MANUAL, częstotliwość=50Hz)
  Czekaj(10 sekund)
  Sprawdź_Prąd_Silnika(W1)  // Weryfikacja obciążenia

KROK 3: Uruchom wentylator W2
  Uruchom_Wentylator(W2, częstotliwość=25Hz)
  Czekaj(10 sekund)
  Sprawdź_Prąd_Silnika(W2)

KROK 4: Wybierz i przygotuj pierwszą nagrzewnicę ciągu 2
  // Deleguj wybór do Algorytmu RC (śledzi czasy pracy/postoju)
  N_nowa = Algorytm_RN_Wybierz_Nagrzewnicę(CIĄG2, ilość=1)
  // Może to być N5, N6, N7 lub N8 - zależy od historii pracy
  
  Ustaw_Zawór(N_nowa, 20%)
  Czekaj(5 sekund)

KROK 5: Otwórz przepustnicę dolotową N_nowa
  Ustaw_Przepustnicę_Dolot(N_nowa, OTWARTA)
  Czekaj(5 sekund)

KROK 6: Aktywuj regulację PID dla N_nowa
  Ustaw_Regulator_PID(N_nowa, tryb=AUTO, setpoint=50°C)
  Czekaj(30 sekund)  // Stabilizacja temperatury N_nowa

KROK 7: Aktywuj regulację PID dla W2
  // W2 teraz będzie regulacyjnym wentylatorem
  Ustaw_Wentylator(W2, tryb=AUTO, setpoint=2°C)
  Czekaj(20 sekund)

KROK 8: Weryfikacja systemu dwuciągowego
  temp_N_nowa = Odczytaj_Temperaturę(N_nowa)
  JEŻELI temp_N_nowa < 30°C WTEDY
    Alarm(N_nowa + " nie osiąga temperatury")
    // Wycofaj zmianę - przywróć S4
    PRZERWIJ
  KONIEC JEŻELI
  
  sprawdź_W1 = Sprawdź_Częstotliwość(W1)
  sprawdź_W2 = Sprawdź_Częstotliwość(W2)
  
  JEŻELI sprawdź_W1 ≠ 50Hz LUB sprawdź_W2 < 25Hz WTEDY
    Alarm("Wentylatory nie pracują poprawnie")
    PRZERWIJ
  KONIEC JEŻELI
  
KROK 9: Otwórz przepustnicę kolektora C2
  Ustaw_Przepustnicę_Kolektor_C2(OTWARTA)
  
  Rejestruj_Zdarzenie("Scenariusz S5 aktywny - dwa ciągi w pracy")

Czas sekwencji: ~100 sekund
```

**Kluczowe aspekty S4→S5:**
- ⚠️ Pierwszy raz otwieramy wyrzutnie +7,90m
- ⚠️ W1 przechodzi z PID → MAX (zmiana trybu regulacji)
- ⚠️ Uruchomienie W2 jako regulacyjnego
- ⚠️ Koordynacja dwóch niezależnych ciągów

#### 5.10.6 Sekwencja TYP E: Zatrzymanie Drugiego Ciągu (S5→S4)

**Warunki:** Temperatura wzrosła do t ≥ -10°C  
**Złożoność:** WYSOKA - zamknięcie drugiego poziomu wyrzutni

```
SEKWENCJA S5→S4 (Zatrzymanie drugiego ciągu):

UWAGA: Algorytm 5 decyduje o zatrzymaniu C2 na podstawie t_zewn ≥ -10°C
       Oba ciągi pracują (C1: N1-N4 + W1 MAX, C2: N5 + W2 PID)

KROK 1: Przełącz PID nagrzewnicy N5 w tryb MANUAL
  Ustaw_Regulator_PID(N5, tryb=MANUAL)
  // PID przestaje regulować, przejmujemy ręczne sterowanie
  
KROK 2: Zamknij zawór N5 do 20%
  aktualna_pozycja = Odczytaj_Pozycję_Zaworu(N5)
  Dla pozycja = aktualna_pozycja DO 20 KROK -10:
    Ustaw_Zawór(N5, pozycja)
    Czekaj(2 sekundy)
  KONIEC DLA
  Czekaj(10 sekund)

KROK 3: Zamknij przepustnicę dolotową N5
  Ustaw_Przepustnicę_Dolot(N5, ZAMKNIĘTA)
  Czekaj(5 sekund)

KROK 4: Zatrzymaj wentylator W2
  Zmniejsz_Częstotliwość(W2, od_aktualnej DO 25Hz, krok=5Hz, czas=2s)
  Czekaj(5 sekund)
  Zatrzymaj_Wentylator(W2)

KROK 5: Zamknij przepustnice ciągu 2
  Ustaw_Przepustnicę_Kolektor_C2(ZAMKNIĘTA)
  Ustaw_Przepustnicę_Wyrzutnia_790(ZAMKNIĘTA)  // ⚠️ Zamykamy poziom +7,90m
  Ustaw_Przepustnicę_Ciąg_C2(ZAMKNIĘTA)
  Czekaj(10 sekund)

KROK 6: Przełącz W1 z MAX na PID
  // W1 przejmuje pełną regulację temperatury
  Ustaw_Wentylator(W1, tryb=AUTO, setpoint=2°C)
  Czekaj(20 sekund)  // Stabilizacja regulacji

KROK 7: Weryfikacja
  JEŻELI Wentylator_Pracuje(W2) WTEDY
    Alarm("W2 nie zatrzymał się")
    PRZERWIJ
  KONIEC JEŻELI
  
  temp_szyb = Odczytaj_Temperaturę_Szybu()
  JEŻELI |temp_szyb - 2°C| > 1°C WTEDY
    Alarm("Temperatura szybu niestabilna po przejściu na S4")
  KONIEC JEŻELI
  
  Rejestruj_Zdarzenie("Scenariusz S4 aktywny - jeden ciąg w pracy")

Czas sekwencji: ~70 sekund
```

#### 5.10.7 Sekwencja TYP F: Dodanie Nagrzewnicy w Drugim Ciągu (S5→S6, S6→S7, S7→S8)

**Przykład: S5→S6** (5 nagrzewnic → 6 nagrzewnic)

```
SEKWENCJA S5→S6 (Dodanie szóstej nagrzewnicy):

UWAGA: C1 (N1-N4) + W1 MAX, C2 (N5) + W2 PID już pracują

KROK 1: Wybierz nagrzewnicę z ciągu 2
  N_nowa = Algorytm_RN_Wybierz_Nagrzewnicę(CIĄG2, ilość=2)
  // Algorytm RN wybiera na podstawie czasu postoju (najdłużej nieużywana)

KROK 2: Przygotuj N_nowa
  Ustaw_Zawór(N_nowa, 20%)
  Czekaj(3 sekundy)

KROK 3: Otwórz przepustnicę dolotową
  Ustaw_Przepustnicę_Dolot(N_nowa, OTWARTA)
  Czekaj(5 sekund)

KROK 4: Aktywuj regulację PID
  Ustaw_Regulator_PID(N_nowa, tryb=AUTO, setpoint=50°C)
  Czekaj(30 sekund)

KROK 5: Weryfikacja
  // PID W2 automatycznie dostosuje prędkość
  temp_N_nowa = Odczytaj_Temperaturę(N_nowa)
  JEŻELI |temp_N_nowa - 50°C| > 5°C WTEDY
    Alarm("N_nowa nie osiąga temperatury")
  KONIEC JEŻELI
  
  Rejestruj_Zdarzenie("Scenariusz S6 aktywny")

Czas sekwencji: ~45 sekund
```

#### 5.10.8 Tabela Czasów Sekwencji

| Przejście | Typ | Czas [s] | Uwagi |
|-----------|-----|----------|-------|
| S0→S1 | B | ~70 | Uruchomienie systemu od zera |
| S1→S0 | A | ~60 | Wyłączenie systemu |
| S1→S2, S2→S3, S3→S4 | C | ~45 | Dodanie nagrzewnicy w C1 |
| S4→S3, S3→S2, S2→S1 | C | ~50 | Usunięcie nagrzewnicy z C1 |
| **S4→S5** | **D** | **~100** | **⚠️ uruchomienie C2** |
| **S5→S4** | **E** | **~70** | **⚠️ zatrzymanie C2** |
| S5→S6, S6→S7, S7→S8 | F | ~45 | Dodanie nagrzewnicy w C2 |
| S8→S7, S7→S6, S6→S5 | F | ~50 | Usunięcie nagrzewnicy z C2 |

#### 5.10.9 Koordynacja Przepustnic - Stany dla Wszystkich Scenariuszy

| Element | S0 | S1-S4 Podst. | S1-S4 Ogr. | S5-S8 |
|---------|----|--------------|-----------| ------|
| **Ciąg 1:** | | | | |
| Przepustnica C1 | Z | **O** | **Z** | **O** |
| Kolektor C1 | Z | **O** | **Z** | **O** |
| Wyrzutnia +4,30m | Z | **O** | Z | **O** |
| **Ciąg 2:** | | | | |
| Przepustnica C2 | Z | Z | **O** | **O** |
| Kolektor C2 | Z | Z | **O** | **O** |
| Wyrzutnia +7,90m | Z | Z | Z | **O** |
| **Spinka:** | | | | |
| Przepustnica spinka | Z | Z | **O** | Z |

**Legenda:** O = Otwarta, Z = Zamknięta

**Kluczowe przejścia przepustnic:**
- **S4→S5:** Otwieramy wyrzutnię +7,90m po raz pierwszy
- **S5→S4:** Zamykamy wyrzutnię +7,90m
- **Układ Podst.→Ogr.:** Zamykamy C1, otwieramy spinę i C2
- **Układ Ogr.→Podst.:** Zamykamy spinę i C2, otwieramy C1

#### 5.10.10 Zarządzanie Zaworami - Strategia Bezpieczeństwa

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

---


