(* ============================================================================
   BOGDANKA Szyb 2 - System Sterowania Nagrzewnicami
   Plik: PLC_Typy_Danych.st
   Opis: Definicje typów danych, struktur i enumeracji
   Standard: IEC 61131-3 Structured Text
   ============================================================================ *)

(* Typ wyliczeniowy: Scenariusze pracy *)
TYPE E_Scenariusz :
(
    S0 := 0,  // Brak ogrzewania
    S1 := 1,  // 1 nagrzewnica
    S2 := 2,  // 2 nagrzewnice
    S3 := 3,  // 3 nagrzewnice
    S4 := 4,  // 4 nagrzewnice
    S5 := 5,  // 5 nagrzewnic
    S6 := 6,  // 6 nagrzewnic
    S7 := 7,  // 7 nagrzewnic
    S8 := 8   // 8 nagrzewnic
);
END_TYPE

(* Typ wyliczeniowy: Układ pracy ciągów *)
TYPE E_Uklad :
(
    UKLAD_BRAK := 0,         // System wyłączony
    UKLAD_PODSTAWOWY := 1,   // C1 aktywny
    UKLAD_OGRANICZONY := 2   // C2 przez spinę
);
END_TYPE

(* Typ wyliczeniowy: Tryb pracy regulatora *)
TYPE E_TrybPracy :
(
    TRYB_MANUAL := 0,  // Sterowanie ręczne
    TRYB_AUTO := 1,    // Regulacja automatyczna PID
    TRYB_OFF := 2      // Wyłączony
);
END_TYPE

(* Typ wyliczeniowy: Stan nagrzewnicy *)
TYPE E_StanNagrzewnicy :
(
    STAN_OFF := 0,       // Wyłączona (zawór 20%)
    STAN_STARTING := 1,  // Uruchamianie
    STAN_RUNNING := 2,   // Praca normalna
    STAN_STOPPING := 3,  // Zatrzymywanie
    STAN_ERROR := 4      // Awaria
);
END_TYPE

(* Struktura: Dane nagrzewnicy *)
TYPE ST_Nagrzewnica :
STRUCT
    nNumer : USINT;                      // Numer nagrzewnicy (1-8)
    eStanNagrzewnicy : E_StanNagrzewnicy; // Aktualny stan
    fTemperaturaWylot : REAL;            // Temperatura na wylocie [°C]
    fPozycjaZaworu : REAL;               // Pozycja zaworu [%] (20-100)
    bPrzepustnicaDolotOtwarta : BOOL;    // Stan przepustnicy dolotowej
    bSprawna : BOOL;                     // Nagrzewnica sprawna
    bGotowoscOperacyjna : BOOL;          // Gotowość do pracy
    tCzasPracy : TIME;                   // Łączny czas pracy
    tCzasPostoju : TIME;                 // Łączny czas postoju
    dtTimestampZalaczenia : DT;          // Timestamp ostatniego załączenia
    dwLiczbaZalaczen : UDINT;            // Licznik załączeń
END_STRUCT
END_TYPE

(* Struktura: Dane wentylatora *)
TYPE ST_Wentylator :
STRUCT
    nNumer : USINT;                // Numer wentylatora (1-2)
    eTrybPracy : E_TrybPracy;      // Tryb: AUTO/MANUAL/OFF
    fCzestotliwosc : REAL;         // Częstotliwość [Hz] (25-50)
    fPradSilnika : REAL;           // Prąd silnika [A]
    bSprawny : BOOL;               // Wentylator sprawny
    bPracuje : BOOL;               // Wentylator w ruchu
    tCzasPracy : TIME;             // Łączny czas pracy
END_STRUCT
END_TYPE

(* Struktura: Parametry systemowe *)
TYPE ST_ParametrySystemowe :
STRUCT
    // Temperatury zadane
    fTzZadana : REAL := 50.0;         // Temperatura na wylocie nagrzewnicy [°C]
    fTsZadana : REAL := 2.0;          // Temperatura w szybie [°C]
    
    // Limity zaworu
    fPzMin : REAL := 20.0;            // Min. otwarcie zaworu [%]
    fPzMax : REAL := 100.0;           // Max. otwarcie zaworu [%]
    
    // Limity wentylatora
    fNWMin : REAL := 25.0;            // Min. częstotliwość [Hz]
    fNWMax : REAL := 50.0;            // Max. częstotliwość [Hz]
    
    // Parametry Algorytmu 5
    tCyklMonitoringuTemp : TIME := T#10s;       // Cykl odczytu temperatury
    tCzasUtrzymaniaPrzyAwarii : TIME := T#5m;   // Czas przy awarii czujnika
    nFiltrUsredniania : USINT := 3;             // Liczba próbek filtru
    tCzasStabilizacjiScenariusza : TIME := T#1m; // Min. czas w scenariuszu
    tCzasMiedzyZalaczeniami : TIME := T#30s;    // Odstęp między załączeniami
    tTimeoutZmianyScenariusza : TIME := T#10m;  // Timeout zmiany
    
    // Parametry Algorytmu 5A
    tOkresRotacjiUkladow : TIME := T#168h;      // Okres rotacji układów (7 dni)
    tHisterezaCzasowa : TIME := T#5m;           // Histereza czasowa
    tCyklPetliAlgorytmow : TIME := T#1m;        // Cykl pętli algorytmów
    
    // Parametry Algorytmu 5B
    tOkresRotacjiNagrzewnic : TIME := T#168h;   // Okres rotacji nagrzewnic
    tMinDeltaCzasu : TIME := T#1h;              // Min. różnica czasu dla rotacji
    tCzasStabilizacjiRotacji : TIME := T#30s;   // Czas stabilizacji po rotacji
END_STRUCT
END_TYPE

(* Struktura: Zmienne stanu systemu *)
TYPE ST_StanSystemu :
STRUCT
    // Temperatury
    fTZewn : REAL;                        // Temperatura zewnętrzna [°C]
    fTSzyb : REAL;                        // Temperatura w szybie [°C]
    bAlarmCzujnikTZewn : BOOL;            // Alarm awarii czujnika
    
    // Scenariusz
    eScenariuszAktualny : E_Scenariusz;   // Aktualny scenariusz
    eScenariuszWymagany : E_Scenariusz;   // Wymagany scenariusz
    dtTimestampOstatniejZmiany : DT;      // Timestamp ostatniej zmiany
    
    // Układ pracy
    eUkladAktualny : E_Uklad;             // Aktualny układ pracy
    tCzasPracyUkladuPodstawowego : TIME;  // Czas pracy układu podstawowego
    tCzasPracyUkladuOgraniczonego : TIME; // Czas pracy układu ograniczonego
    
    // Tryb pracy
    eTrybPracySystemu : E_TrybPracy;      // AUTO/MANUAL
    
    // Blokady koordynacji
    bZmianaUkladuWToku : BOOL;            // Blokada dla 5B
    bRotacjaNagrzewnicWToku : BOOL;       // Blokada dla 5A
    dtCzasOstatniejZmianyUkladu : DT;     // Dla koordynacji 5B
    dtCzasOstatniejRotacjiGlobalny : DT;  // Dla odstępu 15 min
END_STRUCT
END_TYPE

(* Struktura: Bufor pomiarów temperatury (filtr) *)
TYPE ST_BuforTemperatury :
STRUCT
    arWartosci : ARRAY[1..10] OF REAL;   // Bufor max 10 próbek
    nIndeks : USINT;                     // Aktualny indeks
    nLiczbaProbek : USINT;               // Liczba próbek w buforze
END_STRUCT
END_TYPE

(* Struktura: Statystyki rotacji *)
TYPE ST_StatystykiRotacji :
STRUCT
    dwLiczbaZmianUkladow : UDINT;        // Licznik rotacji układów
    dwLiczbaRotacjiNagrzewnic : UDINT;   // Licznik rotacji nagrzewnic
    tSredniCzasZmianyUkladu : TIME;      // Średni czas zmiany układu
    tSredniCzasRotacjiNagrzewnicy : TIME; // Średni czas rotacji
    fStosunEksploatacjiC1C2 : REAL;      // C1/C2 (cel: 1.0)
END_STRUCT
END_TYPE

