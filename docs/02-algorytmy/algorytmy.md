# Algorytmy Sterowania - System BOGDANKA Szyb 2

**Dokument szczegółowy zawierający algorytmy automatycznego sterowania i rotacji**

_Plik ten jest częścią dokumentacji systemu sterowania nagrzewnicami BOGDANKA Szyb 2._

[← Powrót do dokumentacji głównej](../01-system/system.md)

---

**Ostatnia aktualizacja:** 24 Listopad 2025  
**Status:** Algorytmy do implementacji w PLC  
**Zatwierdzenie:** Wymaga akceptacji technologa

---

## 📑 Spis Treści

1. [Algorytm WS: Wybór Scenariusza Pracy](algorytm-WS-wybor-scenariusza.md)
2. [Algorytm RC: Rotacja Układów Pracy Ciągów](algorytm-RC-rotacja-ciagow.md)
3. [Algorytm RN: Rotacja Nagrzewnic w Obrębie Ciągu](algorytm-RN-rotacja-nagrzewnic.md)
4. [Wizualizacja Koordynacji RC↔RN](./schematy/koordynacja-RC-RN-timeline.svg)

---

## Wprowadzenie

System sterowania BOGDANKA Szyb 2 wykorzystuje **trzy współpracujące algorytmy** zapewniające automatyczne sterowanie i równomierne rozłożenie eksploatacji urządzeń:

### **Algorytm WS: Automatyczny Wybór Scenariusza Pracy**
- **Cel:** Automatyczny dobór ilości nagrzewnic i konfiguracji systemu w zależności od temperatury zewnętrznej
- **Zakres:** Przełączanie między scenariuszami S0-S8
- **Częstotliwość:** Ciągły monitoring temperatury
- **Dotyczy:** Całego systemu - fundament sterowania

### **Algorytm RC: Rotacja Układów Pracy Ciągów**
- **Cel:** Wyrównanie eksploatacji między ciągiem 1 (W1) a ciągiem 2 (W2)
- **Zakres:** Zmiana między układem Podstawowym a Ograniczonym
- **Okres:** dni/tygodnie/miesiące (definiowany przez technologa)
- **Dotyczy:** Scenariuszy S1-S4

### **Algorytm RN: Rotacja Nagrzewnic w Ciągu**
- **Cel:** Wyrównanie eksploatacji nagrzewnic w obrębie jednego ciągu
- **Zakres:** Wymiana pracującej nagrzewnicy na rezerwową w tym samym ciągu
- **Okres:** godziny/dni/tygodnie (definiowany przez technologa)
- **Dotyczy:** Wszystkich nagrzewnic N1-N8

### **Hierarchia i Koordynacja Algorytmów**

```
┌────────────────────────────────────────────┐
│ Algorytm WS: Wybór Scenariusza (S0-S8)      │
│ └─ Decyduje: ile nagrzewnic, który układ   │
└─────────────────────┬──────────────────────┘
                      │
            ┌─────────┴─────────┐
            │                   │
            ▼                   ▼
     ┌──────────────┐    ┌──────────────┐
     │ Algorytm RC  │    │ Algorytm RN  │
     │ Rotacja      │◄───┤ Rotacja      │
     │ Układów      │───►│ Nagrzewnic   │
     │ (C1 ↔ C2)    │    │ (N1-N8)      │
     └──────────────┘    └──────────────┘
```

Algorytmy są **skoordynowane** i działają współbieżnie, zapewniając:
- Automatyczną adaptację do warunków atmosferycznych (Alg. WS)
- Równomierność zużycia ciągów wentylacyjnych C1, C2 i wentylatorów W1, W2 (Alg. RC)
- Równomierność zużycia wszystkich 8 nagrzewnic N1-N8 (Alg. RN)

---

## Relacja między PARTPG/PARTS a Algorytmami 5, 5A, 5B

### Architektura Dwuwarstwowa Systemu SAR

System automatycznej regulacji (SAR) temperatury szybu ma **dwuwarstwową architekturę**:

![Architektura SAR](../01-system/architektura_SAR_system.svg)

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
│ │ • Algorytm WS:  Automatyczny dobór scenariusza (S0-S8)    │ │
│ │ • Algorytm RC: Rotacja układów pracy ciągów (C1 ↔ C2)    │ │
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
│ │ • Algorytm RN: Rotacja nagrzewnic w ciągach (N1-N8)      │ │
│ └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Kluczowe Zasady Relacji

**1. PARTPG i PARTS to PODSYSTEMY zawierające warstwy regulacji i zarządzania**

| Podsystem | Warstwa Regulacji | Warstwa Zarządzania (Optymalizacja) |
|-----------|-------------------|-------------------------------------|
| **PARTPG** | 8 × PID zaworów (Tz=50°C) | **Algorytm RN** - rotacja nagrzewnic |
| **PARTS** | 2 × PID wentylatorów (Ts=2°C) | **Algorytmy WS i RC** - wybór scenariusza i rotacja układów |

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
│ Algorytm WS: t_zewn = -6°C → Scenariusz S3 (3 nagr.)     │
│ Algorytm RC: Aktualny układ = "Podstawowy" → Ciąg C1    │
└────────────────────────────┬────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────┐
│ PARTPG - WARSTWA ZARZĄDZANIA                            │
│ Algorytm RN: Wybiera N2, N3, N4 (na podstawie rotacji)  │
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
- Algorytm WS → część zarządzająca PARTS
- Algorytm RC → część zarządzająca PARTS
- Algorytm RN → część zarządzająca PARTPG

**Dokument główny** ([`docs/01-system/system.md`](../01-system/system.md)) opisuje:
- Punkt 2: Definicje PARTPG i PARTS (warstwa regulacji + zarządzania)
- Punkt 3-4: Warunki załączania/wyłączania (warstwa regulacji)
- Punkt 5: Scenariusze (warstwa zarządzania - Algorytm 5)
- Punkt 6-7: UAR nagrzewnic i wentylatorów (warstwa regulacji)

---

## 🎨 Wizualizacje

Wszystkie diagramy flowchart dostępne są w katalogu [`visualization/algorytmy/`](./schematy/):

- [Algorytm WS - Wybór Scenariusza](./schematy/algorytm-WS-wybor-scenariusza-flowchart.svg)
- [Algorytm RC - Rotacja Układów](./schematy/algorytm-RC-rotacja-ciagow-flowchart.svg)
- [Algorytm RN - Rotacja Nagrzewnic](./schematy/algorytm-RN-rotacja-nagrzewnic-flowchart.svg)
- [Koordynacja RC ↔ RN - Timeline](./schematy/koordynacja-RC-RN-timeline.svg)

---

**Wersja:** 2.0 (zreorganizowana struktura)  
**Data:** 24 Listopad 2025  
**Branch:** `refactor/docs-restructure`

