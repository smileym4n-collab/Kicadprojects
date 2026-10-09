"""Scoped conversion of the saved 2026-10-06 schematic; preserves existing UUIDs/placement."""
from pathlib import Path
import re,json,uuid,copy
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'review/before-single-supply/ClassA.kicad_sch'
class Atom(str):
 def __new__(cls,s,quoted=False):o=super().__new__(cls,s);o.quoted=quoted;return o
def parse(s):
 tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s);i=0
 def read():
  nonlocal i
  t=tokens[i];i+=1
  if t=='(':
   out=[]
   while tokens[i]!=')':out.append(read())
   i+=1;return out
  return Atom(json.loads(t),True) if t.startswith('"') else Atom(t)
 return read()
def dump(x):
 if isinstance(x,list):return '('+' '.join(dump(v) for v in x)+')'
 return json.dumps(str(x)) if getattr(x,'quoted',False) else str(x)
def kids(s,k):return [x for x in s if isinstance(x,list) and x and x[0]==k]
def fld(s,k):return kids(s,k)[0]
def coord(s):return tuple(round(float(x),4) for x in fld(s,'at')[1:3])
def prop(s,k):return next(x for x in kids(s,'property') if x[1]==k)
def val(s,k,v):prop(s,k)[2]=Atom(v,True)
def U():return str(uuid.uuid4())
ns={'__file__':str(ROOT/'scripts/build_schematic.py')};exec((ROOT/'scripts/build_schematic.py').read_text().split("text('MONO SINGLE-ENDED")[0],ns)
ns['ng']=20;ns['nf']=10;ns['nt']=15
sch=parse(SOURCE.read_text());new=[]
def take():
 for s in ns['parts']+ns['elements']:new.append(parse(s))
 ns['parts'].clear();ns['elements'].clear()
def lab(name,xy):ns['label'](name,(xy[0]/2.54,xy[1]/2.54));take()
def ground(xy):ns['ground']((xy[0]/2.54,xy[1]/2.54));take()
def wire(a,b):ns['wire']((a[0]/2.54,a[1]/2.54),(b[0]/2.54,b[1]/2.54));take()
def node(s):return [(float(p[1]),float(p[2])) for p in fld(s,'pts')[1:]]
removed=set(); changed=[]
# Actual ground and supply translation; sensitive returns become VREF, not power GND.
ref_returns={(96.52,152.4),(78.74,259.08),(152.4,355.6),(182.88,355.6)}
for item in sch[1:]:
 if not isinstance(item,list):continue
 kind=item[0]
 if kind=='symbol':
  ref=str(prop(item,'Reference')[2])
  if ref=='R2' or ref=='#FLG003':removed.add(id(item));continue
  if coord(item) in ref_returns and prop(item,'Value')[2]=='GND':
   lab('VREF_20V',coord(item));removed.add(id(item));continue
  changes={'C6':'470u / 63V','C7':'100n / 63V','C8':'1000u / 50V REF','C9':'100n / 63V REF','C4':'470u / 50V BP','R10':'18k / 0.25W','TP13':'+40V','TP10':'SINK_GND_REF','J3':'40V / GND'}
  if ref in changes:val(item,'Value',changes[ref]);changed.append(ref)
  if ref=='J3':
   fld(item,'lib_id')[1]=Atom('Connector_Generic:Conn_01x02',True);fld(item,'at')[2]=Atom('360.68')
   for pin in kids(item,'pin'):
    if pin[1]=='3':item.remove(pin)
  # R2 is removed: input must remain AC coupled with a ground-referenced source.
 elif kind=='label':
  if coord(item)==(58.42,388.62):removed.add(id(item));continue
  if item[1]=='+20V':item[1]=Atom('+40V',True)
  elif item[1]=='-20V':ground(coord(item));removed.add(id(item))
 elif kind=='wire':
  pts=node(item)
  # Delete only the obsolete DC input bypass and third supply pin wires.
  if any(109.21<=y<=109.23 for x,y in pts):removed.add(id(item))
  elif any(abs(x-38.1)<.001 and abs(y-365.76)<.001 for x,y in pts) or (all(abs(x-58.42)<.001 for x,y in pts) and any(abs(y-388.62)<.001 for x,y in pts)):
   removed.add(id(item))
 elif kind=='text':
  t=str(item[1])
  if 'FIRST-PASS SCHEMATIC' in t:t=t.replace('FIRST-PASS SCHEMATIC','40 V SINGLE SUPPLY / CAP-COUPLED')
  t=t.replace('EXTERNAL SPLIT SUPPLY','EXTERNAL 40 V SUPPLY').replace('negative rail','GND')
  t=t.replace('Warm offset <50 mV is a target, not verified. Test startup/shutdown DC,','AMP_OUT ~20 V DC; speaker output AC coupled. Test capacitor charging,')
  t=t.replace('Join at J3 GND/local capacitor star. No ground-plane split implied. PSU reservoirs external.','Join at J3 GND/local capacitor star. VREF is a quiet signal reference, not a power return.')
  item[1]=Atom(t,True)
# Current-mirror reference transistor must have collector tied to its common base net.
wire((170.18,154.94),(170.18,165.1))
new.append(parse(f'(junction (at 170.18 154.94) (diameter 0) (color 0 0 0 0) (uuid {U()}))'))
# C10 between output inductor/damping network and loudspeaker, positive at amplifier.
for item in sch[1:]:
 if isinstance(item,list) and item[0]=='wire' and set(node(item))=={(514.35,193.04),(553.72,193.04)}:removed.add(id(item))
cap=ns['inst'](ns['CP'],'C10','4700u / 50V',208,76,a=90);take()
for item in new:
 if item[0]=='symbol' and prop(item,'Reference')[2]=='C10':
  fld(prop(item,'Reference'),'at')[2]=Atom('200.66');fld(prop(item,'Value'),'at')[2]=Atom('205.74')
wire((514.35,193.04),tuple(x*2.54 for x in cap['1']));wire(tuple(x*2.54 for x in cap['2']),(553.72,193.04));lab('PRE_CAP',(516.89,193.04))
# Define speaker-side DC potential and permit capacitor discharge without a speaker attached.
ns['resistor']('R34','10k BLEED',(220,85),(220,99));ns['wire']((216,76),(216,82),(220,82),(220,85));ns['ground']((220,99));take()
new.append(parse(f'(junction (at 548.64 193.04) (diameter 0) (color 0 0 0 0) (uuid {U()}))'))
# Half-supply divider: 9.09 mA, 0.182 W each. VREF bypass caps C8/C9 are separate from power bypass.
ns['resistor']('R32','2k2 / 0.5W / 1%',(20,117),(20,123));ns['label']('+40V',(20,117));ns['resistor']('R33','2k2 / 0.5W / 1%',(20,123),(20,129));ns['label']('VREF_20V',(20,123));ns['ground']((20,129));ns['tp']('VREF_20V',(20,123),(6,0));take()
new.append(parse(f'(junction (at 50.8 312.42) (diameter 0) (color 0 0 0 0) (uuid {U()}))'))
ns['text']('40 V single supply. AMP_OUT rests at ~20 V DC; SPK_OUT has DC blocked by C10.\nC10 positive faces amplifier; 4700u / 50V gives ~4.23 Hz into 8 ohm.\nVREF = filtered divider midpoint (~20 V); input/feedback only, never speaker return.\nC1 must remain fitted for a ground-referenced source; DC bypass R2 removed.\nC8/C9 filter VREF; C6/C7 bypass the 40 V supply. R10 changed to preserve bias.\nStartup/shutdown thump and reference settling require bench verification.',12,168,1.25);take()
# Preserve existing cached libraries, IDs and user placement; append only new items.
sch=[x for x in sch if id(x) not in removed];sch.extend(new)
tb=fld(sch,'title_block');fld(tb,'date')[1]=Atom('2026-10-06',True);fld(tb,'rev')[1]=Atom('0.2 SINGLE SUPPLY',True)
(ROOT/'ClassA.kicad_sch').write_text('('+str(sch[0])+'\n'+'\n'.join(dump(x) for x in sch[1:])+'\n)\n')
print('Changed values:',changed,'; added C10, R32, R33, R34, TP16; restored mirror reference link.')
