from pathlib import Path
from sexpr import parse,dump,children,child,Q
P=Path(__file__).resolve().parents[1]/'libraries/SubController.pretty'
def line(x1,y1,x2,y2,layer,w=.12):return f'(fp_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width {w}) (type default)) (layer "{layer}"))'
def rect(x,y,layer,w=.12):return line(-x,-y,x,-y,layer,w)+line(x,-y,x,y,layer,w)+line(x,y,-x,y,layer,w)+line(-x,y,-x,-y,layer,w)
def header(name,desc,attr):return f'(footprint "{name}" (version 20241229) (generator "pcbnew") (layer "F.Cu") (descr "{desc}") (attr {attr}) (property "Reference" "REF**" (at 0 -4.2 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)))) (property "Value" "{name}" (at 0 4.2 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15)))) '
name='SOP-8_uPC4570G2_4.4x5.2mm_P1.27mm'
s=header(name,'Renesas PLSP0008DE-A; body 4.4x5.2; span 6.5; pitch 1.27. Engineer land pattern, compare physical salvaged sample before layout.','smd')+rect(2.2,2.6,'F.Fab',.1)+rect(3.9,2.95,'F.CrtYd',.05)
s+=line(-2.2,-2.6,-1.45,-2.6,'F.SilkS')+line(-2.2,-2.6,-2.2,-2.0,'F.SilkS')
for num,x,y in [(i+1,-2.9,-1.905+i*1.27) for i in range(4)]+[(8-i,2.9,-1.905+i*1.27) for i in range(4)]:s+=f'(pad "{num}" smd roundrect (at {x} {y}) (size 1.5 0.65) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2))'
(P/(name+'.kicad_mod')).write_text(s+')\n')
name='Film_7.2x2.5mm_P5.00mm'
s=header(name,'Preferred 7.2x2.5mm film body. 5mm lead pitch PROVISIONAL; measure owned capacitors before layout.','through_hole')+rect(3.6,1.25,'F.Fab',.1)+rect(3.75,1.4,'F.SilkS')+rect(3.9,1.65,'F.CrtYd',.05)
for num,x in [(1,-2.5),(2,2.5)]:s+=f'(pad "{num}" thru_hole circle (at {x} 0) (size 1.5 1.5) (drill 0.8) (layers "*.Cu" "*.Mask"))'
(P/(name+'.kicad_mod')).write_text(s+')\n')
name='VOM617A_Verified'
s=header(name,'Vishay VOM617A 83446 rev1.4: body width4.4 length3.85 pitch2.54; recommended pads at +/-3.25, pad1.6x0.8.','smd')+rect(2.2,1.925,'F.Fab',.1)+rect(4.3,2.3,'F.CrtYd',.05)+line(-2.2,-2.05,2.2,-2.05,'F.SilkS')+line(-2.2,2.05,2.2,2.05,'F.SilkS')
for num,x,y in [(1,-3.25,-1.27),(2,-3.25,1.27),(3,3.25,1.27),(4,3.25,-1.27)]:s+=f'(pad "{num}" smd roundrect (at {x} {y}) (size 1.6 0.8) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2))'
(P/(name+'.kicad_mod')).write_text(s+')\n')
src=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Relay_THT.pretty/Relay_DPDT_Omron_G6K-2P-Y.kicad_mod')
d=parse(src.read_text());d[1]=Q('G6K-2P-Y_Verified')
for p in children(d,'pad'):
 if str(p[1]) in ['2','7']:child(p,'at')[2]='3.2'
 child(p,'drill')[1]='0.85'
for pr in children(d,'property'):
 if pr[1]=='Value':pr[2]=Q('G6K-2P-Y_Verified')
child(d,'descr')[1]=Q('Omron en-g6k p6 -Y drawing: contact rows 3.2,5.4,7.6; coil rows0; row separation5.08; drill0.85. Corrected stock library 3.0 spacing.')
(P/'G6K-2P-Y_Verified.kicad_mod').write_text(dump(d)+'\n')
# Bourns PTD90 rev04/24, pp2-3: recommended PCB pattern, shaft along +X.
# Origin is the mounting-surface/shaft centre projection. Manufacturer repeats
# terminal numbers in every gang; pad IDs retain section and terminal Rn.t.
name='PTD904_2015K_B203_Horizontal'
s=header(name,'Bourns PTD904-2015K-B203, PTD90 rev04/24 pp2-3. Top/component view: R1 nearest +X shaft; R1/R2/R3/R4 at X=-5/-7.5/-12.5/-15; terminal1/2/3 at Y=+2.5/0/-2.5. 12 holes, finished drill1.0. Shaft L15, knurled6mm; no board layout.','through_hole')
def box(x1,y1,x2,y2,layer,w=.12):return line(x1,y1,x2,y1,layer,w)+line(x2,y1,x2,y2,layer,w)+line(x2,y2,x1,y2,layer,w)+line(x1,y2,x1,y1,layer,w)
s+=box(-17.2,-4.75,0,4.75,'F.Fab',.1)+box(0,-4.75,.8,4.75,'F.Fab',.1)
s+=box(.8,-3.5,5,3.5,'F.Fab',.1)+box(5,-3,15,3,'F.Fab',.1)
s+=box(-17.45,-5.0,1.05,5.0,'F.SilkS')+box(-18,-5.55,15.75,5.55,'F.CrtYd',.05)
s+=line(0,-5.2,0,5.2,'Dwgs.User',.15)+line(-18,0,15.75,0,'Dwgs.User',.1)
for gang,x in [(1,-5),(2,-7.5),(3,-12.5),(4,-15)]:
 for term,y in [(1,2.5),(2,0),(3,-2.5)]:
  shape='rect' if term==1 else 'circle'
  s+=f'(pad "R{gang}.{term}" thru_hole {shape} (at {x} {y}) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask"))'
 s+=f'(fp_text user "R{gang}" (at {x} -4.05) (layer "F.Fab") (effects (font (size .65 .65) (thickness .1))))'
s+='(fp_text user "MOUNTING SURFACE" (at 0 -7) (layer "Dwgs.User") (effects (font (size .8 .8) (thickness .12))))'
s+='(fp_text user "CW: HIGHER Hz" (at 7.5 7) (layer "Dwgs.User") (effects (font (size .8 .8) (thickness .12))))'
# Keep reference/value clear of the complete body and shaft envelope.
sd=parse(s+')')
for pr in children(sd,'property'):
 if pr[1]=='Reference':child(pr,'at')[1:3]=['-8.6','-6.5']
 if pr[1]=='Value':child(pr,'at')[1:3]=['-8.6','6.5']
(P/(name+'.kicad_mod')).write_text(dump(sd)+'\n')
from tps7a3901 import build_footprint
build_footprint(P/'TPS7A3901_DSC0010J_WSON10.kicad_mod')
print('Created six local footprints; no board layout performed.')
