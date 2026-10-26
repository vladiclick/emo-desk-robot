"""CAD sampled rear insertion of the populated electronics cassette."""
import adsk.core as C
import adsk.fusion as F
import adsk,json,os
from .base import objs,vector

def audit_carrier(app,design,occ):
    root=design.rootComponent;head=occ[0]
    moving=[];stationary=[]
    for body in head.component.bRepBodies:
        name=body.name
        if name.startswith('PRINT |'):
            if any(s in name for s in ('Removable electronics','TPU loose battery','TPU speaker')):moving.append(body)
            elif 'Rear lid' not in name:stationary.append(body.createForAssemblyContext(head))
        elif name.startswith('REF |'):
            if 'MG90S HIP' in name or 'OLED' in name:stationary.append(body.createForAssemblyContext(head))
            else:moving.append(body)
    # Include only leg bodies that can overlap the swept cassette bounding boxes.
    for o in occ[1:]:
        for body in o.component.bRepBodies:
            if not body.name.startswith(('PRINT |','REF |')):continue
            bb=body.boundingBox
            for m in moving:
                b=m.boundingBox
                if b.minPoint.x<bb.maxPoint.x and b.maxPoint.x>bb.minPoint.x and b.minPoint.y<bb.maxPoint.y and b.maxPoint.y>bb.minPoint.y and b.minPoint.z<bb.maxPoint.z:
                    stationary.append(body.createForAssemblyContext(o));break
    probe=root.occurrences.addNewComponent(C.Matrix3D.create());probe.component.name='Temporary cassette insertion audit'
    temp=F.TemporaryBRepManager.get();feature=probe.component.features.baseFeatures.add();feature.startEdit()
    for body in moving:
        v=probe.component.bRepBodies.add(temp.copy(body.createForAssemblyContext(head)),feature);v.name='PROBE | '+body.name
    feature.finishEdit();probe.isLightBulbOn=False
    samples=[]
    try:
        for dz in (0,4,8,16,24,36,52,65):
            matrix=C.Matrix3D.create();matrix.translation=vector((0,0,dz/10));probe.transform2=matrix;adsk.doEvents()
            seq=stationary+[v.createForAssemblyContext(probe) for v in probe.component.bRepBodies]
            query=design.createInterferenceInput(objs(seq));query.areCoincidentFacesIncluded=False
            clashes=[]
            for item in design.analyzeInterference(query):
                a,c=item.entityOne.name,item.entityTwo.name
                if a.startswith('PROBE')==c.startswith('PROBE'):continue
                if item.interferenceBody and item.interferenceBody.volume>=.00002:
                    clashes.append({'a':a,'b':c,'volume_mm3':round(item.interferenceBody.volume*1000,5),'bbox':[[round(v*10,3) for v in item.interferenceBody.boundingBox.minPoint.asArray()],[round(v*10,3) for v in item.interferenceBody.boundingBox.maxPoint.asArray()]]})
            samples.append({'rear_offset_mm':dz,'collisions':clashes})
        report={'purpose':'Populated cassette rear insertion, cap removed; rigid sampled positions only','moving_bodies':len(moving),'samples':samples,'all_passed':not any(s['collisions'] for s in samples)}
        out=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','outputs','Emo-Complete'))
        with open(os.path.join(out,'cassette-insertion-validation.json'),'w') as f:json.dump(report,f,indent=2)
        return report
    finally:
        probe.deleteMe();adsk.doEvents();app.activeViewport.refresh()
