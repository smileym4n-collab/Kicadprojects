#!/usr/bin/env python3
"""Run every ClassA2 Rev A simulation experiment and write results/summary.json plus docs/plots/*.png.

Needs numpy + matplotlib (PYTHONPATH may point at a site-packages folder holding them).
Models are author approximations (models/classa2_bjt.lib). Results are engineering
estimates for trend and margin checking, not hardware performance claims."""
import sys, json, pathlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import run

P = pathlib.Path(__file__).resolve().parent
PLOTS = P.parent / 'docs' / 'plots'; PLOTS.mkdir(parents=True, exist_ok=True)
RV_WARM = 78          # trimmer ohms giving ~0.70 A at the warm reference temperatures below
WARM = 'TS=46 TD=48 TO=63'   # heatsink ~45 C: sensor +1 K, drivers +3 K, output junctions +18 K
INST = f'RV={RV_WARM} {WARM}'
S = {}

def plot(name):
    plt.tight_layout(); plt.savefig(PLOTS / f'{name}.png', dpi=110); plt.close()

# ---------------------------------------------------------------- DC / bias
DEV = ['@q.xa.q12[ic]', '@q.xa.q13[ic]', '@q.xa.q10[ic]', '@q.xa.q11[ic]', '@q.xa.q7[ic]', '@q.xa.q8[ic]',
       '@q.xa.q1[ic]', '@q.xa.q3[ic]', '@q.xa.q9[ic]', '@q.xa.q5[ic]', '@q.xa.q6[ic]']
keep = run.OPV
run.OPV = keep + DEV + ['v(xa.c1n)', 'v(xa.c3p)', 'v(xa.e1)', 'v(xa.e3)', 'v(xa.b9)']
d = run.op('op_nominal', INST, vs=15.6)
run.OPV = keep
vp, vn, out = d['v(vp)'] if 'v(vp)' in d else 15.6, -15.6, d['v(xa.out)']
diss = {
    'Q12 2SA1941': abs(d['@q.xa.q12[ic]']) * (15.6 - d['v(xa.ep)']),
    'Q13 2SC5198': abs(d['@q.xa.q13[ic]']) * (d['v(xa.en)'] + 15.6),
    'Q10 BD139': abs(d['@q.xa.q10[ic]']) * (d['v(xa.bop)'] - d['v(xa.ep)']),
    'Q11 BD140': abs(d['@q.xa.q11[ic]']) * (d['v(xa.en)'] - d['v(xa.bon)']),
    'Q7 2SA1145': abs(d['@q.xa.q7[ic]']) * (d['v(xa.e7)'] - d['v(xa.vbp)']),
    'Q8 2SC2705': abs(d['@q.xa.q8[ic]']) * (d['v(xa.vbn)'] - d['v(xa.e8)']),
    'Q1 2SC2240': abs(d['@q.xa.q1[ic]']) * (d['v(xa.c1n)'] - d['v(xa.e1)']),
    'Q3 2SA970': abs(d['@q.xa.q3[ic]']) * (d['v(xa.e3)'] - d['v(xa.c3p)']),
    'Q9 BD139': abs(d['@q.xa.q9[ic]']) * d['V_bias'],
    'R22/R25 each': d['Iq_top'] ** 2 * 0.33,
}
S['op_nominal'] = dict(rails=15.6, Iq_top=d['Iq_top'], Iq_bot=d['Iq_bot'], offset_mV=d['offset_mV'],
                       V_bias=d['V_bias'], I_vas=d['I_vas_p'], I_tail_n=d['I_tail_n'], I_tail_p=d['I_tail_p'],
                       rail_current=-d['i(vp)'], dissipation_W=diss)

sweep = []
for rv in [0, 25, 50, 78, 100, 150, 200, 300, 400, 500]:
    o = run.op('rv', f'RV={rv+0.01} {WARM}', vs=15.6)
    sweep.append((rv, o['Iq_top']))
S['bias_vs_RV1'] = sweep
plt.figure(figsize=(5, 3.2)); plt.plot(*zip(*sweep), 'o-')
plt.xlabel('RV1 base-emitter leg setting (ohm)'); plt.ylabel('Iq (A)'); plt.grid(alpha=.3)
plt.title('Bias vs RV1 (warm, +/-15.6 V)'); plot('bias_vs_rv1')

temp = []
for ts in [25, 35, 45, 55, 65]:
    o = run.op('th', f'RV={RV_WARM} TS={ts+1} TD={ts+3} TO={ts+18}', vs=15.6)
    temp.append((ts, o['Iq_top'], o['offset_mV']))
S['bias_vs_heatsink'] = temp
base = run.op('thb', INST, vs=15.6)['Iq_top']
sens = {}
for k, inst in [('sensor Q9', f'RV={RV_WARM} TS=56 TD=48 TO=63'), ('drivers Q10/Q11', f'RV={RV_WARM} TS=46 TD=58 TO=63'),
                ('outputs Q12/Q13', f'RV={RV_WARM} TS=46 TD=48 TO=73')]:
    sens[k] = (run.op('ths', inst, vs=15.6)['Iq_top'] - base) * 1e3 / 10
S['bias_tempco_mA_per_K'] = sens
rails = []
for vs in [14.0, 14.5, 15.6, 16.5, 17.5, 20.2]:
    o = run.op('vs', INST, vs=vs); rails.append((vs, o['Iq_top'], o['offset_mV']))
S['bias_vs_rails'] = rails
S['offset_trim'] = [(x, run.op('os', f'{INST} OS={x}', vs=15.6)['offset_mV']) for x in [0, 0.25, 0.5, 0.75, 1]]

# ---------------------------------------------------------------- AC
f, H = run.ac('cl', INST, vs=15.6)
g = 20*np.log10(abs(H)); g0 = g[np.argmin(abs(f-1e3))]
S['closed_loop'] = dict(gain_dB=g0, gain_VV=10**(g0/20), dB_10Hz=g[np.argmin(abs(f-10))]-g0, dB_20Hz=g[np.argmin(abs(f-20))]-g0,
                        dB_20kHz=g[np.argmin(abs(f-2e4))]-g0, f_3dB_hi=float(f[np.where((g < g0-3) & (f > 100))[0][0]]),
                        f_3dB_lo=float(f[np.where(g > g0-3)[0][0]]), peaking_dB=float(g.max()-g0))
plt.figure(figsize=(5.5, 3.2)); plt.semilogx(f, g); plt.xlim(1, 1e7); plt.ylim(g0-30, g0+3)
plt.xlabel('Hz'); plt.ylabel('dB'); plt.grid(alpha=.3, which='both'); plt.title('Closed-loop response, 8 ohm'); plot('closed_loop')

LOADS = [('8R', 'RL SPK 0 8'), ('4R', 'RL SPK 0 4'), ('open', 'RL SPK 0 1e6'), ('8R//1u', 'RL SPK 0 8\nCL SPK 0 1u'),
         ('open//100n', 'RL SPK 0 1e6\nCL SPK 0 100n'), ('open//470n', 'RL SPK 0 1e6\nCL SPK 0 470n'),
         ('open//1u', 'RL SPK 0 1e6\nCL SPK 0 1u'), ('open//2u2', 'RL SPK 0 1e6\nCL SPK 0 2.2u'), ('open//10u', 'RL SPK 0 1e6\nCL SPK 0 10u')]
lg = {}
fig, ax = plt.subplots(2, 1, figsize=(5.5, 5), sharex=True)
for nm, load in LOADS:
    f, T = run.ac('lg', INST, load=load, lg=True, vs=15.6)
    m = run.margins(f, T)
    lg[nm] = dict(fc_kHz=m['fc']/1e3, pm_deg=m['pm'], gm_dB=m['gm'][0] if m['gm'] else None,
                  gm_f_MHz=m['gm'][1]/1e6 if m['gm'] else None, T_1k_dB=m['T1k'], T_20k_dB=m['T20k'])
    if nm in ('8R', 'open//1u', 'open//10u'):
        ax[0].semilogx(f, 20*np.log10(abs(T)), label=nm); ax[1].semilogx(f, np.degrees(np.unwrap(np.angle(T))), label=nm)
S['loop_gain'] = lg
ax[0].set_ylabel('|T| dB'); ax[0].grid(alpha=.3, which='both'); ax[0].legend(); ax[0].set_ylim(-40, 100)
ax[1].set_ylabel('phase deg'); ax[1].set_xlabel('Hz'); ax[1].grid(alpha=.3, which='both'); ax[1].set_xlim(10, 5e7)
ax[0].set_title('Loop gain (voltage injection at OUT)'); plot('loop_gain')

# ---------------------------------------------------------------- distortion / power
thd = []
for P_ in [0.1, 0.5, 1, 2, 3, 5, 6, 7, 7.5, 8, 9, 10]:
    r = run.thd('thd', (16*P_)**.5, INST, vs=15.6, rip=1.0)
    thd.append(dict(P=P_, thd=r['thd'], itop_min=r['itop_min'], ibot_min=r['ibot_min']))
S['thd_1k_8R_nominal_10mF'] = thd
S['thd_20k'] = {f'{p}W': run.thd('thd20', (16*p)**.5, INST, vs=15.6, f0=2e4, cycles=10, rip=1.0)['thd'] for p in [1, 5, 7.5]}
S['thd_1k_4R_informative'] = {f'{p}W': run.thd('thd4', (8*p)**.5, INST, vs=15.6, load='RL SPK 0 4', rip=1.0)['thd'] for p in [1, 5, 10]}
cl = [t for t in thd if min(t['itop_min'], t['ibot_min']) > 0.02]
S['class_A_limit_W'] = max(t['P'] for t in cl)
plt.figure(figsize=(5.5, 3.2)); plt.loglog([t['P'] for t in thd], [t['thd'] for t in thd], 'o-')
plt.axvline(S['class_A_limit_W'], ls='--', c='gray'); plt.text(S['class_A_limit_W'], max(t['thd'] for t in thd), ' Class-A limit', va='top')
plt.xlabel('W into 8 ohm'); plt.ylabel('THD % (model)'); plt.grid(alpha=.3, which='both'); plt.title('1 kHz THD, +/-15.6 V, 1 Vpp ripple'); plot('thd_vs_power')

def clip(vs, rip, load='RL SPK 0 8', R=8):
    lo, hi = 8.0, 17.5
    for _ in range(9):
        m = (lo+hi)/2
        if run.thd('clip', m, INST, vs=vs, rip=rip, load=load, cycles=4)['thd'] > 1.0: hi = m
        else: lo = m
    return dict(vpk=lo, W=lo**2/2/R)
S['power_1pct_THD'] = {'low mains 216 V, 10 mF (14.55 V, 1 Vpp)': clip(14.55, 1.0), 'nominal 230 V, 10 mF (15.63 V, 1 Vpp)': clip(15.63, 1.0),
                       'nominal 230 V, 22 mF (15.66 V, 0.45 Vpp)': clip(15.66, 0.45), 'high mains 253 V, 10 mF (17.4 V, 1 Vpp)': clip(17.4, 1.0)}

# ---------------------------------------------------------------- transient stability
sq = {}
for nm, load in LOADS:
    r = run.square('sq', 2, INST, load=load, vs=15.6)
    sq[nm] = dict(overshoot_pct=float(r['overshoot_pct']), residual_pp_V=float(r['settled_pp']), rise_ns=float(r['rise_ns']))
S['square_10k_2Vpk'] = sq
r = run.square('sq8', 8, INST, vs=15.6); S['square_10k_8Vpk_8R'] = {k: float(v) for k, v in r.items()}
fig, ax = plt.subplots(1, 1, figsize=(5.5, 3.2))
for nm, load in [('8R', 'RL SPK 0 8'), ('8R//1u', 'RL SPK 0 8\nCL SPK 0 1u'), ('open//2u2', 'RL SPK 0 1e6\nCL SPK 0 2.2u')]:
    run.square('sqp', 2, INST, load=load, vs=15.6)
    a = np.loadtxt(run.R/'sqp.txt', skiprows=1); s = (a[:, 0] > 2.2e-4) & (a[:, 0] < 2.9e-4)
    ax.plot((a[s, 0]-2.2e-4)*1e6, a[s, 1], label=nm)
ax.set_xlabel('us'); ax.set_ylabel('V(SPK)'); ax.grid(alpha=.3); ax.legend(); ax.set_title('10 kHz square, 2 Vpk'); plot('square_wave')
# intrinsic slew (input RC filter bypassed)
run.AMP, amp_keep = run.AMP.replace('R2   INA INB 1k', 'R2   INA INB 1').replace('C2   INB 0   470p', 'C2   INB 0   1p'), run.AMP
run.square('slew', 10, INST, vs=15.6, tr=10e-9, f0=20e3)
a = np.loadtxt(run.R/'slew.txt', skiprows=1); dv = np.diff(a[:, 2])/np.diff(a[:, 0])
S['slew_V_per_us_no_input_filter'] = dict(rise=float(dv.max()/1e6), fall=float(-dv.min()/1e6))
run.AMP = amp_keep

# ---------------------------------------------------------------- power cycling
V = 15.6
pc = {}
for k, (p, n, ts, uic) in {
        'startup symmetric (40 ms ramp)': (f'0 0 1m 0 41m {V} 3 {V}', f'0 0 1m 0 41m {-V} 3 {-V}', 3.0, True),
        'startup +rail leads by 10 ms': (f'0 0 1m 0 31m {V} 3 {V}', f'0 0 11m 0 51m {-V} 3 {-V}', 3.0, True),
        'shutdown symmetric (110 ms decay)': (f'0 {V} 0.4 {V} 0.51 0 1.0 0', f'0 {-V} 0.4 {-V} 0.51 0 1.0 0', 1.0, False),
        'shutdown -rail collapses first': (f'0 {V} 0.4 {V} 0.55 0 1.0 0', f'0 {-V} 0.4 {-V} 0.47 0 1.0 0', 1.0, False)}.items():
    t, v, vpp, vnn, iq = run.rails_tran('pwr', p, n, ts, f'RV={RV_WARM} TS=30 TD=30 TO=30', step=50e-6, uic=uic)
    if not uic:
        s = t > 0.35; t, v, iq = t[s], v[s], iq[s]
    i = np.argmax(abs(v))
    pc[k] = dict(peak_V=float(v[i]), t_peak_ms=float(t[i]*1e3), end_mV=float(v[-1]*1e3), Iq_max=float(iq.max()))
    if k.startswith('startup symmetric'):
        plt.figure(figsize=(5.5, 3.2)); plt.plot(t, v*1e3); plt.xlabel('s'); plt.ylabel('V(SPK) mV'); plt.grid(alpha=.3)
        plt.title('Power-up from discharged capacitors, 8 ohm'); plot('startup')
S['power_cycle'] = pc

# ---------------------------------------------------------------- gain spread
cases = {'nominal': {}, 'outputs hFE 55': dict(Q2SC5198=55, Q2SA1941=55), 'outputs hFE 160': dict(Q2SC5198=160, Q2SA1941=160),
         'outputs NPN 160 / PNP 55': dict(Q2SC5198=160, Q2SA1941=55), 'drivers hFE 40': dict(QBD139=40, QBD140=40),
         'drivers hFE 250': dict(QBD139=250, QBD140=250), 'VAS hFE 80': dict(Q2SC2705=80, Q2SA1145=80),
         'input GR200 / BL700': dict(Q2SC2240GR=200, Q2SA970BL=700), 'input GR400 / BL350': dict(Q2SC2240GR=400, Q2SA970BL=350),
         'everything at minimum': dict(Q2SC5198=55, Q2SA1941=55, QBD139=40, QBD140=40, Q2SC2705=80, Q2SA1145=80, Q2SC2240GR=200, Q2SA970BL=350)}
bs = {}
for k, bf in cases.items():
    lib = run.lib_beta(**bf) if bf else run.LIB
    o = run.op('b', INST, vs=15.6, lib=lib)
    keep_lib, run.LIB = run.LIB, lib
    try:
        f, T = run.ac('blg', INST, lg=True, vs=15.6); m = run.margins(f, T)
        t5 = run.thd('bthd', 8.94, INST, vs=15.6)['thd']
    finally:
        run.LIB = keep_lib
    bs[k] = dict(Iq=o['Iq_top'], offset_mV=o['offset_mV'], pm_deg=m['pm'], fc_kHz=m['fc']/1e3, thd_5W=t5)
S['gain_spread'] = bs

# ---------------------------------------------------------------- noise
nlog = run.run('noise', run.deck('noise', INST, vs=15.6, src='DC 0 AC 1',
               control='noise v(spk) vin dec 20 20 20k\nsetplot noise2\nprint onoise_total inoise_total'))
S['noise'] = dict(output_uV_20_20k=run.val(nlog, 'onoise_total')*1e6, input_nV_rms=run.val(nlog, 'inoise_total')*1e9)
S['noise']['snr_dB_re_7W5'] = 20*np.log10((7.5*8)**.5 / (S['noise']['output_uV_20_20k']*1e-6))

(P/'results'/'summary.json').write_text(json.dumps(S, indent=1, default=float))
print(json.dumps(S, indent=1, default=lambda x: round(float(x), 4)))
