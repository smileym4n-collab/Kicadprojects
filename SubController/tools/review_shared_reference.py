"""Check the approved shared rail reference against the live exported netlist.

Usage: python3 tools/review_shared_reference.py BASELINE_NET BACKUP_ZIP
No schematic generation, PCB edits, or inventory reservations.
"""
from pathlib import Path
import sys,json,itertools,zipfile,hashlib,re
from sexpr import parse,child,children

P=Path(__file__).resolve().parents[1]
def netlist(path):
    a=parse(Path(path).read_text())
    comps={str(child(c,'ref')[1]):{'value':str(child(c,'value')[1]),'footprint':str(child(c,'footprint')[1])} for c in children(child(a,'components'),'comp')}
    pins={};nets={}
    for n in children(child(a,'nets'),'net'):
        name=str(child(n,'name')[1]);nets[name]=set()
        for c in children(n,'node'):
            ref,pin=str(child(c,'ref')[1]),str(child(c,'pin')[1])
            pins.setdefault(ref,{})[pin]=name;nets[name].add((ref,pin))
    return comps,pins,nets
c,pins,nets=netlist(P/'design/checks/SubController.net')
old,opins,onets=netlist(sys.argv[1]);checks=[]
def check(ok,note):
    assert ok,note
    checks.append(note)
expected={
    'R75':('10k / 0.1%',{'1':'VREF_2V5','2':'VREF_1V25'}),
    'R76':('10k / 0.1%',{'1':'VREF_1V25','2':'GND'}),
    'R83':('100k / 1%',{'1':'+15V','2':'SENSE_POS15'}),
    'R84':('10k / 1%',{'1':'SENSE_POS15','2':'GND'}),
    'R85':('10k / 1%',{'1':'VREF_2V5','2':'SENSE_NEG15'}),
    'R86':('120k / 1%',{'1':'SENSE_NEG15','2':'-15V'}),
    'R87':('24k / 1%',{'1':'+5A','2':'SENSE_POS5'}),
    'R88':('10k / 1%',{'1':'SENSE_POS5','2':'GND'}),
    'R89':('10k / 1%',{'1':'VREF_2V5','2':'SENSE_NEG5'}),
    'R90':('43k / 1%',{'1':'SENSE_NEG5','2':'-5A'}),
}
removed={f'R{i}' for i in range(77,83)}
changed=set(expected)|{'U15'}
check(set(old)-set(c)==removed and not set(c)-set(old),'Exactly R77-R82 removed; no added components')
for ref,(value,mapping) in expected.items():
    check(c[ref]['value']==value,ref+' approved value/tolerance')
    check(pins[ref]==mapping,ref+' exact divider connections')
    check(c[ref]['footprint']==old[ref]['footprint'],ref+' footprint preserved')
check(pins['U15']=={'1':'RAIL_GOOD','2':'RAIL_GOOD','3':'+5R','4':'VREF_1V25','5':'SENSE_POS15','6':'SENSE_NEG15','7':'VREF_1V25','8':'SENSE_NEG5','9':'VREF_1V25','10':'VREF_1V25','11':'SENSE_POS5','12':'GND','13':'RAIL_GOOD','14':'RAIL_GOOD'},'All comparator pins/polarities and open-collector outputs correct')
check(nets['VREF_1V25']=={('R75','2'),('R76','1'),('U15','4'),('U15','7'),('U15','9'),('U15','10')},'One shared reference has exactly six intended connections')
check(not {'VREF_2V25','VREF_1V0','VREF_2V345','VREF_0V71'}&set(nets),'All four obsolete reference nets removed')
unaffected=set(old)-changed-removed
for ref in unaffected:
    check(old[ref]==c[ref],ref+' value and footprint unchanged')
    check(opins[ref]==pins[ref],ref+' full pin map unchanged')
manifest={x['Reference']:x for x in json.loads((P/'design/component-manifest.json').read_text())}
for ref in expected:
    check(manifest[ref]['Value']==c[ref]['value'] and manifest[ref]['Footprint']==c[ref]['footprint'],ref+' detector manifest value/footprint match')
def manifest_drift(m,components):
    result={'netlist_only':sorted(set(components)-set(m)),'manifest_only':sorted(set(m)-set(components)),'value_or_footprint_differences':{}}
    for ref in set(m)&set(components)-changed:
        if m[ref]['Value']!=components[ref]['value'] or m[ref]['Footprint']!=components[ref]['footprint']:
            result['value_or_footprint_differences'][ref]={'manifest':{'value':m[ref]['Value'],'footprint':m[ref]['Footprint']},'live':components[ref]}
    return result
with zipfile.ZipFile(sys.argv[2]) as z:oldmanifest={x['Reference']:x for x in json.loads(z.read('design/component-manifest.json'))}
drift=manifest_drift(manifest,c)
check(drift==manifest_drift(oldmanifest,old),'Existing unrelated manifest/netlist differences are unchanged')

def resistance(ref):
    s=c[ref]['value'].split()[0].lower();a,b=s.split('k');return float(a+'.'+b)*1000

# Datasheet envelope: LM4040A25 +/-19mV over -40..85C plus
# 8mV current-change allowance. LM339 used only in its 0..70C range:
# offset <=9mV, input bias <=400nA. Treat bias errors as independently
# signed to bound shared-node loading conservatively.
vref_bounds=[2.5-.019-.008,2.5+.019+.008]
ib=.4e-6;offset=.009
rails=[('POS15','R83','R84',1,14.7,15.75),('NEG15','R85','R86',-1,14.7,15.75),('POS5','R87','R88',1,4.897,5.25),('NEG5','R89','R90',-1,4.828,5.25)]
review={};common_inputs=[]
for name,top,bottom,pol,legalmin,legalmax in rails:
    rt,rb=resistance(top),resistance(bottom)
    trips=[];sense=[]
    for vref,a,b,t,u in itertools.product(vref_bounds,[.999,1.001],[.999,1.001],[.99,1.01],[.99,1.01]):
        r1,r2=10000*a,10000*b;rth_ref=r1*r2/(r1+r2)
        mid=vref*r2/(r1+r2);r_top,r_bot=rt*t,rb*u;rth_sense=r_top*r_bot/(r_top+r_bot)
        error=4*ib*rth_ref+ib*rth_sense+offset
        for e in [-error,error]:
            threshold=mid+e
            trips.append(threshold*(r_top+r_bot)/r_bot if pol==1 else ((vref-threshold)*r_bot/r_top-threshold))
        # Full rail-collapse sweep, assuming +5R keeps U14 and U15 valid.
        for mag in [0,legalmax]:
            vs=mag*r_bot/(r_top+r_bot) if pol==1 else (vref*r_bot-mag*r_top)/(r_top+r_bot)
            # LM339 bias current flows out of each input (PNP stage),
            # so it raises a passive sense node; it cannot drive a
            # grounded positive-rail divider below ground at zero rail.
            sense.extend([vs,vs+ib*rth_sense])
        common_inputs.extend([mid-4*ib*rth_ref,mid+4*ib*rth_ref])
    nominal=1.25*(rt+rb)/rb if pol==1 else 1.25*(rb/rt-1)
    check(max(trips)<legalmin,name+' no false fault at conservative valid rail minimum')
    check(min(sense)>=0 and max(sense)<2.75,name+' sense stays within LM339 common-mode range for +5R>=4.75V')
    review[name]={'nominal_trip_magnitude_V':nominal,'conservative_trip_magnitude_bounds_V':[min(trips),max(trips)],'sense_voltage_bounds_V': [min(sense),max(sense)],'valid_rail_minimum_magnitude_V':legalmin}
check(min(common_inputs)>0 and max(common_inputs)<2.75,'Shared threshold stays within comparator common-mode range')
# Shunt bias remains valid with both negative rails high and low.
loadmax=2.527/(20000*.999)+(2.527+15.75)/(130000*.99)+(2.527+5.25)/(53000*.99)+8*ib
shuntmin=(4.75-2.527)/(680*1.01)-loadmax
shuntmax=(5.25-2.473)/(680*.99)
check(shuntmin>.000080 and shuntmax<.015,'LM4040 current remains between 80uA minimum and 15mA maximum')

with zipfile.ZipFile(sys.argv[2]) as z:
    h=json.loads(z.read('baseline-hashes.json'));protected=[]
    for file in h:
        if file.endswith(('.kicad_sch','.kicad_pcb','.kicad_pro','.kicad_sym','.kicad_mod')) or file in ['fp-lib-table','sym-lib-table']:
            if file=='06_power_mute.kicad_sch':continue
            check(hashlib.sha256((P/file).read_bytes()).hexdigest()==h[file],file+' byte-identical to backup')
            protected.append(file)
    check((P/'SubController.kicad_pro').read_bytes()==z.read('SubController.kicad_pro'),'Project/ERC settings exactly preserved')
report={'assertions_passed':len(checks),'assertions':checks,'removed_components':sorted(removed),'unchanged_component_values_footprints_and_pin_maps':len(unaffected),'preserved_files':protected,'backup':str(Path(sys.argv[2]).relative_to(P)),'rail_threshold_review':review,'reference_voltage_budget_V':vref_bounds,'LM339_budget':{'offset_V':offset,'input_bias_A':ib,'shared_reference_inputs':4,'temperature_C':[0,70]},'LM4040_shunt_current_bounds_A':[shuntmin,shuntmax],'pre_existing_manifest_drift':drift,'limitations':'Static datasheet-envelope calculation, no transient simulation or bench validation. Sense-voltage check assumes +5R>=4.75V and valid LM4040 reference; arbitrary supply/reference collapse is not certified pop-free. Resistor tolerances assumed to apply in operation; verify selected part temperature coefficients. +/-5V detector is not an operating-range supervisor. Existing audio AC assertion fails identically before/after; see baseline comparison report. Existing unrelated manifest/BOM differences are preserved, not corrected by this detector update. PCB is unchanged and not synchronized to the new schematic.'}
(P/'design/checks/shared-reference-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v['conservative_trip_magnitude_bounds_V'] for k,v in review.items()},indent=2))
print(len(checks),'assertions passed;',len(unaffected),'unaffected components preserved')
