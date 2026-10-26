"""Documented component envelopes, removable electronics carrier and battery bay.
All coordinates are mm. Connector heights are conservative design allowances.
"""
import math,json,os
import adsk.core as C
import adsk.fusion as F
from .base import pt,vi,objs

COMPONENTS=(
 {'name':'ESP32-C3 SuperMini','center':(-35,90.9,-34),'size':(22.5,18,6),'color':(32,80,122),'kind':'pcb'},
 {'name':'Pololu U3V70F5','center':(-35,90,-17.5),'size':(40.6,15.2,4.6),'color':(30,89,55),'kind':'pcb'},
 {'name':'DFRobot DFR0668 charger','center':(-35,64,-31),'size':(28,16.5,6),'color':(35,72,105),'kind':'pcb'},
 {'name':'DFPlayer Mini','center':(-35,64,-19),'size':(20,20,6),'color':(29,88,65),'kind':'pcb'},
 {'name':'1S protection 32195','center':(-35,67.8,-5.8),'size':(28.8,7,2.5),'color':(26,95,64),'kind':'pcb'},
 {'name':'IMU GY-521 envelope','center':(-35,52,-36.5),'size':(20,16,4),'color':(34,87,134),'kind':'pcb'},
)
BATTERY={'name':'GNB6501S70A 1S 650mAh','center':(-35,86.3,-1.25),'size':(46,25,8.5),'kind':'battery'}

def hardware(b,v,name,color):
    b.paint(v,name,color);b.add_hardware(v,name);return v

def cosmetic(b,v,name,color):
    b.paint(v,name,color);v.name='VIS | '+name;b.visuals.append(v);return v

def board(b,spec):
    name=spec['name'];x,y,z=spec['center'];w,h,depth=spec['size'];back=z+depth/2
    pcb=b.box(name+' PCB',(x,y,back-.8),(w,h,1.6))
    hardware(b,pcb,name+' PCB',spec['color'])
    # Plated pads, real package blocks and connectors make the packing inspectable.
    for sx in (-1,1):
        for sy in (-1,1):
            cosmetic(b,b.cyl('Gold pad',(x+sx*(w/2-1.2),y+sy*(h/2-1.2),back-1.63),(x+sx*(w/2-1.2),y+sy*(h/2-1.2),back-1.69),.55),name+' gold pad',(188,146,65))
    if name.startswith('ESP32'):
        hardware(b,b.box('C3 package',(x,y+1.0,z-.2),(5,5,2.2)),name+' main IC',(27,29,32))
        hardware(b,b.box('Supermini USB-C',(x,y-h/2+3.2,z-.6),(8.8,6.4,3.0)),name+' USB-C',(159,165,173))
        hardware(b,b.box('Ceramic antenna',(x+6.8,y+h/2-1.7,z-.4),(3.2,2.2,1.2)),name+' ceramic antenna',(218,214,194))
        for dx in (-5.3,5.3):cosmetic(b,b.box('Tactile switch',(x+dx,y+3,z-.1),(2.5,3,1.5)),name+' boot reset switch',(122,127,132))
    elif name.startswith('Pololu'):
        hardware(b,b.box('Shielded boost inductor',(x,y,z-.65),(6.7,6.7,2.7)),name+' inductor',(60,64,69))
        for dx in (-12,12):hardware(b,b.box('Power converter IC',(x+dx,y,z-.25),(4.6,4.6,1.9)),name+' power IC '+str(dx),(33,34,38))
    elif name.startswith('DFPlayer'):
        hardware(b,b.box('MicroSD socket',(x,y+.8,z-.3),(13,15,3.4)),name+' microSD slot',(159,164,171))
        cosmetic(b,b.box('Removable microSD card',(x,y+4.9,z-.6),(10.8,14,1)),name+' microSD card',(29,31,34))
    elif 'charger' in name:
        hardware(b,b.box('Charger USB-C',(x,y-h/2+3.3,z-.4),(8.8,6.6,3)),name+' internal USB-C',(158,164,173))
        hardware(b,b.box('TP4056X IC',(x,y+2,z+.5),(5,6,1.6)),name+' charge IC',(29,31,34))
    else:
        hardware(b,b.box('Module IC',(x,y,back-1.6-max(.5,depth-1.8)/2),(min(5,w-4),min(5,h-2),max(.5,depth-1.8))),name+' IC',(31,32,36))
    return back

def tray(b,spec):
    """Slide-in PCB edge rails; no printed fastener enters a copper hole."""
    x,y,z=spec['center'];w,h,d=spec['size'];back=z+d/2
    t=b.box(spec['name']+' tray',(x,y,back+.9),(w+2.4,h+2.4,1.2))
    for sign in (-1,1):
        wall=b.box('PCB side rail',(x+sign*(w/2+.65),y,back-.7),(1,h+2.4,3.2))
        # Interrupted capture lips leave both board ends accessible.
        lip=b.box('PCB edge capture',(x+sign*(w/2+.15),y,back-1.95),(1.4,max(3,h-6),.5))
        t=b.join(t,[wall,lip],'PCB edge rail and retaining lip')
    for dx in (-w/2+2,w/2-2):
        stop=b.box('PCB corner end stop',(x+dx,y+h/2+.65,back-.7),(2,1,3.2))
        t=b.join(t,[stop],'PCB top corner stops')
    # Integral bottom release latch prevents the PCB sliding out in motion.
    left=x-w/2;bottom=y-h/2
    t=b.cut(t,[b.box('Latch flex window',(left+3.8,bottom-.7,back+.3),(7.1,1.6,4.0))],'Free PCB end latch')
    beam=b.box('PCB end latch beam',(left+2.8,bottom-.85,back-1.85),(7.2,1.4,.6))
    hook=b.box('PCB end latch hook',(left+5.6,bottom-.85,back-1.55),(1.2,1.3,.8))
    t=b.join(t,[beam,hook],'Manual release positive PCB stop')
    return t

def install_electronics(b,front,lid,rack):
    from .EmoComplete import sleeve
    # One rear-loading carrier connects board decks and padded battery cradle.
    carrier=b.box('Electronics left backbone',(-60.5,73,-7.2),(2.4,50,2.4))
    carrier=b.join(carrier,[b.box('Electronics right backbone',(-9.5,73,-7.2),(2.4,50,2.4))]+[
        b.box('Carrier crossbar',(-35,y,-8.5),(54,2,1.4)) for y in (49.5,75,81.2,97)],'Rigid removable electronics frame')
    # Battery is never squeezed. 0.8 mm clearance each side plus soft floor pads.
    plate=b.box('Battery insulated backstop',(-35,86.3,-6.9),(50,28.2,1.2))
    carrier=b.join(carrier,[plate],'Battery front cradle on removable frame')
    for x in (-59.4,-10.6):
        carrier=b.join(carrier,[b.box('Battery side bumper',(x,86.3,-1.6),(1.2,28.2,11.8))],'Battery lateral support')
    for y in (72.4,100.2):
        carrier=b.join(carrier,[b.box('Battery end bumper',(-35,y,-1.6),(50,1.2,11.8))],'Battery end clearance')
    # Shallow keys locate carrier; rear lid traps it after all connectors are seated.
    for x in (-60.5,-9.5):
        for y in (54,94):
            key=b.box('Rear loading carrier guide',(x,y,-9.5),(3.4,4,3.0))
            carrier=b.join(carrier,[key],'Carrier keyed rail')
            front=b.cut(front,[b.box('Carrier guide receiver',(x,y,-9.5),(3.9,4.6,3.6))],'Carrier guide clearance')
            rack=b.cut(rack,[b.box('Rack carrier keyway',(x,y,-9.8),(3.9,4.6,5.4))],'Electronics rack key receiver')
            if y==54:carrier=b.join(carrier,[b.box('Carrier axial spacer',(x,y,-9.0),(5.0,3.6,1.5))],'Carrier front seating shoulder')
    decks=[]
    for spec in COMPONENTS:
        board(b,spec)
        if spec['name']=='IMU GY-521 envelope':
            # Board is close behind the face but below the OLED.
            pass
        decks.append((spec,tray(b,spec)))
    for spec,t in decks:
        x,y,z=spec['center'];w,h,d=spec['size'];back=z+d/2
        # Each deck links to a crossbar along a clear edge, outside module bodies.
        if spec['name'].startswith('ESP32'):
            row=81.2;positions=(-48,-22)
        elif spec['name'].startswith('Pololu'):
            row=81.2;positions=(-57,-13)
        elif spec['name']=='IMU GY-521 envelope':
            row=49.5;positions=(-47,-23)
        elif spec['name'].startswith('1S'):
            row=49.5;positions=(-47,-23)
        else:
            row=75;positions=(-51,-19)
        bridge=b.box('Deck upper bridge',(x,row,back+.9),(abs(positions[1]-positions[0])+2.8,2,1.2))
        # Join each deck to its bridge with small lateral supports at its top edge.
        reach=b.box('Deck longitudinal bridge',(x,(y+row)/2,back+.9),(2,abs(row-y)+2,1.2))
        t=b.join(t,[bridge,reach],spec['name']+' carrier bridge')
        posts=[b.box('Deck depth post',(xx,row,(back+.9-8.5)/2),(2.8,2,abs(back+.9+8.5)+1.2)) for xx in positions]
        carrier=b.join(carrier,[t]+posts,'Stacked removable electronics decks')
    # Open rear loading path for the entire front electronics stack.
    rack=b.cut(rack,[b.box('Cassette through opening',(-35,64.5,-10.5),(40.8,29,6.8))]+[b.box('Lower deck support slot',(x,49.5,-22),(3.4,2.6,28)) for x in (-47,-23)],'Rear-load electronics path through hip rack')
    rack=b.cut(rack,[b.box('IMU lower insertion clearance',(-35,51,-24),(26,3.2,35))],'Full IMU loading path below rack')
    # Electrolytic bulk capacitor sits beside the audio board.
    capacitor=b.cyl('Servo rail reservoir',(-50,53,-22),(-50,65,-22),4)
    hardware(b,capacitor,'470uF reservoir allowance',(47,54,62))
    clamp=sleeve(b,'Capacitor support',(-50,52.5,-22),(-50,54,-22),4.7,4.25)
    clamp=b.cut(clamp,[b.box('Capacitor radial loading opening',(-53,53,-22),(6.2,3,12))],'Open side of capacitor saddle')
    clamp=b.join(clamp,[b.box('Cap support arm',(-50,53,-14.9),(2,2,5.0))],'Capacitor sleeve arm')
    clamp=b.join(clamp,[b.box('Cap axial spine',(-50,59,-17.1),(2,13.6,1))]+[
        b.box('Cap axial end stop',(-50,y,-18.8),(4,.4,3)) for y in (52.6,65.4)],'End stops retain capacitor axially')
    carrier=b.join(carrier,[clamp,b.box('Cap carrier link',(-50,51.5,-8.5),(2,5.5,1.4)),b.box('Cap depth link',(-50,53,-11.5),(2,2,7.4))],'Protected bulk capacitor cradle')
    tie=sleeve(b,'Capacitor nylon tie allowance',(-50,58.3,-21.3),(-50,60.8,-21.3),5.15,4.9)
    hardware(b,tie,'Capacitor 2.5mm nylon tie allowance',(38,43,49))
    carrier=b.cut(carrier,[sleeve(b,'Tie routing relief',(-50,58.1,-21.3),(-50,61,-21.3),5.4,4.85)],'Local tie clearance beside PCB rail')
    # Battery details and two compliant foam pads, separate from the pouch.
    bx,by,bz=BATTERY['center'];bw,bh,bd=BATTERY['size']
    cell=b.rounded_xy('GNB aluminium pouch',bx,by,bz,bw,bh,1.8,bd)
    hardware(b,cell,BATTERY['name'],(174,181,190))
    cosmetic(b,b.box('Battery cyan label',(bx,by,bz+bd/2+.05),(36,18,.08)),'GNB label',(28,132,139))
    for x in (-49,-21):
        pad=b.box('Soft insulating battery pad',(x,86.3,-5.95),(5,20,.5))
        hardware(b,pad,'Battery foam pad '+str(x),(41,47,51))
    # TPU bridge closes on rigid cradle sides, never stretches tightly over pouch.
    strap=b.box('TPU battery bridge',(-35,86.3,4.6),(50.4,7,.8))
    for x in (-60.2,-9.8):
        leg=b.box('Battery bridge leg',(x,86.3,-.1),(1.2,7,9.4))
        inward=.3 if x<-35 else -.3
        toe=b.box('Battery bridge key',(x+inward,86.3,-4.4),(2.0,7,1.0))
        strap=b.join(strap,[leg,toe],'Battery strap wraps rigid cradle edges')
        carrier=b.cut(carrier,[b.box('Strap side relief',(x,86.3,-.1),(1.7,7.6,10.0)),b.box('Strap key receiver',(x+inward,86.3,-4.4),(2.6,7.6,1.6))],'Battery bridge keyed seating')
    b.paint(strap,'Battery TPU accent',(51,163,163));b.add_part(strap,'TPU loose battery retaining bridge')
    carrier=b.cut(carrier,[b.box('Battery bridge rear seat',(-35,86.3,3.85),(51,7.6,1.5))],'Clear battery bridge above rigid side walls')
    carrier=b.cut(carrier,[b.box('Battery connector parking clearance',(-52,72.4,0),(20.4,3.0,10.2))],'Battery lead path to accessible connector parking')
    # High-current connector pocket remains accessible after the rear cap is removed.
    hardware(b,b.box('XT30 coupled envelope',(-52,68.5,1.2),(18,10,7.0)),'XT30 coupled connector allowance',(220,173,43))
    # Rear speaker. Its load-bearing rim is held by a removable TPU ring.
    speaker=b.cyl('Speaker body',(-35,54,-2.5),(-35,54,.5),10)
    hardware(b,speaker,'20mm 8ohm speaker allowance',(109,116,125))
    cosmetic(b,b.cyl('Speaker cone',(-35,54,.5),(-35,54,.7),8.5),'Speaker cone',(37,40,44))
    ring=sleeve(b,'Speaker support ring',(-35,54,-4),(-35,54,-2.8),11.8,10.4)
    ring=b.join(ring,[b.box('Speaker frame link',(-35,47.5,-6.6),(22,2,6.0))],'Speaker ring link')
    carrier=b.join(carrier,[ring,b.box('Speaker lower crossbar',(-35,49.5,-8.5),(54,2,1.4))],'Integrated speaker carrier')
    seal=sleeve(b,'Speaker TPU retainer',(-35,54,.65),(-35,54,1.75),11.8,9.8)
    for x in (-46.2,-23.8):
        arm=b.box('Speaker retaining leg',(x,54,-1.2),(1,4,5.0))
        seal=b.join(seal,[arm],'Flexible speaker edge retainer')
        carrier=b.cut(carrier,[b.box('Speaker retainer socket',(x,54,-2.9),(1.5,4.6,2.6))],'Speaker ring fit')
    b.paint(seal,'Speaker TPU seal',(49,151,156));b.add_part(seal,'TPU speaker rim retainer')
    # Charge pigtail, never the inaccessible native charger connector, receives USB.
    hardware(b,b.box('BOB-23055 PCB flange',(-57,57.14,-3.5),(20.32,11.43,1.6)),'SparkFun BOB-23055 PCB flange',(151,35,37))
    hardware(b,b.box('Rear vertical USB-C inlet',(-57,54.6,2.35),(8.94,3.45,10.1)),'External charge USB-C allowance',(161,169,178))
    usb=b.box('USB flange front stop',(-57,57.14,-5.1),(22.72,13.83,1.0))
    usb=b.cut(usb,[b.box('USB PCB underside wiring opening',(-57,57.14,-5.1),(18,9,3))],'Support only USB PCB perimeter')
    for x in (-67.81,):
        usb=b.join(usb,[b.box('USB flange lateral guide',(x,57.14,-3.5),(.8,13.83,3.2))],'USB PCB edge positioning')
    usb=b.join(usb,[b.box('USB short right guide',(-46.09,60.6,-3.5),(1,3,3.2))]+[b.box('USB end guide',(-57,y,-3.8),(22.72,1,2.6)) for y in (50.775,63.505)],'USB flange end guides')
    usb=b.join(usb,[b.box('USB mount depth link',(-67.1,51.8,-6.6),(2,2,4)),
                    b.box('USB carrier crossbar extension',(-63.8,50.65,-8.5),(8.6,4.3,1.4))],'USB flange ties to carrier')
    carrier=b.join(carrier,[usb],'Positive charging connector front stop')
    for x in (-65,-49):
        lid=b.join(lid,[b.box('USB PCB rear capture',(x,57.14,1.9),(2,7,8.6))],'Rear cap traps USB PCB flange with clearance')
    hardware(b,b.box('Three-position switch housing',(-14,55,4.45),(13,3.9,3.5)),'RUN OFF CHARGE switch allowance',(58,63,70))
    for dx in (-4,-2,2,4):
        for dy in (-1.65,1.65):
            hardware(b,b.box('Switch terminal',(-14+dx,55+dy,.85),(.6,.3,3.7)),'Mode switch terminal '+str((dx,dy)),(153,159,167))
    cosmetic(b,b.box('Mode slider',(-14,55,7.6),(3.0,2.2,3.0)),'Mode slider',(54,164,167))
    # Individual cable grommet holes and strain relief in the rack.
    rack=b.cut(rack,[b.cyl('Harness rear passage',(-49,68,-13),(-49,68,-8),2.5),
                     b.cyl('Speaker power passage',(-35,54,-13),(-35,54,-8),2.5)],'Internal connector harness passages')
    for x,y in ((-57,54.6),(-14,55)):
        w,h=(10.3,4.3) if x==-57 else (9.5,3.0)
        front=b.cut(front,[b.rounded_xy('Rear interface tunnel',x,y,4.2,w,h,.8,5.5)],'Charge and mode access through rear seat')
        lid=b.cut(lid,[b.rounded_xy('Rear interface opening',x,y,6.8,w,h,.8,7.0)],'Recessed rear user controls')
    # Switch body is larger than its slider aperture; clip into the removable frame.
    for x,y,w,h in ((-14,55,13,3.9),):
        cup=b.box('Rear interface frame',(x,y,1.0),(w+2.8,h+2.8,2.0))
        cup=b.cut(cup,[b.box('Rear interface pocket',(x,y,2.0),(w+.6,h+.6,5.5))],'Open connector pocket')
        sx=x+(w/2+1.2)*(1 if x==-57 else -1)
        link=b.box('Rear interface depth bridge',(sx,52.5,-3.0),(1.6,8,11.0))
        stop=b.box('Switch housing shoulder stop',(x,y,2.0),(w+2.8,h+2.8,1))
        stop=b.cut(stop,[b.box('Switch terminals open well',(x,y,1),(11.6,4.5,5))],'Support housing ends and clear all terminal rows')
        carrier=b.join(carrier,[cup,link,stop],'Rear controls retained by removable carrier')
    lid=b.cut(lid,[b.rounded_xy('Switch internal body recess',-14,55,5.2,13.6,4.5,1,2.6)],'Hidden switch body clearance')
    for x in (-46.2,-23.8):
        lid=b.join(lid,[b.box('Speaker retainer rear capture',(x,54,4.125),(2,4.5,4.15))],'Rear lid positively traps TPU speaker ring')
    foam=sleeve(b,'Speaker rim foam',(-35,54,-2.8),(-35,54,-2.55),10.5,9.7)
    hardware(b,foam,'Speaker rim foam allowance',(45,51,58))
    # Perforated, recessed grille keeps the speaker hidden behind the back shell.
    holes=[]
    for ix in range(-3,4):
        for iy in range(-3,4):
            if ix*ix+iy*iy<=10:
                holes.append(b.cyl('Speaker grille hole',(-35+ix*2.5,54+iy*2.5,4.6),(-35+ix*2.5,54+iy*2.5,9.1),.65))
    lid=b.cut(lid,holes,'Hidden rear audio grille')
    # Rear lid compresses only rigid guides, with positive 0.3 mm seating clearance.
    for x in (-60.5,-9.5):
        post=b.box('Carrier rear stop',(x,96,5.45),(2.4,4,1.7))
        lid=b.join(lid,[post],'Rear cap traps removable carrier')
    b.paint(carrier,'Electronics carrier graphite',(67,75,83));b.add_part(carrier,'Removable electronics and padded battery carrier')
    # Update objects that were modified after registration.
    rack.name='PRINT | Two hip servo clip rack';front.name='PRINT | Original head - no exterior screws';lid.name='PRINT | Rear lid - two squeeze releases'
    return front,lid,rack
