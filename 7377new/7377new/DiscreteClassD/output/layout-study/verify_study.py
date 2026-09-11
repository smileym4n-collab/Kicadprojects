from pathlib import Path
import sys,json,hashlib,math
import pcbnew as p
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/layout-study'
sys.path.insert(0,str(ROOT/'scripts'))
from sexp import parse,get,allof,prop
src=OUT/'production-source-snapshot.kicad_pcb';study=ROOT/'DiscreteClassD-layout-study.kicad_pcb'
def canonical(path,name):
 b=p.LoadBoard(str(path))
 for f in b.GetFootprints():f.SetOrientationDegrees(0);f.SetPosition(p.VECTOR2I(0,0))
 temp=OUT/name;p.SaveBoard(str(temp),b)
 tree=parse(temp.read_text());temp.unlink()
 def normal(a):
  if isinstance(a,list):return [normal(v) for v in a]
  try:return round(float(a),5)
  except (TypeError,ValueError):return str(a)
 return {prop(f,'Reference')[2]:normal([v for v in f if isinstance(v,list) and v[0] in ('pad','fp_line','fp_arc','fp_rect','fp_circle','fp_poly','model','attr')]) for f in allof(tree,'footprint')}
original=canonical(src,'normalize-source.tmp.kicad_pcb');final=canonical(study,'normalize-study.tmp.kicad_pcb')
assert original==final, 'Pad or physical footprint geometry changed'
s=parse(src.read_text());t=parse(study.read_text())
edges=lambda tree:[v for v in tree if isinstance(v,list) and get(v,'layer')==['layer','Edge.Cuts']]
assert edges(s)==edges(t),'Outline changed'
assert get(s,'layers')==get(t,'layers'),'Layer configuration changed'
assert get(s,'setup')==get(t,'setup'),'PCB setup changed'
assert not any(allof(t,k) for k in ['segment','arc','via','zone'])
initial=json.loads((OUT/'source-hashes.json').read_text())
assert hashlib.sha256((ROOT/'DiscreteClassD.kicad_pcb').read_bytes()).hexdigest()==initial['DiscreteClassD.kicad_pcb']
for path in ['DiscreteClassD.kicad_pro','DiscreteClassD.kicad_sym','fp-lib-table','sym-lib-table','AGENTS.md']:
 assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==initial[path],path
dr=json.loads((OUT/'study-drc.json').read_text())
bad=[v for v in dr['violations'] if v['type'] in ('courtyards_overlap','shorting_items','copper_edge_clearance')]
assert not bad,bad
result={'production_pcb_sha256':initial['DiscreteClassD.kicad_pcb'],'study_sha256':hashlib.sha256(study.read_bytes()).hexdigest(),
 'production_pcb_unchanged':True,'production_project_and_libraries_unchanged':True,
 'footprints_preserved':len(original),'physical_footprint_geometry_and_pad_nets_preserved':True,
 'outline_layers_setup_preserved':True,'study_tracks_vias_zones':0,
 'no_courtyard_overlap_or_interfootprint_short_or_edge_clearance_errors':True,
 'schematic_files_saved_externally_during_task':json.loads((OUT/'external-file-changes.json').read_text())}
(OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
