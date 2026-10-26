# Emo Complete — montaj și printare

Acesta este un **prototip CAD pentru componentele din BOM**, construit peste geometria originală a utilizatorului. Nu este un robot fizic testat. Ansamblul neutru păstrează gabaritul de **130 × 104 × 60 mm**, capul de **80 × 65 × 56 mm** și amprenta de **50 × 60 mm** a fiecărei tălpi. Axa Y este verticală în fișierul Fusion; reorientează piesele în slicer.

## Ce se deschide

`Emo-Complete.f3d` este ansamblul editabil în Fusion: un cap fix, două picioare U și două tălpi. Are patru articulații revolute independente, cu limite CAD ±15° la șolduri și ±12° la tălpi. Aceste limite sunt de coliziune geometrică pentru modelul actual, nu o demonstrație de echilibru sau de mers. Nu există transmisii cu fire. Hornurile originale se montează direct pe axele servourilor.

`Emo-Complete-print.step` și cele 17 STL-uri conțin exclusiv piesele de printat. Corpurile `REF` sunt repere pentru componente cumpărate; `VIS` sunt detalii de prezentare. Nu printa servourile sau plăcile electronice din ansamblu. MG90S-urile au carcase și detalii colorate reprezentative; poziția exactă a canelurilor, etichetei și hornului diferă între loturi.

| Grup | Piese printate | Material propus |
|---|---:|---|
| Cap față + capac spate + suport șolduri + suport OLED + casetă electronică | 5 | PETG |
| Punte baterie + reținător difuzor | 2 | TPU 95A |
| Două picioare U | 2 | PETG |
| Două corpuri talpă + două capace superioare | 4 | PETG |
| Două capace axe posterioare + două tălpi de aderență | 4 | TPU 95A |

## Ordine de montaj

1. Măsoară un MG90S, hornul, OLED-ul și bateria cumpărate. Alege servouri **poziționale**, nu variante de rotație continuă. Centrează electric fiecare servo înainte de cuplarea hornului. Printează întâi o talpă și probează montajul; anvelopele plăcilor generice nu certifică lotul primit.
2. Montează OLED-ul fără bare de pini în suportul său, cu fire flexibile joase. Introdu suportul din spatele capului, până în locașul feței. Nu aplica forță pe sticlă. Fereastra vizibilă este 22,8 × 12,2 mm; verifică poziția ariei active față de PCB-ul de 27 × 27 mm ales.
3. În afara capului, cu tălpile încă nemontate, cuplează fiecare servo de șold cu hornul original și piciorul U. Strânge șurubul central original dinspre partea inferioară a piciorului; verifică accesul cu șurubelnița folosită înainte de introducerea în carcasă. Cheia piciorului transmite cuplul prin horn, nu prin șurub.
4. Introdu fiecare ansamblu servo–horn–picior în suportul de șolduri **dinspre față spre spate (+Z)**. Ține manual cele două vârfuri ale clipsurilor depărtate aproximativ 1 mm; nu împinge motorul peste clipsuri cu forță. Jurnalul și flanșa piciorului intră prin deschiderile din față ale lagărului C. Eliberează clipsurile după așezarea urechilor motorului pe reazeme.
5. Introdu suportul cu ambele șolduri și picioare prin deschiderea posterioară a capului **spre față (−Z)**. Tălpile și caseta electronică se montează ulterior. Suportul se așază în ghidajele interne; capacul posterior îl reține axial la închidere.
6. Pentru fiecare talpă, montează hornul de gleznă în cheia piciorului, apoi așază MG90S-ul orizontal în corpul tălpii și cuplează-l direct la horn. Fixează șurubul original ascuns prin accesul frontal înainte de capacul superior. Introdu axa posterioară Ø3 mm în alezajul orb și pune capacul TPU. Verifică manual că axul anterior și pivotul posterior sunt coaxiale și libere. Axa posterioară are rezervă CAD de aproximativ 5,2 mm; taie și finisează la lungimea măsurată, fără presare forțată.
7. Așază cablul în canalele tălpii și piciorului. Lasă bucle libere la ambele articulații, fără să ajungă în horn sau lagăr. Închide capacul tălpii cu cheile interioare introduse primele și clipsurile accesibile la exterior. Montează tălpile TPU în cele patru locașuri cu cap de reținere.
8. Populează caseta electronică pe banc. Plăcile culisează pe margini și au opritoare de capăt cu eliberare manuală. Firele sunt lipite direct și izolate; nu monta bornele înalte ale convertorului. Păstrează firele și lipiturile în golurile dintre deck-uri, fără contact cu piesele metalice.
9. Așază condensatorul Ø8 × 12 mm lateral în șaua deschisă, între opritoarele axiale, și strânge moderat colierul nylon de 2,5 mm în canalul rezervat. Nu acoperi supapa de siguranță. Montează difuzorul pe inelul de spumă și reținătorul TPU pe **rama** lui; membrana rămâne liberă.
10. Montează USB-ul vertical BOB-23055 în suport, folosind **flanșa PCB**. Placa este 20,32 × 11,43 mm în orientarea din model, iar mufa este deplasată cu 2,54 mm față de centru pe latura scurtă. Selectorul C&K se sprijină pe capetele carcasei; terminalele și firele trec prin golul central. Nu pune sarcini de inserare pe terminale. Capacul spate reține axial ambele componente.
11. Așază bateria pe cele două tampoane de spumă, cu firele spre parcarea XT30 de sub ea. Puntea TPU se fixează pe **pereții rigizi**, păstrând spațiu față de punga bateriei. Nu strânge sau lipi permanent bateria. Nu folosi coliere peste pungă.
12. Cu bateria deconectată, verifică toate lipiturile și schema RUN/OFF/CHARGE din `Alimentare-si-cablare.md`. Conectează cablurile, introdu caseta populată din spate, verifică firele la margini și închide capacul. Cele două eliberări laterale permit deschiderea fără șuruburi pe exterior.

Cele **patru șuruburi centrale ale hornurilor** sunt singurele șuruburi de montaj prevăzute. Nu sunt necesare șuruburi vizibile pe carcasă. Șuruburile de fabrică ale MG90S rămân în servouri.

## Setări inițiale de printare

PETG: duză 0,4 mm, strat 0,16–0,20 mm, 4 pereți la piese portante, 5 straturi sus/jos și 25–35% umplere. Temperatura și răcirea se iau din profilul filamentului. TPU: 0,20 mm, 3 pereți, viteză redusă conform imprimantei. Nu folosi PLA pentru clipsurile flexate repetat.

Corpurile tălpilor pot sta pe baza plană după reorientarea axei Y. Capacele se așază cu suprafața mare în jos. Pentru cap și picioarele U, alege orientarea care păstrează fața vizibilă și găurile lagărelor curate; verifică toate suprapunerile în previzualizarea slicerului. Caseta cu deck-uri și suportul șoldurilor au zone suspendate: vor necesita suporturi locale bine alese. Nu sunt prezentate ca piese fără suporturi. Scoate suporturile fără a flexa brusc limbile subțiri; ajustează numai bavurile, fără a lărgi lagărele la întâmplare.

Jocurile sunt în general de ordinul 0,2–0,35 mm pe suprafață; materialul și imprimanta pot cere ajustări. Clipsurile au porțiuni de 0,6–0,8 mm și trebuie verificate în slicer ca linii continue. Printează întâi piesele de probă ale unei singure articulații. Probează în special retenția hornului, clipsurile de șold, capacul tălpii și cheile TPU.

## Ce validează fișierele de control

`mechanical-validation.json`: poziția neutră și 49 de poziții ale celor patru articulații, corpuri rigide și anvelope hardware. `native-reload-validation.json`: reimportarea F3D, patru articulații funcționale și axe coaxiale. `mesh-validation.json`: cele 17 STL-uri închise și conectate. Rapoartele de inserție verifică **poziții discrete** ale casetei și șoldurilor; vârfurile clipsurilor de șold sunt reprezentate ca eliberate manual.

Aceste verificări nu simulează deformarea plasticului, traseul real al fiecărui fir, forța șurubelniței, toleranțele lotului, temperatura, cuplul disponibil, alunecarea sau echilibrul dinamic. Montajul și mersul cer testarea unui prototip fizic. Cele trei culori Cloud/Night/Sage schimbă finisajul aceleiași geometrii.
