#!/usr/bin/env python3
"""Plot actual saved ngspice output; never synthesize amplifier results."""
from pathlib import Path
import sys,json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'simulation'));import run
D=P/'docs/plots';D.mkdir(exist_ok=True)
s=json.loads((run.R/'summary.json').read_text());e=json.loads((run.R/'extended_summary.json').read_text())
plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':.25,'figure.dpi':150})
def finish(fig,name):
 fig.suptitle(f'MOSFETAmp2 Rev 0.2 — {run.MOS} MOSFET models, imposed temperature; hardware unverified',fontsize=12)
 fig.tight_layout(rect=(0,0,1,.96));fig.savefig(D/(name+'.png'));fig.savefig(D/(name+'.pdf'));plt.close(fig)
fig,axes=plt.subplots(3,1,figsize=(9,8))
for ax,f in zip(axes,[20,1000,20000]):
 a=run.data('sine_'+str(f));sel=a[:,0]>a[-1,0]-2/f;t=(a[sel,0]-a[sel,0][0])*1000
 ax.plot(t,a[sel,2],label='speaker output');ax.plot(t,a[sel,1]*10.52,'--',label='input ×10.52');ax.set(xlabel='Time (ms)',ylabel='V',title=f'{f:g} Hz, ±15 V, 8 Ω; THD(2–10) {s["sine"][str(f)]["thd_percent"]:.4g}%');ax.legend(loc='upper right')
finish(fig,'sines')
a=run.data('frequency');z=a[:,1]+1j*a[:,2];db=20*np.log10(abs(z));ph=np.unwrap(np.angle(z))*180/np.pi
fig,ax=plt.subplots(2,1,figsize=(9,6),sharex=True);ax[0].semilogx(a[:,0],db);ax[0].set(ylabel='Gain (dB)',ylim=(0,23),title='External IN to SPK; ±15 V, 8 Ω');ax[1].semilogx(a[:,0],ph);ax[1].set(xlabel='Frequency (Hz)',ylabel='Phase (°)',xlim=(1,1e7));finish(fig,'frequency')
fig,ax=plt.subplots(2,1,figsize=(9,7),sharex=True)
for name in ['8R','8R_10n','open_100n','reactive','parasitic']:
 a=run.data('loop_'+name);z=a[:,1]+1j*a[:,2];ax[0].semilogx(a[:,0],20*np.log10(abs(z)),label=name);ax[1].semilogx(a[:,0],np.unwrap(np.angle(z))*180/np.pi,label=name)
ax[0].axhline(0,color='k',lw=.7);ax[0].set(ylabel='Return ratio (dB)',title='Voltage injection at feedback input — approximate first-crossing margins only');ax[0].legend(ncol=3);ax[1].axhline(-180,color='k',lw=.7);ax[1].set(ylabel='Unwrapped phase (°)',xlabel='Frequency (Hz)',xlim=(1e3,1e8));finish(fig,'loop')
fig,ax=plt.subplots(3,1,figsize=(9,8))
for axis,name in zip(ax,['8R','open_100n','reactive']):
 a=run.data('square_'+name);sel=a[:,0]>a[-1,0]-.00021;axis.plot(a[sel,0]*1e6,a[sel,3],label='OUT before coil');axis.plot(a[sel,0]*1e6,a[sel,2],label='SPK after coil');axis.set(xlabel='Time (µs)',ylabel='V',title='10 kHz square: '+name);axis.legend(loc='upper right')
finish(fig,'square_loads')
fig,ax=plt.subplots(2,1,figsize=(9,7))
for v in ['12','15','16','20.5']:
 rows=s['clipping'][v];x=[d['power_w'] for d in rows.values()];y=[d['thd_percent'] for d in rows.values()];ax[0].semilogy(x,y,'o-',label='±'+v+' V')
ax[0].set(xlabel='Fundamental power into 8 Ω (W)',ylabel='THD 2–10 (%)',title='1 kHz amplitude sweep; sparse points around a sharp clipping knee');ax[0].legend()
a=run.data('overload_recovery');ax[1].plot(a[:,0]*1000,a[:,2]);ax[1].set(xlabel='Time (ms)',ylabel='Speaker output (V)',title='Three clipped cycles followed by 0.1 V peak input');finish(fig,'clipping')
fig,ax=plt.subplots(2,1,figsize=(9,7))
t=[0,27,50,75];iq=[s['temperature'][f'junction{k}_sensor{k}_driver{k}']['iq_p']*1000 for k in t];ax[0].plot(t,iq,'o-',label='all temperatures track; imposed −4 mV/K per MOSFET');ax[0].plot([75,100],[s['temperature'][f'junction{k}_sensor27_driver27']['iq_p']*1000 for k in [75,100]],'s--',label='sensor + drivers remain at 27 °C');ax[0].set(xlabel='Imposed MOSFET temperature (°C)',ylabel='P-device idle current (mA)',title='Sensitivity study — imposed slope, no self-heating');ax[0].legend(fontsize=8)
for name in ['symmetric','asymmetric']:
 a=run.data('startup_'+name);ax[1].plot(a[:,0]*1000,a[:,1],label=name)
ax[1].set(xlabel='Time (ms)',ylabel='Output (V)',title='Zero-input power ramps; ideal rails and approximate models');ax[1].legend();finish(fig,'temperature_startup')
print('Wrote six PNG/PDF plot pairs to docs/plots')
