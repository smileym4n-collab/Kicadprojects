from pathlib import Path
import hashlib,json
root=Path.cwd()
name='R_Dual_0R22_Yamaha'
fp='R_Dual_Power_L31_W5_H18_P10'
tracked=['DarlingtonAmp.kicad_sch','DarlingtonAmp.kicad_pcb','DarlingtonAmp.kicad_pro','DarlingtonAmp.kicad_sym']
(root/'work/dual-resistor/before-hashes.json').write_text(json.dumps({f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in tracked},indent=2))
# Executed after body dimensions and centre-common mapping are confirmed.
props=''
for key,value,y,hide in [('Reference','R',3.81,False),('Value','0R22 + 0R22',-3.81,False),('Footprint',f'YamahaSalvage:{fp}',0,True),('Datasheet','',0,True),('Description','Salvaged dual emitter resistor; pins 1-2 and 2-3; pin 2 common. Power rating per section TBC.',0,True)]:
 props+=f'(property "{key}" "{value}" (at 0 {y} 0) (effects (font (size 1.27 1.27))'+(' (hide yes)' if hide else '')+'))\n'
graphics=''
for x1,x2 in [(-6.35,-1.27),(1.27,6.35)]:
 graphics+=f'(rectangle (start {x1} 1.016) (end {x2} -1.016) (stroke (width 0.254) (type default)) (fill (type none)))\n'
for pts in ['(xy -1.27 0) (xy 1.27 0)','(xy 0 0) (xy 0 -2.54)']:
 graphics+=f'(polyline (pts {pts}) (stroke (width 0.254) (type default)) (fill (type none)))\n'
graphics+='(circle (center 0 0) (radius 0.25) (stroke (width 0) (type default)) (fill (type outline)))'
pins=''
for num,x,y,angle,label in [(1,-8.89,0,0,'A'),(2,0,-5.08,90,'COM'),(3,8.89,0,180,'B')]:
 pins+=f'(pin passive line (at {x} {y} {angle}) (length 2.54) (name "{label}" (effects (font (size 1 1)))) (number "{num}" (effects (font (size 1 1)))))\n'
sym=f'(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") (symbol "{name}" (pin_names (offset 0) (hide yes)) (in_bom yes) (on_board yes) {props} (symbol "{name}_0_1" {graphics}) (symbol "{name}_1_1" {pins})))\n'
(root/'YamahaSalvage.kicad_sym').write_text(sym)
lib=root/'YamahaSalvage.pretty';lib.mkdir(exist_ok=True)
foot=f'(footprint "{fp}" (version 20241229) (generator "pcbnew") (layer "F.Cu") (descr "Dual resistor, body 31x5x18 mm, adjacent pitch 10 mm; centre common; 1 mm leads") (tags "Yamaha dual emitter resistor") (attr through_hole)\n'
for key,val,y,layer in [('Reference','REF**',-4,'F.SilkS'),('Value',fp,4,'F.Fab')]:
 foot+=f'(property "{key}" "{val}" (at 0 {y} 0) (layer "{layer}") (effects (font (size 1 1) (thickness 0.15))))\n'
for layer,x,y,width in [('F.Fab',15.5,2.5,.1),('F.SilkS',15.65,2.65,.12),('F.CrtYd',16,3,.05)]:
 foot+=f'(fp_rect (start {-x} {-y}) (end {x} {y}) (stroke (width {width}) (type default)) (fill none) (layer "{layer}"))\n'
foot+='(fp_text user "${REFERENCE}" (at 0 1.8) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.1))))\n'
foot+='(fp_circle (center -10 -1.8) (end -9.7 -1.8) (stroke (width 0.12) (type default)) (fill none) (layer "F.SilkS"))\n'
for n,x in [(1,-10),(2,0),(3,10)]:
 foot+=f'(pad "{n}" thru_hole '+('rect' if n==1 else 'circle')+f' (at {x} 0) (size 2.8 2.8) (drill 1.3) (layers "*.Cu" "*.Mask"))\n'
foot+=')\n';(lib/f'{fp}.kicad_mod').write_text(foot)
