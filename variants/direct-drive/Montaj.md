# Emo — patru MG90S cu acționare directă

Modelul păstrează gabaritul inițial de aproximativ **130 × 104 × 60 mm**, fără ridicarea capului. Două MG90S din cap rotesc picioarele la șolduri; câte un MG90S în fiecare picior, lat de 15 mm, înclină direct talpa. Arborele servo-ului și pivotul tălpii sunt coaxiale. Nu există cabluri Bowden, tendoane sau scripeți; prin picioare trec doar fire electrice.

Arhitectura este adaptată după [ghidul comunității LivingAI despre cele patru servouri EMO](https://forums.living.ai/t/parts-and-repairs-guide-with-images-and-video-tutorial-view-ask-share/8712/21). Este o interpretare pentru MG90S, nu o copie a mecanismului de fabrică; EMO utilizează ansambluri servo proprii.

## Piese și potrivire

Sunt necesare patru MG90S cu brațele originale și **patru șuruburi centrale ascunse**, două axe scurte din oțel Ø3 mm și două capace TPU. Nu se folosesc șuruburi exterioare de carcasă. [TowerPro](https://towerpro.com.tw/product/mg90s-3/) indică un corp nominal de 22,8 × 12,2 × 28,5 mm, dar desenul său cotează lățimea și la 12,4 mm. Măsoară exemplarele cumpărate, urechile, poziția arborelui și brațele înainte de print; profilul canelat rămâne cel al brațului original.

Suportul OLED presupune o placă **29,2 × 26,7 mm**. Diagonala de 0,96″ nu garantează acest contur sau aceiași pini.

## Ordinea de montaj

1. Centrează electric servourile. Pregătește carcasa și suportul comun al celor două servouri de șold, cu capacul posterior deschis.
2. Introdu lateral jurnalul fiecărui picior în lagărul deschis în C al suportului. Flanșa captivă transferă sarcina piciorului către suport; acesta se sprijină în locașurile capului și este reținut de stâlpii capacului posterior.
3. Așază brațul original în cheia șoldului, montează servo-ul în clipsuri și strânge șurubul central ascuns. **Fă asta înainte să introduci servo-ul de gleznă**, cât accesul prin picior este liber.
4. Introdu servo-ul de gleznă din față. Potrivește talpa pe brațul original și strânge șurubul central, încă fără capacul frontal. În spate, introdu axul scurt Ø3 mm între alezajul orb al tălpii și capacul TPU.
5. Montează capacul frontal: întâi cheile inferioare, apoi apasă manual limba superioară și închide. Clipsul nu are rampă de autoînchidere; nu-l forța. Opritoarele capacului rețin axial coroana rotundă a tălpii.
6. Montează OLED-ul, lasă bucle libere firelor la articulații și închide capacul posterior.

## Print și limite

Folosește PETG pentru piesele rigide, TPU pentru capacele axelor, strat de 0,2 mm și minimum patru pereți. Testează întâi cupoane pentru locașul servo, cheia brațului, lagăr și clipsuri. Alimentarea servo trebuie stabilizată conform fișei, cu masă comună cu ESP32; LiPo 1S nu se conectează direct.

ESP32, bateria și sistemul audio nu sunt încă amplasate. Jocurile, rezistența clipsurilor, cuplul și mersul stabil necesită probe fizice.

## Verificări realizate

Fișierul F3D a fost redeschis în Fusion: toate cele patru articulații revolute au fost acționate separat și axele tălpilor au rămas coaxiale cu ieșirile servourilor. Nu există motion links. Verificarea CAD a găsit zero interferențe rigide în cele 49 de poziții eșantionate, cu limite de ±15° la șolduri și ±12° la glezne. Aceasta nu demonstrează mersul fizic sau absența contactelor în orice poziție intermediară.

Cele 12 STL sunt corpuri închise și conectate, în milimetri. STEP-ul conține numai cele 12 piese pentru printare; F3D-ul include și servourile detaliate colorate, brațele, axele și reprezentarea OLED. Servourile sunt modele geometrice construite după dimensiunile și aspectul TowerPro, nu fișiere CAD furnizate de producător.

Pentru editare, deschide `Emo-DirectDrive.f3d`. Directorul `Fusion-source/EmoDirect` conține scriptul de regenerare; adaugă-l din Utilities → Scripts and Add-Ins numai dacă vrei să reconstruiești varianta. Păstrează structura directoarelor pentru acces la copia originalului. Scriptul creează un document nou și exportă peste fișierele generate din acest director.
