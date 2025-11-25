# Dokumentacja Systemu Sterowania BOGDANKA Szyb 2

**Dokumentacja systemu automatycznego sterowania ogrzewaniem szybu**

---

## 📁 Struktura Dokumentacji

### [01-system/system.md](./01-system/system.md) - Przegląd Systemu
- Komponenty (8 nagrzewnic, 2 wentylatory, 2 wyrzutnie)
- Architektura sterowania (SAR): PARTPG i PARTS
- Tabela scenariuszy (S0-S8) - referencyjna
- Przegląd algorytmów (WS, RC, RN)
- Parametry systemowe

### [02-projekt-instalacji/projekt-instalacji.md](./02-projekt-instalacji/projekt-instalacji.md) -  Instalacja Ogrzewania Szybu
- Układ instalacji ogrzewania szybu
- Schematy scenariuszy pracy (S0-S8)
- Przykłady stanów rotacji ciągów (RC) i nagrzewnic (RN)
- Schematy układów automatycznej regulacji (UAR)

### [03-algorytmy/algorytmy.md](./03-algorytmy/algorytmy.md) - Algorytmy Sterowania
- Szczegółowa dokumentacja logiki algorytmów:
  - Algorytm WS - automatyczny wybór scenariusza
  - Algorytm RC - cykliczna rotacja układów pracy ciągów
  - Algorytm RN - cykliczna rotacja nagrzewnic
- Schematy blokowe przedstawiające logikę decyzji
- Analiza przypadków i koordynacja algorytmów

### [04-scada-hmi/scada-hmi.md](./04-scada-hmi/scada-hmi.md) - System SCADA/HMI
- Interfejs operatorski i wizualizacja
- Panel główny, wskaźniki i trendy historyczne
- Tryby pracy (AUTO/MANUAL)
- System alarmów i diagnostyka
- Wymagania techniczne platformy SCADA

---

**Ostatnia aktualizacja:** 24 Listopad 2025  
**Wersja dokumentu:** 1.0

