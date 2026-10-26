"""Four direct-drive MG90S, two in head and one flat inside each foot.
Mechanical prototype: horn fit and snap fatigue need physical tests.
"""
import adsk.core as C
import adsk.fusion as F
import adsk
import os, json, math, traceback, itertools
from .base import Build,new_group,pt,vi,objs,vector,revolute
from .servo_detail import make_servo
from .electronics import install_electronics
from .refinement import refine_parts,apply_theme,THEMES
HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(HERE,'..','..','outputs','Emo-Complete'))
BACKUP=os.path.abspath(os.path.join(HERE,'..','..','outputs','Emo-4servo','Original-user-backup.f3d'))
_packaged=os.path.abspath(os.path.join(HERE,'..','..'))
if os.path.basename(_packaged)=='Emo-Complete':
    OUT=_packaged
    BACKUP=os.path.join(OUT,'Original-user-backup.f3d')
HIP_X=(-62.5,-7.5)
LOG=os.path.join(HERE,'build-log.txt')
def log(s):
    with open(LOG,'a') as f:f.write(str(s)+'\n')

def move(b,body,delta):
    m=C.Matrix3D.create();m.translation=vector(tuple(v/10 for v in delta))
    data=b.comp.features.moveFeatures.createInput2(objs([body]));data.defineAsFreeMove(m)
    return b.comp.features.moveFeatures.add(data).bodies.item(0)

def finish(b,body,name,color=(44,47,51)):
    b.paint(body,name,color);return b.add_part(body,name)

def sleeve(b,name,a,c,outer,inner):
    t=b.cyl(name,a,c,outer)
    d=tuple(c[i]-a[i] for i in range(3));l=math.sqrt(sum(v*v for v in d))
    aa=tuple(a[i]-d[i]/l*.1 for i in range(3));cc=tuple(c[i]+d[i]/l*.1 for i in range(3))
    return b.cut(t,[b.cyl('Bore',aa,cc,inner)],name+' bore')

def shell(b,source):
    h=source.copyToComponent(b.occ)
    patch=b.rounded_xy('Restore face for single OLED',-35,78,-44,58,32,4,8)
    h=b.join(h,[patch,b.rounded_xy('Full outline service back',-35,71.5,6.5,80,65,15,3)],'Fill eye apertures and form full-size service back')
    h=b.cut(h,[b.rounded_xy('Original-height electronics cavity',-35,71.5,-17.5,74,60,11,47)],'Hollow original unraised head')
    # Relieve only the undersides around the user's pre-existing overlap.
    for cx in HIP_X:
        h=b.cut(h,[b.cyl('Hip swept clearance',(cx,37,-20),(cx,48.5,-20),26.5)],'Clear existing head-leg overlap for yaw')
    # OLED aperture flush in existing front, no external flange or fasteners.
    h=b.cut(h,[b.rounded_xy('OLED viewing aperture',-35,78,-47,22.8,12.2,1,12)],'OLED face window')
    h=b.cut(h,[b.rounded_xy('Hidden OLED insertion bay',-35,78,-42.4,32.2,32.2,2.3,6.2)],'Rear loaded OLED bay')
    for cx in HIP_X:
        h=b.cut(h,[b.box('Hip tab shell clearance',(cx,59.2,-25.7),(13.1,2.7,33.2))],'Hidden hip ear clearance')
    for cx in HIP_X:
        h=b.cut(h,[b.box('Hip electrical lead relief',(cx,75.6,-41.7),(4,3,5))],'Hip cable exit clearance')
        h=b.cut(h,[b.box('Hip bearing rear loading groove',(cx,49,-10.5),(19.4,2.2,41))],'Rear insertion path for loaded hip bearing')
    # Head rear splits at Z5; preserve original exterior geometry.
    data=b.comp.features.splitBodyFeatures.createInput(h,b.plane('z',5),True)
    feature=b.comp.features.splitBodyFeatures.add(data);feature.name='Original rear outline - clip lid'
    front=min(tuple(feature.bodies),key=lambda q:q.physicalProperties.centerOfMass.z)
    lid=max(tuple(feature.bodies),key=lambda q:q.physicalProperties.centerOfMass.z)
    for x,sgn in ((-68.8,-1),(-1.2,1)):
        for y in (65,):
            # 1.2-thick cantilever, anchored in lid; accessible inward release.
            beam=b.box('PETG rear latch beam',(x,y,-1.8),(.8,8,16))
            hook=b.box('Rear latch hook',(x+sgn*.55,y,-8.8),(1.2,8,1.2))
            lid=b.join(lid,[beam,hook],'Integral rear snap latch')
            relief=b.box('Latch clearance',(x,y,-2),(1.5,8.6,16.6))
            pocket=b.box('Latch locking pocket',(x+sgn*.55,y,-8.8),(1.8,8.6,1.8))
            front=b.cut(front,[relief,pocket],'Rear latch pocket and flexure space')
    for x in (-65.5,-4.5):
        stop=b.cyl('Rear lid rack retaining post',(x,67,-9.7),(x,67,6.2),2)
        lid=b.join(lid,[stop],'Lid traps hip rack against keyed front seats')
        front=b.cut(front,[b.cyl('Rack post passage',(x,67,3.5),(x,67,5.4),2.35)],'Rear lid rack post clearance')
    for x in (-74.0,4.0):
        front=b.cut(front,[b.box('Side pinch access',(x,65,-8.8),(10,9.0,4.0))],'Two accessible rear lid releases')
    finish(b,front,'Original head - no exterior screws')
    finish(b,lid,'Rear lid - two squeeze releases')
    b.occ.isGrounded=True
    return front,lid

def oled(b):
    # Hidden carrier and slide-out cap, matching 27 x27 headerless PCB, with soldered flexible leads.
    carrier=b.rounded_xy('Hidden OLED tray',-35,78,-42.5,31.6,31.6,2,5)
    inner=b.rounded_xy('PCB bay',-35,78,-42.1,27.6,27.6,1,5)
    aperture=b.rounded_xy('Tray light aperture',-35,78,-45,22.8,12.2,1,6)
    carrier=b.cut(carrier,[inner,aperture],'OLED board slide fit')
    for x in (-48.5,-21.5):
        pad=b.box('PCB rear retaining lip',(x,78,-41.1),(2,20,1))
        carrier=b.join(carrier,[pad],'Captive OLED PCB edge clips')
    finish(b,carrier,'OLED hidden slide carrier',(43,52,60))
    board=b.box('OLED PCB',(-35,78,-42.3),(27,27,1.2));b.paint(board,'OLED blue PCB',(14,69,121));b.add_hardware(board,'OLED 27mm headerless PCB')
    glass=b.rounded_xy('OLED black glass',-35,78,-46.15,24.5,14,1,1.0)
    b.paint(glass,'Screen black',(3,9,13));glass.name='VIS | OLED black glass';b.visuals.append(glass)
    for x in (-39.4,-30.6):
        eye=b.rounded_xy('OLED cyan eye',x,78,-46.7,3.2,5.5,1.25,.15)
        b.paint(eye,'OLED lit cyan',(99,238,223));eye.name='VIS | OLED eye';b.visuals.append(eye)
    # Carrier is keyed to two internal head rails and captured by rear rack.
    return carrier

def horn(b,cx,label):
    arm=b.box('Stock hip horn arm',(cx,47.1,-14),(5.5,1.5,13))
    hub=b.cyl('Hip horn hub',(cx,46.4,-20),(cx,50.9,-20),3.6)
    arm=b.join(arm,[hub],'Supplied MG90S hip horn')
    arm=b.cut(arm,[b.cyl('Spline and screw bore',(cx,45.5,-20),(cx,51.5,-20),2.4)],'Hip horn bore')
    b.paint(arm,'Stock horn ivory',(225,226,216));b.add_hardware(arm,'Stock hip horn '+label)
    screw=b.cyl('Hidden stock hip horn screw',(cx,45.8,-20),(cx,49.9,-20),.8)
    b.paint(screw,'Stock horn steel',(120,124,129));screw.name='VIS | hidden hip horn screw '+label;b.visuals.append(screw)

def hip_rack(b):
    frame=b.box('Hip rack rear spine',(-35,65,-11),(70,27,2))
    frame=b.join(frame,[b.box('Lower rack shelf',(-35,51,-26),(74,2,29))],'Hip rack base')
    for x in (-70.6,.6):frame=b.join(frame,[b.box('Hip rack guide',(x,65,-26),(2.6,27,29))],'Hip rack side guide')
    frame=b.join(frame,[b.box('Hip rack upper crossbar',(-35,79,-26),(74,2,27))],'Hip rack upper bridge')
    for cx in HIP_X:
        frame=b.join(frame,[b.box('Hip ear saddle',(cx,57.1,-25.7),(16,2,34))],'Hip ear support')
        frame=b.cut(frame,[b.box('Hip case front loading clearance',(cx,66.1,-33.5),(13.1,24,39.1)),
                           b.box('Hip tab clearance',(cx,59.2,-25.7),(13.1,2.7,33.2)),
                           b.cyl('Output boss passage',(cx,48,-20),(cx,56,-20),6),
                           b.cyl('Second gear hump',(cx,52,-30.2),(cx,55,-30.2),5)],'Two hip pockets')
        for sign in (-1,1):
            frame=b.cut(frame,[b.box('Snap flexure clearance',(cx+sign*7.2,68.5,-40.4),(3.2,18,5))],'Free single-ended snap tongue')
            beam=b.box('Hip tab snap tongue',(cx+sign*7.2,70,-40.4),(.8,20,3))
            hook=b.box('Hip tab retaining hook',(cx+sign*6.35,60.8,-40.4),(2.1,1,3))
            frame=b.join(frame,[beam,hook],'Hip snap retention')
    for cx in HIP_X:
        frame=b.cut(frame,[b.cyl('Hip rotor flange clearance',(cx,49.8,-20),(cx,51.6,-20),9.2),
                           b.box('Hip flange front insertion slot',(cx,50.7,-35.5),(18.8,1.8,31))],'Front load captive hip rotor above bearing')
        ring=sleeve(b,'Hip C thrust bearing',(cx,48.3,-20),(cx,49.7,-20),10.5,5.6)
        ring=b.intersect(ring,b.box('Bearing insertion flats',(cx,49,-20),(18.8,3,24)),'Flatten only lateral bearing edges')
        slot=b.box('Front loading journal slot',(cx,49,-29),(11.3,2,19))
        ring=b.cut(ring,[slot],'Open C bearing for lateral leg assembly')
        posts=[b.cyl('Hip bearing support',(cx+dx,49.5,-11.6),(cx+dx,51.9,-11.6),1) for dx in (-6,6)]
        frame=b.join(frame,posts+[ring],'Hip axial bearing carries leg weight')
    finish(b,frame,'Two hip servo clip rack',(84,89,95))
    return frame

def hip_capture(b,body,cx):
    body=b.cut(body,[b.box('Reversed hip horn arm pocket',(cx,47.25,-14),(6,2.1,13.8)),
                     b.cyl('Hip horn hub pocket',(cx,45.8,-20),(cx,51,-20),3.9)],'Hidden hip horn key')
    return body

def rounded_xz(b,name,cx,cy,cz,width,depth,r,height):
    box=b.box(name,(cx,cy,cz),(width-2*r,height,depth))
    additions=[b.box(name+' cross',(cx,cy,cz),(width,height,depth-2*r))]
    additions += [b.cyl(name+' corner',(cx+dx,cy-height/2,cz+dz),(cx+dx,cy+height/2,cz+dz),r) for dx in (-width/2+r,width/2-r) for dz in (-depth/2+r,depth/2-r)]
    return b.join(box,additions,name+' rounded outline')

def leg(b,source,cx,label):
    body=source.copyToComponent(b.occ)
    body=b.intersect(body,b.box('Original slim upper U fork',(cx,42,-20),(30,36,60)),'Keep original open upper leg')
    # Original front/back walls stay slender. No enclosing block remains.
    front_neck=b.box('Slim driven neck',(cx,20.0,-37.65),(8.4,22.0,3.5))
    front_crown=b.cyl('Driven leg pivot crown',(cx,9.5,-39.4),(cx,9.5,-35.9),5.7)
    bridge=b.box('Front U fork transition',(cx,27.0,-40),(15,6,7.6))
    rear_neck=b.box('Slim rear neck',(cx,20,2.5),(8.4,22,3.5))
    rear_crown=b.cyl('Passive leg pivot crown',(cx,9.5,.75),(cx,9.5,4.25),5.7)
    rear_bridge=b.box('Rear U fork transition',(cx,27,2.5),(15,6,5))
    body=b.join(body,[front_neck,front_crown,bridge,rear_neck,rear_crown,rear_bridge],'Slim leg with two supported ankle ends')
    body=b.cut(body,[b.box('Upward stock horn key',(cx,13.3,-38.9),(5.6,8.6,4.2)),
                     b.cyl('Stock horn hub pocket',(cx,9.5,-40),(cx,9.5,-35.5),3.9),
                     b.cyl('Passive rear axle bore',(cx,9.5,1.4),(cx,9.5,4.45),1.65)],'Keyed driven leg and passive rear journal')
    stem=sleeve(b,'Hip axial journal',(cx,47.8,-20),(cx,51.4,-20),5.4,4.05)
    flange=sleeve(b,'Hip captive flange',(cx,50,-20),(cx,51.4,-20),8.8,4.05)
    body=b.join(body,[stem,flange],'Original hip captured rotor')
    body=hip_capture(b,body,cx)
    # Electrical cable tunnel in the rear leg; servo itself now belongs to foot.
    body=b.cut(body,[b.box('Rear electrical cable tunnel',(cx,32,2.5),(3,30,2.4)),
                     b.box('Rear wire entry',(cx,19,1.7),(3,6,3)),
                     b.box('Top cable bridge',(cx,45.5,-3.5),(3,2,13)),
                     b.box('Top cable lateral turn',(cx+2.5,45.5,-8.6),(8,2,3)),
                     b.box('Hip cable bypass',(cx+5,46,-8.6),(3,8,3))],'Hidden electrical lead routing')
    finish(b,body,'Leg '+label+' - slim open U fork')
    horn(b,cx,label)
    ankle_horn(b,cx,label)
    return body

def ankle_horn(b,cx,label):
    hub=b.cyl('Stock ankle horn hub',(cx,9.5,-38.3),(cx,9.5,-34.9),3.6)
    blade=b.box('Upward original horn arm',(cx,13.3,-37.95),(5,8,1.4))
    h=b.join(hub,[blade],'Stock horn fixed directly to slim leg')
    h=b.cut(h,[b.cyl('Supplied horn spline socket',(cx,9.5,-38.7),(cx,9.5,-34.6),2.4)],'Stock spline and screw socket')
    b.paint(h,'Stock nylon horn ivory',(224,226,217));b.add_hardware(h,'Stock ankle horn '+label+' - fixed to leg')
    screw=b.cyl('Hidden ankle horn screw',(cx,9.5,-38.4),(cx,9.5,-35.0),.8)
    b.paint(screw,'Stock horn screw metal',(125,130,136));screw.name='VIS | hidden ankle horn screw '+label;b.visuals.append(screw)

def foot(b,source,cx,label):
    hand=-1 if label=='L' else 1
    motor_x=cx+hand*5.7
    body=source.copyToComponent(b.occ)
    body=b.intersect(body,b.box('Original sole outline',(cx,0,-20),(110,24,90)),'Preserve original 50 by 60 sole')
    pod=rounded_xz(b,'Raised smooth servo shoe',cx+hand*7.5,10.7,-20,40,40,10,15.6)
    body=b.join(body,[pod],'Blend motor pod into original foot island')
    body=b.cut(body,[b.box('Flat servo body clearance',(motor_x,9.5,-20.1),(23.5,13.1,24.0)),
                     b.box('Servo ears open insertion',(motor_x,9.5,-27.0),(33.2,13.1,2.7)),
                     b.cyl('Main output hump clearance',(cx,9.5,-36),(cx,9.5,-31),5.8),
                     b.cyl('Second output hump clearance',(cx+hand*10.2,9.5,-33.4),(cx+hand*10.2,9.5,-31),5.05)],'Flat MG90S foot pocket')
    # Open the entire cavity upward; the removable roof traps motor ears.
    body=b.cut(body,[b.box('Top loaded servo insertion',(motor_x,17,-20.1),(33.2,14,25.3))],'Open top installation bay')
    # Front horn and rear journal sit between load-bearing thrust walls.
    body=b.cut(body,[b.cyl('Front leg crown clearance',(cx,9.5,-39.75),(cx,9.5,-35.55),6.05),
                     b.box('Front neck roof sweep',(cx,20,-37.65),(14.6,25,4.2)),
                     b.box('Front hidden screw access',(cx,10.7,-41.2),(19.0,15.0,4.8)),
                     b.cyl('Rear leg crown clearance',(cx,9.5,.4),(cx,9.5,4.6),6.05),
                     b.box('Rear neck roof sweep',(cx,20,2.5),(14.6,25,4.2)),
                     b.cyl('Rear steel axle bore',(cx,9.5,4.4),(cx,9.5,7.1),1.65)],'Supported direct ankle articulation')
    # Electrical leads need a true passage, including cosmetics outside body audit.
    body=b.cut(body,[b.box('Motor cable outlet',(cx+hand*19.7,9.5,-10.6),(6,4,4)),
                     b.box('Outer cable return',(cx+hand*19.7,9.5,-8),(4,4,8)),
                     b.box('Cable behind motor',(cx+hand*10,9.5,-5.5),(23,4,4)),
                     b.box('Rear ankle service loop',(cx,12.5,-2),(4,10,9))],'Continuous foot cable passage to rear leg')
    # Add the rear bearing outside the old top island but inside the original sole.
    boss=sleeve(b,'Passive rear bearing socket',(cx,9.5,4.6),(cx,9.5,7.0),4.0,1.65)
    support=b.box('Rear bearing root',(cx,5.2,5.8),(8,5.0,2.4))
    body=b.join(body,[support,boss],'Rear foot journal load support')
    body=b.cut(body,[b.cyl('Rear cap seat',(cx,9.5,6.1),(cx,9.5,7.2),2.8),
                     b.cyl('Rear cap bead receiver',(cx,9.5,6.35),(cx,9.5,6.85),3.0)],'TPU axle cap receiver')
    # Roof follows same radius as the shoe; skirt conceals the horn screw.
    lid=rounded_xz(b,'Smooth removable foot roof',cx+hand*7.5,17.5,-20,40,40,10,2.0)
    skirt=b.box('Hidden front screw skirt',(cx,10,-41.0),(18.4,13.4,2.0))
    ribs=[b.box('Skirt roof bridge',(cx+dx,16.8,-38.4),(1.0,3.2,7.1)) for dx in (-8.4,8.4)]
    lid=b.join(lid,[skirt]+ribs,'Roof and concealed servo access face')
    lid=b.cut(lid,[b.box('Front neck motion aperture',(cx,20,-37.65),(14.6,14,4.2)),
                   b.box('Rear neck motion aperture',(cx,20,2.5),(14.6,14,4.2))],'Leg roof articulation slots')
    for dx in (-8,8):
        pad=b.box('Roof motor retaining pad',(motor_x+dx,16.25,-18.5),(3,.6,5))
        lid=b.join(lid,[pad],'Roof traps flat servo vertically')
    # Positive alignment keys carry shear; spring tongues retain the cap.
    for z in (-32,-9):
        x=cx+hand*24.5
        key=b.box('Roof outer guide',(x,15.3,z),(1.2,3.2,3.0))
        lid=b.join(lid,[key],'Hidden foot lid shear guides')
        body=b.cut(body,[b.box('Roof outer guide pocket',(x,15.2,z),(1.6,3.8,3.5))],'Roof guide clearance')
    # Pair of manually released outside clips, tucked above the sole lip.
    for z in (-28,-12):
        x=cx+hand*25.7
        beam=b.box('Foot roof latch tongue',(x,12.6,z),(.8,8.2,3.0))
        hook=b.box('Foot roof latch hook',(x+hand*.6,9.3,z),(1.8,1.0,3))
        lid=b.join(lid,[beam,hook],'Two accessible concealed foot snap latches')
        body=b.cut(body,[b.box('Foot latch flex space',(x,12.5,z),(1.4,8.8,3.6)),
                         b.box('Foot latch locking pocket',(x+hand*.6,9.3,z),(2.3,1.6,3.6))],'Foot roof clip receiver')
    # Two inner keys prevent lid lift about the outside snap latches.
    for z in (-31,-8):
        x=cx-hand*10.6
        key=b.box('Inner roof downward key',(x,15.0,z),(1.0,4,3))
        lip=b.box('Inner roof capture toe',(x-hand*.6,13.4,z),(2.0,1,3))
        lid=b.join(lid,[key,lip],'Key inner lid edge before closing outer snaps')
        body=b.cut(body,[b.box('Inner roof key receiver',(x,15,z),(1.5,4.5,3.6)),
                         b.box('Inner roof toe receiver',(x-hand*.6,13.4,z),(2.5,1.6,3.6))],'Inner cap key receiver')
    for dx in (-8.4,8.4):
        body=b.cut(body,[b.box('Front lid bridge clearance',(cx+dx,16.8,-38.4),(1.5,3.8,7.6))],'Front access skirt bridge receivers')
    body=b.intersect(body,b.box('Foot roof split datum',(cx,0,-20),(120,33,100)),'Shoe body below roof seam')
    if label=='R':
        body=b.join(body,[b.cyl('Original sole tangent reinforcement',(cx,3,-.8),(cx,3,5.8),.7)],'Repair inherited zero thickness sole edge')
        body=b.cut(body,[b.cyl('Rear crown floor clearance',(cx,9.5,.4),(cx,9.5,4.6),6.05)],'Restore rear pivot floor gap')
    finish(b,body,'Foot '+label+' - enclosed flat MG90S shoe')
    finish(b,lid,'Foot '+label+' - top access lid',(49,52,57))
    u=(hand,0,0);v=(0,hand*-1,0)
    make_servo(b,(motor_x,9.5,-8.5),u,v,(0,0,-1),'ANKLE IN FOOT '+label)
    pin=b.cyl('Short opposing steel axle',(cx,9.5,1.5),(cx,9.5,6.7),1.5)
    b.paint(pin,'Rear ankle steel',(128,134,141));b.add_hardware(pin,'Short passive axle '+label)
    cap=b.cyl('Rear hidden axle cap',(cx,9.5,6.35),(cx,9.5,7.15),2.6)
    cap=b.cut(cap,[b.cyl('Blind axle cap socket',(cx,9.5,6.2),(cx,9.5,6.95),1.55)],'Rear axle end stop')
    bead=sleeve(b,'TPU retaining bead',(cx,9.5,6.5),(cx,9.5,6.8),2.9,1.55)
    cap=b.join(cap,[bead],'Rear axle captive bead')
    finish(b,cap,'Foot '+label+' - TPU rear axle cap')
    return body

def collisions(design,groups):
    seq=[v.createForAssemblyContext(g.occ) for g in groups for v in g.parts+g.hardware]
    query=design.createInterferenceInput(objs(seq));query.areCoincidentFacesIncluded=False
    result=[]
    for item in design.analyzeInterference(query):
        if not item.interferenceBody or item.interferenceBody.volume<.00002:continue
        a,c=item.entityOne.name,item.entityTwo.name
        result.append({'a':a,'b':c,'volume_mm3':round(item.interferenceBody.volume*1000,5),
                       'bbox_mm':[[round(v*10,4) for v in item.interferenceBody.boundingBox.minPoint.asArray()],[round(v*10,4) for v in item.interferenceBody.boundingBox.maxPoint.asArray()]]})
    return result

def poses():
    limits=(15,15,12,12)
    yield (0,0,0,0)
    for i in range(4):
        for f in (-1,-.75,-.5,-.25,.25,.5,.75,1):yield tuple(limits[j]*f if j==i else 0 for j in range(4))
    for signs in itertools.product((-1,1),repeat=4):yield tuple(a*b for a,b in zip(signs,limits))

def setpose(joints,angles):
    for j,a in zip(joints,angles):j.jointMotion.rotationValue=math.radians(a)
    adsk.doEvents()

def camera(app,eye,target=(-35,54,-20)):
    cam=app.activeViewport.camera;cam.cameraType=C.CameraTypes.OrthographicCameraType
    cam.eye=pt(*eye);cam.target=pt(*target);cam.upVector=vector((0,1,0));cam.isFitView=True;cam.isSmoothTransition=False
    app.activeViewport.camera=cam;app.activeViewport.refresh()

def export(app,design,groups,joints):
    manager=design.exportManager
    for j in joints:j.isLightBulbOn=False
    for g in groups:
        g.comp.isOriginFolderLightBulbOn=False
        for s in g.comp.sketches:s.isLightBulbOn=False
    camera(app,(-200,170,-300))
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-Complete-exterior.png'),1600,1600)
    for theme in THEMES:
        apply_theme(groups,theme);app.activeViewport.refresh()
        app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-Complete-style-'+theme+'.png'),1600,1600)
    apply_theme(groups,'Cloud');camera(app,(140,140,260))
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-Complete-rear.png'),1600,1600)
    saved=[(v,v.isLightBulbOn) for g in groups for v in g.parts+g.hardware+g.visuals]
    for g in groups:
        for v in g.parts:
            if g is groups[0] and ('Original head' in v.name or 'Rear lid' in v.name or 'servo clip rack' in v.name) or 'top access lid' in v.name:v.isLightBulbOn=False
    camera(app,(-200,150,-260),(-35,58,-20))
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-Complete-cutaway.png'),1600,1600)
    # Dedicated packing views, using actual geometry from the assembly.
    for g in groups[1:]:
        for v in g.parts+g.hardware+g.visuals:v.isLightBulbOn=False
    camera(app,(-120,130,-220),(-35,75,-18))
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-Complete-electronics.png'),1600,1600)
    for v,on in saved:v.isLightBulbOn=on
    groups[0].parts[1].isLightBulbOn=False
    camera(app,(110,140,240),(-35,75,-5))
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-Complete-service.png'),1600,1600)
    for g in groups:
        for v in g.parts:
            if g is groups[0] and ('Original head' in v.name or 'Rear lid' in v.name or 'servo clip rack' in v.name) or 'top access lid' in v.name:v.isLightBulbOn=False
    # A close-up of the exact coaxial shaft/foot connection.
    for g in (groups[0],groups[3],groups[4]):
        for body in g.parts+g.hardware+g.visuals:body.isLightBulbOn=False
    for body in groups[1].hardware+groups[1].visuals:
        if 'hip' in body.name.lower():body.isLightBulbOn=False
    camera(app,(-160,95,-240),(-62.5,24,-20))
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-Complete-mechanism.png'),1600,1600)
    for v,on in saved:v.isLightBulbOn=on
    setpose(joints,(10,-10,9,-9));camera(app,(-200,170,-300))
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-Complete-motion.png'),1600,1600)
    setpose(joints,(0,0,0,0));camera(app,(-200,170,-300))
    assert manager.execute(manager.createFusionArchiveExportOptions(os.path.join(OUT,'Emo-Complete.f3d')))
    for g in groups:
        for body in g.parts:
            path=os.path.join(OUT,body.name.replace('PRINT | ','').replace(' ','_')+'.stl')
            opt=manager.createSTLExportOptions(body,path);opt.meshRefinement=F.MeshRefinementSettings.MeshRefinementHigh;opt.unitType=F.DistanceUnits.MillimeterDistanceUnits
            assert manager.execute(opt)

def run(context):
    os.makedirs(OUT,exist_ok=True)
    with open(LOG,'w') as f:f.write('EMO COMPLETE\n')
    app=C.Application.get()
    try:
        doc=app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(BACKUP))
        doc.name='Emo original - complete assembly - working'
        design=F.Design.cast(app.activeProduct);design.designIntent=F.DesignIntentTypes.HybridDesignIntentType
        root=design.rootComponent;source=tuple(root.bRepBodies)
        head=new_group(design,'01 Original head - 2 hip MG90S + OLED')
        log('Shell');front,lid=shell(head,source[2])
        log('Hip servos')
        for cx,label in zip(HIP_X,('L','R')):make_servo(head,(cx,77.7,-25.7),(0,0,-1),(1,0,0),(0,-1,0),'HIP '+label)
        rack=hip_rack(head);oled(head)
        for x in (-53,-17):
            rail=head.box('OLED slide rail',(x,78,-42.5),(2,32,6));front=head.join(front,[rail],'OLED internal slide rail')
            lip=head.box('OLED carrier rear clip',(x+1.1 if x<-35 else x-1.1,78,-39.25),(2.6,26,.7));front=head.join(front,[lip],'OLED hidden carrier clip')
        front=head.cut(front,[head.temp_body(head.temp.copy(rack),'Rack receiver')],'Keyed internal hip rack receiver')
        tool=head.temp.copy(rack);matrix=C.Matrix3D.create();scale=1.006
        for i in range(3):matrix.setCell(i,i,scale)
        matrix.translation=vector(tuple((1-scale)*v/10 for v in (-35,65,-26)));assert head.temp.transform(tool,matrix)
        front=head.cut(front,[head.temp_body(tool,'Rack tolerance tool')],'Hip rack clearance')
        head.parts[0]=front;front.name='PRINT | Original head - no exterior screws'
        log('Electronics');front,lid,rack=install_electronics(head,front,lid,rack)
        head.parts[0]=front;head.parts[1]=lid;head.parts[2]=rack
        groups=[head];legs=[];feet=[]
        for original,cx,label in zip(source[:2],HIP_X,('L','R')):
            lb=new_group(design,'Leg '+label+' - slim U fork');log('Leg '+label);leg(lb,original,cx,label)
            fb=new_group(design,'Foot '+label+' - enclosed MG90S direct joint');log('Foot '+label);foot(fb,original,cx,label)
            groups.extend((lb,fb));legs.append(lb);feet.append(fb)
        for v in source:v.isLightBulbOn=False
        for s in root.sketches:s.isLightBulbOn=False
        joints=[]
        for lb,cx,label in zip(legs,HIP_X,('L','R')):joints.append(revolute(root,head,lb,'HIP '+label+' direct yaw 15deg',(cx,48,-20),(0,1,0),15))
        for lb,fb,cx,label in zip(legs,feet,HIP_X,('L','R')):joints.append(revolute(root,lb,fb,'ANKLE '+label+' direct roll 12deg',(cx,9.5,-37),(0,0,1),12))
        log('Refinement');refine_parts(groups)
        log('Neutral audit');neutral=collisions(design,groups);log(json.dumps(neutral))
        report={'architecture':'4 direct MG90S: 2 hip motors in original head, 1 ankle motor per foot, horn fixed to leg','head_lift_mm':0,'outer_leg_width_mm':15,'ankle_servo_in_foot':True,'foot_center_height_mm':18.5,'bowden_tendons':0,'joints':4,'motion_links':0,'hidden_horn_screws':4,'neutral_collisions':neutral,'poses':[]}
        if not neutral:
            log('Motion sweep')
            for angles in poses():
                setpose(joints,angles)
                for lb,fb,cx in zip(legs,feet,HIP_X):
                    a=pt(cx,9.5,-37);a.transformBy(lb.occ.transform2)
                    c=pt(cx,9.5,-37);c.transformBy(fb.occ.transform2)
                    assert a.distanceTo(c)<1e-6,'Ankle ceased to be coaxial with servo'
                    u=vector((0,0,1));u.transformBy(lb.occ.transform2)
                    v=vector((0,0,1));v.transformBy(fb.occ.transform2)
                    assert abs(u.dotProduct(v)-1)<1e-6,'Ankle axis changed relative to case'
                report['poses'].append({'degrees':angles,'collisions':collisions(design,groups),'transforms':[g.occ.transform2.asArray() for g in groups]})
            setpose(joints,(0,0,0,0))
        report['feature_errors']=[q.entity.name for q in design.timeline if hasattr(q.entity,'healthState') and q.entity.healthState==F.FeatureHealthStates.ErrorFeatureHealthState]
        report['parts']=[{'name':v.name,'solid':v.isSolid,'volume_mm3':v.volume*1000} for g in groups for v in g.parts]
        with open(os.path.join(OUT,'mechanical-validation.json'),'w') as f:json.dump(report,f,indent=2)
        log('Failed samples: '+str(sum(bool(p['collisions']) for p in report['poses'])))
        assert not report['neutral_collisions'] and len(report['poses'])==49 and not any(p['collisions'] for p in report['poses']), 'Rigid interference remains'
        assert not report['feature_errors'],report['feature_errors']
        for g in groups:
            assert g.comp.bRepBodies.count==len(g.parts+g.hardware+g.visuals),'Unclassified or disconnected body'
        log('Assembly insertion samples')
        from .assembly_audit import audit_carrier
        from .hip_audit import audit_hips
        assert audit_carrier(app,design,[g.occ for g in groups])['all_passed'],'See cassette-insertion-validation.json'
        assert audit_hips(app,design,[g.occ for g in groups])['all_passed'],'See hip-insertion-validation.json'
        log('Export');export(app,design,groups,joints);log('SUCCESS')
    except Exception:
        log(traceback.format_exc());app.activeDocument.activate()
