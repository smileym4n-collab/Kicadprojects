from pathlib import Path
import cadquery as cq
import json,hashlib,zipfile
root=Path.cwd(); out=root/'output/dual-emitter-resistor'
files=list(root.glob('*.kicad_*'))
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
name='R_Dual_0R22_L31_W5_H18_P10'
a=cq.Assembly(name=name)
body=cq.Workplane('XY').box(31,5,18,centered=(True,True,False)).edges().fillet(.55).translate((0,0,3))
a.add(body,name='Ceramic_body',color=cq.Color(.85,.83,.76))
# Leads meet the PCB on the footprint centres. Outer leads include a modest formed bend.
for i,x in enumerate([-10,0,10],1):
    pts=[(x,0,-3),(x,0,.8),(x+(-.8 if x<0 else .8 if x>0 else 0),0,1.8),(x,0,2.8),(x,0,3.6)]
    lead=None
    for p,q in zip(pts,pts[1:]):
        v=cq.Vector(q)-cq.Vector(p)
        s=cq.Solid.makeCylinder(.5,v.Length,cq.Vector(p),v.normalized())
        lead=s if lead is None else lead.fuse(s)
    for p in pts[1:-1]: lead=lead.fuse(cq.Solid.makeSphere(.5,cq.Vector(p)))
    a.add(lead,name=f'Lead_{i}',color=cq.Color(.65,.67,.69))
# Generic value marking; no unverified power rating or manufacturer branding.
mark=cq.Workplane('XZ',origin=(0,-2.505,15)).text('0R22 + 0R22',1.7,.015,combine=False)
a.add(mark,name='Value_marking',color=cq.Color(.24,.25,.23))
step=out/'YamahaSalvage.3dshapes'/f'{name}.step'
a.save(str(step))
loaded=cq.importers.importStep(str(step))
assert all(s.isValid() for s in loaded.solids().vals())
fpname='R_Dual_Power_L31_W5_H18_P10'
source=(root/'YamahaSalvage.pretty'/f'{fpname}.kicad_mod').read_text()
model=f'\n(model "${{KIPRJMOD}}/YamahaSalvage.3dshapes/{name}.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n'
fp=source.rstrip()[:-1]+model+')\n'
(out/'YamahaSalvage.pretty'/f'{fpname}.kicad_mod').write_text(fp)
# An isolated board allows KiCad's renderer to verify actual STEP placement.
absfp=fp.replace('${KIPRJMOD}',str(out))
board='(kicad_pcb (version 20241229) (generator "pcbnew") (general (thickness 1.6)) (paper "A4") (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "b.silkscreen") (37 "F.SilkS" user "f.silkscreen") (44 "Edge.Cuts" user) (47 "F.CrtYd" user "f.courtyard") (49 "F.Fab" user)) (setup (pad_to_mask_clearance 0)) '+absfp+' (gr_rect (start -18 -5) (end 18 5) (stroke (width .05) (type default)) (fill none) (layer "Edge.Cuts")))'
(root/'work/dual-resistor-3d/check.kicad_pcb').write_text(board)
report={'body_mm':[31,5,18],'body_bottom_above_PCB_mm':3,'lead_diameter_mm':1,'pad_and_lead_centres_mm':[[-10,0],[0,0],[10,0]],'hole_diameter_mm':1.3,'STEP_reimport_valid':True,'STEP_solids':loaded.solids().size(),'production_files_unchanged':all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items())}
(out/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
