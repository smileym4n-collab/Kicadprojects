#!/usr/bin/env python3
"""Average output-device dissipation vs output level (1 kHz sine, nominal rails, warm bias)."""
import sys, re, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import run
INST = 'RV=78 TS=46 TD=48 TO=63'
out = {}
for load, R, levels in [('RL SPK 0 8', 8, [0, 1, 3.75, 7.5, 10, 12]), ('RL SPK 0 4', 4, [5, 10])]:
    for P in levels:
        vin = max((2*R*P)**.5, 1e-6) / run.GAIN
        ctl = ('tran 2.5u 6m 0 2.5u\n'
               'let pq12 = (v(vp)-v(xa.ep))*(-1*@q.xa.q12[ic])\n'
               'let pq13 = (v(xa.en)-v(vn))*@q.xa.q13[ic]\n'
               'let pload = v(spk)*v(spk)/%g\n'
               'meas tran p12 AVG pq12 from=5m to=6m\n'
               'meas tran p13 AVG pq13 from=5m to=6m\n'
               'meas tran pl AVG pload from=5m to=6m\n' % R)
        d = run.deck('pd', INST, src=f'DC 0 SIN(0 {vin} 1k)', load=load, vs=15.6, control='save all @q.xa.q12[ic] @q.xa.q13[ic]\n' + ctl)
        log = run.run('pd', d)
        out[f'{R}ohm_{P}W'] = dict(P12=run.val(log, 'p12'), P13=run.val(log, 'p13'), Pload=run.val(log, 'pl'))
        print(R, P, {k: round(v, 2) for k, v in out[f'{R}ohm_{P}W'].items()})
(run.R / 'device_dissipation.json').write_text(json.dumps(out, indent=1))
