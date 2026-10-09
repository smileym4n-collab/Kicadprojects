"""DC/tolerance screening, not SPICE or a guarantee of uncharacterised module behaviour."""
from pathlib import Path
import itertools,json,math,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parent.parent
cs={c.attrib['ref']:c for c in ET.parse(root/'review/final-netlist.xml').findall('components/comp')}
checks=[]
def check(ok,msg):
 assert ok,msg
 checks.append(msg)
for base,dc,amp in [(20,'U10','U5'),(40,'U11','U7')]:
 for n,v in {0:'30R / 3W / 1%',1:'100R',2:'3k3',3:'470k',4:'100k',5:'100k',6:'1k',7:'10k',8:'100k',9:'2M2',10:'4k7',11:'100k',12:'390R',14:'1k'}.items():
  check(cs[f'R{base+n}'].findtext('value')==v,f'R{base+n} matches reviewed value {v}')
 check(cs[dc].findtext('value')=='SPU03L-05',dc+' is 5V-in/5V-out module')
 check(cs[amp].findtext('value')=='LM358N',amp+' remains LM358 DIP-8')
check(cs['U1'].findtext('value')=='R-78B5.0-2.0','Buck is 2A model')
check(cs['F1'].findtext('value')=='T1A','Input fuse updated for load budget')
# Established design/test envelope, not claimed as guaranteed SPU03 worst-case specification.
# Quiet rail >=3.6V requires filter draw <=4mA at raw 4V and tolerances included in bench acceptance.
qmin,qmax=3.6,6.0
peak=2*math.sqrt(2)
attenmax=101000/(465300+101000)
bmax=qmin*1010/(3267+1010) # ignoring threshold loading increases upper bound
bmin=qmin*990/(3333+990+35) # conservative additional load allowance
input_max=bmax+attenmax*peak+0.05+0.009
input_min=bmin-attenmax*peak-0.05-0.009
check(input_max<qmin-2,'Amplifier input retains upper common-mode margin at 2Vrms, min supply')
check(input_min>0,'Amplifier input remains above return at 2Vrms, min supply')
# TI SLOA277B 6.2: LM358 comparator common-mode equals its LESS POSITIVE input.
# Non-inverting threshold remains valid, even if amplifier output reaches its high saturation limit.
# Solve bias/threshold two-node resistive network for all 1% corners, comparator output low/high.
def bt(q,vo,rtop,rbot,rt,rb,rh):
 g1=1/rtop+1/rbot+1/rt;g2=1/rt+1/rb+1/rh;g=1/rt
 det=g1*g2-g*g
 bias=(q/rtop*g2+g*vo/rh)/det
 threshold=(g1*vo/rh+g*q/rtop)/det
 return bias,threshold
min_release=99;min_cm=99;thresholds=[]
for q in [qmin,4.8,qmax]:
 for t in itertools.product([.99,1.01],repeat=5):
  vals=[a*b for a,b in zip([3300,1000,10000,100000,2.2e6],t)]
  for vo in [.02,q]:
   bias,th=bt(q,vo,*vals)
   min_cm=min(min_cm,q-2-th)
   if vo==q:min_release=min(min_release,bias-th-.026-.0135)
   else:
    # Amplifier DC error +/-26mV; comparator equivalent input error +/-13.5mV.
    for err in [-.0395,.0395]:thresholds.append((bias-th+err)/(101*100/570)/math.sqrt(2)*1000)
check(min_release>0,'Comparator cannot statically latch after audio: tolerance/offset release margin positive')
check(min_cm>0,'Comparator threshold always within conservative common-mode range')
bias,th=bt(4.8,.02,3300,1000,10000,100000,2.2e6)
preload_min=4/(30*1.01*1.025) # include 100K TCR excursion at 250ppm/K
preload_max_power=6**2/(30*.99*.975)
check(preload_min>.120,'Preload exceeds 20% of 600mA through stated voltage/tolerance/temperature screen')
check(preload_max_power<1.5,'Preload screen remains below half 3W rating')
# Explicit power-budget assumptions. Mean Well gives no guaranteed low-load efficiency/current curve.
# 60mA no-load current PLUS 70% incremental conversion efficiency is deliberately conservative,
# but is a planning estimate, not a manufacturer upper bound.
module_current=.060+(6**2/(30*.99*.975)+6*.018)/(.70*4.6)
board_current=2*module_current+.100
check(board_current<1.2,'5V planning load below 60% of new 2A buck capacity')
input_current=board_current*5.4/(.85*11.0)+.170+.005
check(input_current<.8,'12V planning input below 80% of 1A adapter/fuse rating')
report={'passed':len(checks),'checks':checks,'scope':'DC/tolerance calculations only; no transient or circuit simulation',
 'design_acceptance_envelope':{'raw_isolated_V':[4,6],'quiet_isolated_V':[3.6,6],'max_audio_sine_Vrms':2,'LM358_ambient_C':[0,70]},
 'results':{'input_min_V':input_min,'input_max_V':input_max,'input_upper_cm_margin_V':qmin-2-input_max,'comparator_cm_margin_V':min_cm,'comparator_release_margin_V':min_release,'bias_nominal_V':bias,'nominal_threshold_mVrms':(bias-th)/(101*100/570)/math.sqrt(2)*1000,'threshold_DC_corner_mVrms':[min(thresholds),max(thresholds)],'preload_min_mA':1000*preload_min,'preload_max_W':preload_max_power,'preload_nominal_pair_W':2*25/30,'estimated_5V_budget_A':board_current,'estimated_12V_budget_A':input_current},
 'limits':['4-6V raw isolated output is a design/bench acceptance window, not a guaranteed datasheet limit','Power estimates assume 60mA fixed input loss plus 70% incremental efficiency; verify actual draw and startup','LM358 legacy DC specifications are mainly measured at >=5V; TI low-VCC guidance supports operation but sensitivity below 5V needs measurement','Tolerance screen omits long-term drift; includes resistor 1%, LM358 offset/bias allowance; not Monte Carlo/SPICE','Bench check detection across frequency, startup/saturation recovery, module ripple and hot preload temperatures']}
(root/'review/detector-calculations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
