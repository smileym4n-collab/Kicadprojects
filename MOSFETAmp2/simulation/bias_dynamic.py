#!/usr/bin/env python3
"""Variant B follow-up: k (R13) selection versus imposed MOSFET threshold slope, clipping
recovery, distortion and loop-gain comparison against variant A, using the Infineon models.
Development evidence only; see docs/BIAS_STUDY.md. Run after bias_study.py."""
import json, re
import numpy as np
from scipy.optimize import brentq
import bias_study as b

OUT = b.OUT
R = json.loads((OUT/'bias_study_infineon.json').read_text())

def trim(var, corner='nominal'):
    e = R['variants'][var][corner]
    return {**e['select_on_test'], 'RV': e['trim_ohm']}

def k_table():
    """For each slope, the R13 (k = 1 + 3k9/R13) that holds 50 mA from cold to sink+40 K (nominal pair)."""
    out = {}
    base = b.thermal(0, 27, 27, 27, 0, 0)
    for tc in [-3e-3, -4e-3, -4.7e-3, -5.5e-3, -6e-3, -7e-3]:
        def hot_minus_cold(r2):
            rv, extra, _ = b.calibrate('B', 'infineon', {**base, 'R2B': r2}, tag='_k')
            if rv is None: raise ValueError
            tj, ts, tb = b.SCEN['hot_idle_sink+40']
            return b.op('k_hot', 'B', 'infineon', {**b.thermal(tc, tj, ts, tb, 0, 0), **extra, 'R2B': r2, 'RV': rv})['iq_p'] - 0.05
        try:
            r2 = brentq(hot_minus_cold, 560, 2700, xtol=5)
            out[f'{tc*1e3:.1f}'] = {'R13_ohm': round(r2), 'k': round(1+3900/r2, 2), 'sensor_mV_per_K_approx': round(-1.93*(1+3900/r2), 1)}
        except ValueError:
            out[f'{tc*1e3:.1f}'] = 'outside 560R..2k7'
        print('k_table', tc, out[f'{tc*1e3:.1f}'], flush=True)
    return out

def tran(name, var, amp, f=1000, cycles=6, load='RL SPK 0 8', vs=15):
    step = min(1/(f*800), 1e-6)
    ctl = f'tran {step} {cycles/f} 0 {step}\nwrdata {b.OUT.name}/{name}.txt v(in) v(out) v(xa.bp) v(xa.bn) v(xa.sn) v(xa.sp)'
    b.deck(name, var, 'infineon', {**trim(var), 'VS': vs}, ctl, src=f'SIN(0 {amp} {f})', load=load)
    return np.loadtxt(OUT/f'{name}.txt', skiprows=1)

def harmonics(a, f, cycles=2):
    t = np.linspace(a[-1,0]-cycles/f, a[-1,0], 16384, endpoint=False)
    y = np.interp(t, a[:,0], a[:,2])
    A = np.column_stack([np.ones(len(t))]+[z for k in range(1,11) for z in (np.sin(2*np.pi*k*f*t), np.cos(2*np.pi*k*f*t))])
    c = np.linalg.lstsq(A, y, rcond=None)[0]; h = np.hypot(c[1::2], c[2::2])
    return {'vpk': float(h[0]), 'thd_2_10_percent': float(100*np.linalg.norm(h[1:])/h[0])}

def clipping(var):
    """1 kHz: 2 cycles at 1.6 Vpk input (hard clipping), then 0.2 Vpk. Report spreader excursion and recovery."""
    name = f'clip_{var}'
    tt = np.arange(0, 5e-3+1e-9, 2e-6)
    vin = np.where(tt < 2e-3, 1.6, 0.2)*np.sin(2*np.pi*1000*tt)
    src = 'PWL(' + '\n+ '.join(f'{x:.6g} {y:.6g}' for x, y in zip(tt, vin)) + ')'
    step = 1e-6
    ctl = f'tran {step} 5m 0 {step}\nwrdata {b.OUT.name}/{name}.txt v(in) v(out) v(xa.bp) v(xa.bn) v(xa.sn) v(xa.sp)'
    b.deck(name, var, 'infineon', {**trim(var)}, ctl, src=src)
    a = np.loadtxt(OUT/f'{name}.txt', skiprows=1)
    t, sp = a[:,0], a[:,3]-a[:,4]
    q = R['variants'][var]['nominal']['spread_V']  # DC operating point at the same trim
    post = (t >= 2e-3) & (t < 2.5e-3)
    iq_n = (a[:,5]-a[:,2])/0.33; iq_p = (a[:,2]-a[:,6])/0.33
    return {'quiescent_spread_V': q, 'spread_min_V': float(sp.min()), 'spread_max_V': float(sp.max()),
            'max_spread_deviation_first_500us_after_clipping_mV': float(1e3*np.abs(sp[post]-q).max()),
            'n_current_min_during_clip_A': float(iq_n[(t>0.2e-3)&(t<2e-3)].min())}

def loop(var, load):
    ch_amp = b.amp(var, 'infineon').replace('Q1 C1N FB E1', 'VTEST FBI FB DC 0 AC 1\nQ1 C1N FBI E1')
    orig = b.amp
    b.amp = lambda v, m: ch_amp
    try:
        name = f'loop_{var}_{load[0]}'
        b.deck(name, var, 'infineon', trim(var), f'ac dec 100 1 100meg\nlet ret=-v(xa.fb)/v(xa.fbi)\nwrdata {b.OUT.name}/{name}.txt ret', src='DC 0 AC 0', load=load[1])
    finally:
        b.amp = orig
    a = np.loadtxt(OUT/f'{name}.txt', skiprows=1); z = a[:,1]+1j*a[:,2]
    db = 20*np.log10(abs(z)); ph = np.unwrap(np.angle(z))*180/np.pi
    i = np.where((db[:-1] >= 0) & (db[1:] < 0))[0][0]; u = -db[i]/(db[i+1]-db[i])
    return {'crossover_hz': float(np.exp(np.log(a[i,0])+u*np.log(a[i+1,0]/a[i,0]))), 'phase_margin_deg': float(180+ph[i]+u*(ph[i+1]-ph[i]))}

if __name__ == '__main__':
    res = {'status': 'INFINEON MODPEX MOSFET MODELS; AUTHORED BD139/140, LED, ZENER MODELS - DEVELOPMENT EVIDENCE ONLY'}
    res['k_table_variant_B'] = k_table()
    for var in ['A', 'B']:
        res[var] = {'sine_1k_0.5Vpk': harmonics(tran(f'sine1k_{var}', var, 0.5), 1000),
                    'sine_20k_0.5Vpk': harmonics(tran(f'sine20k_{var}', var, 0.5, f=20000, cycles=20), 20000),
                    'clipping_burst': clipping(var),
                    'loop': {n: loop(var, (n, l)) for n, l in [('8R', 'RL SPK 0 8'), ('reactive', 'RL REAC 0 8\nLL SPK REAC 0.5m\nCL SPK 0 100n')]}}
        print(var, json.dumps(res[var]), flush=True)
    (OUT/'bias_dynamic_infineon.json').write_text(json.dumps(res, indent=1))
