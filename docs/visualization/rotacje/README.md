# Wizualizacje Rotacji Układów i Nagrzewnic

## 🔄 Diagramy Rotacji

Ten katalog zawiera wizualizacje przedstawiające różne konfiguracje układów pracy podczas rotacji.

## 📊 Rotacja Układów (Algorytm RC)

### Układ Podstawowy vs Ograniczony w Scenariuszach S1-S4

#### `5A-uklad-podstawowy-S1.svg` do `5A-uklad-podstawowy-S4.svg`
**Układ Podstawowy - Ciąg 1 Aktywny**

Diagram pokazuje:
- Ciąg 1 (N1-N4) aktywny
- Wentylator W1 w trybie PID
- Nawiew: +4,30m (wyrzutnia górna)
- Przepustnice: C1 otwarte, spinka zamknięta
- Ilość nagrzewnic zależna od scenariusza (S1: 1, S2: 2, S3: 3, S4: 4)

**Kiedy:** Układ Podstawowy w scenariuszach S1-S4

---

#### `RC-uklad-ograniczony-S1.svg` do `RC-uklad-ograniczony-S4.svg`
**Układ Ograniczony - Ciąg 2 Aktywny**

Diagram pokazuje:
- Ciąg 2 (N5-N8) aktywny
- Wentylator W2 w trybie PID
- Nawiew: +4,30m (przez spinę ciągów)
- Przepustnice: C2 otwarte, spinka otwarta, C1 zamknięte
- Ilość nagrzewnic zależna od scenariusza (S1: 1, S2: 2, S3: 3, S4: 4)

**Kiedy:** Układ Ograniczony w scenariuszach S1-S4 (po rotacji układów)

---

## 🔁 Rotacja Nagrzewnic (Algorytm RN)

### Przykłady Rotacji w Scenariuszu S3

#### `5B-rotacja-S3-tydzien-1.svg`
**Tydzień 1: Konfiguracja Początkowa**

Pracują: N1, N2, N3  
Postój: N4

---

#### `5B-rotacja-S3-tydzien-2.svg`
**Tydzień 2: Po Pierwszej Rotacji**

Pracują: N2, N3, N4  
Postój: N1

**Zmiana:** N1 → N4 (N1 najdłużej pracowała, N4 najdłużej w postoju)

---

#### `5B-rotacja-S3-tydzien-3.svg`
**Tydzień 3: Po Drugiej Rotacji**

Pracują: N3, N4, N1  
Postój: N2

**Zmiana:** N2 → N1

---

#### `5B-rotacja-S3-tydzien-4.svg`
**Tydzień 4: Po Trzeciej Rotacji**

Pracują: N4, N1, N2  
Postój: N3

**Zmiana:** N3 → N2

---

## 📈 Zrozumienie Rotacji

### Cel Rotacji Układów (5A)
**Problem bez rotacji:**
- Ciąg 1 pracuje zawsze w S1-S4 → nierównomierne zużycie C1 vs C2
- W1 pracuje znacznie więcej niż W2

**Rozwiązanie z rotacją:**
- Co X dni system zmienia układ: Podstawowy ↔ Ograniczony
- Równomierne zużycie obu ciągów i wentylatorów

### Cel Rotacji Nagrzewnic (5B)
**Problem bez rotacji:**
- N1 pracuje zawsze (100% czasu) → najszybsze zużycie
- N4 nie pracuje (0% czasu) → brak zużycia
- Nierównomierne obciążenie nagrzewnic

**Rozwiązanie z rotacją:**
- Co Y dni system wymienia nagrzewnicę: najdłużej pracująca ↔ najdłużej w postoju
- Równomierne zużycie wszystkich nagrzewnic (~25% dla 4 nagrzewnic)

## 🎯 Przykład Użycia Diagramów

### Dla Operatorów
1. Zobacz aktualny układ pracy na HMI
2. Sprawdź odpowiedni diagram rotacji
3. Zidentyfikuj aktywne nagrzewnice i wentylatory
4. Zrozum dlaczego system zmienił konfigurację

### Dla Serwisantów
1. Przed konserwacją sprawdź diagramy rotacji
2. Zidentyfikuj która nagrzewnica była najdłużej w pracy
3. Zaplanuj wymianę filtrów/czyszczenie
4. Sprawdź historię rotacji w systemie

### Dla Projektantów
1. Zrozum logikę rotacji
2. Zaprojektuj HMI zgodnie z diagramami
3. Wizualizuj aktualną konfigurację
4. Dodaj historię rotacji

## 📊 Parametry Rotacji

| Parametr | Wartość domyślna | Zakres | Opis |
|----------|-----------------|--------|------|
| OKRES_ROTACJI_UKŁADÓW | Do ustalenia | 24h - 30 dni | Częstotliwość zmiany układu |
| OKRES_ROTACJI_NAGRZEWNIC | Do ustalenia | 24h - 720h | Częstotliwość zmiany nagrzewnicy |
| MIN_DELTA_CZASU | 3600s | 1800s - 7200s | Min. różnica czasu dla rotacji RN |

## 🔗 Powiązana Dokumentacja

- [Algorytm RC](../../02-algorytmy/algorytm-RC-rotacja-ciagow.md) - rotacja układów
- [Algorytm RN](../../02-algorytmy/algorytm-RN-rotacja-nagrzewnic.md) - rotacja nagrzewnic
- [Koordynacja RC↔RN](../algorytmy/koordynacja-RC-RN-timeline.svg) - timeline
- [Scenariusze](../scenariusze/) - konfiguracje scenariuszy S0-S8

## 🎨 Konwencje Wizualne

### Kolory
- 🟢 **Zielony:** nagrzewnice aktywne
- ⚪ **Biały/Szary:** nagrzewnice w postoju
- 🔵 **Niebieski:** wentylatory aktywne
- 🟡 **Żółty:** przepustnice otwarte
- 🔴 **Czerwony:** przepustnice zamknięte

### Oznaczenia
- ➡️ **Strzałki:** kierunek przepływu powietrza
- 🔄 **Symbol rotacji:** nagrzewnica w trakcie zmiany
- ⏱️ **Zegar:** wskazanie tygodnia/okresu rotacji

