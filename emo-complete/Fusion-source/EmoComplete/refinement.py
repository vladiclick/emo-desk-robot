"""Reversible appearance themes and printed compliant soles."""
import adsk.core as C
import adsk.fusion as F
from .base import objs,vi

THEMES={
 'Cloud':{'shell':(211,214,210),'lid':(225,227,221),'leg':(49,58,66),'shoe':(193,200,196),'accent':(49,159,161)},
 'Night':{'shell':(45,51,59),'lid':(64,72,80),'leg':(39,45,53),'shoe':(56,65,74),'accent':(67,177,184)},
 'Sage':{'shell':(131,155,143),'lid':(208,214,202),'leg':(57,68,64),'shoe':(151,171,158),'accent':(208,179,113)},
}

def apply_theme(groups,name='Cloud'):
    t=THEMES[name]
    for g in groups:
        for body in g.parts:
            n=body.name.lower()
            color=t['accent'] if 'tpu' in n else t['leg'] if 'leg ' in n else t['lid'] if 'lid' in n else t['shoe'] if 'shoe' in n else t['shell'] if 'head -' in n else (70,79,88)
            g.paint(body,name+' '+str(color),color)
            if 'head -' in n:
                for face in body.faces:
                    bb=face.boundingBox
                    if abs(bb.maxPoint.z-bb.minPoint.z)<1e-6 and bb.maxPoint.z<-4.39 and face.area>.05:
                        g.paint(face,name+' face graphite',(22,28,34))

def grip_sole(b,cx,label):
    from .EmoComplete import rounded_xz
    shoe=b.parts[0];old=shoe.name
    recess=rounded_xz(b,'Compliant sole recess',cx,.42,-20,50.5,60.5,10.2,1.26)
    shoe=b.cut(shoe,[recess],'Recess flush TPU traction sole')
    pad=rounded_xz(b,'TPU contact sole',cx,.4,-20,50,60,10,.8)
    for dx in (-12,12):
        for z in (-44,4):
            peg=b.cyl('TPU retaining neck',(cx+dx,.6,z),(cx+dx,1.95,z),1.2)
            head=b.cyl('TPU retaining head',(cx+dx,1.75,z),(cx+dx,2.5,z),1.55)
            pad=b.join(pad,[peg,head],'Four compliant sole retaining pegs')
            shoe=b.cut(shoe,[b.cyl('Sole neck receiver',(cx+dx,.55,z),(cx+dx,2.0,z),1.35),b.cyl('Sole head pocket',(cx+dx,1.6,z),(cx+dx,2.8,z),1.7)],'Blind TPU mushroom receivers')
    # Narrow, shallow siping gives purchase without creating fragile islands.
    grooves=[b.box('TPU tread groove',(cx,.07,z),(35,.3,.65)) for z in (-33,-25,-17,-9)]
    pad=b.cut(pad,grooves,'Flexible sole traction channels')
    shoe.name=old;b.parts[0]=shoe
    b.paint(pad,'TPU traction accent',(49,159,161));b.add_part(pad,'Foot '+label+' - TPU traction sole')

def safe_round(b,body,radius,selector,name):
    edges=[edge for edge in body.edges if selector(edge.boundingBox)]
    if not edges:return body
    data=b.comp.features.filletFeatures.createInput()
    data.addConstantRadiusEdgeSet(objs(edges),vi(radius),False)
    data.isRollingBallCorner=True
    feature=b.comp.features.filletFeatures.add(data);feature.name=name
    assert feature.healthState!=F.FeatureHealthStates.ErrorFeatureHealthState
    return feature.bodies.item(0)

def refine_parts(groups):
    for g,cx,label in ((groups[2],-75,'L'),(groups[4],5,'R')):
        grip_sole(g,cx,label)
    # Existing fillets on the original shell are retained. Do not round fit faces.
    apply_theme(groups,'Cloud')
