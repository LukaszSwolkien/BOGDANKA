# Pseudokod Algorytmów Sterowania - BOGDANKA Szyb 2

**SINGLE SOURCE OF TRUTH - Pseudokod implementacyjny**

Ten dokument zawiera **jedyne obowiązujące źródło pseudokodu** dla algorytmów WS, RC, RN systemu sterowania BOGDANKA Szyb 2.

---

## Zasady Użycia Tego Dokumentu

**KLUCZOWE ZASADY:**

1. **Źródło Prawdy:** Ten plik jest **jedynym źródłem prawdy** dla pseudokodu algorytmów
2. **Implementacja 1:1:** Każda implementacja (symulacja, PLC) musi **dokładnie** odzwierciedlać ten pseudokod
3. **Aktualizacje:** Wszelkie zmiany w logice algorytmów **NAJPIERW** wprowadzamy tutaj, potem w kodzie
4. **Weryfikacja:** Po testach/symulacji, jeśli wykryjemy błąd w logice → aktualizujemy TEN plik

**Proces zmian:**
1. Problem wykryty w testach/symulacji
2. Analiza logiki w pseudokodzie
3. **Aktualizacja pseudokodu** w tym pliku
4. Re-implementacja w kodzie zgodnie z nowym pseudokodem
5. Weryfikacja poprawności

---

## Zawartość

1. [Globalne Parametry Rotacyjne (RC/RN)](#globalne-parametry-rotacyjne-rcn)
2. [Algorytm WS: Automatyczny Wybór Scenariusza](#algorytm-ws-automatyczny-wybór-scenariusza)
3. [Algorytm RC: Rotacja Układów Pracy Ciągów](#algorytm-rc-rotacja-układów-pracy-ciągów)
4. [Algorytm RN: Rotacja Nagrzewnic w Ciągu](#algorytm-rn-rotacja-nagrzewnic-w-ciągu)

---

## Globalne Parametry Rotacyjne (RC/RN)

Parametry te są współdzielone przez algorytmy RC i RN:

| Parametr | Wartość domyślna | Jednostka | Zakres | Stosowanie |
|----------|-----------------|-----------|--------|------------|
| **CYKL_PĘTLI_ALGORYTMÓW** | 60 | sekundy | 10‑600 | Częstość wywołania głównej pętli RC i RN (aktualizacja liczników, warunków) |
| **HISTEREZA_CZASOWA** | 300 | sekundy | 60‑900 | Bufor czasowy przed uznaniem, że upłynął okres rotacji układów (RC) |
| **MIN_DELTA_CZASU** | 3600 | sekundy | 1800‑7200 | Minimalna różnica czasów pracy nagrzewnic, aby RN wykonał zamianę |
| **ODSTĘP_PO_ZMIANIE_UKŁADU** | 3600 | sekundy | 1800‑7200 | Czas blokujący RN po zakończeniu RC (`czas_ostatniej_zmiany_układu`) |
| **ODSTĘP_MIĘDZY_ROTACJAMI** | 900 | sekundy | 600‑1800 | Globalny odstęp pomiędzy rotacjami RN w różnych ciągach |

---

# Algorytm WS: Automatyczny Wybór Scenariusza

## Pseudokod

```
ZMIENNE GLOBALNE:
  - aktualny_scenariusz = S0                    // Scenariusz (S0-S8)
  - T_zewn_bufor[FILTR_UŚREDNIANIA] = []       // Bufor pomiarów temp.
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
    T_zewn_raw = Odczytaj_Czujnik_Temperatury_Zewnętrznej()
    
    // Walidacja odczytu
    JEŻELI T_zewn_raw = NULL LUB 
           T_zewn_raw < -40°C LUB 
           T_zewn_raw > 50°C WTEDY
      
      // Awaria czujnika
      alarm_czujnik_temp = PRAWDA
      Rejestruj_Alarm("Awaria czujnika temperatury zewnętrznej")
      
      czas_od_ostatniego_odczytu = czas_systemowy - timestamp_ostatniego_odczytu
      
      JEŻELI czas_od_ostatniego_odczytu < CZAS_UTRZYMANIA_PRZY_AWARII WTEDY
        // Utrzymaj ostatni scenariusz
        T_zewn = ostatni_poprawny_odczyt
        Rejestruj_Zdarzenie("Utrzymanie scenariusza " + aktualny_scenariusz + 
                           " (awaria czujnika, t=" + T_zewn + "°C)")
      W PRZECIWNYM RAZIE:
        // Za długi czas bez odczytu - przejdź na tryb bezpieczny (S4 lub aktualny)
        Rejestruj_Alarm("KRYTYCZNE: Brak odczytu > " + CZAS_UTRZYMANIA_PRZY_AWARII + "s")
        Przełącz_Na_Tryb_Manual()
        PRZEJDŹ DO KOŃCA PĘTLI
      KONIEC JEŻELI
    
    W PRZECIWNYM RAZIE:
      // Odczyt prawidłowy
      alarm_czujnik_temp = FAŁSZ
      ostatni_poprawny_odczyt = T_zewn_raw
      timestamp_ostatniego_odczytu = czas_systemowy
      
      // Dodaj do bufora i oblicz średnią (filtr antyfluktuacyjny)
      Dodaj_Do_Bufora(T_zewn_bufor, T_zewn_raw)
      T_zewn = Średnia(T_zewn_bufor)
    
    KONIEC JEŻELI
  
  KROK 2: Określ wymagany scenariusz na podstawie temperatury
    wymagany_scenariusz = Określ_Scenariusz_Dla_Temperatury(T_zewn, aktualny_scenariusz)
  
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
  
  KROK 4A: Sprawdź blokady RC/RN
    JEŻELI zmiana_układu_w_toku = PRAWDA LUB rotacja_nagrzewnic_w_toku = PRAWDA WTEDY
      Rejestruj_Zdarzenie("Zmiana scenariusza odroczona (koordynacja RC/RN)")
      PRZEJDŹ DO KOŃCA PĘTLI
    KONIEC JEŻELI
  
  KROK 5: Wykonaj zmianę scenariusza
    Rejestruj_Zdarzenie("Zmiana scenariusza: " + aktualny_scenariusz + 
                       " → " + wymagany_scenariusz + " (t=" + T_zewn + "°C)")
    
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

FUNKCJA Określ_Scenariusz_Dla_Temperatury(T_zewn, aktualny_scenariusz):
  
  // Progi włączania (temperatura spada - dodajemy nagrzewnice)
  JEŻELI T_zewn ≥ 3.0 WTEDY
    ZWRÓĆ S0
  KONIEC JEŻELI
  
  JEŻELI T_zewn > 2.0 WTEDY
    // Strefa histerezy: utrzymuj S1 aż do 3°C, ale nie wymuszaj przełączenia przy ochłodzeniu
    JEŻELI aktualny_scenariusz = S1 WTEDY
      ZWRÓĆ S1
    W PRZECIWNYM RAZIE:
      ZWRÓĆ S0
    KONIEC JEŻELI
  KONIEC JEŻELI
  
  // S1: -1°C < t ≤ 2°C (wyłączenie: t ≥ 3°C)
  JEŻELI T_zewn > -1.0 WTEDY
    ZWRÓĆ S1
  KONIEC JEŻELI
  
  // S2: -4°C < t ≤ -1°C (wyłączenie: t ≥ 0°C)
  JEŻELI T_zewn > -4.0 WTEDY
    ZWRÓĆ S2
  KONIEC JEŻELI
  
  // Histereza S2→S1
  JEŻELI T_zewn ≥ 0.0 ORAZ aktualny_scenariusz = S2 WTEDY
    ZWRÓĆ S1
  KONIEC JEŻELI
  
  // S3: -8°C < t ≤ -4°C (wyłączenie: t ≥ -3°C)
  JEŻELI T_zewn > -8.0 WTEDY
    ZWRÓĆ S3
  KONIEC JEŻELI
  
  // Histereza S3→S2
  JEŻELI T_zewn ≥ -3.0 ORAZ aktualny_scenariusz = S3 WTEDY
    ZWRÓĆ S2
  KONIEC JEŻELI
  
  // S4: -11°C < t ≤ -8°C (wyłączenie: t ≥ -6°C, histereza 2°C)
  JEŻELI T_zewn > -11.0 WTEDY
    ZWRÓĆ S4
  KONIEC JEŻELI
  
  // Histereza S4→S3
  JEŻELI T_zewn ≥ -6.0 ORAZ aktualny_scenariusz = S4 WTEDY
    ZWRÓĆ S3
  KONIEC JEŻELI
  
  // S5: -15°C < t ≤ -11°C (wyłączenie: t ≥ -10°C)
  JEŻELI T_zewn > -15.0 WTEDY
    ZWRÓĆ S5
  KONIEC JEŻELI
  
  // Histereza S5→S4
  JEŻELI T_zewn ≥ -10.0 ORAZ aktualny_scenariusz = S5 WTEDY
    ZWRÓĆ S4
  KONIEC JEŻELI
  
  // S6: -18°C < t ≤ -15°C (wyłączenie: t ≥ -13°C, histereza 2°C)
  JEŻELI T_zewn > -18.0 WTEDY
    ZWRÓĆ S6
  KONIEC JEŻELI
  
  // Histereza S6→S5
  JEŻELI T_zewn ≥ -13.0 ORAZ aktualny_scenariusz = S6 WTEDY
    ZWRÓĆ S5
  KONIEC JEŻELI
  
  // S7: -21°C < t ≤ -18°C (wyłączenie: t ≥ -15°C, histereza 3°C)
  JEŻELI T_zewn > -21.0 WTEDY
    ZWRÓĆ S7
  KONIEC JEŻELI
  
  // Histereza S7→S6
  JEŻELI T_zewn ≥ -15.0 ORAZ aktualny_scenariusz = S7 WTEDY
    ZWRÓĆ S6
  KONIEC JEŻELI
  
  // S8: t ≤ -21°C (wyłączenie: t ≥ -20°C)
  JEŻELI T_zewn ≤ -21.0 WTEDY
    ZWRÓĆ S8
  KONIEC JEŻELI
  
  // Histereza S8→S7
  JEŻELI T_zewn ≥ -20.0 ORAZ aktualny_scenariusz = S8 WTEDY
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
        nawiew: "-4,30m"
      }
    
    S2:
      ZWRÓĆ {
        ilość_nagrzewnic: 2,
        tryb_W1: PID,
        tryb_W2: OFF,
        freq_W1: 25-50,
        freq_W2: 0,
        układ_pracy: "Podstawowy lub Ograniczony",
        nawiew: "-4,30m"
      }
    
    S3:
      ZWRÓĆ {
        ilość_nagrzewnic: 3,
        tryb_W1: PID,
        tryb_W2: OFF,
        freq_W1: 25-50,
        freq_W2: 0,
        układ_pracy: "Podstawowy lub Ograniczony",
        nawiew: "-4,30m"
      }
    
    S4:
      ZWRÓĆ {
        ilość_nagrzewnic: 4,
        tryb_W1: PID,  // Lub MAX jeśli temp. bardzo niska
        tryb_W2: OFF,
        freq_W1: 25-50,
        freq_W2: 0,
        układ_pracy: "Podstawowy lub Ograniczony",
        nawiew: "-4,30m"
      }
    
    S5:
      ZWRÓĆ {
        ilość_nagrzewnic: 5,
        tryb_W1: MAX,
        tryb_W2: PID,
        freq_W1: 50,    // Stała maksymalna częstotliwość
        freq_W2: 25-50, // Regulacja PID
        układ_pracy: "Podstawowy",  // ZAWSZE podstawowy w S5-S8
        nawiew: "-4,30m -7,90m"
      }
    
    S6:
      ZWRÓĆ {
        ilość_nagrzewnic: 6,
        tryb_W1: MAX,
        tryb_W2: PID,
        freq_W1: 50,
        freq_W2: 25-50,
        układ_pracy: "Podstawowy",
        nawiew: "-4,30m -7,90m"
      }
    
    S7:
      ZWRÓĆ {
        ilość_nagrzewnic: 7,
        tryb_W1: MAX,
        tryb_W2: PID,
        freq_W1: 50,
        freq_W2: 25-50,
        układ_pracy: "Podstawowy",
        nawiew: "-4,30m -7,90m"
      }
    
    S8:
      ZWRÓĆ {
        ilość_nagrzewnic: 8,
        tryb_W1: MAX,
        tryb_W2: PID,
        freq_W1: 50,
        freq_W2: 25-50,
        układ_pracy: "Podstawowy",
        nawiew: "-4,30m -7,90m"
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
      // W praktyce przy braku awarii to będą N1-N4 w S4, ale RN decyduje
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

---

# Algorytm RC: Rotacja Układów Pracy Ciągów

## Pseudokod

```
ZMIENNE GLOBALNE (współdzielone z Algorytmem RN):
  - aktualny_układ = "Podstawowy"               // aktualny układ pracy
  - zmiana_układu_w_toku = FAŁSZ                // blokada dla koordynacji z RN
  - czas_ostatniej_zmiany_układu = 0            // timestamp dla RN [sekundy]
  - rotacja_nagrzewnic_w_toku = FAŁSZ           // blokada dla koordynacji z RN

ZMIENNE LOKALNE (tylko dla RC):
  - czas_pracy_układu_podstawowego = 0          // [sekundy]
  - czas_pracy_układu_ograniczonego = 0         // [sekundy]
  - czas_ostatniej_zmiany = czas_systemowy      // timestamp ostatniej rotacji układu
  - scenariusz = S0..S8                         // aktualny scenariusz
  - last_update_time = NULL                     // timestamp ostatniej aktualizacji liczników

PARAMETRY:
  - OKRES_ROTACJI_UKŁADÓW                       // definiowany przez technologa [s]
  - HISTEREZA_CZASOWA = 300                     // 5 minut [s]
  - CYKL_PĘTLI_ALGORYTMÓW = 60                  // częstość sprawdzania [s] (domyślnie 1 min)

GŁÓWNA PĘTLA (co CYKL_PĘTLI_ALGORYTMÓW):
  
  KROK 0: Inicjalizacja przy pierwszym uruchomieniu
    JEŻELI last_update_time = NULL WTEDY
      last_update_time = czas_systemowy
      PRZEJDŹ DO KROKU 5  // Pomiń rotację przy pierwszym uruchomieniu
    KONIEC JEŻELI
  
  KROK 1: Sprawdź warunki rotacji
    JEŻELI scenariusz ∈ {S1, S2, S3, S4} ORAZ
           wszystkie_nagrzewnice_C2_sprawne ORAZ
           wentylator_W2_sprawny ORAZ
           tryb = AUTO ORAZ
           brak_alarmów_krytycznych WTEDY
      
      rotacja_możliwa = PRAWDA
    
    W PRZECIWNYM RAZIE:
      rotacja_możliwa = FAŁSZ
      // Poza S1-S4 utrzymujemy definicyjnie układ podstawowy (oba ciągi pracują równolegle)
      JEŻELI scenariusz ∈ {S1, S2, S3, S4} ORAZ aktualny_układ = "Ograniczony" WTEDY
        Wykonaj_Zmianę_Układu("Podstawowy")
      W PRZECIWNYM RAZIE:
        aktualny_układ = "Podstawowy"   // aktualizacja stanu logicznego bez ingerencji sprzętowej
      KONIEC JEŻELI
      PRZEJDŹ DO KROKU 5
    
    KONIEC JEŻELI
  
  KROK 2: Sprawdź czy upłynął okres rotacji
    czas_od_ostatniej_zmiany = czas_systemowy - czas_ostatniej_zmiany
    
    JEŻELI czas_od_ostatniej_zmiany ≥ (OKRES_ROTACJI_UKŁADÓW - HISTEREZA_CZASOWA) WTEDY
      rotacja_wymagana = PRAWDA
    W PRZECIWNYM RAZIE:
      rotacja_wymagana = FAŁSZ
      PRZEJDŹ DO KROKU 5
    KONIEC JEŻELI
  
  KROK 3: Określ nowy układ
    JEŻELI aktualny_układ = "Podstawowy" WTEDY
      nowy_układ = "Ograniczony"
    W PRZECIWNYM RAZIE:
      nowy_układ = "Podstawowy"
    KONIEC JEŻELI
  
  KROK 4: Wykonaj zmianę układu
    JEŻELI rotacja_możliwa = PRAWDA ORAZ rotacja_wymagana = PRAWDA WTEDY
      
      // Sprawdź czy Algorytm RN nie wykonuje rotacji nagrzewnic
      JEŻELI rotacja_nagrzewnic_w_toku = PRAWDA WTEDY
        Rejestruj_Zdarzenie("Zmiana układu odroczona - trwa rotacja nagrzewnic")
        PRZEJDŹ DO KROKU 5
      KONIEC JEŻELI
      
      // Ustaw blokadę dla Algorytmu RC
      zmiana_układu_w_toku = PRAWDA
      
      Rejestruj_Zdarzenie("Rozpoczęcie zmiany układu z " + aktualny_układ + " na " + nowy_układ)
      
      // Sekwencja zmiany układu
      Wykonaj_Zmianę_Układu(nowy_układ)
      
      // Aktualizacja zmiennych
      aktualny_układ = nowy_układ
      czas_ostatniej_zmiany = czas_systemowy
      czas_ostatniej_zmiany_układu = czas_systemowy  // dla koordynacji z RN
      
      Rejestruj_Zdarzenie("Zakończono zmianę układu na " + nowy_układ)
      
      // Zwolnij blokadę
      zmiana_układu_w_toku = FAŁSZ
    
    KONIEC JEŻELI
  
  KROK 5: Aktualizuj liczniki czasu pracy
    // Oblicz rzeczywisty czas który upłynął od ostatniej aktualizacji
    // (uwzględnia przyspieszenie czasu w symulacji i ewentualne opóźnienia w PLC)
    delta_time = czas_systemowy - last_update_time
    
    JEŻELI delta_time > 0 WTEDY
      JEŻELI aktualny_układ = "Podstawowy" WTEDY
        czas_pracy_układu_podstawowego += delta_time
      W PRZECIWNYM RAZIE:
        czas_pracy_układu_ograniczonego += delta_time
      KONIEC JEŻELI
      
      last_update_time = czas_systemowy
    KONIEC JEŻELI

KONIEC PĘTLI

FUNKCJA Wykonaj_Zmianę_Układu(docelowy_układ):
  
  JEŻELI docelowy_układ = "Ograniczony" WTEDY
    // Przejście: Podstawowy → Ograniczony
    
    KROK 1: Zatrzymaj ciąg 1 (stopniowo)
      // Pobierz listę aktualnie aktywnych nagrzewnic C1
      aktywne_C1 = Pobierz_Listę_Aktywnych_Nagrzewnic(CIĄG1)
      
      Dla KAŻDEJ N w aktywne_C1:
        Wyłącz_Nagrzewnicę(N)
        Czekaj(30 sekund)       // stabilizacja
      KONIEC DLA
      Zatrzymaj_Wentylator(W1)
    
    KROK 2: Otwórz przepustnicę na spince ciągów
      Ustaw_Przepustnicę_Spinka(OTWARTA)
      Czekaj(10 sekund)
    
    KROK 3: Zamknij przepustnice ciągu 1
      Ustaw_Przepustnicę_Kolektor_C1(ZAMKNIĘTA)
      Ustaw_Przepustnicę_Wyrzutnia_790(ZAMKNIĘTA)
    
    KROK 4: Uruchom ciąg 2 (stopniowo)
      Uruchom_Wentylator(W2, częstotliwość = 25Hz)
      Czekaj(10 sekund)
      
      // Deleguj wybór nagrzewnic do Algorytmu RC
      nagrzewnice_do_załączenia = Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy(CIĄG2, wymagana_ilość_nagrzewnic)
      
      Dla KAŻDEJ N w nagrzewnice_do_załączenia:
        Załącz_Nagrzewnicę(N)
        Czekaj(30 sekund)            // stabilizacja
      KONIEC DLA
    
    KROK 5: Aktywuj regulację PID dla W2
      Ustaw_Wentylator_W2_Tryb(PID)
      Ustaw_Setpoint_W2(Ts = 2°C)
  
  W PRZECIWNYM RAZIE:  // docelowy_układ = "Podstawowy"
    // Przejście: Ograniczony → Podstawowy
    
    KROK 1: Zatrzymaj ciąg 2 (stopniowo)
      // Pobierz listę aktualnie aktywnych nagrzewnic C2
      aktywne_C2 = Pobierz_Listę_Aktywnych_Nagrzewnic(CIĄG2)
      
      Dla KAŻDEJ N w aktywne_C2:
        Wyłącz_Nagrzewnicę(N)
        Czekaj(30 sekund)
      KONIEC DLA
      Zatrzymaj_Wentylator(W2)
    
    KROK 2: Zamknij przepustnicę na spince ciągów
      Ustaw_Przepustnicę_Spinka(ZAMKNIĘTA)
      Czekaj(10 sekund)
    
    KROK 3: Otwórz przepustnice ciągu 1
      Ustaw_Przepustnicę_Kolektor_C1(OTWARTA)
      Ustaw_Przepustnicę_Ciąg_C1(OTWARTA)
    
    KROK 4: Uruchom ciąg 1 (stopniowo)
      Uruchom_Wentylator(W1, częstotliwość = 25Hz)
      Czekaj(10 sekund)
      
      // Deleguj wybór nagrzewnic do Algorytmu RC
      nagrzewnice_do_załączenia = Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy(CIĄG1, wymagana_ilość_nagrzewnic)
      
      Dla KAŻDEJ N w nagrzewnice_do_załączenia:
        Załącz_Nagrzewnicę(N)
        Czekaj(30 sekund)
      KONIEC DLA
    
    KROK 5: Aktywuj regulację PID dla W1
      Ustaw_Wentylator_W1_Tryb(PID)
      Ustaw_Setpoint_W1(Ts = 2°C)
  
  KONIEC JEŻELI
  
KONIEC FUNKCJI
```

---

# Algorytm RN: Rotacja Nagrzewnic w Ciągu

## Pseudokod

```
ZMIENNE GLOBALNE (współdzielone z Algorytmem RC):
  - aktualny_układ                                       // Podstawowy lub Ograniczony
  - zmiana_układu_w_toku                                 // blokada od RC
  - czas_ostatniej_zmiany_układu                         // timestamp od RC
  - rotacja_nagrzewnic_w_toku = FAŁSZ                    // blokada dla RC
  - czas_ostatniej_rotacji_globalny = 0                  // dla odstępu 15 min [sekundy]

ZMIENNE LOKALNE (dla każdego ciągu osobno):
  - czas_pracy[N1..N8] = [0, 0, 0, 0, 0, 0, 0, 0]       // [sekundy]
  - czas_postoju[N1..N8] = [0, 0, 0, 0, 0, 0, 0, 0]     // [sekundy]
  - timestamp_zalaczenia[N1..N8] = [0, 0, 0, 0, 0, 0, 0, 0] // [timestamp pierwszego załączenia]
  - czas_ostatniej_rotacji[CIĄG1, CIĄG2] = [0, 0]       // [timestamp]
  - nagrzewnice_aktywne[CIĄG] = []                       // lista aktywnych
  - last_update_time = NULL                              // timestamp ostatniej aktualizacji liczników

PARAMETRY:
  - OKRES_ROTACJI_NAGRZEWNIC[S1..S8]  // definiowany przez technologa [s]
  - MIN_DELTA_CZASU                   // definiowany przez technologa [s] (domyślnie 3600)
  - CZAS_STABILIZACJI = 30            // czas na stabilizację po zmianie [s]
  - CYKL_PĘTLI_ALGORYTMÓW = 60        // częstość sprawdzania [s] (współdzielony z RC)

GŁÓWNA PĘTLA (co CYKL_PĘTLI_ALGORYTMÓW):
  
  KROK 0A: Inicjalizacja przy pierwszym uruchomieniu
    JEŻELI last_update_time = NULL WTEDY
      last_update_time = czas_systemowy
      // Zaktualizuj stany nagrzewnic na podstawie aktualnego scenariusza/układu
      Aktualizuj_Stany_Nagrzewnic()
      PRZEJDŹ DO KOŃCA PĘTLI  // Pomiń rotację przy pierwszym uruchomieniu
    KONIEC JEŻELI
  
  DLA KAŻDEGO ciągu w [CIĄG1, CIĄG2]:
    
    KROK 0B: Sprawdź czy ciąg jest aktywny w aktualnym układzie/scenariuszu
      aktualny_scenariusz = Pobierz_Scenariusz()
      aktualny_układ = Pobierz_Układ()  // Podstawowy lub Ograniczony
      
      // W S1-S4: tylko JEDEN ciąg jest aktywny (w zależności od układu)
      JEŻELI aktualny_scenariusz ∈ {S1, S2, S3, S4} WTEDY
        JEŻELI aktualny_układ = "Podstawowy" ORAZ ciąg = CIĄG2 WTEDY
          POMIŃ ciąg  // C2 wyłączony w układzie podstawowym
        KONIEC JEŻELI
        
        JEŻELI aktualny_układ = "Ograniczony" ORAZ ciąg = CIĄG1 WTEDY
          POMIŃ ciąg  // C1 wyłączony w układzie ograniczonym
        KONIEC JEŻELI
      KONIEC JEŻELI
      
      // W S5-S8: oba ciągi aktywne, ale C1 nie może rotować (brak rezerwowej)
      JEŻELI aktualny_scenariusz ∈ {S5, S6, S7, S8} ORAZ ciąg = CIĄG1 WTEDY
        POMIŃ ciąg  // C1 niemożliwa - wszystkie nagrzewnice N1-N4 pracują
      KONIEC JEŻELI
    
    KROK 1: Aktualizuj liczniki czasu pracy i postoju
      // Oblicz rzeczywisty czas który upłynął od ostatniej aktualizacji
      // (uwzględnia przyspieszenie czasu w symulacji i ewentualne opóźnienia w PLC)
      delta_time = czas_systemowy - last_update_time
      
      JEŻELI delta_time > 0 WTEDY
        DLA KAŻDEJ nagrzewnicy w ciągu:
          JEŻELI nagrzewnica_aktywna(N) WTEDY
            czas_pracy[N] += delta_time
          W PRZECIWNYM RAZIE:
            czas_postoju[N] += delta_time
          KONIEC JEŻELI
        KONIEC DLA
        
        last_update_time = czas_systemowy
      KONIEC JEŻELI
    
    KROK 2: Sprawdź warunki rotacji
      
      // Koordynacja z Algorytmem RC - sprawdź czy RC nie wykonuje zmiany układu
      JEŻELI zmiana_układu_w_toku = PRAWDA WTEDY
        POMIŃ ciąg  // odrocz rotację - trwa zmiana układu
      KONIEC JEŻELI
      
      // Sprawdź czy upłynęła 1h od ostatniej zmiany układu (RC)
      // (dotyczy tylko S1-S4, bo tylko tam działa Algorytm RC)
      JEŻELI aktualny_scenariusz ∈ {S1, S2, S3, S4} WTEDY
        czas_od_zmiany_układu = czas_systemowy - czas_ostatniej_zmiany_układu
        JEŻELI czas_od_zmiany_układu < 3600 WTEDY  // 1 godzina
          POMIŃ ciąg  // za wcześnie po zmianie układu
        KONIEC JEŻELI
      KONIEC JEŻELI
      
      // Sprawdź odstęp 15 min od ostatniej rotacji (w dowolnym ciągu)
      czas_od_ostatniej_rotacji_globalnej = czas_systemowy - czas_ostatniej_rotacji_globalny
      JEŻELI czas_od_ostatniej_rotacji_globalnej < 900 WTEDY  // 15 minut
        POMIŃ ciąg  // za krótki odstęp od ostatniej rotacji
      KONIEC JEŻELI
      
      aktualny_scenariusz = Pobierz_Scenariusz()
      ilość_pracujących = Liczba_Aktywnych_Nagrzewnic(ciąg)
      ilość_sprawnych = Liczba_Sprawnych_Nagrzewnic(ciąg)
      
      JEŻELI ilość_sprawnych ≤ ilość_pracujących WTEDY
        // Brak nagrzewnic rezerwowych - rotacja niemożliwa
        POMIŃ ciąg
      KONIEC JEŻELI
      
      czas_od_ostatniej_rotacji = czas_systemowy - czas_ostatniej_rotacji[ciąg]
      okres = OKRES_ROTACJI_NAGRZEWNIC[aktualny_scenariusz]
      
      JEŻELI czas_od_ostatniej_rotacji < okres WTEDY
        // Nie upłynął jeszcze okres rotacji
        POMIŃ ciąg
      KONIEC JEŻELI
      
      JEŻELI NIE Warunki_Stabilności_Spełnione(ciąg) WTEDY
        // System niestabilny - nie wykonuj rotacji
        POMIŃ ciąg
      KONIEC JEŻELI
    
    KROK 3: Wybierz nagrzewnicę do wyłączenia i załączenia
      // Znajdź nagrzewnicę najdłużej pracującą (aktywną)
      nagrzewnica_do_wyłączenia = NULL
      max_czas_pracy = 0
      earliest_timestamp = nieskonczonosc
      
      DLA KAŻDEJ N w nagrzewnice_aktywne[ciąg]:
        JEŻELI czas_pracy[N] > max_czas_pracy WTEDY
          max_czas_pracy = czas_pracy[N]
          nagrzewnica_do_wyłączenia = N
          earliest_timestamp = timestamp_zalaczenia[N]
        W PRZECIWNYM RAZIE JEŻELI czas_pracy[N] = max_czas_pracy WTEDY
          // Przy identycznych czasach pracy wybierz tę załączoną wcześniej
          JEŻELI timestamp_zalaczenia[N] < earliest_timestamp WTEDY
            nagrzewnica_do_wyłączenia = N
            earliest_timestamp = timestamp_zalaczenia[N]
          KONIEC JEŻELI
        KONIEC JEŻELI
      KONIEC DLA
      
      // Znajdź nagrzewnicę najdłużej postoju (nieaktywną, sprawną)
      nagrzewnica_do_załączenia = NULL
      max_czas_postoju = 0
      
      DLA KAŻDEJ N w [nagrzewnice ciągu]:
        JEŻELI N NIE w nagrzewnice_aktywne[ciąg] ORAZ
               N_sprawna(N) ORAZ
               czas_postoju[N] > max_czas_postoju WTEDY
          max_czas_postoju = czas_postoju[N]
          nagrzewnica_do_załączenia = N
        KONIEC JEŻELI
      KONIEC DLA
      
      // Sprawdź czy warto wykonać rotację
      delta_czasu = max_czas_pracy - max_czas_postoju
      JEŻELI delta_czasu < MIN_DELTA_CZASU WTEDY
        // Różnica czasu zbyt mała - nie ma sensu rotować
        POMIŃ ciąg
      KONIEC JEŻELI
    
    KROK 4: Wykonaj rotację
      JEŻELI nagrzewnica_do_wyłączenia ≠ NULL ORAZ 
             nagrzewnica_do_załączenia ≠ NULL WTEDY
        
        // Ustaw blokadę dla Algorytmu RC
        rotacja_nagrzewnic_w_toku = PRAWDA
        
        Rejestruj_Zdarzenie("Rotacja w " + ciąg + ": " + 
                          nagrzewnica_do_wyłączenia + " → " + 
                          nagrzewnica_do_załączenia)
        
        // Sekwencja rotacji
        Wykonaj_Rotację_Nagrzewnicy(ciąg, 
                                    nagrzewnica_do_wyłączenia,
                                    nagrzewnica_do_załączenia)
        
        // Aktualizacja stanu
        czas_ostatniej_rotacji[ciąg] = czas_systemowy
        czas_ostatniej_rotacji_globalny = czas_systemowy  // dla odstępu 15 min
        
        Rejestruj_Zdarzenie("Rotacja zakończona pomyślnie")
        
        // Zwolnij blokadę
        rotacja_nagrzewnic_w_toku = FAŁSZ
      
      KONIEC JEŻELI
  
  KONIEC DLA

KONIEC PĘTLI

FUNKCJA Wykonaj_Rotację_Nagrzewnicy(ciąg, N_stara, N_nowa):
  
  // ⚠️ WAŻNA ZASADA BEZPIECZEŃSTWA:
  // Najpierw ZAŁĄCZAMY nową nagrzewnicę, potem WYŁĄCZAMY starą
  // Oznacza to chwilowo WIĘCEJ nagrzewnic niż wymaga scenariusz (np. 4 zamiast 3)
  // 
  // UZASADNIENIE:
  // ✓ Bezpieczeństwo termiczne - nigdy nie tracimy mocy grzewczej
  // ✓ Weryfikacja - sprawdzamy czy N_nowa działa PRZED wyłączeniem N_starej
  // ✓ Możliwość wycofania - jeśli N_nowa nie działa, N_stara nadal pracuje
  
  KROK 1: Przygotowanie nagrzewnicy nowej
    // Sprawdź gotowość N_nowa
    JEŻELI NIE Sprawdź_Gotowość(N_nowa) WTEDY
      Rejestruj_Alarm("Nagrzewnica " + N_nowa + " nie jest gotowa")
      ZWRÓĆ BŁĄD
    KONIEC JEŻELI
    
    // Ustaw zawór N_nowa na pozycję startową (20%)
    Ustaw_Zawór(N_nowa, 20%)
    Czekaj(5 sekund)
  
  KROK 2: Załączenie nagrzewnicy nowej
    // ⚠️ W tym momencie pracuje: N_stara + N_nowa = WIĘCEJ niż wymaga scenariusz
    // Przykład dla S3: pracują 4 nagrzewnice zamiast 3
    // To jest ZAMIERZONE dla bezpieczeństwa!
    
    // Otwórz przepustnicę dolotową N_nowa
    Ustaw_Przepustnicę_Dolot(N_nowa, OTWARTA)
    Czekaj(5 sekund)
    
    // Otwórz zawór N_nowa stopniowo do 100%
    Dla pozycja = 20 DO 100 KROK 10:
      Ustaw_Zawór(N_nowa, pozycja)
      Czekaj(2 sekundy)
    KONIEC DLA
    
    // Aktywuj regulator PID dla N_nowa
    Ustaw_Regulator_PID(N_nowa, tryb = AUTO, setpoint = 50°C)
    Czekaj(CZAS_STABILIZACJI sekund)
  
  KROK 3: Sprawdź stabilność temperatury
    temp_N_nowa = Odczytaj_Temperaturę(N_nowa)
    
    JEŻELI |temp_N_nowa - 50°C| > 5°C WTEDY
      // Nowa nagrzewnica nie osiągnęła temperatury
      Rejestruj_Alarm("N_nowa nie osiągnęła temp. docelowej")
      // Wycofaj zmianę - N_stara nadal pracuje, więc system bezpieczny
      Wyłącz_Nagrzewnicę(N_nowa)
      ZWRÓĆ BŁĄD
    KONIEC JEŻELI
  
  KROK 4: Wyłączenie nagrzewnicy starej
    // Dopiero teraz, gdy mamy pewność że N_nowa działa, wyłączamy N_starą
    // Po tym kroku: poprawna ilość nagrzewnic zgodna ze scenariuszem
    
    // Przełącz regulator PID dla N_stara w tryb MANUAL
    Ustaw_Regulator_PID(N_stara, tryb = MANUAL)
    
    // Zamknij zawór N_stara stopniowo do 20%
    aktualna_pozycja = Odczytaj_Pozycję_Zaworu(N_stara)
    Dla pozycja = aktualna_pozycja DO 20 KROK -10:
      Ustaw_Zawór(N_stara, pozycja)
      Czekaj(2 sekundy)
    KONIEC DLA
    
    // Poczekaj na stabilizację
    Czekaj(CZAS_STABILIZACJI sekund)
    
    // Zamknij przepustnicę dolotową N_stara
    Ustaw_Przepustnicę_Dolot(N_stara, ZAMKNIĘTA)
  
  KROK 5: Aktualizacja listy aktywnych nagrzewnic
    Usuń(nagrzewnice_aktywne[ciąg], N_stara)
    Dodaj(nagrzewnice_aktywne[ciąg], N_nowa)
    
    // Zeruj licznik postoju dla N_nowa
    czas_postoju[N_nowa] = 0
    
    // Zapisz timestamp załączenia N_nowa (do rozstrzygania przy identycznych czasach)
    timestamp_zalaczenia[N_nowa] = czas_systemowy
    
    // Kontynuuj liczenie czasu pracy dla N_stara
    // (nie zeruj - chcemy pamiętać łączny czas)
  
  ZWRÓĆ SUKCES

KONIEC FUNKCJI

FUNKCJA Warunki_Stabilności_Spełnione(ciąg):
  // Sprawdź temperaturę w szybie
  temp_szyb = Odczytaj_Temperaturę_Szybu()
  JEŻELI |temp_szyb - 2°C| > 0.5°C WTEDY
    ZWRÓĆ FAŁSZ
  KONIEC JEŻELI
  
  // Sprawdź parametry wody grzewczej
  JEŻELI NIE Parametry_Wody_OK() WTEDY
    ZWRÓĆ FAŁSZ
  KONIEC JEŻELI
  
  // Sprawdź wentylator
  JEŻELI NIE Wentylator_Sprawny(ciąg) WTEDY
    ZWRÓĆ FAŁSZ
  KONIEC JEŻELI
  
  // Sprawdź alarmy
  JEŻELI Aktywne_Alarmy_Krytyczne(ciąg) > 0 WTEDY
    ZWRÓĆ FAŁSZ
  KONIEC JEŻELI
  
  ZWRÓĆ PRAWDA

KONIEC FUNKCJI

//=============================================================================
// FUNKCJE SERWISOWE - Wywoływane przez Algorytmy WS i RC
//=============================================================================

FUNKCJA Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy(ciąg, ilość):
  // Ta funkcja jest wywoływana przez Algorytm WS i RC
  // aby uzyskać listę nagrzewnic do załączenia
  //
  // LOGIKA:
  // - Wybiera nagrzewnice na podstawie czasu postoju (najdłużej nieużywane mają priorytet)
  // - Śledzi historię pracy i postoju
  // - Zapewnia równomierne zużycie
  
  nagrzewnice_ciągu = Pobierz_Wszystkie_Nagrzewnice(ciąg)
  sprawne = Filtruj_Sprawne(nagrzewnice_ciągu)
  
  // Sortuj według czasu postoju (malejąco) i czasu pracy (rosnąco)
  // Priorytet: najdłużej w postoju, potem najmniej przepracowane
  posortowane = Sortuj(sprawne, 
                       klucz1=czas_postoju DESC, 
                       klucz2=czas_pracy ASC,
                       klucz3=timestamp_zalaczenia ASC)
  
  wybrane = posortowane[0:ilość]
  
  ZWRÓĆ wybrane

KONIEC FUNKCJI

FUNKCJA Algorytm_RN_Wybierz_Nagrzewnicę(ciąg, ilość_docelowa):
  // Ta funkcja jest wywoływana przez sekwencje zmian scenariuszy
  // aby wybrać JEDNĄ nagrzewnicę do załączenia
  //
  // PARAMETR ilość_docelowa: łączna ilość nagrzewnic która ma pracować po załączeniu
  //
  // LOGIKA: Wybiera nagrzewnicę z najdłuższym czasem postoju
  
  wszystkie = Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy(ciąg, ilość_docelowa)
  aktywne = Pobierz_Aktywne_Nagrzewnice(ciąg)
  
  // Znajdź nagrzewnicę która jest w 'wszystkie' ale NIE jest w 'aktywne'
  DLA KAŻDEJ N w wszystkie:
    JEŻELI N NIE w aktywne WTEDY
      ZWRÓĆ N  // To jest nowa nagrzewnica do załączenia
    KONIEC JEŻELI
  KONIEC DLA
  
  // Nie powinno się zdarzyć (oznacza błąd logiczny)
  Rejestruj_Alarm("BŁĄD: Algorytm_RN_Wybierz_Nagrzewnicę nie znalazł kandydata")
  ZWRÓĆ NULL

KONIEC FUNKCJI
```

---

**Koniec dokumentu pseudokodu**

**Historia zmian:**
- **v1.1** (2 Grudnia 2025): Dodano inicjalizację liczników czasu i obliczanie delta_time dla RC i RN (wynik testów w symulacji)
- **v1.0** (24 Listopad 2025): Wersja początkowa

**Ostatnia aktualizacja:** 25 Listopad 2025  
**Wersja:** 1.1

