# Wizualizacje Scenariuszy Pracy (S0-S8)

## 🎯 Diagramy Scenariuszy

Ten katalog zawiera wizualizacje przedstawiające konfiguracje systemu dla każdego scenariusza pracy.

## 📊 Scenariusze - Przegląd

System automatycznie dobiera scenariusz w zależności od **temperatury zewnętrznej**:

| Scenariusz | Zakres Temp. | Nagrzewnice | Ciągi | W1 | W2 |
|------------|--------------|-------------|-------|----|----|
| **S0** | t ≥ 3°C | 0 | - | OFF | OFF |
| **S1** | -1°C < t ≤ 2°C | 1 | C1 lub C2 | PID | OFF |
| **S2** | -4°C < t ≤ -1°C | 2 | C1 lub C2 | PID | OFF |
| **S3** | -8°C < t ≤ -4°C | 3 | C1 lub C2 | PID | OFF |
| **S4** | -11°C < t ≤ -8°C | 4 | C1 lub C2 | PID/MAX | OFF |
| **S5** | -15°C < t ≤ -11°C | 5 | C1 + C2 | MAX | PID |
| **S6** | -18°C < t ≤ -15°C | 6 | C1 + C2 | MAX | PID |
| **S7** | -21°C < t ≤ -18°C | 7 | C1 + C2 | MAX | PID |
| **S8** | t ≤ -21°C | 8 | C1 + C2 | MAX | PID |

## 📄 Dostępne Diagramy

### `scenariusz-S0.svg`
**S0: System Wyłączony (t ≥ 3°C)**

Diagram pokazuje:
- Wszystkie nagrzewnice wyłączone
- Oba wentylatory zatrzymane
- Wszystkie przepustnice zamknięte
- Brak nawiewu do szybu

**Kiedy:** Temperatura zewnętrzna ≥ 3°C (ciepło)

---

### `scenariusz-S1.svg`
**S1: Jedna Nagrzewnica (-1°C < t ≤ 2°C)**

Diagram pokazuje:
- 1 nagrzewnica aktywna (z C1 lub C2 - zależnie od układu)
- 1 wentylator w trybie PID (W1 lub W2)
- Nawiew: +4,30m
- Minimalna moc grzewcza

**Kiedy:** Temperatura zewnętrzna: -1°C do 2°C (chłodno)

---

### `scenariusz-S2.svg`
**S2: Dwie Nagrzewnice (-4°C < t ≤ -1°C)**

Diagram pokazuje:
- 2 nagrzewnice aktywne
- 1 wentylator w trybie PID
- Nawiew: +4,30m
- Zwiększona moc grzewcza

**Kiedy:** Temperatura zewnętrzna: -4°C do -1°C (zimno)

---

### `scenariusz-S3.svg`
**S3: Trzy Nagrzewnice (-8°C < t ≤ -4°C)**

Diagram pokazuje:
- 3 nagrzewnice aktywne
- 1 wentylator w trybie PID
- Nawiew: +4,30m
- Średnia moc grzewcza

**Kiedy:** Temperatura zewnętrzna: -8°C do -4°C (mróz)

---

### `scenariusz-S4.svg`
**S4: Cztery Nagrzewnice (-11°C < t ≤ -8°C)**

Diagram pokazuje:
- 4 nagrzewnice aktywne (cały ciąg)
- 1 wentylator w trybie PID lub MAX
- Nawiew: +4,30m
- Maksymalna moc jednego ciągu

**Kiedy:** Temperatura zewnętrzna: -11°C do -8°C (silny mróz)

---

### `scenariusz-S5.svg`
**S5: Pięć Nagrzewnic (-15°C < t ≤ -11°C)**

Diagram pokazuje:
- **C1: 4 nagrzewnice** (N1-N4) + W1 MAX
- **C2: 1 nagrzewnica** (N5) + W2 PID
- Nawiew: +4,30m + +7,90m (dwa poziomy!)
- Układ ZAWSZE podstawowy
- Pierwszy scenariusz z dwoma ciągami

**Kiedy:** Temperatura zewnętrzna: -15°C do -11°C (bardzo zimno)

---

### `scenariusz-S6.svg`
**S6: Sześć Nagrzewnic (-18°C < t ≤ -15°C)**

Diagram pokazuje:
- **C1: 4 nagrzewnice** (N1-N4) + W1 MAX
- **C2: 2 nagrzewnice** (N5-N6) + W2 PID
- Nawiew: +4,30m + +7,90m
- Zwiększona moc drugiego ciągu

**Kiedy:** Temperatura zewnętrzna: -18°C do -15°C (ekstremalny mróz)

---

### `scenariusz-S7.svg`
**S7: Siedem Nagrzewnic (-21°C < t ≤ -18°C)**

Diagram pokazuje:
- **C1: 4 nagrzewnice** (N1-N4) + W1 MAX
- **C2: 3 nagrzewnice** (N5-N7) + W2 PID
- Nawiew: +4,30m + +7,90m
- Prawie maksymalna moc systemu

**Kiedy:** Temperatura zewnętrzna: -21°C do -18°C (ekstremalne warunki)

---

### `scenariusz-S8.svg`
**S8: Osiem Nagrzewnic (t ≤ -21°C)**

Diagram pokazuje:
- **C1: 4 nagrzewnice** (N1-N4) + W1 MAX
- **C2: 4 nagrzewnice** (N5-N8) + W2 PID
- Nawiew: +4,30m + +7,90m
- **Maksymalna moc systemu** - wszystkie nagrzewnice pracują!
- Oba ciągi w pełnej mocy

**Kiedy:** Temperatura zewnętrzna ≤ -21°C (najzimniejsze warunki)

---

## 🌡️ Histereza Przy Przełączaniu

System stosuje **histerezę** aby zapobiec częstym przełączeniom przy temperaturach granicznych:

```
Przykład S1:
- Załączenie: t ≤ 2°C
- Wyłączenie: t ≥ 3°C
- Histereza: 1°C
```

**Dlaczego?**
- Zapobiega oscylacjom przy temp. ~2°C
- Zmniejsza zużycie urządzeń (mniej starów)
- Stabilizuje system

## 🔄 Przejścia Między Scenariuszami

### Typy Przejść

| Typ | Przykład | Czas | Złożoność |
|-----|----------|------|-----------|
| **A** | S1→S0 | ~60s | Wyłączenie systemu |
| **B** | S0→S1 | ~70s | Uruchomienie systemu |
| **C** | S2→S3 | ~45s | Dodanie nagrzewnicy |
| **D** | S4→S5 | ~100s | ⚠️ Uruchomienie C2 |
| **E** | S5→S4 | ~70s | ⚠️ Zatrzymanie C2 |
| **F** | S6→S7 | ~45s | Dodanie w C2 |

### Najważniejsze Przejście: S4→S5

**Dlaczego specjalne?**
- Po raz pierwszy uruchamia się drugi ciąg (C2)
- Otwiera się wyrzutnia +7,90m
- W1 przechodzi z PID → MAX
- Uruchamia się W2 jako regulator

📊 Zobacz [Algorytm WS - Sekwencje](../../docs/02-algorytmy/algorytm-WS-wybor-scenariusza.md#510-szczegółowe-sekwencje-zmian-scenariuszy)

## 🎯 Jak Używać Tych Diagramów?

### Dla Operatorów
1. Sprawdź aktualną temperaturę zewnętrzną
2. Znajdź odpowiedni scenariusz w tabeli
3. Zobacz diagram - zrozum aktywną konfigurację
4. Porównaj z HMI - zweryfikuj poprawność

### Dla Serwisantów
1. Przed interwencją sprawdź aktualny scenariusz
2. Zobacz diagram - zidentyfikuj aktywne urządzenia
3. Zaplanuj sekwencję wyłączenia (bezpieczeństwo)
4. Po naprawie sprawdź czy system wrócił do scenariusza

### Dla Projektantów HMI
1. Użyj diagramów jako wzór wizualizacji
2. Pokaż aktywne nagrzewnice zielonym kolorem
3. Zaznacz aktywne wentylatory
4. Wyświetl stan przepustnic

## 🔗 Powiązana Dokumentacja

- [Algorytm WS](../../docs/02-algorytmy/algorytm-WS-wybor-scenariusza.md) - automatyczny wybór scenariusza
- [Architektura](../../docs/01-system/architektura.md) - szczegóły scenariuszy
- [Flowchart Algorytmu 5](../algorytmy/algorytm-WS-wybor-scenariusza-flowchart.svg)
- [Rotacje](../rotacje/) - diagramy rotacji w scenariuszach

## 🎨 Konwencje Wizualne

### Kolory Nagrzewnic
- 🟢 **Zielony:** nagrzewnica aktywna (pracuje)
- ⚪ **Biały/Szary:** nagrzewnica nieaktywna (postój)

### Kolory Wentylatorów
- 🔵 **Niebieski PID:** wentylator w trybie regulacji (25-50 Hz)
- 🔴 **Czerwony MAX:** wentylator na maksymalnej mocy (50 Hz)
- ⚫ **Czarny OFF:** wentylator zatrzymany

### Przepustnice
- 🟡 **Żółty:** przepustnica otwarta
- 🔴 **Czerwony:** przepustnica zamknięta

### Kierunek Przepływu
- ➡️ **Grube strzałki:** główny kierunek nawiewu do szybu
- → **Cienkie strzałki:** przepływ między elementami

