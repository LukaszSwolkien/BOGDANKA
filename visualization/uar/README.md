# Wizualizacje Układów Automatycznej Regulacji (UAR)

## 🎯 Schematy Regulacji

Ten katalog zawiera diagramy przedstawiające układy automatycznej regulacji (regulatory PID) w systemie.

## 📊 Dostępne Schematy

### `schemat-uar-nagrzewnica.svg`
**UAR Temperatury Powietrza na Wylocie z Nagrzewnicy**

#### Opis Regulatora
- **Typ:** PID (Proportional-Integral-Derivative)
- **Cel:** Utrzymanie temperatury Tz = 50°C na wylocie z nagrzewnicy
- **Wielkość regulowana:** Temperatura powietrza [°C]
- **Wielkość sterująca:** Pozycja zaworu wody grzewczej [%]

#### Schemat Blokowy
```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Setpoint  │────▶│  Regulator  │────▶│    Zawór     │
│  Tz = 50°C  │     │     PID     │     │   20-100%    │
└─────────────┘     └─────────────┘     └──────────────┘
                           ▲                     │
                           │                     ▼
                           │            ┌──────────────┐
                           │            │ Nagrzewnica  │
                           │            │ (wymiennik)  │
                           │            └──────────────┘
                           │                     │
                           │                     ▼
                    ┌──────────────┐    ┌──────────────┐
                    │   Czujnik    │◀───│  Powietrze   │
                    │ Temp. Tz     │    │  Grzewcze    │
                    └──────────────┘    └──────────────┘
```

#### Parametry
| Parametr | Wartość | Jednostka | Opis |
|----------|---------|-----------|------|
| **Setpoint** | 50 | °C | Temperatura zadana |
| **Zakres zaworu** | 20 - 100 | % | Min. 20% (ochrona antyzamrożeniowa) |
| **Czas próbkowania** | 1 - 5 | s | Częstotliwość działania regulatora |
| **Kp** | Do strojenia | - | Współczynnik proporcjonalny |
| **Ki** | Do strojenia | - | Współczynnik całkujący |
| **Kd** | Do strojenia | - | Współczynnik różniczkujący |

#### Zasada Działania
1. **Pomiar:** Czujnik mierzy temperaturę Tz na wylocie z nagrzewnicy
2. **Porównanie:** PID porównuje Tz z setpoint (50°C)
3. **Obliczenie:** PID oblicza uchyb i wyznacza korekcję
4. **Sterowanie:** PID reguluje zawór wody grzewczej (20-100%)
5. **Efekt:** Więcej wody → więcej ciepła → wyższa Tz

**Przykład:**
- Tz = 45°C (za nisko) → PID otwiera zawór → więcej gorącej wody → Tz rośnie
- Tz = 55°C (za wysoko) → PID przymyka zawór → mniej wody → Tz spada

📖 [Dokumentacja UAR Nagrzewnic](../../docs/01-system/architektura.md#6-uar-nagrzewnic)

---

### `schemat-uar-predkosc-wentylatora.svg`
**UAR Temperatury Szybu (Jeden Wentylator)**

#### Opis Regulatora
- **Typ:** PID
- **Cel:** Utrzymanie temperatury Ts = 2°C w szybie (na głębokości -30m)
- **Wielkość regulowana:** Temperatura w szybie [°C]
- **Wielkość sterująca:** Częstotliwość wentylatora [Hz]

#### Schemat Blokowy
```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Setpoint  │────▶│  Regulator  │────▶│  Wentylator  │
│  Ts = 2°C   │     │     PID     │     │   25-50 Hz   │
└─────────────┘     └─────────────┘     └──────────────┘
                           ▲                     │
                           │                     ▼
                           │            ┌──────────────┐
                           │            │  Nagrzewnice │
                           │            │  (grzewcze)  │
                           │            └──────────────┘
                           │                     │
                           │                     ▼
                    ┌──────────────┐    ┌──────────────┐
                    │   Czujnik    │◀───│     Szyb     │
                    │ Temp. Ts     │    │   (-30m)     │
                    │   (-30m)     │    │              │
                    └──────────────┘    └──────────────┘
```

#### Parametry
| Parametr | Wartość | Jednostka | Opis |
|----------|---------|-----------|------|
| **Setpoint** | 2 | °C | Temperatura zadana w szybie |
| **Zakres częstotliwości** | 25 - 50 | Hz | Zakres regulacji prędkości |
| **Czas próbkowania** | 5 - 10 | s | Częstotliwość działania regulatora |
| **Kp** | Do strojenia | - | Współczynnik proporcjonalny |
| **Ki** | Do strojenia | - | Współczynnik całkujący |
| **Kd** | Do strojenia | - | Współczynnik różniczkujący |

#### Zasada Działania
1. **Pomiar:** Czujnik mierzy temperaturę Ts w szybie (-30m)
2. **Porównanie:** PID porównuje Ts z setpoint (2°C)
3. **Obliczenie:** PID oblicza uchyb i wyznacza korekcję
4. **Sterowanie:** PID reguluje prędkość wentylatora (25-50 Hz)
5. **Efekt:** Większa prędkość → więcej gorącego powietrza → wyższa Ts

**Przykład:**
- Ts = 0°C (za zimno) → PID zwiększa prędkość → więcej powietrza → Ts rośnie
- Ts = 4°C (za ciepło) → PID zmniejsza prędkość → mniej powietrza → Ts spada

📖 [Dokumentacja UAR Wentylatorów](../../docs/01-system/architektura.md#7-uar-wentylatorów)

---

### `schemat-uar-predkosc-wentylatorow-w1-w2.svg`
**UAR Temperatury Szybu (Dwa Wentylatory)**

#### Opis Regulatora
- **Typ:** PID dla W2, MAX dla W1
- **Cel:** Utrzymanie Ts = 2°C w szybie (scenariusze S5-S8)
- **Wielkości regulowane:** Temperatura w szybie [°C]
- **Wielkości sterujące:** 
  - W1: 50 Hz (stała maksymalna)
  - W2: 25-50 Hz (regulowana)

#### Schemat Blokowy
```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Setpoint  │────▶│  Regulator  │────▶│ Wentylator   │
│  Ts = 2°C   │     │     PID     │     │  W2 25-50Hz  │
└─────────────┘     └─────────────┘     └──────────────┘
                           ▲                     │
                           │                     ▼
                    ┌──────────────┐    ┌──────────────┐
                    │   Czujnik    │    │ Wentylator   │
                    │ Temp. Ts     │    │  W1 = 50Hz   │
                    │   (-30m)     │    │   (MAX)      │
                    └──────────────┘    └──────────────┘
                           ▲                     │
                           │                     ▼
                           │            ┌──────────────┐
                           └────────────│     Szyb     │
                                        │   (-30m)     │
                                        └──────────────┘
```

#### Charakterystyka
- **W1:** Pracuje na maksymalnej mocy (50 Hz) - zapewnia bazowy przepływ
- **W2:** Reguluje prędkość (25-50 Hz) - dostosowuje temperaturę

#### Kiedy Jest Używany?
**Scenariusze S5-S8** (temp. zewnętrzna < -11°C):
- Oba ciągi aktywne
- C1: 4 nagrzewnice + W1 MAX
- C2: 1-4 nagrzewnice + W2 PID

**Dlaczego W1 na MAX?**
- Ciąg 1 pracuje z pełną mocą (wszystkie N1-N4)
- Maksymalny przepływ przez C1
- W2 "dokłada" tyle ile potrzeba

📖 [Scenariusze S5-S8](../../docs/01-system/architektura.md#5-scenariusze)

---

## 🎓 Zrozumienie Regulacji PID

### Czym Jest PID?

**PID** to regulator proporcjonalno-całkująco-różniczkujący:

```
u(t) = Kp·e(t) + Ki·∫e(t)dt + Kd·de(t)/dt

gdzie:
- u(t) = sygnał sterujący (np. pozycja zaworu)
- e(t) = uchyb (różnica: setpoint - wartość mierzona)
- Kp, Ki, Kd = nastawy regulatora
```

### Składowe Regulatora

#### Składowa P (Proporcjonalna)
- Reaguje na **aktualny** uchyb
- Im większy uchyb, tym silniejsza reakcja
- **Szybka** ale może oscylować

**Przykład:** Ts = 0°C, setpoint = 2°C → uchyb = 2°C → mocne otwarcie zaworu

#### Składowa I (Całkująca)
- Reaguje na **skumulowany** uchyb w czasie
- Eliminuje uchyb ustalony
- **Powolna** ale dokładna

**Przykład:** Długo Ts = 1.8°C (mały stały uchyb 0.2°C) → I stopniowo zwiększa sterowanie

#### Składowa D (Różniczkująca)
- Reaguje na **szybkość zmian** uchybu
- Tłumi oscylacje
- **Stabilizuje** system

**Przykład:** Ts szybko spada z 2°C do 1°C → D mocno zwiększa sterowanie

### Strojenie PID

Parametry Kp, Ki, Kd muszą być **dostrojone** dla każdego układu:

| Parametr | Za mały | Optymalny | Za duży |
|----------|---------|-----------|---------|
| **Kp** | Wolna reakcja | Szybka i stabilna | Oscylacje |
| **Ki** | Uchyb ustalony | Dokładność | Niestabilność |
| **Kd** | Oscylacje | Tłumienie | Czułość na zakłócenia |

**Metody strojenia:**
1. Metoda Zieglera-Nicholsa
2. Strojenie eksperymentalne
3. Autotuning (wbudowany w PLC)

## 🔗 Powiązana Dokumentacja

- [Architektura - UAR Nagrzewnic](../../docs/01-system/architektura.md#6-uar-nagrzewnic)
- [Architektura - UAR Wentylatorów](../../docs/01-system/architektura.md#7-uar-wentylatorów)
- [Scenariusze S0-S8](../../docs/01-system/architektura.md#5-scenariusze)
- [Wizualizacje Scenariuszy](../scenariusze/)

## 🛠️ Dla Programistów PLC

### Implementacja PID

Większość PLC ma **wbudowane bloki funkcyjne PID**:

**Siemens TIA Portal:**
```
PID_Compact (FB)
- Setpoint (Real)
- Input (Real) 
- Output (Real)
- Kp, Ki, Kd (Real)
```

**Beckhoff TwinCAT:**
```
FB_CTRL_PID (Function Block)
```

**Schneider Unity Pro:**
```
PID_REG (EFB)
```

### Parametry Konfiguracyjne

| Element | Parametr | Opis |
|---------|----------|------|
| **Nagrzewnica** | `Tz_Setpoint` | 50°C |
| | `Tz_Min` | 0°C |
| | `Tz_Max` | 80°C |
| | `Zawor_Min` | 20% |
| | `Zawor_Max` | 100% |
| **Wentylator** | `Ts_Setpoint` | 2°C |
| | `Ts_Min` | -5°C |
| | `Ts_Max` | 10°C |
| | `Freq_Min` | 25 Hz |
| | `Freq_Max` | 50 Hz |

## 🎨 Konwencje Wizualne

### Bloki Funkcyjne
- 🟦 **Niebieski prostokąt:** regulator PID
- 🟩 **Zielony prostokąt:** element wykonawczy (zawór, wentylator)
- 🟨 **Żółty prostokąt:** obiekt regulowany (nagrzewnica, szyb)
- ⚪ **Biały okrąg:** czujnik pomiarowy

### Strzałki
- **Gruba czarna:** główny sygnał (pomiar, sterowanie)
- **Cienka czarna:** sygnał pomocniczy
- **Kropkowana:** sprzężenie zwrotne

### Oznaczenia
- **Tz:** Temperatura powietrza na wylocie z nagrzewnicy [°C]
- **Ts:** Temperatura w szybie na głębokości -30m [°C]
- **PID:** Regulator proporcjonalno-całkująco-różniczkujący
- **Hz:** Hertz - jednostka częstotliwości wentylatora

