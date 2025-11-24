# START - Przewodnik po Dokumentacji

## 👋 Witaj w Dokumentacji Systemu BOGDANKA Szyb 2

To jest punkt startowy dla wszystkich użytkowników systemu automatycznego sterowania ogrzewaniem szybu wydobywczego.

## 🎯 Dla Kogo Jest Ta Dokumentacja?

### 👨‍💻 Programiści PLC/SCADA
**Zacznij tutaj:**
1. [Architektura Systemu](../01-system/architektura.md) - zrozum strukturę
2. [Algorytmy Sterowania](../02-algorytmy/README.md) - poznaj logikę
3. [Wizualizacje Algorytmów](../../visualization/algorytmy/) - zobacz flowcharty

**Co znajdziesz:**
- Pseudokod algorytmów 5, 5A, 5B
- Diagramy przepływu
- Parametry konfiguracyjne
- Obsługa stanów awaryjnych

### 👷 Inżynierowie/Technolodzy
**Zacznij tutaj:**
1. [Scenariusze Pracy](../01-system/architektura.md#5-scenariusze) - tabela S0-S8
2. [Projekt Instalacji](../03-projekt-instalacji/) - schematy instalacji
3. [Wizualizacje Scenariuszy](../../visualization/scenariusze/) - diagramy nawiewu

**Co znajdziesz:**
- Zakresy temperatur dla scenariuszy
- Konfiguracje nagrzewnic i wentylatorów
- Schematy instalacji grzewczej
- Warunki załączania/wyłączania

### 👔 Kierownicy Projektów/Analitycy
**Zacznij tutaj:**
1. [Przegląd Systemu](../01-system/architektura.md#1-wprowadzenie) - cel i zakres
2. [Pytania i Wyjaśnienia](../04-analizy/pytania-wyjasnienia.md) - wymagania
3. [Wycena Projektu](../../wycena_projektu.md) - szacunki czasowe i kosztowe

**Co znajdziesz:**
- Cele biznesowe systemu
- Wymagania funkcjonalne
- Analizy techniczne

## 📖 Struktura Dokumentacji

```
docs/
├── 00-start/           ← JESTEŚ TUTAJ
├── 01-system/          → Architektura (PARTPG, PARTS, UAR)
├── 02-algorytmy/       → Algorytmy 5, 5A, 5B
├── 03-projekt-instalacji/ → Projekt instalacji grzewczej
└── 04-analizy/         → Pytania, wyjaśnienia, analizy
```

## 🚀 Szybki Start - 15 Minut

### Krok 1: Zrozum Problem (5 min)
Szyb wydobywczy wymaga ogrzewania zimą. System musi:
- Utrzymywać temperaturę 2°C w szybie
- Automatycznie dobierać ilość nagrzewnic (1-8) zależnie od temp. zewnętrznej
- Równomiernie zużywać urządzenia (rotacja)

### Krok 2: Poznaj Scenariusze (5 min)
System ma 9 scenariuszy:
- **S0**: t ≥ 3°C → brak ogrzewania
- **S1-S4**: 1-4 nagrzewnice (jeden ciąg)
- **S5-S8**: 5-8 nagrzewnic (dwa ciągi)

📊 [Wizualizacje scenariuszy](../../visualization/scenariusze/)

### Krok 3: Zrozum Algorytmy (5 min)
Trzy kluczowe algorytmy:
- **Algorytm 5**: Wybiera scenariusz (S0-S8) na podstawie temp. zewnętrznej
- **Algorytm 5A**: Rotuje układy pracy (Ciąg 1 ↔ Ciąg 2) co X dni
- **Algorytm 5B**: Rotuje nagrzewnice w ciągu (N1↔N2↔N3↔N4) co Y dni

🔀 [Flowcharty algorytmów](../../visualization/algorytmy/)

## 📚 Kluczowe Dokumenty

| Dokument | Czas czytania | Opis |
|----------|---------------|------|
| [Architektura Systemu](../01-system/architektura.md) | 60 min | Kompletny opis systemu PARTPG i PARTS |
| [Przegląd Algorytmów](../02-algorytmy/README.md) | 15 min | Wprowadzenie do algorytmów 5, 5A, 5B |
| [Algorytm 5](../02-algorytmy/algorytm-5-wybor-scenariusza.md) | 45 min | Wybór scenariusza pracy |
| [Algorytm 5A](../02-algorytmy/algorytm-5A-rotacja-ukladow.md) | 30 min | Rotacja układów ciągów |
| [Algorytm 5B](../02-algorytmy/algorytm-5B-rotacja-nagrzewnic.md) | 45 min | Rotacja nagrzewnic |

## 🎨 Wizualizacje

Wszystkie diagramy SVG: [visualization/](../../visualization/)

| Kategoria | Ilość | Opis |
|-----------|-------|------|
| [Algorytmy](../../visualization/algorytmy/) | 4 | Flowcharty 5, 5A, 5B + koordynacja |
| [Scenariusze](../../visualization/scenariusze/) | 9 | Nawiew dla S0-S8 |
| [Rotacje](../../visualization/rotacje/) | 12 | Diagramy rotacji układów i nagrzewnic |
| [UAR](../../visualization/uar/) | 3 | Schematy regulacji |

## ❓ Często Zadawane Pytania

### Dlaczego potrzebujemy rotacji?
Bez rotacji: N1 pracuje 100% czasu → szybkie zużycie  
Z rotacją: N1, N2, N3, N4 po 25% czasu → równomierne zużycie

### Kiedy pracują dwa ciągi?
Dwa ciągi (C1 + C2) włączają się w S5-S8 (temp. < -11°C)

### Co to jest histereza?
Scenariusz włącza się przy jednej temperaturze, wyłącza przy wyższej.  
Przykład S1: włącza się przy 2°C, wyłącza się przy 3°C (histereza 1°C)

## 🔗 Powiązane Zasoby

- [Kod PLC](../../PLC/) - *(będzie dodane w przyszłości)*
- [Symulacje](../../Serwisy/) - *(będzie dodane w przyszłości)*
- [Testy](../../tests/) - *(będzie dodane w przyszłości)*

## 📞 Potrzebujesz Pomocy?

1. Sprawdź [Pytania i Wyjaśnienia](../04-analizy/pytania-wyjasnienia.md)
2. Zobacz [Archiwum](../02-algorytmy/_ARCHIVE_pelny-dokument.md) - pełna dokumentacja
3. Przejrzyj [Wizualizacje](../../visualization/)

---

**Następny krok:** [Architektura Systemu →](../01-system/architektura.md)

