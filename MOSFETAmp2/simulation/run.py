#!/usr/bin/env python3
"""Reproducible ngspice experiments (Rev 0.2). Run from simulation/; see model limitations.
MOSFET_MODELS=authored selects the Rev 0.1 authored approximations instead of the Infineon models."""
import os, pathlib, subprocess, json, re
import numpy as np
from scipy.optimize import brentq
P=pathlib.Path(__file__).resolve().parent
os.chdir(P)
BIN=os.environ.get('NGSPICE',str(P.parent/'tools/ngspice/bin/ngspice'))
R=P/'results'; R.mkdir(exist_ok=True)
MOS=os.environ.get('MOSFET_MODELS','infineon')
CH=(P/'channel.cir').read_text().replace('models/mosfets_infineon.lib',f'models/mosfets_{MOS}.lib')
RV_POT=200  # trim rheostat fitted with the nominal RE = 1k0

def thermal(tj, coeff=-.004):
    """Imposed MOSFET threshold slope (V/K per device, negative) and KP ~ T^-1.5 at junction tj (C)."""
    return f' DVN={coeff*(tj-27)} DVP={coeff*(tj-27)} KPS={((tj+273.15)/300.15)**-1.5}'

def run(name, params='', source='DC 0 AC 1', control='op', load='RL SPK 0 8', channel=None, extra=''):
    inc=CH if channel is None else channel
    deck=f'''MOSFETAmp2 {name} - approximate models
{inc}
{params}
VP VP 0 {{VS}}
VN VN 0 {{-VS}}
VIN IN 0 {source}
XA IN OUT VP VN 0 AMP
LOUT OUT SPK 0.7u
RLDCR OUT SPK 10
{load}
{extra}
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
    (R/(name+'.cir')).write_text(deck)
    p=subprocess.run([BIN,'-b','-o',str(R/(name+'.log')),str(R/(name+'.cir'))],capture_output=True,timeout=90)
    log=(R/(name+'.log')).read_text()
    if re.search(r'(Error|Timestep too small|doAnalyses:|unknown parameter)',log):
        raise RuntimeError(name+' failed: '+log[-3000:])
    return log

def op(name, params='',channel=None,load='RL SPK 0 8'):
    vs=['v(out)','v(xa.sn)','v(xa.sp)','v(xa.gn)','v(xa.gp)','v(xa.bp)','v(xa.bn)','i(vp)','i(vn)','v(xa.tail)','v(xa.ve)']
    run(name,params,control='op\nprint '+' '.join(vs),channel=channel,load=load)
    log=(R/(name+'.log')).read_text()
    d={k:float(re.search(re.escape(k)+r'\s*=\s*([-+\deE.]+)',log).group(1)) for k in vs}
    d['iq_n']=(d['v(xa.sn)']-d['v(out)'])/.33
    d['iq_p']=(d['v(out)']-d['v(xa.sp)'])/.33
    return d

def data(name):
    p=R/(name+'.txt')
    return np.loadtxt(p if p.exists() else R/(name+'.txt.gz'),skiprows=1)
def tran(name,f=1000,amp=.5,params='',load='RL SPK 0 8',square=False,extra='',channel=None,cycles=10):
    end=cycles/f; step=min(1/(f*800),1e-6)
    src=f'SIN(0 {amp} {f})' if not square else f'PULSE({-amp} {amp} 0 200n 200n {0.5/f-200e-9} {1/f})'
    run(name,params,src,f'tran {step} {end} 0 {step}\nwrdata results/{name}.txt v(in) v(spk) v(out) v(xa.sn) v(xa.sp) v(xa.gn) v(xa.gp) i(vp) i(vn)',load,extra=extra,channel=channel)
    return data(name)

def harmonics(a,f,cycles=3):
    t=np.linspace(a[-1,0]-cycles/f,a[-1,0],32768,endpoint=False)
    y=np.interp(t,a[:,0],a[:,2]); x=np.interp(t,a[:,0],a[:,1])
    A=np.column_stack([np.ones(len(t))]+[z for k in range(1,11) for z in (np.sin(2*np.pi*k*f*t),np.cos(2*np.pi*k*f*t))])
    b=np.linalg.lstsq(A,y,rcond=None)[0]; h=np.hypot(b[1::2],b[2::2]); fit=A@b
    return dict(vpk=float(h[0]),power_w=float(h[0]**2/16),thd_percent=float(100*np.linalg.norm(h[1:])/h[0]),offset_v=float(b[0]),gain=float(h[0]/((np.max(x)-np.min(x))/2)),residual_rms=float(np.std(y-fit)))

def main():
    nominal=brentq(lambda v:op('bias_search',f'.param RV={v}')['iq_p']-.05,0,RV_POT,xtol=.01)
    print('Rheostat for 50 mA:',nominal,flush=True)
    baseline=f'.param RV={nominal}'
    summary={'model_status':'MOSFET MODELS: '+MOS+'; imposed temperature/spread - NOT HARDWARE VALIDATION','revision':'0.2','rheostat_ohm':nominal,'op':{},'sine':{},'clipping':{},'loop':{},'temperature':{},'tolerance':{}}
    for v in [12,15,16,20.5]: summary['op'][str(v)]=op('op_'+str(v),baseline+f' VS={v}')
    for f in [20,1000,20000]:
        a=tran('sine_'+str(f),f=f,params=baseline)
        summary['sine'][str(f)]=harmonics(a,f)
        print('sine',f,summary['sine'][str(f)],flush=True)
    for v in [12,15,16,20.5]:
        summary['clipping'][str(v)]={}
        for amp in [.4,.6,.8,1,1.2,1.4]:
            a=tran(f'clip_{v}_{amp}',amp=amp,params=baseline+f' VS={v}',cycles=7)
            d=harmonics(a,1000); d.update(vmax=float(np.max(a[-2000:,2])),vmin=float(np.min(a[-2000:,2])))
            summary['clipping'][str(v)][str(amp)]=d
    for name,load in [('8R','RL SPK 0 8'),('4R','RL SPK 0 4'),('8R_10n','RL SPK 0 8\nCL SPK 0 10n'),('open_100n','RL SPK 0 1meg\nCL SPK 0 100n'),('reactive','RL REAC 0 8\nLL SPK REAC 0.5m\nCL SPK 0 100n')]:
        tran('square_'+name,f=10000,amp=.2,params=baseline,load=load,square=True,cycles=8)
        c=CH.replace('Q1 C1N FB E1','VTEST FBI FB DC 0 AC 1\nQ1 C1N FBI E1')
        run('loop_'+name,baseline,'DC 0 AC 0',f'ac dec 100 1 100meg\nlet ret=-v(xa.fb)/v(xa.fbi)\nwrdata results/loop_{name}.txt ret',load,channel=c)
        a=data('loop_'+name); z=a[:,1]+1j*a[:,2]
        db=20*np.log10(abs(z)); ph=np.unwrap(np.angle(z))*180/np.pi
        idx=np.where((db[:-1]>=0)&(db[1:]<0))[0]
        if len(idx):
            i=idx[0]; u=-db[i]/(db[i+1]-db[i]); fc=np.exp(np.log(a[i,0])+u*np.log(a[i+1,0]/a[i,0])); phase=ph[i]+u*(ph[i+1]-ph[i])
            summary['loop'][name]={'crossover_hz':float(fc),'phase_margin_deg':float(180+phase)}
        else: summary['loop'][name]={'status':'no crossing'}
    run('frequency',baseline,control='ac dec 100 1 100meg\nwrdata results/frequency.txt v(spk)')
    # Imposed MOSFET threshold (-4 mV/K per device) and mobility drift; sensor and driver/board
    # temperatures independent. Same conditions as Rev 0.1 for comparison.
    for tj,ts,td in [(0,0,0),(27,27,27),(50,50,50),(75,75,75),(100,75,75),(75,27,27),(100,27,27)]:
        param=baseline+thermal(tj)+f' TS={ts} TD={td}'
        summary['temperature'][f'junction{tj}_sensor{ts}_driver{td}']=op(f'temp_{tj}_{ts}_{td}',param)
    for rv in [0,RV_POT,1e9]: summary['tolerance']['rheostat_'+str(rv)]=op('rv_'+str(rv),f'.param RV={rv}')
    summary['tolerance']['RE_unfitted']=op('re_open',baseline+' RE=1e9')
    for dn,dp in [(-.5,-.5),(-.5,.5),(.5,-.5),(.5,.5)]:
        summary['tolerance'][f'vth_{dn}_{dp}']=op(f'vth_{dn}_{dp}',baseline+f' DVN={dn} DVP={dp}')
    # Rail ramp with both equal and deliberately asymmetric collapse; capacitors initially discharged.
    for name,vp,vn in [('symmetric','PWL(0 0 10m 0 60m 15 150m 15 200m 0 250m 0)','PWL(0 0 10m 0 60m -15 150m -15 200m 0 250m 0)'),('asymmetric','PWL(0 0 10m 0 60m 15 150m 15 170m 0 250m 0)','PWL(0 0 10m 0 80m -15 150m -15 230m 0 250m 0)')]:
        # Replace ideal sources in deck after writing through a separate wrapper below.
        run('startup_'+name,baseline,control='tran 10u 250m 0 10u uic\nwrdata results/startup_'+name+'.txt v(spk) v(vp) v(vn)',extra='')
        p=R/('startup_'+name+'.cir'); s=p.read_text().replace('VP VP 0 {VS}','VP VP 0 '+vp).replace('VN VN 0 {-VS}','VN VN 0 '+vn);p.write_text(s)
        subprocess.run([BIN,'-b','-o',str(R/('startup_'+name+'.log')),str(p)],capture_output=True,timeout=90)
        a=data('startup_'+name); summary['startup_'+name]={'vmax':float(a[:,1].max()),'vmin':float(a[:,1].min())}
    (R/'summary.json').write_text(json.dumps(summary,indent=2))
    return summary

if __name__=='__main__': main()
