import re,json,zipfile,shutil
from pathlib import Path
root=Path.cwd();out=root/'output/dual-emitter-resistor'
def parse(text):
 tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text); stack=[];top=[]
 for t in tokens:
  if t=='(':
   x=[]
   if stack:stack[-1].append(x)
   else:top.append(x)
   stack.append(x)
  elif t==')':stack.pop()
  else:stack[-1].append(t.strip('"'))
 return top[0]
def child(x,key):return [a for a in x if isinstance(a,list) and a and a[0]==key]
def check(path,refs):
 b=parse(path.read_text()); result={}
 for fp in child(b,'footprint'):
  properties=child(fp,'property');ref=next((p[2] for p in properties if p[1]=='Reference'),None)
  if ref not in refs:continue
  pads={p[1]:[float(v) for v in child(p,'at')[0][1:3]] for p in child(fp,'pad')}
  assert pads=={'1':[-10.,0.],'2':[0.,0.],'3':[10.,0.]},pads
  result[ref]={'footprint':fp[1],'pad_centres_mm':pads}
 assert set(result)==set(refs)
 return result
report={'DarlingtonAmp':check(root/'DarlingtonAmp.kicad_pcb',['R1']),'DarlingtonAmpDual':check(root.parent/'DarlingtonAmpDual/DarlingtonAmpDual.kicad_pcb',['R1','R23']),'body_mm':[31,5,18],'body_clearance_mm_assumed':3,'lead_diameter_mm':1,'KiCad_render':'Passed and visually inspected','KiCad_STEP_roundtrip':'Passed; output 739 kB including component solids','geometry':'Faceted STEP with planar surfaces; 32-sided lead sections','production_files_modified':False}
(out/'validation.json').write_text(json.dumps(report,indent=2))
shutil.copy(root/'work/dual-resistor-3d/build_faceted.py',out/'build_model.py')
p=out/'README.md';s=p.read_text().replace('rounded ceramic casing','chamfered ceramic casing');s+='\n## Validation\n\nPad centres were checked against the saved R1 and R23 instances in DarlingtonAmpDual and R1 in DarlingtonAmp. KiCad 10 imported and rendered the STEP successfully; the final image was visually inspected. A STEP export of the isolated test assembly also retained the component solids. The model uses faceted planar surfaces with 32-sided lead sections. This verifies CAD placement, not real-part fit or thermal suitability.\n';p.write_text(s)
with zipfile.ZipFile(root/'output/Dual-0R22-resistor-KiCad.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in out.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(out))
print(json.dumps(report,indent=2))
