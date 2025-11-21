# BOGDANKA Szyb 2 - Aplikacja Symulacji

## 📋 Przegląd Projektu

Aplikacja webowa symulująca w czasie rzeczywistym **System Automatycznej Regulacji (SAR)** temperatury szybu kopalnianego BOGDANKA Szyb 2.

### Funkcjonalność:
- ✅ 8 nagrzewnic (N1-N8) w dwóch ciągach wentylacyjnych
- ✅ 2 wentylatory (W1, W2) ze sterowaniem częstotliwościowym (25-50 Hz)
- ✅ 9 scenariuszy pracy (S0-S8) zależnych od temperatury zewnętrznej
- ✅ Algorytm 5A: cykliczna rotacja układów pracy ciągów (Podstawowy ↔ Ograniczony)
- ✅ Algorytm 5B: cykliczna rotacja nagrzewnic w obrębie ciągu
- ✅ Regulatory PID dla temperatury powietrza i prędkości wentylatorów
- ✅ Wizualizacja HMI w czasie rzeczywistym (SVG)
- ✅ Wykresy trendów, alarmy, konfiguracja parametrów

---

## 📚 Dokumentacja

Ten katalog (`app/`) zawiera **pełną dokumentację planowania i implementacji**:

### 1️⃣ **[implementation.md](implementation.md)** - Wytyczne Implementacji
Szczegółowa specyfikacja techniczna zawierająca:
- Architekturę aplikacji (Backend: Node.js + WebSocket, Frontend: Vanilla JS)
- Model danych (SystemState)
- Opis wszystkich komponentów (SimulationEngine, PID Controller, HeaterController, FanController)
- Algorytmy rotacji 5A i 5B (pseudokod)
- Protokół komunikacji WebSocket
- Specyfikację interfejsu użytkownika (HMI, formularze, wykresy)
- Strukturę projektu (katalogi, pliki)

**Przeczytaj najpierw ten dokument**, aby zrozumieć architekturę!

### 2️⃣ **[plan.md](plan.md)** - Plan Zadań Programistycznych
Kompleksowy plan realizacji podzielony na **38 zadań w 7 fazach**:

| Faza | Nazwa | Czas | Zadania |
|------|-------|------|---------|
| **0** | Setup Projektu | 2h | 5 |
| **1** | Backend - Core | 15h | 7 |
| **2** | Backend - Algorytmy | 20h | 5 |
| **3** | Frontend - Podstawy | 12h | 5 |
| **4** | Frontend - HMI | 15h | 4 |
| **5** | Frontend - Formularze i Wykresy | 12h | 4 |
| **6** | Integracja i Testy | 10h | 5 |
| **7** | Dokumentacja | 4h | 3 |
| **Σ** | **TOTAL** | **90h** | **38** |

**Każde zadanie zawiera:**
- Szczegółowe kroki wykonania
- Gotowy kod do wklejenia
- Kryteria akceptacji
- Zależności od innych zadań

---

## 🚀 Szybki Start - Jak Zacząć?

### Krok 1: Przeczytaj Dokumentację
```bash
# Otwórz i przeczytaj:
1. implementation.md  # Zrozum architekturę
2. plan.md            # Zobacz plan realizacji
```

### Krok 2: Przygotuj Środowisko
Wymagania:
- **Node.js** >= 18.x
- **npm** >= 9.x
- Przeglądarka: Chrome/Firefox/Edge

### Krok 3: Rozpocznij Implementację

#### Opcja A: Katalog w tym samym repozytorium
```bash
# Utwórz katalog projektu obok app/
cd /Users/lukaszswolkien/Devel/my-github/BOGDANKA
mkdir bogdanka-simulation
cd bogdanka-simulation

# Przejdź do Fazy 0 - Setup Projektu (plan.md, linia 28)
# Wykonaj Zadanie 0.1: Inicjalizacja Projektu Node.js
npm init -y
npm install express ws
npm install --save-dev eslint mocha
```

#### Opcja B: Osobne repozytorium
```bash
# Utwórz nowe repo
mkdir ~/bogdanka-simulation
cd ~/bogdanka-simulation
git init

# Skopiuj dokumentację
cp /path/to/BOGDANKA/app/* ./docs/

# Rozpocznij implementację od Fazy 0
```

### Krok 4: Realizuj Zadanie po Zadaniu
Otwórz `plan.md` i wykonuj zadania sekwencyjnie:
1. **Zadanie 0.1** → Inicjalizacja npm
2. **Zadanie 0.2** → Struktura katalogów
3. **Zadanie 0.3** → ESLint
4. **Zadanie 0.4** → Pliki konfiguracyjne
5. **Zadanie 0.5** → Prosty serwer HTTP
6. ... i tak dalej przez wszystkie 38 zadań

---

## 🛠️ Stack Technologiczny

### Backend:
- **Node.js** 18+ (runtime)
- **Express.js** (HTTP server)
- **ws** (WebSocket library)
- Brak frameworków - czysty JavaScript

### Frontend:
- **Vanilla JavaScript** (bez React/Vue/Angular)
- **HTML5 + CSS3**
- **SVG** (wizualizacja HMI)
- **Canvas API** lub Chart.js (wykresy)

### Minimalne Zależności:
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

## 📁 Struktura Docelowa Projektu

```
bogdanka-simulation/
│
├── server/
│   ├── index.js                    # Główny plik serwera
│   ├── config/
│   │   └── default-config.js       # Domyślne parametry
│   ├── simulation/
│   │   ├── SimulationEngine.js     # Silnik symulacji (1s tick)
│   │   ├── SystemState.js          # Model stanu
│   │   ├── ScenarioManager.js      # Zarządzanie S0-S8
│   │   ├── PIDController.js        # Regulator PID
│   │   └── AlarmSystem.js          # System alarmów
│   ├── controllers/
│   │   ├── HeaterController.js     # Kontroler nagrzewnic
│   │   ├── FanController.js        # Kontroler wentylatorów
│   │   └── DamperController.js     # Kontroler przepustnic
│   ├── algorithms/
│   │   ├── Rotation5A.js           # Algorytm rotacji układów
│   │   └── Rotation5B.js           # Algorytm rotacji nagrzewnic
│   └── utils/
│       ├── Logger.js
│       └── StateMachine.js
│
├── client/
│   ├── index.html                  # Strona główna
│   ├── css/
│   │   ├── main.css
│   │   ├── hmi.css
│   │   └── forms.css
│   ├── js/
│   │   ├── app.js                  # Główna logika
│   │   ├── WebSocketClient.js      # Klient WS
│   │   ├── HMIRenderer.js          # Renderer SVG
│   │   ├── ConfigForm.js           # Formularz
│   │   ├── ChartRenderer.js        # Wykresy
│   │   └── AlarmPanel.js           # Alarmy
│   └── assets/
│       └── svg/                    # 21 plików SVG
│
├── shared/
│   └── constants.js                # Wspólne stałe
│
├── tests/
│   ├── pid.test.js
│   ├── rotation5a.test.js
│   └── rotation5b.test.js
│
├── package.json
├── README.md
└── .gitignore
```

---

## ⚙️ Kluczowe Komponenty

### 1. SimulationEngine
Główna pętla symulacji wykonywana co 1 sekundę:
1. Odczyt temperatury zewnętrznej
2. Określenie scenariusza (S0-S8)
3. Aktualizacja nagrzewnic (HeaterController)
4. Aktualizacja wentylatorów (FanController)
5. Regulacja PID
6. Symulacja temperatury w szybie
7. Sprawdzenie rotacji 5A i 5B
8. Broadcast stanu przez WebSocket

### 2. PIDController
Regulator PID z anty-windupem:
```
e(t) = SP - PV
P = Kp * e(t)
I += Ki * e(t) * dt
D = Kd * (e(t) - e(t-1)) / dt
CV = P + I + D
```

### 3. Rotation5A (Rotacja Układów)
Cykliczna zmiana: Układ Podstawowy ↔ Układ Ograniczony
- Wyrównanie eksploatacji ciągu 1 (W1) vs ciągu 2 (W2)
- Okres: definiowany przez technologa (np. 168h)

### 4. Rotation5B (Rotacja Nagrzewnic)
Wymiana: najdłużej pracująca → postój, najdłużej w postoju → praca
- Wyrównanie eksploatacji N1-N8
- Okres: definiowany przez technologa (np. 168h)

---

## 🎯 Ścieżka Nauki

### Dla Początkujących:
1. Zacznij od przeczytania **implementation.md** (sekcje 1-3)
2. Zobacz **plan.md** - Fazę 0 i Fazę 1
3. Rozpocznij od Zadania 0.1 i idź krok po kroku
4. Testuj każde zadanie przed przejściem do następnego

### Dla Zaawansowanych:
1. Przejrzyj całą dokumentację
2. Zrozum algorytmy rotacji (implementation.md, sekcje 4.4-4.5)
3. Możesz modyfikować plan według swoich potrzeb
4. Skup się na kluczowych komponentach (PID, rotacje)

---

## 📊 Metryki Projektu

- **Łączny czas realizacji (człowiek):** ~90 godzin
- **Łączny czas realizacji (człowiek + AI):** ~20-30 godzin
- **Liczba zadań:** 38
- **Liczba plików źródłowych:** ~30
- **Liczba plików SVG:** 21
- **Liczba scenariuszy:** 9 (S0-S8)
- **Liczba nagrzewnic:** 8 (N1-N8)
- **Liczba wentylatorów:** 2 (W1-W2)

---

## ✅ Kryteria Ukończenia

### Milestone 1: Backend działa
- [x] Symulacja uruchamia się i działa stabilnie
- [x] WebSocket broadcast działa
- [x] Scenariusze przełączają się poprawnie
- [x] Regulatory PID działają

### Milestone 2: Algorytmy rotacji działają
- [x] Rotacja 5A wykonuje się automatycznie
- [x] Rotacja 5B wykonuje się automatycznie
- [x] Liczniki czasu są poprawne

### Milestone 3: Frontend podstawowy działa
- [x] Interfejs wyświetla się
- [x] WebSocket połączenie działa
- [x] Kontrolki (start/stop) działają

### Milestone 4: HMI wizualizacja działa
- [x] SVG ładowane dynamicznie
- [x] Kolory aktualizują się
- [x] Wartości wyświetlają się

### Milestone 5: Aplikacja kompletna
- [x] Wszystkie funkcje działają
- [x] Testy przechodzą
- [x] Dokumentacja gotowa

---

## 🔗 Linki do Dokumentacji Źródłowej

W głównym repozytorium znajdziesz:
- `../Doc/System Sterowania BOGDANKA szyb 2.md` - Specyfikacja systemu
- `../Doc/Algorytmy_rotacji.md` - Szczegółowy opis algorytmów 5A i 5B
- `../symulacja.md` - Wizualizacje HMI i scenariusze
- `../Symulacja/*.svg` - 21 plików SVG do skopiowania

---

## 🐛 Troubleshooting

### Problem: WebSocket nie łączy się
```bash
# Sprawdź czy port 3001 jest wolny
lsof -i :3001
# Zmień port w server/index.js i client/js/app.js
```

### Problem: SVG nie ładują się
```bash
# Sprawdź czy pliki SVG są w client/assets/svg/
ls client/assets/svg/
# Powinno być 21 plików
```

### Problem: Testy nie przechodzą
```bash
# Uruchom testy z verbose
npm test -- --reporter spec
```

---

## 📝 Notatki

### Nastawy PID
Wartości domyślne (do strojenia podczas testów):
- **Nagrzewnice:** Kp=2.0, Ki=0.1, Kd=0.05
- **Wentylatory:** Kp=1.5, Ki=0.08, Kd=0.03

### Prędkość Symulacji
Można przyspieszyć symulację (do testów):
- 1x = czas rzeczywisty
- 10x = 10 sekund symulacji = 1 sekunda rzeczywista
- 100x = do testów rotacji (zmniejsz okresy do 60s)

---

## 👥 Wsparcie

Jeśli masz pytania:
1. Sprawdź **implementation.md** (sekcja odpowiadająca tematowi)
2. Zobacz **plan.md** (szczegóły zadania)
3. Przejrzyj dokumentację źródłową w `../Doc/`

---

## 📜 Licencja

Projekt wewnętrzny - BOGDANKA Szyb 2

---

**Ostatnia aktualizacja:** 2025-11-21  
**Wersja:** 1.0  
**Status:** Gotowe do implementacji

---

## 🚀 Następny krok:

```bash
# Utwórz katalog projektu
mkdir bogdanka-simulation
cd bogdanka-simulation

# Rozpocznij od Zadania 0.1 w plan.md
npm init -y
```

**Powodzenia! 💪**

