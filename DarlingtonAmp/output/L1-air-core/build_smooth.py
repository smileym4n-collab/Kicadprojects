from pathlib import Path
import cadquery as cq
import json
out=Path('output/L1-air-core'); step=out/'YamahaSalvage.3dshapes/L_AirCore_0u95H_P12_Horizontal.step'
a=cq.Assembly(name='L1_horizontal_air_core')
helix=cq.Wire.makeHelix(1.2,12,5.8).rotate((0,0,0),(0,1,0),90).translate((-6,0,7.3))
plane=cq.Plane(origin=helix.startPoint(),normal=helix.Edges()[0].tangentAt(0))
coil=cq.Workplane(plane).circle(.55).sweep(helix,isFrenet=True)
assert coil.val().isValid()
a.add(coil,name='Copper_winding',color=cq.Color(.65,.28,.09))
for i,x in enumerate([-6,6],1):
 pts=[(x,6,-.5),(x,6,.8),(x,5.7,1.5),(x,0,1.5)]
 lead=None
 for p,q in zip(pts,pts[1:]):
  v=cq.Vector(q)-cq.Vector(p);s=cq.Solid.makeCylinder(.55,v.Length,cq.Vector(p),v.normalized());lead=s if lead is None else lead.fuse(s)
 for p in pts[1:-1]:lead=lead.fuse(cq.Solid.makeSphere(.55,cq.Vector(p)))
 a.add(lead,name=f'Copper_lead_{i}',color=cq.Color(.65,.28,.09))
 a.add(cq.Solid.makeCylinder(.55,2.5,cq.Vector(x,6,-3)),name=f'Tinned_pin_{i}',color=cq.Color(.7,.72,.74))
a.save(str(step))
s=cq.importers.importStep(str(step));assert all(v.isValid() for v in s.solids().vals())
(out/'validation.json').write_text(json.dumps({'STEP_solids':s.solids().size(),'all_solids_valid':True,'pin_pitch_mm':12,'wire_diameter_mm':1.1,'turns_illustrative':10,'coil_outer_diameter_mm':12.7,'coil_top_above_board_mm':13.65,'electrical_inductance_not_validated':True},indent=2))
print('STEP reimport: valid',s.solids().size(),'solids')
