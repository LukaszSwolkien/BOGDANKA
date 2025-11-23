(* ============================================================================
   BOGDANKA Szyb 2 - Algorytm 5: Automatyczny Wybór Scenariusza Pracy
   Plik: PLC_Algorytm_5_Wybor_Scenariusza.st
   Opis: Główny algorytm wyboru scenariusza na podstawie temperatury zewnętrznej
   Standard: IEC 61131-3 Structured Text
   ============================================================================ *)

PROGRAM PRG_Algorytm5_WyborScenariusza
VAR
    // Dane wejściowe
    Parametry : ST_ParametrySystemowe;
    StanSystemu : ST_StanSystemu;
    arrNagrzewnice : ARRAY[1..8] OF ST_Nagrzewnica;
    arrWentylatory : ARRAY[1..2] OF ST_Wentylator;
    
    // Zmienne lokalne
    BuforTZewn : ST_BuforTemperatury;
    fTZewnUsr : REAL;                        // Temperatura uśredniona
    fOstatniPoprawnyOdczyt : REAL := 20.0;  // Ostatni poprawny odczyt
    dtTimestampOstatniegoOdczytu : DT;
    
    // Timery
    tonCyklMonitoringu : TON;
    tonCzasStabilizacji : TON;
    
    // Zmienne pomocnicze
    bRotacjaMozliwa : BOOL;
    bRotacjaWymagana : BOOL;
    eScenariuszWymagany : E_Scenariusz;
    nWynik : INT;
END_VAR

(* ============================================================================
   GŁÓWNA PĘTLA - wykonywana cyklicznie
   ============================================================================ *)

// Timer cyklu monitoringu
tonCyklMonitoringu(IN := NOT tonCyklMonitoringu.Q, PT := Parametry.tCyklMonitoringuTemp);

IF tonCyklMonitoringu.Q THEN
    tonCyklMonitoringu(IN := FALSE);  // Reset timera
    
    // ========================================================================
    // KROK 1: Odczyt i walidacja temperatury zewnętrznej
    // ========================================================================
    
    IF (StanSystemu.fTZewn >= -40.0) AND (StanSystemu.fTZewn <= 50.0) THEN
        // Odczyt prawidłowy
        StanSystemu.bAlarmCzujnikTZewn := FALSE;
        fOstatniPoprawnyOdczyt := StanSystemu.fTZewn;
        dtTimestampOstatniegoOdczytu := DT_NOW();
        
        // Dodaj do bufora i oblicz średnią (filtr antyfluktuacyjny)
        BuforTZewn := FB_DodajDoBufora(BuforTZewn, StanSystemu.fTZewn, Parametry.nFiltrUsredniania);
        fTZewnUsr := FB_ObliczSrednia(BuforTZewn);
    ELSE
        // Awaria czujnika
        StanSystemu.bAlarmCzujnikTZewn := TRUE;
        
        IF (DT_NOW() - dtTimestampOstatniegoOdczytu) < Parametry.tCzasUtrzymaniaPrzyAwarii THEN
            // Utrzymaj ostatni scenariusz
            fTZewnUsr := fOstatniPoprawnyOdczyt;
        ELSE
            // Za długo bez odczytu - przełącz na tryb MANUAL
            StanSystemu.eTrybPracySystemu := TRYB_MANUAL;
            RETURN;  // Wyjdź z algorytmu
        END_IF;
    END_IF;
    
    // ========================================================================
    // KROK 2: Określ wymagany scenariusz na podstawie temperatury
    // ========================================================================
    
    eScenariuszWymagany := FB_OkreslScenariusz(fTZewnUsr, StanSystemu.eScenariuszAktualny);
    
    // ========================================================================
    // KROK 3: Sprawdź czy wymagana zmiana scenariusza
    // ========================================================================
    
    IF eScenariuszWymagany = StanSystemu.eScenariuszAktualny THEN
        RETURN;  // Brak zmiany - kontynuuj w aktualnym scenariuszu
    END_IF;
    
    // Sprawdź czas stabilizacji
    tonCzasStabilizacji(IN := TRUE, PT := Parametry.tCzasStabilizacjiScenariusza);
    
    IF NOT tonCzasStabilizacji.Q THEN
        RETURN;  // Za krótki czas od ostatniej zmiany
    END_IF;
    
    tonCzasStabilizacji(IN := FALSE);  // Reset timera
    
    // ========================================================================
    // KROK 4: Sprawdź tryb pracy
    // ========================================================================
    
    IF StanSystemu.eTrybPracySystemu <> TRYB_AUTO THEN
        RETURN;  // W trybie MANUAL operator kontroluje system
    END_IF;
    
    // ========================================================================
    // KROK 5: Wykonaj zmianę scenariusza
    // ========================================================================
    
    nWynik := FB_WykonajZmianeScenariusza(
        eScenariuszStary := StanSystemu.eScenariuszAktualny,
        eScenariuszNowy := eScenariuszWymagany,
        arrNagrzewnice := arrNagrzewnice,
        arrWentylatory := arrWentylatory,
        StanSystemu := StanSystemu,
        Parametry := Parametry
    );
    
    IF nWynik = 0 THEN
        // Sukces
        StanSystemu.eScenariuszAktualny := eScenariuszWymagany;
        StanSystemu.dtTimestampOstatniejZmiany := DT_NOW();
    ELSE
        // Błąd - pozostań w aktualnym scenariuszu
        // Alarm został już wygenerowany w funkcji
    END_IF;
END_IF;

END_PROGRAM


(* ============================================================================
   FUNKCJA: Określenie wymaganego scenariusza z histerezą
   ============================================================================ *)

FUNCTION FB_OkreslScenariusz : E_Scenariusz
VAR_INPUT
    fTZewn : REAL;                    // Temperatura zewnętrzna
    eAktualnyScenariusz : E_Scenariusz; // Aktualny scenariusz (dla histerezy)
END_VAR

    // Progi włączania (temperatura spada - dodajemy nagrzewnice)
    
    IF fTZewn >= 3.0 THEN
        FB_OkreslScenariusz := S0;
        RETURN;
    END_IF;
    
    // S1: -1°C < t ≤ 2°C (wyłączenie: t ≥ 3°C, histereza 1°C)
    IF fTZewn > 2.0 OR (fTZewn > -1.0 AND eAktualnyScenariusz = S0) THEN
        IF eAktualnyScenariusz = S0 THEN
            FB_OkreslScenariusz := S0;  // Zostań w S0
        ELSE
            FB_OkreslScenariusz := S1;  // Utrzymuj S1
        END_IF;
        RETURN;
    END_IF;
    
    IF fTZewn > -1.0 THEN
        FB_OkreslScenariusz := S1;
        RETURN;
    END_IF;
    
    // Histereza S1→S0
    IF fTZewn >= 0.0 AND eAktualnyScenariusz = S1 THEN
        FB_OkreslScenariusz := S0;
        RETURN;
    END_IF;
    
    // S2: -4°C < t ≤ -1°C (wyłączenie: t ≥ 0°C)
    IF fTZewn > -4.0 THEN
        FB_OkreslScenariusz := S2;
        RETURN;
    END_IF;
    
    IF fTZewn >= 0.0 AND eAktualnyScenariusz = S2 THEN
        FB_OkreslScenariusz := S1;
        RETURN;
    END_IF;
    
    // S3: -8°C < t ≤ -4°C (wyłączenie: t ≥ -3°C)
    IF fTZewn > -8.0 THEN
        FB_OkreslScenariusz := S3;
        RETURN;
    END_IF;
    
    IF fTZewn >= -3.0 AND eAktualnyScenariusz = S3 THEN
        FB_OkreslScenariusz := S2;
        RETURN;
    END_IF;
    
    // S4: -11°C < t ≤ -8°C (wyłączenie: t ≥ -6°C, histereza 2°C)
    IF fTZewn > -11.0 THEN
        FB_OkreslScenariusz := S4;
        RETURN;
    END_IF;
    
    IF fTZewn >= -6.0 AND eAktualnyScenariusz = S4 THEN
        FB_OkreslScenariusz := S3;
        RETURN;
    END_IF;
    
    // S5: -15°C < t ≤ -11°C (wyłączenie: t ≥ -10°C)
    IF fTZewn > -15.0 THEN
        FB_OkreslScenariusz := S5;
        RETURN;
    END_IF;
    
    IF fTZewn >= -10.0 AND eAktualnyScenariusz = S5 THEN
        FB_OkreslScenariusz := S4;
        RETURN;
    END_IF;
    
    // S6: -18°C < t ≤ -15°C (wyłączenie: t ≥ -13°C, histereza 2°C)
    IF fTZewn > -18.0 THEN
        FB_OkreslScenariusz := S6;
        RETURN;
    END_IF;
    
    IF fTZewn >= -13.0 AND eAktualnyScenariusz = S6 THEN
        FB_OkreslScenariusz := S5;
        RETURN;
    END_IF;
    
    // S7: -21°C < t ≤ -18°C (wyłączenie: t ≥ -15°C, histereza 3°C)
    IF fTZewn > -21.0 THEN
        FB_OkreslScenariusz := S7;
        RETURN;
    END_IF;
    
    IF fTZewn >= -15.0 AND eAktualnyScenariusz = S7 THEN
        FB_OkreslScenariusz := S6;
        RETURN;
    END_IF;
    
    // S8: t ≤ -21°C (wyłączenie: t ≥ -20°C)
    IF fTZewn <= -21.0 THEN
        FB_OkreslScenariusz := S8;
        RETURN;
    END_IF;
    
    IF fTZewn >= -20.0 AND eAktualnyScenariusz = S8 THEN
        FB_OkreslScenariusz := S7;
        RETURN;
    END_IF;
    
    // Domyślnie zwróć aktualny scenariusz
    FB_OkreslScenariusz := eAktualnyScenariusz;

END_FUNCTION


(* ============================================================================
   FUNKCJA: Wykonanie zmiany scenariusza
   Zwraca: 0 = sukces, -1 = błąd
   ============================================================================ *)

FUNCTION FB_WykonajZmianeScenariusza : INT
VAR_INPUT
    eScenariuszStary : E_Scenariusz;
    eScenariuszNowy : E_Scenariusz;
    arrNagrzewnice : ARRAY[1..8] OF ST_Nagrzewnica;
    arrWentylatory : ARRAY[1..2] OF ST_Wentylator;
    StanSystemu : ST_StanSystemu;
    Parametry : ST_ParametrySystemowe;
END_VAR
VAR
    dtStartZmiany : DT;
    nIloscStara : USINT;
    nIloscNowa : USINT;
    i : USINT;
    nWynik : INT;
END_VAR

    dtStartZmiany := DT_NOW();
    
    // Pobierz ilości nagrzewnic dla scenariuszy
    nIloscStara := FB_IloscNagrzewnicDlaScenariusza(eScenariuszStary);
    nIloscNowa := FB_IloscNagrzewnicDlaScenariusza(eScenariuszNowy);
    
    // ========================================================================
    // KROK 1: Zatrzymaj zbędne nagrzewnice (jeśli przechodzimy na niższy)
    // ========================================================================
    
    IF nIloscNowa < nIloscStara THEN
        FOR i := 1 TO (nIloscStara - nIloscNowa) DO
            // Pobierz nagrzewnicę do wyłączenia (najwyższy numer aktywny)
            nWynik := FB_WylaczNagrzewnice(arrNagrzewnice, 1);
            
            IF nWynik <> 0 THEN
                // Alarm już wygenerowany, ale kontynuuj
            END_IF;
            
            // Odstęp między wyłączeniami
            FB_Czekaj(Parametry.tCzasMiedzyZalaczeniami);
        END_FOR;
    END_IF;
    
    // ========================================================================
    // KROK 2: Skonfiguruj wentylatory
    // ========================================================================
    
    nWynik := FB_KonfigurujWentylatory(eScenariuszNowy, arrWentylatory, StanSystemu);
    
    IF nWynik <> 0 THEN
        FB_WykonajZmianeScenariusza := -1;
        RETURN;
    END_IF;
    
    FB_Czekaj(T#10s);  // Stabilizacja wentylatorów
    
    // ========================================================================
    // KROK 3: Skonfiguruj przepustnice
    // ========================================================================
    
    nWynik := FB_KonfigurujPrzepustnice(eScenariuszNowy, StanSystemu);
    
    IF nWynik <> 0 THEN
        FB_WykonajZmianeScenariusza := -1;
        RETURN;
    END_IF;
    
    FB_Czekaj(T#5s);
    
    // ========================================================================
    // KROK 4: Uruchom dodatkowe nagrzewnice (jeśli przechodzimy na wyższy)
    // ========================================================================
    
    IF nIloscNowa > nIloscStara THEN
        FOR i := 1 TO (nIloscNowa - nIloscStara) DO
            nWynik := FB_ZalaczNagrzewnice(arrNagrzewnice, eScenariuszNowy, StanSystemu);
            
            IF nWynik <> 0 THEN
                // Alarm, ale system może działać z mniejszą ilością
            END_IF;
            
            FB_Czekaj(Parametry.tCzasMiedzyZalaczeniami);
        END_FOR;
    END_IF;
    
    // ========================================================================
    // KROK 5: Weryfikacja
    // ========================================================================
    
    FB_Czekaj(T#30s);  // Czas na stabilizację
    
    IF FB_WeryfikujScenariusz(eScenariuszNowy, arrNagrzewnice, arrWentylatory) THEN
        FB_WykonajZmianeScenariusza := 0;  // Sukces
    ELSE
        FB_WykonajZmianeScenariusza := -1;  // Błąd weryfikacji
    END_IF;

END_FUNCTION

