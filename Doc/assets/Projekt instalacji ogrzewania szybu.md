# Projekt instalacji ogrzewania szybu

_Dokument wyodrębniony z pliku PDF przy użyciu OCR_

_Liczba stron: 9_

---

## Strona 1

Opis algorytmu systemu automatycznej regulacji (SAR) temperatury szybu 2.2
w Stefanowie.

Zadaniem systemu regulacji automatycznej temperatury szybu jest utrzymanie
temperatury szybu na zadanym poziomie oraz ochrona nagrzewnic przed zamrożeniem.

Warunkiem niezbędnym poprawnej pracy SAR temperatury szybu jest sprawność
układów pomiarowych, sprawność sterowanych urządzeń oraz odpowiedni poziom
dostarczanej mocy cieplnej czynnika grzewczego (temperatury i wartości przepływu
strumienia wody grzewczej) dostarczanego do nagrzewnic ciągów wentylacyjnych.
Każde zakłócenie spowodowane niedotrzymaniem podanych wyżej warunków
może skutkować utratą stabilności SAR i przełączeniem systemu na sterowanie
ręczne.

Wszystkie wejściowe sygnały pomiarowe systemu będą testowane pod
względem ciągłości torów pomiarowych jak również programowo filtrowane i uśredniane
na poziomie sterownika PLC. Kontrolowany będzie również czy dany pomiar mieści się

w dopuszczalnym zakresie. W ten sposób uzyska się wzrost bezpieczeństwa działania
systemu.

Niniejszy opis zakłada spełnienie powyższych warunków i nie uwzględnia stanów
awaryjnych.

SAR temperatury szybu składa się z dwóch podsystemów:

e podsystemu automatycznej regulacji temperatur powietrza grzewczego
(PARTPG),

e podsystemu automatycznej regulacji temperatury szybu (PARTS).

Zadaniem PARTPG jest stabilizacja temperatury powietrza grzewczego
używanego przez PARTS. PARTPG składa się z układów automatycznej regulacji
(UAR) temperatury powietrza za każdą nagrzewnicą ciągu 1-go i 2-go. Ilość UAR
odpowiada ilości zainstalowanych w systemie nagrzewnic (8). Jednocześnie podsystem
ten realizuje załączania (wyłączania) kolejnych nagrzewnic do (z) ruchu jak również
realizuje funkcje zabezpieczenia nagrzewnicy przed przemarzaniem.

W ramach PARTS możliwa jest cykliczna zmiana pracy nagrzewnic pracujących
w jednym ciągu wentylacyjnym.


## Strona 2

Zadaniem PARTS jest utrzymanie temperatury szybu na zadanym poziomie przy
stabilnych parametrach (temperatura przy określonym przepływie) powietrza
grzewczego utrzymywanych przez PARTPG. Brak stabilnych parametrów powietrza
grzewczego może skutkować pogorszeniem jakości regulacji SAR temperatury szybu, a
w sytuacji krytycznej wyłączeniem SAR szybu.

1. Działanie podsystemu automatycznej regulacji temperatur
powietrza grzewczego (PARTG)

1.1 Działanie UAR temperatury powietrza na wylocie z nagrzewnicy.

Na rys. 1 przedstawiono schemat ideowy układu regulacji. Wartością zadaną Tz jest
żądana temperatura powietrza na wylocie z nagrzewnicy, a wartością regulowaną jest
położenie zaworu regulacyjnego na wylocie wody powrotnej z nagrzewnicy.

Wartość zadana Tz jest ustalona przez technologa i wynosi ona 50 °C. Zakłóceniem
układu regulacji jest temperatura strumienia zimnego powietrza na wlocie do
nagrzewnicy jak również zmiana parametrów strumienia wody grzewczej do
nagrzewnicy. W strukturze UAR zastosowano blok funkcyjny regulatora PID sterownika
PLC. Umożliwia on m. in. pracę w trybie automatycznym i sterowanie ręczne zdalne
położeniem zaworu regulacyjnego. Przy sterowaniu ręcznym, zdalnym wykorzystywana
jest wartość zadana dla regulacji ręcznej Pzm położenia zaworu regulacyjnego. Blok
funkcjonalny PID zapewnia bezuderzeniowe (bumpless) przejście między trybami
sterowania ręcznego i automatycznego. Ustawienie wartości maksymalnego i
minimalnego poziomu otwarcia zaworu regulacyjnego wyznacza zakres pracy tego
zaworu. (tu Pzmin=20+Pzmax=100%). Minimalny (20%) stopień otwarcia zaworu
zabezpiecza nagrzewnicę przed zamrożeniem w przypadku wyłączenia jej z ruchu.
Spadek temperatury powietrza z nagrzewnicy powoduje wzrost stopnia otwarcia zaworu
regulacyjnego, zaś jej wzrost powoduje przymknięcie zaworu. Nastawy Kp, Ti, Td
regulatora dobrane będą doświadczalnie podczas procesu uruchomienia UAR na
obiekcie.

Kp — współczynnik wzmocnienia członu proporcjonalnego,

Ti — stała członu całkującego (czas zdwojenia),

Td — stała członu różniczkującego (czas wyprzedzenia).


## Strona 3

Istnieje możliwość elastycznego (w określonym zakresie) wyznaczania
wymaganej ilości załączanych nagrzewnic w funkcji temperatury zewnętrznej. W tym
wypadku konkretne nagrzewnice nie są przypisane do określonego zakresu temperatury
zewnętrznej. Unika się w ten sposób zakłóceń w pracy układu regulacyjnego przy
wyłączeniu danej nagrzewnicy z eksploatacji (np. wskutek awarii nagrzewnicy).
Dodatkowo w ten sposób można realizować algorytm rotacyjnej pracy nagrzewnic.
Warunki termiczne dla elastycznej pracy nagrzewnic przedstawiono w tabeli 2.


## Strona 4

określonej w tab. 2. Stosując zasadę priorytetu nawiewu ciepłego powietrza na poziom
+4,30, w pierwszej kolejności zostaną uruchomione nagrzewnice zasilające ten właśnie
ciąg. Jeżeli z przyczyn technicznych ilość nagrzewnic ciągu pierwszego (brak gotowości
gperacyjnej na skutek uszkodzenia) jest mniejsza od wymaganej ilości pracujących
nagrzewnic, zostanie uruchomiony nawiew na poziom +7,80. W ten sposób zapewnia
się dostarczenie wymaganej mocy ciepinej SAR temperatury szybu.

istnieje różnica pomiędzy temperaturą załączania a temperaturą wyłączania
nagrzewnicy. Z pracy Przyjęto, że temperatur wyłączania jest wyższa od temperatury
załączania o 1+2 °C. Jest to wartość histerezy układu sterowania nagrzewnicą.
technologicznego.
zimnego powietrza do nagrzewnicy i rozpoczyna się proces regulacji.

1.3 _ Wyłączenie nagrzewnicy z ruchu.

Warunki startowe:

* Zawér regulacyjny sprawny, gotowość operacyjna przepustnicy dolotowej. Zawór
i przepustnica pracuje w trybie sterowania zdalnego,

Wyłączenie nagrzewnicy z pracy następuje:
« po osiągnięciu parametrów wody grzewczej poniżej dolnej dopuszczalnej
granicy,
* po zamknięciu przepustnicy na wylocie powietrza z nagrzewnicy,


## Strona 5

wystąpieniu sygnału żądania wyłączenia nagrzewnicy związany

PO określonej temperatury zewnętrznej dla danej nagrzewnicy.
z osiągn tora Tzw p. tab 1),

ul wystąpieniu sygnału programowego wyłączenia nagrzewnicy przy rotacji

tąp
. s ic pracujących w jednym ciągu wentylacyjnym.

nie z ruchu nagrzewnicy powoduje ustawienie zaworu regulacyjnego
+ minimalnego otwarcia oraz zamknięcie przepustnicy dolotowej powietrza
w pozy! :
„mnego PIZePUSITICY’

awaryjne wyłączenie nagrzewnicy powoduje załączenie sygnalizacji

owej systemu, co wymaga dokonania operacji skwitowania przez obsługę.
alarm

4.4 Cykliczna rotacja nagrzewnic pracujących w jednym ciągu
wentylacyjnym.

Cykliczna rotacja nagrzewnic pracujących w jednym ciągu wentylacyjnym polega
na okresowej zmianie pracującej nagrzewnicy danego ciągu wentylacyjnego.

Jest ona możliwa wówczas, gdy ilość nagrzewnic ciągu wentylacyjnego (max 4)
przewyższa ilość aktualnie pracujących nagrzewnic danego ciągu. (co najmniej 1)

W takim przypadku możliwe jest wyłączenie z ruchu nagrzewnicy najdłużej
pracującej, a załączenie w jej miejsce nagrzewnicy o najdłuższym czasie postoju.
Wyrównuje się w ten sposób czasy eksploatacji nagrzewnic. Okres rotacji zostanie
ustalony przez technologa w czasie testowania pracy układu na obiekcie.

2. Działanie podsystemu automatycznej regulacji temperatury szybu
(PARTS)

2.1. Układy pracy ciągów grzewczych.
Istnieją dwa stabilne układy pracy ciągów grzewczych:

z Podstawowy, w którym wyrzutnie poziomu +4,30m zasilane są z ciągu
pierwszego (wentylator W1), a wyrzutnie poziomu +7,90m zasilane są z ciągu
drugiego (wentylator W2). W tym przypadku przepustnica na spince ciągów

wentylacyjnych jest zamknięta, a przepustnice w ciągach są otwarte. Stan ten
przedstawiono na rysunku 3.


## Strona 6

A ny, W którym wyrzutnie poziomu +4,30m zasilane są z ciągu drugiego

n
z on" tor w2), a wyrzutnie poziomu +7,90m nie są zasilane. W tym wypadku
na kolektorze ciepłego powietrza ciągu pierwszego oraz
ica na zasilaniu wyrzutni poziomu +7,90m zostaje zamknięta.

p przepustnice układu sterowania nawiewem pozostają otwarte. Stan ten
ein na rysunku 4.
zauważyć. że praca w układzie ograniczonym jest możliwa jedynie w sytuacji
- wymagana zewnętrznymi warunkami termicznymi ilość pracujących nagrzewnic
wktórej p” od ilości nagrzewnic ciągu drugiego znajdujących się w gotowości
jest (R Dla maksymalnej ilości nagrzewnic ciągu drugiego posiadających zdolność
at zakres temperatury zewnetrznej wynosi do -11 °C, a dla 2 nagrzewnic do
40. Spadek temperatury zewnętrznej poniżej dopuszczalnej powoduje przejście z
układu ograniczonego do układu podstawowego.

układy pracy różne od opisanych powyżej są w trybie regulacji automatycznej,
układami przejściowymi wynikającymi z przechodzenia z jednego trybu stabilnego do
drugiego. PrZY sterowaniu ręcznym możliwe jest kształtowanie układu zasilania
w sposób zgodny z uznaniem operatora.

Należy

2.2. Cykliczna zmiana układów pracy ciągów grzewczych.

PARTS umożliwia cykliczną zmianę układów pracy ciągów grzewczych. Polega
ona na okresowym (ustalonym przez technologa) zmianie układu pracy ciągów.
Możliwość ta może być wykorzystana jedynie przy zachowaniu warunków
przedstawionych w p. 2.1. Stosując cykliczną zmianę układów pracy ciągów uzyskuje
się wyrównanie czasów eksploatacji ciągów grzewczych. Należy zauważyć, że praca
jedynie w układzie podstawowym powoduje nadmierną eksploatację ciągu pierwszego
ponieważ ciąg drugi zostaje włączony dopiero przy zapotrzebowaniu na moc cieplną
przekraczającą wartość dostarczanej mocy ciągu pierwszego.


## Strona 7

p” UAR temperatury powietrza w szybie.
głanie

no schemat ideowy układu regulacji. Wartością zadaną Ts
2 prz zybie mierzona na poziomie -30m, a wartością

Z BOB biolo wa wentylatorów W1 i W2.
zad® jest P kos stalona przez technologa i wynosi ona 2 °C. Zakłóceniem
p gana Ta jes" ratura strumienia zimnego powietrza wdechowego oraz
poło dac jest na powietrza grzewczego ciągów. W strukturze UAR
„ładu rame A ine regulatorów PID sterownika PLC. Umożliwia on m.
pian? iR yi i sterowanie ręczne zdalne obrotami wentylatorów.
w trybie Sh GAIA wykorzystywana jest wartość zadana prędkości

i prace . n , z
EE g rowaniu zał ręcznej wentylatorów. Blok funkcjonalny PID zapewnia
; dla reg

stawio
owietrza w $

; (bumpless) przejscie między trybami sterowania ręcznego i
pezyderzeniow" Ustawienie wartości minimalnej prędkości obrotowej wentylatorów jest
ż A nio = 25 Hz, natomiast wartość maksymalna zależy od ilości

oe posiadających gotowość operacyjną i pracujących wjednym ciągu
. Dla maksymalnej ilości wentylatorów (4) wynosi ona NWmax = 50 Hz.
sf ograniczenie prędkości obrotowej wentylatora zabezpiecza nagrzewnice przed

nadmiernym wychłodzeniem. Górne wartości NWmax zostaną określone przez
technologa w czasie rozruchu technologicznego układu regulacji.

Spadek temperatury powietrza w szybie na poziomie -30m powoduje wzrost
prędkości obrotowej wentylatora w aktualnie sterowanym ciągu.

Nastawy Kp, Ti, Td regulatora dobrane będą doświadczalnie podczas procesu
uruchomienia UAR na obiekcie.

Kp - współczynnik wzmocnienia członu proporcjonalnego,
Ti - stała członu całkującego (czas zdwojenia),
Td- : ;

d- stała członu różniczkującego (czas wyprzedzenia).

W układzi
as ładzie podstawowym pracy ciągów grzewczych, przy pracy wentylatorów

ciągów .
napa O WI pierwszego ciągu grzewczego pracuje ze swoją
r .
A prędkością. W tym przypadku wentylatorem regulacyjnym (na którym
€ Zmiana prędkości obr

otowej) jest wentylator W2.

dokonuje


## Strona 8

NWimin — minimalne obroty wentyłatora
NWzm — w. zad. obrotów went. przy rr.
Ts — temperatura zadana

Ts- temp. pow. w szybie na poz. — 30 m

Rys, 2,
Schemat ideowy UAR temperatury w szybie.


## Strona 9

Z - zamknięcie
Rys, 4 O - otwarcie

"slllacyjnego powietrzą ogrzanego do wyrzutni poziomu 4,30 m z wykorzystaniem drugiego ciągu


