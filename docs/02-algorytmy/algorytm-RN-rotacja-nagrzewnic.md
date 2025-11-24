# Algorytm RN: Cykliczna Rotacja Nagrzewnic w Obrębie Ciągu

> **Część dokumentacji:** Algorytmy Sterowania  
> **Powiązane algorytmy:** [Algorytm WS](./algorytm-WS-wybor-scenariusza.md), [Algorytm RC](./algorytm-RC-rotacja-ciagow.md)  
> **Wizualizacja:** [Flowchart](./schematy/algorytm-RN-rotacja-nagrzewnic-flowchart.svg), [Koordynacja z 5A](./schematy/koordynacja-RC-RN-timeline.svg), [Przykłady rotacji](./schematy/)

## 1. Cel Algorytmu

Algorytm realizuje **cykliczną rotację nagrzewnic pracujących w jednym ciągu wentylacyjnym** w celu:
- Wyrównania czasów eksploatacji poszczególnych nagrzewnic w ciągu
- Zmniejszenia zużycia pojedynczej nagrzewnicy
- Zwiększenia niezawodności systemu przez równomierne zużycie urządzeń

## 2. Problem do Rozwiązania

**Bez rotacji nagrzewnic (przykład dla S3 - 3 nagrzewnice):**
- N1 pracuje ZAWSZE (najdłuższy czas pracy)
- N2 pracuje często (średni czas pracy)
- N3 pracuje rzadziej (krótszy czas pracy)
- N4 NIE pracuje (brak zużycia)
- **Rezultat:** Nierównomierne zużycie nagrzewnic → N1 będzie wymagać konserwacji znacznie wcześniej niż N4

**Z rotacją nagrzewnic:**
```
Dzień 1-7:   N1, N2, N3 pracują
Dzień 8-14:  N2, N3, N4 pracują  (N1 odpoczynek, N4 wchodzi)
Dzień 15-21: N3, N4, N1 pracują  (N2 odpoczynek, N1 wchodzi)
Dzień 22-28: N4, N1, N2 pracują  (N3 odpoczynek, N2 wchodzi)
```
- **Rezultat:** Równomierne zużycie wszystkich 4 nagrzewnic ciągu

## 3. Parametry Konfiguracyjne

Parametry definiowane przez **technologa podczas rozruchu**:

| Parametr | Wartość domyślna | Jednostka | Zakres | Opis |
|----------|-----------------|-----------|--------|------|
| **OKRES_ROTACJI_NAGRZEWNIC** | Do ustalenia* | godziny | 24h - 720h | Czas po którym następuje zmiana nagrzewnicy w ciągu |
| **MIN_DELTA_CZASU** | 3600 | sekundy | 1800 - 7200 | Minimalna różnica czasu pracy dla wykonania rotacji |
| **CYKL_PĘTLI_ALGORYTMÓW** | 60 | sekundy | 10 - 600 | Częstość wykonywania pętli głównej (współdzielony z 5A) |

*Wartości zostaną ustalone podczas testowania pracy układu na obiekcie (zgodnie z sekcją 1.4 projektu).

**Przykładowe wartości OKRES_ROTACJI_NAGRZEWNIC:**
- **168h (7 dni)** - typowa wartość dla równomiernego rozłożenia eksploatacji
- **720h (30 dni)** - dla zmniejszenia częstotliwości przełączeń
- **48h (2 dni)** - dla intensywnej rotacji i szybszego wyrównania

**Uzasadnienie MIN_DELTA_CZASU:**
- **3600s (1h)** - wartość domyślna, zapobiega częstym rotacjom przy niewielkich różnicach
- **7200s (2h)** - dla bardziej konserwatywnego podejścia
- **1800s (30min)** - dla agresywniejszego wyrównywania w scenariuszach dynamicznych
- Jeśli różnica czasu pracy jest mniejsza niż MIN_DELTA_CZASU, rotacja nie ma sensu (zmiana dla zmiany)

**Uzasadnienie CYKL_PĘTLI_ALGORYTMÓW:**
- Parametr **współdzielony** z Algorytmem 5A (wspólna wartość dla obu algorytmów)
- Szczegółowe wyjaśnienie i przykładowe wartości: patrz sekcja 5A.3
- Liczniki `czas_pracy[N]` i `czas_postoju[N]` aktualizują się co CYKL_PĘTLI_ALGORYTMÓW sekund

## 4. Warunki Aktywacji Rotacji Nagrzewnic

Rotacja nagrzewnic jest możliwa **TYLKO** gdy spełnione są **WSZYSTKIE** warunki:

1. **Warunek konfiguracji ciągu:**
   - Ilość sprawnych nagrzewnic ciągu > ilość aktualnie pracujących nagrzewnic
   - Co najmniej 1 nagrzewnica musi pozostać aktywna podczas zmiany
   - Maksymalnie 4 nagrzewnice w ciągu

2. **Warunek czasowy:**
   - Upłynął OKRES_ROTACJI_NAGRZEWNIC od ostatniej rotacji w tym ciągu
   - System pracuje w trybie AUTO

3. **Warunek stabilności:**
   - Brak aktywnych alarmów dla nagrzewnic w ciągu
   - Parametry wody grzewczej w normie
   - Temperatura w szybie stabilna (brak oscylacji > ±0.5°C)
   - Wentylator ciągu sprawny i pracujący

4. **Warunek dostępności:**
   - Nagrzewnica zastępcza w gotowości operacyjnej
   - Zawór regulacyjny sprawny
   - Przepustnice sprawne

## 5. Algorytm Rotacji Nagrzewnic Krok po Kroku

**WAŻNE - Algorytm RN jako serwis dla innych algorytmów:**

Algorytm RN pełni **podwójną funkcję**:

1. **Funkcja aktywna** - Wykonuje cykliczną rotację nagrzewnic (wymiana najdłużej pracującej → najdłużej w postoju)
2. **Funkcja serwisowa** - Dostarcza funkcje wyboru nagrzewnic wywoływane przez:
   - **Algorytm WS** (wybór scenariusza) - wywołuje `Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy(ciąg, ilość)`
   - **Algorytm RC** (rotacja układów) - wywołuje `Algorytm_RN_Pobierz_Nagrzewnice_Do_Pracy(ciąg, ilość)`
   - **Sekwencje zmian scenariuszy** - wywołują `Algorytm_RN_Wybierz_Nagrzewnicę(ciąg, ilość)`

**Zasada:** NIGDY nie zakładamy sekwencyjnego wyboru nagrzewnic (N1→N2→N3...). Zawsze delegujemy wybór do Algorytmu RC, który:
- Śledzi czasy pracy i postoju każdej nagrzewnicy
- Wybiera nagrzewnice na podstawie historii eksploatacji
- Zapewnia równomierne zużycie wszystkich nagrzewnic N1-N8

**Diagram wizualizujący algorytm:**

![Algorytm RN Flowchart](./schematy/algorytm-RN-rotacja-nagrzewnic-flowchart.svg)

```
ZMIENNE GLOBALNE (współdzielone z Algorytmem 5A):
  - aktualny_układ                                       // Podstawowy lub Ograniczony
  - zmiana_układu_w_toku                                 // blokada od 5A
  - czas_ostatniej_zmiany_układu                         // timestamp od 5A
  - rotacja_nagrzewnic_w_toku = FAŁSZ                    // blokada dla 5A
  - czas_ostatniej_rotacji_globalny = 0                  // dla odstępu 15 min [sekundy]

ZMIENNE LOKALNE (dla każdego ciągu osobno):
  - czas_pracy[N1..N8] = [0, 0, 0, 0, 0, 0, 0, 0]       // [sekundy]
  - czas_postoju[N1..N8] = [0, 0, 0, 0, 0, 0, 0, 0]     // [sekundy]
  - timestamp_zalaczenia[N1..N8] = [0, 0, 0, 0, 0, 0, 0, 0] // [timestamp pierwszego załączenia]
  - czas_ostatniej_rotacji[CIĄG1, CIĄG2] = [0, 0]       // [timestamp]
  - nagrzewnice_aktywne[CIĄG] = []                       // lista aktywnych

PARAMETRY:
  - OKRES_ROTACJI_NAGRZEWNIC[S1..S8]  // definiowany przez technologa [s]
  - MIN_DELTA_CZASU                   // definiowany przez technologa [s] (domyślnie 3600)
  - CZAS_STABILIZACJI = 30            // czas na stabilizację po zmianie [s]
  - CYKL_PĘTLI_ALGORYTMÓW = 60        // częstość sprawdzania [s] (współdzielony z 5A)

GŁÓWNA PĘTLA (co CYKL_PĘTLI_ALGORYTMÓW):
  
  DLA KAŻDEGO ciągu w [CIĄG1, CIĄG2]:
    
    KROK 0: Sprawdź czy ciąg jest aktywny w aktualnym układzie/scenariuszu
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
      DLA KAŻDEJ nagrzewnicy w ciągu:
        JEŻELI nagrzewnica_aktywna(N) WTEDY
          czas_pracy[N] += CYKL_PĘTLI_ALGORYTMÓW
        W PRZECIWNYM RAZIE:
          czas_postoju[N] += CYKL_PĘTLI_ALGORYTMÓW
        KONIEC JEŻELI
      KONIEC DLA
    
    KROK 2: Sprawdź warunki rotacji
      
      // Koordynacja z Algorytmem 5A - sprawdź czy 5A nie wykonuje zmiany układu
      JEŻELI zmiana_układu_w_toku = PRAWDA WTEDY
        POMIŃ ciąg  // odrocz rotację - trwa zmiana układu
      KONIEC JEŻELI
      
      // Sprawdź czy upłynęła 1h od ostatniej zmiany układu (5A)
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
  // Ta funkcja jest wywoływana przez Algorytm WS i 5A
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

## 6. Priorytety Rotacji

**Aktywność ciągów w zależności od scenariusza:**

| Scenariusz | Aktywne ciągi | Układ | Uwaga |
|------------|---------------|-------|-------|
| **S1-S4** | **TYLKO JEDEN ciąg** na raz | Układ Podstawowy: **C1** (W1 PID)<br>Układ Ograniczony: **C2** (W2 PID) | Algorytm RC przełącza między układami → rotacja RN dotyczy ciągu który **aktualnie pracuje** |
| **S5-S8** | **OBA ciągi** jednocześnie | C1 MAX + C2 PID/MAX | Oba ciągi aktywne, ale tylko C2 może rotować (C1 niemożliwa - brak rezerwowej) |

Gdy wiele ciągów wymaga rotacji jednocześnie, stosuje się następujące priorytety:

| Priorytet | Ciąg | Warunek | Uzasadnienie |
|-----------|------|---------|--------------|
| 1 | **Ciąg aktywny w S1-S4** | **C1 (Układ Podstawowy)** ALBO **C2 (Układ Ograniczony)** - pracuje SOLO | Najwyższe zużycie - całe obciążenie grzewcze na jednym ciągu, priorytetowa rotacja |
| 2 | Ciąg 2 (S5-S7) | C1 MAX + C2 PID | C2 reguluje temperaturę PID - rotacja **MOŻLIWA** i ważna dla stabilności (są nagrzewnice rezerwowe) |
| 3 | Ciąg 1 (S5-S8) | C1 MAX + C2 PID/MAX | C1 pracuje na MAX - rotacja **NIEMOŻLIWA*** (wszystkie N1-N4 pracują, brak rezerwowej) |

**Ograniczenia rotacji:**
- *W **S5-S8**: rotacja RN w **C1 jest NIEMOŻLIWA** - wszystkie nagrzewnice N1-N4 muszą pracować (brak nagrzewnicy rezerwowej)
- W **S5-S7**: rotacja RN w **C2 jest MOŻLIWA** - są nagrzewnice rezerwowe (N8 w S7, N7-N8 w S6, N6-N8 w S5)
- W **S8**: rotacja RN w **C2 jest NIEMOŻLIWA** - wszystkie nagrzewnice N5-N8 muszą pracować (brak nagrzewnicy rezerwowej)

**Koordynacja z Algorytmem 5A (Rotacja Układów):**

⚠️ **WAŻNE - W S1-S4 pracuje TYLKO JEDEN ciąg na raz (nie oba jednocześnie!):**
- Gdy aktywny jest **Układ Podstawowy**: pracuje **TYLKO C1**, rotacja RN dotyczy **C1** (priorytet 1)
- Gdy aktywny jest **Układ Ograniczony**: pracuje **TYLKO C2**, rotacja RN dotyczy **C2** (priorytet 1)
- Algorytm RC przełącza między układami → zmiana który ciąg pracuje

**Zasady koordynacji:**
- Po zmianie układu (5A) poczekaj min. **1 godzinę** przed rotacją nagrzewnic (5B)
- Priorytet ma zawsze **ciąg aktualnie pracujący** (w S1-S4 to jeden ciąg, w S5-S8 to oba ciągi, ale C2 ma priorytet rotacji bo C1 nie może rotować)

**Zasada odstępu:** Nie wykonuj rotacji w dwóch ciągach jednocześnie - zachowaj min. 15 minut odstępu między rotacjami.

**Uzasadnienie odstępu 15 minut:**
- Stabilność systemu (uniknięcie podwójnych perturbacji temperatury)
- Łatwiejsza diagnostyka problemów (wiadomo który ciąg jest przyczyną)
- Czas na reakcję operatora/SCADA w przypadku nieprawidłowości

## 7. Obsługa Stanów Awaryjnych

| Stan Awaryjny | Reakcja Systemu |
|---------------|-----------------|
| Nagrzewnica nowa nie osiąga temperatury | Wycofaj zmianę, przywróć N_starą, alarm |
| Awaria zaworu podczas rotacji | Zatrzymaj rotację, utrzymaj aktualny stan, alarm krytyczny |
| Wentylator zatrzymał się podczas rotacji | Natychmiastowe wyłączenie obu nagrzewnic, alarm krytyczny |
| Temperatura szybu spadła o >1°C | Przerwij rotację, przywróć N_starą, zwiększ moc |
| Przekroczenie czasu rotacji (>5 min) | Przerwij rotację, alarm, przejście na tryb MANUAL |

## 8. Monitoring i Statystyki

System rejestruje następujące dane dla każdej nagrzewnicy:

| Parametr | Opis |
|----------|------|
| Łączny czas pracy [h] | Suma czasu aktywnej pracy nagrzewnicy |
| Łączny czas postoju [h] | Suma czasu kiedy nagrzewnica była wyłączona |
| Liczba załączeń | Licznik startów nagrzewnicy |
| Ostatnie załączenie | Timestamp ostatniego startu |
| Liczba rotacji | Ile razy nagrzewnica była wymieniana przez rotację |
| Średnia temperatura [°C] | Średnia temp. na wylocie podczas pracy |

**Raport dostępny w HMI:**
- Wykres słupkowy czasu pracy dla N1-N8
- Stosunek czasu pracy nagrzewnic w ciągu (cel: wyrównany)
- Historia rotacji z timestampami
- Predykcja następnej rotacji

## 9. Przykłady Działania

#### **Przykład 1: Scenariusz S3 (3 nagrzewnice)**

**Warunki początkowe:**
- Temperatura: -6°C → Scenariusz S3
- Ciąg 1: 4 nagrzewnice sprawne
- Aktualnie pracują: N1, N2, N3
- OKRES_ROTACJI_NAGRZEWNIC = 168h (7 dni)
- Moment: System po pierwszym tygodniu pracy, przed pierwszą rotacją
- Czasy pracy: N1=168h, N2=168h, N3=168h, N4=0h

**Przebieg rotacji:**

1. **Dzień 0** - System w konfiguracji początkowej
   ```
   Czasy: N1=168h, N2=168h, N3=168h, N4=0h
   Pracują: [N1, N2, N3]  ← 3 nagrzewnice
   Postój:  [N4]
   ```

2. **Dzień 7** - Pierwsza rotacja (upłynęło 168h)
   ```
   Analiza:
   - Najdłużej pracująca: N1, N2, N3 (wszystkie 336h) - wybór N1 (najwcześniejszy timestamp załączenia)
   - Najdłużej postój: N4 (168h postoju)
   - Delta: 336h - 0h = 336h > MIN_DELTA_CZASU ✅
   
   Akcja: Wymiana N1 → N4
   
   Sekwencja czasowa:
   t=0s:   Pracują: [N1, N2, N3]           ← 3 nagrzewnice
   t=5s:   Załączanie N4...
   t=35s:  Pracują: [N1, N2, N3, N4]       ← ⚠️ 4 nagrzewnice (WIĘCEJ!)
           PID wentylatora kompensuje (zmniejsza prędkość)
   t=65s:  N4 zweryfikowana (50°C) 
   t=65s:  Rozpoczęcie wyłączania N1...
   t=95s:  Pracują: [N2, N3, N4]           ← 3 nagrzewnice
   
   Po rotacji:
   Czasy: N1=336h, N2=336h, N3=336h, N4=0h
   Pracują: [N2, N3, N4]
   Postój:  [N1]
   ```

**⚠️ Kluczowa obserwacja:**
- Przez ~30 sekund (t=35s do t=65s) pracują 4 nagrzewnice zamiast 3
- To jest **zamierzone** dla bezpieczeństwa
- PID wentylatora automatycznie redukuje prędkość 
- Gdyby N4 nie zadziałała, N1 nadal pracuje - system bezpieczny

3. **Dzień 14** - Druga rotacja
   ```
   Czasy pracy: N1=336h (postój 168h), N2=504h, N3=504h, N4=168h
   
   Analiza:
   - Najdłużej pracująca: N2, N3 (obie 504h) - wybór N2 (wcześniejszy timestamp załączenia niż N3)
   - Najdłużej postój: N1 (168h postoju)
   
   Akcja: Wyłącz N2, załącz N1
   
   Po rotacji:
   Czasy: N1=336h, N2=504h, N3=504h, N4=168h
   Pracują: [N3, N4, N1]
   Postój:  [N2]
   ```

4. **Dzień 21** - Trzecia rotacja
   ```
   Czasy pracy: N1=504h, N2=504h (postój 168h), N3=672h, N4=336h
   
   Analiza:
   - Najdłużej pracująca: N3 (672h)
   - Najdłużej postój: N2 (168h postoju)
   
   Akcja: Wyłącz N3, załącz N2
   
   Po rotacji:
   Czasy: N1=504h, N2=504h, N3=672h, N4=336h
   Pracują: [N4, N1, N2]
   Postój:  [N3]
   ```

5. **Dzień 28** - Czwarta rotacja
   ```
   Czasy pracy: N1=672h, N2=672h, N3=672h (postój 168h), N4=504h
   
   Analiza:
   - Najdłużej pracująca: N1, N2 (obie 672h) - wybór wg timestamp (ta załączona wcześniej)
   - Najdłużej postój: N3 (168h postoju)
   
   Akcja: Wyłącz N1, załącz N3
   
   Po rotacji:
   Czasy: N1=672h, N2=672h, N3=672h, N4=504h
   Pracują: [N4, N2, N3]
   Postój:  [N1]
   ```

**Rezultat po 4 tygodniach:**
- N1: 672h pracy ≈ 26.7% (ideał: 25%) → odchylenie +1.7%
- N2: 672h pracy ≈ 26.7% (ideał: 25%) → odchylenie +1.7%
- N3: 672h pracy ≈ 26.7% (ideał: 25%) → odchylenie +1.7%
- N4: 504h pracy ≈ 20.0% (ideał: 25%) → odchylenie -5.0%
- **Suma:** 2520h
- **Różnica max-min:** 672h - 504h = 168h (1 okres rotacji)
- **Wyrównanie:** ~93% ✅ (max odchylenie od średniej 630h to tylko 6.7%)

**Po 3 miesiącach** (12 tygodni = 2016h):
- Wszystkie nagrzewnice: ~1512h ± 50h
- **Różnica max-min:** ~84h (0.5 okresu rotacji)
- **Wyrównanie:** > 95% ✅

#### **Przykład 2: Dynamiczna zmiana scenariuszy**

**Sytuacja:** Temperatura oscyluje między S2 a S3

```
Dzień 1-3: S3 (N1, N2, N3) - 72h
Dzień 4-5: S2 (N1, N2) - 48h     → N3 idzie w postój
Dzień 6-7: S3 (N1, N2, N3) - 48h → N3 wraca do pracy
```

**Algorytm dostosowuje się:**
- Licznik czasu pracy N3: 72h + 48h = 120h (postój nie jest liczony podwójnie)
- Licznik postoju N3: 48h
- N4 cały czas w postoju: 168h
- Po tygodniu: rotacja N1 → N4 (N1 ma najwięcej godzin)

## 10. Integracja z Rotacją Układów (Sekcja 5A)

**Koordynacja dwóch algorytmów rotacji:**

1. **Rotacja układów** (5A) - zmienia CIĄG (C1 ↔ C2)
   - Okres: tygodnie/miesiące
   - Dotyczy wyboru: C1 vs C2

2. **Rotacja nagrzewnic** (5B) - zmienia NAGRZEWNICĘ w ciągu
   - Okres: dni/tygodnie
   - Dotyczy wyboru: N1/N2/N3/N4 w C1 lub N5/N6/N7/N8 w C2

**Zasady koordynacji:**
- Nie wykonuj rotacji nagrzewnic w ciągu, który jest w trakcie zmiany układu
- Po zmianie układu (5A) poczekaj min. 1h przed rotacją nagrzewnic (5B)
- Jeśli zbiegły się oba okresy rotacji → najpierw rotacja układów (5A), potem nagrzewnic (5B) z odstępem min. 1h

**⚠️ WAŻNE - Przesunięcie faz rotacji:**

Jeśli oba algorytmy (5A i 5B) mają ten sam okres (np. 168h), NIE MOGĄ wykonać rotacji w tym samym momencie. System musi zapewnić przesunięcie faz aby uniknąć:
- Podwójnej perturbacji systemu (zmiana układu + zmiana nagrzewnicy)
- Trudności w diagnostyce (niejednoznaczność przyczyny zmian temperatury)

**Rozwiązania:**
1. **Różne okresy rotacji** - np. 5A: 10 dni, 5B: 7 dni
2. **Przesunięcie fazy startowej** - np. 5A start w dniu 0, 5B start w dniu 3
3. **Logika zapobiegania kolizji** - jeśli obie rotacje przypadają tego samego dnia, wykonaj tylko 5A, a 5B przełóż o 1 dzień

**Przykład (zakłada przesunięcie faz):**
```
Dzień 0:  Układ Podstawowy, C1: N1, N2, N3
Dzień 7:  Rotacja nagrzewnic (5B) → C1: N2, N3, N4
Dzień 14: Rotacja układów (5A) → Układ Ograniczony, C2: N5, N6, N7
Dzień 21: Rotacja nagrzewnic (5B) → C2: N6, N7, N8
Dzień 28: Rotacja układów (5A) → Układ Podstawowy, C1: N2, N3, N4
```
*Uwaga: W tym przykładzie okresy są różne lub fazy przesunięte, więc rotacje nie kolidują.*

**Efekt końcowy:**
- Równomierne zużycie wszystkich 8 nagrzewnic
- Równomierne zużycie obu ciągów (W1, W2)
- Maksymalna niezawodność systemu

UWAGA: Powyzsze wyliczenia trzeba potwierdzic w symulacji z roznymi scenariuszami i okresami rotacji

## 5B.11 Wizualizacja Koordynacji Algorytmów RC i RN

**Diagram Timeline - Przykładowy Scenariusz S3:**

![Koordynacja RC ↔ RN](./schematy/koordynacja-RC-RN-timeline.svg)

Diagram timeline pokazuje praktyczny przykład koordynacji między algorytmami w scenariuszu S3:

**Kluczowe elementy wizualizacji:**
1. **Timeline zdarzeń** (0h → 410h):
   - T=0h: System w układzie Podstawowym, C1 aktywny
   - T=168h: Algorytm RN rotuje nagrzewnice w C1 (N1 → N4)
   - T=168h+2min: Algorytm RC próbuje zmienić układ → **BLOKADA** (5B rotuje)
   - T=168h+5min: 5B kończy, 5A wykonuje zmianę układu
   - T=169h: Układ Ograniczony, C2 aktywny
   - T=169h+15min: 5B próbuje rotować w C2 → **ODROCZONE** (odstęp 1h)
   - T=170h: 5B może rotować w C2 ✅ (upłynęła 1h od zmiany układu)

2. **Blokady (Mutex)**:
   - `zmiana_układu_w_toku`: chroni przed rotacją nagrzewnic podczas zmiany układu
   - `rotacja_nagrzewnic_w_toku`: chroni przed zmianą układu podczas rotacji nagrzewnic

3. **Odstępy czasowe**:
   - **1 godzina**: po zmianie układu (5A) przed rotacją nagrzewnic (5B)
   - **15 minut**: między rotacjami w różnych ciągach

4. **Kolorystyka**:
   - 🟨 Żółty: Algorytm RC (rotacja układów)
   - 🟩 Zielony: Algorytm RN (rotacja nagrzewnic)
   - 🟥 Czerwony: Blokada / Odroczone

**Wnioski z diagramu:**
- System **NIGDY** nie wykonuje dwóch operacji jednocześnie
- Wszystkie blokady są dwukierunkowe (RC ↔ RN)
- Odstępy czasowe zapewniają stabilność temperatury
- Mechanizmy są zaimplementowane w pseudokodzie (KROK 0, KROK 2, KROK 4)

---
