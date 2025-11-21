# Plan Implementacji - Aplikacja Symulacji BOGDANKA Szyb 2

## Metadane Projektu

**Nazwa projektu:** BOGDANKA Simulation App  
**Data rozpoczęcia:** 2025-11-21  
**Szacowany czas realizacji:** 80-100 godzin roboczych  
**Status:** Planowanie

---

## Harmonogram Faz

| Faza | Nazwa | Czas [h] | Zależności |
|------|-------|----------|------------|
| **0** | Setup Projektu | 2h | - |
| **1** | Backend - Core | 15h | Faza 0 |
| **2** | Backend - Algorytmy | 20h | Faza 1 |
| **3** | Frontend - Podstawy | 12h | Faza 1 |
| **4** | Frontend - HMI | 15h | Faza 3 |
| **5** | Frontend - Formularze i Wykresy | 12h | Faza 3 |
| **6** | Integracja i Testy | 10h | Fazy 2, 4, 5 |
| **7** | Dokumentacja | 4h | Faza 6 |
| **Σ** | **TOTAL** | **90h** | |

---

## FAZA 0: Setup Projektu

**Cel:** Przygotowanie środowiska, struktury projektu i podstawowych narzędzi

### Zadanie 0.1: Inicjalizacja Projektu Node.js
**Czas:** 30 min  
**Priorytet:** Krytyczny

**Kroki:**
1. Utwórz katalog `bogdanka-simulation/`
2. Inicjalizacja npm: `npm init`
3. Konfiguracja `package.json`:
   ```json
   {
     "name": "bogdanka-simulation",
     "version": "1.0.0",
     "description": "Symulacja systemu sterowania nagrzewnicami BOGDANKA Szyb 2",
     "main": "server/index.js",
     "scripts": {
       "start": "node server/index.js",
       "dev": "node --watch server/index.js",
       "test": "mocha tests/**/*.test.js"
     },
     "keywords": ["simulation", "HVAC", "mining", "PLC"],
     "author": "",
     "license": "MIT"
   }
   ```
4. Instalacja zależności:
   ```bash
   npm install express ws
   npm install --save-dev eslint mocha
   ```

**Kryteria akceptacji:**
- [x] package.json utworzony
- [x] Zależności zainstalowane
- [x] `npm start` nie wywołuje błędów

---

### Zadanie 0.2: Struktura Katalogów
**Czas:** 15 min  
**Priorytet:** Krytyczny

**Kroki:**
1. Utwórz strukturę zgodnie z `implementation.md` sekcja 2:
   ```
   mkdir -p server/{config,simulation,controllers,algorithms,utils,data}
   mkdir -p client/{css,js,assets/svg}
   mkdir -p shared
   mkdir -p tests
   ```

2. Skopiuj pliki SVG:
   ```bash
   cp ../Symulacja/*.svg client/assets/svg/
   ```

**Kryteria akceptacji:**
- [x] Wszystkie katalogi utworzone
- [x] Pliki SVG skopiowane (21 plików)

---

### Zadanie 0.3: Konfiguracja ESLint
**Czas:** 15 min  
**Priorytet:** Średni

**Kroki:**
1. Inicjalizacja ESLint: `npx eslint --init`
2. Wybór konfiguracji:
   - Environment: Node.js
   - Style: Standard / Airbnb
   - Format: JavaScript
3. Utworzenie `.eslintrc.js`:
   ```javascript
   module.exports = {
     env: { node: true, es2021: true },
     extends: 'eslint:recommended',
     parserOptions: { ecmaVersion: 'latest' },
     rules: {
       'indent': ['error', 2],
       'quotes': ['error', 'single'],
       'semi': ['error', 'always']
     }
   };
   ```
4. Dodanie skryptu do `package.json`:
   ```json
   "lint": "eslint server/**/*.js client/js/**/*.js"
   ```

**Kryteria akceptacji:**
- [x] `.eslintrc.js` utworzony
- [x] `npm run lint` działa

---

### Zadanie 0.4: Pliki Konfiguracyjne
**Czas:** 30 min  
**Priorytet:** Wysoki

**Kroki:**
1. Utwórz `server/config/default-config.js`:
   ```javascript
   module.exports = {
     // Temperatury zadane
     Tz: 50.0,
     Ts: 2.0,
     
     // Zakresy regulacji
     Pzmin: 20,
     Pzmax: 100,
     NWmin: 25,
     NWmax: 50,
     
     // PID nagrzewnic
     pid_heaters: { Kp: 2.0, Ki: 0.1, Kd: 0.05 },
     
     // PID wentylatorów
     pid_fans: { Kp: 1.5, Ki: 0.08, Kd: 0.03 },
     
     // Rotacja 5A
     OKRES_ROTACJI_UKLADOW: 168 * 3600,
     rotacja_5A_enabled: true,
     
     // Rotacja 5B
     OKRES_ROTACJI_NAGRZEWNIC: 168 * 3600,
     MIN_DELTA_CZASU: 3600,
     rotacja_5B_enabled: true,
     
     // Symulacja
     SIMULATION_SPEED: 1,
     TICK_INTERVAL: 1000
   };
   ```

2. Utwórz `shared/constants.js`:
   ```javascript
   module.exports = {
     SCENARIOS: [
       { id: 'S0', temp_min: 3, temp_max: Infinity, heaters: 0, W1: 'OFF', W2: 'OFF', temp_wyl: null, hist: 0 },
       { id: 'S1', temp_min: -1, temp_max: 2, heaters: 1, W1: 'PID', W2: 'OFF', temp_wyl: 3, hist: 1 },
       { id: 'S2', temp_min: -4, temp_max: -1, heaters: 2, W1: 'PID', W2: 'OFF', temp_wyl: 0, hist: 1 },
       { id: 'S3', temp_min: -8, temp_max: -4, heaters: 3, W1: 'PID', W2: 'OFF', temp_wyl: -3, hist: 1 },
       { id: 'S4', temp_min: -11, temp_max: -8, heaters: 4, W1: 'PID', W2: 'OFF', temp_wyl: -6, hist: 2 },
       { id: 'S5', temp_min: -15, temp_max: -11, heaters: 5, W1: 'MAX', W2: 'PID', temp_wyl: -10, hist: 1 },
       { id: 'S6', temp_min: -18, temp_max: -15, heaters: 6, W1: 'MAX', W2: 'PID', temp_wyl: -13, hist: 2 },
       { id: 'S7', temp_min: -21, temp_max: -18, heaters: 7, W1: 'MAX', W2: 'PID', temp_wyl: -15, hist: 3 },
       { id: 'S8', temp_min: -Infinity, temp_max: -21, heaters: 8, W1: 'MAX', W2: 'PID', temp_wyl: -20, hist: 1 }
     ],
     
     HEATER_IDS: ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8'],
     FAN_IDS: ['W1', 'W2'],
     
     ALARM_TYPES: {
       CRITICAL: 'CRITICAL',
       WARNING: 'WARNING',
       INFO: 'INFO'
     }
   };
   ```

3. Utwórz `.gitignore`:
   ```
   node_modules/
   server/data/*.json
   npm-debug.log
   .env
   ```

**Kryteria akceptacji:**
- [x] Pliki konfiguracyjne utworzone
- [x] Stałe zdefiniowane
- [x] `.gitignore` utworzony

---

### Zadanie 0.5: Prosty Serwer HTTP
**Czas:** 30 min  
**Priorytet:** Krytyczny

**Kroki:**
1. Utwórz `server/index.js`:
   ```javascript
   const express = require('express');
   const path = require('path');
   const WebSocket = require('ws');
   
   const app = express();
   const PORT = process.env.PORT || 3000;
   const WS_PORT = process.env.WS_PORT || 3001;
   
   // Serwowanie plików statycznych
   app.use(express.static(path.join(__dirname, '../client')));
   
   // Endpoint główny
   app.get('/', (req, res) => {
     res.sendFile(path.join(__dirname, '../client/index.html'));
   });
   
   // Start HTTP server
   const server = app.listen(PORT, () => {
     console.log(`HTTP Server running on http://localhost:${PORT}`);
   });
   
   // WebSocket server
   const wss = new WebSocket.Server({ port: WS_PORT });
   console.log(`WebSocket Server running on ws://localhost:${WS_PORT}`);
   
   wss.on('connection', (ws) => {
     console.log('Client connected');
     
     ws.on('message', (message) => {
       console.log('Received:', message.toString());
     });
     
     ws.on('close', () => {
       console.log('Client disconnected');
     });
   });
   ```

2. Utwórz `client/index.html`:
   ```html
   <!DOCTYPE html>
   <html lang="pl">
   <head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <title>BOGDANKA Simulation - Szyb 2</title>
     <link rel="stylesheet" href="css/main.css">
   </head>
   <body>
     <header>
       <h1>System Sterowania BOGDANKA Szyb 2 - Symulacja</h1>
     </header>
     <main>
       <div id="app">
         <p>Ładowanie...</p>
       </div>
     </main>
     <script src="js/app.js"></script>
   </body>
   </html>
   ```

3. Utwórz `client/css/main.css`:
   ```css
   * {
     box-sizing: border-box;
     margin: 0;
     padding: 0;
   }
   
   body {
     font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
     background-color: #1a1a1a;
     color: #e0e0e0;
   }
   
   header {
     background: #2c3e50;
     padding: 1rem;
     box-shadow: 0 2px 4px rgba(0,0,0,0.3);
   }
   
   header h1 {
     font-size: 1.5rem;
     color: #ecf0f1;
   }
   
   main {
     padding: 1rem;
   }
   ```

4. Utwórz `client/js/app.js`:
   ```javascript
   console.log('BOGDANKA Simulation App loaded');
   
   const appDiv = document.getElementById('app');
   appDiv.innerHTML = '<p>Połączenie z serwerem...</p>';
   
   // Test WebSocket
   const ws = new WebSocket('ws://localhost:3001');
   
   ws.onopen = () => {
     console.log('WebSocket connected');
     appDiv.innerHTML = '<p style="color: green;">✓ Połączono z serwerem</p>';
     ws.send(JSON.stringify({ type: 'HELLO' }));
   };
   
   ws.onmessage = (event) => {
     console.log('Message from server:', event.data);
   };
   
   ws.onerror = (error) => {
     console.error('WebSocket error:', error);
     appDiv.innerHTML = '<p style="color: red;">✗ Błąd połączenia</p>';
   };
   ```

**Kryteria akceptacji:**
- [x] `npm start` uruchamia serwer
- [x] `http://localhost:3000` wyświetla stronę
- [x] WebSocket połączenie działa
- [x] Konsola pokazuje "Client connected"

---

## FAZA 1: Backend - Core

**Cel:** Implementacja podstawowego silnika symulacji, modelu danych i ScenarioManager

### Zadanie 1.1: Model Stanu Systemu (SystemState.js)
**Czas:** 2h  
**Priorytet:** Krytyczny  
**Zależności:** Zadanie 0.4

**Kroki:**
1. Utwórz `server/simulation/SystemState.js`:
   ```javascript
   const defaultConfig = require('../config/default-config');
   const { HEATER_IDS, FAN_IDS } = require('../../shared/constants');
   
   class SystemState {
     constructor(config = {}) {
       this.config = { ...defaultConfig, ...config };
       this.reset();
     }
     
     reset() {
       this.timestamp = Date.now();
       
       // Input
       this.input = {
         t_zewn: 5.0,
         t_wody_grzewczej: 80.0,
         woda_przeplyw_ok: true
       };
       
       // Scenario
       this.scenario = {
         current: 'S0',
         uklad_pracy: 'Podstawowy',
         active_ciag: null,
         required_heaters: 0
       };
       
       // Heaters N1-N8
       this.heaters = HEATER_IDS.map((id, index) => ({
         id,
         ciag: index < 4 ? 'C1' : 'C2',
         active: false,
         sprawna: true,
         temp_wylot: 20.0,
         zawor_pozycja: 20,
         przepustnica_dolot: false,
         pid_mode: 'MANUAL',
         pid_cv: 20,
         pid_integral: 0,
         pid_last_error: 0,
         czas_pracy: 0,
         czas_postoju: 0,
         liczba_zalaczeń: 0,
         ostatnie_zalaczenie: null
       }));
       
       // Fans W1-W2
       this.fans = FAN_IDS.map((id, index) => ({
         id,
         ciag: index === 0 ? 'C1' : 'C2',
         active: false,
         sprawny: true,
         czestotliwosc: 0,
         prad: 0,
         pid_mode: 'OFF',
         pid_cv: 0,
         pid_integral: 0,
         pid_last_error: 0,
         czas_pracy: 0
       }));
       
       // Dampers
       this.dampers = {
         spinka_ciagow: false,
         kolektor_C1: true,
         kolektor_C2: false,
         wyrzutnia_430: false,
         wyrzutnia_790: false
       };
       
       // Shaft temperature
       this.shaft_temp = {
         poziom_minus30: 5.0,
         poziom_plus430: 10.0,
         poziom_plus790: 10.0
       };
       
       // Rotation 5A
       this.rotation_5A = {
         aktualny_uklad: 'Podstawowy',
         czas_ostatniej_zmiany: this.timestamp,
         czas_pracy_podstawowy: 0,
         czas_pracy_ograniczony: 0,
         liczba_rotacji: 0,
         nastepna_rotacja_za: this.config.OKRES_ROTACJI_UKLADOW
       };
       
       // Rotation 5B
       this.rotation_5B = {
         C1: {
           czas_ostatniej_rotacji: this.timestamp,
           nastepna_rotacja_za: this.config.OKRES_ROTACJI_NAGRZEWNIC,
           liczba_rotacji: 0
         },
         C2: {
           czas_ostatniej_rotacji: this.timestamp,
           nastepna_rotacja_za: this.config.OKRES_ROTACJI_NAGRZEWNIC,
           liczba_rotacji: 0
         }
       };
       
       // Alarms
       this.alarms = [];
       
       // Stats
       this.stats = {
         simulation_time: 0,
         system_uptime: 0,
         total_energy: 0
       };
     }
     
     toJSON() {
       return {
         timestamp: this.timestamp,
         input: this.input,
         config: this.config,
         scenario: this.scenario,
         heaters: this.heaters,
         fans: this.fans,
         dampers: this.dampers,
         shaft_temp: this.shaft_temp,
         rotation_5A: this.rotation_5A,
         rotation_5B: this.rotation_5B,
         alarms: this.alarms,
         stats: this.stats
       };
     }
     
     updateConfig(newConfig) {
       this.config = { ...this.config, ...newConfig };
     }
     
     getHeater(id) {
       return this.heaters.find(h => h.id === id);
     }
     
     getFan(id) {
       return this.fans.find(f => f.id === id);
     }
     
     getActiveHeaters(ciag = null) {
       if (ciag) {
         return this.heaters.filter(h => h.active && h.ciag === ciag);
       }
       return this.heaters.filter(h => h.active);
     }
   }
   
   module.exports = SystemState;
   ```

**Kryteria akceptacji:**
- [x] Klasa SystemState utworzona
- [x] Metoda `reset()` inicjalizuje stan
- [x] Metoda `toJSON()` zwraca pełny stan
- [x] Gettery działają poprawnie

---

### Zadanie 1.2: Zarządzanie Scenariuszami (ScenarioManager.js)
**Czas:** 2h  
**Priorytet:** Krytyczny  
**Zależności:** Zadanie 1.1

**Kroki:**
1. Utwórz `server/simulation/ScenarioManager.js`:
   ```javascript
   const { SCENARIOS } = require('../../shared/constants');
   
   class ScenarioManager {
     constructor() {
       this.scenarios = SCENARIOS;
       this.currentScenario = null;
       this.lastScenario = null;
     }
     
     /**
      * Określa scenariusz na podstawie temperatury zewnętrznej
      * @param {number} t_zewn - Temperatura zewnętrzna [°C]
      * @param {string} currentScenarioId - Aktualny scenariusz
      * @returns {object} Scenariusz
      */
     determineScenario(t_zewn, currentScenarioId) {
       const current = this.scenarios.find(s => s.id === currentScenarioId);
       
       // Sprawdź czy trzeba zmienić scenariusz (z histerezą)
       if (current) {
         // Sprawdź warunek wyłączenia (temperatura wzrosła)
         if (current.temp_wyl !== null && t_zewn >= current.temp_wyl) {
           // Przejdź do scenariusza wyższego (mniej nagrzewnic)
           return this.findScenarioByTemp(t_zewn);
         }
         
         // Sprawdź czy jesteśmy w zakresie aktualnego scenariusza
         if (t_zewn > current.temp_min && t_zewn <= current.temp_max) {
           return current;
         }
       }
       
       // Znajdź nowy scenariusz
       return this.findScenarioByTemp(t_zewn);
     }
     
     findScenarioByTemp(t_zewn) {
       for (const scenario of this.scenarios) {
         if (t_zewn > scenario.temp_min && t_zewn <= scenario.temp_max) {
           return scenario;
         }
       }
       // Fallback do S8 (najniższa temperatura)
       return this.scenarios[this.scenarios.length - 1];
     }
     
     /**
      * Określa układ pracy (Podstawowy / Ograniczony)
      * @param {object} scenario
      * @param {object} state
      * @returns {string}
      */
     determineUkladPracy(scenario, state) {
       // Rotacja 5A może wymusić układ ograniczony w S1-S4
       if (state.rotation_5A.aktualny_uklad === 'Ograniczony' && 
           ['S1', 'S2', 'S3', 'S4'].includes(scenario.id)) {
         return 'Ograniczony';
       }
       
       // W S5-S8 zawsze Podstawowy (oba ciągi)
       if (['S5', 'S6', 'S7', 'S8'].includes(scenario.id)) {
         return 'Podstawowy';
       }
       
       // W S1-S4 domyślnie Podstawowy (tylko C1)
       return 'Podstawowy';
     }
     
     /**
      * Określa aktywny ciąg
      * @param {object} scenario
      * @param {string} uklad_pracy
      * @returns {string}
      */
     determineActiveCiag(scenario, uklad_pracy) {
       if (['S5', 'S6', 'S7', 'S8'].includes(scenario.id)) {
         return 'C1+C2';  // Oba ciągi
       }
       
       if (uklad_pracy === 'Ograniczony') {
         return 'C2';  // Tylko C2 (przez spinę)
       }
       
       return 'C1';  // Tylko C1
     }
   }
   
   module.exports = ScenarioManager;
   ```

2. Testy jednostkowe `tests/scenario-manager.test.js`:
   ```javascript
   const assert = require('assert');
   const ScenarioManager = require('../server/simulation/ScenarioManager');
   
   describe('ScenarioManager', () => {
     let manager;
     
     beforeEach(() => {
       manager = new ScenarioManager();
     });
     
     it('should select S0 for t_zewn = 5°C', () => {
       const scenario = manager.findScenarioByTemp(5);
       assert.strictEqual(scenario.id, 'S0');
     });
     
     it('should select S3 for t_zewn = -6°C', () => {
       const scenario = manager.findScenarioByTemp(-6);
       assert.strictEqual(scenario.id, 'S3');
     });
     
     it('should apply hysteresis when switching scenarios', () => {
       // Aktualnie S1, temp. wzrasta
       let scenario = manager.determineScenario(2.5, 'S1');
       assert.strictEqual(scenario.id, 'S1'); // Pozostaje S1
       
       scenario = manager.determineScenario(3.5, 'S1');
       assert.strictEqual(scenario.id, 'S0'); // Przełącza na S0
     });
   });
   ```

**Kryteria akceptacji:**
- [x] Klasa ScenarioManager utworzona
- [x] Metoda `determineScenario()` wybiera poprawny scenariusz
- [x] Histereza działa
- [x] Testy przechodzą: `npm test`

---

### Zadanie 1.3: Regulator PID (PIDController.js)
**Czas:** 3h  
**Priorytet:** Krytyczny  
**Zależności:** -

**Kroki:**
1. Utwórz `server/simulation/PIDController.js`:
   ```javascript
   /**
    * Regulator PID z anty-windupem
    */
   class PIDController {
     /**
      * @param {number} Kp - Wzmocnienie proporcjonalne
      * @param {number} Ki - Wzmocnienie całkowe
      * @param {number} Kd - Wzmocnienie różniczkowe
      * @param {number} min - Minimalna wartość wyjścia
      * @param {number} max - Maksymalna wartość wyjścia
      */
     constructor(Kp, Ki, Kd, min, max) {
       this.Kp = Kp;
       this.Ki = Ki;
       this.Kd = Kd;
       this.min = min;
       this.max = max;
       
       this.reset();
     }
     
     reset() {
       this.integral = 0;
       this.lastError = 0;
       this.lastOutput = this.min;
     }
     
     /**
      * Oblicza wartość sterującą
      * @param {number} setpoint - Wartość zadana
      * @param {number} processValue - Wartość rzeczywista
      * @param {number} deltaTime - Czas od ostatniego obliczenia [s]
      * @returns {number} Wartość sterująca [min, max]
      */
     compute(setpoint, processValue, deltaTime = 1.0) {
       // Uchyb
       const error = setpoint - processValue;
       
       // Składowa proporcjonalna
       const P = this.Kp * error;
       
       // Składowa całkowa
       this.integral += error * deltaTime;
       
       // Anty-windup: ograniczenie całki
       const maxIntegral = (this.max - this.min) / (this.Ki || 1);
       this.integral = Math.max(-maxIntegral, Math.min(maxIntegral, this.integral));
       
       const I = this.Ki * this.integral;
       
       // Składowa różniczkowa
       const derivative = (error - this.lastError) / deltaTime;
       const D = this.Kd * derivative;
       
       // Wyjście
       let output = P + I + D;
       
       // Ograniczenie wyjścia
       output = Math.max(this.min, Math.min(this.max, output));
       
       // Zapisz stan
       this.lastError = error;
       this.lastOutput = output;
       
       return output;
     }
     
     /**
      * Zmiana nastaw PID
      */
     setTunings(Kp, Ki, Kd) {
       this.Kp = Kp;
       this.Ki = Ki;
       this.Kd = Kd;
     }
     
     /**
      * Zmiana limitów
      */
     setLimits(min, max) {
       this.min = min;
       this.max = max;
     }
     
     getState() {
       return {
         integral: this.integral,
         lastError: this.lastError,
         lastOutput: this.lastOutput
       };
     }
   }
   
   module.exports = PIDController;
   ```

2. Testy `tests/pid.test.js`:
   ```javascript
   const assert = require('assert');
   const PIDController = require('../server/simulation/PIDController');
   
   describe('PIDController', () => {
     it('should compute correct output for proportional control', () => {
       const pid = new PIDController(1.0, 0, 0, 0, 100);
       const output = pid.compute(50, 40, 1);
       assert.strictEqual(output, 10); // P = 1.0 * (50 - 40) = 10
     });
     
     it('should limit output to min/max range', () => {
       const pid = new PIDController(10.0, 0, 0, 0, 100);
       const output = pid.compute(50, 0, 1);
       assert.strictEqual(output, 100); // Limited to max
     });
     
     it('should implement anti-windup for integral term', () => {
       const pid = new PIDController(0, 1.0, 0, 0, 100);
       
       // Symuluj długi czas z dużym uchybem
       for (let i = 0; i < 1000; i++) {
         pid.compute(100, 0, 1);
       }
       
       // Integral nie powinien eksplodować
       const state = pid.getState();
       assert.ok(state.integral < 200); // Rozsądna wartość
     });
     
     it('should reset state', () => {
       const pid = new PIDController(1.0, 0.5, 0.1, 0, 100);
       pid.compute(50, 40, 1);
       pid.reset();
       
       const state = pid.getState();
       assert.strictEqual(state.integral, 0);
       assert.strictEqual(state.lastError, 0);
     });
   });
   ```

**Kryteria akceptacji:**
- [x] Klasa PIDController utworzona
- [x] Algorytm PID poprawny (P + I + D)
- [x] Anty-windup działa
- [x] Limitowanie wyjścia działa
- [x] Testy przechodzą

---

### Zadanie 1.4: Kontroler Nagrzewnic (HeaterController.js)
**Czas:** 3h  
**Priorytet:** Wysoki  
**Zależności:** Zadania 1.1, 1.3

**Kroki:**
1. Utwórz `server/controllers/HeaterController.js`:
   ```javascript
   const PIDController = require('../simulation/PIDController');
   
   class HeaterController {
     constructor(state) {
       this.state = state;
       this.pidControllers = {};
       
       // Inicjalizacja regulatorów PID dla każdej nagrzewnicy
       this.state.heaters.forEach(heater => {
         const { Kp, Ki, Kd } = this.state.config.pid_heaters;
         this.pidControllers[heater.id] = new PIDController(
           Kp, Ki, Kd,
           this.state.config.Pzmin,
           this.state.config.Pzmax
         );
       });
     }
     
     /**
      * Aktualizacja nagrzewnic (1 krok symulacji)
      */
     update(deltaTime) {
       this.state.heaters.forEach(heater => {
         if (heater.active && heater.sprawna) {
           this.updateHeater(heater, deltaTime);
         } else {
           this.updateInactiveHeater(heater, deltaTime);
         }
       });
     }
     
     updateHeater(heater, deltaTime) {
       // Aktualizacja licznika czasu pracy
       heater.czas_pracy += deltaTime;
       
       if (heater.pid_mode === 'AUTO') {
         // Regulacja PID
         const pid = this.pidControllers[heater.id];
         const cv = pid.compute(
           this.state.config.Tz,
           heater.temp_wylot,
           deltaTime
         );
         
         heater.pid_cv = cv;
         heater.zawor_pozycja = cv;
         
         // Zapisz stan PID
         const pidState = pid.getState();
         heater.pid_integral = pidState.integral;
         heater.pid_last_error = pidState.lastError;
       }
       
       // Symulacja temperatury na wylocie
       heater.temp_wylot = this.simulateHeaterTemp(heater);
     }
     
     updateInactiveHeater(heater, deltaTime) {
       heater.czas_postoju += deltaTime;
       
       // Utrzymanie zaworu na min. pozycji (ochrona antyzamrożeniowa)
       heater.zawor_pozycja = this.state.config.Pzmin;
       
       // Temperatura spada do temp. zewnętrznej
       const coolingRate = 0.1; // °C/s
       heater.temp_wylot = Math.max(
         this.state.input.t_zewn + 5,
         heater.temp_wylot - coolingRate * deltaTime
       );
     }
     
     /**
      * Symulacja temperatury na wylocie nagrzewnicy
      */
     simulateHeaterTemp(heater) {
       if (!heater.active || !heater.sprawna) {
         return heater.temp_wylot;
       }
       
       // Parametry symulacji
       const MAX_TEMP = 70; // Maksymalna temperatura przy 100% zaworu
       const HEATING_RATE = 2.0; // °C/s przy 100% mocy
       const COOLING_RATE = 0.5; // °C/s
       
       // Temperatura docelowa zależna od pozycji zaworu
       const targetTemp = this.state.input.t_zewn + 
         (MAX_TEMP - this.state.input.t_zewn) * (heater.zawor_pozycja / 100);
       
       // Inercja termiczna (model 1. rzędu)
       const TAU = 30; // Stała czasowa [s]
       const alpha = 1 - Math.exp(-1 / TAU);
       
       const newTemp = heater.temp_wylot + alpha * (targetTemp - heater.temp_wylot);
       
       return newTemp;
     }
     
     /**
      * Załączenie nagrzewnicy
      */
     startHeater(heaterId) {
       const heater = this.state.getHeater(heaterId);
       if (!heater || !heater.sprawna) {
         return false;
       }
       
       heater.active = true;
       heater.przepustnica_dolot = true;
       heater.pid_mode = 'AUTO';
       heater.liczba_zalaczeń++;
       heater.ostatnie_zalaczenie = Date.now();
       
       // Reset regulatora PID
       this.pidControllers[heaterId].reset();
       
       return true;
     }
     
     /**
      * Wyłączenie nagrzewnicy
      */
     stopHeater(heaterId) {
       const heater = this.state.getHeater(heaterId);
       if (!heater) {
         return false;
       }
       
       heater.active = false;
       heater.przepustnica_dolot = false;
       heater.pid_mode = 'MANUAL';
       heater.zawor_pozycja = this.state.config.Pzmin;
       heater.pid_cv = this.state.config.Pzmin;
       
       return true;
     }
     
     /**
      * Zmiana trybu PID
      */
     setMode(heaterId, mode) {
       const heater = this.state.getHeater(heaterId);
       if (!heater) return false;
       
       if (mode === 'AUTO' && heater.pid_mode === 'MANUAL') {
         // Bumpless transfer: reset PID ze stanem początkowym
         this.pidControllers[heaterId].reset();
         this.pidControllers[heaterId].integral = 
           heater.zawor_pozycja / this.state.config.pid_heaters.Ki;
       }
       
       heater.pid_mode = mode;
       return true;
     }
   }
   
   module.exports = HeaterController;
   ```

**Kryteria akceptacji:**
- [x] HeaterController utworzony
- [x] Regulacja PID nagrzewnic działa
- [x] Symulacja temperatury działa
- [x] Załączanie/wyłączanie działa
- [x] Bumpless transfer zaimplementowany

---

### Zadanie 1.5: Kontroler Wentylatorów (FanController.js)
**Czas:** 2h  
**Priorytet:** Wysoki  
**Zależności:** Zadania 1.1, 1.3

**Kroki:**
1. Utwórz `server/controllers/FanController.js` - analogicznie do HeaterController
2. Implementacja regulacji PID dla wentylatorów (control variable: częstotliwość Hz)
3. Obsługa trybu MAX (stała częstotliwość 50 Hz)

**Kryteria akceptacji:**
- [x] FanController utworzony
- [x] Regulacja PID wentylatorów działa
- [x] Tryb MAX działa
- [x] Załączanie/wyłączanie działa

---

### Zadanie 1.6: System Alarmów (AlarmSystem.js)
**Czas:** 2h  
**Priorytet:** Średni  
**Zależności:** Zadanie 1.1

**Kroki:**
1. Utwórz `server/simulation/AlarmSystem.js`
2. Implementacja dodawania alarmów (CRITICAL, WARNING, INFO)
3. Kwituowanie alarmów
4. Sprawdzanie warunków alarmowych:
   - Temperatura nagrzewnicy > 60°C
   - Temperatura nagrzewnicy < 40°C przy pracy
   - Wentylator nie pracuje
   - Temperatura wody < 5°C

**Kryteria akceptacji:**
- [x] AlarmSystem utworzony
- [x] Alarmy są generowane poprawnie
- [x] Kwituowanie działa

---

### Zadanie 1.7: Główny Silnik Symulacji (SimulationEngine.js)
**Czas:** 3h  
**Priorytet:** Krytyczny  
**Zależności:** Zadania 1.1-1.6

**Kroki:**
1. Utwórz `server/simulation/SimulationEngine.js`:
   ```javascript
   const SystemState = require('./SystemState');
   const ScenarioManager = require('./ScenarioManager');
   const HeaterController = require('../controllers/HeaterController');
   const FanController = require('../controllers/FanController');
   const AlarmSystem = require('./AlarmSystem');
   
   class SimulationEngine {
     constructor(config, wsServer) {
       this.config = config;
       this.wsServer = wsServer;
       
       this.state = new SystemState(config);
       this.scenarioManager = new ScenarioManager();
       this.heaterController = new HeaterController(this.state);
       this.fanController = new FanController(this.state);
       this.alarmSystem = new AlarmSystem(this.state);
       
       this.isRunning = false;
       this.intervalId = null;
       this.tickCount = 0;
     }
     
     start() {
       if (this.isRunning) return;
       
       this.isRunning = true;
       const tickInterval = this.config.TICK_INTERVAL / this.config.SIMULATION_SPEED;
       
       this.intervalId = setInterval(() => {
         this.tick();
       }, tickInterval);
       
       console.log('Simulation started');
     }
     
     stop() {
       if (!this.isRunning) return;
       
       this.isRunning = false;
       clearInterval(this.intervalId);
       this.intervalId = null;
       
       console.log('Simulation stopped');
     }
     
     /**
      * Pojedynczy krok symulacji (1 sekunda)
      */
     tick() {
       const deltaTime = 1.0 * this.config.SIMULATION_SPEED;
       this.tickCount++;
       
       // 1. Określenie scenariusza
       const scenario = this.scenarioManager.determineScenario(
         this.state.input.t_zewn,
         this.state.scenario.current
       );
       
       const uklad_pracy = this.scenarioManager.determineUkladPracy(scenario, this.state);
       const active_ciag = this.scenarioManager.determineActiveCiag(scenario, uklad_pracy);
       
       // Aktualizacja scenariusza
       this.state.scenario = {
         current: scenario.id,
         uklad_pracy,
         active_ciag,
         required_heaters: scenario.heaters
       };
       
       // 2. Aktualizacja kontrolerów
       this.heaterController.update(deltaTime);
       this.fanController.update(deltaTime);
       
       // 3. Symulacja temperatury w szybie
       this.simulateShaftTemperature(deltaTime);
       
       // 4. Sprawdzenie alarmów
       this.alarmSystem.check();
       
       // 5. Aktualizacja statystyk
       this.state.stats.simulation_time += deltaTime;
       
       // 6. Broadcast stanu do klientów
       if (this.tickCount % 1 === 0) { // Co 1 sekundę
         this.broadcastState();
       }
     }
     
     simulateShaftTemperature(deltaTime) {
       // Uproszczony model temperatury w szybie
       const THERMAL_MASS = 50000;
       const HEAT_LOSS_COEFF = 0.05;
       
       let totalHeat = 0;
       this.state.heaters.forEach(heater => {
         if (heater.active) {
           const power = 100000 * (heater.zawor_pozycja / 100); // 100 kW max
           totalHeat += power * deltaTime;
         }
       });
       
       const heatLoss = HEAT_LOSS_COEFF * 
         (this.state.shaft_temp.poziom_minus30 - this.state.input.t_zewn) * deltaTime;
       
       const deltaTemp = (totalHeat - heatLoss) / THERMAL_MASS;
       this.state.shaft_temp.poziom_minus30 += deltaTemp;
     }
     
     broadcastState() {
       const message = JSON.stringify({
         type: 'STATE_UPDATE',
         payload: this.state.toJSON()
       });
       
       this.wsServer.clients.forEach(client => {
         if (client.readyState === 1) { // WebSocket.OPEN
           client.send(message);
         }
       });
     }
     
     reset() {
       this.stop();
       this.state.reset();
       this.tickCount = 0;
       console.log('Simulation reset');
     }
     
     updateConfig(newConfig) {
       this.state.updateConfig(newConfig);
       this.config = { ...this.config, ...newConfig };
     }
   }
   
   module.exports = SimulationEngine;
   ```

2. Integracja z `server/index.js`:
   ```javascript
   const SimulationEngine = require('./simulation/SimulationEngine');
   const defaultConfig = require('./config/default-config');
   
   // ... istniejący kod ...
   
   // Inicjalizacja silnika symulacji
   const simulationEngine = new SimulationEngine(defaultConfig, wss);
   
   wss.on('connection', (ws) => {
     console.log('Client connected');
     
     // Wyślij aktualny stan
     ws.send(JSON.stringify({
       type: 'STATE_UPDATE',
       payload: simulationEngine.state.toJSON()
     }));
     
     ws.on('message', (message) => {
       try {
         const data = JSON.parse(message.toString());
         
         switch (data.type) {
           case 'SIMULATION_CONTROL':
             if (data.payload.action === 'START') simulationEngine.start();
             if (data.payload.action === 'STOP') simulationEngine.stop();
             if (data.payload.action === 'RESET') simulationEngine.reset();
             break;
             
           case 'CONFIG_UPDATE':
             simulationEngine.updateConfig(data.payload);
             break;
             
           case 'SET_T_ZEWN':
             simulationEngine.state.input.t_zewn = data.payload.t_zewn;
             break;
         }
       } catch (error) {
         console.error('Error handling message:', error);
       }
     });
   });
   
   // Auto-start symulacji
   simulationEngine.start();
   ```

**Kryteria akceptacji:**
- [x] SimulationEngine utworzony
- [x] Główna pętla (tick) działa
- [x] Scenariusze przełączają się poprawnie
- [x] WebSocket broadcast działa
- [x] Start/Stop/Reset działają

---

## FAZA 2: Backend - Algorytmy Rotacji

**Cel:** Implementacja algorytmów 5A i 5B

### Zadanie 2.1: Algorytm 5A - Rotacja Układów (Rotation5A.js)
**Czas:** 5h  
**Priorytet:** Wysoki  
**Zależności:** Faza 1

**Kroki:**
1. Utwórz `server/algorithms/Rotation5A.js`
2. Implementacja sprawdzania warunków rotacji:
   - Scenariusz S1-S4
   - Sprawność C2
   - Upływ okresu rotacji
3. Implementacja sekwencji zmiany układu (state machine):
   - Przejście Podstawowy → Ograniczony
   - Przejście Ograniczony → Podstawowy
4. Obsługa opóźnień między krokami (async/await lub kolejka zdarzeń)

**Szczegółowy pseudokod w `implementation.md` sekcja 4.4**

**Kryteria akceptacji:**
- [x] Rotation5A utworzony
- [x] Warunki rotacji sprawdzane poprawnie
- [x] Sekwencja zmiany działa
- [x] Liczniki czasu aktualizowane

---

### Zadanie 2.2: Algorytm 5B - Rotacja Nagrzewnic (Rotation5B.js)
**Czas:** 6h  
**Priorytet:** Wysoki  
**Zależności:** Zadanie 2.1

**Kroki:**
1. Utwórz `server/algorithms/Rotation5B.js`
2. Implementacja liczników czasu pracy/postoju
3. Implementacja wyboru nagrzewnic:
   - Najdłużej pracująca (active)
   - Najdłużej w postoju (idle)
4. Sprawdzenie MIN_DELTA_CZASU
5. Implementacja sekwencji rotacji (state machine):
   - Załączenie nagrzewnicy nowej
   - Sprawdzenie stabilizacji
   - Wyłączenie nagrzewnicy starej

**Szczegółowy pseudokod w `implementation.md` sekcja 4.5**

**Kryteria akceptacji:**
- [x] Rotation5B utworzony
- [x] Wybór nagrzewnic działa poprawnie
- [x] Sekwencja rotacji działa
- [x] Liczniki aktualizowane

---

### Zadanie 2.3: Integracja Algorytmów z SimulationEngine
**Czas:** 3h  
**Priorytet:** Wysoki  
**Zależności:** Zadania 2.1, 2.2

**Kroki:**
1. Dodanie algorytmów do `SimulationEngine`:
   ```javascript
   const Rotation5A = require('../algorithms/Rotation5A');
   const Rotation5B = require('../algorithms/Rotation5B');
   
   // W konstruktorze
   this.rotation5A = new Rotation5A(this.state);
   this.rotation5B = new Rotation5B(this.state);
   ```

2. Wywołanie w pętli `tick()`:
   ```javascript
   // Po aktualizacji kontrolerów
   if (this.state.config.rotacja_5A_enabled) {
     this.rotation5A.check();
   }
   
   if (this.state.config.rotacja_5B_enabled) {
     this.rotation5B.check('C1');
     this.rotation5B.check('C2');
   }
   ```

3. Obsługa zdarzeń rotacji (broadcasting do klientów)

**Kryteria akceptacji:**
- [x] Algorytmy zintegrowane
- [x] Rotacje wykonują się automatycznie
- [x] Zdarzenia broadcastowane do klientów

---

### Zadanie 2.4: State Machine dla Sekwencji
**Czas:** 4h  
**Priorytet:** Wysoki  
**Zależności:** Zadania 2.1, 2.2

**Kroki:**
1. Utwórz `server/utils/StateMachine.js`:
   ```javascript
   class StateMachine {
     constructor() {
       this.currentState = 'IDLE';
       this.steps = [];
       this.currentStep = 0;
       this.stepStartTime = null;
     }
     
     start(steps) {
       this.steps = steps;
       this.currentStep = 0;
       this.currentState = 'RUNNING';
       this.executeStep();
     }
     
     executeStep() {
       if (this.currentStep >= this.steps.length) {
         this.currentState = 'COMPLETED';
         return;
       }
       
       const step = this.steps[this.currentStep];
       this.stepStartTime = Date.now();
       
       // Wykonaj akcję
       step.action();
       
       // Zaplanuj następny krok
       if (step.delay > 0) {
         setTimeout(() => {
           this.currentStep++;
           this.executeStep();
         }, step.delay * 1000);
       } else {
         this.currentStep++;
         this.executeStep();
       }
     }
     
     abort() {
       this.currentState = 'ABORTED';
       this.steps = [];
     }
   }
   
   module.exports = StateMachine;
   ```

2. Użycie w Rotation5A i Rotation5B

**Kryteria akceptacji:**
- [x] StateMachine utworzony
- [x] Sekwencje wykonują się z opóźnieniami
- [x] Możliwość przerwania sekwencji

---

### Zadanie 2.5: Testy Algorytmów Rotacji
**Czas:** 2h  
**Priorytet:** Średni  
**Zależności:** Zadania 2.1, 2.2

**Kroki:**
1. Testy `tests/rotation5a.test.js`:
   - Test warunków rotacji
   - Test przełączania układów
   - Test liczników czasu

2. Testy `tests/rotation5b.test.js`:
   - Test wyboru nagrzewnic
   - Test delta czasu
   - Test sekwencji

**Kryteria akceptacji:**
- [x] Testy utworzone
- [x] Wszystkie testy przechodzą

---

## FAZA 3: Frontend - Podstawy

**Cel:** Struktura frontendu, WebSocket client, podstawowy layout

### Zadanie 3.1: WebSocket Client (WebSocketClient.js)
**Czas:** 2h  
**Priorytet:** Krytyczny  
**Zależności:** Faza 1

**Kroki:**
1. Utwórz `client/js/WebSocketClient.js`:
   ```javascript
   class WebSocketClient {
     constructor(url) {
       this.url = url;
       this.ws = null;
       this.reconnectInterval = 5000;
       this.callbacks = {
         onStateUpdate: null,
         onAlarm: null,
         onError: null
       };
     }
     
     connect() {
       this.ws = new WebSocket(this.url);
       
       this.ws.onopen = () => {
         console.log('WebSocket connected');
       };
       
       this.ws.onmessage = (event) => {
         try {
           const data = JSON.parse(event.data);
           this.handleMessage(data);
         } catch (error) {
           console.error('Error parsing message:', error);
         }
       };
       
       this.ws.onerror = (error) => {
         console.error('WebSocket error:', error);
         if (this.callbacks.onError) {
           this.callbacks.onError(error);
         }
       };
       
       this.ws.onclose = () => {
         console.log('WebSocket closed, reconnecting...');
         setTimeout(() => this.connect(), this.reconnectInterval);
       };
     }
     
     handleMessage(data) {
       switch (data.type) {
         case 'STATE_UPDATE':
           if (this.callbacks.onStateUpdate) {
             this.callbacks.onStateUpdate(data.payload);
           }
           break;
           
         case 'NEW_ALARM':
           if (this.callbacks.onAlarm) {
             this.callbacks.onAlarm(data.payload);
           }
           break;
       }
     }
     
     send(type, payload) {
       if (this.ws && this.ws.readyState === WebSocket.OPEN) {
         this.ws.send(JSON.stringify({ type, payload }));
       }
     }
     
     on(event, callback) {
       this.callbacks[event] = callback;
     }
   }
   ```

**Kryteria akceptacji:**
- [x] WebSocketClient utworzony
- [x] Połączenie działa
- [x] Auto-reconnect działa
- [x] Callbacki działają

---

### Zadanie 3.2: Layout HTML i CSS
**Czas:** 3h  
**Priorytet:** Wysoki  
**Zależności:** -

**Kroki:**
1. Aktualizacja `client/index.html`:
   ```html
   <body>
     <header>
       <h1>BOGDANKA Szyb 2 - Symulacja</h1>
       <div class="controls">
         <button id="btn-start">▶ Start</button>
         <button id="btn-stop">⏸ Stop</button>
         <button id="btn-reset">⟳ Reset</button>
         <select id="select-speed">
           <option value="1">1x</option>
           <option value="10">10x</option>
           <option value="100">100x</option>
         </select>
       </div>
     </header>
     
     <nav>
       <button class="tab active" data-tab="hmi">HMI</button>
       <button class="tab" data-tab="config">Konfiguracja</button>
       <button class="tab" data-tab="charts">Wykresy</button>
       <button class="tab" data-tab="alarms">Alarmy</button>
       <button class="tab" data-tab="rotation">Rotacja</button>
     </nav>
     
     <main>
       <div id="tab-hmi" class="tab-content active">
         <!-- Panel HMI -->
       </div>
       
       <div id="tab-config" class="tab-content">
         <!-- Formularz konfiguracji -->
       </div>
       
       <div id="tab-charts" class="tab-content">
         <!-- Wykresy -->
       </div>
       
       <div id="tab-alarms" class="tab-content">
         <!-- Alarmy -->
       </div>
       
       <div id="tab-rotation" class="tab-content">
         <!-- Rotacja 5A i 5B -->
       </div>
     </main>
     
     <script src="js/WebSocketClient.js"></script>
     <script src="js/app.js"></script>
   </body>
   ```

2. Styling `client/css/main.css`:
   - Ciemny motyw (dark theme)
   - Grid layout
   - Responsywność

**Kryteria akceptacji:**
- [x] Layout utworzony
- [x] Zakładki przełączają się
- [x] Responsywny design

---

### Zadanie 3.3: Główna Aplikacja (app.js)
**Czas:** 3h  
**Priorytet:** Krytyczny  
**Zależności:** Zadania 3.1, 3.2

**Kroki:**
1. Aktualizacja `client/js/app.js`:
   ```javascript
   const wsClient = new WebSocketClient('ws://localhost:3001');
   
   let currentState = null;
   
   // Połączenie
   wsClient.connect();
   
   // Callbacki
   wsClient.on('onStateUpdate', (state) => {
     currentState = state;
     updateUI(state);
   });
   
   // Kontrolki
   document.getElementById('btn-start').onclick = () => {
     wsClient.send('SIMULATION_CONTROL', { action: 'START' });
   };
   
   document.getElementById('btn-stop').onclick = () => {
     wsClient.send('SIMULATION_CONTROL', { action: 'STOP' });
   };
   
   document.getElementById('btn-reset').onclick = () => {
     wsClient.send('SIMULATION_CONTROL', { action: 'RESET' });
   };
   
   // Zakładki
   document.querySelectorAll('.tab').forEach(tab => {
     tab.onclick = () => switchTab(tab.dataset.tab);
   });
   
   function switchTab(tabId) {
     document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
     document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
     
     document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
     document.getElementById(`tab-${tabId}`).classList.add('active');
   }
   
   function updateUI(state) {
     // Aktualizacja widoków (wywołanie rendererów)
     if (document.getElementById('tab-hmi').classList.contains('active')) {
       HMIRenderer.render(state);
     }
     // ...
   }
   ```

**Kryteria akceptacji:**
- [x] app.js utworzony
- [x] Kontrolki działają
- [x] Zakładki działają
- [x] Stan aktualizuje się

---

### Zadanie 3.4: Moduły Utility (Helpers.js)
**Czas:** 1h  
**Priorytet:** Niski  
**Zależności:** -

**Kroki:**
1. Utwórz `client/js/Helpers.js`:
   ```javascript
   const Helpers = {
     formatTemp(temp) {
       return temp.toFixed(1) + '°C';
     },
     
     formatTime(seconds) {
       const hours = Math.floor(seconds / 3600);
       const minutes = Math.floor((seconds % 3600) / 60);
       return `${hours}h ${minutes}m`;
     },
     
     formatTimestamp(timestamp) {
       return new Date(timestamp).toLocaleString('pl-PL');
     },
     
     getScenarioColor(scenarioId) {
       const colors = {
         'S0': '#555',
         'S1': '#4CAF50',
         'S2': '#8BC34A',
         'S3': '#FFC107',
         'S4': '#FF9800',
         'S5': '#FF5722',
         'S6': '#F44336',
         'S7': '#E91E63',
         'S8': '#9C27B0'
       };
       return colors[scenarioId] || '#555';
     }
   };
   ```

**Kryteria akceptacji:**
- [x] Helpers.js utworzony
- [x] Funkcje działają

---

### Zadanie 3.5: Panel Statusu
**Czas:** 2h  
**Priorytet:** Średni  
**Zależności:** Zadanie 3.3

**Kroki:**
1. Dodanie panelu statusu do `index.html`:
   ```html
   <aside id="status-panel">
     <div class="status-item">
       <label>Scenariusz:</label>
       <span id="status-scenario">S0</span>
     </div>
     <div class="status-item">
       <label>Układ:</label>
       <span id="status-uklad">-</span>
     </div>
     <div class="status-item">
       <label>T zewn:</label>
       <span id="status-t-zewn">-</span>
     </div>
     <div class="status-item">
       <label>T szybu:</label>
       <span id="status-t-szyb">-</span>
     </div>
   </aside>
   ```

2. Aktualizacja w `app.js`

**Kryteria akceptacji:**
- [x] Panel statusu wyświetla się
- [x] Dane aktualizują się w czasie rzeczywistym

---

## FAZA 4: Frontend - Panel HMI

**Cel:** Wizualizacja synoptyczna z SVG

### Zadanie 4.1: Renderer HMI (HMIRenderer.js)
**Czas:** 4h  
**Priorytet:** Wysoki  
**Zależności:** Faza 3

**Kroki:**
1. Utwórz `client/js/HMIRenderer.js`:
   ```javascript
   const HMIRenderer = {
     currentSVG: null,
     svgContainer: null,
     
     init() {
       this.svgContainer = document.getElementById('hmi-svg-container');
     },
     
     render(state) {
       // Wybór odpowiedniego SVG
       const svgFile = this.selectSVG(state);
       
       if (this.currentSVG !== svgFile) {
         this.loadSVG(svgFile);
       }
       
       // Aktualizacja elementów SVG
       this.updateElements(state);
     },
     
     selectSVG(state) {
       const scenario = state.scenario.current;
       const uklad = state.scenario.uklad_pracy;
       
       // Logika wyboru SVG zgodnie z dokumentacją
       if (['S1', 'S2', 'S3', 'S4'].includes(scenario) && 
           uklad === 'Ograniczony') {
         return `assets/svg/nawiew_${scenario}_uklad_ograniczony.svg`;
       }
       
       return `assets/svg/nawiew_scenariusz_${scenario}.svg`;
     },
     
     loadSVG(file) {
       fetch(file)
         .then(response => response.text())
         .then(svgText => {
           this.svgContainer.innerHTML = svgText;
           this.currentSVG = file;
         })
         .catch(error => {
           console.error('Error loading SVG:', error);
         });
     },
     
     updateElements(state) {
       // Aktualizacja kolorów nagrzewnic
       state.heaters.forEach(heater => {
         const element = document.getElementById(`svg-${heater.id}`);
         if (element) {
           element.style.fill = heater.active ? '#4CAF50' : '#555';
         }
       });
       
       // Aktualizacja wartości tekstowych
       this.updateTextElements(state);
     },
     
     updateTextElements(state) {
       // Temperatury nagrzewnic
       state.heaters.forEach(heater => {
         const textEl = document.getElementById(`text-${heater.id}-temp`);
         if (textEl) {
           textEl.textContent = Helpers.formatTemp(heater.temp_wylot);
         }
       });
       
       // Wentylatory
       state.fans.forEach(fan => {
         const textEl = document.getElementById(`text-${fan.id}-freq`);
         if (textEl) {
           textEl.textContent = `${fan.czestotliwosc.toFixed(1)} Hz`;
         }
       });
     }
   };
   ```

2. Modyfikacja plików SVG:
   - Dodanie ID do elementów (nagrzewnice, wentylatory, teksty)
   - Przygotowanie elementów do manipulacji z JavaScript

**Kryteria akceptacji:**
- [x] HMIRenderer utworzony
- [x] SVG ładowane dynamicznie
- [x] Elementy aktualizują się
- [x] Kolory zmieniają się zgodnie ze stanem

---

### Zadanie 4.2: Edycja Plików SVG
**Czas:** 6h  
**Priorytet:** Wysoki  
**Zależności:** Zadanie 4.1

**Kroki:**
1. Dla każdego pliku SVG (21 plików):
   - Otwórz w edytorze (Inkscape / Visual Studio Code)
   - Dodaj ID do elementów:
     ```xml
     <!-- Nagrzewnica N1 -->
     <rect id="svg-N1" ... />
     <text id="text-N1-temp">45.0°C</text>
     
     <!-- Wentylator W1 -->
     <circle id="svg-W1" ... />
     <text id="text-W1-freq">40 Hz</text>
     ```

2. Grupowanie elementów (dla lepszej organizacji)

**Kryteria akceptacji:**
- [x] Wszystkie SVG zmodyfikowane
- [x] ID dodane do kluczowych elementów
- [x] Pliki nadal poprawnie wyświetlają się

---

### Zadanie 4.3: Animacje Przepływu (opcjonalnie)
**Czas:** 3h  
**Priorytet:** Niski  
**Zależności:** Zadanie 4.2

**Kroki:**
1. CSS animacje dla linii przepływu
2. SVG `<animateMotion>` dla kropek przepływu

**Kryteria akceptacji:**
- [x] Animacje działają
- [x] Wydajność dobra (>30 FPS)

---

### Zadanie 4.4: Tooltips w HMI
**Czas:** 2h  
**Priorytet:** Niski  
**Zależności:** Zadanie 4.1

**Kroki:**
1. Dodanie event listenerów do elementów SVG:
   ```javascript
   element.onmouseover = (e) => {
     showTooltip(e, heater);
   };
   ```

2. Wyświetlanie szczegółowych informacji w tooltipie

**Kryteria akceptacji:**
- [x] Tooltips wyświetlają się przy hover
- [x] Zawierają szczegółowe dane

---

## FAZA 5: Frontend - Formularze i Wykresy

**Cel:** Formularz konfiguracji i wykresy trendów

### Zadanie 5.1: Formularz Konfiguracji (ConfigForm.js)
**Czas:** 4h  
**Priorytet:** Wysoki  
**Zależności:** Faza 3

**Kroki:**
1. HTML formularz w `index.html` (tab-config):
   ```html
   <form id="config-form">
     <fieldset>
       <legend>Temperatury zadane</legend>
       <label>Tz (nagrzewnica) [°C]:</label>
       <input type="number" name="Tz" min="30" max="70" step="1" value="50">
       
       <label>Ts (szyb) [°C]:</label>
       <input type="number" name="Ts" min="-5" max="10" step="0.5" value="2">
     </fieldset>
     
     <!-- ... więcej sekcji ... -->
     
     <button type="submit">Zapisz</button>
   </form>
   ```

2. Utwórz `client/js/ConfigForm.js`:
   ```javascript
   const ConfigForm = {
     init() {
       this.form = document.getElementById('config-form');
       this.form.onsubmit = (e) => this.handleSubmit(e);
       
       // Walidacja w czasie rzeczywistym
       this.form.querySelectorAll('input').forEach(input => {
         input.oninput = () => this.validateField(input);
       });
     },
     
     handleSubmit(e) {
       e.preventDefault();
       
       if (!this.validate()) {
         alert('Błędy w formularzu');
         return;
       }
       
       const config = this.getFormData();
       wsClient.send('CONFIG_UPDATE', config);
     },
     
     getFormData() {
       const formData = new FormData(this.form);
       const config = {};
       
       for (const [key, value] of formData.entries()) {
         config[key] = parseFloat(value) || value;
       }
       
       return config;
     },
     
     validate() {
       let valid = true;
       this.form.querySelectorAll('input').forEach(input => {
         if (!this.validateField(input)) {
           valid = false;
         }
       });
       return valid;
     },
     
     validateField(input) {
       const value = parseFloat(input.value);
       const min = parseFloat(input.min);
       const max = parseFloat(input.max);
       
       if (isNaN(value) || value < min || value > max) {
         input.classList.add('error');
         return false;
       }
       
       input.classList.remove('error');
       return true;
     },
     
     loadConfig(config) {
       for (const [key, value] of Object.entries(config)) {
         const input = this.form.querySelector(`[name="${key}"]`);
         if (input) {
           input.value = value;
         }
       }
     }
   };
   ```

**Kryteria akceptacji:**
- [x] Formularz utworzony
- [x] Walidacja działa
- [x] Zapis konfiguracji działa
- [x] Ładowanie konfiguracji działa

---

### Zadanie 5.2: Wykresy Trendów (ChartRenderer.js)
**Czas:** 5h  
**Priorytet:** Średni  
**Zależności:** Faza 3

**Kroki:**
1. Decyzja: Canvas API vs Chart.js
   - Jeśli Canvas API: implementacja od zera
   - Jeśli Chart.js: `npm install chart.js`

2. Utwórz `client/js/ChartRenderer.js`:
   ```javascript
   const ChartRenderer = {
     charts: {},
     data: {
       t_zewn: [],
       t_szyb: [],
       heaters: [[], [], [], [], [], [], [], []],
       fans: [[], []]
     },
     maxPoints: 86400, // 24h przy 1s
     
     init() {
       this.createCharts();
     },
     
     createCharts() {
       // Wykres temperatury zewnętrznej
       this.charts.t_zewn = new Chart(
         document.getElementById('chart-t-zewn'),
         {
           type: 'line',
           data: {
             labels: [],
             datasets: [{
               label: 'T zewn [°C]',
               data: [],
               borderColor: '#2196F3'
             }]
           }
         }
       );
       
       // ... więcej wykresów ...
     },
     
     update(state) {
       const timestamp = new Date(state.timestamp);
       
       // Dodaj nowe punkty danych
       this.data.t_zewn.push({
         x: timestamp,
         y: state.input.t_zewn
       });
       
       this.data.t_szyb.push({
         x: timestamp,
         y: state.shaft_temp.poziom_minus30
       });
       
       // Ogranicz ilość punktów
       if (this.data.t_zewn.length > this.maxPoints) {
         this.data.t_zewn.shift();
       }
       
       // Aktualizuj wykresy
       this.charts.t_zewn.data.datasets[0].data = this.data.t_zewn;
       this.charts.t_zewn.update('none'); // No animation
     }
   };
   ```

**Kryteria akceptacji:**
- [x] Wykresy wyświetlają się
- [x] Dane aktualizują się w czasie rzeczywistym
- [x] Wydajność dobra (>30 FPS)
- [x] Zoom/pan (opcjonalnie)

---

### Zadanie 5.3: Panel Alarmów (AlarmPanel.js)
**Czas:** 2h  
**Priorytet:** Średni  
**Zależności:** Faza 3

**Kroki:**
1. HTML tabela alarmów
2. Utwórz `client/js/AlarmPanel.js`
3. Kwituowanie alarmów
4. Dźwięk alarmu (HTML5 Audio API)

**Kryteria akceptacji:**
- [x] Alarmy wyświetlają się
- [x] Kwituowanie działa
- [x] Dźwięk odtwarza się (krytyczne)

---

### Zadanie 5.4: Panel Rotacji (RotationPanel.js)
**Czas:** 3h  
**Priorytet:** Średni  
**Zależności:** Faza 3

**Kroki:**
1. Zakładki 5A i 5B
2. Wyświetlanie statystyk rotacji
3. Historia rotacji (tabela)
4. Wykresy czasu pracy (Canvas API - bar chart)

**Kryteria akceptacji:**
- [x] Panel rotacji wyświetla się
- [x] Statystyki poprawne
- [x] Wykresy działają

---

## FAZA 6: Integracja i Testy

**Cel:** Testy end-to-end, optymalizacja, bugfixy

### Zadanie 6.1: Testy Integracyjne
**Czas:** 4h  
**Priorytet:** Krytyczny  
**Zależności:** Fazy 1-5

**Kroki:**
1. Scenariusz testowy 1: Pełny cykl S0 → S8 → S0
2. Scenariusz testowy 2: Rotacja 5A (przyspieszony okres)
3. Scenariusz testowy 3: Rotacja 5B (przyspieszony okres)
4. Scenariusz testowy 4: Tryb MANUAL
5. Scenariusz testowy 5: Awarie (nagrzewnica, wentylator)

**Kryteria akceptacji:**
- [x] Wszystkie scenariusze przechodzą
- [x] Brak błędów w konsoli
- [x] Wydajność OK

---

### Zadanie 6.2: Optymalizacja Wydajności
**Czas:** 2h  
**Priorytet:** Średni  
**Zależności:** Zadanie 6.1

**Kroki:**
1. Profiling (Chrome DevTools)
2. Optymalizacja renderowania SVG
3. Throttling aktualizacji wykresów
4. Downsampling danych historycznych

**Kryteria akceptacji:**
- [x] CPU < 10%
- [x] Memory stable (no leaks)
- [x] FPS > 30

---

### Zadanie 6.3: Bugfixy
**Czas:** 2h  
**Priorytet:** Wysoki  
**Zależności:** Zadanie 6.1

**Kroki:**
1. Lista bugów z testów
2. Priorytetyzacja
3. Naprawy

**Kryteria akceptacji:**
- [x] Krytyczne bugi naprawione
- [x] Stabilność aplikacji

---

### Zadanie 6.4: Cross-browser Testing
**Czas:** 1h  
**Priorytet:** Niski  
**Zależności:** Zadanie 6.3

**Kroki:**
1. Test w Chrome
2. Test w Firefox
3. Test w Edge (opcjonalnie Safari)

**Kryteria akceptacji:**
- [x] Działa w głównych przeglądarkach

---

### Zadanie 6.5: Responsywność Mobile
**Czas:** 1h  
**Priorytet:** Niski  
**Zależności:** Zadanie 6.4

**Kroki:**
1. Test na tablet (1024x768)
2. Ewentualne poprawki CSS

**Kryteria akceptacji:**
- [x] Działa na tabletach

---

## FAZA 7: Dokumentacja

**Cel:** README, User Manual, Technical Docs

### Zadanie 7.1: README.md
**Czas:** 1h  
**Priorytet:** Wysoki  
**Zależności:** Faza 6

**Kroki:**
1. Opis projektu
2. Instalacja i uruchomienie
3. Konfiguracja
4. Screenshoty

**Kryteria akceptacji:**
- [x] README kompletny
- [x] Instrukcje działają

---

### Zadanie 7.2: User Manual
**Czas:** 2h  
**Priorytet:** Średni  
**Zależności:** Zadanie 7.1

**Kroki:**
1. Utworzenie `docs/USER_MANUAL.md`
2. Opis interfejsu
3. Przykłady użycia

**Kryteria akceptacji:**
- [x] User manual kompletny

---

### Zadanie 7.3: Technical Documentation
**Czas:** 1h  
**Priorytet:** Niski  
**Zależności:** Zadanie 7.2

**Kroki:**
1. Utworzenie `docs/TECHNICAL.md`
2. Opis architektury
3. API Reference (WebSocket)

**Kryteria akceptacji:**
- [x] Technical docs kompletne

---

## Podsumowanie Zadań

| Faza | Liczba Zadań | Łączny Czas |
|------|--------------|-------------|
| 0 - Setup | 5 | 2h |
| 1 - Backend Core | 7 | 15h |
| 2 - Algorytmy | 5 | 20h |
| 3 - Frontend Podstawy | 5 | 12h |
| 4 - Panel HMI | 4 | 15h |
| 5 - Formularze/Wykresy | 4 | 12h |
| 6 - Testy | 5 | 10h |
| 7 - Dokumentacja | 3 | 4h |
| **TOTAL** | **38** | **90h** |

---

## Kontrola Jakości

### Definicja "Done" dla Zadania:
- [x] Kod napisany i przetestowany lokalnie
- [x] Linter (ESLint) nie pokazuje błędów
- [x] Testy jednostkowe przechodzą (jeśli dotyczy)
- [x] Kod zcommitowany do git
- [x] Dokumentacja zaktualizowana (jeśli dotyczy)

### Checklisty Milestones:

**Milestone 1: Backend działa**
- [x] Symulacja uruchamia się i działa stabilnie
- [x] WebSocket broadcast działa
- [x] Scenariusze przełączają się poprawnie
- [x] Regulatory PID działają

**Milestone 2: Algorytmy rotacji działają**
- [x] Rotacja 5A wykonuje się automatycznie
- [x] Rotacja 5B wykonuje się automatycznie
- [x] Liczniki czasu są poprawne

**Milestone 3: Frontend podstawowy działa**
- [x] Interfejs wyświetla się
- [x] WebSocket połączenie działa
- [x] Kontrolki (start/stop) działają

**Milestone 4: HMI wizualizacja działa**
- [x] SVG ładowane dynamicznie
- [x] Kolory aktualizują się
- [x] Wartości wyświetlają się

**Milestone 5: Aplikacja kompletna**
- [x] Wszystkie funkcje działają
- [x] Testy przechodzą
- [x] Dokumentacja gotowa

---

## Zarządzanie Ryzykiem

| Ryzyko | Prawdopodobieństwo | Wpływ | Mitigacja |
|--------|-------------------|-------|-----------|
| Problemy z wydajnością WebSocket | Średnie | Wysoki | Throttling broadcast, kompresja |
| Błędy w algorytmach rotacji | Średnie | Wysoki | Dokładne testy, code review |
| Problemy z SVG (duże pliki) | Niskie | Średni | Optymalizacja SVG, lazy loading |
| Niekompatybilność przeglądarek | Niskie | Niski | Testy cross-browser |
| Przekroczenie czasu realizacji | Średnie | Średni | Priorytetyzacja zadań, MVP first |

---

## Harmonogram Realizacji (Przykładowy)

**Tydzień 1:**
- Faza 0: Setup
- Faza 1: Backend Core (częściowo)

**Tydzień 2:**
- Faza 1: Backend Core (dokończenie)
- Faza 2: Algorytmy (częściowo)

**Tydzień 3:**
- Faza 2: Algorytmy (dokończenie)
- Faza 3: Frontend Podstawy

**Tydzień 4:**
- Faza 4: Panel HMI
- Faza 5: Formularze/Wykresy (częściowo)

**Tydzień 5:**
- Faza 5: Formularze/Wykresy (dokończenie)
- Faza 6: Testy
- Faza 7: Dokumentacja

---

## Następne Kroki

1. **Code Review** punktów krytycznych (PID, rotacje)
2. **Ustalenie nastaw PID** (tuning podczas testów)
3. **Feedback od użytkownika końcowego**
4. **Ewentualne rozszerzenia** (Faza 2 z implementation.md)

---

**Koniec dokumentu planu**

Data stworzenia: 2025-11-21  
Wersja: 1.0  
Status: Gotowy do realizacji

Powodzenia w implementacji! 🚀

