# Dokumentacja Systemu Sterowania BOGDANKA Szyb 2

Kompleksowa dokumentacja systemu automatycznego sterowania ogrzewaniem szybu wydobywczego.

## 📁 Struktura Dokumentacji

### [00-start](./00-start/) - START
- `start.md` - Przewodnik po dokumentacji
- Szybki start dla nowych użytkowników

### [01-system](./01-system/) - Architektura Systemu
- `system.md` - Szczegółowy opis systemu sterowania
- Definicje podsystemów PARTPG i PARTS
- Warunki załączania/wyłączania
- Scenariusze pracy (S0-S8)
- Układy automatycznej regulacji (UAR)

### [02-algorytmy](./02-algorytmy/) - Algorytmy Sterowania
- `algorytmy.md` - Przegląd algorytmów WS, RC, RN
- `algorytmy.md#algorytm-ws-automatyczny-wybór-scenariusza-pracy` - Automatyczny wybór scenariusza
- `algorytmy.md#algorytm-rc-cykliczna-rotacja-układów-pracy-ciągów` - Rotacja układów pracy ciągów
- `algorytmy.md#algorytm-rn-cykliczna-rotacja-nagrzewnic-w-obrębie-ciągu` - Rotacja nagrzewnic w ciągu
- `_ARCHIVE_pelny-dokument.md` - Archiwum oryginalnej dokumentacji

### [03-projekt-instalacji](./03-projekt-instalacji/) - Projekt Instalacji
- Szczegóły instalacji ogrzewania szybu
- Schematy instalacji (SVG)

### [04-analizy](./04-analizy/) - Analizy i Wyjaśnienia
- `pytania-wyjasnienia.md` - Pytania i wyjaśnienia wymagań
- Dodatkowe analizy techniczne

## 🎯 Nawigacja

**Dla nowych użytkowników:**
1. Zacznij od [START](./00-start/start.md)
2. Przeczytaj [Architekturę Systemu](./01-system/system.md)
3. Zapoznaj się z [Algorytmami](./02-algorytmy/algorytmy.md)

**Dla programistów:**
- Algorytmy: `02-algorytmy/`
- Wizualizacje: `./03-projekt-instalacji/projekt-instalacji.md`

**Dla inżynierów:**
- Projekt instalacji: `03-projekt-instalacji/`
- Schematy: `03-projekt-instalacji/schematy/`

## 📊 Wizualizacje

Wszystkie diagramy SVG znajdują się w katalogu [wizualizacje](./03-projekt-instalacji/projekt-instalacji.md):
- Flowcharty algorytmów
- Scenariusze pracy
- Schematy rotacji
- Schematy UAR

## 📝 Konwencje

- **Pliki MD**: kebab-case (np. `algorytmy.md#algorytm-ws-automatyczny-wybór-scenariusza-pracy`)
- **Katalogi**: numerowane prefiksem dla kolejności (np. `00-start/`)
- **Wizualizacje**: oddzielny katalog `doc./03-projekt-instalacji/projekt-instalacji.md`

## 🔗 Powiązania

- Kod algorytmów (PLC): *(będzie dodane w przyszłości)*
- Symulacje: *(będzie dodane w przyszłości)*
- Serwisy: *(będzie dodane w przyszłości)*

