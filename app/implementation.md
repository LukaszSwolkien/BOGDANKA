# Wytyczne Implementacji - Aplikacja Symulacji Systemu BOGDANKA Szyb 2

## 1. Przegląd Projektu

### 1.1 Cel Aplikacji
Aplikacja webowa symulująca w czasie rzeczywistym system automatycznej regulacji (SAR) temperatury szybu kopalnianego BOGDANKA Szyb 2, obejmująca:
- 8 nagrzewnic (N1-N8) w dwóch ciągach wentylacyjnych
- 2 wentylatory (W1, W2) ze sterowaniem częstotliwościowym
- 9 scenariuszy pracy (S0-S8) zależnych od temperatury zewnętrznej
- Algorytm 5A: cykliczna rotacja układów pracy ciągów
- Algorytm 5B: cykliczna rotacja nagrzewnic w obrębie ciągu
- Regulatory PID dla temperatury powietrza i prędkości wentylatorów

### 1.2 Wymagania Techniczne
- **Backend:** Node.js (wersja 18.x lub wyższa)
- **Frontend:** Vanilla JavaScript + HTML5 + CSS3
- **Komunikacja:** WebSocket (dla real-time updates)
- **Zależności minimalne:** Express.js, ws (WebSocket)
- **Brak frameworków frontend:** React/Vue/Angular - nie używać
- **Baza danych:** Opcjonalnie JSON file store dla historii (bez zewnętrznej DB)

### 1.3 Architektura Aplikacji

```
┌─────────────────────────────────────────────────────────────┐
│                     PRZEGLĄDARKA (Client)                    │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │  Panel HMI │  │  Formularz   │  │  Wykresy/Trendy  │    │
│  │  (SVG)     │  │  Konfiguracji│  │                  │    │
│  └────────────┘  └──────────────┘  └──────────────────┘    │
│         ↕                ↕                    ↕              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          WebSocket Client (real-time)               │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────┘
                               │ WebSocket
┌──────────────────────────────┴──────────────────────────────┐
│                    NODE.JS SERVER                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          WebSocket Server (ws)                      │    │
│  └─────────────────────────────────────────────────────┘    │
│         ↕                ↕                    ↕              │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │  Silnik    │  │  Algorytmy   │  │  System          │    │
│  │  Symulacji │  │  Rotacji     │  │  Alarmów         │    │
│  │  (PLC)     │  │  (5A + 5B)   │  │                  │    │
│  └────────────┘  └──────────────┘  └──────────────────┘    │
│         ↕                ↕                    ↕              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          Model Danych (State Manager)               │    │
│  └─────────────────────────────────────────────────────┘    │
│         ↕                                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          Historia/Logger (JSON File)                │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Struktura Projektu

```
bogdanka-simulation/
│
├── server/
│   ├── index.js                    # Główny plik serwera
│   ├── config/
│   │   └── default-config.js       # Domyślne parametry systemu
│   ├── simulation/
│   │   ├── SimulationEngine.js     # Główny silnik symulacji (1s tick)
│   │   ├── SystemState.js          # Model stanu systemu
│   │   ├── ScenarioManager.js      # Zarządzanie scenariuszami S0-S8
│   │   ├── PIDController.js        # Implementacja regulatora PID
│   │   └── AlarmSystem.js          # System alarmów
│   ├── controllers/
│   │   ├── HeaterController.js     # Kontroler nagrzewnic (UAR N1-N8)
│   │   ├── FanController.js        # Kontroler wentylatorów (UAR W1-W2)
│   │   └── DamperController.js     # Kontroler przepustnic
│   ├── algorithms/
│   │   ├── Rotation5A.js           # Algorytm rotacji układów
│   │   └── Rotation5B.js           # Algorytm rotacji nagrzewnic
│   ├── utils/
│   │   ├── Logger.js               # Logger zdarzeń
│   │   ├── Validator.js            # Walidacja parametrów
│   │   └── Helpers.js              # Funkcje pomocnicze
│   └── data/
│       ├── history.json            # Historia symulacji
│       └── events.json             # Log zdarzeń
│
├── client/
│   ├── index.html                  # Strona główna
│   ├── css/
│   │   ├── main.css                # Główne style
│   │   ├── hmi.css                 # Style panelu HMI
│   │   └── forms.css               # Style formularzy
│   ├── js/
│   │   ├── app.js                  # Główna logika aplikacji klienckiej
│   │   ├── WebSocketClient.js      # Klient WebSocket
│   │   ├── HMIRenderer.js          # Renderer panelu HMI
│   │   ├── ConfigForm.js           # Formularz konfiguracji
│   │   ├── ChartRenderer.js        # Wykresy trendów
│   │   └── AlarmPanel.js           # Panel alarmów
│   └── assets/
│       └── svg/                    # Kopiowane z Symulacja/
│
├── shared/
│   └── constants.js                # Wspólne stałe (client + server)
│
├── tests/
│   ├── pid.test.js                 # Testy regulatora PID
│   ├── rotation5a.test.js          # Testy algorytmu 5A
│   └── rotation5b.test.js          # Testy algorytmu 5B
│
├── package.json
├── README.md
└── .gitignore
```

---

## 3. Model Danych

### 3.1 Stan Systemu (SystemState)

```javascript
{
  // Parametry wejściowe
  input: {
    t_zewn: -5.0,              // Temperatura zewnętrzna [°C]
    t_wody_grzewczej: 80.0,    // Temp. wody grzewczej [°C]
    woda_przeplyw_ok: true      // Status przepływu wody
  },
  
  // Konfiguracja
  config: {
    tryb: "AUTO",               // AUTO | MANUAL
    scenariusz_manual: null,    // Dla trybu MANUAL
    Tz: 50.0,                   // Temp. zadana nagrzewnicy [°C]
    Ts: 2.0,                    // Temp. zadana w szybie [°C]
    Pzmin: 20,                  // Min otwarcie zaworu [%]
    Pzmax: 100,                 // Max otwarcie zaworu [%]
    NWmin: 25,                  // Min częstotliwość [Hz]
    NWmax: 50,                  // Max częstotliwość [Hz]
    
    // Parametry rotacji
    OKRES_ROTACJI_UKLADOW: 168 * 3600,      // [sekundy]
    OKRES_ROTACJI_NAGRZEWNIC: 168 * 3600,   // [sekundy]
    rotacja_5A_enabled: true,
    rotacja_5B_enabled: true,
    
    // Nastawy PID (dla nagrzewnic)
    pid_heaters: { Kp: 2.0, Ki: 0.1, Kd: 0.05 },
    // Nastawy PID (dla wentylatorów)
    pid_fans: { Kp: 1.5, Ki: 0.08, Kd: 0.03 }
  },
  
  // Stan scenariusza
  scenario: {
    current: "S3",              // S0-S8
    uklad_pracy: "Podstawowy",  // Podstawowy | Ograniczony
    active_ciag: "C1",          // C1 | C2 | "C1+C2"
    required_heaters: 3,        // Ilość wymaganych nagrzewnic
    temp_range: { min: -8, max: -4 },
    temp_wyl: -3,               // Temp. wyłączenia [°C]
    histereza: 1                // Histereza [°C]
  },
  
  // Nagrzewnice N1-N8
  heaters: [
    {
      id: "N1",
      ciag: "C1",
      active: true,             // Czy pracuje
      sprawna: true,            // Gotowość operacyjna
      temp_wylot: 48.5,         // Temperatura na wylocie [°C]
      zawor_pozycja: 65,        // Pozycja zaworu [%]
      przepustnica_dolot: true, // Otwarta/zamknięta
      pid_mode: "AUTO",         // AUTO | MANUAL
      pid_cv: 65,               // Control Variable [%]
      czas_pracy: 12500,        // Łączny czas pracy [s]
      czas_postoju: 3600,       // Łączny czas postoju [s]
      liczba_zalaczeń: 15,      // Licznik startów
      ostatnie_zalaczenie: 1637512800  // Timestamp
    },
    // ... N2-N8
  ],
  
  // Wentylatory W1-W2
  fans: [
    {
      id: "W1",
      ciag: "C1",
      active: true,
      sprawny: true,
      czestotliwosc: 45,        // [Hz]
      prad: 125,                // [A]
      pid_mode: "AUTO",         // AUTO | MANUAL | MAX
      pid_cv: 45,               // Control Variable [Hz]
      czas_pracy: 50000         // [s]
    },
    {
      id: "W2",
      ciag: "C2",
      active: false,
      sprawny: true,
      czestotliwosc: 0,
      prad: 0,
      pid_mode: "OFF",
      pid_cv: 0,
      czas_pracy: 25000
    }
  ],
  
  // Przepustnice
  dampers: {
    spinka_ciagow: false,       // Spinka między C1-C2
    kolektor_C1: true,
    kolektor_C2: false,
    wyrzutnia_430: true,
    wyrzutnia_790: false
  },
  
  // Temperatura w szybie
  shaft_temp: {
    poziom_minus30: 2.1,        // [°C]
    pozom_plus430: 15.0,        // [°C]
    poziom_plus790: 18.0        // [°C]
  },
  
  // Rotacja 5A
  rotation_5A: {
    aktualny_uklad: "Podstawowy",
    czas_ostatniej_zmiany: 1637500000,  // Timestamp
    czas_pracy_podstawowy: 150000,      // [s]
    czas_pracy_ograniczony: 145000,     // [s]
    liczba_rotacji: 8,
    nastepna_rotacja_za: 18000          // [s]
  },
  
  // Rotacja 5B
  rotation_5B: {
    C1: {
      czas_ostatniej_rotacji: 1637510000,
      nastepna_rotacja_za: 12000,
      liczba_rotacji: 5,
      kolejka_nagrzewnic: ["N1", "N2", "N3", "N4"]  // Sorted by czas_pracy
    },
    C2: {
      czas_ostatniej_rotacji: 1637508000,
      nastepna_rotacja_za: 14000,
      liczba_rotacji: 3,
      kolejka_nagrzewnic: ["N5", "N6", "N7", "N8"]
    }
  },
  
  // Alarmy
  alarms: [
    {
      id: "ALM001",
      type: "CRITICAL",         // CRITICAL | WARNING | INFO
      message: "Temperatura N3 poniżej 40°C",
      timestamp: 1637512900,
      acknowledged: false
    }
  ],
  
  // Statystyki
  stats: {
    simulation_time: 125000,    // Łączny czas symulacji [s]
    system_uptime: 124500,      // Czas pracy systemu [s]
    total_energy: 1250.5        // Łączna energia [kWh]
  }
}
```

---

## 4. Implementacja Kluczowych Komponentów

### 4.1 Silnik Symulacji (SimulationEngine.js)

**Główna pętla:**
- Wykonywana co **1 sekundę** (setInterval 1000ms)
- Krok symulacji:
  1. Odczyt temperatury zewnętrznej (t_zewn)
  2. Określenie scenariusza (ScenarioManager)
  3. Aktualizacja stanu nagrzewnic (HeaterController)
  4. Aktualizacja stanu wentylatorów (FanController)
  5. Regulacja PID dla nagrzewnic
  6. Regulacja PID dla wentylatorów
  7. Symulacja temperatury w szybie (model uproszczony)
  8. Sprawdzenie warunków rotacji 5A
  9. Sprawdzenie warunków rotacji 5B
  10. Sprawdzenie alarmów
  11. Aktualizacja liczników czasu
  12. Wysłanie stanu przez WebSocket do klientów

**Metody:**
```javascript
class SimulationEngine {
  constructor(config) { ... }
  start() { ... }               // Uruchomienie symulacji
  stop() { ... }                // Zatrzymanie
  tick() { ... }                // Pojedynczy krok (1s)
  updateConfig(newConfig) { ... }
  getState() { ... }            // Pobranie aktualnego stanu
  reset() { ... }               // Reset symulacji
}
```

### 4.2 Regulator PID (PIDController.js)

**Algorytm PID:**
```
e(t) = SP - PV                  // Uchyb
P = Kp * e(t)                   // Proporcjonalny
I += Ki * e(t) * dt             // Całkowy
D = Kd * (e(t) - e(t-1)) / dt   // Różniczkowy
CV = P + I + D                  // Control Variable
```

**Anty-windup:** Ograniczenie całki I do zakresu [CV_min, CV_max]

**Metody:**
```javascript
class PIDController {
  constructor(Kp, Ki, Kd, min, max) { ... }
  compute(setpoint, processValue, deltaTime) { ... }
  reset() { ... }
  setTunings(Kp, Ki, Kd) { ... }
}
```

### 4.3 Zarządzanie Scenariuszami (ScenarioManager.js)

**Tablica scenariuszy:**
```javascript
const SCENARIOS = [
  { 
    id: "S0", 
    temp_min: 3, 
    temp_max: Infinity, 
    heaters: 0, 
    W1_mode: "OFF", 
    W2_mode: "OFF",
    temp_wyl: null,
    histereza: 0
  },
  { 
    id: "S1", 
    temp_min: -1, 
    temp_max: 2, 
    heaters: 1, 
    W1_mode: "PID", 
    W2_mode: "OFF",
    temp_wyl: 3,
    histereza: 1
  },
  // ... S2-S8
];
```

**Logika z histerezą:**
- Załączenie scenariusza gdy: `t_zewn ≤ temp_max`
- Wyłączenie scenariusza gdy: `t_zewn ≥ temp_wyl`
- Zapobiega oscylacjom przy granicznych temperaturach

### 4.4 Algorytm 5A - Rotacja Układów (Rotation5A.js)

**Pseudokod (z dokumentacji):**
```javascript
class Rotation5A {
  check(state) {
    // Krok 1: Sprawdź warunki rotacji
    if (!this.canRotate(state)) return null;
    
    // Krok 2: Sprawdź okres rotacji
    if (!this.isPeriodElapsed(state)) return null;
    
    // Krok 3: Określ nowy układ
    const newUklad = state.rotation_5A.aktualny_uklad === "Podstawowy" 
      ? "Ograniczony" 
      : "Podstawowy";
    
    return { action: "CHANGE_UKLAD", uklad: newUklad };
  }
  
  execute(state, newUklad) {
    if (newUklad === "Ograniczony") {
      return this.switchToOgraniczony(state);
    } else {
      return this.switchToPodstawowy(state);
    }
  }
  
  switchToOgraniczony(state) {
    // Sekwencja przełączenia (10 kroków z opóźnieniami)
    return {
      steps: [
        { action: "STOP_HEATERS_C1", delay: 30 },
        { action: "STOP_FAN_W1", delay: 10 },
        { action: "OPEN_DAMPER_SPINKA", delay: 10 },
        { action: "CLOSE_DAMPER_C1_KOLEKTOR", delay: 0 },
        { action: "CLOSE_DAMPER_WYRZUTNIA_790", delay: 0 },
        { action: "START_FAN_W2", freq: 25, delay: 10 },
        { action: "START_HEATERS_C2", count: required, delay: 30 },
        { action: "ACTIVATE_PID_W2", delay: 0 }
      ]
    };
  }
}
```

**Uwaga:** Sekwencja zmiany układu wymaga **automatu stanów** (state machine), ponieważ każdy krok ma opóźnienie czasowe.

### 4.5 Algorytm 5B - Rotacja Nagrzewnic (Rotation5B.js)

**Pseudokod:**
```javascript
class Rotation5B {
  check(state, ciag) {
    // Krok 1: Aktualizuj liczniki czasu
    this.updateCounters(state, ciag);
    
    // Krok 2: Sprawdź warunki rotacji
    if (!this.canRotate(state, ciag)) return null;
    
    // Krok 3: Wybierz nagrzewnice
    const heaterToStop = this.findLongestRunning(state, ciag);
    const heaterToStart = this.findLongestIdle(state, ciag);
    
    if (!heaterToStop || !heaterToStart) return null;
    
    // Krok 4: Sprawdź delta czasu
    const delta = heaterToStop.czas_pracy - heaterToStart.czas_postoju;
    if (delta < MIN_DELTA_CZASU) return null;
    
    return { 
      action: "ROTATE_HEATER", 
      ciag, 
      stop: heaterToStop.id, 
      start: heaterToStart.id 
    };
  }
  
  execute(state, stopId, startId) {
    // Sekwencja rotacji (7 kroków)
    return {
      steps: [
        { action: "CHECK_READINESS", heater: startId },
        { action: "SET_VALVE", heater: startId, value: 20 },
        { action: "OPEN_DAMPER", heater: startId },
        { action: "RAMP_VALVE_UP", heater: startId, to: 100, duration: 16 },
        { action: "ACTIVATE_PID", heater: startId },
        { action: "WAIT_STABILIZATION", duration: 30 },
        { action: "CHECK_TEMP", heater: startId, expected: 50, tolerance: 5 },
        { action: "DEACTIVATE_PID", heater: stopId },
        { action: "RAMP_VALVE_DOWN", heater: stopId, to: 20, duration: 16 },
        { action: "CLOSE_DAMPER", heater: stopId }
      ]
    };
  }
}
```

### 4.6 Symulacja Temperatury w Szybie

**Model uproszczony (brak CFD):**
```javascript
function simulateShaftTemperature(state, deltaTime) {
  // Parametry modelu
  const THERMAL_MASS = 50000;      // Masa termiczna szybu [J/K]
  const HEAT_LOSS = 0.05;          // Straty ciepła [W/K]
  
  // Oblicz moc grzewczą z aktywnych nagrzewnic
  let totalHeatPower = 0;
  state.heaters.forEach(heater => {
    if (heater.active) {
      const efficiency = heater.zawor_pozycja / 100;
      totalHeatPower += 100000 * efficiency;  // 100 kW max na nagrzewnicę
    }
  });
  
  // Oblicz przepływ powietrza z wentylatorów
  let totalAirflow = 0;
  state.fans.forEach(fan => {
    if (fan.active) {
      totalAirflow += (fan.czestotliwosc / 50) * 10;  // m³/s
    }
  });
  
  // Bilans cieplny (uproszczony)
  const heatIn = totalHeatPower * deltaTime;
  const heatOut = HEAT_LOSS * (state.shaft_temp.poziom_minus30 - state.input.t_zewn) * deltaTime;
  
  // Zmiana temperatury
  const deltaTemp = (heatIn - heatOut) / THERMAL_MASS;
  
  return state.shaft_temp.poziom_minus30 + deltaTemp;
}
```

**Uwaga:** To jest bardzo uproszczony model. Rzeczywisty system wymaga modelu CFD lub identyfikacji obiektu.

---

## 5. Komunikacja Client-Server

### 5.1 Protokół WebSocket

**Rodzaje wiadomości (Client → Server):**

```javascript
// 1. Zmiana konfiguracji
{
  type: "CONFIG_UPDATE",
  payload: {
    tryb: "AUTO",
    Tz: 50,
    OKRES_ROTACJI_UKLADOW: 604800,
    // ...
  }
}

// 2. Sterowanie ręczne (tryb MANUAL)
{
  type: "MANUAL_CONTROL",
  payload: {
    heater: "N3",
    zawor_pozycja: 75
  }
}

// 3. Kwituowanie alarmu
{
  type: "ALARM_ACK",
  payload: {
    alarmId: "ALM001"
  }
}

// 4. Start/Stop symulacji
{
  type: "SIMULATION_CONTROL",
  payload: {
    action: "START" | "STOP" | "RESET"
  }
}

// 5. Zmiana temperatury zewnętrznej (symulacja)
{
  type: "SET_T_ZEWN",
  payload: {
    t_zewn: -12.5
  }
}
```

**Rodzaje wiadomości (Server → Client):**

```javascript
// 1. Aktualizacja stanu (co 1s)
{
  type: "STATE_UPDATE",
  payload: {
    timestamp: 1637512900,
    ...systemState  // Cały stan systemu
  }
}

// 2. Nowy alarm
{
  type: "NEW_ALARM",
  payload: {
    alarm: { id, type, message, timestamp }
  }
}

// 3. Zdarzenie rotacji
{
  type: "ROTATION_EVENT",
  payload: {
    algorithm: "5A" | "5B",
    event: "STARTED" | "COMPLETED" | "FAILED",
    details: { ... }
  }
}

// 4. Błąd konfiguracji
{
  type: "ERROR",
  payload: {
    message: "Invalid parameter: Tz must be > 0"
  }
}
```

### 5.2 REST API (opcjonalnie)

Dla operacji które nie wymagają real-time:

```
GET  /api/config          # Pobranie konfiguracji
POST /api/config          # Zapisanie konfiguracji
GET  /api/history         # Historia symulacji
GET  /api/events          # Log zdarzeń
POST /api/export          # Export danych do CSV
```

---

## 6. Interfejs Użytkownika (Frontend)

### 6.1 Główne Widoki

**A. Panel HMI (Synoptyczny)**
- Dynamiczne ładowanie SVG z katalogu `assets/svg/`
- Kolorowanie elementów według stanu:
  - Nagrzewnice: zielony (aktywne), szary (nieaktywne), czerwony (awaria)
  - Zawory: wyświetlenie pozycji w % 
  - Wentylatory: wyświetlenie częstotliwości Hz
  - Przepustnice: O (otwarta) / Z (zamknięta)
- Animacje przepływu (opcjonalnie)
- Wyświetlenie aktualnego scenariusza (S0-S8)
- Przełącznik trybu AUTO/MANUAL

**B. Formularz Konfiguracji**

Sekcje:
1. **Temperatury zadane:**
   - Tz (temp. nagrzewnicy): [30-70°C]
   - Ts (temp. w szybie): [-5 - +10°C]

2. **Zakresy regulacji:**
   - Pzmin, Pzmax (zawory): [0-100%]
   - NWmin, NWmax (wentylatory): [20-50 Hz]

3. **Parametry PID nagrzewnic:**
   - Kp: [0.1 - 10]
   - Ki: [0.01 - 1]
   - Kd: [0 - 1]

4. **Parametry PID wentylatorów:**
   - Kp: [0.1 - 10]
   - Ki: [0.01 - 1]
   - Kd: [0 - 1]

5. **Rotacja 5A:**
   - Włącz/Wyłącz
   - OKRES_ROTACJI_UKŁADÓW: [24h - 720h]

6. **Rotacja 5B:**
   - Włącz/Wyłącz
   - OKRES_ROTACJI_NAGRZEWNIC: [24h - 720h]
   - MIN_DELTA_CZASU: [1h - 24h]

7. **Symulacja:**
   - Temperatura zewnętrzna: [-30°C - +10°C]
   - Prędkość symulacji: [1x, 10x, 100x, 1000x]
   - Scenariusz automatyczny / ręczny

8. **Sprawność urządzeń:**
   - Checkboxy dla N1-N8 (sprawna/niesprawna)
   - Checkboxy dla W1-W2

**Walidacja:**
- Real-time walidacja pól
- Wyświetlanie błędów pod polami
- Blokada zapisu przy błędach

**C. Wykresy/Trendy**

Wyświetlane parametry (ostatnie 24h symulacji):
1. Temperatura zewnętrzna (t_zewn)
2. Temperatura w szybie (T_szyb) vs Ts (setpoint)
3. Temperatury nagrzewnic N1-N8 (8 linii)
4. Pozycje zaworów N1-N8 (8 linii)
5. Częstotliwości W1, W2
6. Scenariusz (S0-S8) - wykres schodkowy
7. Układ pracy (Podstawowy/Ograniczony)

**Implementacja wykresów:**
- Użycie Canvas API (bez bibliotek)
- Lub minimalna biblioteka: Chart.js (jeśli konieczne)
- Aktualizacja co 1s (nowy punkt danych)
- Zoom, pan (opcjonalnie)

**D. Panel Alarmów**

- Lista alarmów (ostatnie 50)
- Filtrowanie: CRITICAL / WARNING / INFO
- Sortowanie: najnowsze na górze
- Kwituowanie alarmów (przycisk ACK)
- Dźwięk przy nowym alarmie krytycznym

**E. Logi/Historia**

- Log zdarzeń (ostatnie 100):
  - Zmiana scenariusza
  - Rotacja 5A
  - Rotacja 5B
  - Załączenia/wyłączenia nagrzewnic
  - Zmiany trybu AUTO/MANUAL
- Timestampy
- Export do CSV

**F. Panel Rotacji**

Zakładki: **5A** | **5B**

**Rotacja 5A:**
- Aktualny układ: Podstawowy / Ograniczony
- Czas do następnej rotacji: XXX h
- Czas pracy C1: XXX h
- Czas pracy C2: XXX h
- Stosunek C1/C2: X.XX
- Wykres: histogram czasu pracy C1 vs C2
- Historia rotacji (tabela)

**Rotacja 5B:**
- Tabela dla C1 i C2:
  - Nagrzewnica | Czas pracy [h] | Czas postoju [h] | Liczba załączeń
  - Sortowanie po czasie pracy
- Czas do następnej rotacji C1: XXX h
- Czas do następnej rotacji C2: XXX h
- Wykres słupkowy: czasy pracy N1-N8
- Historia rotacji (tabela)

### 6.2 Responsywność

- Desktop: >= 1920x1080
- Tablet: >= 1024x768
- Mobile: >= 768x1024 (pionowo)

Layout:
- Desktop: Panel HMI po lewej (70%), Panel sterowania po prawej (30%)
- Tablet/Mobile: Stack layout (HMI na górze, sterowanie poniżej)

---

## 7. Testowanie

### 7.1 Testy Jednostkowe

**Moduły do przetestowania:**
1. PIDController.js
   - Test stabilności
   - Test anty-windup
   - Test zmiany nastaw

2. ScenarioManager.js
   - Test wyboru scenariusza
   - Test histerezy
   - Test przejść między scenariuszami

3. Rotation5A.js
   - Test warunków rotacji
   - Test sekwencji przełączenia

4. Rotation5B.js
   - Test wyboru nagrzewnic
   - Test delta czasu
   - Test sekwencji rotacji

5. Validator.js
   - Test walidacji parametrów

### 7.2 Testy Integracyjne

**Scenariusze testowe:**

1. **Test pełnego cyklu:**
   - Start symulacji w S0
   - Spadek temperatury S0 → S1 → S2 → ... → S8
   - Wzrost temperatury S8 → S7 → ... → S0
   - Sprawdzenie histerezy

2. **Test rotacji 5A:**
   - Ustawienie okresu 60s (zamiast 168h)
   - Obserwacja przełączenia Podstawowy → Ograniczony → Podstawowy
   - Sprawdzenie liczników czasu

3. **Test rotacji 5B:**
   - Scenariusz S3 (3 nagrzewnice)
   - Okres 60s
   - Obserwacja 4 rotacji (pełny cykl)
   - Sprawdzenie równomierności

4. **Test awaryjny:**
   - Symulacja awarii nagrzewnicy podczas pracy
   - Sprawdzenie alarmu
   - Sprawdzenie przełączenia na rezerwową

5. **Test trybu MANUAL:**
   - Przełączenie AUTO → MANUAL
   - Ręczne sterowanie zaworem
   - Przełączenie MANUAL → AUTO (bumpless transfer)

### 7.3 Testy Akceptacyjne

**Kryteria:**
- Symulacja działa stabilnie przez min. 24h czasu rzeczywistego
- Brak memory leaks (Node.js)
- Wydajność: < 5% CPU przy 1 kliencie
- WebSocket latency < 100ms
- Poprawność algorytmów zgodnie z dokumentacją

---

## 8. Optymalizacje

### 8.1 Wydajność Backendu

1. **Throttling aktualizacji:**
   - Stan pełny: co 1s
   - Stan częściowy (tylko zmiany): co 100ms

2. **Kompresja danych WebSocket:**
   - Opcja: włączenie permessage-deflate

3. **Historia danych:**
   - Przechowywanie ostatnich 24h w pamięci
   - Starsze dane: zapis do pliku JSON
   - Rotacja plików co tydzień

### 8.2 Wydajność Frontendu

1. **Renderowanie HMI:**
   - Aktualizacja tylko zmienionych elementów SVG
   - Użycie requestAnimationFrame dla animacji

2. **Wykresy:**
   - Downsampling danych (jeśli > 1000 punktów)
   - Lazy loading historii

3. **Debouncing:**
   - Inputy w formularzu: debounce 500ms

---

## 9. Deployment

### 9.1 Uruchomienie Lokalne

```bash
# Instalacja zależności
npm install

# Uruchomienie serwera (development)
npm run dev

# Uruchomienie serwera (production)
npm start

# Uruchomienie testów
npm test
```

### 9.2 Zmienne Środowiskowe

```
PORT=3000                    # Port serwera HTTP
WS_PORT=3001                 # Port WebSocket (opcjonalnie ten sam)
LOG_LEVEL=info               # debug | info | warn | error
HISTORY_RETENTION=24         # Ilość godzin historii w pamięci
SIMULATION_SPEED=1           # Prędkość symulacji (1x domyślnie)
```

### 9.3 Docker (opcjonalnie)

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

---

## 10. Dokumentacja dla Użytkownika

### 10.1 Quick Start Guide

**README.md:**
1. Instalacja Node.js
2. Klonowanie repozytorium
3. Instalacja zależności
4. Uruchomienie aplikacji
5. Otwarcie przeglądarki: http://localhost:3000
6. Podstawowa konfiguracja

### 10.2 User Manual

**Dokumentacja interfejsu:**
- Opis paneli HMI
- Jak konfigurować parametry
- Jak interpretować wykresy
- Jak reagować na alarmy
- Przykłady scenariuszy

### 10.3 Technical Documentation

**Dokumentacja algorytmów:**
- Opis implementacji PID
- Opis implementacji rotacji 5A
- Opis implementacji rotacji 5B
- Model symulacji temperatury
- API Reference (WebSocket, REST)

---

## 11. Roadmap (Rozszerzenia)

### Faza 2 (opcjonalnie):
1. **Zapis konfiguracji:**
   - Możliwość zapisania wielu konfiguracji (presets)
   - Import/Export konfiguracji JSON

2. **Porównywanie scenariuszy:**
   - Side-by-side comparison dwóch symulacji

3. **Optymalizacja nastaw PID:**
   - Automatyczny tuning (Ziegler-Nichols, Cohen-Coon)

4. **Baza danych:**
   - PostgreSQL / SQLite dla historii
   - Zapytania SQL dla raportów

5. **Autentykacja:**
   - Login/logout
   - Role: Operator / Inżynier / Admin

6. **Multi-tenancy:**
   - Wiele symulacji równocześnie
   - Izolacja sesji

---

## 12. Podsumowanie Stack Technologiczny

| Warstwa | Technologia | Uzasadnienie |
|---------|-------------|--------------|
| **Backend** | Node.js 18+ | Wymaganie projektowe |
| **Framework HTTP** | Express.js | Minimalna, popularna biblioteka |
| **WebSocket** | ws | Lekka biblioteka WebSocket |
| **Frontend** | Vanilla JS + HTML5 + CSS3 | Brak zależności, maksymalna kontrola |
| **SVG Rendering** | Natywne API przeglądarki | Istniejące pliki SVG z dokumentacji |
| **Wykresy** | Canvas API (+ opcjonalnie Chart.js) | Wydajność, brak dużych zależności |
| **Testy** | Node.js assert lub Mocha | Wbudowane lub minimalna biblioteka |
| **Linter** | ESLint | Standard w Node.js |
| **Logger** | Winston (opcjonalnie) | Jeśli potrzebny zaawansowany logging |

**Minimalne zależności package.json:**
```json
{
  "dependencies": {
    "express": "^4.18.2",
    "ws": "^8.14.0"
  },
  "devDependencies": {
    "eslint": "^8.50.0",
    "mocha": "^10.2.0"
  }
}
```

---

## 13. Konwencje Kodowania

### 13.1 JavaScript Style Guide

- **Standard:** ESLint recommended
- **Indentacja:** 2 spacje
- **Quotes:** Single quotes dla stringów
- **Semicolons:** Używaj średników
- **Naming:**
  - camelCase dla zmiennych i funkcji
  - PascalCase dla klas
  - UPPER_SNAKE_CASE dla stałych

### 13.2 Komentarze

- JSDoc dla klas i funkcji publicznych
- Inline comments dla skomplikowanej logiki
- TODO/FIXME dla oznaczania problemów

**Przykład:**
```javascript
/**
 * Regulator PID dla systemu BOGDANKA
 * @class PIDController
 */
class PIDController {
  /**
   * Oblicza wartość sterującą (CV)
   * @param {number} setpoint - Wartość zadana
   * @param {number} processValue - Wartość rzeczywista
   * @param {number} deltaTime - Czas od ostatniego obliczenia [s]
   * @returns {number} Wartość sterująca w zakresie [min, max]
   */
  compute(setpoint, processValue, deltaTime) {
    // Implementacja...
  }
}
```

### 13.3 Struktura Plików

- Jeden plik = jedna klasa (preferowane)
- Małe utility functions: mogą być w jednym pliku
- Export: używaj `module.exports` (CommonJS)

---

## 14. Metryki Sukcesu

### 14.1 Kryteria Akceptacji

✅ **Funkcjonalność:**
- [ ] Wszystkie scenariusze S0-S8 działają poprawnie
- [ ] Algorytm 5A wykonuje rotację układów zgodnie z algorytmem
- [ ] Algorytm 5B wykonuje rotację nagrzewnic zgodnie z algorytmem
- [ ] Regulatory PID stabilizują temperaturę
- [ ] System alarmów działa poprawnie
- [ ] Tryb MANUAL pozwala na pełną kontrolę

✅ **Wydajność:**
- [ ] Symulacja działa płynnie (1 krok/s) przy 5 klientach
- [ ] Latency WebSocket < 100ms
- [ ] CPU usage < 10% (Node.js)
- [ ] Memory usage < 200MB

✅ **UX:**
- [ ] Interfejs intuicyjny i responsywny
- [ ] Formularz konfiguracji czytelny
- [ ] Wykresy aktualizują się w czasie rzeczywistym
- [ ] Alarmy są widoczne i słyszalne

✅ **Jakość kodu:**
- [ ] Pokrycie testami > 70%
- [ ] Brak błędów ESLint
- [ ] Dokumentacja JSDoc dla wszystkich klas publicznych
- [ ] README.md z instrukcją uruchomienia

---

**Koniec dokumentu implementacji**

Data stworzenia: 2025-11-21  
Wersja: 1.0  
Status: Gotowe do implementacji

