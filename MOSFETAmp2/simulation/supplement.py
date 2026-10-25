#!/usr/bin/env python3
"""Commissioning link, select-on-test bias cases, LED sensitivity and parasitics (Rev 0.2).
Imposed MOSFET temperature/spread; engineering approximations, not hardware evidence."""
import run,numpy as np,json
from scipy.optimize import brentq
s=json.loads((run.R/'summary.json').read_text());base=f'.param RV={s["rheostat_ohm"]}'
ch=run.CH;out={}
linked=ch.replace('C3 BP BN 100n','C3 BP BN 100n\nRBIASLINK BP BN 1m')
out['bias_link']={str(v):run.op('bias_link_'+str(v),f'.param VS={v} RV={run.RV_POT}',channel=linked,load='RL SPK 0 1meg') for v in [8,12,15]}
# Lowest datasheet threshold pair (2 V / 2 V at 250 uA), relative to the model VTO.
vto=(3.58173,3.74034) if run.MOS=='infineon' else (3.4,3.77)
low=f' DVN={2-vto[0]} DVP={2-vto[1]}'
# First power-up with RE unfitted: no programmed offset, minimum possible spread.
out['low_threshold_RE_unfitted']=run.op('low_threshold_re_open','.param RE=1e9'+low)
# Select-on-test for this pair: largest E24 RE whose 0..2k trim range reaches 50 mA, then trim.
rv2k=lambda re_,rv,extra='':run.op('low_threshold_sel',f'.param RE={re_} RV={rv}'+low+extra)['iq_p']-.05
sel=None
for re_ in [10e3,9.1e3,8.2e3,7.5e3,6.8e3,6.2e3,5.6e3,5.1e3,4.7e3,4.3e3,3.9e3,3.6e3]:
 if rv2k(re_,0)>=0>=rv2k(re_,2000):sel=re_;break
assert sel,'no RE selection reaches 50 mA'
rv=brentq(lambda v:rv2k(sel,v),0,2000,xtol=.05)
out['low_threshold_selected']={'RE':sel,'RV_2k_trim':rv,**run.op('low_threshold_min',f'.param RE={sel} RV={rv}'+low)}
# Same imposed warm condition as the Rev 0.1 failed corner: -4 mV/K, 75 C, sensor and drivers tracking.
out['low_threshold_warm']=run.op('low_threshold_warm',f'.param RE={sel} RV={rv} DVN={2-vto[0]-.004*48} DVP={2-vto[1]-.004*48} KPS={(348.15/300.15)**-1.5} TS=75 TD=75')
# LED forward-voltage temperature coefficient about -1.5 / -2.5 mV/K instead of -1.8 (EG), board and all at 75 C.
for eg,label in [(2.2,'-1.5mV_per_K'),(2.5,'-2.5mV_per_K')]:
 out['led_tc_'+label]=run.op('led_tc_'+label,base+run.thermal(75)+f' TS=75 TD=75 LEDEG={eg}')
# External parasitics around the MOSFET terminals and power path (assumed values, not extracted).
par=ch.replace('XQ11 VP GNI SN MOSN','LGN GNI GNL 30n\nLSN SNL SN 10n\nXQ11 VP GNL SNL MOSN').replace('XQ12 VN GPI SP MOSP','LGP GPI GPL 30n\nLSP SPL SP 10n\nXQ12 VN GPL SPL MOSP')
par=par.replace('R19 SN OUT 0.33','LSR19 SN SNR 100n\nR19 SNR OUT 0.33').replace('R20 OUT SP 0.33','LSR20 OUT SPR 100n\nR20 SPR SP 0.33')
par=par.replace('C7 VP 0 100n','LC7 VP VP7 10n\nC7 VP7 0 100n').replace('C8 0 VN 100n','LC8 VN VN8 10n\nC8 0 VN8 100n')
par=par.replace('C5 VP 0 220u','RCE5 VP VCP 0.1\nC5 VCP 0 220u').replace('C6 0 VN 220u','RCE6 VCN VN 0.1\nC6 0 VCN 220u')
for a in ['LGN','LSP','LSR20','LC8','RCE6']:assert a in par,a
run.tran('parasitic_square',f=10000,amp=.2,params=base,load='RL REAC 0 8\nLL SPK REAC 0.5m\nCL SPK 0 100n',square=True,cycles=8,channel=par)
loop=par.replace('Q1 C1N FB E1','VTEST FBI FB DC 0 AC 1\nQ1 C1N FBI E1')
run.run('loop_parasitic',base,'DC 0 AC 0','ac dec 100 1 100meg\nlet ret=-v(xa.fb)/v(xa.fbi)\nwrdata results/loop_parasitic.txt ret',load='RL REAC 0 8\nLL SPK REAC 0.5m\nCL SPK 0 100n',channel=loop)
a=run.data('loop_parasitic');z=a[:,1]+1j*a[:,2];db=20*np.log10(abs(z));ph=np.unwrap(np.angle(z))*180/np.pi;i=np.where((db[:-1]>=0)&(db[1:]<0))[0][0];u=-db[i]/(db[i+1]-db[i]);out['parasitic_loop']={'crossover_hz':float(np.exp(np.log(a[i,0])+u*np.log(a[i+1,0]/a[i,0]))),'phase_margin_deg':float(180+ph[i]+u*(ph[i+1]-ph[i]))}
(run.R/'supplement_summary.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
