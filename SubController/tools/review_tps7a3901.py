"""Datasheet-based regulator calculations and preservation audit; no PCB edits."""
from pathlib import Path
import sys,json,math,itertools,hashlib,zipfile
from sexpr import parse,child,children
P=Path(__file__).resolve().parents[1]
def readnet(path):
 d=parse(Path(path).read_text());c={str(child(x,'ref')[1]):{'value':str(child(x,'value')[1]),'foot':str(child(x,'footprint')[1])} for x in children(child(d,'components'),'comp')};pins={}
 for net in children(child(d,'nets'),'net'):
  for n in children(net,'node'):pins.setdefault(str(child(n,'ref')[1]),{})[str(child(n,'pin')[1])]=str(child(net,'name')[1])
 return c,pins
def resistor(ref):
 s=c[ref]['value'].split()[0].lower();a,b=s.split('k');return float(a+'.'+b)*1000
c,pins=readnet(P/'design/checks/SubController.net')
rp=resistor('R105')+resistor('R106');rn=sum(resistor(r) for r in ['R108','R109','R110']);lp=resistor('R107');ln=resistor('R111')
assert (rp,rn,lp,ln)==(32000,42000,10000,10000)
def limits(arms):
 lows=sum(resistor(r)*(1-t) for r,t in arms);highs=sum(resistor(r)*(1+t) for r,t in arms);return lows,highs
pmin,pmax=limits([('R105',.005),('R106',.001)]);nmin,nmax=limits([('R108',.005),('R109',.001),('R110',.001)])
vp=1.188*(1+rp/lp);vn=-1.19*rn/ln
# TI output-accuracy specifications already include internal reference/error-amplifier effects.
p_range=[1.188*(1+pmin/(lp*1.001))*.985,1.188*(1+pmax/(lp*.999))*1.015]
n_range=[1.19*nmin/(ln*1.001)*.97,1.19*nmax/(ln*.999)*1.03]
assert min(p_range+n_range)>=4.75 and max(p_range+n_range)<=5.25
assert min(p_range)>4.68782 and min(n_range)>4.65706
dc=json.load(open(P/'design/source-data/CL31A106KBHNNN-DC-bias.json'))
curve=sorted((float(x['x']),float(x['y'])) for x in dc['curve'])
def cap(v):
 for (a,b),(x,y) in zip(curve,curve[1:]):
  if a<=v<=x:return 10*(1+(b+(y-b)*(v-a)/(x-a))/100)
 raise ValueError(v)
input_effective=2*cap(15.75)*.9*.85*.9 # tolerance, temperature and an additional 10% aging allowance
output_effective=cap(5.25)*.9*.85*.9
assert input_effective>2.2 and output_effective>2.2
nr=100e-9;ss=350000*nr*math.log((1.19+5.1e-6*350000)/(5.1e-6*350000))
tau_p=rp*10e-9;tau_n=rn*10e-9;assert ss>10*max(tau_p,tau_n)
f=parse((P/'libraries/SubController.pretty/TPS7A3901_DSC0010J_WSON10.kicad_mod').read_text());pads=children(f,'pad')
for i in range(5):
 for number,x,y in [(i+1,-1.4,-1+i*.5),(10-i,1.4,-1+i*.5)]:
  p=next(p for p in pads if str(p[1])==str(number));assert list(map(float,child(p,'at')[1:3]))==[x,y];assert list(map(float,child(p,'size')[1:3]))==[.6,.24]
ep=next(p for p in pads if str(p[1])=='11' and list(map(float,child(p,'at')[1:3]))==[0,0]);assert list(map(float,child(ep,'size')[1:3]))==[1.65,2.4]
assert pins['U11']['11']=='GND' and len([p for p in pads if str(p[1])=='11'])==5
opto=parse(Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Package_DIP.pretty/DIP-4_W7.62mm.kicad_mod').read_text())
assert {str(p[1]):list(map(float,child(p,'at')[1:3])) for p in children(opto,'pad')}=={'1':[0,0],'2':[0,2.54],'3':[7.62,2.54],'4':[7.62,0]}
power={'part':'TPS7A3901','positive_nominal_V':vp,'negative_nominal_V_ignoring_FB_offset':vn,'positive_bounds_V':p_range,'negative_magnitude_bounds_V':n_range,'bounds_basis':'TI +/-1.5% positive and +/-3% negative plus owned resistor corners; independent bounds, not simulation.','feedback_parts':{r:c[r] for r in ['R105','R106','R107','R108','R109','R110','R111']},'BUF_load_uA':1.19/ln*1e6,'max_allowed_BUF_uA':1000,'estimated_input_effective_uF_at_15V75':input_effective,'estimated_output_effective_uF_at_5V25':output_effective,'capacitance_basis':'Samsung typical bias curve, -10% tolerance, -15% temperature, additional -10% aging estimate; bench validation still required.','soft_start_typ_ms':ss*1000,'feedback_time_constants_ms':[tau_p*1000,tau_n*1000],'nominal_dissipation_budget_W':.27,'max_input_dissipation_budget_W':(15.75-5)*(.015+.012)+.01,'TI_theta_JA_C_per_W':44.4,'thermal_limitations':'Datasheet test-board theta only. Solder EP11 to GND copper; thermal vias at PCB stage; bench test enclosure.','pin_map':pins['U11'],'package_review':'TI DSC0010J drawing4221826/E03/2026, datasheet pages50-52. 0.5mm pitch, 0.6x0.24 pads at +/-1.4; EP1.65x2.4 plus fingers, segmented stencil.','VO617A':{'part':'VO617A-3','package':'DIP4, 7.62mm rows, 2.54mm pitch','pin_map':pins['U10'],'trigger_LED_current_typ_mA':(12-1.1)/2200*1000,'pullup_current_approx_mA':5/10000*1000,'CTR_bin_percent_at_5mA':[100,200],'trigger_polarity_and_isolation_unchanged':True,'stock':'No positive connected inventory VO617 search result; user-selected common part, purchase/check availability.'},'limitations':'Datasheet calculations and connectivity review; no regulator SPICE, prototype, thermal or trigger bench validation.'}
(P/'design/checks/TPS7A3901-supply-review.json').write_text(json.dumps(power,indent=2)+'\n')
before,bpins=readnet('/private/tmp/SubController-before-TPS.net');changed={'U10','U11','C46','C47','C48','C49'};removed={'U12','C56'};added={f'R{i}' for i in range(105,112)}|{f'C{i}' for i in range(57,62)};repaired={'C12','C15'}
assert set(before)-set(c)==removed and set(c)-set(before)==added
unaffected=set(before)-changed-removed
for ref in unaffected:
 assert before[ref]==c[ref],(ref,'value/footprint changed')
 if ref not in repaired:assert bpins[ref]==pins[ref],(ref,'connection changed',bpins[ref],pins[ref])
for ref,l,r in [('C12','LP1_A','LP12'),('C15','LP2_A','LP24')]:assert pins[ref]=={'1':r,'2':l}
backup=json.load(open(P/'design/checks/TPS7A3901-baseline.json'))['backup'];same=[];project_delta={}
with zipfile.ZipFile(P/backup) as z:
 for name in ['SubController.kicad_sch','SubController.kicad_pcb','SubController.kicad_pro','SubController.kicad_prl','01_inputs.kicad_sch','03_level_phase.kicad_sch','04_protection_output.kicad_sch','07_drivers.kicad_sch','08_rail_interlock.kicad_sch','fp-lib-table','sym-lib-table']:
  old=z.read(name);new=(P/name).read_bytes()
  if name=='SubController.kicad_pro' and old!=new:
   a=json.loads(old);b=json.loads(new)
   project_delta={'old_used_designators':a['schematic']['used_designators'],'new_used_designators':b['schematic']['used_designators'],'explanation':'KiCad bookkeeping records removed U12 as used; all other project settings remain identical.'}
   a['schematic']['used_designators']=b['schematic']['used_designators']
   assert a==b,'Project settings changed beyond removed-designator bookkeeping'
  else:
   assert old==new,name+' changed';same.append(name)
pres={'baseline_snapshot':backup,'unchanged_components_values_footprints':len(unaffected),'unchanged_component_pin_maps':len(unaffected-repaired),'changed_components':sorted(changed),'removed_components':sorted(removed),'added_components':sorted(added),'crossover_geometry_repair':'Four explicit T junctions at X68.58/121.92/256.54/309.88 Y58.42 restore C12/C15 connections after merged-wire saves. Baseline 4 errors+4 warnings; final ERC has zero.','preserved_files':same,'project_bookkeeping_delta':project_delta,'existing_user_changes_preserved':'Input sheet already had R5/R6=22k, Panasonic AGN2004H K1/K2 and JST-XH J1/J2/J3. These values/footprints/wiring were not changed. Generic pad parity and AC checks include them; no new relay/connector qualification.'}
(P/'design/checks/TPS7A3901-change-preservation.json').write_text(json.dumps(pres,indent=2)+'\n')
print(json.dumps({k:power[k] for k in ['positive_nominal_V','negative_nominal_V_ignoring_FB_offset','positive_bounds_V','negative_magnitude_bounds_V','estimated_input_effective_uF_at_15V75','estimated_output_effective_uF_at_5V25','soft_start_typ_ms']},indent=2));print('Preserved',len(unaffected),'component values/footprints and',len(unaffected-repaired),'pin maps; PCB unchanged, project settings unchanged except removed-designator bookkeeping.')
