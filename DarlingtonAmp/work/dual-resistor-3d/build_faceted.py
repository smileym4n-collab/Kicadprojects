from pathlib import Path
import math,json,hashlib
root=Path.cwd(); out=root/'output/dual-emitter-resistor'; name='R_Dual_0R22_L31_W5_H18_P10'
E=[]
def add(s):
 E.append(s);return '#'+str(len(E))
def refs(xs):return '('+','.join(xs)+')'
ctx=add("APPLICATION_CONTEXT('automotive_design')")
add(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,{ctx})")
prodctx=add(f"PRODUCT_CONTEXT('',{ctx},'mechanical')")
p=add(f"PRODUCT('{name}','{name}','',{refs([prodctx])})")
f=add(f"PRODUCT_DEFINITION_FORMATION('','',{p})")
dc=add(f"PRODUCT_DEFINITION_CONTEXT('part definition',{ctx},'design')")
d=add(f"PRODUCT_DEFINITION('design','',{f},{dc})")
pds=add(f"PRODUCT_DEFINITION_SHAPE('','',{d})")
unit=add("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
ang=add("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sa=add("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
u=add(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.000001),{unit},'distance_accuracy_value','')")
gc=add(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT({refs([u])})GLOBAL_UNIT_ASSIGNED_CONTEXT({refs([unit,ang,sa])})REPRESENTATION_CONTEXT('',''))")
items=[]; styles=[]
def solid(label,verts,faces,color):
 pts=[add("CARTESIAN_POINT('',("+','.join(f'{a:.8f}' for a in v)+'))') for v in verts]
 fs=[]
 for face in faces:
  loop=add(f"POLY_LOOP('',{refs([pts[i] for i in face])})")
  bound=add(f"FACE_OUTER_BOUND('',{loop},.T.)")
  a,b,c=[verts[i] for i in face[:3]]
  v=[b[i]-a[i] for i in range(3)];w=[c[i]-b[i] for i in range(3)]
  n=[v[1]*w[2]-v[2]*w[1],v[2]*w[0]-v[0]*w[2],v[0]*w[1]-v[1]*w[0]]
  ln=math.sqrt(sum(x*x for x in n));lv=math.sqrt(sum(x*x for x in v))
  normal=add("DIRECTION('',("+','.join(str(x/ln) for x in n)+'))')
  direction=add("DIRECTION('',("+','.join(str(x/lv) for x in v)+'))')
  axis=add(f"AXIS2_PLACEMENT_3D('',{pts[face[0]]},{normal},{direction})")
  plane=add(f"PLANE('',{axis})")
  fs.append(add(f"FACE_SURFACE('',{refs([bound])},{plane},.T.)"))
 shell=add(f"CLOSED_SHELL('',{refs(fs)})")
 item=add(f"FACETED_BREP('{label}',{shell})");items.append(item)
 c=add("COLOUR_RGB('',"+','.join(map(str,color))+')')
 fill=add(f"FILL_AREA_STYLE_COLOUR('',{c})")
 fas=add(f"FILL_AREA_STYLE('',{refs([fill])})")
 ss=add(f"SURFACE_STYLE_FILL_AREA({fas})")
 side=add(f"SURFACE_SIDE_STYLE('',{refs([ss])})")
 use=add(f"SURFACE_STYLE_USAGE(.BOTH.,{side})")
 assign=add(f"PRESENTATION_STYLE_ASSIGNMENT({refs([use])})")
 styles.append(add(f"STYLED_ITEM('',{refs([assign])},{item})"))
# Chamfered corners on ceramic block, with bevels on the front and back edges.
profile=[(-15.5,3.6),(-14.9,3),(14.9,3),(15.5,3.6),(15.5,20.4),(14.9,21),(-14.9,21),(-15.5,20.4)]
verts=[]
for y,shrink in [(-2.5,.25),(-2.25,0),(2.25,0),(2.5,.25)]:
 for x,z in profile:verts.append((x-math.copysign(shrink,x),y,z+shrink if z<12 else z-shrink))
faces=[list(range(7,-1,-1)),list(range(24,32))]
for j in range(3):
 for i in range(8):faces.append([j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i])
# Orientation is reversed to account for the XZ ring normal.
faces=[f[::-1] for f in faces]
solid('Ceramic body',verts,faces,(.86,.84,.77))
for n,x in enumerate([-10,0,10],1):
 rings=[(x,-3),(x,.6),(x+(-.8 if x<0 else .8 if x>0 else 0),1.6),(x,2.7),(x,3.5)]
 vs=[(xx+.5*math.cos(i*math.tau/32),.5*math.sin(i*math.tau/32),z) for xx,z in rings for i in range(32)]
 fs=[list(range(31,-1,-1)),list(range(128,160))]
 for j in range(4):
  for i in range(32):fs.append([j*32+i,j*32+(i+1)%32,(j+1)*32+(i+1)%32,(j+1)*32+i])
 solid(f'Lead {n}',vs,fs,(.68,.7,.72))
# Simple raised dark value lettering on the front face.
glyphs={'0':[[(0,0),(0,1.5),(.85,1.5),(.85,0),(0,0)]], '2':[[(0,1.5),(.85,1.5),(.85,.8),(0,.7),(0,0),(.85,0)]], 'R':[[(0,0),(0,1.5),(.85,1.5),(.85,.8),(0,.8)],[(.35,.8),(.85,0)]], '+':[[(0,.75),(.85,.75)],[(.425,.3),(.425,1.2)]]}
for ci,ch in enumerate('0R22 + 0R22'):
 for path in glyphs.get(ch,[]):
  for a,b in zip(path,path[1:]):
   x1,z1=a;x2,z2=b;dx=x2-x1;dz=z2-z1;length=math.hypot(dx,dz);nx=-dz/length*.055;nz=dx/length*.055
   ring=[(x1+nx,z1+nz),(x1-nx,z1-nz),(x2-nx,z2-nz),(x2+nx,z2+nz)]
   vs=[(x+ci*1.15-5.7,y,z+17) for y in [-2.525,-2.495] for x,z in ring]
   fs=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
   solid('Value ink',vs,fs,(.2,.22,.19))
rep=add(f"FACETED_BREP_SHAPE_REPRESENTATION('',{refs(items)},{gc})")
add(f"SHAPE_DEFINITION_REPRESENTATION({pds},{rep})")
add(f"MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',{refs(styles)},{gc})")
step=out/'YamahaSalvage.3dshapes'/f'{name}.step'
step.write_text("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('Dual emitter resistor'),'2;1');\nFILE_NAME('resistor.step','2026-10-15T22:00:00',(''),(''),'Codex','Codex','');\nFILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\nENDSEC;\nDATA;\n"+'\n'.join(f'#{i}={s};' for i,s in enumerate(E,1))+'\nENDSEC;\nEND-ISO-10303-21;\n')
fpname='R_Dual_Power_L31_W5_H18_P10'
s=(root/'YamahaSalvage.pretty'/f'{fpname}.kicad_mod').read_text()
model=f'\n(model "${{KIPRJMOD}}/YamahaSalvage.3dshapes/{name}.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n'
fp=s.rstrip()[:-1]+model+')\n';(out/'YamahaSalvage.pretty'/f'{fpname}.kicad_mod').write_text(fp)
board='(kicad_pcb (version 20241229) (generator "pcbnew") (general (thickness 1.6)) (paper "A4") (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "b.silkscreen") (37 "F.SilkS" user "f.silkscreen") (44 "Edge.Cuts" user) (47 "F.CrtYd" user "f.courtyard") (49 "F.Fab" user)) (setup (pad_to_mask_clearance 0)) '+fp.replace('${KIPRJMOD}',str(out))+' (gr_rect (start -18 -5) (end 18 5) (stroke (width .05) (type default)) (fill none) (layer "Edge.Cuts")))'
(root/'work/dual-resistor-3d/check.kicad_pcb').write_text(board)
print(step)
