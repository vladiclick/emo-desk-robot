"""Integrate mechanisms in a new imported copy of the user's archived design.
All dimensions mm; Y is up, face is toward negative Z. Original is untouched.
"""
import adsk.core as C
import adsk.fusion as F
import adsk
import os,json,math,traceback,itertools
from .config import HIP_X,HIP_Y,HIP_Z,HEAD_LIFT,ANKLE_Y,ANKLE_Z,OLED_PCB,HIP_LIMIT_DEG,ANKLE_LIMIT_DEG,motion_samples,validate

HERE=os.path.dirname(os.path.abspath(__file__))
_default_out=os.path.abspath(os.path.join(HERE,'..','..','outputs','Emo-4servo'))
_packaged_out=os.path.abspath(os.path.join(HERE,'..','..'))
OUT=_packaged_out if os.path.exists(os.path.join(_packaged_out,'Original-user-backup.f3d')) else _default_out
LOG=os.path.join(HERE,'build-log.txt')

def log(s):
    with open(LOG,'a') as f:f.write(str(s)+'\n')

def pt(x,y,z):return C.Point3D.create(x/10,y/10,z/10)
def vi(v):return C.ValueInput.createByReal(v/10)
def objs(seq):
    result=C.ObjectCollection.create()
    for item in seq:result.add(item)
    return result

def vector(v):return C.Vector3D.create(*v)

class Build:
    def __init__(self,design,occ):
        self.design=design
        self.occ=occ
        self.comp=occ.component
        self.temp=F.TemporaryBRepManager.get()
        self.parts=[]
        self.hardware=[]
        self.visuals=[]

    def temp_body(self,body,name):
        feature=self.comp.features.baseFeatures.add()
        feature.name=name
        feature.startEdit()
        self.comp.bRepBodies.add(body,feature)
        feature.finishEdit()
        result=feature.bodies.item(0)
        result.name=name
        return result

    def box(self,name,center,size):
        bb=C.OrientedBoundingBox3D.create(pt(*center),vector((1,0,0)),vector((0,1,0)),*[v/10 for v in size])
        return self.temp_body(self.temp.createBox(bb),name)

    def cyl(self,name,a,b,r):
        return self.temp_body(self.temp.createCylinderOrCone(pt(*a),r/10,pt(*b),r/10),name)

    def boolean(self,target,tools,operation,name):
        data=self.comp.features.combineFeatures.createInput(target,objs(tools))
        data.operation=operation
        data.isKeepToolBodies=False
        feature=self.comp.features.combineFeatures.add(data)
        feature.name=name
        assert feature.bodies.count==1,(name,feature.bodies.count)
        return feature.bodies.item(0)

    def cut(self,target,tools,name):return self.boolean(target,tools,F.FeatureOperations.CutFeatureOperation,name)
    def join(self,target,tools,name):return self.boolean(target,tools,F.FeatureOperations.JoinFeatureOperation,name)
    def intersect(self,target,tool,name):return self.boolean(target,[tool],F.FeatureOperations.IntersectFeatureOperation,name)

    def plane(self,axis,value):
        base={'x':self.comp.yZConstructionPlane,'y':self.comp.xZConstructionPlane,'z':self.comp.xYConstructionPlane}[axis]
        data=self.comp.constructionPlanes.createInput()
        data.setByOffset(base,vi(-value if axis=='y' else value))
        plane=self.comp.constructionPlanes.add(data)
        plane.isLightBulbOn=False
        return plane

    def translate(self,body,dy):
        matrix=C.Matrix3D.create()
        matrix.translation=vector((0,dy/10,0))
        data=self.comp.features.moveFeatures.createInput2(objs([body]))
        data.defineAsFreeMove(matrix)
        feature=self.comp.features.moveFeatures.add(data)
        feature.name='Raise head for hip mechanism clearance'
        return feature.bodies.item(0)

    def rounded_xy(self,name,cx,cy,z,w,h,r,depth):
        sketch=self.comp.sketches.add(self.plane('z',z))
        sketch.name=name+' profile'
        a,b=w/2,h/2
        points=((-a+r,-b),(a-r,-b),(a,-b+r),(a,b-r),(a-r,b),(-a+r,b),(-a,b-r),(-a,-b+r))
        mid=((a-r+r/math.sqrt(2),-b+r-r/math.sqrt(2)),(a-r+r/math.sqrt(2),b-r+r/math.sqrt(2)),(-a+r-r/math.sqrt(2),b-r+r/math.sqrt(2)),(-a+r-r/math.sqrt(2),-b+r-r/math.sqrt(2)))
        local=lambda p:pt(cx+p[0],cy+p[1],0)
        for i in range(0,8,2):
            sketch.sketchCurves.sketchLines.addByTwoPoints(local(points[i]),local(points[i+1]))
            sketch.sketchCurves.sketchArcs.addByThreePoints(local(points[i+1]),local(mid[i//2]),local(points[(i+2)%8]))
        data=self.comp.features.extrudeFeatures.createInput(sketch.profiles.item(0),F.FeatureOperations.NewBodyFeatureOperation)
        data.setSymmetricExtent(vi(depth),True)
        feature=self.comp.features.extrudeFeatures.add(data)
        feature.name=name
        sketch.isLightBulbOn=False
        return feature.bodies.item(0)

    def paint(self,body,name,rgb):
        appearance=next((a for a in self.design.appearances if a.name==name),None)
        if not appearance:
            candidates=('Plastic - Matte (White)','ABS (White)','Plastic - Glossy (White)')
            base=None
            for library in C.Application.get().materialLibraries:
                base=next((a for a in library.appearances if a.name in candidates),None)
                if base:break
            if base:
                appearance=self.design.appearances.addByCopy(base,name)
                prop=C.ColorProperty.cast(appearance.appearanceProperties.itemById('opaque_albedo'))
                prop.value=C.Color.create(*rgb,255)
        if appearance:body.appearance=appearance

    def add_part(self,body,name):
        body.name='PRINT | '+name
        self.parts.append(body)
        return body

    def add_hardware(self,body,name):
        body.name='REF | '+name
        self.hardware.append(body)
        return body


def new_group(design,name):
    occ=design.rootComponent.occurrences.addNewComponent(C.Matrix3D.create())
    occ.component.name=name
    return Build(design,occ)


def hip_servo(b,cx,label):
    case=b.box('Hip servo case',(cx,66.1,-25.7),(12.4,23.2,22.8))
    flange=b.box('Hip servo mounting ears',(cx,56.5,-25.7),(12.4,2,32.5))
    case=b.join(case,[flange],'MG90S case with mounting ears')
    gear=b.cyl('Hip output boss',(cx,51.5,-20),(cx,54.5,-20),3.6)
    shaft=b.cyl('Hip spline envelope',(cx,49.2,-20),(cx,51.5,-20),2.35)
    case=b.join(case,[gear,shaft],'MG90S hip complete reference')
    for z in (-39.7,-11.7):
        case=b.cut(case,[b.cyl('Servo ear clearance',(cx,55,-0+z),(cx,58,z),1.1)],'Servo tab hole')
    b.paint(case,'MG90S graphite',(45,48,56))
    b.add_hardware(case,'MG90S hip '+label)


def torso(b,source):
    head=source.copyToComponent(b.occ)
    head=b.translate(head,HEAD_LIFT)
    envelope=b.temp.copy(head)
    cavity=b.rounded_xy('Electronics cavity',-35,83.5,-17.65,72,57,11,43.7)
    head=b.cut(head,[cavity],'Hollow user head, preserve outer silhouette')
    for cx in HIP_X:
        for z in (-39.7,-11.7):
            boss=b.cyl('Hip screw support',(cx,52,z),(cx,55.5,z),3.5)
            trim=b.temp_body(b.temp.copy(envelope),'Original head envelope trim')
            boss=b.intersect(boss,trim,'Trim support within user silhouette')
            head=b.join(head,[boss],'Hip mounting pedestal')
        case=b.box('Hip servo case clearance',(cx,66.1,-25.7),(13.1,24,23.5))
        ears=b.box('Hip servo ear clearance',(cx,56.675,-25.7),(13.1,2.35,33.2))
        output=b.cyl('Hip shaft passage',(cx,48,-20),(cx,56,-20),4.1)
        head=b.cut(head,[case,ears,output],'MG90S hip pocket and horn exit')
        for z in (-39.7,-11.7):
            head=b.cut(head,[b.cyl('Hip M2 pilot',(cx,51,z),(cx,55.7,z),.8)],'Hip servo fastening pilots')
    panel=b.rounded_xy('OLED carrier clearance',-35,90,-44.0,38.6,34.6,3.3,9)
    head=b.cut(head,[panel],'Removable OLED bay behind existing face')
    for x in (-58,-12):
        for y in (76,104):
            head=b.cut(head,[b.cyl('OLED M2 pilot',(x,y,-50),(x,y,-41.5),.8)],'OLED front mounting pilot')
    for x in (-50.5,-19.5):
        cable=b.box('Ankle wiring passage',(x,53,-36),(5,8,5))
        head=b.cut(head,[cable],'Ankle cable entry into torso')
    split=b.comp.features.splitBodyFeatures.createInput(head,b.plane('z',2),True)
    feature=b.comp.features.splitBodyFeatures.add(split)
    feature.name='Removable rear service lid'
    halves=tuple(feature.bodies)
    front=min(halves,key=lambda v:v.physicalProperties.centerOfMass.z)
    rear=max(halves,key=lambda v:v.physicalProperties.centerOfMass.z)
    for x in (-68,-2):
        for y in (66,101):
            boss=b.cyl('Rear lid screw boss',(x,y,-3),(x,y,1.6),3.4)
            front=b.join(front,[boss],'Rear lid internal screw support')
            front=b.cut(front,[b.cyl('Rear lid pilot',(x,y,-4),(x,y,2),.8)],'Rear lid M2 pilot')
            rear=b.cut(rear,[b.cyl('Rear lid clearance',(x,y,1),(x,y,10),1.1)],'Rear lid M2 clearance')
    b.add_part(front,'User head - hollow torso')
    b.add_part(rear,'User head - rear service lid')
    for cx,label in zip(HIP_X,('L','R')):hip_servo(b,cx,label)
    oled(b)
    b.occ.isGrounded=True


def oled(b):
    bezel=b.rounded_xy('OLED face flange',-35,90,-49,54,34,4,2)
    stem=b.rounded_xy('OLED carrier walls',-35,90,-44,38,34,3,8)
    bezel=b.join(bezel,[stem],'OLED front flange and rear carrier')
    inner=b.rounded_xy('OLED PCB drop in bay',-35,90,-43.9,30.4,28.4,1,8.2)
    aperture=b.rounded_xy('OLED viewing window',-35,90,-49,22.8,12.2,1,6)
    bezel=b.cut(bezel,[inner,aperture],'PCB clearance and active display aperture')
    for x in (-58,-12):
        for y in (76,104):
            bezel=b.cut(bezel,[b.cyl('OLED front screw clearance',(x,y,-52),(x,y,-47),1.1)],'OLED flange screw holes')
    for x in (-52.2,-17.8):
        for y in (78,102):
            bezel=b.cut(bezel,[b.cyl('Carrier clamp pilot',(x,y,-47.5),(x,y,-39),.8)],'OLED retaining clamp pilot')
    clamp=b.rounded_xy('OLED removable rear clamp',-35,90,-39,38,34,3,2)
    hole=b.rounded_xy('Clamp open centre',-35,90,-39,26,24,1,5)
    clamp=b.cut(clamp,[hole],'Open PCB back for wiring')
    for x in (-49.2,-20.8):
        pad=b.box('PCB axial retaining pad',(x,90,-40.75),(1.8,20,1.5))
        clamp=b.join(clamp,[pad],'OLED rear edge bearing pad')
    for x in (-52.2,-17.8):
        for y in (78,102):
            clamp=b.cut(clamp,[b.cyl('Clamp screw clearance',(x,y,-42),(x,y,-36),1.1)],'Rear OLED clamp screw holes')
    b.paint(bezel,'OLED face charcoal',(28,33,39))
    b.paint(clamp,'OLED carrier graphite',(70,76,79))
    b.add_part(bezel,'OLED 0.96 removable face carrier')
    b.add_part(clamp,'OLED PCB retaining frame')
    board=b.box('OLED PCB envelope',(-35,90,-44.6),OLED_PCB)
    b.add_hardware(board,'OLED assumed 29.2x26.7x6.2')
    board.isLightBulbOn=False
    glass=b.rounded_xy('OLED screen glass',-35,90,-48.1,21.74,11.18,.6,.2)
    b.paint(glass,'OLED glass black',(5,12,15))
    glass.name='VIS | OLED glass'
    b.visuals.append(glass)
    for x in (-39.5,-30.5):
        eye=b.rounded_xy('OLED preview eye',x,90,-48.25,3,5.8,1.3,.1)
        b.paint(eye,'OLED cyan pixels',(120,236,216))
        eye.name='VIS | OLED eye '+str(x)
        b.visuals.append(eye)


def ankle_servo(b,cx,label):
    case=b.box('Ankle servo case',(cx,30,-28.8),(12.4,22.8,23.2))
    flange=b.box('Ankle mounting ears',(cx,30,-39),(12.4,32.5,2))
    case=b.join(case,[flange],'MG90S ankle mounting ears')
    gear=b.cyl('Ankle output boss',(cx,35.7,-43.4),(cx,35.7,-40.4),3.6)
    shaft=b.cyl('Ankle spline envelope',(cx,35.7,-45.7),(cx,35.7,-43.4),2.35)
    case=b.join(case,[gear,shaft],'MG90S ankle complete reference')
    for y in (16,44):
        case=b.cut(case,[b.cyl('Servo tab hole',(cx,y,-41),(cx,y,-37),1.1)],'Ankle servo tab hole')
    b.paint(case,'MG90S graphite',(45,48,56))
    b.add_hardware(case,'MG90S ankle '+label)


def leg(b,source,cx,label):
    body=source.copyToComponent(b.occ)
    keep=b.box('Upper user leg selection',(cx,60,-20),(50,84,70))
    body=b.intersect(body,keep,'Separate moving leg from foot at Y18')
    for sign in (-1,1):
        rail=b.box('Servo retaining side rail',(cx+sign*8.05,30,-29),(3,25,24))
        body=b.join(body,[rail],'Ankle servo cradle side rail')
    for y in (16,44):
        boss=b.cyl('Servo screw support',(cx,y,-45),(cx,y,-40.0),3.2)
        body=b.join(body,[boss],'Ankle servo mounting boss')
    case=b.box('Ankle case clearance',(cx,30,-28.8),(13.1,23.5,23.9))
    tabs=b.box('Ankle mounting ear clearance',(cx,30,-38.825),(13.1,33.2,2.35))
    gear=b.cyl('Ankle output clearance',(cx,35.7,-46),(cx,35.7,-39),4.1)
    body=b.cut(body,[case,tabs,gear],'MG90S ankle housing and shaft opening')
    for y in (16,44):
        body=b.cut(body,[b.cyl('Ankle M2 pilot',(cx,y,-46),(cx,y,-39.7),.8)],'Ankle servo mounting pilots')
    passive=b.cyl('Opposing ankle pivot support',(cx,35.7,0),(cx,35.7,5),6)
    body=b.join(body,[passive],'Passive ankle pivot boss')
    body=b.cut(body,[b.cyl('M3 passive axle',(cx,35.7,-1),(cx,35.7,6),1.6)],'Opposing M3 pivot bore')
    hip=b.cyl('Hip horn landing',(cx,45.5,-20),(cx,48,-20),9)
    body=b.join(body,[hip],'Hip horn saddle')
    socket=b.box('Short hip horn recess',(cx,47.8,-26),(6.8,2.2,14))
    hub=b.cyl('Hip horn hub clearance',(cx,44.5,-20),(cx,50.5,-20),3.8)
    slot=b.box('Hip horn fastener slot',(cx,46.5,-29),(2.2,9,5))
    body=b.cut(body,[socket,hub,slot],'Original servo horn seat and adjustable attachment')
    wire=b.box('Ankle cable exit',(cx,44,-24),(5,9,6))
    body=b.cut(body,[wire],'Ankle servo cable passage through leg bridge')
    for sign in (-1,1):
        for y in (24,38):
            a=(cx+sign*8,y,-28); c=(cx+sign*9.8,y,-28)
            boss=b.cyl('Leg cover screw boss',a,c,2.8)
            body=b.join(body,[boss],'Side cover mounting boss')
            pilot=b.cyl('Side cover M2 pilot',(cx+sign*7.8,y,-28),(cx+sign*10,y,-28),.8)
            body=b.cut(body,[pilot],'Leg side cover pilot')
    b.add_part(body,'User leg '+label+' - servo cradle')
    for sign in (-1,1):
        cover=b.box('Removable leg servo cover',(cx+sign*10.8,31.25,-20),(2,28.5,39.5))
        for y in (24,38):
            clear=b.cyl('Cover M2 clearance',(cx+sign*9,y,-28),(cx+sign*13,y,-28),1.1)
            cover=b.cut(cover,[clear],'Side cover screw clearance')
        b.add_part(cover,'Leg '+label+' side cover '+str(sign))
    ankle_servo(b,cx,label)
    hip_horn(b,cx,label)


def hip_horn(b,cx,label):
    arm=b.box('Short stock hip horn',(cx,47.7,-26),(5.5,1.5,13))
    hub=b.cyl('Stock hip horn hub',(cx,47.2,-20),(cx,49.2,-20),3.5)
    arm=b.join(arm,[hub],'Original plastic hip horn reference')
    b.paint(arm,'Servo horns ivory',(218,220,209))
    b.add_hardware(arm,'Hip horn '+label)


def foot(b,source,cx,label):
    body=source.copyToComponent(b.occ)
    keep=b.box('User foot selection',(cx,0,-20),(110,24,90))
    body=b.intersect(body,keep,'Separate original foot at Y12')
    relief=b.cyl('Ankle circular sweep clearance',(cx,35.7,-45.3),(cx,35.7,5.3),24)
    body=b.cut(body,[relief],'Clear rotating foot beneath leg cradle')
    for z in (-47.5,7.5):
        arm=b.box('Ankle fork upright',(cx,22,-0+z),(15,38,3))
        crown=b.cyl('Rounded fork pivot',(cx,35.7,z-1.5),(cx,35.7,z+1.5),7.5)
        body=b.join(body,[arm,crown],'Ankle double supported fork')
    rear=b.cyl('Rear M3 pivot clearance',(cx,35.7,5.5),(cx,35.7,10),1.6)
    hub=b.cyl('Front horn hub passage',(cx,35.7,-51),(cx,35.7,-45.4),3.8)
    socket=b.box('Short ankle horn recess',(cx,29.7,-48.1),(6.8,14,1.8))
    fastener=b.box('Ankle horn adjustable screw slot',(cx,26.7,-47.5),(2.2,5,6))
    body=b.cut(body,[rear,hub,socket,fastener],'Ankle horn and passive pivot fixings')
    if label=='R':
        rib=b.cyl('Repair original zero-thickness sole contact',(cx,3,-.8),(cx,3,5.8),.8)
        body=b.join(body,[rib],'Reinforce original right sole junction')
    b.add_part(body,'User foot '+label+' - ankle fork')
    arm=b.box('Short stock ankle horn',(cx,29.7,-48.1),(5.5,13,1.4))
    hornhub=b.cyl('Ankle horn hub',(cx,35.7,-48.8),(cx,35.7,-45.7),3.5)
    arm=b.join(arm,[hornhub],'Original plastic ankle horn reference')
    b.paint(arm,'Servo horns ivory',(218,220,209))
    b.add_hardware(arm,'Ankle horn '+label)


def revolute(root,parent,child,name,position,direction,limit):
    # AsBuiltJoints may ignore custom input axes. Align geometry's local Z instead.
    axis='y' if direction[1] else 'z'
    offset=position[1] if axis=='y' else position[2]
    sketch=parent.comp.sketches.add(parent.plane(axis,offset))
    sketch.name=name+' aligned hinge datum'
    center=sketch.modelToSketchSpace(pt(*position))
    sketch.sketchCurves.sketchCircles.addByCenterRadius(center,.1)
    profile=sketch.profiles.item(0).createForAssemblyContext(parent.occ)
    geom=F.JointGeometry.createByProfile(profile,None,F.JointKeyPointTypes.CenterKeyPoint)
    unit=geom.primaryAxisVector
    assert abs(unit.dotProduct(vector(direction)))>.9999,(name,unit.asArray())
    data=root.asBuiltJoints.createInput(parent.occ,child.occ,geom)
    assert data.setAsRevoluteJointMotion(F.JointDirections.ZAxisJointDirection)
    joint=root.asBuiltJoints.add(data)
    joint.name=name
    motion=F.RevoluteJointMotion.cast(joint.jointMotion)
    limits=motion.rotationLimits
    limits.minimumValue=math.radians(-limit)
    limits.maximumValue=math.radians(limit)
    limits.isMinimumValueEnabled=True
    limits.isMaximumValueEnabled=True
    sketch.isLightBulbOn=False
    return joint


def collisions(design,groups):
    bodies=[]
    for b in groups:
        wanted={v.name for v in b.parts+b.hardware}
        bodies.extend(v for v in b.occ.bRepBodies if v.name in wanted)
    query=design.createInterferenceInput(objs(bodies))
    query.areCoincidentFacesIncluded=False
    results=design.analyzeInterference(query)
    clashes=[]
    for result in results:
        if not result.interferenceBody or result.interferenceBody.volume<0.00002:continue
        a,c=result.entityOne.name,result.entityTwo.name
        if ('MG90S' in a and 'horn' in c) or ('MG90S' in c and 'horn' in a):
            # A horn is seated on its servo spline; check corresponding hardware only.
            if a.split()[-1]==c.split()[-1] and ('hip' in a.lower())==('hip' in c.lower()):continue
        clashes.append({'a':a,'b':c,'volume_mm3':result.interferenceBody.volume*1000})
    return clashes


def audit(design,groups,joints):
    for b in groups:
        assert b.comp.bRepBodies.count==len(b.parts+b.hardware+b.visuals),(b.comp.name,[v.name for v in b.comp.bRepBodies])
    errors=[]
    for item in design.timeline:
        entity=item.entity
        if hasattr(entity,'healthState') and entity.healthState==F.FeatureHealthStates.ErrorFeatureHealthState:
            errors.append(entity.name+': '+entity.errorOrWarningMessage)
    report={'feature_errors':errors,'joint_count':len(joints),'neutral_collisions':collisions(design,groups),'poses':[]}
    report['parts']=[{'name':v.name,'solid':v.isSolid,'volume_mm3':v.volume*1000} for b in groups for v in b.parts]
    report['joints']=[{'name':j.name,'axis':[j.jointMotion.rotationAxisVector.x,j.jointMotion.rotationAxisVector.y,j.jointMotion.rotationAxisVector.z]} for j in joints]
    with open(os.path.join(OUT,'mechanical-validation.json'),'w') as f:json.dump(report,f,indent=2)
    assert not errors,errors
    assert all(v['solid'] and v['volume_mm3']>0 for v in report['parts'])
    if report['neutral_collisions']:return report
    try:
        for angles in motion_samples(HIP_LIMIT_DEG,ANKLE_LIMIT_DEG):
            for joint,angle in zip(joints,angles):joint.jointMotion.rotationValue=math.radians(angle)
            adsk.doEvents()
            overlap=collisions(design,groups)
            transforms=[b.occ.transform2.asArray() for b in groups]
            for lb,fb,cx in ((groups[1],groups[2],HIP_X[0]),(groups[3],groups[4],HIP_X[1])):
                up=vector((0,1,0)); up.transformBy(lb.occ.transform2)
                assert abs(up.dotProduct(vector((0,1,0)))-1)<1e-6,'Hip must yaw about vertical Y'
                pivot=pt(cx,HIP_Y,HIP_Z); pivot.transformBy(lb.occ.transform2)
                assert pivot.distanceTo(pt(cx,HIP_Y,HIP_Z))<1e-6,'Hip pivot moved'
                legaxis=vector((0,0,1)); legaxis.transformBy(lb.occ.transform2)
                footaxis=vector((0,0,1)); footaxis.transformBy(fb.occ.transform2)
                assert abs(legaxis.dotProduct(footaxis)-1)<1e-6,'Ankle must roll about leg Z'
            report['poses'].append({'degrees':angles,'collisions':overlap,'transforms':transforms})
        return report
    finally:
        for joint in joints:joint.jointMotion.rotationValue=0
        adsk.doEvents()
        with open(os.path.join(OUT,'mechanical-validation.json'),'w') as f:json.dump(report,f,indent=2)


def clean_step(design,groups,app):
    # STEP contains only the twelve print solids; native F3D retains the live mechanism.
    source=app.activeDocument
    temp=F.TemporaryBRepManager.get()
    snapshots=[(temp.copy(body.createForAssemblyContext(b.occ)),body.name)
               for b in groups for body in b.parts]
    document=app.documents.add(C.DocumentTypes.FusionDesignDocumentType)
    try:
        clean=F.Design.cast(app.activeProduct)
        base=clean.rootComponent.features.baseFeatures.add()
        base.startEdit()
        for transient,name in snapshots:
            body=clean.rootComponent.bRepBodies.add(transient,base)
            body.name=name
        base.finishEdit()
        assert clean.rootComponent.bRepBodies.count==12
        manager=clean.exportManager
        assert manager.execute(manager.createSTEPExportOptions(os.path.join(OUT,'Emo-4servo.step')))
    finally:
        document.close(False)
        source.activate()


def export(design,groups,app):
    manager=design.exportManager
    for joint in design.rootComponent.asBuiltJoints:joint.isLightBulbOn=False
    for b in groups:
        for body in b.parts:
            filename=body.name.replace('PRINT | ','').replace(' ','_')+'.stl'
            options=manager.createSTLExportOptions(body,os.path.join(OUT,filename))
            options.meshRefinement=F.MeshRefinementSettings.MeshRefinementHigh
            options.unitType=F.DistanceUnits.MillimeterDistanceUnits
            assert manager.execute(options),filename
    for b in groups:
        for sketch in b.comp.sketches:sketch.isLightBulbOn=False
        b.comp.isOriginFolderLightBulbOn=False
    camera=app.activeViewport.camera
    camera.cameraType=C.CameraTypes.OrthographicCameraType
    camera.eye=pt(-200,180,-300)
    camera.target=pt(-35,65,-20)
    camera.upVector=vector((0,1,0))
    camera.isFitView=True
    camera.isSmoothTransition=False
    app.activeViewport.camera=camera
    app.activeViewport.refresh()
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-4servo-preview.png'),1600,1600)
    try:
        for joint,angle in zip(design.rootComponent.asBuiltJoints,(15,-15,10,-10)):
            joint.jointMotion.rotationValue=math.radians(angle)
        adsk.doEvents()
        assert not collisions(design,groups),'Demonstration pose has interference'
        app.activeViewport.refresh()
        app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-4servo-joints-demo.png'),1600,1600)
    finally:
        for joint in design.rootComponent.asBuiltJoints:joint.jointMotion.rotationValue=0
        adsk.doEvents()
    visibility=[(v,v.isLightBulbOn) for v in groups[0].parts+groups[0].hardware]
    for body in groups[0].parts:
        if 'rear service lid' in body.name:body.isLightBulbOn=False
    for body in groups[0].hardware:body.isLightBulbOn=True
    camera=app.activeViewport.camera
    camera.eye=pt(130,180,260)
    camera.target=pt(-35,65,-20)
    camera.upVector=vector((0,1,0))
    camera.isFitView=True
    app.activeViewport.camera=camera
    app.activeViewport.refresh()
    app.activeViewport.saveAsImageFile(os.path.join(OUT,'Emo-4servo-interior.png'),1600,1600)
    for body,visible in visibility:body.isLightBulbOn=visible
    camera.eye=pt(-200,180,-300)
    camera.target=pt(-35,65,-20)
    camera.isFitView=True
    app.activeViewport.camera=camera
    app.activeViewport.refresh()
    clean_step(design,groups,app)
    assert manager.execute(manager.createFusionArchiveExportOptions(os.path.join(OUT,'Emo-4servo.f3d')))


def run(context):
    os.makedirs(OUT,exist_ok=True)
    with open(LOG,'w') as f:f.write('EMO INTEGRATION\n')
    app=C.Application.get()
    try:
        assert not validate(),validate()
        backup=os.path.join(OUT,'Original-user-backup.f3d')
        assert os.path.exists(backup),'Run EmoInspect on the original first'
        document=app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(backup))
        document.name='emo robot - 4x MG90S + OLED - working copy'
        design=F.Design.cast(app.activeProduct)
        design.designIntent=F.DesignIntentTypes.HybridDesignIntentType
        root=design.rootComponent
        source=tuple(root.bRepBodies)
        assert len(source)==5,len(source)
        head=new_group(design,'01 Torso - grounded - OLED and hip servos')
        log('Torso');torso(head,source[2])
        groups=[head]
        legs=[];feet=[]
        for body,cx,label in zip(source[:2],HIP_X,('L','R')):
            lb=new_group(design,'Leg '+label+' - hip moving assembly')
            log('Leg '+label);leg(lb,body,cx,label)
            fb=new_group(design,'Foot '+label+' - ankle moving assembly')
            log('Foot '+label);foot(fb,body,cx,label)
            legs.append(lb);feet.append(fb);groups.extend((lb,fb))
        for body in source:body.isLightBulbOn=False
        for sketch in root.sketches:sketch.isLightBulbOn=False
        joints=[]
        for lb,cx,label in zip(legs,HIP_X,('L','R')):
            joints.append(revolute(root,head,lb,'HIP '+label+' - yaw +/-'+str(HIP_LIMIT_DEG)+' deg',(cx,HIP_Y,HIP_Z),(0,1,0),HIP_LIMIT_DEG))
        for lb,fb,cx,label in zip(legs,feet,HIP_X,('L','R')):
            joints.append(revolute(root,lb,fb,'ANKLE '+label+' - roll +/-'+str(ANKLE_LIMIT_DEG)+' deg',(cx,ANKLE_Y,ANKLE_Z),(0,0,1),ANKLE_LIMIT_DEG))
        log('Audit');report=audit(design,groups,joints)
        log(json.dumps({'neutral':report['neutral_collisions'],'failed_poses':sum(bool(v['collisions']) for v in report['poses'])}))
        assert not report['neutral_collisions'],report['neutral_collisions']
        assert len(report['poses'])==49 and not any(v['collisions'] for v in report['poses']),'Sampled motion contains collisions'
        document.activate()
        log('Export');export(design,groups,app)
        log('SUCCESS')
    except Exception:
        log(traceback.format_exc())
        app.userInterface.messageBox(traceback.format_exc())
