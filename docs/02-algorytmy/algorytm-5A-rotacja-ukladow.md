# Algorytm 5A: Cykliczna Rotacja Układów Pracy Ciągów

> **Część dokumentacji:** Algorytmy Sterowania  
> **Powiązane algorytmy:** [Algorytm 5](./algorytm-5-wybor-scenariusza.md), [Algorytm 5B](./algorytm-5B-rotacja-nagrzewnic.md)  
> **Wizualizacja:** [Flowchart](../../visualization/algorytmy/algorytm-5A-rotacja-ukladow-flowchart.svg), [Diagramy rotacji](../../visualization/rotacje/)

## 1. Cel Algorytmu

Algorytm realizuje **cykliczną zmianę układów pracy ciągów grzewczych** w celu:
- Wyrównania czasów eksploatacji ciągów grzewczych (W1 vs W2)
- Uniknięcia nadmiernej eksploatacji ciągu pierwszego
- Zwiększenia niezawodności i równomiernego zużycia urządzeń

## 2. Problem do Rozwiązania

**Bez rotacji układów:**
- Ciąg 1 (N1-N4 + W1) pracuje zawsze w scenariuszach S1-S4 (temp. od 2°C do -11°C)
- Ciąg 2 (N5-N8 + W2) włącza się dopiero w S5-S8 (temp. < -11°C)
- **Rezultat:** Ciąg 1 jest eksploatowany znacznie częściej i intensywniej niż ciąg 2

**Z rotacją układów:**
- System okresowo zmienia układ: Podstawowy → Ograniczony → Podstawowy
- Oba ciągi mają równomierne czasy pracy

## 3. Parametr Konfiguracyjny

**⚙️ OKRES_ROTACJI_UKŁADÓW** - parametr definiowany przez **technologa podczas rozruchu**

| Parametr | Wartość domyślna | Jednostka | Zakres | Opis |
|----------|-----------------|-----------|--------|------|
| OKRES_ROTACJI_UKŁADÓW | Do ustalenia* | godziny lub dni | 24h - 30 dni | Czas po którym następuje zmiana układu pracy |

*Wartość zostanie ustalona podczas testowania pracy układu na obiekcie i może być modyfikowana w zależności od warunków eksploatacyjnych.

**Przykładowe wartości:**
- **168h (7 dni)** - typowa wartość dla równomiernego rozłożenia eksploatacji
- **720h (30 dni)** - dla zmniejszenia częstotliwości przełączeń
- **24h (1 dzień)** - dla testów i weryfikacji działania

**CYKL_PĘTLI_ALGORYTMÓW** - parametr częstotliwości sprawdzania (wspólny dla 5A i 5B)

| Parametr | Wartość domyślna | Jednostka | Zakres | Opis |
|----------|-----------------|-----------|--------|------|
| CYKL_PĘTLI_ALGORYTMÓW | 60 | sekundy | 10s - 600s | Częstotliwość wykonywania pętli głównej algorytmów |

**Uzasadnienie i przykładowe wartości:**
- **60s (1 minuta)** - zalecane dla krótkich okresów rotacji (24h-168h)
  - Dokładność: ±1 minuta (0.04% błędu dla 168h)
  - Obciążenie: ~10,080 sprawdzeń na 7 dni
  - Liczniki czasu pracy: aktualizacja co 1 minutę
- **300s (5 minut)** - zalecane dla długich okresów rotacji (168h-720h)
  - Dokładność: ±5 minut (0.2% błędu dla 168h)
  - Obciążenie: ~2,016 sprawdzeń na 7 dni (bardzo niskie)
  - Liczniki czasu pracy: aktualizacja co 5 minut
- **600s (10 minut)** - dla bardzo długich okresów (>720h)
  - Dokładność: ±10 minut (0.4% błędu dla 168h)
  - Obciążenie: ~1,008 sprawdzeń na 7 dni (minimalne)

**Wpływ na liczniki:**
- `czas_pracy_układu_podstawowego` i `czas_pracy_układu_ograniczonego` aktualizują się co CYKL_PĘTLI_ALGORYTMÓW
- Dla 60s: dokładność ±1 minuta (akceptowalna dla okresów dni/tygodni)
- Dla 300s: dokładność ±5 minut (nadal akceptowalna)

## 4. Warunki Aktywacji Rotacji

Rotacja układów jest możliwa **TYLKO** gdy spełnione są **WSZYSTKIE** warunki:

1. **Warunek temperaturowy:**
   - Aktualny scenariusz: S1, S2, S3 lub S4
   - Temperatura zewnętrzna: -11°C < t ≤ 2°C
   - Wymagana ilość nagrzewnic ≤ 4

2. **Warunek gotowości ciągu 2:**
   - Ilość sprawnych nagrzewnic ciągu 2 (N5-N8) ≥ wymagana ilość nagrzewnic
   - Wentylator W2 sprawny i w gotowości operacyjnej
   - Przepustnica na spince ciągów sprawna

3. **Warunek czasowy:**
   - Upłynął OKRES_ROTACJI_UKŁADÓW od ostatniej zmiany układu
   - System pracuje w trybie AUTO

4. **Warunek stabilności:**
   - Brak aktywnych alarmów krytycznych
   - Parametry wody grzewczej w normie
   - System SAR stabilny (brak oscylacji temperatury)

## 5. Algorytm Rotacji Krok po Kroku

**Diagram przepływu algorytmu:**

![Algorytm 5A - Diagram przepływu](../../visualization/algorytmy/algorytm-5A-rotacja-ukladow-flowchart.svg)

**Pseudokod:**

```
ZMIENNE GLOBALNE (współdzielone z Algorytmem 5B):
  - aktualny_układ = "Podstawowy"               // aktualny układ pracy
  - zmiana_układu_w_toku = FAŁSZ                // blokada dla koordynacji z 5B
  - czas_ostatniej_zmiany_układu = 0            // timestamp dla 5B [sekundy]
  - rotacja_nagrzewnic_w_toku = FAŁSZ           // blokada dla koordynacji z 5B

ZMIENNE LOKALNE (tylko dla 5A):
  - czas_pracy_układu_podstawowego = 0          // [sekundy]
  - czas_pracy_układu_ograniczonego = 0         // [sekundy]
  - czas_ostatniej_zmiany = czas_systemowy      // timestamp ostatniej rotacji układu
  - scenariusz = S0..S8                         // aktualny scenariusz

PARAMETRY:
  - OKRES_ROTACJI_UKŁADÓW                       // definiowany przez technologa [s]
  - HISTEREZA_CZASOWA = 300                     // 5 minut [s]
  - CYKL_PĘTLI_ALGORYTMÓW = 60                  // częstość sprawdzania [s] (domyślnie 1 min)

GŁÓWNA PĘTLA (co CYKL_PĘTLI_ALGORYTMÓW):
  
  KROK 1: Sprawdź warunki rotacji
    JEŻELI scenariusz ∈ {S1, S2, S3, S4} ORAZ
           wszystkie_nagrzewnice_C2_sprawne ORAZ
           wentylator_W2_sprawny ORAZ
           tryb = AUTO ORAZ
           brak_alarmów_krytycznych WTEDY
      
      rotacja_możliwa = PRAWDA
    
    W PRZECIWNYM RAZIE:
      rotacja_możliwa = FAŁSZ
      // Powrót do układu podstawowego jeśli był ograniczony
      JEŻELI aktualny_układ = "Ograniczony" WTEDY
        Wykonaj_Zmianę_Układu("Podstawowy")
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
      
      // Sprawdź czy Algorytm 5B nie wykonuje rotacji nagrzewnic
      JEŻELI rotacja_nagrzewnic_w_toku = PRAWDA WTEDY
        Rejestruj_Zdarzenie("Zmiana układu odroczona - trwa rotacja nagrzewnic")
        PRZEJDŹ DO KROKU 5
      KONIEC JEŻELI
      
      // Ustaw blokadę dla Algorytmu 5B
      zmiana_układu_w_toku = PRAWDA
      
      Rejestruj_Zdarzenie("Rozpoczęcie zmiany układu z " + aktualny_układ + " na " + nowy_układ)
      
      // Sekwencja zmiany układu
      Wykonaj_Zmianę_Układu(nowy_układ)
      
      // Aktualizacja zmiennych
      aktualny_układ = nowy_układ
      czas_ostatniej_zmiany = czas_systemowy
      czas_ostatniej_zmiany_układu = czas_systemowy  // dla koordynacji z 5B
      
      Rejestruj_Zdarzenie("Zakończono zmianę układu na " + nowy_układ)
      
      // Zwolnij blokadę
      zmiana_układu_w_toku = FAŁSZ
    
    KONIEC JEŻELI
  
  KROK 5: Aktualizuj liczniki czasu pracy
    JEŻELI aktualny_układ = "Podstawowy" WTEDY
      czas_pracy_układu_podstawowego += CYKL_PĘTLI_ALGORYTMÓW
    W PRZECIWNYM RAZIE:
      czas_pracy_układu_ograniczonego += CYKL_PĘTLI_ALGORYTMÓW
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
      
      // Deleguj wybór nagrzewnic do Algorytmu 5B
      nagrzewnice_do_załączenia = Algorytm_5B_Pobierz_Nagrzewnice_Do_Pracy(CIĄG2, wymagana_ilość_nagrzewnic)
      
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
      
      // Deleguj wybór nagrzewnic do Algorytmu 5B
      nagrzewnice_do_załączenia = Algorytm_5B_Pobierz_Nagrzewnice_Do_Pracy(CIĄG1, wymagana_ilość_nagrzewnic)
      
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

## 6. Obsługa Stanów Awaryjnych Podczas Rotacji

| Stan Awaryjny | Reakcja Systemu |
|---------------|-----------------|
| Awaria nagrzewnicy podczas zmiany | Kontynuuj zmianę z pominiętą nagrzewnicą, alarm informacyjny |
| Awaria wentylatora podczas zmiany | Natychmiastowy powrót do poprzedniego układu, alarm krytyczny |
| Przekroczenie czasu zmiany (>10 min) | Przerwij zmianę, powrót do układu podstawowego, alarm |
| Oscylacje temperatury podczas zmiany | Zwiększ czas stabilizacji (60s zamiast 30s), kontynuuj |
| Brak przepływu wody grzewczej | Natychmiastowe zatrzymanie zmiany, wyłączenie wszystkich nagrzewnic, alarm krytyczny |

## 7. Monitoring i Statystyki

System rejestruje następujące dane dla analizy:

| Parametr | Opis |
|----------|------|
| Łączny czas pracy C1 | Suma czasu pracy ciągu 1 w układzie podstawowym [h] |
| Łączny czas pracy C2 | Suma czasu pracy ciągu 2 w układzie ograniczonym [h] |
| Liczba zmian układów | Licznik wykonanych rotacji |
| Średni czas zmiany układu | Średni czas trwania procedury zmiany [min] |
| Liczba nieudanych zmian | Licznik przerwanych rotacji z powodu błędów |
| Stosunek eksploatacji C1/C2 | Proporcja czasu pracy obu ciągów (cel: ~1.0) |

**Raport dostępny w HMI:**
- Wykres czasu pracy ciągów (histogram tygodniowy/miesięczny)
- Historia zmian układów z timestampem
- Analiza równomierności eksploatacji

## 8. Przykład Działania

**Warunki początkowe:**
- Temperatura zewnętrzna: -5°C
- Scenariusz: S3 (3 nagrzewnice)
- OKRES_ROTACJI_UKŁADÓW = 168h (7 dni)
- Aktualny układ: Podstawowy
- Czas od ostatniej zmiany: 169h

**Przebieg:**

1. **Dzień 0, godz. 00:00** - System w układzie Podstawowym
   - Pracują: N1, N2, N3 + W1 (PID)
   - Nawiew na -4,30m

2. **Dzień 7, godz. 01:00** - Upłynął OKRES_ROTACJI_UKŁADÓW
   - Warunki rotacji spełnione 
   - Algorytm rozpoczyna zmianę: Podstawowy → Ograniczony

3. **Dzień 7, godz. 01:05** - Zmiana zakończona
   - Pracują: N5, N6, N7 + W2 (PID)
   - Nawiew na -4,30m przez spinę ciągów
   - Zarejestrowano zdarzenie w dzienniku

4. **Dzień 14, godz. 01:00** - Kolejna rotacja
   - Zmiana: Ograniczony → Podstawowy
   - Powrót do N1, N2, N3 + W1

**Rezultat po miesiącu:**
- Ciąg 1: ~360h pracy (50%)
- Ciąg 2: ~360h pracy (50%)
- Stosunek eksploatacji: 1.0 ✅ Idealne wyrównanie

---

