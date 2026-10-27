from schlib import *
import xml.etree.ElementTree as E,hashlib,json,collections,math,argparse
args=argparse.ArgumentParser()
args.add_argument("--preservation-baseline",default="review/original/hashes.json",help="Hash snapshot taken before the scoped change; does not replace original pin-map/UUID checks")
args=args.parse_args()
root=E.parse('review/validation/final.xml').getroot()
nets={};names={};checks=[]
for net in root.findall('./nets/net'):
 for no in net.findall('node'):nets[(no.get('ref'),no.get('pin'))]=net.get('code');names[(no.get('ref'),no.get('pin'))]=net.get('name')
def eq(desc,*nodes):
 ns=[nets.get((r,str(p))) for r,p in nodes];assert None not in ns and len(set(ns))==1,(desc,nodes,ns);checks.append({'check':desc,'result':'PASS'})
def ne(desc,*nodes):
 ns=[nets.get((r,str(p))) for r,p in nodes];assert None not in ns and len(set(ns))==len(ns),(desc,ns);checks.append({'check':desc,'result':'PASS'})
def ok(desc,v):assert v,desc;checks.append({'check':desc,'result':'PASS'})
g=('J1',2)
# Every amplifier pin has an explicit verified disposition.
for pin,ref,pn in [(1,'J1',2),(2,'C30',1),(3,'R30',2),(4,'C1',2),(5,'C2',2),(6,'C29',1),(7,'C28',1),(8,'R18',1),(9,'J1',2),(10,'C6',2),(11,'C5',2),(12,'C31',1),(13,'J1',2),(14,'J1',2),(15,'J1',2),(17,'Q1',3),(18,'Q1',3),(19,'Q1',3),(20,'C27',1),(21,'L3',4),(22,'J1',2),(23,'L3',1),(24,'C26',1),(25,'J1',2),(26,'C25',1),(27,'L2',4),(28,'J1',2),(29,'L2',1),(30,'C24',1),(31,'Q1',3),(32,'Q1',3)]:eq('TPA3126D2 pin '+str(pin),('U1',pin),(ref,pn))
ok('Master SYNC intentionally NC',names['U1','16'].startswith('unconnected-'))
for cr,out in [('C24',29),('C25',27),('C26',23),('C27',21)]:eq('Matching bootstrap '+cr,(cr,2),('U1',out))
for pin,ref,pn in [(1,'IC4',5),(2,'C14',1),(3,'J1',2),(4,'C14',2),(5,'C12',1),(6,'R2',1),(7,'R3',2),(8,'IC4',5),(9,'J1',2),(10,'J1',2),(11,'IC5',33),(12,'IC5',31),(16,'J1',2),(17,'J1',2),(18,'IC4',5),(20,'J1',2),(21,'R5',1),(22,'R9',1),(23,'R4',1),(24,'J1',2),(25,'IC5',30),(26,'C15',1),(27,'J1',2),(28,'IC4',5)]:eq('PCM5122 pin '+str(pin),('U2',pin),(ref,pn))
for pn in [13,14,15,19]:ok('DAC GPIO '+str(pn)+' intentionally NC',names['U2',str(pn)].startswith('unconnected-'))
# Preserve all seven proven GPIOs and their series resistors.
for pin,rr in [(8,'R8'),(9,'R7'),(10,'R4'),(11,'R5'),(16,'R9')]:eq('Retained ESP32 module pin '+str(pin),('IC5',pin),(rr,2))
eq('SCL GPIO19 retained',('IC5',31),('U2',12),('R31',2));eq('SDA GPIO21 retained',('IC5',33),('U2',11),('R33',2))
for pin,ref,pn in [(2,'U4',2),(3,'R10',2),(4,'R27',2),(7,'U1',3),(12,'R21',1),(25,'R11',2),(30,'U2',25),(34,'J2',2),(35,'J2',3),(37,'R26',1)]:eq('ESP additional supply/control pin '+str(pin),('IC5',pin),(ref,pn))
for pn in [1,15,*range(38,48)]:eq('ESP GND pad '+str(pn),('IC5',pn),g)
for pn in [17,18,19,20,21,22,27,28,32]:ok('Flash/PSRAM NC pad '+str(pn),names['IC5',str(pn)].startswith('unconnected-'))
eq('Wi-Fi LED anode via R8',('D3',2),('R8',1));eq('BT LED anode via R7',('D4',2),('R7',1));eq('LED cathodes grounded',('D3',1),('D4',1),g)
# Speakers remain BTL; external capacitor loop does not bypass filter.
eq('Woofer + filtered',('L2',2),('C37',2),('J16',1));eq('Woofer - filtered',('L2',3),('C38',1),('J16',2))
eq('Tweeter + before capacitor',('L3',2),('C39',2),('J18',1),('C54',1));eq('Tweeter + after capacitor',('J18',2),('C54',2),('J17',1));eq('Tweeter - filtered',('L3',3),('C40',1),('J17',2))
ne('Both BTL pairs and ground are distinct',('J16',1),('J16',2),('J17',1),('J17',2),g);ne('Cap loop is open on PCB without external cap/link',('J18',1),('J18',2));ne('Bridge switching nodes not shorted',('U1',29),('U1',27),('U1',23),('U1',21),g)
eq('DAC left -> woofer pad',('R2',2),('R12',1));eq('DAC right -> tweeter pad',('R3',1),('R14',1))
for refs in [('C1','R13','R12'),('C6','R15','R14')]:eq('Input pad '+refs[0],(refs[0],1),(refs[1],2),(refs[2],2))
# Power and connector polarities.
eq('Reverse FET drain from fuse',('J1',1),('F2',1));eq('Fuse to PMOS drain',('F2',2),('Q1',2));eq('Protected source rail',('Q1',3),('D2',1),('D1',1),('U3',3));eq('FET gate / Zener anode',('Q1',1),('D1',2),('R22',1));eq('TVS anode ground',('D2',2),g)
for pin,ref,pn in [(1,'J1',2),(2,'L1',1),(3,'Q1',3),(4,'R24',1),(5,'Q1',3),(6,'C48',1)]:eq('Buck pin '+str(pin),('U3',pin),(ref,pn))
eq('Buck bootstrap return',('C48',2),('U3',2));eq('Pre-regulator feeds LDOs',('L1',2),('U4',3),('R1',1));eq('Feedback top',('R23',1),('L1',2));eq('Feedback divider node',('R23',2),('R24',1),('U3',4));eq('Feedback bottom ground',('R24',2),g)
eq('ESP LDO ground',('U4',1),g);eq('ESP LDO output',('U4',2),('IC5',2));eq('DAC input after RC',('IC4',1),('IC4',3),('C7',1),('R1',2));eq('DAC LDO ground',('IC4',2),g);ne('Separate digital and DAC positive supply rails',('IC5',2),('IC4',5))
# Verify schematic symbol pin sets against assigned footprint pads for every board component.
fp_root=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
for fn in ['TPA3126','ESP32','DAC','Amp','Power']:
 n=load(fn+'.kicad_sch')
 for s in many(n,'symbol'):
  ref=val(s,'Reference');fp=val(s,'Footprint')
  if ref.startswith('#') or not fp or get(s,'on_board')[1]=='no':continue
  nick,fpname=fp.split(':');p=(Path('TPA3126.pretty') if nick in ['Custom','TPA3220'] else fp_root/(nick+'.pretty'))/(fpname+'.kicad_mod')
  ok('Footprint resolves '+ref,p.exists());f=load(p)
  ss=set(pp[0] for pp in pins(n,s));pads=set(pp[1] for pp in many(f,'pad') if pp[1])
  ok('Pad mapping '+ref,ss<=pads)
# Exact selected IC pin-name maps remain unchanged from the original user symbols.
for fn,ref in [('Amp','U1'),('ESP32','IC5'),('DAC','U2'),('DAC','IC4')]:
 old=load('review/original/'+fn+'.kicad_sch');new=load(fn+'.kicad_sch');os=next(s for s in many(old,'symbol') if val(s,'Reference')==ref);ns=next(s for s in many(new,'symbol') if val(s,'Reference')==ref)
 ok('Original physical pin map preserved '+ref,{p[:2] for p in pins(old,os)}=={p[:2] for p in pins(new,ns)})
# Every existing component identity retained; no project or PCB settings modified.
original=json.load(open(args.preservation_baseline))
for fn in ['TPA3126.kicad_pcb','TPA3126.kicad_pro','TPA3126.kicad_prl']:ok('Unchanged '+fn,hashlib.sha256(Path(fn).read_bytes()).hexdigest()==original[fn])
for fn in ['TPA3126','ESP32','DAC','Amp','Power']:
 o=load('review/original/'+fn+'.kicad_sch');n=load(fn+'.kicad_sch');o={val(s,'Reference'):get(s,'uuid')[1] for s in many(o,'symbol') if not val(s,'Reference').startswith('#')};nn={val(s,'Reference'):get(s,'uuid')[1] for s in many(n,'symbol') if not val(s,'Reference').startswith('#')}
 ok('Existing component UUIDs retained '+fn,all(nn.get(k)==v for k,v in o.items()))
r=json.load(open('review/validation/final-erc.json'));viol=[v for s in r['sheets'] for v in s['violations']];ok('KiCad 10.0.5 final ERC zero findings',not viol)
Path('review/validation/connectivity-checks.json').write_text(json.dumps({'count':len(checks),'checks':checks},indent=2));print(str(len(checks))+' checks PASS')
# Numerical design checks, independently calculated from the selected values.
Vpre=.6*(1+100/16.2);Vmin=.6*.985*(1+99/16.2/1.01);Vmax=.6*1.015*(1+101/16.2/.99)
L=10e-6;C=680e-9;fc=1/(2*math.pi*math.sqrt(L*C));q=4/2*math.sqrt(C/L)
ri=50000;rt=3300+470;rb=1000;rl=1/(1/rb+1/ri);att=rl/(rt+rl)
vp=5.6*33/133;vpk=4*vp;rs=.09+.055
out={'pre_regulator_nominal_V':Vpre,'pre_regulator_tolerance_min_V':Vmin,'pre_regulator_tolerance_max_V':Vmax,'ESP_LDO_0p25A_W':(Vpre-3.3)*.25,'ESP_LDO_0p5A_W':(Vpre-3.3)*.5,'ESP_LDO_1A_W':Vpre-3.3,'LC_natural_frequency_Hz':fc,'LC_Q_resistive_4ohm':q,'LC_differential_L_H':2*L,'LC_differential_C_F':C/2,'input_attenuation':att,'input_attenuation_dB':20*math.log10(att),'output_requested_DAC_2p1Vrms_gain20dB_Vrms':2.1*att*10,'PLIMIT_nominal_V':vp,'PLIMIT_divider_min_V':5.1*(33*.99)/(100*1.01+33*.99),'PLIMIT_divider_max_V':6.3*(33*1.01)/(100*.99+33*1.01),'PLIMIT_model_output_peak_V':vpk,'PLIMIT_model_unclipped_W_4ohm':(vpk*4/(4+2*rs))**2/8,'output_ripple_p_p_worst_L8u_376k_16V_A':16/(4*8e-6*376e3),'output_ripple_rms_A':(16/(4*8e-6*376e3))/math.sqrt(12),'tweeter_47uF_4ohm_HP_Hz':1/(2*math.pi*4*47e-6),'buck_ripple_16V_6p8u_500k_A':Vpre*(16-Vpre)/(16*6.8e-6*500e3)}
Path('review/validation/calculations.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
