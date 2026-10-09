from schlib import *
from collections import defaultdict
import xml.etree.ElementTree as E,json
ROOT=Path(__file__).resolve().parent.parent
r=E.parse(ROOT/'review/final-netlist.xml').getroot();pins=defaultdict(set)
for n in r.findall('nets/net'):
 for p in n.findall('node'):pins[p.attrib['ref']].add(p.attrib['pin'])
results=[]
for c in r.findall('components/comp'):
 ref=c.attrib['ref'];f=c.findtext('footprint');group,name=f.split(':')
 path=(ROOT/'InputSwitch.pretty' if group=='InputSwitch' else Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')/(group+'.pretty'))/(name+'.kicad_mod')
 assert path.exists(),(ref,path)
 m=parse(path.read_text());padnums={str(p[1]) for p in kids(m,'pad') if str(p[1])}
 assert pins[ref]<=padnums,(ref,pins[ref],padnums)
 # No numbered footprint pad may silently be omitted from the schematic.
 assert padnums<=pins[ref],(ref,'extra pad',padnums-pins[ref])
 results.append({'reference':ref,'footprint':f,'numbered_pads':sorted(padnums),'status':'pad-number parity checked; dimensional assembly review still required'})
(ROOT/'review/footprint-pad-checks.json').write_text(json.dumps(results,indent=2)+'\n')
print(len(results),'component footprint references resolved; complete pad-number parity passed.')
