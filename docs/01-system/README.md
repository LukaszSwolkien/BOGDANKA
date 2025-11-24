# System Sterowania - Architektura

## 📄 Dokumenty

### [architektura.md](./architektura.md)
Główny dokument opisujący **kompletną architekturę systemu sterowania BOGDANKA Szyb 2**.

**Zawartość:**
1. **Wprowadzenie** - cel, zakres, terminologia
2. **Podsystemy** - PARTPG (temp. powietrza grzewczego) i PARTS (temp. szybu)
3. **Warunki załączania** - sekwencje startowe nagrzewnic
4. **Warunki wyłączania** - sekwencje stopowe nagrzewnic
5. **Scenariusze S0-S8** - tabele konfiguracji w zależności od temp. zewnętrznej
6. **UAR nagrzewnic** - regulatory PID zaworów wody grzewczej (Tz = 50°C)
7. **UAR wentylatorów** - regulatory PID prędkości (Ts = 2°C)

**Czas czytania:** ~60 minut  
**Dla kogo:** wszyscy użytkownicy systemu

## 🏗️ Architektura Podsystemów

```
┌─────────────────────────────────────────────────────────┐
│                    SYSTEM OGRZEWANIA                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ PARTS - Podsystem Automatycznej Regulacji     │    │
│  │         Temperatury Szybu                      │    │
│  │                                                 │    │
│  │  • Regulacja prędkości wentylatorów W1, W2    │    │
│  │  • Utrzymanie Ts = 2°C (na głębokości -30m)   │    │
│  │  • Algorytmy WS i RC (scenariusze + rotacja)   │    │
│  └────────────────────────────────────────────────┘    │
│                          ▼                              │
│  ┌────────────────────────────────────────────────┐    │
│  │ PARTPG - Podsystem Automatycznej Regulacji    │    │
│  │          Temperatury Powietrza Grzewczego      │    │
│  │                                                 │    │
│  │  • 8 × UAR zaworów (regulatory PID)           │    │
│  │  • Utrzymanie Tz = 50°C (wylot z nagrzewnicy) │    │
│  │  • Algorytm RN (rotacja nagrzewnic)           │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 🎯 Kluczowe Koncepcje

### Warstwa Regulacji vs Warstwa Zarządzania

**Warstwa Regulacji** (podstawowa funkcja):
- UAR nagrzewnic → utrzymanie Tz = 50°C
- UAR wentylatorów → utrzymanie Ts = 2°C
- Praca ciągła, realizacja w czasie rzeczywistym

**Warstwa Zarządzania** (optymalizacja):
- Algorytm WS → wybór scenariusza (ile nagrzewnic)
- Algorytm RC → rotacja układów (który ciąg)
- Algorytm RN → rotacja nagrzewnic (które konkretnie)

### Scenariusze Pracy (S0-S8)

System automatycznie dobiera konfigurację w zależności od temperatury zewnętrznej:

| Scenariusz | Temp. | Nagrzewnice | Ciągi |
|------------|-------|-------------|-------|
| S0 | ≥ 3°C | 0 | - |
| S1-S4 | 2°C do -11°C | 1-4 | Jeden (C1 lub C2) |
| S5-S8 | < -11°C | 5-8 | Dwa (C1 + C2) |

📊 [Wizualizacje scenariuszy](../../visualization/scenariusze/)

### Układy Pracy

**Układ Podstawowy:**
- Nawiew: +4,30m (wyrzutnia górna)
- Ciąg 1 aktywny (N1-N4 + W1)

**Układ Ograniczony:**
- Nawiew: +4,30m (przez spinę)
- Ciąg 2 aktywny (N5-N8 + W2)

## 🔗 Powiązane Dokumenty

- [Algorytmy](../02-algorytmy/README.md) - szczegóły algorytmów WS, RC, RN
- [Projekt Instalacji](../03-projekt-instalacji/) - schematy instalacji
- [Wizualizacje UAR](../../visualization/uar/) - schematy regulacji

## 📖 Dalsze Kroki

1. Przeczytaj [architektura.md](./architektura.md) - pełny opis systemu
2. Zapoznaj się z [algorytmami](../02-algorytmy/README.md)
3. Zobacz [wizualizacje scenariuszy](../../visualization/scenariusze/)

