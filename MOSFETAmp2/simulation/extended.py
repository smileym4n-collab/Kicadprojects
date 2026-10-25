#!/usr/bin/env python3
"""Additional stress, mismatch and output-limit experiments (Rev 0.2); see models/README.md."""
import run,json,re,pathlib,numpy as np
s=json.loads((run.R/'summary.json').read_text());base=f'.param RV={s["rheostat_ohm"]}'
out={'power_limits':{},'temperature_coefficient':{},'component_corners':{},'stress':{}}
for v in [12,15,16,18,20.5,21]:
 out['power_limits'][str(v)]={}
 for target in [.1,1.0]:
  lo=.2;hi=1.7
  for i in range(8):
   amp=(lo+hi)/2
   a=run.tran(f'power_{v}_{target}',amp=amp,params=base+f' VS={v}',cycles=6)
   d=run.harmonics(a,1000)
   if d['thd_percent']<=target:lo=amp
   else:hi=amp
  a=run.tran(f'power_{v}_{target}',amp=lo,params=base+f' VS={v}',cycles=6);d=run.harmonics(a,1000)
  d['input_vpk']=lo;d['output_peak_max']=float(a[-3000:,2].max());d['output_peak_min']=float(a[-3000:,2].min())
  t=a[:,0];sel=t>t[-1]-.003
  d['dc_input_power_w']=float(np.trapezoid(v*(-a[sel,8]+a[sel,9]),a[sel,0])/(a[sel,0][-1]-a[sel,0][0]))
  d['efficiency_percent']=100*d['power_w']/d['dc_input_power_w']
  out['power_limits'][str(v)][str(target)]=d
 print('power',v,out['power_limits'][str(v)],flush=True)
for coeff in [.002,.004,.006]:
 out['temperature_coefficient'][str(coeff)]=run.op('tempco_'+str(coeff),base+run.thermal(75,-coeff)+' TS=75 TD=75')
# +/-1% on the fixed bias resistors, each in the direction that raises (high) or lowers (low) bias.
for case,mods in [('bias_R_high',{'R12 BC BB 3.9k':'R12 BC BB 3.939k','R13 BB BN {R13}':'R13 BB BN {0.99*R13}','R14 BCE BW {RE}':'R14 BCE BW {0.99*RE}'}),('bias_R_low',{'R12 BC BB 3.9k':'R12 BC BB 3.861k','R13 BB BN {R13}':'R13 BB BN {1.01*R13}','R14 BCE BW {RE}':'R14 BCE BW {1.01*RE}'}),('input_1mV',{'Q2 C2N B1 E2 BC556B':'VOS B2 B1 1m\nQ2 C2N B2 E2 BC556B'})]:
 ch=run.CH
 for a,b in mods.items():assert a in ch;ch=ch.replace(a,b)
 out['component_corners'][case]=run.op(case,base,channel=ch)
for bf in [25,250]:
 model=(run.P/'models/devices.lib').read_text().replace('.model BD139A NPN(IS=2e-13 BF=100',f'.model BD139A NPN(IS=2e-13 BF={bf}').replace('.model BD140A PNP(IS=2e-13 BF=100',f'.model BD140A PNP(IS=2e-13 BF={bf}')
 ch=run.CH.replace('.include models/devices.lib',model)
 out['component_corners']['BD_beta_'+str(bf)]=run.op('BD_beta_'+str(bf),base,channel=ch)
# Gate capacitance doubling at the pessimistic 100 nF speaker load.
lib=f'models/mosfets_{run.MOS}.lib';mos=(run.P/lib).read_text()
for a,b in ([('CGSO=1.896e-05','CGSO=3.792e-05'),('CAP 11 10 2.35428e-09','CAP 11 10 4.70856e-09'),('CGSO=1.15995e-05','CGSO=2.3199e-05'),('CAP 11 10 3.66446e-09','CAP 11 10 7.32892e-09')] if run.MOS=='infineon' else [('1.92n','3.84n'),('CGD GI DI 40p','CGD GI DI 80p'),('1.06n','2.12n'),('CGD GI DI 240p','CGD GI DI 480p')]):
 assert a in mos,a;mos=mos.replace(a,b)
ch=run.CH.replace('.include '+lib,mos)
run.tran('cap_double',f=10000,amp=.2,params=base,load='RL SPK 0 8\nCL SPK 0 100n',square=True,channel=ch)
# Recovery after three clipped cycles, with a step to small-signal sine at zero crossing.
run.tran('overload_recovery',params=base,amp=1.5,cycles=10)
p=run.R/'overload_recovery.cir';deck=p.read_text();deck=re.sub(r'VIN IN 0 .*','BVIN IN 0 V=sin(2*pi*1000*time)*(time<.003 ? 1.5 : .1)',deck);p.write_text(deck)
import subprocess
subprocess.run([run.BIN,'-b','-o',str(run.R/'overload_recovery.log'),str(p)],capture_output=True,timeout=90)
a=run.data('overload_recovery');sel=a[:,0]>.004;out['stress']['post_overload']=run.harmonics(a,1000)
run.tran('slew',f=1000,amp=.7,params=base,square=True,cycles=3)
a=run.data('slew');sel=(a[:,0]>.001)&(a[:,0]<.002);slope=np.diff(a[sel,3])/np.diff(a[sel,0])/1e6;out['stress']['slew_up_v_us']=float(np.max(slope));out['stress']['slew_down_v_us']=float(-np.min(slope))
(run.R/'extended_summary.json').write_text(json.dumps(out,indent=2))
