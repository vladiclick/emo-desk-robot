# Piese și cumpărături — Emo-Complete

Lista este pentru varianta cu **patru servouri MG90S poziționale: două la șolduri, în cap, și două ascunse în tălpi**. Forma exterioară pornește din modelul utilizatorului. Nu este o listă garantată de cumpărare fără măsurători: plăcile și servourile cu aceeași denumire pot avea alte dimensiuni, hornuri, conectori sau circuite. Anvelopele rezervate în CAD nu sunt automat cote certificate ale componentelor.

AliExpress nu a permis inspectarea paginilor de produs în această verificare. Linkurile de căutare de mai jos ajută la găsirea pieselor; **nu confirmă stocul, prețul, autenticitatea sau varianta selectată**. Nu s-au făcut comenzi. Fișierul `parts.csv` conține toate cantitățile, anvelopele și rezervele dimensionale.

## Module și mecanică

| Cantitate | Piesă aleasă / reper | Dimensiuni și condiții pentru model |
|---|---|---|
| 4 | MG90S **180° pozițional**, metal gear | Nominal 22,8 × 12,4 × 28,5 mm, urechi 32,5 mm. Nu cumpăra varianta 360° continuous. Verifică hornurile înainte de printul complet. [TowerPro](https://towerpro.com.tw/product/mg90s-3/) |
| 1 | GNB6501S70A, **1S 3,7 V, 650 mAh, 70C**, varianta XT30 | Pungă 46 × 25 × 8,5 mm, fără a include firele și mufa; aproximativ 17 ± 2 g. Pagina are titlu A30 și specificații XT30U-F contradictorii: cere confirmarea mufei SKU. Nu substitui cu 2S sau LiHV. [Gaoneng](https://www.gaoneng.shop/products/gaoneng-gnb-1s-3.7v-650mah-70c-xt30-lipo-battery) |
| 1 | ESP32-C3 SuperMini USB-C | Reper 22,5 × 18 mm; grosime **rezervată** 6 mm. Lipire directă, fără bare de pini. Verifică pinoutul și poziția USB-C ale clonei primite. [Furnizor ProtoSupplies](https://protosupplies.com/product/esp32c3-supermini/) |
| 1 | OLED 0,96″ SSD1306 I²C, 128 × 64, monocrom | PCB țintă 27 × 27 mm, cabluri joase pe paduri. Reperul Joy-IT este 27 × 27 × **11 mm cu pini**; această cotă nu dovedește grosimea fără pini. Verifică sticla, aria activă și poziția acesteia, nu doar diagonala. [Joy-IT SBC-OLED01](https://www.joy-it.net/en/products/SBC-OLED01) |
| 1 + 1 | DFPlayer Mini DFR0299 și microSD până la 32 GB | PCB 20 × 20 mm, grosime **rezervată** 6 mm, fără pini înalți. Card FAT16/FAT32; păstrează acces la slot. [DFRobot](https://www.dfrobot.com/product-1121.html) |
| 1 | Difuzor rotund 8 Ω / 0,5 W | Reper PUI AS02008MR-R, Ø20 × 3 mm. Limitează volumul: DFPlayer poate furniza mai mult decât puterea acestui difuzor. Nu este buzzer. [PUI Audio](https://puiaudio.com/product/speakers-and-receivers/as02008mr-r) |
| 1 | GY-521 MPU-6050 pentru orientare | Anvelopă **asumată** 20 × 16 × 4 mm, nu desen verificat al unei plăci fabricate de TDK. Măsoară clona și testează I²C/identitatea senzorului. Datele cipului nu certifică placa GY-521. [TDK MPU-6050](https://product.tdk.com/en/search/sensor/mortion-inertial/imu/info?part_no=MPU-6050) |
| 2 + 4 | Două axe posterioare scurte Ø3 mm și patru șuruburi centrale originale pentru horn | Lungimea axelor se ia din locașurile modelului curent. Axele sunt pivoti posteriori, nu trec prin servo. Cele patru șuruburi de horn sunt ascunse; nu se adaugă șuruburi vizibile pe carcasă. |
| 4 | Hornuri compatibile cu servourile primite | Verifică numărul de caneluri, hubul și forma brațului; seturile generice diferă. Nu forța o piesă printată direct pe canelurile metalice. |

**MX1508, motoarele N20 și roțile din ideea inițială nu sunt folosite în acest robot cu patru servouri.** MG90S primește semnal PWM direct; driverul MX1508 nu îi este necesar.

## Alimentare, încărcare și selector

| Cantitate | Componentă | Condiție |
|---|---|---|
| 1 | Pololu U3V70F5 | 40,6 × 15,2 × 4,6 mm fără borne/pini. Intrare 2,9–5 V, ieșire 5 V. Curentul de ieșire depinde de Vin și temperatură; nu este o sursă de 10 A la ieșire. Verifică la banc sarcina celor patru servouri și bateria aproape descărcată. [Producător](https://www.pololu.com/product/2891) |
| 1 | DFRobot DFR0668 USB-C | Contur 28 × 16,5 mm, grosime **rezervată** 6 mm. Configurează **200 mA**, recomandarea fabricantului pentru 400–1000 mAh. Încărcător 4,2 V pentru o celulă; nu este singur protecția la descărcare a robotului. [Producător](https://www.dfrobot.com/product-2068.html) |
| 1 | Tenergy P/N 32195, protecție 1S | 28,8 × 7 × 2,5 mm; 8,5 A curent de lucru, supracurent declarat 18 A și prag de descărcare nominal 2,8 V. Nu înlocui automat cu o placă TP4056/DW01/8205. [Tenergy](https://power.tenergy.com/tenergy-1s-li-ion-8-5a-18a-pcb-discharging-cut-off-voltage-2-8v/) |
| 1 | C&K JS203011CQN DP3T, trei poziții, non-shorting | Corp 13 × 3,6 nominal / 3,9 maxim × 3,5 mm; terminale 3,3 ± 0,4 mm și buton separat. Locaș cu reazeme pe capetele carcasei și gol pentru lipituri; verifică poziția rândurilor de pini. Contactele sunt de numai **0,3 A la 6 V**: selector de mod/semnale, nu întrerupător pentru curentul servourilor. Nu îl înlocui cu unul care unește contactele în timpul comutării. [Fișa C&K JS](https://www.ckswitches.com/media/1422/js.pdf) |
| 1 | SparkFun USB-C Breakout Vertical **BOB-23055** | PCB/flanșă **11,43 × 20,32 mm**, anvelopă totală documentată **20,32 × 11,43 × 11,70 mm**. Centrul J2 este la (3,175; 10,16) mm în coordonatele Eagle, adică deplasat cu **−2,54 mm față de centrul PCB** pe latura scurtă. Se reține PCB-ul în locaș, nu doar carcasa mufei; fire joase lipite pe paduri, fără header. **R1 și R2 de 5,1 kΩ sunt deja montate separat pe CC1/CC2 spre GND; nu adăuga alte Rd.** [SparkFun](https://www.sparkfun.com/sparkfun-usb-c-breakout-vertical.html), [Eagle și schema originale](https://github.com/sparkfun/SparkFun_USB-C_Vertical_Breakout/tree/main/Hardware) |
| 1 pereche | XT30 compatibil cu bateria | Rezervă pereche 10 × 18 × 7 mm; măsoară conectorii. Fire principale silicon 20–22 AWG, terminale izolate individual și descărcare de tracțiune. |

Acționările se opresc pentru încărcare. Pragul de protecție este ultima limită a bateriei, nu o țintă pentru funcționare normală. Nu alimenta cele patru servouri prin regulatorul de 3,3 V al ESP32 sau prin contactele selectorului. Protecția, polaritatea, modul de încărcare și izolarea USB trebuie verificate electric înainte de conectarea tuturor modulelor. Un pachet de 650 mAh nu stabilește singur autonomia: consumul mediu real trebuie măsurat.

## Pasive, cabluri și piese printate

- **1 × 470 µF, minimum 6,3 V**, low ESR; anvelopă rezervată Ø8 × 12 mm, lângă distribuția servo. Verifică seria aleasă. **1 × colier nylon mini de 2,5 mm lățime**, pentru reținerea condensatorului în ghidajele printate; strânge moderat și nu folosi colierul peste bateria LiPo.
- **1 × 33 µF, minimum 6,3 V** pe intrarea boost, cu fire scurte; **1 × 100 µF, minimum 6,3 V** lângă ESP după dioda de izolare. Măsoară capsulele reale.
- **5 × 1 kΩ**: patru pe semnalele PWM, unul între TX ESP și RX DFPlayer.
- **6 × 100 kΩ**: patru pulldown pe PWM și două pentru divizorul 1:2 de măsurare a bateriei; **1 × 100 nF** de la intrarea ADC la masă. Confirmă domeniul ADC și calibrarea în firmware.
- **1 × SS34** pentru izolarea alimentării ESP conform schemei electrice; verifică polaritatea, capsula și căderea de tensiune. Nu presupune că toate plăcile SuperMini izolează corect alimentarea USB.
- Fire flexibile pentru semnale, tub termocontractabil, materiale de lipire și **spumă moale 0,5 mm**. Fără adeziv permanent pe baterie și fără presiune pe pungă sau membrana difuzorului.
- **PETG** pentru piesele rigide, inclusiv clipsurile; **TPU** pentru două tălpi de aderență, reținătorul difuzorului și puntea de retenție a bateriei. Utilizează STL-urile variantei curente. Nu adăuga șuruburi vizibile.

## Cum cumpărăm și testăm

1. Întâi cumpără **un MG90S cu hornurile lui**, un OLED și o baterie din varianta exactă. Măsoară cu șublerul; testează servo pozițional la o sursă limitată în curent.
2. Printează **o singură talpă**, suportul/hornul aferent și probele de clips. Verifică introducerea, accesul șurubului ascuns și rotația fără frecare înainte de celelalte trei servouri și setul complet.
3. Confirmă modelele modulelor, mufele, grosimea condensatoarelor și traseul cablurilor; corectează parametrii înainte de printul final. Nici „SSD1306”, nici „SuperMini”, nici „MG90S” singure nu certifică toate cotele.
4. Testează separat protecția, încărcarea la 200 mA și convertorul de 5 V, apoi o talpă și cele patru servouri. Măsoară curentul, căderea de tensiune și temperatura în carcasă. Abia apoi montează restul electronicii și începe testele de mers.

## Căutări AliExpress — stoc și variantă neconfirmate

[MG90S 180°](https://www.aliexpress.com/w/wholesale-MG90S-180-degree-positional-servo.html) · [GNB 650 mAh 1S 70C XT30](https://www.aliexpress.com/w/wholesale-GNB-650mAh-1S-70C-XT30.html) · [OLED SSD1306 I²C 27 mm](https://www.aliexpress.com/w/wholesale-0.96-SSD1306-I2C-27mm.html) · [ESP32-C3 SuperMini](https://www.aliexpress.com/w/wholesale-ESP32-C3-SuperMini.html) · [DFPlayer Mini](https://www.aliexpress.com/w/wholesale-DFPlayer-Mini.html) · [Difuzor Ø20 mm 8 Ω](https://www.aliexpress.com/w/wholesale-20mm-8ohm-speaker.html) · [GY-521](https://www.aliexpress.com/w/wholesale-GY-521-MPU6050.html) · [XT30](https://www.aliexpress.com/w/wholesale-XT30-connector.html) · [USB-C vertical BOB-23055](https://www.aliexpress.com/w/wholesale-SparkFun-BOB-23055-USB-C-vertical.html) · [Colier nylon mini 2,5 mm](https://www.aliexpress.com/w/wholesale-2.5mm-mini-nylon-cable-tie.html).

Candidați găsiți, **pagini neinspectate și produse nevalidate**: [OLED](https://www.aliexpress.com/item/1005006262908701.html), [SuperMini](https://www.aliexpress.com/item/1005008988143743.html). Pentru protecție, încărcător și convertor, reperele documentate de mai sus sunt preferabile substituirii după un titlu generic. Nu sunt furnizate prețuri neverificate.
