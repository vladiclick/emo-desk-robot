# Emo Complete

Deschide **Emo-Complete.f3d** în Fusion pentru ansamblul cu 4 articulații. Este un export local verificat prin reimportare; copia deschisă în Fusion poate apărea Unsaved deoarece nu a fost salvată în cloud.

- **Montaj-si-printare.md**: ordine de montaj, 17 piese, materiale, orientare și limitele verificării CAD.
- **Piese-si-cumparaturi.md / parts.csv**: repere documentate și căutări AliExpress. Vânzătorii, prețurile și stocul nu sunt confirmați.
- **Alimentare-si-cablare.md**: LiPo 1S, protecție, convertor, moduri RUN/OFF/CHARGE și GPIO.
- **Emo-Complete-print.step / STL**: numai piesele printabile.
- **PNG**: exterior, interior, mecanism și finisaje Cloud/Night/Sage.
- **JSON**: rapoarte de coliziuni, introducere în carcasă, reimportare și plase STL.
- **Original-user-backup.f3d**: copia păstrată a modelului inițial.

Sursa folosită în Fusion este inclusă în Fusion-source. Pentru regenerare, adaugă folderul **EmoCompleteRunner** în Scripts and Add-ins și rulează scriptul. Acesta construiește un document nou din backup și rescrie exporturile din acest pachet. Folosirea normală a modelului nu cere regenerare.

Acesta este un prototip CAD. Firele, lipiturile și componentele discrete mici ale cablajului nu sunt modelate individual; trebuie montate și izolate în spațiile libere dintre suporturi. Dimensiunile clonelor, flexibilitatea clipsurilor, accesul sculelor, răcirea și mersul trebuie verificate pe componente reale și pe un prim print.
