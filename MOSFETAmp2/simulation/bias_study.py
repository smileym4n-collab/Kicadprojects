#!/usr/bin/env python3
"""Bias-network comparison study: current network (A) against two candidates (P, B).

Run from anywhere; decks are written to simulation/results_bias/ and run with cwd=simulation/.
Development evidence only. MOSFET temperature behaviour is IMPOSED (threshold slope per device,
mobility T^-1.5), not modelled by the manufacturer models. See docs/BIAS_STUDY.md.

Variants
  A  existing: 4.3 V Zener + BD139 multiplier, 1k / 47k || (130R + 2k rheostat).
  P  select-on-test Zener + BD139 multiplier with narrow k trim (2k7 / 1k2 || (820R + 2k)).
  B  two board diodes + fixed-ratio BD139 multiplier (3k9 / 1k0) + LED-referenced BC546 current
     sink drawing a programmed current from the multiplier base; select-on-test RE + trim sized to RE.
"""
import os, re, json, pathlib, subprocess, sys
import numpy as np
from scipy.optimize import brentq

P = pathlib.Path(__file__).resolve().parent
BIN = os.environ.get('NGSPICE', str(P.parent/'tools/ngspice/bin/ngspice'))
OUT = P/'results_bias'; OUT.mkdir(exist_ok=True)
CH = (P.parent/'work/rev0.1/channel.cir').read_text()  # Rev 0.1 circuit, the basis of this comparison

E24 = [1.0,1.1,1.2,1.3,1.5,1.6,1.8,2.0,2.2,2.4,2.7,3.0,3.3,3.6,3.9,4.3,4.7,5.1,5.6,6.2,6.8,7.5,8.2,9.1]
# BZX79 values considered for variant P. TC and rdif are ASSUMED representative values for a
# study at about 5 mA, not datasheet guarantees (BZX79 low-voltage SZ spans roughly -3.5..+0.2 mV/K).
ZENERS = {2.4:(-2.0e-3,90), 2.7:(-2.0e-3,80), 3.0:(-2.1e-3,80), 3.3:(-2.2e-3,80), 3.6:(-2.2e-3,80), 3.9:(-2.0e-3,75),
          4.3:(-1.6e-3,70), 4.7:(-0.8e-3,60), 5.1:(-0.2e-3,40), 5.6:(1.2e-3,15), 6.2:(2.3e-3,8), 6.8:(3.0e-3,10)}

BIAS_A = '''DZ1 BC BP ZSEL TEMP={TB}
Q8 BC BB BN BD139A TEMP={TS}
R12 BC BB 1k
R13 BB BN 47k
R14 BB BW 130
RV1 BW BN {RV}'''
BIAS_P = '''DZ1 BC BP ZSEL TEMP={TB}
Q8 BC BB BN BD139A TEMP={TS}
R12 BC BB 2.7k
R13 BB BN 1.2k
R14 BB BW 820
RV1 BW BN {RV}'''
BIAS_B = '''DB1 BP BX1 D4148 TEMP={TB}
DB2 BX1 BC D4148 TEMP={TB}
Q8 BC BB BN BD139A TEMP={TS}
R12 BC BB 3.9k
R13 BB BN {R2B}
QCS BB BREF BCE BC546B TEMP={TB}
RE BCE BW {RE}
RV1 BW VN {RV}
DLED BREF VN LEDR TEMP={TB}
QLF BREF TREF BLE BC556B TEMP={TB}
RLF VP BLE 680'''
VARIANTS = {'A':BIAS_A, 'P':BIAS_P, 'B':BIAS_B}
RV_MAX = {'A':2000, 'P':2000, 'B':200}
def rvmax(variant, extra):
    # Variant B: trim rheostat sized to the selected RE (>= ~15 % of RE) from stocked 200R / 500R / 2k parts.
    if variant != 'B': return RV_MAX[variant]
    return 200 if extra['RE'] <= 1300 else 500 if extra['RE'] <= 3300 else 2000

def amp(variant, mos):
    c = CH
    blk = re.search(r'DZ1 BC BP Z4V3\n.*?RV1 BW BN \{RV\}', c, re.S).group(0)
    c = c.replace(blk, VARIANTS[variant])
    # Board-temperature parts: CCS reference, active load, drivers.
    c = c.replace('Q7 BP TREF VCE BC556B', 'Q7 BP TREF VCE BC556B TEMP={TB}')
    c = c.replace('D1 TDI TREF D4148', 'D1 TDI TREF D4148 TEMP={TB}').replace('D2 VP TDI D4148', 'D2 VP TDI D4148 TEMP={TB}')
    c = c.replace('TEMP={TD}', 'TEMP={TB}')
    # Imposed threshold shift (spread + temperature) as a gate series source; positive DVN/DVP = higher |Vth|.
    n, p = ('irf540n_k', 'irf9540n_k') if mos == 'infineon' else ('IRF540_APPROX', 'IRF9540_APPROX')
    c = c.replace('XQ11 VP GN SN IRF540_APPROX', f'VTHN GN GNI DC {{DVN}}\nXQ11 VP GNI SN {n}')
    c = c.replace('XQ12 VN GP SP IRF9540_APPROX', f'VTHP GPI GP DC {{DVP}}\nXQ12 VN GPI SP {p}')
    return c

def infineon_lib():
    n = (P/'models/infineon/irf540n.spi').read_text()
    n = n[:n.index('.ENDS irf540n')+len('.ENDS irf540n')]
    n = n.replace('.SUBCKT irf540n', '.SUBCKT irf540n_k').replace('.ENDS irf540n', '.ENDS irf540n_k').replace('KP=112.25', 'KP={112.25*KPS}')
    p = (P/'models/infineon/irf9540npbf.spi').read_text()
    p = p.replace('.SUBCKT irf9540npbf', '.SUBCKT irf9540n_k').replace('.ENDS irf9540npbf', '.ENDS irf9540n_k').replace('KP=6.90462', 'KP={6.90462*KPS}')
    return n + '\n' + p

# Red LED model LEDR (about 1.85 V at 1 mA, about -1.8 mV/K) is defined in models/devices.lib.
ZSEL = '.model ZSEL D(IS=1n N=1.5 RS={RZ} BV={VZ} IBV=5m CJO=100p TBV1={TCZ/VZ})'

DEFAULTS = dict(R2B=1000, VS=15, RV=100, RE=1000, VZ=4.3, TCZ=-1.6e-3, RZ=15, LEDEG=2.3,
                TS=27, TB=27, DVN=0, DVP=0, KPS=1, KPN=20, KPP=7.07, VTON=3.4, VTOP=-3.77, CC='330p')

def deck(name, variant, mos, prm, control, src='DC 0', load='RL SPK 0 8', vp=None, vn=None):
    q = dict(DEFAULTS); q.update(prm)
    ps = ' '.join(f'{k}={v}' for k, v in q.items())
    text = f'''MOSFETAmp2 bias study {name} variant {variant} models {mos}
.param {ps}
.include models/devices.lib
{infineon_lib()}
{ZSEL}
{amp(variant, mos).split(".include models/devices.lib",1)[1].split(".param",1)[0]}
VP VP 0 {vp or '{VS}'}
VN VN 0 {vn or '{-VS}'}
VIN IN 0 {src}
XA IN OUT VP VN 0 AMP
LOUT OUT SPK 0.7u
RLDCR OUT SPK 10
{load}
.options reltol=1e-5 abstol=1e-10 vntol=1e-7
.control
set noaskquit
set wr_singlescale
set wr_vecnames
{control}
quit
.endc
.end
'''
    f = OUT/(name+'.cir'); f.write_text(text)
    subprocess.run([BIN, '-b', '-o', str(OUT/(name+'.log')), str(f)], capture_output=True, timeout=120, cwd=P)
    log = (OUT/(name+'.log')).read_text()
    if re.search(r'(Error|Timestep too small|doAnalyses:|unknown parameter)', log):
        raise RuntimeError(name+' failed: '+log[-2500:])
    return log

VEC = ['v(out)','v(xa.sn)','v(xa.sp)','v(xa.bp)','v(xa.bn)','v(xa.bb)','i(vp)','i(vn)']
def op(name, variant, mos, prm):
    log = deck(name, variant, mos, prm, 'op\nprint '+' '.join(VEC))
    d = {k: float(re.search(re.escape(k)+r'\s*=\s*([-+\deE.]+)', log).group(1)) for k in VEC}
    d['iq_n'] = (d['v(xa.sn)']-d['v(out)'])/.33
    d['iq_p'] = (d['v(out)']-d['v(xa.sp)'])/.33
    d['spread'] = d['v(xa.bp)']-d['v(xa.bn)']
    return d

# Device corners: datasheet VGS(th) window 2..4 V at 250 uA, relative to each model's VTO.
def corners(mos):
    n0, p0 = (3.58173, 3.74034) if mos == 'infineon' else (3.4, 3.77)
    return {'nominal':(0,0), 'low_2V_2V':(2-n0, 2-p0), 'high_4V_4V':(4-n0, 4-p0),
            'N2V_P4V':(2-n0, 4-p0), 'N4V_P2V':(4-n0, 2-p0)}

def thermal(tc, tj, ts, tb, dvn0, dvp0):
    """Imposed MOSFET threshold slope tc (V/K, negative) and mobility T^-1.5; sensor ts; board tb."""
    return dict(DVN=dvn0+tc*(tj-27), DVP=dvp0+tc*(tj-27), KPS=((tj+273.15)/300.15)**-1.5, TS=ts, TB=tb)

SCEN = {  # name: (Tj, Tsensor, Tboard) in degC; ambient = 27
    'cold_calibration': (27, 27, 27),
    'warm_idle_sink+20': (49, 47, 37),
    'hot_idle_sink+40': (69, 67, 42),
    'lag_after_burst_sink+20_die+9': (56, 47, 37),
    'burst_start_die+15_sensor_cold': (42, 27, 27),
    'ambient+15_all': (42, 42, 42),
    'board_only+15': (27, 27, 42),
}

def calibrate(variant, mos, base, target=0.05, tag=''):
    """Find the trim giving `target` P current. For P/B first choose the select-on-test part."""
    f = lambda rv, extra: op(f'cal_{variant}{tag}', variant, mos, {**base, **extra, 'RV': rv})['iq_p'] - target
    if variant == 'A':
        extra = {'VZ':4.3, 'TCZ':-1.6e-3, 'RZ':15}
        lo, hi = f(0, extra), f(RV_MAX['A'], extra)
        if lo < 0 or hi > 0: return None, extra, (lo+target, hi+target)
        return brentq(f, 0, RV_MAX['A'], args=(extra,), xtol=0.02), extra, (lo+target, hi+target)
    best = None
    choices = [{'VZ':v, 'TCZ':t, 'RZ':r} for v,(t,r) in ZENERS.items()] if variant == 'P' else \
              [{'RE':round(m*10**e)} for e in (2,3,4) for m in E24 if 330 <= m*10**e <= 15000]
    for extra in choices:
        lo, hi = f(0, extra), f(rvmax(variant, extra), extra)
        if lo >= 0 >= hi:
            rv = brentq(f, 0, rvmax(variant, extra), args=(extra,), xtol=0.02)
            score = abs(rv/rvmax(variant, extra) - 0.5)
            if best is None or score < best[3]: best = (rv, extra, (lo+target, hi+target), score)
    return (best[0], best[1], best[2]) if best else (None, None, None)

def main(mos='infineon', variants=('A', 'P', 'B')):
    res = {'models':mos, 'status':'IMPOSED MOSFET THERMAL BEHAVIOUR - DEVELOPMENT EVIDENCE ONLY', 'variants':{}}
    for var in variants:
        res['variants'][var] = {}
        for cname, (dvn0, dvp0) in corners(mos).items():
            base = thermal(0, 27, 27, 27, dvn0, dvp0)
            rv, extra, rng = calibrate(var, mos, base, tag='_'+cname)
            entry = {'trim_ohm':rv, 'trim_pot_ohm':None if extra is None else rvmax(var, extra), 'select_on_test':extra, 'iq_p_at_trim_ends_mA':None if rng is None else [1e3*x for x in rng]}
            if rv is None:
                res['variants'][var][cname] = entry; print(var, cname, 'cannot reach 50 mA', rng, flush=True); continue
            cal = op(f'calop_{var}_{cname}', var, mos, {**base, **extra, 'RV':rv})
            entry['spread_V'] = cal['spread']
            if var == 'B': entry['multiplier_k_nominal'] = 1+3.9/1.0
            entry['open_wiper_iq_p_mA'] = 1e3*op(f'open_{var}_{cname}', var, mos, {**base, **extra, 'RV':1e9})['iq_p']
            entry['thermal'] = {}
            for tc in [-3e-3, -4.7e-3, -6e-3]:
                row = {}
                for sname, (tj, ts, tb) in SCEN.items():
                    d = op(f't_{var}_{cname}_{int(-tc*1e4)}_{sname[:12]}', var, mos, {**thermal(tc, tj, ts, tb, dvn0, dvp0), **extra, 'RV':rv})
                    row[sname] = round(1e3*d['iq_p'], 1)
                entry['thermal'][f'{tc*1e3:.1f}mV_per_K'] = row
            entry['rails'] = {str(v): round(1e3*op(f'rail_{var}_{cname}_{v}', var, mos, {**base, **extra, 'RV':rv, 'VS':v})['iq_p'], 1) for v in [12.5, 15, 20.6]}
            res['variants'][var][cname] = entry
            print(var, cname, json.dumps({k:entry[k] for k in ('trim_ohm','select_on_test','open_wiper_iq_p_mA','rails')}), flush=True)
            print('   ', json.dumps(entry['thermal']), flush=True)
    (OUT/f'bias_study_{mos}.json').write_text(json.dumps(res, indent=1))
    return res

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'infineon')
