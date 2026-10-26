# MG90S ascunse în tălpi — prototip mecanic

Am păstrat capul și conturul tălpilor din modelul original al utilizatorului. Cele două MG90S ale gleznelor sunt culcate în tălpi, cu corpul de 12,4 mm pe verticală. Partea centrală a tălpii crește de la 12 la **18,5 mm**; conturul exterior la sol rămâne 50 × 60 mm pentru fiecare talpă. Gabaritul neutru al ansamblului rămâne aproximativ 130 × 104 × 60 mm. Picioarele revin la forma deschisă în U, fără blocul care închidea motorul în varianta anterioară.

Celelalte două MG90S rămân în cap și rotesc picioarele în jurul axei verticale. Ecranul OLED de 0,96″ rămâne în față. Suportul presupune o placă de 29,2 × 26,7 mm și trebuie verificat pe modulul cumpărat.

## Acționare și montaj

La gleznă, corpul servo-ului este fixat de talpă, iar brațul original este prins în cheia piciorului. Arborele și axul pasiv din spate sunt coaxiale. Motorul înclină talpa direct față de picior. Firele electrice trec pe la spatele motorului și urcă prin picior, cu o buclă flexibilă la articulație. Nu există transmisie prin tendoane.

Sunt necesare **patru șuruburi centrale originale ale brațelor**, ascunse în interior, două axe scurte Ø3 mm și cele două capace TPU. Șuruburile proprii carcaselor servo nu sunt șuruburi suplimentare de montaj. Nu sunt prevăzute șuruburi vizibile de carcasă.

1. Centrează electric servourile înainte de montaj. Introdu jurnalele picioarelor în lagărele deschise în C ale suportului din cap. Montează cele două brațe de șold și strânge șuruburile lor cât accesul prin picioare este liber.
2. În exteriorul tălpii, potrivește brațul de gleznă în cheia piciorului, cu brațul orientat în sus. Montează motorul pe braț și strânge șurubul central.
3. Cu capacul superior al tălpii scos, coboară ansamblul motor + picior în locașul deschis. Urechile servo-ului se așază în canalele de sprijin; fața deschisă permite accesul la șurub până la închiderea capacului.
4. Introdu axul Ø3 mm din spate în alezajul orb al piciorului; capacul TPU îl reține din cealaltă parte. Nu se introduce un arbore prin corpul motorului.
5. Așază firele în canale, păstrează bucla liberă și cuplează întâi cheile interioare ale capacului tălpii, apoi cele două clipsuri exterioare. Clipsurile se acționează manual și nu se forțează. Masca frontală a capacului ascunde șurubul brațului.
6. Montează OLED-ul și închide capacul posterior al capului, care reține și suportul servourilor de șold.

## Print și verificare fizică

PETG pentru piesele rigide, TPU pentru capacele axelor; strat 0,2 mm și cel puțin patru pereți. Inspectează în slicer suporturile pentru bolți, canale și clipsuri. Printează întâi o singură talpă și testează locașul motorului, brațul original, axul și închiderea capacului. Modelele MG90S sunt reconstrucții geometrice detaliate după [dimensiunile și aspectul TowerPro](https://towerpro.com.tw/product/mg90s-3/), nu CAD oficial al producătorului. Măsoară servourile reale și brațele înainte de lotul final.

Acesta este un prototip CAD: rezistența, jocurile, frecarea, oboseala clipsurilor, cuplul și mersul stabil necesită probe fizice. ESP32, bateria și sistemul audio nu sunt încă amplasate. Alimentarea servo trebuie stabilizată conform fișei tehnice, cu masă comună cu ESP32.

## Verificări CAD și fișiere

Au fost testate 49 de poziții eșantionate, inclusiv combinații ale limitelor ±15° la șolduri și ±12° la glezne, fără interferențe rigide raportate peste pragul de 0,02 mm³. Nu este o demonstrație pentru toate pozițiile intermediare sau pentru mers. Cele 12 STL au trecut verificarea de închidere, conectivitate și volum pozitiv. F3D-ul a fost redeschis și toate cele patru joints au fost acționate separat; s-a verificat că servourile gleznelor aparțin componentelor tălpilor, iar axele rămân coaxiale.

Deschide `Emo-FootDrive.f3d` pentru ansamblul cu motoare și joints. `Emo-FootDrive-print.step` conține numai cele 12 piese imprimabile. Piesele STL sunt în milimetri.

Directorul `Fusion-source/EmoFoot` conține scriptul de regenerare. Pentru reconstruire, adaugă-l în Utilities → Scripts and Add-Ins și păstrează structura de directoare, inclusiv `Original-user-backup.f3d`. Scriptul pornește de la original într-un document nou și exportă peste fișierele generate din acest director. Varianta anterioară, cu motorul în picior, rămâne în propriul director separat.
