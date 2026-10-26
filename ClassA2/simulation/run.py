#!/usr/bin/env python3
"""ClassA2 ngspice harness. Run from anywhere: python3 run.py <experiment...>.
Uses the ngspice 47 build bundled in ../../MOSFETAmp2/tools/ngspice unless NGSPICE is set.
All models are author approximations (models/classa2_bjt.lib); see docs/SIMULATION.md."""
import os, sys, re, json, pathlib, subprocess
P = pathlib.Path(__file__).resolve().parent
BIN = os.environ.get('NGSPICE', str(P.parents[1] / 'MOSFETAmp2/tools/ngspice/bin/ngspice'))
R = P / 'results'; R.mkdir(exist_ok=True)
AMP = (P / 'amp.cir').read_text()
LIB = (P / 'models/classa2_bjt.lib').read_text()

def deck(name, inst='', src='DC 0 AC 1', load='RL SPK 0 8', vs=15.5, vsn=None, control='op', extra='', lib=None, rip=0):
    vsn = vs if vsn is None else vsn
    rp = f' SIN({vs} {-rip/2} 100)' if rip else ''
    rn = f' SIN({-vsn} {rip/2} 100)' if rip else ''
    return f'''ClassA2 {name}
{lib or LIB}
{AMP}
VP VP 0 DC {vs}{rp}
VN VN 0 DC {-vsn}{rn}
VIN IN 0 {src}
XA IN SPK VP VN AMP {inst}
{load}
{extra}
.options reltol=1e-4 abstol=1e-11 vntol=1e-7 itl1=500 itl4=200
.control
set noaskquit
set wr_singlescale
set wr_vecnames
{control}
quit
.endc
.end
'''

def run(name, d, timeout=600):
    (R / (name + '.cir')).write_text(d)
    subprocess.run([BIN, '-b', '-o', str(R / (name + '.log')), str(R / (name + '.cir'))], capture_output=True, timeout=timeout)
    log = (R / (name + '.log')).read_text(errors='ignore')
    if re.search(r'(Error[: ]|Timestep too small|doAnalyses:|unknown parameter|singular matrix)', log, re.I):
        raise RuntimeError(name + ' failed:\n' + log[-2500:])
    return log

def val(log, key):
    m = re.search(re.escape(key) + r'\s*=\s*([-+\deE.]+)', log)
    return float(m.group(1)) if m else float('nan')

OPV = ['v(spk)', 'v(xa.out)', 'v(xa.ep)', 'v(xa.en)', 'v(xa.vbp)', 'v(xa.vbn)', 'v(xa.vpf)', 'v(xa.vnf)',
       'v(xa.e7)', 'v(xa.e8)', 'v(xa.tn)', 'v(xa.tp)', 'v(xa.c1n)', 'v(xa.c3p)', 'v(xa.e5)', 'v(xa.e6)',
       'v(xa.bop)', 'v(xa.bon)', 'v(xa.b10)', 'v(xa.b11)', 'v(xa.fb)', 'v(xa.inb)', 'i(vp)', 'i(vn)']

def op(name, inst='', vs=15.5, vsn=None, lib=None, load='RL SPK 0 8'):
    log = run(name, deck(name, inst, vs=vs, vsn=vsn, lib=lib, load=load, control='op\nprint ' + ' '.join(OPV)))
    d = {k: val(log, k) for k in OPV}
    d['Iq_top'] = (d['v(xa.ep)'] - d['v(xa.out)']) / 0.33
    d['Iq_bot'] = (d['v(xa.out)'] - d['v(xa.en)']) / 0.33
    d['I_vas_p'] = (d['v(xa.vpf)'] - d['v(xa.e7)']) / 100
    d['I_vas_n'] = (d['v(xa.e8)'] - d['v(xa.vnf)']) / 100
    d['I_tail_n'] = (d['v(xa.e5)'] - d['v(xa.vnf)']) / 270
    d['I_tail_p'] = (d['v(xa.vpf)'] - d['v(xa.e6)']) / 270
    d['V_bias'] = d['v(xa.vbp)'] - d['v(xa.vbn)']
    d['offset_mV'] = d['v(spk)'] * 1e3
    return d

if __name__ == '__main__':
    d = op('op_nominal')
    print(json.dumps({k: round(v, 5) for k, v in d.items()}, indent=1))

def amp_lg():
    """Amp text with an AC voltage injector VLG between OUT and the feedback network."""
    t = AMP.replace('R26  OUT FB  47k', 'VLG  FBX OUT DC 0 AC 1\nR26  FBX FB  47k').replace('C8   OUT FB  {CF}', 'C8   FBX FB  {CF}')
    assert 'VLG' in t
    return t

def ac(name, inst='', load='RL SPK 0 8', vs=15.5, lg=False, fstop='50Meg'):
    """Returns dict f-> (closed-loop V(spk)) or loop gain T=-V(out)/V(fbx)."""
    global AMP
    keep = AMP
    if lg: AMP = amp_lg()
    vecs = 'v(xa.out) v(xa.fbx)' if lg else 'v(spk) v(xa.out)'
    try:
        d = deck(name, inst, src=('DC 0 AC 0' if lg else 'DC 0 AC 1'), load=load, vs=vs,
                 control=f'ac dec 50 1 {fstop}\nwrdata {R/(name+".txt")} {vecs}')
        run(name, d)
    finally:
        AMP = keep
    import numpy as np
    a = np.loadtxt(R/(name+'.txt'), skiprows=1)
    f = a[:, 0]
    if lg:
        vo = a[:, 1] + 1j*a[:, 2]; vx = a[:, 3] + 1j*a[:, 4]
        return f, -vo/vx
    return f, a[:, 1] + 1j*a[:, 2]

def margins(f, T):
    import numpy as np
    mag = 20*np.log10(abs(T)); ph = np.degrees(np.unwrap(np.angle(T)))
    i = np.where((mag[:-1] > 0) & (mag[1:] <= 0))[0]
    if not len(i): return dict(fc=None)
    i = i[-1]; fc = f[i]; pm = 180 + ph[i]
    pm = ((pm + 180) % 360) - 180
    j = np.where(np.diff(np.sign(((ph + 180) % 360) - 180)) != 0)[0]
    gm = [(-mag[k], f[k]) for k in j if f[k] > fc]
    return dict(fc=fc, pm=pm, gm=gm[0] if gm else None, T1k=mag[np.argmin(abs(f-1e3))], T20k=mag[np.argmin(abs(f-2e4))])

GAIN = 16.67  # closed-loop V/V at 1 kHz (ac analysis, nominal)

def thd(name, vout_pk, inst='', load='RL SPK 0 8', vs=15.5, f0=1e3, cycles=6, extra='', vsn=None, rip=0):
    """Transient THD at the speaker (ngspice fourier over the last cycle). Returns (thd%, harmonics, peak currents)."""
    vin = vout_pk / GAIN
    T = cycles / f0
    ctl = (f'set fourgridsize=2048\ntran {1/f0/400} {T} 0 {1/f0/400}\n'
           f'fourier {f0} v(spk)\n'
           f'meas tran vpk MAX v(spk) from={T-1/f0} to={T}\n'
           f'meas tran vmn MIN v(spk) from={T-1/f0} to={T}\n'
           f'meas tran itop_min MIN i(v.xa.vsp) from={T-1/f0} to={T}\n'
           f'meas tran ibot_min MIN i(v.xa.vsn) from={T-1/f0} to={T}\n')
    global AMP
    keep = AMP
    AMP = AMP.replace('R22  EP  OUT 0.33', 'VSP  EP  EPX 0\nR22  EPX OUT 0.33').replace('R25  EN  OUT 0.33', 'VSN  OUTX EN 0\nR25  OUT OUTX 0.33')
    try:
        log = run(name, deck(name, inst, src=f'DC 0 SIN(0 {vin} {f0})', load=load, vs=vs, vsn=vsn, control=ctl, extra=extra, rip=rip))
    finally:
        AMP = keep
    m = re.search(r'THD:\s*([-+\deE.]+)\s*%', log)
    harm = re.findall(r'^\s*(\d+)\s+([\deE.+-]+)\s+([\deE.+-]+)\s+([\deE.+-]+)', log, re.M)
    return dict(thd=float(m.group(1)) if m else float('nan'), vpk=val(log, 'vpk'), vmn=val(log, 'vmn'),
                itop_min=val(log, 'itop_min'), ibot_min=val(log, 'ibot_min'), harm=harm[:6])

def square(name, vout, inst='', load='RL SPK 0 8', f0=10e3, vs=15.5, tr=50e-9):
    """Square-wave response; returns overshoot % and an HF-residue figure after settling."""
    import numpy as np
    vin = vout / GAIN
    T = 4 / f0
    pts = ['0 0']
    for k in range(4):   # symmetric about 0 V so C1 stays uncharged at t=0
        a = (k + 0.25) / f0; b = (k + 0.75) / f0
        pts += [f'{a} {-vin if k else 0}', f'{a+tr} {vin}', f'{b} {vin}', f'{b+tr} {-vin}']
    src = 'DC 0 PWL(' + ' '.join(pts) + ')'
    ctl = f'tran 2n {T} 0 5n\nwrdata {R/(name+".txt")} v(spk) v(xa.out)'
    run(name, deck(name, inst, src=src, load=load, vs=vs, control=ctl))
    a = np.loadtxt(R/(name+'.txt'), skiprows=1)
    t, v = a[:, 0], a[:, 1]
    # last full positive half period
    t0 = 2.25/f0; t1 = t0 + 0.5/f0
    s = (t >= t0) & (t < t1)
    vv = v[s]; tt = t[s]
    final = np.mean(vv[-len(vv)//5:])
    ov = (vv.max() - final) / (2*vout) * 100
    tail = vv[len(vv)//2:]
    hf = tail.max() - tail.min()
    # 10-90 rise time
    lo = -vout + 0.1*2*vout; hi = -vout + 0.9*2*vout  # thresholds on the rising edge
    try:
        tr10 = tt[np.where(vv > lo)[0][0]]; tr90 = tt[np.where(vv > hi)[0][0]]; rise = tr90 - tr10
    except IndexError:
        rise = float('nan')
    return dict(overshoot_pct=ov, settled_pp=hf, rise_ns=rise*1e9, final=final)

def lib_beta(**bf):
    """Model library with BF overridden, e.g. lib_beta(Q2SC5198=55, QBD139=40)."""
    t = LIB
    for name, b in bf.items():
        m = re.search(r'(\.model ' + name + r' (?:NPN|PNP)\()(.*?)(\)\n)', t, re.S)
        body = re.sub(r'\bBF=[\d.eE+-]+', f'BF={b}', m.group(2))
        t = t[:m.start()] + m.group(1) + body + m.group(3) + t[m.end():]
    return t

def rails_tran(name, vp_pwl, vn_pwl, tstop, inst='', load='RL SPK 0 8', step=20e-6, uic=True):
    """Transient with arbitrary rail PWLs (startup/shutdown). Returns arrays t, v(spk), vp, vn, Iq."""
    import numpy as np
    d = deck(name, inst, src='DC 0', load=load, vs=0,
             control=f'tran {step} {tstop} 0 {step}\nwrdata {R/(name+".txt")} v(spk) v(vp) v(vn) v(xa.ep) v(xa.out)')
    d = d.replace('VP VP 0 DC 0\n', f'VP VP 0 PWL({vp_pwl})\n').replace('VN VN 0 DC 0\n', f'VN VN 0 PWL({vn_pwl})\n')
    if uic:   # power-up from fully discharged capacitors
        d = d.replace(f'tran {step} {tstop} 0 {step}', f'tran {step} {tstop} 0 {step} uic')
    run(name, d, timeout=1200)
    a = np.loadtxt(R/(name+'.txt'), skiprows=1)
    return a[:, 0], a[:, 1], a[:, 2], a[:, 3], (a[:, 4]-a[:, 5])/0.33
