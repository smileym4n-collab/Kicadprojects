from pathlib import Path
import hashlib,json
root=Path.cwd()
tracked=['DarlingtonAmp.kicad_sch','DarlingtonAmp.kicad_pcb','DarlingtonAmp.kicad_pro','YamahaSalvage.kicad_sym','fp-lib-table','sym-lib-table']
before={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in tracked}
name='L_Yamaha_L505_15x15mm_P12mm'
s=f'''(footprint "{name}" (version 20241229) (generator "pcbnew")
(layer "F.Cu")
(descr "Salvaged Yamaha L505; body 15x15 mm; round leads 2 mm; pitch 12 mm. Pin-to-near-edge setback assumed 1.5 mm: verify physical part.")
(tags "Yamaha L505 output inductor salvage")
(attr through_hole)
(property "Reference" "REF**" (at 0 -10 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
(property "Value" "{name}" (at 0 9 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
(fp_rect (start -7.5 -7.5) (end 7.5 7.5) (stroke (width 0.1) (type default)) (fill none) (layer "F.Fab"))
(fp_rect (start -8.5 -8.5) (end 8.5 8.5) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))
(fp_text user "${{REFERENCE}}" (at 0 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
(fp_text user "EDGE SETBACK TBC" (at 0 3) (layer "Dwgs.User") (effects (font (size 0.8 0.8) (thickness 0.12))))
'''
# Silkscreen opened around pads; body outline intact on fabrication layer.
for a,b in [((-3.5,-7.65),(3.5,-7.65)),((-7.65,-3.5),(-7.65,7.65)),((7.65,-3.5),(7.65,7.65)),((-7.65,7.65),(7.65,7.65))]:
 s+=f'(fp_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width 0.12) (type default)) (layer "F.SilkS"))\n'
for n,x in [(1,-6),(2,6)]:
 s+=f'(pad "{n}" thru_hole '+('rect' if n==1 else 'circle')+f' (at {x} -6) (size 3.8 3.8) (drill 2.3) (layers "*.Cu" "*.Mask"))\n'
s+=')\n'
p=root/'YamahaSalvage.pretty'/f'{name}.kicad_mod';p.write_text(s)
assert s.count('(drill 2.3)')==2
assert s.count('(size 3.8 3.8)')==2
for f,h in before.items():assert hashlib.sha256((root/f).read_bytes()).hexdigest()==h,f
(root/'work/L505/README.md').write_text('''# Yamaha L505 footprint\n\nLibrary ID: YamahaSalvage:L_Yamaha_L505_15x15mm_P12mm\n\nOwner measurements: body 15 x 15 mm, pin pitch 12 mm, round lead diameter 2 mm. Finished plated holes 2.3 mm, pads 3.8 mm (0.75 mm nominal annular ring). Pin centres at (-6,-6) and (6,-6) relative to body centre. Nonpolar component.\n\nIMPORTANT: Pin-centre distance from nearest body edge was not supplied. This footprint assumes 1.5 mm; confirm or correct before fabrication. Print at 1:1 and physically fit the part. No component height or 3D model supplied.\n\nOriginal schematic, PCB, project and library tables unchanged. Assign this footprint to the ordinary two-pin inductor symbol when ready; it has not been assigned automatically.\n''')
print('Created',p)
print('Protected file hashes unchanged; hole and pad assertions passed.')
