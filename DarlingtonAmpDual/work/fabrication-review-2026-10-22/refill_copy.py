import pcbnew,wx
from pathlib import Path
app=wx.App(False)
b=pcbnew.LoadBoard('DarlingtonAmpDual.kicad_pcb')
b.BuildConnectivity()
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
p=Path('work/fabrication-review-2026-10-22/refilled-copy');p.mkdir(exist_ok=True)
pcbnew.SaveBoard(str(p/'DarlingtonAmpDual.kicad_pcb'),b)
print('Refilled isolated review copy; production board unchanged')
