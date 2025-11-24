# Algorytmy Sterowania - System BOGDANKA Szyb 2

**Dokument szczegółowy zawierający algorytmy automatycznego sterowania i rotacji**

_Plik ten jest częścią dokumentacji systemu sterowania nagrzewnicami BOGDANKA Szyb 2._

[← Powrót do dokumentacji głównej](../01-system/architektura.md)

---

**Ostatnia aktualizacja:** 24 Listopad 2025  
**Status:** Algorytmy do implementacji w PLC  
**Zatwierdzenie:** Wymaga akceptacji technologa

---

## 📑 Spis Treści

1. [Algorytm 5: Wybór Scenariusza Pracy](algorytm-5-wybor-scenariusza.md)
2. [Algorytm 5A: Rotacja Układów Pracy Ciągów](algorytm-5A-rotacja-ukladow.md)
3. [Algorytm 5B: Rotacja Nagrzewnic w Obrębie Ciągu](algorytm-5B-rotacja-nagrzewnic.md)
4. [Koordynacja Algorytmów](koordynacja.md)

---

## Wprowadzenie

System sterowania BOGDANKA Szyb 2 wykorzystuje **trzy współpracujące algorytmy** zapewniające automatyczne sterowanie i równomierne rozłożenie eksploatacji urządzeń:

### **Algorytm 5: Automatyczny Wybór Scenariusza Pracy**
- **Cel:** Automatyczny dobór ilości nagrzewnic i konfiguracji systemu w zależności od temperatury zewnętrznej
- **Zakres:** Przełączanie między scenariuszami S0-S8
- **Częstotliwość:** Ciągły monitoring temperatury
- **Dotyczy:** Całego systemu - fundament sterowania

### **Algorytm 5A: Rotacja Układów Pracy Ciągów**
- **Cel:** Wyrównanie eksploatacji między ciągiem 1 (W1) a ciągiem 2 (W2)
- **Zakres:** Zmiana między układem Podstawowym a Ograniczonym
- **Okres:** dni/tygodnie/miesiące (definiowany przez technologa)
- **Dotyczy:** Scenariuszy S1-S4

### **Algorytm 5B: Rotacja Nagrzewnic w Ciągu**
- **Cel:** Wyrównanie eksploatacji nagrzewnic w obrębie jednego ciągu
- **Zakres:** Wymiana pracującej nagrzewnicy na rezerwową w tym samym ciągu
- **Okres:** godziny/dni/tygodnie (definiowany przez technologa)
- **Dotyczy:** Wszystkich nagrzewnic N1-N8

### **Hierarchia i Koordynacja Algorytmów**

```
┌────────────────────────────────────────────┐
│ Algorytm 5: Wybór Scenariusza (S0-S8)      │
│ └─ Decyduje: ile nagrzewnic, który układ   │
└─────────────────────┬──────────────────────┘
                      │
            ┌─────────┴─────────┐
            │                   │
            ▼                   ▼
     ┌──────────────┐    ┌──────────────┐
     │ Algorytm 5A  │    │ Algorytm 5B  │
     │ Rotacja      │◄───┤ Rotacja      │
     │ Układów      │───►│ Nagrzewnic   │
     │ (C1 ↔ C2)    │    │ (N1-N8)      │
     └──────────────┘    └──────────────┘
```

Algorytmy są **skoordynowane** i działają współbieżnie, zapewniając:
- Automatyczną adaptację do warunków atmosferycznych (Alg. 5)
- Równomierność zużycia ciągów wentylacyjnych C1, C2 i wentylatorów W1, W2 (Alg. 5A)
- Równomierność zużycia wszystkich 8 nagrzewnic N1-N8 (Alg. 5B)

---

## Relacja między PARTPG/PARTS a Algorytmami 5, 5A, 5B

### Architektura Dwuwarstwowa Systemu SAR

System automatycznej regulacji (SAR) temperatury szybu ma **dwuwarstwową architekturę**:

![Architektura SAR](../assets/images/architektura_SAR_system.svg)

*Rys. Dwuwarstwowa architektura systemu SAR z podziałem na warstwy regulacji i zarządzania.*

```
┌──────────────────────────────────────────────────────────────┐
│ PARTS - Podsystem Automatycznej Regulacji Temperatury Szybu  │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ WARSTWA REGULACJI (podstawowa funkcja systemu)           │ │
│ │ • 2 × UAR (regulatory PID wentylatorów W1, W2)           │ │
│ │ • Utrzymanie Ts = 2°C w szybie (-30m)                    │ │
│ │ • Sterowanie częstotliwością (25-50 Hz)                  │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ WARSTWA ZARZĄDZANIA (optymalizacja użycia urządzeń)      │ │
│ │ • Algorytm 5:  Automatyczny dobór scenariusza (S0-S8)    │ │
│ │ • Algorytm 5A: Rotacja układów pracy ciągów (C1 ↔ C2)    │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ PARTPG - Podsystem Automatycznej Regulacji Temp. Pow. Grz.   │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ WARSTWA REGULACJI (podstawowa funkcja systemu)           │ │
│ │ • 8 × UAR (regulatory PID zaworów N1-N8)                 │ │
│ │ • Utrzymanie Tz = 50°C na wylocie z nagrzewnicy          │ │
│ │ • Sterowanie zaworem wody grzewczej (20-100%)            │ │
│ │ • Załączanie/wyłączanie nagrzewnic                       │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ WARSTWA ZARZĄDZANIA (optymalizacja użycia urządzeń)      │ │
│ │ • Algorytm 5B: Rotacja nagrzewnic w ciągach (N1-N8)      │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Kluczowe Zasady Relacji

**1. PARTPG i PARTS to PODSYSTEMY zawierające warstwy regulacji i zarządzania**

| Podsystem | Warstwa Regulacji | Warstwa Zarządzania (Optymalizacja) |
|-----------|-------------------|-------------------------------------|
| **PARTPG** | 8 × PID zaworów (Tz=50°C) | **Algorytm 5B** - rotacja nagrzewnic |
| **PARTS** | 2 × PID wentylatorów (Ts=2°C) | **Algorytmy 5 i 5A** - wybór scenariusza i rotacja układów |

**2. Warstwa Regulacji = Funkcja Podstawowa**
- Utrzymanie zadanych temperatur (50°C, 2°C)
- Praca ciągła, realizacja w czasie rzeczywistym
- Niezbędna dla działania systemu

**3. Warstwa Zarządzania = Funkcja Optymalizująca**
- Równomierne wykorzystanie urządzeń
- Minimalizacja zużycia pojedynczych komponentów
- Maksymalizacja niezawodności i żywotności systemu
- Automatyczna adaptacja do warunków zewnętrznych

### Przykład Działania Warstw

**Scenariusz: Temperatura zewnętrzna -6°C**

```
┌─────────────────────────────────────────────────────────┐
│ PARTS - WARSTWA ZARZĄDZANIA                             │
│ Algorytm 5: t_zewn = -6°C → Scenariusz S3 (3 nagr.)     │
│ Algorytm 5A: Aktualny układ = "Podstawowy" → Ciąg C1    │
└────────────────────────────┬────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────┐
│ PARTPG - WARSTWA ZARZĄDZANIA                            │
│ Algorytm 5B: Wybiera N2, N3, N4 (na podstawie rotacji)  │
└────────────────────────────┬────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────┐
│ PARTPG - WARSTWA REGULACJI                              │
│ • PID nagrzewnicy N2: reguluje zawór → Tz = 50°C        │
│ • PID nagrzewnicy N3: reguluje zawór → Tz = 50°C        │
│ • PID nagrzewnicy N4: reguluje zawór → Tz = 50°C        │
└────────────────────────────┬────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────┐
│ PARTS - WARSTWA REGULACJI                               │
│ • PID wentylatora W1: reguluje częstotliwość → Ts = 2°C │
└─────────────────────────────────────────────────────────┘
```

**Kluczowa obserwacja:**
- Bez **warstwy regulacji** (PID) - system nie utrzyma temperatury
- Bez **warstwy zarządzania** (algorytmy) - system działa, ale:
  - Zawsze te same nagrzewnice (np. N1, N2, N3)
  - Nierównomierne zużycie → awarie, przestoje

### Dokumentacja w Kontekście Projektu

**Ten katalog** (`docs/02-algorytmy/`) szczegółowo opisuje **warstwę zarządzania**:
- Algorytm 5 → część zarządzająca PARTS
- Algorytm 5A → część zarządzająca PARTS
- Algorytm 5B → część zarządzająca PARTPG

**Dokument główny** ([`docs/01-system/architektura.md`](../01-system/architektura.md)) opisuje:
- Punkt 2: Definicje PARTPG i PARTS (warstwa regulacji + zarządzania)
- Punkt 3-4: Warunki załączania/wyłączania (warstwa regulacji)
- Punkt 5: Scenariusze (warstwa zarządzania - Algorytm 5)
- Punkt 6-7: UAR nagrzewnic i wentylatorów (warstwa regulacji)

---

## 🎨 Wizualizacje

Wszystkie diagramy flowchart dostępne są w katalogu [`visualization/algorytmy/`](../../visualization/algorytmy/):

- [Algorytm 5 - Wybór Scenariusza](../../visualization/algorytmy/algorytm-5-wybor-scenariusza-flowchart.svg)
- [Algorytm 5A - Rotacja Układów](../../visualization/algorytmy/algorytm-5A-rotacja-ukladow-flowchart.svg)
- [Algorytm 5B - Rotacja Nagrzewnic](../../visualization/algorytmy/algorytm-5B-rotacja-nagrzewnic-flowchart.svg)
- [Koordynacja 5A ↔ 5B - Timeline](../../visualization/algorytmy/koordynacja-5A-5B-timeline.svg)

---

**Wersja:** 2.0 (zreorganizowana struktura)  
**Data:** 24 Listopad 2025  
**Branch:** `refactor/docs-restructure`

