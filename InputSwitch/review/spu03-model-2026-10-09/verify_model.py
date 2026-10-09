from pathlib import Path
import hashlib
import json
import pcbnew

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
MODEL = ROOT / 'InputSwitch.3dshapes/SPU03L-05.step'
paths = sorted(set(ROOT.glob('*.kicad_sch')) | set(ROOT.glob('*.kicad_pro')) |
               set(ROOT.glob('*.kicad_pcb')) | set((ROOT/'InputSwitch.pretty').glob('*.kicad_mod')))
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(OUT/'design-hashes-before.json').write_text(json.dumps(hashes, indent=2)+'\n')
assert (ROOT/'InputSwitch.kicad_pcb').read_bytes() == (OUT/'source/InputSwitch.kicad_pcb').read_bytes()

board = pcbnew.BOARD()
fp = pcbnew.FootprintLoad(str(ROOT/'InputSwitch.pretty'), 'SPU03L_05_SIP7')
assert fp
assert fp.Models().size() == 0
fp.SetReference('U1')
fp.SetValue('SPU03L-05')
fp.Reference().SetVisible(False)
fp.Value().SetVisible(False)
fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(6), pcbnew.FromMM(4)))
model = pcbnew.FP_3DMODEL()
model.m_Filename = str(MODEL)
fp.Add3DModel(model)
board.Add(fp)
pins = {str(p.GetNumber()): [round(pcbnew.ToMM(p.GetPosition().x-fp.GetPosition().x),8), round(pcbnew.ToMM(p.GetPosition().y-fp.GetPosition().y),8)] for p in fp.Pads()}
assert pins == {'1':[0,0], '2':[2.54,0], '5':[10.16,0], '7':[15.24,0]}
assert all(abs(pcbnew.ToMM(p.GetDrillSize().x)-0.9)<1e-8 for p in fp.Pads())
for a,b in [((1,1),(27,1)), ((27,1),(27,14)), ((27,14),(1,14)), ((1,14),(1,1))]:
    edge=pcbnew.PCB_SHAPE()
    edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
    edge.SetLayer(pcbnew.Edge_Cuts)
    edge.SetWidth(pcbnew.FromMM(0.05))
    edge.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(a[0]),pcbnew.FromMM(a[1])))
    edge.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(b[0]),pcbnew.FromMM(b[1])))
    board.Add(edge)
pcbnew.SaveBoard(str(OUT/'verify.kicad_pcb'),board)
(OUT/'footprint-validation.json').write_text(json.dumps({'KiCad':pcbnew.GetBuildVersion(),'pad_centres_mm':pins,'drills_mm':0.9},indent=2)+'\n')
print('Footprint pad centres and lead fit verified; isolated board saved.')
