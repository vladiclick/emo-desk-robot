"""Four direct-drive MG90S, two in head and one in each leg.
Mechanical prototype: horn fit and snap fatigue need physical tests.
"""
import adsk.core as C
import adsk.fusion as F
import adsk
import os, json, math, traceback, itertools
from .base import Build,new_group,pt,vi,objs,vector,revolute
from .servo_detail import make_servo
HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(HERE,'..','..','outputs','Emo-DirectDrive'))
BACKUP=os.path.abspath(os.path.join(HERE,'..','..','outputs','Emo-4servo','Original-user-backup.f3d'))
_packaged=os.path.abspath(os.path.join(HERE,'..','..'))
if os.path.basename(_packaged)=='Emo-DirectDrive':
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
    for cx in HIP_X:
        h=b.cut(h,[b.box('Hip electrical lead relief',(cx,75.6,-41.7),(4,3,5))],'Hip cable exit clearance')
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
    for x in (-55,-15):
        stop=b.cyl('Rear lid rack retaining post',(x,65,-9.7),(x,65,5.2),3)
        lid=b.join(lid,[stop],'Lid traps hip rack against keyed front seats')
        front=b.cut(front,[b.cyl('Rack post passage',(x,65,3.5),(x,65,5.4),3.35)],'Rear lid rack post clearance')
    finish(b,front,'Original head - no exterior screws')
    finish(b,lid,'Rear lid - four release clips')
    b.occ.isGrounded=True
    return front,lid

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
    arm=b.box('Stock hip horn arm',(cx,47.1,-14),(5.5,1.5,13))
    hub=b.cyl('Hip horn hub',(cx,46.4,-20),(cx,50.9,-20),3.6)
    arm=b.join(arm,[hub],'Supplied MG90S hip horn')
    arm=b.cut(arm,[b.cyl('Spline and screw bore',(cx,45.5,-20),(cx,51.5,-20),2.4)],'Hip horn bore')
    b.paint(arm,'Stock horn ivory',(225,226,216));b.add_hardware(arm,'Stock hip horn '+label)
    screw=b.cyl('Hidden stock hip horn screw',(cx,45.8,-20),(cx,49.9,-20),.8)
    b.paint(screw,'Stock horn steel',(120,124,129));screw.name='VIS | hidden hip horn screw '+label;b.visuals.append(screw)

def hip_rack(b):
    frame=b.box('Hip rack rear spine',(-35,65,-11),(70,27,2))
    frame=b.join(frame,[b.box('Lower rack shelf',(-35,51,-26),(68,2,29))],'Hip rack base')
    for x in (-68.5,-1.5):frame=b.join(frame,[b.box('Hip rack guide',(x,65,-26),(2,27,29))],'Hip rack side guide')
    frame=b.join(frame,[b.box('Hip rack upper crossbar',(-35,79,-26),(68,2,27))],'Hip rack upper bridge')
    for cx in HIP_X:
        frame=b.join(frame,[b.box('Hip ear saddle',(cx,57.1,-25.7),(16,2,34))],'Hip ear support')
        frame=b.cut(frame,[b.box('Hip case clearance',(cx,66.1,-25.7),(13.1,24,23.5)),
                           b.box('Hip tab clearance',(cx,59.2,-25.7),(13.1,2.7,33.2)),
                           b.cyl('Output boss passage',(cx,48,-20),(cx,56,-20),6),
                           b.cyl('Second gear hump',(cx,52,-30.2),(cx,55,-30.2),5)],'Two hip pockets')
        for sign in (-1,1):
            frame=b.cut(frame,[b.box('Snap flexure clearance',(cx+sign*7.2,57.4,-40.4),(2,10.8,4))],'Free snap tongue')
            beam=b.box('Hip tab snap tongue',(cx+sign*7.2,56.5,-40.4),(.8,13,3))
            hook=b.box('Hip tab retaining hook',(cx+sign*6.35,60.8,-40.4),(2.1,1,3))
            frame=b.join(frame,[beam,hook],'Hip snap retention')
    for cx in HIP_X:
        frame=b.cut(frame,[b.cyl('Hip rotor flange clearance',(cx,49.8,-20),(cx,51.6,-20),9.2)],'Clear captive hip rotor above bearing')
        ring=sleeve(b,'Hip C thrust bearing',(cx,48.3,-20),(cx,49.7,-20),10.5,5.6)
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

def leg(b,source,cx,label):
    body=source.copyToComponent(b.occ)
    body=b.intersect(body,b.box('Original upper leg',(cx,60,-20),(30,91,60)),'Original leg outline')
    core=b.box('Enclosed direct servo leg',(cx,27.1,-20),(15,32.2,40.4))
    body=b.join(body,[core],'Enclose servo within original 15mm leg width')
    # Front plate is the only servo access cover, retaining original profile.
    inp=b.comp.features.splitBodyFeatures.createInput(body,b.plane('z',-40.2),True)
    split=b.comp.features.splitBodyFeatures.add(inp);split.name='Removable original leg front plate'
    assert split.bodies.count==2
    cover=min(tuple(split.bodies),key=lambda q:q.physicalProperties.centerOfMass.z)
    body=max(tuple(split.bodies),key=lambda q:q.physicalProperties.centerOfMass.z)
    # MG90S inserted from front. Upper/lower ears seat on rear shoulders.
    cuts=[b.box('Servo main clearance',(cx,28.8,-18.1),(13.1,23.5,24.0)),
          b.box('Servo insertion and ear channel',(cx,28.8,-34.5),(13.1,33.2,21.3)),
          b.cyl('Shaft and main gear clearance',(cx,23.1,-36),(cx,23.1,-28.5),5.8),
          b.cyl('Second gearbox hump clearance',(cx,33.3,-32),(cx,33.3,-28.5),5.05),
          b.cyl('Front foot horn sweep',(cx,23.1,-39.6),(cx,23.1,-33.4),16),
          b.cyl('Rear foot bearing sweep',(cx,23.1,-4.3),(cx,23.1,-.2),16),
          b.cyl('Rear stub pivot bore',(cx,23.1,-1),(cx,23.1,5.5),1.65),
          b.cyl('Rear pivot end cap seat',(cx,23.1,3.75),(cx,23.1,5.1),2.8),
          b.cyl('Rear cap snap bead groove',(cx,23.1,4.05),(cx,23.1,4.75),3.0),
          b.box('Ankle cable rise',(cx,42,-8.6),(4,7,3)),
          b.box('Ankle cable lateral turn',(cx+2.5,44.3,-8.6),(7,2,3)),
          b.box('Cable bypass beside hip horn',(cx+5,47.5,-8.6),(3,9,3))]
    body=b.cut(body,cuts,'Direct ankle servo cavity and passive rear pivot')
    stem=sleeve(b,'Hip axial bearing journal',(cx,47.8,-20),(cx,51.4,-20),5.4,4.05)
    flange=sleeve(b,'Hip captured thrust flange',(cx,50.0,-20),(cx,51.4,-20),8.8,4.05)
    body=b.join(body,[stem,flange],'Integral captured hip rotor')
    body=hip_capture(b,body,cx)
    # Cover side cheeks seal the fork area while preserving original width.
    for sign in (-1,1):
        cheek=b.box('Cover side cheek',(cx+sign*7.0,27.4,-37.4),(1.0,29.2,6.0))
        cover=b.join(cover,[cheek],'Front cover side skirt')
        # Deep keys hook into the solid lower shelf; top clip locks the cover.
        for y,height in ((13.2,2.0),(43.3,2.5)):
            finger=b.box('Servo ear compression finger',(cx+sign*6.05,y,-33.8),(1.3,height,15.2))
            cover=b.join(cover,[finger],'Positive front cover retention of servo tabs')
        key=b.box('Lower cover locating key',(cx+sign*6.05,11.9,-30.8),(1.3,1.4,1.0))
        cover=b.join(cover,[key],'Lower hooks engage leg floor pocket')
    for dx in (-4.8,4.8):
        stop=b.cyl('Front foot axial thrust stop',(cx+dx,23.1,-40.5),(cx+dx,23.1,-37.7),.85)
        cover=b.join(cover,[stop],'Front cover captures keyed foot without forced horn snaps')
    beam=b.box('Upper front lid snap beam',(cx,45.9,-35.2),(4,.8,10.4))
    hook=b.box('Upper front lid snap hook',(cx,46.45,-31.5),(4,1.2,1.0))
    cover=b.join(cover,[beam,hook],'Single top release clip for servo access')
    body=b.cut(body,[b.box('Snap beam flexure space',(cx,45.85,-35.2),(4.6,1.4,10.8)),
                     b.box('Top latch receiver',(cx,46.45,-31.5),(4.6,1.8,1.6))],'Top cover latch receiver')
    # Clear cover geometry from the leg, preserving receiving shoulders.
    tool=b.temp_body(b.temp.copy(cover),'Front cover exact receiver')
    data=b.comp.features.combineFeatures.createInput(body,objs([tool]));data.operation=F.FeatureOperations.CutFeatureOperation
    cut=b.comp.features.combineFeatures.add(data);cut.name='Keyed front cover fit'
    outputs=tuple(cut.bodies);body=max(outputs,key=lambda v:v.volume)
    for offcut in outputs:
        if offcut!=body:
            log('Cover offcut '+json.dumps({'volume_mm3':offcut.volume*1000,'bbox':[[v*10 for v in offcut.boundingBox.minPoint.asArray()],[v*10 for v in offcut.boundingBox.maxPoint.asArray()]]}))
            assert offcut.volume<body.volume*.03,'Unexpected structural offcut'
            b.comp.features.removeFeatures.add(offcut)
    # Allow paint/printing clearance along the longitudinal side skirts.
    for sign in (-1,1):
        body=b.cut(body,[b.box('Skirt side clearance',(cx+sign*7,27.4,-37.3),(1.35,29.8,6.3))],'Front cover skirt clearance')
    finish(b,body,'Leg '+label+' - enclosed direct MG90S')
    finish(b,cover,'Leg '+label+' - clip front cover',(49,52,57))
    make_servo(b,(cx,28.8,-6.5),(0,1,0),(1,0,0),(0,0,-1),'ANKLE '+label)
    horn(b,cx,label)
    return body

def ankle_horn(b,cx,label):
    hub=b.cyl('Stock ankle horn hub',(cx,23.1,-36.3),(cx,23.1,-32.9),3.6)
    blade=b.box('Short stock horn arm',(cx,19.3,-35.95),(5,8,1.4))
    h=b.join(hub,[blade],'Original MG90S horn - direct foot drive')
    h=b.cut(h,[b.cyl('Original spline and screw bore',(cx,23.1,-36.7),(cx,23.1,-32.6),2.4)],'Stock horn spline socket')
    b.paint(h,'Stock nylon horn ivory',(224,226,217));b.add_hardware(h,'Stock ankle horn '+label)
    screw=b.cyl('Hidden ankle horn screw',(cx,23.1,-36.4),(cx,23.1,-33.0),.8)
    b.paint(screw,'Stock horn screw metal',(125,130,136));screw.name='VIS | Hidden ankle horn screw '+label;b.visuals.append(screw)

def foot(b,source,cx,label):
    body=source.copyToComponent(b.occ)
    body=b.intersect(body,b.box('Original sole',(cx,0,-20),(110,24,90)),'Preserve original foot outer outline')
    body=b.cut(body,[b.box('Concealed leg roll recess',(cx,11,-20.5),(21,6.4,43))],'Internal sole relief for direct motor and roll')
    for z,name in ((-35.65,'Driven front'),(-2.2,'Passive rear')):
        stem=b.box(name+' narrow foot stem',(cx,10.3,z),(4.5,8.6,3.5))
        neck=b.box(name+' foot bearing neck',(cx,19.5,z),(8.4,10,3.5))
        crown=b.cyl(name+' pivot crown',(cx,23.1,z-1.75),(cx,23.1,z+1.75),5.7)
        body=b.join(body,[stem,neck,crown],name+' compact foot fork')
    # Supplied short horn is positively keyed; axial lips capture it.
    body=b.cut(body,[b.box('Ankle horn blade recess',(cx,19.3,-36.9),(5.6,8.6,4.2)),
                     b.cyl('Ankle horn hub pocket',(cx,23.1,-38.2),(cx,23.1,-33.5),3.9)],'Direct drive keyed horn socket')
    body=b.cut(body,[b.cyl('Rear 3mm stub pin bore',(cx,23.1,-3.25),(cx,23.1,.2),1.65)],'Passive rear bearing bore')
    if label=='R':body=b.join(body,[b.cyl('Inherited sole edge repair',(cx,3,-.8),(cx,3,5.8),.8)],'Reinforce inherited right sole contact')
    finish(b,body,'Foot '+label+' - direct keyed drive')
    ankle_horn(b,cx,label)
    pin=b.cyl('Short opposing steel pivot',(cx,23.1,-3.15),(cx,23.1,4.65),1.5)
    b.paint(pin,'Ankle steel pivot',(128,134,141));b.add_hardware(pin,'Short passive axle '+label)
    cap=b.cyl('Rear hidden axle cap',(cx,23.1,4.1),(cx,23.1,4.9),2.6)
    cap=b.cut(cap,[b.cyl('Blind axle socket',(cx,23.1,4),(cx,23.1,4.7),1.55)],'Axle cap end stop')
    bead=sleeve(b,'TPU cap bead',(cx,23.1,4.3),(cx,23.1,4.7),2.9,1.55)
    cap=b.join(cap,[bead],'Snap retaining bead')
    finish(b,cap,'Foot '+label+' - TPU rear axle cap')

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
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-DirectDrive-exterior.png'),1600,1600)
    saved=[(v,v.isLightBulbOn) for g in groups for v in g.parts+g.hardware+g.visuals]
    for g in groups:
        for v in g.parts:
            if g is groups[0] and ('Original head' in v.name or 'Rear lid' in v.name or 'servo clip rack' in v.name) or 'clip front cover' in v.name:v.isLightBulbOn=False
    camera(app,(-200,150,-260),(-35,58,-20))
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-DirectDrive-cutaway.png'),1600,1600)
    # A close-up of the exact coaxial shaft/foot connection.
    for g in (groups[0],groups[3],groups[4]):
        for body in g.parts+g.hardware+g.visuals:body.isLightBulbOn=False
    for body in groups[1].hardware+groups[1].visuals:
        if 'hip' in body.name.lower():body.isLightBulbOn=False
    camera(app,(-160,95,-240),(-62.5,24,-20))
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-DirectDrive-mechanism.png'),1600,1600)
    for v,on in saved:v.isLightBulbOn=on
    setpose(joints,(10,-10,9,-9));camera(app,(-200,170,-300))
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-DirectDrive-motion.png'),1600,1600)
    setpose(joints,(0,0,0,0));camera(app,(-200,170,-300))
    assert manager.execute(manager.createFusionArchiveExportOptions(os.path.join(OUT,'Emo-DirectDrive.f3d')))
    for g in groups:
        for body in g.parts:
            path=os.path.join(OUT,body.name.replace('PRINT | ','').replace(' ','_')+'.stl')
            opt=manager.createSTLExportOptions(body,path);opt.meshRefinement=F.MeshRefinementSettings.MeshRefinementHigh;opt.unitType=F.DistanceUnits.MillimeterDistanceUnits
            assert manager.execute(opt)

def run(context):
    os.makedirs(OUT,exist_ok=True)
    with open(LOG,'w') as f:f.write('EMO DIRECT DRIVE\n')
    app=C.Application.get()
    try:
        doc=app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(BACKUP))
        doc.name='Emo original - four MG90S direct drive - working'
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
        groups=[head];legs=[];feet=[]
        for original,cx,label in zip(source[:2],HIP_X,('L','R')):
            lb=new_group(design,'Leg '+label+' - direct MG90S assembly');log('Leg '+label);leg(lb,original,cx,label)
            fb=new_group(design,'Foot '+label+' - coaxial direct joint');log('Foot '+label);foot(fb,original,cx,label)
            groups.extend((lb,fb));legs.append(lb);feet.append(fb)
        for v in source:v.isLightBulbOn=False
        for s in root.sketches:s.isLightBulbOn=False
        joints=[]
        for lb,cx,label in zip(legs,HIP_X,('L','R')):joints.append(revolute(root,head,lb,'HIP '+label+' direct yaw 15deg',(cx,48,-20),(0,1,0),15))
        for lb,fb,cx,label in zip(legs,feet,HIP_X,('L','R')):joints.append(revolute(root,lb,fb,'ANKLE '+label+' direct roll 12deg',(cx,23.1,-35),(0,0,1),12))
        log('Neutral audit');neutral=collisions(design,groups);log(json.dumps(neutral))
        report={'architecture':'4 direct MG90S: 2 hip motors in original head, 1 ankle motor per leg, coaxial foot horns','head_lift_mm':0,'outer_leg_width_mm':15,'bowden_tendons':0,'joints':4,'motion_links':0,'hidden_horn_screws':4,'neutral_collisions':neutral,'poses':[]}
        if not neutral:
            log('Motion sweep')
            for angles in poses():
                setpose(joints,angles)
                for lb,fb,cx in zip(legs,feet,HIP_X):
                    a=pt(cx,23.1,-35);a.transformBy(lb.occ.transform2)
                    c=pt(cx,23.1,-35);c.transformBy(fb.occ.transform2)
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
        log('Export');export(app,design,groups,joints);log('SUCCESS')
    except Exception:
        log(traceback.format_exc());app.activeDocument.activate()
