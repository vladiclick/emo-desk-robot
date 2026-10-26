# Emo: 4 servouri și OLED de 0,96″

**Prototip pentru probă pe banc și verificarea montajului.** Copia modificată păstrează forma proiectului tău, cu capul ridicat cu 12 mm pentru mecanismul șoldurilor. Coarnele servourilor și pivoții exteriori rămân vizibili. Fișierul `Original-user-backup.f3d` este copia originală, nemodificată.

## Fișiere și verificări

- `Emo-4servo.f3d`: ansamblu nativ cu istoric, 5 componente principale și 4 articulații. Corpurile originale rămân ascunse la rădăcină; nu le activa la printare.
- `Emo-4servo.step`: cele 12 solide pentru print, fără joints.
- 12 STL-uri individuale: trunchi, capac spate, două picioare, două tălpi cu furci, patru capace laterale și două piese pentru OLED. Import în **mm, scară 100%**.
- Rapoartele JSON consemnează 12 solide valide, fără erori de feature, STL-uri închise și fără interferențe detectate în poziția neutră și cele 49 de poziții eșantionate. Axele mișcării au fost verificate din transformările componentelor. Fișierul F3D exportat a fost redeschis, iar toate cele patru joints au fost acționate din nou cu succes; vezi `native-reload-validation.json`.

Aceste verificări nu demonstrează absența coliziunilor în fiecare poziție intermediară, stabilitatea mersului, cuplul suficient sau funcționarea electrică. Firele nu sunt modelate fizic.

## Articulațiile în Fusion

Trunchiul este fixat prin Ground. În Browser extinde **Joints**, apoi clic dreapta pe articulație → **Drive Joint**. Revino la 0° după probă.

| Joint | Componente | Mișcare și limită |
|---|---|---|
| HIP L / HIP R | Trunchi–picior | Rotație în jurul axei verticale Y, ±20° |
| ANKLE L / ANKLE R | Picior–talpă | Înclinare laterală în jurul axei Z orientate înainte–înapoi, ±15° |

## Dimensiuni de confirmat înainte de print

Modelul folosește 4 × MG90S. Anvelopa nominală de referință este 22,8 × 12,4 × 28,5 mm; carcasa are adâncime 23,2 mm, urechi de 32,5 mm, ax decalat cu 5,7 mm și pas de prindere **presupus** de 28 mm. Buzunarele au 0,35 mm joc pe fiecare latură. Măsoară servourile reale: documentația [TowerPro MG90S](https://towerpro.com.tw/product/mg90s-3/) prezintă inclusiv valori diferite pentru lățime.

OLED-ul presupus are PCB de 29,2 × 26,7 × 6,2 mm și zonă activă de 21,74 × 11,18 mm. Fereastra este 22,8 × 12,2 mm. Modulul real nu a fost furnizat; verifică PCB-ul, sticla, conectorii și poziția zonei active.

## Montaj

1. Probează întâi un locaș servo și suportul OLED. Nu forța piesele.
2. Centrează electronic servourile, apoi montează **coarnele originale** scurte. Referințele presupun braț de 13 × 5,5 mm. Nu printa canelura de antrenare. Fixarea în piesele mobile folosește fante pentru M2 și necesită verificarea cornului real.
3. Fixează fiecare servo prin cele două urechi, cu M2 potrivite. Montează tălpile și pivoții pasivi M3 cu distanțiere: strângerea șurubului nu trebuie să blocheze rotația.
4. Montează OLED-ul în suport, apoi rama de retenție: 4 M2 pentru flanșa frontală și 4 pentru ramă. Nu comprima sticla.
5. Lasă bucle de cablu la articulații. Închide capacele laterale cu câte 2 M2 și capacul spate cu 4 M2; alege lungimile după adâncimea disponibilă.

TowerPro indică alimentare la 4,8 V. LiPo de 3,7 V necesită o sursă servo reglată în jur de 5 V, compatibilă cu exemplarele reale, și GND comun cu microcontrolerul. Curentul necesar nu este încă verificat.

Pentru prima probă: duză 0,4 mm, strat 0,2 mm, 4 pereți și 15–20% umplere, ajustate în slicer. Verifică orientarea și suporturile fiecărei piese; [Prusa explică rolul straturilor și perimetrelor](https://help.prusa3d.com/article/layers-and-perimeters_1748). Dimensiunile din script sunt parțial constante; modificările necesită editarea feature-urilor native sau regenerarea modelului.

Scriptul din `Fusion-source/EmoIntegrate` regenerează o copie nouă din backup-ul original, aflat în același pachet. În Fusion: Scripts and Add-Ins → + → Script or add-in from device → selectează folderul `EmoIntegrate`. Rezultatele regenerate suprascriu fișierele derivate din acest folder, nu backup-ul original.
