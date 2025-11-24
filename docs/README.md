# Dokumentacja Systemu Sterowania BOGDANKA Szyb 2

Kompleksowa dokumentacja systemu automatycznego sterowania ogrzewaniem szybu wydobywczego.

## 📁 Struktura Dokumentacji

### [00-start](./00-start/) - START
- `README.md` - Przewodnik po dokumentacji
- Szybki start dla nowych użytkowników

### [01-system](./01-system/) - Architektura Systemu
- `architektura.md` - Szczegółowy opis systemu sterowania
- Definicje podsystemów PARTPG i PARTS
- Warunki załączania/wyłączania
- Scenariusze pracy (S0-S8)
- Układy automatycznej regulacji (UAR)

### [02-algorytmy](./02-algorytmy/) - Algorytmy Sterowania
- `README.md` - Przegląd algorytmów WS, RC, RN
- `algorytm-WS-wybor-scenariusza.md` - Automatyczny wybór scenariusza
- `algorytm-RC-rotacja-ciagow.md` - Rotacja układów pracy ciągów
- `algorytm-RN-rotacja-nagrzewnic.md` - Rotacja nagrzewnic w ciągu
- `_ARCHIVE_pelny-dokument.md` - Archiwum oryginalnej dokumentacji

### [03-projekt-instalacji](./03-projekt-instalacji/) - Projekt Instalacji
- Szczegóły instalacji ogrzewania szybu
- Schematy instalacji (SVG)

### [04-analizy](./04-analizy/) - Analizy i Wyjaśnienia
- `pytania-wyjasnienia.md` - Pytania i wyjaśnienia wymagań
- Dodatkowe analizy techniczne

## 🎯 Nawigacja

**Dla nowych użytkowników:**
1. Zacznij od [START](./00-start/README.md)
2. Przeczytaj [Architekturę Systemu](./01-system/architektura.md)
3. Zapoznaj się z [Algorytmami](./02-algorytmy/README.md)

**Dla programistów:**
- Algorytmy: `02-algorytmy/`
- Wizualizacje: `./03-projekt-instalacji/wizualizacja-systemu.md`

**Dla inżynierów:**
- Projekt instalacji: `03-projekt-instalacji/`
- Schematy: `03-projekt-instalacji/schematy/`

## 📊 Wizualizacje

Wszystkie diagramy SVG znajdują się w katalogu [wizualizacje](./03-projekt-instalacji/wizualizacja-systemu.md):
- Flowcharty algorytmów
- Scenariusze pracy
- Schematy rotacji
- Schematy UAR

## 📝 Konwencje

- **Pliki MD**: kebab-case (np. `algorytm-WS-wybor-scenariusza.md`)
- **Katalogi**: numerowane prefiksem dla kolejności (np. `00-start/`)
- **Wizualizacje**: oddzielny katalog `doc./03-projekt-instalacji/wizualizacja-systemu.md`

## 🔗 Powiązania

- Kod algorytmów (PLC): *(będzie dodane w przyszłości)*
- Symulacje: *(będzie dodane w przyszłości)*
- Serwisy: *(będzie dodane w przyszłości)*

