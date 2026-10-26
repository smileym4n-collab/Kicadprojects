#!/usr/bin/env python3
"""PSU study for the shared 12-0-12 VAC, ~100 VA toroid feeding two ClassA2 channels.
The transformer is NOT characterised: regulation is an assumption (8 % and 12 % cases);
winding resistance is referred to each secondary. Each Class-A channel is a constant DC
load per rail (its average rail current does not change with signal level)."""
import sys, json, re, pathlib, subprocess
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import run
R = run.R

def psu(name, mains=230, reg=0.10, I=1.37, bank='10000u', ctype='C', rcrc=0.1, tstop=4.0):
    vnl = 12*(1+reg)*mains/230           # open-circuit secondary rms
    rs = reg*12/(100/24)                 # ohms per secondary at the 100 VA rating
    pk = vnl*2**.5
    if ctype == 'C':
        tgt, tgn = 'P', 'N'
        cap = f'CRP P 0 {bank}\nCRN 0 N {bank}'
    else:  # CRC: first bank, series R, second bank (amplifier side)
        tgt, tgn = 'P1', 'N1'
        cap = (f'CRP1 P1 0 {bank}\nRRP P1 P {rcrc}\nCRP2 P 0 {bank}\n'
               f'CRN1 0 N1 {bank}\nRRN N1 N {rcrc}\nCRN2 0 N {bank}')
    d = f'''PSU {name}
.model DRECT D(IS=5n RS=0.02 N=1.6 CJO=50p TT=3u BV=1000)
VA SA 0 SIN(0 {pk} 50)
RSA SA A {rs}
LSA A A2 5u
VB 0 SB SIN(0 {pk} 50)
RSB SB B {rs}
LSB B B2 5u
D1 A2 {tgt} DRECT
D2 B2 {tgt} DRECT
D3 {tgn} A2 DRECT
D4 {tgn} B2 DRECT
{cap}
IP P 0 {I}
IN 0 N {I}
.options reltol=1e-4
.control
set noaskquit
tran 20u {tstop} {tstop-0.2} 20u
meas tran vp_avg AVG v(p) from={tstop-0.2} to={tstop}
meas tran vp_min MIN v(p) from={tstop-0.2} to={tstop}
meas tran vp_max MAX v(p) from={tstop-0.2} to={tstop}
meas tran vn_avg AVG v(n) from={tstop-0.2} to={tstop}
meas tran ia_rms RMS i(VA) from={tstop-0.2} to={tstop}
meas tran ia_pk MAX i(VA) from={tstop-0.2} to={tstop}
meas tran pd1 AVG par('v(a2,{tgt})*i(D1)') from={tstop-0.2} to={tstop}
quit
.endc
.end
'''
    (R/(name+'.cir')).write_text(d)
    subprocess.run([run.BIN, '-b', '-o', str(R/(name+'.log')), str(R/(name+'.cir'))], capture_output=True, timeout=600)
    log = (R/(name+'.log')).read_text(errors='ignore')
    o = {k: run.val(log, k) for k in ['vp_avg', 'vp_min', 'vp_max', 'vn_avg', 'ia_rms', 'ia_pk', 'pd1']}
    o['ripple_pp'] = o['vp_max'] - o['vp_min']
    o['VA_sec'] = 2*vnl*o['ia_rms']      # both secondaries, open-circuit voltage x rms current
    o['VA_loaded'] = 2*12*mains/230*o['ia_rms']
    o['P_dc'] = 2*o['vp_avg']*I
    o['vnl_rms'] = vnl; o['Rs'] = rs
    return o

if __name__ == '__main__':
    out = {}
    for ctype, bank in [('C', '10000u'), ('C', '22000u'), ('CRC', '9400u')]:
        for reg in [0.08, 0.12]:
            for mains in [216, 230, 253]:
                k = f'{ctype}_{bank}_reg{int(reg*100)}_{mains}V'
                out[k] = psu('psu_'+k, mains, reg, bank=bank, ctype=ctype, rcrc=0.1)
                o = out[k]
                print(k, 'Vavg %.2f Vmin %.2f ripple %.2f Irms/sec %.2f Ipk %.1f VA %.0f Pdc %.0f' % (o['vp_avg'], o['vp_min'], o['ripple_pp'], o['ia_rms'], o['ia_pk'], o['VA_loaded'], o['P_dc']))
    # no-load (amplifier unpowered/ bias collapsed) high-mains peak, worst for capacitor ratings
    o = psu('psu_noload', 253, 0.12, I=0.001, bank='10000u', tstop=3)
    out['noload_253V_reg12'] = o; print('no-load high mains', o['vp_max'])
    (R/'psu_summary.json').write_text(json.dumps(out, indent=1))
