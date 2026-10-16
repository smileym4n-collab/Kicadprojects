from pathlib import Path
import math,json,hashlib
root=Path.cwd(); out=root/'output/L1-air-core'; name='L_AirCore_0u95H_P12_Horizontal'
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
  fs.append(add(f"FACE('',{refs([bound])})"))
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

def tube(label,path,r,color):
 vs=[]; n=16
 for j,p in enumerate(path):
  p0=path[max(0,j-1)];p1=path[min(len(path)-1,j+1)]
  t=[p1[k]-p0[k] for k in range(3)];l=math.sqrt(sum(v*v for v in t));t=[v/l for v in t]
  axis=[0,0,1] if abs(t[2])<.9 else [0,1,0]
  u=[t[1]*axis[2]-t[2]*axis[1],t[2]*axis[0]-t[0]*axis[2],t[0]*axis[1]-t[1]*axis[0]]
  l=math.sqrt(sum(v*v for v in u));u=[v/l for v in u]
  v=[t[1]*u[2]-t[2]*u[1],t[2]*u[0]-t[0]*u[2],t[0]*u[1]-t[1]*u[0]]
  for i in range(n):
   a=i*math.tau/n;vs.append(tuple(p[k]+r*(u[k]*math.cos(a)+v[k]*math.sin(a)) for k in range(3)))
 fs=[list(range(n-1,-1,-1)),list(range((len(path)-1)*n,len(path)*n))]
 for j in range(len(path)-1):
  for i in range(n):fs.append([j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i])
 solid(label,vs,fs,color)
copper=(.62,.25,.075);tin=(.7,.72,.74)
path=[(-6+12*j/720,5.8*math.sin(j*math.tau*10/720),7.3-5.8*math.cos(j*math.tau*10/720)) for j in range(721)]
tube('Enamelled copper winding - 10 illustrative turns',path,.55,copper)
for x in [-6,6]:
 tube('Formed copper lead',[(x,6,-.5),(x,6,.8),(x,5.7,1.5),(x,0,1.5)],.55,copper)
 tube('Tinned terminal',[(x,6,-3),(x,6,-.5)],.55,tin)
rep=add(f"FACETED_BREP_SHAPE_REPRESENTATION('',{refs(items)},{gc})")
add(f"SHAPE_DEFINITION_REPRESENTATION({pds},{rep})")
add(f"MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',{refs(styles)},{gc})")
step=out/'YamahaSalvage.3dshapes'/f'{name}.step'
step.write_text("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('Horizontal air core inductor'),'2;1');\nFILE_NAME('inductor.step','2026-10-15T22:00:00',(''),(''),'Codex','Codex','');\nFILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\nENDSEC;\nDATA;\n"+'\n'.join(f'#{i}={s};' for i,s in enumerate(E,1))+'\nENDSEC;\nEND-ISO-10303-21;\n')
fpname='L_Yamaha_L505_15x15mm_P12mm'
s=(root/'YamahaSalvage.pretty'/f'{fpname}.kicad_mod').read_text()
model=f'\n(model "${{KIPRJMOD}}/YamahaSalvage.3dshapes/{name}.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n'
fp=s.rstrip()[:-1]+model+')\n';(out/'YamahaSalvage.pretty'/f'{fpname}.kicad_mod').write_text(fp)
board='(kicad_pcb (version 20241229) (generator "pcbnew") (general (thickness 1.6)) (paper "A4") (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (36 "B.SilkS" user "b.silkscreen") (37 "F.SilkS" user "f.silkscreen") (44 "Edge.Cuts" user) (47 "F.CrtYd" user "f.courtyard") (49 "F.Fab" user)) (setup (pad_to_mask_clearance 0)) '+fp.replace('${KIPRJMOD}',str(out))+' (gr_rect (start -10 -10) (end 10 10) (stroke (width .05) (type default)) (fill none) (layer "Edge.Cuts")))'
(root/'work/L1-air-core/check.kicad_pcb').write_text(board)
print(step)
