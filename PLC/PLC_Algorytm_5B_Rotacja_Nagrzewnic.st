(* ============================================================================
   BOGDANKA Szyb 2 - Algorytm 5B: Rotacja Nagrzewnic w Obrębie Ciągu
   Plik: PLC_Algorytm_5B_Rotacja_Nagrzewnic.st
   Opis: Cykliczna rotacja nagrzewnic - najdłużej pracująca → najdłużej w postoju
   Standard: IEC 61131-3 Structured Text
   ============================================================================ *)

PROGRAM PRG_Algorytm5B_RotacjaNagrzewnic
VAR
    // Dane wejściowe
    Parametry : ST_ParametrySystemowe;
    StanSystemu : ST_StanSystemu;
    arrNagrzewnice : ARRAY[1..8] OF ST_Nagrzewnica;
    arrWentylatory : ARRAY[1..2] OF ST_Wentylator;
    
    // Zmienne lokalne
    arrCzasOstatniejRotacji : ARRAY[1..2] OF DT;  // Dla każdego ciągu
    
    // Timer
    tonCyklPetliAlgorytmu : TON;
    
    // Zmienne pomocnicze
    nCiag : USINT;
    tCzasOdOstatniejRotacji : TIME;
    tCzasOdZmianyUkladu : TIME;
    tCzasOdOstatniejRotacjiGlobalnej : TIME;
    nIloscPracujacych : USINT;
    nIloscSprawnych : USINT;
    nNagrzewnicaDoWylaczenia : USINT;
    nNagrzewnicaDoZalaczenia : USINT;
    tMaxCzasPracy : TIME;
    tMaxCzasPostoju : TIME;
    tDeltaCzasu : TIME;
    nWynik : INT;
END_VAR

(* ============================================================================
   GŁÓWNA PĘTLA - wykonywana cyklicznie
   ============================================================================ *)

// Timer cyklu algorytmu
tonCyklPetliAlgorytmu(IN := NOT tonCyklPetliAlgorytmu.Q, PT := Parametry.tCyklPetliAlgorytmow);

IF tonCyklPetliAlgorytmu.Q THEN
    tonCyklPetliAlgorytmu(IN := FALSE);  // Reset timera
    
    // Przetwarzaj oba ciągi
    FOR nCiag := 1 TO 2 DO
        
        // ====================================================================
        // KROK 0: Sprawdź czy ciąg jest aktywny w aktualnym układzie/scenariuszu
        // ====================================================================
        
        // W S1-S4: tylko JEDEN ciąg aktywny (zależy od układu)
        IF (StanSystemu.eScenariuszAktualny >= S1) AND (StanSystemu.eScenariuszAktualny <= S4) THEN
            IF (StanSystemu.eUkladAktualny = UKLAD_PODSTAWOWY) AND (nCiag = 2) THEN
                CONTINUE;  // C2 wyłączony w układzie podstawowym
            END_IF;
            
            IF (StanSystemu.eUkladAktualny = UKLAD_OGRANICZONY) AND (nCiag = 1) THEN
                CONTINUE;  // C1 wyłączony w układzie ograniczonym
            END_IF;
        END_IF;
        
        // W S5-S8: C1 nie może rotować (brak rezerwowej - wszystkie 4 pracują)
        IF (StanSystemu.eScenariuszAktualny >= S5) AND (nCiag = 1) THEN
            CONTINUE;  // C1 rotacja niemożliwa
        END_IF;
        
        // ====================================================================
        // KROK 1: Aktualizuj liczniki czasu pracy i postoju
        // ====================================================================
        
        FB_AktualizujLicznikiCzasu(arrNagrzewnice, nCiag, Parametry.tCyklPetliAlgorytmow);
        
        // ====================================================================
        // KROK 2: Sprawdź warunki rotacji
        // ====================================================================
        
        // Koordynacja z Algorytmem 5A - sprawdź czy 5A nie wykonuje zmiany układu
        IF StanSystemu.bZmianaUkladuWToku THEN
            CONTINUE;  // Odrocz rotację
        END_IF;
        
        // Sprawdź czy upłynęła 1h od ostatniej zmiany układu (tylko S1-S4)
        IF (StanSystemu.eScenariuszAktualny >= S1) AND (StanSystemu.eScenariuszAktualny <= S4) THEN
            tCzasOdZmianyUkladu := DT_NOW() - StanSystemu.dtCzasOstatniejZmianyUkladu;
            IF tCzasOdZmianyUkladu < T#1h THEN
                CONTINUE;  // Za wcześnie po zmianie układu
            END_IF;
        END_IF;
        
        // Sprawdź odstęp 15 min od ostatniej rotacji (w dowolnym ciągu)
        tCzasOdOstatniejRotacjiGlobalnej := DT_NOW() - StanSystemu.dtCzasOstatniejRotacjiGlobalny;
        IF tCzasOdOstatniejRotacjiGlobalnej < T#15m THEN
            CONTINUE;  // Za krótki odstęp
        END_IF;
        
        // Sprawdź czy są nagrzewnice rezerwowe
        nIloscPracujacych := FB_LiczbaAktywnychNagrzewnic(arrNagrzewnice, nCiag);
        nIloscSprawnych := FB_LiczbaSprawnych(arrNagrzewnice, nCiag);
        
        IF nIloscSprawnych <= nIloscPracujacych THEN
            CONTINUE;  // Brak nagrzewnic rezerwowych
        END_IF;
        
        // Sprawdź czy upłynął okres rotacji
        tCzasOdOstatniejRotacji := DT_NOW() - arrCzasOstatniejRotacji[nCiag];
        
        IF tCzasOdOstatniejRotacji < Parametry.tOkresRotacjiNagrzewnic THEN
            CONTINUE;  // Nie upłynął jeszcze okres
        END_IF;
        
        // Sprawdź warunki stabilności
        IF NOT FB_WarunkiStabilnosciSpelnione(nCiag, arrWentylatory, StanSystemu) THEN
            CONTINUE;  // System niestabilny
        END_IF;
        
        // ====================================================================
        // KROK 3: Wybierz nagrzewnicę do wyłączenia i załączenia
        // ====================================================================
        
        // Znajdź nagrzewnicę najdłużej pracującą (aktywną)
        nNagrzewnicaDoWylaczenia := 0;
        tMaxCzasPracy := T#0s;
        
        nNagrzewnicaDoWylaczenia := FB_ZnajdzNajdluzejPracujaca(arrNagrzewnice, nCiag);
        
        IF nNagrzewnicaDoWylaczenia = 0 THEN
            CONTINUE;  // Nie znaleziono
        END_IF;
        
        tMaxCzasPracy := arrNagrzewnice[nNagrzewnicaDoWylaczenia].tCzasPracy;
        
        // Znajdź nagrzewnicę najdłużej w postoju (nieaktywną, sprawną)
        nNagrzewnicaDoZalaczenia := FB_ZnajdzNajdluzejWPostoju(arrNagrzewnice, nCiag);
        
        IF nNagrzewnicaDoZalaczenia = 0 THEN
            CONTINUE;  // Nie znaleziono
        END_IF;
        
        tMaxCzasPostoju := arrNagrzewnice[nNagrzewnicaDoZalaczenia].tCzasPostoju;
        
        // Sprawdź czy warto wykonać rotację
        tDeltaCzasu := tMaxCzasPracy - tMaxCzasPostoju;
        
        IF tDeltaCzasu < Parametry.tMinDeltaCzasu THEN
            CONTINUE;  // Różnica zbyt mała
        END_IF;
        
        // ====================================================================
        // KROK 4: Wykonaj rotację
        // ====================================================================
        
        // Ustaw blokadę dla Algorytmu 5A
        StanSystemu.bRotacjaNagrzewnicWToku := TRUE;
        
        nWynik := FB_WykonajRotacjeNagrzewnicy(
            nCiag := nCiag,
            nNStara := nNagrzewnicaDoWylaczenia,
            nNNowa := nNagrzewnicaDoZalaczenia,
            arrNagrzewnice := arrNagrzewnice,
            Parametry := Parametry
        );
        
        IF nWynik = 0 THEN
            // Sukces
            arrCzasOstatniejRotacji[nCiag] := DT_NOW();
            StanSystemu.dtCzasOstatniejRotacjiGlobalny := DT_NOW();
        END_IF;
        
        // Zwolnij blokadę
        StanSystemu.bRotacjaNagrzewnicWToku := FALSE;
        
    END_FOR;  // Koniec pętli ciągów
END_IF;

END_PROGRAM


(* ============================================================================
   FUNKCJA: Wykonanie rotacji nagrzewnicy
   Zwraca: 0 = sukces, -1 = błąd
   
   WAŻNA ZASADA BEZPIECZEŃSTWA:
   Najpierw ZAŁĄCZAMY nową nagrzewnicę, potem WYŁĄCZAMY starą
   ============================================================================ *)

FUNCTION FB_WykonajRotacjeNagrzewnicy : INT
VAR_INPUT
    nCiag : USINT;
    nNStara : USINT;
    nNNowa : USINT;
    arrNagrzewnice : ARRAY[1..8] OF ST_Nagrzewnica;
    Parametry : ST_ParametrySystemowe;
END_VAR
VAR
    fTempNNowa : REAL;
    fPozycjaZaworu : REAL;
    i : USINT;
END_VAR

    // ========================================================================
    // KROK 1: Przygotowanie nagrzewnicy nowej
    // ========================================================================
    
    IF NOT arrNagrzewnice[nNNowa].bGotowoscOperacyjna THEN
        FB_WykonajRotacjeNagrzewnicy := -1;
        RETURN;
    END_IF;
    
    // Ustaw zawór na pozycję startową (20%)
    FB_UstawZawor(arrNagrzewnice[nNNowa], Parametry.fPzMin);
    FB_Czekaj(T#5s);
    
    // ========================================================================
    // KROK 2: Załączenie nagrzewnicy nowej
    // ⚠️ W tym momencie pracuje: N_stara + N_nowa = WIĘCEJ niż wymaga scenariusz
    // To jest ZAMIERZONE dla bezpieczeństwa!
    // ========================================================================
    
    // Otwórz przepustnicę dolotową N_nowa
    FB_UstawPrzepustniceDolot(arrNagrzewnice[nNNowa], TRUE);
    FB_Czekaj(T#5s);
    
    // Otwórz zawór N_nowa stopniowo do 100%
    FOR fPozycjaZaworu := Parametry.fPzMin TO Parametry.fPzMax BY 10.0 DO
        FB_UstawZawor(arrNagrzewnice[nNNowa], fPozycjaZaworu);
        FB_Czekaj(T#2s);
    END_FOR;
    
    // Aktywuj regulator PID dla N_nowa
    FB_UstawRegulatorPID(arrNagrzewnice[nNNowa], TRYB_AUTO, Parametry.fTzZadana);
    FB_Czekaj(Parametry.tCzasStabilizacjiRotacji);
    
    // ========================================================================
    // KROK 3: Sprawdź stabilność temperatury
    // ========================================================================
    
    fTempNNowa := arrNagrzewnice[nNNowa].fTemperaturaWylot;
    
    IF ABS(fTempNNowa - Parametry.fTzZadana) > 5.0 THEN
        // Nowa nagrzewnica nie osiągnęła temperatury
        // Wycofaj zmianę - N_stara nadal pracuje, więc system bezpieczny
        FB_WylaczNagrzewnice(arrNagrzewnice, nCiag);
        FB_WykonajRotacjeNagrzewnicy := -1;
        RETURN;
    END_IF;
    
    // ========================================================================
    // KROK 4: Wyłączenie nagrzewnicy starej
    // ✅ Dopiero teraz, gdy mamy pewność że N_nowa działa, wyłączamy N_starą
    // Po tym kroku: poprawna ilość nagrzewnic zgodna ze scenariuszem
    // ========================================================================
    
    // Przełącz regulator PID dla N_stara w tryb MANUAL
    FB_UstawRegulatorPID(arrNagrzewnice[nNStara], TRYB_MANUAL, 0.0);
    
    // Zamknij zawór N_stara stopniowo do 20%
    fPozycjaZaworu := arrNagrzewnice[nNStara].fPozycjaZaworu;
    
    FOR i := 1 TO 10 DO
        fPozycjaZaworu := fPozycjaZaworu - 10.0;
        IF fPozycjaZaworu < Parametry.fPzMin THEN
            fPozycjaZaworu := Parametry.fPzMin;
        END_IF;
        FB_UstawZawor(arrNagrzewnice[nNStara], fPozycjaZaworu);
        FB_Czekaj(T#2s);
    END_FOR;
    
    // Poczekaj na stabilizację
    FB_Czekaj(Parametry.tCzasStabilizacjiRotacji);
    
    // Zamknij przepustnicę dolotową N_stara
    FB_UstawPrzepustniceDolot(arrNagrzewnice[nNStara], FALSE);
    
    // ========================================================================
    // KROK 5: Aktualizacja stanów
    // ========================================================================
    
    arrNagrzewnice[nNNowa].eStanNagrzewnicy := STAN_RUNNING;
    arrNagrzewnice[nNNowa].tCzasPostoju := T#0s;  // Zeruj licznik postoju
    arrNagrzewnice[nNNowa].dtTimestampZalaczenia := DT_NOW();
    
    arrNagrzewnice[nNStara].eStanNagrzewnicy := STAN_OFF;
    // Nie zeruj czasu pracy N_starej - pamiętamy łączny czas
    
    FB_WykonajRotacjeNagrzewnicy := 0;  // Sukces

END_FUNCTION

