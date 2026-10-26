"""Four head-mounted MG90S, original shell, remote tendon ankles.
Mechanical prototype: cable flexibility and snap fatigue need physical tests.
"""
import adsk.core as C
import adsk.fusion as F
import adsk
import os, json, math, traceback, itertools
from .base import Build,new_group,pt,vi,objs,vector,revolute
from .servo_detail import make_servo
HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(HERE,'..','..','outputs','Emo-HeadDrive'))
BACKUP=os.path.abspath(os.path.join(HERE,'..','..','outputs','Emo-4servo','Original-user-backup.f3d'))
_packaged=os.path.abspath(os.path.join(HERE,'..','..'))
if os.path.basename(_packaged)=='Emo-HeadDrive':
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
    h=b.join(h,[patch],'Fill original eye apertures behind OLED face')
    h=b.cut(h,[b.rounded_xy('Original-height electronics cavity',-35,71.5,-18.5,74,59,9,45)],'Hollow original unraised head')
    # Relieve only the undersides around the user's pre-existing overlap.
    for cx in HIP_X:
        h=b.cut(h,[b.cyl('Hip swept clearance',(cx,37,-20),(cx,48.5,-20),26.5)],'Clear existing head-leg overlap for yaw')
    # OLED aperture flush in existing front, no external flange or fasteners.
    h=b.cut(h,[b.rounded_xy('OLED viewing aperture',-35,78,-47,22.8,12.2,1,12)],'OLED face window')
    h=b.cut(h,[b.rounded_xy('Hidden OLED insertion bay',-35,78,-42.4,34.6,32.1,2.3,6.2)],'Rear loaded OLED bay')
    for cx in HIP_X:
        h=b.cut(h,[b.box('Hip tab shell clearance',(cx,59.2,-25.7),(13.1,2.7,33.2))],'Hidden hip ear clearance')
    # Head rear splits at Z5; preserve original exterior geometry.
    data=b.comp.features.splitBodyFeatures.createInput(h,b.plane('z',5),True)
    feature=b.comp.features.splitBodyFeatures.add(data);feature.name='Original rear outline - clip lid'
    front=min(tuple(feature.bodies),key=lambda q:q.physicalProperties.centerOfMass.z)
    lid=max(tuple(feature.bodies),key=lambda q:q.physicalProperties.centerOfMass.z)
    for x,sgn in ((-68.8,-1),(-1.2,1)):
        for y in (64,92):
            # 1.2-thick cantilever, anchored in lid; accessible inward release.
            beam=b.box('PETG rear latch beam',(x,y,-1.8),(1.2,4,14))
            hook=b.box('Rear latch hook',(x+sgn*1.7,y,-7.1),(4.0,4,1.1))
            lid=b.join(lid,[beam,hook],'Integral rear snap latch')
            relief=b.box('Latch clearance',(x,y,-2),(1.8,4.6,14.5))
            pocket=b.box('Latch locking pocket',(x+sgn*1.7,y,-7.1),(4.6,4.6,1.7))
            front=b.cut(front,[relief,pocket],'Rear latch pocket and flexure space')
    finish(b,front,'Original head - no exterior screws')
    finish(b,lid,'Rear lid - four release clips')
    b.occ.isGrounded=True
    return front,lid

def servo_layout(b):
    references=[]
    for cx,label in zip(HIP_X,('L','R')):
        references.append(make_servo(b,(cx,77.7,-25.7),(0,0,-1),(1,0,0),(0,-1,0),'HIP '+label))
    for x,sgn,label in ((-55,-1,'L'),(-15,1,'R')):
        references.append(make_servo(b,(x,88,-38),(sgn,0,0),(0,sgn,0),(0,0,1),'REMOTE ANKLE '+label))
    return references

def cage(b,servos):
    frame=b.box('Internal servo rack rear spine',(-35,74,-11),(70,45,2))
    frame=b.join(frame,[b.box('Lower rack shelf',(-35,51,-26),(68,2,29))],'Rack spine and shelf')
    for x in (-68.5,-1.5):
        frame=b.join(frame,[b.box('Outer cage rail',(x,74,-26),(2,45,29))],'Rack side guide')
    top=b.box('Top snap cross rail',(-35,95.5,-26),(68,2,29))
    frame=b.join(frame,[top],'Rack upper bridge')
    for cx in HIP_X:
        frame=b.join(frame,[b.box('Hip retention saddle',(cx,57.1,-25.7),(16,2,34))],'Hip tab support shelf')
        cuts=[b.box('Hip case insertion clearance',(cx,66.1,-25.7),(13.1,24,23.5)),
              b.box('Hip tab pocket',(cx,59.2,-25.7),(13.1,2.7,33.2)),
              b.cyl('Hip output passage',(cx,48,-20),(cx,56,-20),6.0),
              b.cyl('Second gear hump clearance',(cx,52,-30.2),(cx,55,-30.2),5.0)]
        frame=b.cut(frame,cuts,'Hip snap cage clearances')
        # Flexible retainers hook above the mounting ears, no M2 screws.
        for sign in (-1,1):
            z=-40.4
            relief=b.box('Long snap flexure clearance',(cx+sign*7.2,57.4,z),(2,10.8,4))
            frame=b.cut(frame,[relief],'Isolate snap tongue from tab saddle')
            beam=b.box('Hip servo capture tongue',(cx+sign*7.2,56.5,z),(.8,13,3))
            hook=b.box('Hip ear capture lip',(cx+sign*6.35,60.8,z),(2.1,1,3))
            frame=b.join(frame,[beam,hook],'Hip servo tab snap retainer')
    for x,sgn in ((-55,-1),(-15,1)):
        frame=b.join(frame,[b.box('Remote lower seat',(x,80.8,-26.4),(33.6,2,25))],'Remote servo lower seat')
        frame=b.cut(frame,[b.box('Upper case clearance',(x,88,-26.4),(23.5,13.1,24)),
                           b.box('Upper tab clearance',(x,88,-19.5),(33.2,13.1,2.7)),
                           b.cyl('Remote output opening',(x-sgn*5.7,88,-16),(x-sgn*5.7,88,-7),6)],'Remote servo pocket')
    for x in (-49.3,-20.7):
        for sign in (-1,1):
            stop=b.box('Upper Bowden stop',(x+sign*8,75,-9),(4,7,6))
            frame=b.join(frame,[stop],'Head fixed Bowden reaction stop')
            frame=b.cut(frame,[b.cyl('Upper sheath socket',(x+sign*8,71,-7.5),(x+sign*8,76.5,-7.5),1.05),
                               b.cyl('Upper tendon exit',(x+sign*8,76.4,-7.5),(x+sign*8,79,-7.5),.4)],'Upper stepped cable stop')
    # Recess receiver tongues in shell; rack will be captured by rear lid.
    finish(b,frame,'Removable four-servo snap rack',(86,91,96))
    return frame

def oled(b):
    # Hidden carrier and slide-out cap, matching 29.2 x26.7 assumed PCB.
    carrier=b.rounded_xy('Hidden OLED tray',-35,78,-42.5,34,31.5,2,5)
    inner=b.rounded_xy('PCB bay',-35,78,-42.1,30.0,27.5,1,5)
    aperture=b.rounded_xy('Tray light aperture',-35,78,-45,22.8,12.2,1,6)
    carrier=b.cut(carrier,[inner,aperture],'OLED board slide fit')
    for x in (-49.6,-20.4):
        pad=b.box('PCB rear retaining lip',(x,78,-41.1),(2,20,1))
        carrier=b.join(carrier,[pad],'Captive OLED PCB edge clips')
    finish(b,carrier,'OLED hidden slide carrier',(43,52,60))
    board=b.box('OLED PCB',(-35,78,-42.3),(29.2,26.7,1.2));b.paint(board,'OLED blue PCB',(14,69,121));b.add_hardware(board,'OLED assumed PCB')
    glass=b.rounded_xy('OLED black glass',-35,78,-46.15,24.5,14,1,1.0)
    b.paint(glass,'Screen black',(3,9,13));glass.name='VIS | OLED black glass';b.visuals.append(glass)
    for x in (-39.4,-30.6):
        eye=b.rounded_xy('OLED cyan eye',x,78,-46.7,3.2,5.5,1.25,.15)
        b.paint(eye,'OLED lit cyan',(99,238,223));eye.name='VIS | OLED eye';b.visuals.append(eye)
    # Carrier is keyed to two internal head rails and captured by rear rack.
    return carrier

def horn(b,cx,label):
    arm=b.box('Stock hip horn arm',(cx,47.1,-26),(5.5,1.5,13))
    hub=b.cyl('Hip horn hub',(cx,46.4,-20),(cx,50.9,-20),3.6)
    arm=b.join(arm,[hub],'Supplied MG90S hip horn')
    arm=b.cut(arm,[b.cyl('Spline and screw bore',(cx,45.5,-20),(cx,51.5,-20),2.4)],'Hip horn bore')
    b.paint(arm,'Stock horn ivory',(225,226,216));b.add_hardware(arm,'Stock hip horn '+label)
    screw=b.cyl('Hidden stock hip horn screw',(cx,45.8,-20),(cx,49.9,-20),.8)
    b.paint(screw,'Stock horn steel',(120,124,129));screw.name='VIS | hidden hip horn screw '+label;b.visuals.append(screw)

def leg(b,source,cx,label):
    body=source.copyToComponent(b.occ)
    body=b.intersect(body,b.box('Original leg only',(cx,60,-20),(30,91,60)),'Separate leg at Y14.5 for ankle roll clearance')
    # Remove all foot material under original U-shaped leg plates.
    for z in (-42.5,2.5):
        boss=b.cyl('Passive ankle bearing cheek',(cx,16,z-2.5),(cx,16,z+2.5),5)
        body=b.join(body,[boss],'Ankle bearing within original leg plates')
        body=b.cut(body,[b.cyl('Unthreaded 3mm axle clearance',(cx,16,z-3),(cx,16,z+3),1.65)],'Plain pivot pin bore')
    for z in (-44.4,4.4):
        body=b.cut(body,[b.cyl('Recess for concealed axle plug',(cx,16,z-.65),(cx,16,z+.65),2.8)],'Axle end plug recess')
        body=b.cut(body,[b.cyl('TPU retaining bead groove',(cx,16,z-.35),(cx,16,z+.35),3.0)],'Axle cap snap bead pocket')
    # Horn recessed in existing upper bridge. Fastener stays inside the head.
    body=b.cut(body,[b.box('Stock horn arm pocket',(cx,47.25,-26),(6,2.1,13.8)),
                     b.cyl('Horn hub pocket',(cx,45.8,-20),(cx,51,-20),3.9)],'Hidden hip horn seat')
    for sign in (-1,1):
        wall=b.box('Hip horn capture wall',(cx+sign*3.6,47.6,-28.5),(1.2,2.6,6))
        lip=b.box('Hip horn retaining lip',(cx+sign*2.9,48.5,-28.5),(1.4,.8,6))
        body=b.join(body,[wall,lip],'Captive stock horn - no exposed screw')
    bridge=b.box('Bowden reaction bridge',(cx,27,-20),(15,3,40.4))
    body=b.join(body,[bridge],'Internal paired tendon reaction bridge')
    for sign in (-1,1):
        socket=b.box('Lower sheath stop',(cx+sign*6,30.2,-20),(3,7,4))
        body=b.join(body,[socket],'Lower Bowden sheath reaction stop')
        body=b.cut(body,[b.cyl('2mm housing socket',(cx+sign*6,28.5,-20),(cx+sign*6,34,-20),1.05),
                         b.cyl('Tendon exit',(cx+sign*6,24,-20),(cx+sign*6,28.6,-20),.4)],'Stepped sheath seating and cord exit')
    # Two sheath paths hug the inside back plate; solid core not printed spline.
    for dx in (-3.0,3.0):
        body=b.cut(body,[b.cyl('Tendon housing guide',(cx+dx,25,2.5),(cx+dx,49,2.5),1.2)],'Paired Bowden guide bore')
    finish(b,body,'Original slim leg '+label)
    horn(b,cx,label)
    return body

def foot(b,source,cx,label):
    body=source.copyToComponent(b.occ)
    body=b.intersect(body,b.box('Original foot only',(cx,0,-20),(110,24,90)),'Separate original foot at Y12')
    for a,c in ((-45.3,-39.8),(-.2,5.3)):
        body=b.cut(body,[b.cyl('Leg bearing sweep relief',(cx,16,a),(cx,16,c),5.35)],'Clear foot below passive leg bearing')
    hub=b.cyl('Concealed foot pivot hub',(cx,16,-39.5),(cx,16,-.5),5.3)
    body=b.join(body,[hub],'Foot pivot inside original U leg')
    drum=b.cyl('Ankle tendon pulley R6',(cx,16,-22),(cx,16,-18),6.5)
    body=b.join(body,[drum],'Integral ankle pulley inside original leg')
    groove=sleeve(b,'Foot tendon groove',(cx,16,-20.6),(cx,16,-19.4),6.7,5.7)
    body=b.cut(body,[groove],'R6 effective cord groove with retaining flanges')
    body=b.cut(body,[b.cyl('Pivot pin passage',(cx,16,-41),(cx,16,1),1.65)],'Unthreaded steel pin passage')
    for dx in (-4.2,4.2):
        body=b.cut(body,[b.cyl('Tendon knot hole',(cx+dx,16,-40),(cx+dx,16,0),.55)],'Ankle tendon anchoring hole')
    if label=='R':body=b.join(body,[b.cyl('Original sole junction reinforcement',(cx,3,-.8),(cx,3,5.8),.8)],'Repair inherited sole edge')
    finish(b,body,'Original foot '+label+' with concealed pulley')
    pin=b.cyl('Plain 3mm steel axle',(cx,16,-44.65),(cx,16,4.65),1.5)
    b.paint(pin,'Plain steel axle',(137,144,151));b.add_hardware(pin,'Plain ankle axle '+label)
    # Press-in end caps cover the plain axle; no threaded fixation.
    for z in (-44.5,4.5):
        cap=b.cyl('Blind axle retaining cap',(cx,16,z-.4),(cx,16,z+.4),2.6)
        a,c=(z-.2,z+.5) if z<0 else (z-.5,z+.2)
        cap=b.cut(cap,[b.cyl('Blind 3mm axle socket',(cx,16,a),(cx,16,c),1.55)],'Axle retention end stop')
        bead=sleeve(b,'TPU snap bead',(cx,16,z-.2),(cx,16,z+.2),2.9,1.55)
        cap=b.join(cap,[bead],'TPU cap retaining bead')
        finish(b,cap,'Axle retaining plug '+label+' '+str(z),(45,48,52))
    return body

def drum(b,x,label):
    # Rotating remote-drive hardware gets its own revolute component.
    body=b.cyl('Remote Bowden drive drum',(x,88,-8.7),(x,88,-5.7),8.5)
    groove=sleeve(b,'Head drum tendon groove',(x,88,-7.8),(x,88,-6.6),8.7,7.7)
    body=b.cut(body,[groove],'R8 effective cord groove and flanges')
    body=b.cut(body,[b.cyl('Original horn hub seat',(x,88,-9),(x,88,-7),3.85),
                     b.cyl('Hidden stock screw passage',(x,88,-10),(x,88,-5),1.1)],'Drum captures supplied horn')
    slot=b.box('Keyed supplied horn arm seat',(x,84.7,-8.4),(5.6,8.6,1.8))
    body=b.cut(body,[slot],'Positive stock horn torque key')
    for dx in (-6,6):body=b.cut(body,[b.cyl('Tendon knot hole',(x+dx,88,-9),(x+dx,88,-5),.55)],'Remote drum cable anchor')
    finish(b,body,'Remote ankle drive drum '+label,(224,225,216))
    # White supplied horn, used instead of trying to print micro splines.
    h=b.cyl('Supplied remote horn hub',(x,88,-10.7),(x,88,-7.2),3.6)
    h=b.join(h,[b.box('Short stock horn blade',(x,84.7,-8.35),(5.0,8.0,1.2))],'Supplied horn blade engages keyed drum')
    h=b.cut(h,[b.cyl('Horn metal spline bore',(x,88,-11),(x,88,-7),2.4)],'Remote horn bore')
    b.paint(h,'Original horn ivory',(224,225,216));b.add_hardware(h,'Stock remote horn '+label)
    screw=b.cyl('Hidden remote horn screw',(x,88,-10),(x,88,-5.5),.8)
    b.paint(screw,'Stock screw steel',(120,124,129));screw.name='VIS | hidden remote horn screw '+label;b.visuals.append(screw)

def path_ref(b,name,points,r,color):
    for i,(a,c) in enumerate(zip(points,points[1:])):
        body=b.cyl(name,a,c,r);b.paint(body,name,color);body.name='VIS | '+name+' '+str(i);b.visuals.append(body)

def transmission(b,cx,x,label):
    # Schematic routed centerlines. Flexible service-loop shape is neutral only.
    for sign in (-1,1):
        points=[(x+sign*8,71.5,-7.5),(x+sign*8,67,-1),
                (cx+sign*3,58,2),(cx+sign*3,48,2.5),
                (cx+sign*3,40,2.5),(cx+sign*6,35,-8),
                (cx+sign*6,33.5,-20)]
        path_ref(b,'Bowden sheath '+label+str(sign),points,1,(73,82,91))
        path_ref(b,'Upper tendon '+label+str(sign),[(x+sign*8,88,-7.5),(x+sign*8,78.5,-7.5)],.3,(199,181,113))
        path_ref(b,'Lower tendon '+label+str(sign),[(cx+sign*6,26,-20),(cx+sign*6,16,-20)],.3,(199,181,113))

def interference(design,groups):
    bodies=[v.createForAssemblyContext(b.occ) for b in groups for v in b.parts+b.hardware]
    query=design.createInterferenceInput(objs(bodies));query.areCoincidentFacesIncluded=False
    clashes=[]
    for result in design.analyzeInterference(query):
        if not result.interferenceBody or result.interferenceBody.volume<.00002:continue
        a,c=result.entityOne.name,result.entityTwo.name
        # Stock horns intentionally seat in their matching output bosses.
        if 'MG90S' in a and 'Stock hip horn' in c or 'MG90S' in c and 'Stock hip horn' in a:continue
        clashes.append({'a':a,'b':c,'volume_mm3':round(result.interferenceBody.volume*1000,5)})
    return clashes

def poses():
    limits=(15,15,12,12)
    yield (0,0,0,0)
    for i in range(4):
        for frac in (-1,-.75,-.5,-.25,.25,.5,.75,1):yield tuple(limits[j]*frac if i==j else 0 for j in range(4))
    for signs in itertools.product((-1,1),repeat=4):yield tuple(a*b for a,b in zip(signs,limits))

def setpose(joints,angles):
    for j,a in zip(joints[:4],angles):j.jointMotion.rotationValue=math.radians(a)
    for j,a in zip(joints[4:],angles[2:]):j.jointMotion.rotationValue=math.radians(a*.75)
    adsk.doEvents()

def camera(app,eye,target=(-35,54,-20)):
    cam=app.activeViewport.camera;cam.cameraType=C.CameraTypes.OrthographicCameraType
    cam.eye=pt(*eye);cam.target=pt(*target);cam.upVector=vector((0,1,0));cam.isFitView=True;cam.isSmoothTransition=False
    app.activeViewport.camera=cam;app.activeViewport.refresh()

def export(app,design,groups,joints,report):
    manager=design.exportManager
    for j in joints:j.isLightBulbOn=False
    for b in groups:
        b.comp.isOriginFolderLightBulbOn=False
        for s in b.comp.sketches:s.isLightBulbOn=False
    camera(app,(-200,170,-300))
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-HeadDrive-exterior.png'),1600,1600)
    saved=[(v,v.isLightBulbOn) for q in groups for v in q.parts+q.hardware+q.visuals]
    for body in groups[0].parts:
        if body.name.startswith('PRINT | Original head') or 'Rear lid' in body.name or 'snap rack' in body.name:body.isLightBulbOn=False
    camera(app,(-200,170,-260),(-35,66,-20))
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-HeadDrive-interior.png'),1600,1600)
    for q in groups:
        for body in q.parts+q.hardware+q.visuals:
            body.isLightBulbOn=q is groups[0] and 'MG90S' in body.name
    camera(app,(-150,155,-220),(-35,76,-23))
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'MG90S-detail.png'),1600,1600)
    for body,visible in saved:body.isLightBulbOn=visible
    camera(app,(-200,170,-300));setpose(joints,(0,0,0,0))
    assert manager.execute(manager.createFusionArchiveExportOptions(os.path.join(OUT,'Emo-HeadDrive.f3d')))
    for b in groups:
        for body in b.parts:
            name=body.name.replace('PRINT | ','').replace(' ','_')+'.stl'
            data=manager.createSTLExportOptions(body,os.path.join(OUT,name));data.meshRefinement=F.MeshRefinementSettings.MeshRefinementHigh;data.unitType=F.DistanceUnits.MillimeterDistanceUnits
            assert manager.execute(data),name
    with open(os.path.join(OUT,'mechanical-validation.json'),'w') as f:json.dump(report,f,indent=2)

def run(context):
    os.makedirs(OUT,exist_ok=True)
    with open(LOG,'w') as f:f.write('EMO HEAD DRIVE\n')
    app=C.Application.get()
    try:
        doc=app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(BACKUP));doc.name='Emo original - 4 MG90S in head - clips'
        design=F.Design.cast(app.activeProduct);design.designIntent=F.DesignIntentTypes.HybridDesignIntentType
        root=design.rootComponent;source=tuple(root.bRepBodies)
        head=new_group(design,'01 Original head - all 4 detailed MG90S')
        log('Shell');front,lid=shell(head,source[2])
        log('Detailed MG90S');servos=servo_layout(head)
        log('Snap rack');rack=cage(head,servos)
        # Constrain rack inside head by paired keyed recesses.
        log('OLED');carrier=oled(head)
        # Internal rails connect OLED tray to head and key the servo rack.
        for x in (-53, -17):
            rail=head.box('OLED slide rail',(x,78,-42.5),(2,32,6))
            front=head.join(front,[rail],'Internal OLED rail')
            lip=head.box('OLED carrier captive back clip',(x+1.1 if x<-35 else x-1.1,78,-39.25),(2.6,26,.7))
            front=head.join(front,[lip],'Hidden carrier retaining clip')
        # Keyed rack receiver removes only local internal overlap, with clearance.
        front=head.cut(front,[head.temp_body(head.temp.copy(rack),'Exact keyed rack receiver')],'Clear exact rack footprint')
        tool=head.temp.copy(rack)
        mat=C.Matrix3D.create();scale=1.006
        for i in range(3):mat.setCell(i,i,scale)
        mat.translation=vector(tuple((1-scale)*v/10 for v in (-35,74,-26)))
        assert head.temp.transform(tool,mat)
        front=head.cut(front,[head.temp_body(tool,'Rack receiver clearance tool')],'Keyed internal rack receiver')
        # Update body reference after joins.
        head.parts[0]=front;front.name='PRINT | Original head - no exterior screws'
        groups=[head];legs=[];feet=[]
        for original,cx,label in zip(source[:2],HIP_X,('L','R')):
            lb=new_group(design,'Leg '+label+' - original outline');log('Leg '+label);leg(lb,original,cx,label)
            fb=new_group(design,'Foot '+label+' - passive remote ankle');log('Foot '+label);foot(fb,original,cx,label)
            legs.append(lb);feet.append(fb);groups.extend((lb,fb))
        drives=[]
        for cx,x,label in zip(HIP_X,(-49.3,-20.7),('L','R')):
            rb=new_group(design,'MG90S remote output '+label);drum(rb,x,label);drives.append(rb);groups.append(rb)
            transmission(head,cx,x,label)
        for v in source:v.isLightBulbOn=False
        for s in root.sketches:s.isLightBulbOn=False
        joints=[]
        for lb,cx,label in zip(legs,HIP_X,('L','R')):joints.append(revolute(root,head,lb,'HIP '+label+' yaw 15deg',(cx,48,-20),(0,1,0),15))
        for lb,fb,cx,label in zip(legs,feet,HIP_X,('L','R')):joints.append(revolute(root,lb,fb,'ANKLE '+label+' remote roll 12deg',(cx,16,-20),(0,0,1),12))
        for rb,x,label in zip(drives,(-49.3,-20.7),('L','R')):joints.append(revolute(root,head,rb,'REMOTE servo '+label+' pulley R8',(x,88,-7),(0,0,1),9))
        for ankle,remote,label in zip(joints[2:4],joints[4:],('L','R')):
            data=root.motionLinks.createInput(ankle,remote)
            data.motionOne=F.JointMotionTypes.RevoluteJointRotateMotionType
            data.motionTwo=F.JointMotionTypes.RevoluteJointRotateMotionType
            data.valueOne=C.ValueInput.createByString('12 deg')
            data.valueTwo=C.ValueInput.createByString('9 deg')
            data.isReversed=False
            link=root.motionLinks.add(data);link.name='Bowden '+label+' - R8 to R6 ideal ratio'
        log('Neutral audit');neutral=interference(design,groups);log(json.dumps(neutral))
        report={'architecture':'4 head-mounted detailed MG90S, paired Bowden ankle transmission','head_lift_mm':0,'enclosure_screws':0,'hidden_stock_horn_screws':4,'joints':len(joints),'motion_links':root.motionLinks.count,'neutral_collisions':neutral,'poses':[],'notes':['Bowden paths are neutral schematic visuals, not deformable collision geometry.','Two persistent motion links implement ideal 0.75 servo/ankle ratio; no elastic cable solver.','Nominal servo reconstruction, measure purchased hardware before manufacture.']}
        if not neutral:
            log('Motion samples')
            for angles in poses():
                setpose(joints,angles);clashes=interference(design,groups)
                report['poses'].append({'degrees':angles,'collisions':clashes})
            setpose(joints,(0,0,0,0))
        report['feature_errors']=[q.entity.name for q in design.timeline if hasattr(q.entity,'healthState') and q.entity.healthState==F.FeatureHealthStates.ErrorFeatureHealthState]
        report['parts']=[{'name':v.name,'volume_mm3':v.volume*1000,'solid':v.isSolid} for b in groups for v in b.parts]
        with open(os.path.join(OUT,'mechanical-validation.json'),'w') as f:json.dump(report,f,indent=2)
        assert not report['neutral_collisions'] and len(report['poses'])==49 and not any(p['collisions'] for p in report['poses']), 'Motion collision detected; see validation report'
        assert not report['feature_errors'],report['feature_errors']
        log('Export');export(app,design,groups,joints,report)
        log('SUCCESS '+str(sum(bool(p['collisions']) for p in report['poses'])))
    except Exception:
        log(traceback.format_exc());app.userInterface.messageBox(traceback.format_exc())
