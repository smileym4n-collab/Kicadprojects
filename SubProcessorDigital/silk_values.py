# Footprint text standard: reference hidden, value on silkscreen 0.5 x 0.5 mm, 0.0625 mm thick.
# Run in the PCB editor's scripting console (Tools > Scripting Console):
#   exec(open('/Users/tomwatson/Documents/GitHub/Kicadprojects/SubProcessorDigital/silk_values.py').read())
# Ctrl+Z undoes it.
import pcbnew

b = pcbnew.GetBoard()
mm = pcbnew.FromMM
for fp in b.GetFootprints():
    r, v = fp.Reference(), fp.Value()
    r.SetVisible(False)
    v.SetVisible(True)
    v.SetLayer(pcbnew.B_SilkS if fp.IsFlipped() else pcbnew.F_SilkS)
    v.SetTextSize(pcbnew.VECTOR2I(mm(0.5), mm(0.5)))
    v.SetTextThickness(mm(0.0625))
pcbnew.Refresh()
