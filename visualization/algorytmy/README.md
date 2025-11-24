# Wizualizacje Algorytmów Sterowania

## 🎯 Flowcharty Algorytmów

Ten katalog zawiera diagramy przepływu dla algorytmów 5, 5A i 5B.

### 📊 Dostępne Diagramy

#### 1. `algorytm-5-wybor-scenariusza-flowchart.svg`
**Algorytm 5: Automatyczny Wybór Scenariusza Pracy**

Diagram przedstawia:
- Monitoring temperatury zewnętrznej (co 10s)
- Logikę wyboru scenariusza S0-S8
- Histerezę przy przełączaniu
- Sekwencje załączania/wyłączania nagrzewnic
- Obsługę stanów awaryjnych

**Kluczowe elementy:**
- Odczyt i walidacja t_zewn
- Określenie wymaganego scenariusza (z histerezą)
- Sprawdzenie warunków stabilności
- Wykonanie zmiany scenariusza
- Weryfikacja stanu końcowego

📖 [Dokumentacja Algorytmu 5](../../docs/02-algorytmy/algorytm-5-wybor-scenariusza.md)

---

#### 2. `algorytm-5A-rotacja-ukladow-flowchart.svg`
**Algorytm 5A: Cykliczna Rotacja Układów Pracy Ciągów**

Diagram przedstawia:
- Sprawdzanie warunków rotacji (scenariusz, sprawność, tryb)
- Licznik czasu pracy układów
- Logikę przełączania Podstawowy ↔ Ograniczony
- Koordynację z Algorytmem 5B (blokady)
- Sekwencje zmiany układu

**Kluczowe elementy:**
- Warunek czasowy (OKRES_ROTACJI_UKŁADÓW)
- Sprawdzenie gotowości ciągu 2
- Blokada `zmiana_układu_w_toku`
- Sekwencja: zatrzymaj C1 → otwórz spinę → uruchom C2
- Aktualizacja liczników

📖 [Dokumentacja Algorytmu 5A](../../docs/02-algorytmy/algorytm-5A-rotacja-ukladow.md)

---

#### 3. `algorytm-5B-rotacja-nagrzewnic-flowchart.svg`
**Algorytm 5B: Cykliczna Rotacja Nagrzewnic w Obrębie Ciągu**

Diagram przedstawia:
- Aktualizację liczników czasu pracy nagrzewnic
- Logikę wyboru nagrzewnicy do wymiany
- Koordynację z Algorytmem 5A (blokady)
- Sekwencję rotacji: załącz nową → wyłącz starą
- Weryfikację temperatury

**Kluczowe elementy:**
- Sprawdzenie ciągu aktywnego w aktualnym układzie/scenariuszu
- Blokada `rotacja_nagrzewnic_w_toku`
- Wybór najdłużej pracującej i najdłużej w postoju
- Zasada bezpieczeństwa: najpierw załącz, potem wyłącz
- Weryfikacja MIN_DELTA_CZASU

📖 [Dokumentacja Algorytmu 5B](../../docs/02-algorytmy/algorytm-5B-rotacja-nagrzewnic.md)

---

#### 4. `koordynacja-5A-5B-timeline.svg`
**Timeline Koordynacji Algorytmów 5A ↔ 5B**

Diagram przedstawia:
- Oś czasu z przykładowym scenariuszem działania
- Momenty wykonania rotacji układów (5A)
- Momenty wykonania rotacji nagrzewnic (5B)
- Blokady wzajemne (mutex)
- Odstępy czasowe (1h, 15 min)

**Kluczowe elementy:**
- Blokada `zmiana_układu_w_toku` (5A → blokuje 5B)
- Blokada `rotacja_nagrzewnic_w_toku` (5B → blokuje 5A)
- Odroczona rotacja nagrzewnic (1h po zmianie układu)
- Odstęp 15 min między rotacjami w różnych ciągach
- Praktyczny przykład koordynacji

📖 [Koordynacja 5A↔5B](../../docs/02-algorytmy/README.md#koordynacja-algorytmów-5a-i-5b)

---

## 🔄 Relacje Między Algorytmami

```
┌─────────────────────────────────────────────────────┐
│  Algorytm 5: Wybór Scenariusza (S0-S8)             │
│  • Monitoruje: t_zewn                               │
│  • Decyduje: ILE nagrzewnic (0-8)                   │
│  • Częstotliwość: co 10s                            │
└────────────────────┬────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────┐
│  Algorytm 5A: Rotacja Układów (tylko S1-S4)        │
│  • Monitoruje: czas pracy układu                    │
│  • Decyduje: KTÓRY ciąg (C1 lub C2)                 │
│  • Częstotliwość: co OKRES_ROTACJI_UKŁADÓW          │
└────────────────────┬────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────┐
│  Algorytm 5B: Rotacja Nagrzewnic                   │
│  • Monitoruje: czas pracy nagrzewnic                │
│  • Decyduje: KTÓRE nagrzewnice (N1-N8)              │
│  • Częstotliwość: co OKRES_ROTACJI_NAGRZEWNIC       │
└─────────────────────────────────────────────────────┘
```

## 🛠️ Jak Używać Tych Diagramów?

### Dla Programistów PLC
1. Użyj flowchartów jako podstawy implementacji
2. Sprawdź wszystkie warunki i blokady
3. Zaimplementuj obsługę stanów awaryjnych
4. Przetestuj koordynację między algorytmami

### Dla Testerów
1. Użyj flowchartów do przygotowania scenariuszy testowych
2. Sprawdź wszystkie ścieżki w diagramie
3. Przetestuj przypadki brzegowe
4. Zweryfikuj blokady i odstępy czasowe

### Dla Dokumentalistów
1. Odnośniki do flowchartów w dokumentacji
2. Flowcharty jako wizualizacja pseudokodu
3. Narzędzie wyjaśniania logiki

## 📖 Powiązana Dokumentacja

- [Przegląd Algorytmów](../../docs/02-algorytmy/README.md) - wprowadzenie
- [Algorytm 5](../../docs/02-algorytmy/algorytm-5-wybor-scenariusza.md) - szczegóły
- [Algorytm 5A](../../docs/02-algorytmy/algorytm-5A-rotacja-ukladow.md) - szczegóły
- [Algorytm 5B](../../docs/02-algorytmy/algorytm-5B-rotacja-nagrzewnic.md) - szczegóły
- [Architektura](../../docs/01-system/architektura.md) - kontekst systemowy

## 🎨 Format Diagramów

- **Format:** SVG (Scalable Vector Graphics)
- **Zalety:** skalowalne bez utraty jakości, edytowalne, małe pliki
- **Narzędzia:** Można otwierać w przeglądarce, edytorze SVG lub IDE

