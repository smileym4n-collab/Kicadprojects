"""Build a simplified, dimensioned ATS heatsink STEP and KiCad footprint.

No CAD kernel dependency. Planar BREP with 48-sided smooth-bore approximations.
Overall dimensions/underside machining follow ATS sheet and TI SLOS942 Fig.39.
Undimensioned fin thickness/base thickness and thread details are documented.
"""
from pathlib import Path
import math, json, sys, copy

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'review/scripts'))
from schlib import load, save, get, many, prop, S, dump

NAME = 'Heatsink_ATS_ATS-TI1OP-521-C1-R1_50x13.9mm_H25mm_P40mm'
MODEL = 'ATS-TI1OP-521-C1-R1'
E, items, styles, solids = [], [], [], []
def add(s):
    E.append(s); return '#'+str(len(E))
def refs(xs): return '('+','.join(xs)+')'
def point(p): return add("CARTESIAN_POINT('',("+','.join(f'{x:.9f}' for x in p)+'))')
ctx=add("APPLICATION_CONTEXT('automotive_design')")
add(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,{ctx})")
pc=add(f"PRODUCT_CONTEXT('',{ctx},'mechanical')")
p=add(f"PRODUCT('{MODEL}','{MODEL}','Simplified mechanical reference model',{refs([pc])})")
pf=add(f"PRODUCT_DEFINITION_FORMATION('','',{p})")
dc=add(f"PRODUCT_DEFINITION_CONTEXT('part definition',{ctx},'design')")
pd=add(f"PRODUCT_DEFINITION('design','',{pf},{dc})")
pds=add(f"PRODUCT_DEFINITION_SHAPE('','',{pd})")
unit=add('(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))')
ang=add('(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))')
sa=add('(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())')
unc=add(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.000001),{unit},'distance_accuracy_value','')")
gc=add(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT({refs([unc])})GLOBAL_UNIT_ASSIGNED_CONTEXT({refs([unit,ang,sa])})REPRESENTATION_CONTEXT('',''))")

def style(item, rgb):
    col=add("COLOUR_RGB('',"+','.join(map(str,rgb))+')')
    fill=add(f"FILL_AREA_STYLE_COLOUR('',{col})")
    fas=add(f"FILL_AREA_STYLE('',{refs([fill])})")
    ss=add(f'SURFACE_STYLE_FILL_AREA({fas})')
    side=add(f"SURFACE_SIDE_STYLE('',{refs([ss])})")
    use=add(f'SURFACE_STYLE_USAGE(.BOTH.,{side})')
    ass=add(f'PRESENTATION_STYLE_ASSIGNMENT({refs([use])})')
    styles.append(add(f"STYLED_ITEM('',{refs([ass])},{item})"))

def solid(label, verts, faces):
    """Faces are outer-loop indices, or (outer-loop, [inner-loops])."""
    # Every edge must occur twice in opposite directions in a closed oriented shell.
    directed={}
    volume=0.0
    for face in faces:
        outer, holes=face if isinstance(face,tuple) else (face,[])
        for loop in [outer]+holes:
            for a,b in zip(loop,loop[1:]+loop[:1]):
                directed[(a,b)]=directed.get((a,b),0)+1
            a=verts[loop[0]]
            for i in range(1,len(loop)-1):
                b,c=verts[loop[i]],verts[loop[i+1]]
                volume += (a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    assert all(count==1 and directed.get((b,a))==1 for (a,b),count in directed.items()),label
    assert volume>0,label
    pts=[point(v) for v in verts]; fs=[]
    for face in faces:
        outer, holes = face if isinstance(face,tuple) else (face,[])
        bounds=[]
        for i, loop in enumerate([outer]+holes):
            lo=add(f"POLY_LOOP('',{refs([pts[j] for j in loop])})")
            typ='FACE_OUTER_BOUND' if i==0 else 'FACE_BOUND'
            bounds.append(add(f"{typ}('',{lo},.T.)"))
        a,b,c=[verts[i] for i in outer[:3]]
        v=[b[i]-a[i] for i in range(3)]; w=[c[i]-b[i] for i in range(3)]
        n=[v[1]*w[2]-v[2]*w[1],v[2]*w[0]-v[0]*w[2],v[0]*w[1]-v[1]*w[0]]
        ln=math.sqrt(sum(x*x for x in n)); lv=math.sqrt(sum(x*x for x in v))
        assert ln>1e-12
        normal=add("DIRECTION('',("+','.join(str(x/ln) for x in n)+'))')
        direction=add("DIRECTION('',("+','.join(str(x/lv) for x in v)+'))')
        axis=add(f"AXIS2_PLACEMENT_3D('',{pts[outer[0]]},{normal},{direction})")
        plane=add(f"PLANE('',{axis})")
        fs.append(add(f"FACE_SURFACE('',{refs(bounds)},{plane},.T.)"))
    shell=add(f"CLOSED_SHELL('',{refs(fs)})")
    item=add(f"FACETED_BREP('{label}',{shell})")
    items.append(item); style(item,(0.075,0.08,0.085))
    solids.append({'name':label,'vertices':verts,'faces':len(faces),'closed_oriented_shell':True,'volume_mm3':volume})

def prism(label,x0,x1,w0,w1,z0,z1,hole=None):
    """Rectangular/trapezoidal prism; optional bottom-opening blind/through bore."""
    verts=[(x0,-w0/2,z0),(x1,-w0/2,z0),(x1,w0/2,z0),(x0,w0/2,z0),
           (x0,-w1/2,z1),(x1,-w1/2,z1),(x1,w1/2,z1),(x0,w1/2,z1)]
    faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
    if hole:
        hx,hy,hz=hole; count=48; radius=2.845/2
        for z in [z0,hz]:
            verts.extend((hx+radius*math.cos(i*math.tau/count),hy+radius*math.sin(i*math.tau/count),z) for i in range(count))
        lower=list(range(8,8+count)); upper=list(range(8+count,8+2*count))
        faces[0]=(faces[0],[lower])
        if abs(hz-z1)<1e-9: faces[1]=(faces[1],[upper[::-1]])
        else: faces.append(upper[::-1])  # ceiling of blind bore, facing down
        for i in range(count):
            j=(i+1)%count; faces.append([lower[i],upper[i],upper[j],lower[j]])
    solid(label,verts,faces)

# Lowest end mounting faces define Z=0. Long axis X; width Y; height Z.
# Three platform segments make the blind bores possible without a CAD boolean kernel.
prism('Base_left_with_blind_4-40_bore',-25,-15,13.9,13.9,3,7,(-20,0,6.5))
prism('Base_centre',-15,15,13.9,13.9,3,7)
prism('Base_right_with_blind_4-40_bore',15,25,13.9,13.9,3,7,(20,0,6.5))
# End trapezoids and central machined contact land. Shoulder width 9.525 is illustrative.
prism('End_mounting_foot_left',-25,-15,6.35,9.525,0,3,(-20,0,3))
prism('End_mounting_foot_right',15,25,6.35,9.525,0,3,(20,0,3))
prism('Central_contact_land',-5.5,5.5,6.35+(9.525-6.35)/3,9.525,1,3)
# Fins: 2 mm thickness and root Z=7 are illustrative, not dimensioned by ATS.
for label,y0,y1 in [('Fin_1',-6.95,-4.95),('Fin_2',-1,1),('Fin_3',4.95,6.95)]:
    verts=[(-25,y0,7),(25,y0,7),(25,y1,7),(-25,y1,7),(-25,y0,25),(25,y0,25),(25,y1,25),(-25,y1,25)]
    solid(label,verts,[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])

rep=add(f"FACETED_BREP_SHAPE_REPRESENTATION('',{refs(items)},{gc})")
add(f'SHAPE_DEFINITION_REPRESENTATION({pds},{rep})')
add(f"MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',{refs(styles)},{gc})")
step=ROOT/'TPA3126.3dshapes'/f'{MODEL}.step'
step.write_text("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('ATS heatsink simplified reference geometry'),'2;1');\nFILE_NAME('ATS-TI1OP-521-C1-R1.step','2026-10-19T20:00:00',(''),(''),'Codex','Codex','');\nFILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\nENDSEC;\nDATA;\n"+'\n'.join(f'#{i}={s};' for i,s in enumerate(E,1))+'\nENDSEC;\nEND-ISO-10303-21;\n')

fp=f'''(footprint "{NAME}"
 (version 20260206) (generator "pcbnew") (layer "F.Cu")
 (descr "ATS-TI1OP-521-C1-R1; nominal 50 x 13.9 x 25 mm; two #4-40 mounting axes 40 mm apart. 3.2 mm NPTH board clearance selected for #4 screws. Stepped underside; full-body guide is manual, only mounting feet have courtyards. Origin geometric centre; long axis X. Verify physical part and thermal contact stack.")
 (tags "ATS TPA3126 TPA3116 heatsink top PowerPAD 4-40 P40")
 (property "Reference" "HS1" (at 0 -8.7 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
 (property "Value" "ATS-TI1OP-521-C1-R1" (at 0 8.7 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
 (attr exclude_from_pos_files)
 (fp_rect (start -25 -6.95) (end 25 6.95) (stroke (width 0.15) (type default)) (fill none) (layer "F.Fab"))
 (fp_rect (start -26.5 -8.45) (end 26.5 8.45) (stroke (width 0.1) (type dash)) (fill none) (layer "Dwgs.User"))
 (fp_rect (start -25.5 -7.65) (end -14.5 7.65) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
 (fp_rect (start 14.5 -7.65) (end 25.5 7.65) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
 (fp_rect (start -25 -4.7625) (end -15 4.7625) (stroke (width 0.12) (type default)) (fill none) (layer "Cmts.User"))
 (fp_rect (start 15 -4.7625) (end 25 4.7625) (stroke (width 0.12) (type default)) (fill none) (layer "Cmts.User"))
 (fp_rect (start -5.5 -4.7625) (end 5.5 4.7625) (stroke (width 0.12) (type dash)) (fill none) (layer "Cmts.User"))
 (fp_line (start -1 0) (end 1 0) (stroke (width 0.1) (type default)) (layer "Dwgs.User"))
 (fp_line (start 0 -1) (end 0 1) (stroke (width 0.1) (type default)) (layer "Dwgs.User"))
 (fp_text user "50 x 13.9 mm / H25; 40 mm screw pitch" (at 0 -10.4 0) (layer "Dwgs.User") (effects (font (size 0.8 0.8) (thickness 0.12))))
 (fp_text user "END FEET Z0 / CONTACT Z1 / RELIEF Z3 - CHECK STACK" (at 0 10.4 0) (layer "Dwgs.User") (effects (font (size 0.7 0.7) (thickness 0.1))))
 (pad "" np_thru_hole circle (at -20 0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))
 (pad "" np_thru_hole circle (at 20 0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask"))
 (model "${{KIPRJMOD}}/TPA3126.3dshapes/{MODEL}.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))
)'''
fpath=ROOT/'TPA3126.pretty'/f'{NAME}.kicad_mod'
fpath.write_text(fp+'\n')

verts=[v for s in solids for v in s['vertices']]
bb=[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]
assert bb==[[-25,25],[-6.95,6.95],[0,25]]
metadata={'model_envelope_mm':[50,13.9,25],'model_bounds_mm':bb,'geometric_subsolids':len(solids),'screw_axes_mm':[[-20,0],[20,0]],'thread':'#4-40','model_bore_diameter_mm':2.845,'thread_depth_mm':6.5,'PCB_NPTH_diameter_mm':3.2,'end_feet_bottom_z_mm':0,'central_contact_bottom_z_mm':1,'relieved_underside_z_mm':3,'base_fin_root_z_mm_illustrative':7,'fin_thickness_mm_illustrative':2,'taper_shoulder_width_mm_illustrative':9.525,'central_land_length_mm':11,'finish':'black anodised; machined-face colour not separately modeled','limitations':['No thread helix; smooth major-diameter blind bores','Fin-root fillets omitted','Model is nine touching geometric subsolids representing one physical extrusion','Fin thickness/root height/shoulder width are illustrative; overall envelope and published machining coordinates are retained','Verify interface/preload/actual mounting stack before ordering a PCB']}
(OUT/'geometry.json').write_text(json.dumps(metadata,indent=2)+'\n')
(OUT/'shell-topology.json').write_text(json.dumps([{k:v for k,v in s.items() if k!='vertices'} for s in solids],indent=2)+'\n')

# Isolated validation fixture, never the production board. Model paths resolved explicitly.
if (ROOT/'TPA3126.kicad_pcb').exists():
    fpnode=load(fpath); fpnode[1]='Custom:'+NAME; fpnode.insert(4,[S('at'),S('40'),S('25')])
    get(fpnode,'model')[1]=str(step)
    board=load(ROOT/'TPA3126.kicad_pcb')
    layers=copy.deepcopy(get(board,'layers'))
    parts=[fpnode]
    for ref,pos in [('U1',(40,25)),('C24',(47.0145,20.521)),('C25',(47.0145,23.569)),('C26',(47.0145,25.855)),('C27',(47.0145,28.649))]:
        orig=next(f for f in many(board,'footprint') if prop(f,'Reference')[2]==ref)
        f=copy.deepcopy(orig); get(f,'at')[1:]=[S(str(x)) for x in pos]
        for pad in many(f,'pad'):
            net=get(pad,'net')
            if net:pad.remove(net)
        parts.append(f)
    fixture='(kicad_pcb (version 20241229) (generator "pcbnew") (general (thickness 1.6)) (paper "A4") '+dump(layers)+' (setup (pad_to_mask_clearance 0)) '+''.join(dump(f) for f in parts)+' (gr_rect (start 5 10) (end 75 40) (stroke (width .05) (type default)) (fill none) (layer "Edge.Cuts")))'
    (OUT/'validation-fixture.kicad_pcb').write_text(fixture+'\n')
print('Generated',fpath,step,flush=True)
print(json.dumps(metadata,indent=2),flush=True)
