"""Generate K4's project-local footprint without editing any PCB.

KiCad's installed G6K-2P-Y footprint places NC pins at 3.0 mm;
Omron's G6K-2P-Y drawing specifies 3.2 mm. Existing relays are untouched.
Run with KiCad's bundled Python.
"""
from pathlib import Path
import pcbnew as p

root = Path(__file__).resolve().parent.parent
f = p.FootprintLoad('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Relay_THT.pretty',
                    'Relay_DPDT_Omron_G6K-2P-Y')
name = 'Relay_DPDT_Omron_G6K-2P-Y_Datasheet'
f.SetFPID(p.LIB_ID('InputSwitch', name))
for pad in f.Pads():
    if pad.GetNumber() in ['2', '7']:
        v = pad.GetFPRelativePosition()
        pad.SetFPRelativePosition(p.VECTOR2I(v.x, p.FromMM(3.2)))
p.FootprintSave(str(root / 'InputSwitch.pretty'), f)
print('Saved project-local G6K footprint; no board was loaded or saved.')
