#!/usr/bin/env python3
"""Compare exported KiCad nets against the intended mono circuit, pin by pin."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json, hashlib, math

root=Path(__file__).resolve().parents[1]
xml=ET.parse(root/'work/review/netlist.xml').getroot()
actual={n.get('name'):{(p.get('ref'),p.get('pin')) for p in n.findall('node')} for n in xml.findall('./nets/net')}
expected={
'+35V':'C6.1 C7.1 J2.1 Q11.2 R12.1 R4.1 R5.1 R9.1 TP5.1',
'-35V':'C10.2 C8.2 C9.2 J2.3 Q12.2 Q7.1 R13.2 R8.2 TP7.1',
'GND':'C2.2 C6.2 C7.2 C8.1 C9.1 J1.2 J2.2 J3.2 R2.2 R21.2 TP6.1',
'INPUT':'C1.1 J1.1 R1.1',
'AMP_OUT':'C3.2 C5.1 L1.1 R10.2 R19.2 R20.1 R22.1 TP3.1',
'SPK_OUT':'J3.1 L1.2 R22.2 TP4.1',
'BIAS_TEST_N':'Q11.3 R19.1 TP1.1',
'BIAS_TEST_P':'Q12.3 R20.2 TP2.1',
'DRIVE_N':'C4.2 Q8.2 Q9.2 R14.1 R17.1',
'DRIVE_P':'Q10.2 Q9.1 R15.2 R18.1 RV1.2 RV1.3',
'IREF':'C10.1 Q10.1 Q5.3 Q6.2 Q6.3 R9.2',
'MIRROR_REF':'Q2.2 Q3.3 Q4.2 Q4.3',
'NFB':'C3.1 Q2.3 R10.1 R11.1',
'VAS_IN':'C4.1 Q1.2 Q3.2 Q8.1',
'input_after_link':'C1.2 R1.2 R2.1 R3.1',
'input_base':'Q1.3 R3.2',
'input_emitter':'Q1.1 R6.1',
'feedback_emitter':'Q2.1 R7.1',
'tail':'Q5.2 R6.2 R7.2',
'tail_emitter':'Q5.1 R8.1',
'mirror_output_emitter':'Q3.1 R4.2',
'mirror_reference_emitter':'Q4.1 R5.2',
'VAS_emitter':'Q8.3 R12.2',
'sink_emitter':'Q10.3 R13.1',
'bias_base':'Q9.3 R14.2 R15.1 R16.1',
'bias_shunt':'R16.2 RV1.1',
'N_base':'Q11.1 R17.2',
'P_base':'Q12.1 R18.2',
'feedback_DC_leg':'C2.1 R11.2',
'zobel_mid':'C5.2 R21.1',
'reference_mid':'Q6.1 Q7.2 Q7.3',
}
passed=[]
for name,pins in expected.items():
    want={tuple(s.split('.')) for s in pins.split()}
    netname=next((k for k,v in actual.items() if want==v),None)
    assert netname is not None,(name,want)
    if '/'+name in actual or name=='GND':assert netname=='GND' if name=='GND' else netname=='/'+name
    passed.append(f'PASS {name}: {netname} = {pins}')
assert len(expected)==len(actual),(len(expected),len(actual))
passed.append('PASS all exported nets accounted for; no unintended joins or orphan component pins')

intent=json.loads((root/'work/review/component-intent.json').read_text())
comps={c.get('ref'):c.findtext('value') for c in xml.findall('./components/comp')}
assert len([v for v in comps.values() if v=='2SD2390'])==1
assert len([v for v in comps.values() if v=='2SB1560'])==1
assert len([r for r in comps if r.startswith('Q')])==12
assert len([r for r in comps if r.startswith('J')])==3
assert intent['C1']['dnp'] and intent['C3']['dnp'] and comps['R1'].startswith('0R')
passed.append('PASS one complementary Darlington pair, no separate output driver pair, three scoped connectors')
passed.append('PASS default input DC link fitted, C1/C3 DNP, feedback capacitor bipolar')

for f in ['DarlingtonAmp.kicad_pro','DarlingtonAmp.kicad_pcb']:
    assert (root/f).read_bytes()==(root/'work/source-backup'/f).read_bytes(),f
    passed.append(f'PASS {f} unchanged: '+hashlib.sha256((root/f).read_bytes()).hexdigest())

gain=1+22000/1150
fc=1/(2*math.pi*1150*220e-6)
values=[f'Audio gain: {gain:.4f} V/V = {20*math.log10(gain):.3f} dB; DC gain 1',
        f'Feedback LF corner: {fc:.3f} Hz; input impedance approximately 22k',
        'Emitter-resistor bias target: 17.6-22.0mV each = 80-100mA; 2.8-3.5W idle per output',
        'Bias spreader: Rcb=2k2, Rbe=2k2 || (680R + RV1 0..5k); VBE nominal 0.65V']
for rv in [5000,0]:
    rbe=1/(1/2200+1/(680+rv))
    ideal=.65*(1+2200/rbe)
    worst=ideal+2200*(.006-.65/rbe)/(25+1)
    values.append(f'RV1={rv} ohm: nominal spread {ideal:.3f}V ignoring Ib; {worst:.3f}V for illustrative beta=25, 6mA')
values+=['Open wiper 2: permanent end 3 connection leaves full 5k track -> minimum setting.',
         'Shunt track open: fixed Rbe=2k2 remains -> still lower voltage. Fixed-resistor failures are not covered.',
         'Voltage spread estimates do not guarantee a current range; verify actual devices and hot bias drift.',
         'Estimated tail 1.8mA and VAS sink 5-7mA; VAS/current sink ~0.2W idle, <0.45W at output excursion.',
         'Estimated resistive output swing 30-31Vpk gives 56.3-60.1W / 8 ohm; 65W requires 32.25Vpk and is not guaranteed.',
         'Resistive Class-B worst dissipation ~15.5W/device at 8 ohm, ~31W/device at 4 ohm, plus bias/reactive load.',
         'No simulation or bench tests performed. No PCB layout or protection circuitry created.']
(root/'work/review/connectivity-check.txt').write_text('\n'.join(passed)+'\n\n'+'\n'.join(values)+'\n')
print('\n'.join(passed[-6:]))
print('\n'.join(values[:7]))
