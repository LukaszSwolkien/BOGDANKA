# Projekt Instalacji Ogrzewania Szybu

## 📁 Zawartość

### Katalog `schematy/`

Zawiera szczegółowe schematy instalacji grzewczej:

#### 📄 Dokumentacja
- `Projekt instalacji ogrzewania szybu.md` - szczegółowy opis instalacji

#### 🎨 Schematy SVG
- `nawiew_z_dolnego_ciagu_wentylacyjnego.svg` - schemat nawiewu z jednego ciągu
- `nawiew_z_dwoch_ciagow_wentylacyjnych.svg` - schemat nawiewu z dwóch ciągów
- `schemat_uar_nagrzewnica.svg` - schemat regulacji zaworu nagrzewnicy
- `schemat_uar_predkosc_wentylatora.svg` - schemat regulacji prędkości wentylatora

## 🏗️ Układ Instalacji

System składa się z:

### Ciąg 1 (C1)
- 4 nagrzewnice: N1, N2, N3, N4
- Wentylator: W1
- Wyrzutnia: +4,30m

### Ciąg 2 (C2)
- 4 nagrzewnice: N5, N6, N7, N8
- Wentylator: W2
- Wyrzutnia: +7,90m

### Elementy Wspólne
- Spinka ciągów (dla układu ograniczonego)
- Przepustnice regulacyjne
- Czujniki temperatury
- Zawory wody grzewczej

## 📊 Schematy Regulacji

### UAR Nagrzewnicy (Tz = 50°C)
Regulator PID steruje zaworem wody grzewczej:
- **Wejście:** temperatura powietrza na wylocie z nagrzewnicy
- **Wyjście:** pozycja zaworu (20-100%)
- **Setpoint:** 50°C

📄 `schematy/schemat_uar_nagrzewnica.svg`

### UAR Wentylatora (Ts = 2°C)
Regulator PID steruje częstotliwością wentylatora:
- **Wejście:** temperatura w szybie (na -30m)
- **Wyjście:** częstotliwość (25-50 Hz)
- **Setpoint:** 2°C

📄 `schematy/schemat_uar_predkosc_wentylatora.svg`

## 🔀 Układy Pracy

### Układ Podstawowy (S1-S8)
- Aktywny: Ciąg 1 (S1-S4) lub Ciąg 1 + Ciąg 2 (S5-S8)
- Nawiew: +4,30m (i +7,90m dla S5-S8)
- Spinka: zamknięta

📄 `schematy/nawiew_z_dolnego_ciagu_wentylacyjnego.svg`

### Układ Ograniczony (S1-S4)
- Aktywny: Ciąg 2
- Nawiew: przez spinę do +4,30m
- Spinka: otwarta

📄 `schematy/nawiew_z_dwoch_ciagow_wentylacyjnych.svg`

## 📋 Parametry Techniczne

### Nagrzewnice
- Ilość: 8 (N1-N8)
- Moc: *(do uzupełnienia)*
- Temperatura wody: *(do uzupełnienia)*
- Temperatura powietrza na wylocie: 50°C (regulowana)

### Wentylatory
- Ilość: 2 (W1, W2)
- Zakres częstotliwości: 25-50 Hz
- Tryby pracy: PID / MAX / OFF

### Przepustnice
- Ciąg 1: główna + kolektor
- Ciąg 2: główna + kolektor
- Spinka: regulacyjna
- Wyrzutnie: +4,30m, +7,90m

## 🔗 Powiązane Dokumenty

- [Architektura Systemu](../01-system/architektura.md) - opis podsystemów
- [Algorytmy](../02-algorytmy/README.md) - logika sterowania
- [Wizualizacje UAR](../visualization/uar/) - diagramy regulacji
- [Wizualizacje Scenariuszy](../visualization/scenariusze/) - konfiguracje nawiewu

## 📖 Dalsze Kroki

1. Przejrzyj [schematy instalacji](./schematy/)
2. Zapoznaj się z [algorytmami sterowania](../02-algorytmy/)
3. Zobacz [wizualizacje układów pracy](../visualization/scenariusze/)

