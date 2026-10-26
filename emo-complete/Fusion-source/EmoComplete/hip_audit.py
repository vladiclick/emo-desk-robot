"""Sample assembly translations; manual clip release is stated explicitly."""
import os,json
import adsk,adsk.core as C,adsk.fusion as F
from .base import objs,vector,pt

def sweep(app,design,shapes,fixed,offsets,name):
    root=design.rootComponent;temp=F.TemporaryBRepManager.get()
    probe=root.occurrences.addNewComponent(C.Matrix3D.create());probe.component.name='Temporary '+name
    feature=probe.component.features.baseFeatures.add();feature.startEdit()
    for body in shapes:
        v=probe.component.bRepBodies.add(temp.copy(body),feature);v.name='PROBE | '+body.name
    feature.finishEdit();probe.isLightBulbOn=False
    samples=[]
    try:
        for dz in offsets:
            matrix=C.Matrix3D.create();matrix.translation=vector((0,0,dz/10));probe.transform2=matrix;adsk.doEvents()
            seq=list(fixed)+[v.createForAssemblyContext(probe) for v in probe.component.bRepBodies]
            query=design.createInterferenceInput(objs(seq));query.areCoincidentFacesIncluded=False
            clashes=[]
            for item in design.analyzeInterference(query):
                a,c=item.entityOne.name,item.entityTwo.name
                if a.startswith('PROBE')==c.startswith('PROBE'):continue
                if item.interferenceBody and item.interferenceBody.volume>=.00002:
                    box=item.interferenceBody.boundingBox
                    clashes.append({'a':a,'b':c,'volume_mm3':round(item.interferenceBody.volume*1000,5),'bbox_mm':[[round(v*10,3) for v in box.minPoint.asArray()],[round(v*10,3) for v in box.maxPoint.asArray()]]})
            samples.append({'z_offset_mm':dz,'collisions':clashes})
        return {'name':name,'moving_bodies':len(shapes),'samples':samples,'all_passed':not any(s['collisions'] for s in samples)}
    finally:probe.deleteMe();adsk.doEvents()

def audit_hips(app,design,occ):
    head=occ[0];root=design.rootComponent;temp=F.TemporaryBRepManager.get()
    rack=next(v for v in head.component.bRepBodies if 'PRINT | Two hip servo' in v.name)
    # Only the hooks are held out by hand. Rigid rack elsewhere is unchanged.
    released=temp.copy(rack)
    for cx in (-62.5,-7.5):
        for sign in (-1,1):
            box=C.OrientedBoundingBox3D.create(pt(cx+sign*5.95,60.8,-40.4),vector((1,0,0)),vector((0,1,0)),.15,.13,.33)
            assert temp.booleanOperation(released,temp.createBox(box),F.BooleanTypes.DifferenceBooleanType)
    holder=root.occurrences.addNewComponent(C.Matrix3D.create());holder.component.name='Temporary held-open hip hooks'
    bf=holder.component.features.baseFeatures.add();bf.startEdit();rel=holder.component.bRepBodies.add(released,bf);bf.finishEdit();rel.name='Rack with two hook tips held outward';holder.isLightBulbOn=False
    tests=[];loaded=[rack.createForAssemblyContext(head)]
    try:
        for legidx,label in ((1,'L'),(3,'R')):
            motor=[v.createForAssemblyContext(head) for v in head.component.bRepBodies if v.name.startswith('REF | MG90S HIP '+label+' |')]
            leg=[v.createForAssemblyContext(occ[legidx]) for v in occ[legidx].component.bRepBodies if v.name.startswith(('PRINT |','REF | Stock hip horn'))]
            shapes=motor+leg;loaded+=shapes
            tests.append(sweep(app,design,shapes,[rel.createForAssemblyContext(holder)],(-55,-45,-35,-25,-18,-12,-8,-4,-2),label+' hip front insertion with clips held open'))
            tests.append(sweep(app,design,shapes,[rack.createForAssemblyContext(head)],(0,),label+' hip seated with released hooks'))
        fixed=[v.createForAssemblyContext(head) for v in head.component.bRepBodies if ('PRINT | Original head' in v.name or 'PRINT | OLED hidden' in v.name or v.name.startswith('REF | OLED'))]
        tests.append(sweep(app,design,loaded,fixed,(65,52,40,30,22,16,12,8,4,2,0),'Loaded rack rear insertion into head'))
    finally:holder.deleteMe();adsk.doEvents()
    report={'purpose':'Sampled rigid assembly paths. Hold both retaining hook tips outward about 1mm during motor front insertion; elasticity not simulated. Feet and cassette installed afterward.','tests':tests,'all_passed':all(t['all_passed'] for t in tests)}
    out=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','outputs','Emo-Complete'))
    with open(os.path.join(out,'hip-insertion-validation.json'),'w') as f:json.dump(report,f,indent=2)
    return report
