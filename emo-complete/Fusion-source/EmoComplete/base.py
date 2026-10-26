import adsk.core as C
import adsk.fusion as F
import math
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


