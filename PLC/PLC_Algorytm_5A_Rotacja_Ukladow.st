(* ============================================================================
   BOGDANKA Szyb 2 - Algorytm 5A: Rotacja Układów Pracy Ciągów
   Plik: PLC_Algorytm_5A_Rotacja_Ukladow.st
   Opis: Cykliczna zmiana układów: Podstawowy ↔ Ograniczony
   Standard: IEC 61131-3 Structured Text
   ============================================================================ *)

PROGRAM PRG_Algorytm5A_RotacjaUkladow
VAR
    // Dane wejściowe
    Parametry : ST_ParametrySystemowe;
    StanSystemu : ST_StanSystemu;
    arrNagrzewnice : ARRAY[1..8] OF ST_Nagrzewnica;
    arrWentylatory : ARRAY[1..2] OF ST_Wentylator;
    
    // Zmienne lokalne
    dtCzasOstatniejZmianyUkladu : DT;
    bRotacjaMozliwa : BOOL;
    bRotacjaWymagana : BOOL;
    eNowyUklad : E_Uklad;
    
    // Timer
    tonCyklPetliAlgorytmu : TON;
    
    // Zmienne pomocnicze
    tCzasOdOstatniejZmiany : TIME;
    nWynik : INT;
END_VAR

(* ============================================================================
   GŁÓWNA PĘTLA - wykonywana cyklicznie
   ============================================================================ *)

// Timer cyklu algorytmu
tonCyklPetliAlgorytmu(IN := NOT tonCyklPetliAlgorytmu.Q, PT := Parametry.tCyklPetliAlgorytmow);

IF tonCyklPetliAlgorytmu.Q THEN
    tonCyklPetliAlgorytmu(IN := FALSE);  // Reset timera
    
    // ========================================================================
    // KROK 1: Sprawdź warunki rotacji
    // ========================================================================
    
    bRotacjaMozliwa := FALSE;
    
    // Rotacja tylko w scenariuszach S1-S4
    IF (StanSystemu.eScenariuszAktualny >= S1) AND 
       (StanSystemu.eScenariuszAktualny <= S4) AND
       FB_WszystkieNagrzewniceC2Sprawne(arrNagrzewnice) AND
       arrWentylatory[2].bSprawny AND
       (StanSystemu.eTrybPracySystemu = TRYB_AUTO) THEN
        
        bRotacjaMozliwa := TRUE;
    ELSE
        // Rotacja niemożliwa - powrót do układu podstawowego jeśli był ograniczony
        IF StanSystemu.eUkladAktualny = UKLAD_OGRANICZONY THEN
            FB_WykonajZmianeUkladu(UKLAD_PODSTAWOWY, StanSystemu, arrNagrzewnice, arrWentylatory, Parametry);
        END_IF;
        
        RETURN;
    END_IF;
    
    // ========================================================================
    // KROK 2: Sprawdź czy upłynął okres rotacji
    // ========================================================================
    
    tCzasOdOstatniejZmiany := DT_NOW() - dtCzasOstatniejZmianyUkladu;
    
    IF tCzasOdOstatniejZmiany >= (Parametry.tOkresRotacjiUkladow - Parametry.tHisterezaCzasowa) THEN
        bRotacjaWymagana := TRUE;
    ELSE
        bRotacjaWymagana := FALSE;
        RETURN;
    END_IF;
    
    // ========================================================================
    // KROK 3: Określ nowy układ
    // ========================================================================
    
    IF StanSystemu.eUkladAktualny = UKLAD_PODSTAWOWY THEN
        eNowyUklad := UKLAD_OGRANICZONY;
    ELSE
        eNowyUklad := UKLAD_PODSTAWOWY;
    END_IF;
    
    // ========================================================================
    // KROK 4: Wykonaj zmianę układu
    // ========================================================================
    
    IF bRotacjaMozliwa AND bRotacjaWymagana THEN
        
        // Sprawdź czy Algorytm 5B nie wykonuje rotacji nagrzewnic
        IF StanSystemu.bRotacjaNagrzewnicWToku THEN
            // Zmiana odroczona
            RETURN;
        END_IF;
        
        // Ustaw blokadę dla Algorytmu 5B
        StanSystemu.bZmianaUkladuWToku := TRUE;
        
        // Wykonaj sekwencję zmiany układu
        nWynik := FB_WykonajZmianeUkladu(
            eDocelowyUklad := eNowyUklad,
            StanSystemu := StanSystemu,
            arrNagrzewnice := arrNagrzewnice,
            arrWentylatory := arrWentylatory,
            Parametry := Parametry
        );
        
        IF nWynik = 0 THEN
            // Sukces
            StanSystemu.eUkladAktualny := eNowyUklad;
            dtCzasOstatniejZmianyUkladu := DT_NOW();
            StanSystemu.dtCzasOstatniejZmianyUkladu := DT_NOW();  // Dla koordynacji z 5B
        END_IF;
        
        // Zwolnij blokadę
        StanSystemu.bZmianaUkladuWToku := FALSE;
    END_IF;
    
    // ========================================================================
    // KROK 5: Aktualizuj liczniki czasu pracy
    // ========================================================================
    
    IF StanSystemu.eUkladAktualny = UKLAD_PODSTAWOWY THEN
        StanSystemu.tCzasPracyUkladuPodstawowego := StanSystemu.tCzasPracyUkladuPodstawowego + Parametry.tCyklPetliAlgorytmow;
    ELSIF StanSystemu.eUkladAktualny = UKLAD_OGRANICZONY THEN
        StanSystemu.tCzasPracyUkladuOgraniczonego := StanSystemu.tCzasPracyUkladuOgraniczonego + Parametry.tCyklPetliAlgorytmow;
    END_IF;
END_IF;

END_PROGRAM


(* ============================================================================
   FUNKCJA: Wykonanie zmiany układu
   Zwraca: 0 = sukces, -1 = błąd
   ============================================================================ *)

FUNCTION FB_WykonajZmianeUkladu : INT
VAR_INPUT
    eDocelowyUklad : E_Uklad;
    StanSystemu : ST_StanSystemu;
    arrNagrzewnice : ARRAY[1..8] OF ST_Nagrzewnica;
    arrWentylatory : ARRAY[1..2] OF ST_Wentylator;
    Parametry : ST_ParametrySystemowe;
END_VAR
VAR
    i : USINT;
    nIloscAktywnych : USINT;
    nWymaganaIlosc : USINT;
END_VAR

    nWymaganaIlosc := FB_IloscNagrzewnicDlaScenariusza(StanSystemu.eScenariuszAktualny);
    
    IF eDocelowyUklad = UKLAD_OGRANICZONY THEN
        // ====================================================================
        // Przejście: Podstawowy → Ograniczony
        // ====================================================================
        
        // KROK 1: Zatrzymaj ciąg 1 (stopniowo)
        nIloscAktywnych := FB_LiczbaAktywnychNagrzewnicC1(arrNagrzewnice);
        
        FOR i := nIloscAktywnych TO 1 BY -1 DO
            FB_WylaczNagrzewnice(arrNagrzewnice, 1);  // Wyłącz z C1
            FB_Czekaj(T#30s);
        END_FOR;
        
        FB_ZatrzymajWentylator(arrWentylatory[1]);
        
        // KROK 2: Otwórz przepustnicę na spince ciągów
        FB_UstawPrzepustnice(PRZEPUSTNICA_SPINKA, TRUE);
        FB_Czekaj(T#10s);
        
        // KROK 3: Zamknij przepustnice ciągu 1
        FB_UstawPrzepustnice(PRZEPUSTNICA_KOLEKTOR_C1, FALSE);
        FB_UstawPrzepustnice(PRZEPUSTNICA_WYRZUTNIA_430, FALSE);
        
        // KROK 4: Uruchom ciąg 2 (stopniowo)
        FB_UruchomWentylator(arrWentylatory[2], 25.0);
        FB_Czekaj(T#10s);
        
        FOR i := 1 TO nWymaganaIlosc DO
            FB_ZalaczNagrzewnice(arrNagrzewnice, StanSystemu.eScenariuszAktualny, StanSystemu);
            FB_Czekaj(T#30s);
        END_FOR;
        
        // KROK 5: Aktywuj regulację PID dla W2
        FB_UstawWentylatorTryb(arrWentylatory[2], TRYB_AUTO);
        
    ELSE
        // ====================================================================
        // Przejście: Ograniczony → Podstawowy
        // ====================================================================
        
        // KROK 1: Zatrzymaj ciąg 2 (stopniowo)
        nIloscAktywnych := FB_LiczbaAktywnychNagrzewnicC2(arrNagrzewnice);
        
        FOR i := nIloscAktywnych TO 1 BY -1 DO
            FB_WylaczNagrzewnice(arrNagrzewnice, 2);  // Wyłącz z C2
            FB_Czekaj(T#30s);
        END_FOR;
        
        FB_ZatrzymajWentylator(arrWentylatory[2]);
        
        // KROK 2: Zamknij przepustnicę na spince ciągów
        FB_UstawPrzepustnice(PRZEPUSTNICA_SPINKA, FALSE);
        FB_Czekaj(T#10s);
        
        // KROK 3: Otwórz przepustnice ciągu 1
        FB_UstawPrzepustnice(PRZEPUSTNICA_KOLEKTOR_C1, TRUE);
        FB_UstawPrzepustnice(PRZEPUSTNICA_CIAG_C1, TRUE);
        FB_UstawPrzepustnice(PRZEPUSTNICA_WYRZUTNIA_430, TRUE);
        
        // KROK 4: Uruchom ciąg 1 (stopniowo)
        FB_UruchomWentylator(arrWentylatory[1], 25.0);
        FB_Czekaj(T#10s);
        
        FOR i := 1 TO nWymaganaIlosc DO
            FB_ZalaczNagrzewnice(arrNagrzewnice, StanSystemu.eScenariuszAktualny, StanSystemu);
            FB_Czekaj(T#30s);
        END_FOR;
        
        // KROK 5: Aktywuj regulację PID dla W1
        FB_UstawWentylatorTryb(arrWentylatory[1], TRYB_AUTO);
    END_IF;
    
    FB_WykonajZmianeUkladu := 0;  // Sukces

END_FUNCTION

