import pcbnew as p,pathlib,json
w=pathlib.Path(__file__).resolve().parent;path=w/'review/BoostedClassD.kicad_pcb';b=p.LoadBoard(str(path));parts=json.loads((w/'parts.json').read_text())
for f in b.GetFootprints():
 r=f.GetReference()
 if r not in parts:continue
 d=parts[r];fields={'Description':'Unpolarized capacitor','Rating':d['value']+' / '+d['voltage']+' X5R','Manufacturer':'Samsung Electro-Mechanics','MPN':d['MPN'],'LCSC':d['LCSC'],'Datasheet':d['datasheet']}
 for k,v in fields.items():
  f.SetField(k,v);q=f.GetField(k);q.SetVisible(False);q.SetPosition(f.GetPosition())
p.SaveBoard(str(path),b);print('Fields synchronized')
