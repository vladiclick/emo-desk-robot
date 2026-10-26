import adsk.core as C
import adsk.fusion as F
import adsk
import os,json,math,traceback
HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(HERE,'..','..','outputs','Emo-Complete'))
def pt(x,y,z):return C.Point3D.create(x/10,y/10,z/10)
def run(context):
 app=C.Application.get()
 try:
  archive=os.path.join(OUT,'Emo-Complete.f3d')
  doc=app.importManager.importToNewDocument(app.importManager.createFusionArchiveImportOptions(archive))
  doc.name='Emo - complete electronics assembly - verified'
  design=F.Design.cast(app.activeProduct);root=design.rootComponent;joints=list(root.asBuiltJoints);occ=list(root.occurrences)
  assert len(joints)==4 and root.motionLinks.count==0 and len(occ)==5
  parts=[v for o in occ for v in o.component.bRepBodies if v.name.startswith('PRINT |')]
  motors=[v for o in occ for v in o.component.bRepBodies if v.name.startswith('REF | MG90S')]
  assert len(parts)==17 and len(motors)==4 and sum(o.isGrounded for o in occ)==1
  tests=[]
  for i,j in enumerate(joints):
   wanted=(0,1,0) if i<2 else (0,0,1)
   assert abs(abs(j.jointMotion.rotationAxisVector.dotProduct(C.Vector3D.create(*wanted)))-1)<1e-6
   before=j.occurrenceTwo.transform2.asArray();j.jointMotion.rotationValue=math.radians(5)
   adsk.doEvents();app.activeViewport.refresh();after=j.occurrenceTwo.transform2.asArray()
   assert max(abs(a-b) for a,b in zip(before,after))>.001
   assert abs(math.degrees(j.jointMotion.rotationValue)-5)<1e-5
   for leg,foot,cx in ((occ[1],occ[2],-62.5),(occ[3],occ[4],-7.5)):
    a=pt(cx,9.5,-37);a.transformBy(leg.transform2)
    b=pt(cx,9.5,-37);b.transformBy(foot.transform2)
    assert a.distanceTo(b)<1e-6,'Ankle output axis and foot pivot not coaxial'
   tests.append({'joint':j.name,'driven_deg':5,'component_moved':True})
   j.jointMotion.rotationValue=0;adsk.doEvents();app.activeViewport.refresh()
  assert all(sum(v.name.startswith('REF | MG90S ANKLE IN FOOT') for v in occ[i].component.bRepBodies)==1 for i in (2,4)), 'Motor not attached to foot'
  assert all(not any(v.name.startswith('REF | MG90S ANKLE') for v in occ[i].component.bRepBodies) for i in (1,3)), 'Ankle motor still in leg'
  required=('ESP32-C3 SuperMini PCB','Pololu U3V70F5 PCB','DFRobot DFR0668 charger PCB','DFPlayer Mini PCB','1S protection 32195 PCB','IMU GY-521 envelope PCB','GNB6501S70A 1S 650mAh','20mm 8ohm speaker allowance','External charge USB-C allowance','SparkFun BOB-23055 PCB flange','Capacitor 2.5mm nylon tie allowance','RUN OFF CHARGE switch allowance')
  present=[body.name.replace('REF | ','') for body in occ[0].component.bRepBodies if body.name.startswith('REF |')]
  assert all(name in present for name in required),(required,present)
  report={'electronics_present':list(required),'ankle_motors_belong_to_feet':True,'archive_reloaded':True,'revolute_joints':4,'motion_links':0,'MG90S':4,'print_parts':17,'grounded_parts':1,'direct_coaxial_axes_verified':True,'tests':tests,'all_passed':True}
  with open(os.path.join(OUT,'native-reload-validation.json'),'w') as f:json.dump(report,f,indent=2)
  from .assembly_audit import audit_carrier
  insertion=audit_carrier(app,design,occ)
  assert insertion['all_passed'],'Carrier insertion clash: '+str(insertion)
  from .hip_audit import audit_hips
  hip_insertion=audit_hips(app,design,occ)
  assert hip_insertion['all_passed'],'Hip insertion clash; see hip-insertion-validation.json'
  temp=F.TemporaryBRepManager.get();snapshots=[(temp.copy(v.createForAssemblyContext(o)),v.name) for o in occ for v in o.component.bRepBodies if v.name.startswith('PRINT |')]
  clean_doc=app.documents.add(C.DocumentTypes.FusionDesignDocumentType)
  clean=F.Design.cast(app.activeProduct);feature=clean.rootComponent.features.baseFeatures.add();feature.startEdit()
  for shape,name in snapshots:
   v=clean.rootComponent.bRepBodies.add(shape,feature);v.name=name
  feature.finishEdit();assert clean.rootComponent.bRepBodies.count==17
  m=clean.exportManager;assert m.execute(m.createSTEPExportOptions(os.path.join(OUT,'Emo-Complete-print.step')))
  clean_doc.close(False);doc.activate()
  for other in tuple(app.documents):
   if other!=doc and (other.name.startswith('Emo original - complete assembly - working') or other.name.startswith('Emo - complete electronics assembly - verified')):other.close(False)
  cam=app.activeViewport.camera;cam.cameraType=C.CameraTypes.OrthographicCameraType
  cam.eye=pt(-200,170,-300);cam.target=pt(-35,54,-20);cam.upVector=C.Vector3D.create(0,1,0);cam.isFitView=True;cam.isSmoothTransition=False
  app.activeViewport.camera=cam;app.activeViewport.refresh()
  with open(os.path.join(HERE,'verify-status.txt'),'w') as f:f.write('DIRECT NATIVE VERIFIED')
 except Exception:
  with open(os.path.join(HERE,'verify-status.txt'),'w') as f:f.write(traceback.format_exc())
  app.activeDocument.activate()
