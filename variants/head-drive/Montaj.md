# Emo — patru MG90S în cap

Modelul pornește din geometria originală a utilizatorului: cap de aproximativ 80 × 65 × 56 mm, fără înălțarea anterioară de 12 mm; ansamblu aproximativ 130 × 104 × 60 mm. Toate cele patru servouri sunt în cap. Carcasa nu are șuruburi vizibile; montajul folosește numai patru șuruburi ascunse pentru brațele originale ale servourilor. Șuruburile reprezentate pe carcasele MG90S aparțin servourilor cumpărate.

## Mecanism

- Două servouri acționează direct șoldurile: rotație în jurul axei verticale, ±15°.
- Două servouri acționează gleznele prin perechi de tendoane în cămăși Bowden: înclinare ±12°.
- Tamburul din cap are raza efectivă de 8 mm, iar fulia piciorului 6 mm. Legăturile din Fusion folosesc raportul ideal: 9° la servo pentru 12° la gleznă. Nu simulează elasticitatea sau frecarea cablurilor.
- Axele gleznelor sunt tije netede din oțel Ø3 mm, aproximativ 49,3 mm lungime, reținute de dopuri TPU cu clips.

## Montaj propus

1. Verifică piesele fizice. MG90S-urile colorate sunt reconstrucții nominale detaliate, nu CAD oficial de producător. Măsoară carcasa, urechile, axa și brațele cumpărate. Referință: [TowerPro MG90S](https://towerpro.com.tw/product/mg90s-3/).
2. Centrează electric servourile. Așază-le în suportul interior și verifică reținerea urechilor prin clipsuri. Folosește brațele originale cu caneluri; nu printa canelurile fine. Montează cele patru șuruburi ale brațelor înainte de închiderea capului.
3. Introdu placa OLED prin spate în suportul captiv. Locașul presupune PCB de 29,2 × 26,7 mm; diagonala de 0,96″ nu garantează această placă. Fereastra vizibilă este 22,8 × 12,2 mm.
4. Montează picioarele, tijele și dopurile. Introdu cămășile Bowden în opritoarele treptate: locaș nominal Ø2,1 mm, adâncime utilă aproximativ 5 mm, ieșire tendon Ø0,8 mm. Prinde tendoanele de tamburi și fulii, reglează pretensionarea și păstrează bucle de serviciu pentru rotația șoldurilor.
5. Introdu suportul în cap și închide capacul posterior. Cele patru clipsuri ale capacului se deflectează manual; nu au rampă de introducere. Nu forța închiderea.

## Probe înainte de printul complet

PETG este alegerea inițială pentru structură și clipsuri; TPU pentru dopuri. Începe cu mostre mici ale clipsurilor și dopurilor, apoi cu un singur mecanism de gleznă. Verifică jocul, accesul la demontare și retenția axei.

Traseele cablurilor sunt reprezentări schematice în poziție neutră. Frecarea, pretensionarea, raza curbelor și spațiul buclelor necesită probe fizice. Centrul de greutate ridicat și cele patru grade de libertate nu demonstrează mersul sau stabilitatea. Restul electronicii nu este încă împachetat în acest ansamblu. Modelul este un prototip mecanic, nu un proiect validat pentru fabricație.

## Verificare CAD

49 de poziții eșantionate fără interferențe între piesele rigide; toate cele 14 STL-uri sunt închise și conectate. Fișierul F3D a fost redeschis: șase joints și două motion links sunt prezente; acționarea fiecărei glezne cu 5° rotește tamburul asociat cu 3,75°. Acest control nu validează fizic transmisia flexibilă.
