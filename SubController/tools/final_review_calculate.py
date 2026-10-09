"""Reproducible engineering checks; ideal netlist equations, not device SPICE."""
import sys,json,math,itertools
from pathlib import Path
import numpy as np
from verify_netlist import solve,pins,comps,ops,output_network,value
from analyse import L,H,AP,LP_K,LP_SERIES,LP_SHUNT,effective_pot,pot_positions
P=Path(__file__).resolve().parents[1];out=P/'design/final-review';data={}
# Stage levels from actual netlist for 2Vrms correlated REF, or 2Vrms mono LFE.
stages=['BUF_L','BUF_R','SUM_INV','MONO','LP12','LP24','LEVEL_IN','ATT_IN','ATT_DRIVE','ATT_OUT','ATT_BUFFER','PHASE_OUT','HP_OUT','HP_FINAL','POLARITY_OUT','AMP_DRIVE','AMP_AC','AMP_OUT']
data['stage_2Vrms']={}
for mode,slope in [('REF',12),('REF',24),('AV',24)]:
 v=solve(70,mode=mode,slope=slope,all_nodes=True)
 data['stage_2Vrms'][f'{mode}_{slope}_70Hz']={n:round(2*abs(v[n]),6) for n in stages}
data['output_network']={f'{f}Hz':{'magnitude':abs(output_network(f)),'dB':20*math.log10(abs(output_network(f))),'phase_deg':math.degrees(np.angle(output_network(f)))} for f in [5,10,15,20,25,40,70,120,1000]}
data['phase_deg']={str(f):[math.degrees(np.angle(AP(f,r))) for r in [2200,2200+50000*47000/97000]] for f in [40,70,120]}
# DC superposition: individual opamp offsets and independent bias injections.
# 1e-7Hz approximates capacitors open; this is not power-up simulation.
dc={}
for mode in ['REF','AV']:
 for hp_bypass in [False,True]:
  sums={n:0. for n in stages};opts=dict(freq=1e-7,mode=mode,ap=50000,source='none',all_nodes=True,hp_bypass=hp_bypass,rv=24000)
  for i in range(12):
   vos=[0.]*12;vos[i]=.005
   v=solve(**opts,vos=vos)
   for n in stages:sums[n]+=abs(v[n])
   for terminal in range(2):
    ib=np.zeros((12,2));ib[i,terminal]=400e-9
    v=solve(**opts,ib=ib)
    for n in stages:sums[n]+=abs(v[n])
  dc[f'{mode}_HPbypass_{hp_bypass}']={n:round(1000*sums[n],5) for n in stages}
data['DC_mV_conservative_independent_5mV_400nA_bound']=dc
# Monte Carlo component tolerance with deterministic seed, 1% R / 5% individual films.
rng=np.random.default_rng(681614);N=50000
stats=lambda a:{'min':float(a.min()),'p05':float(np.quantile(a,.05)),'median':float(np.median(a)),'p95':float(np.quantile(a,.95)),'max':float(a.max())}
def sampled_lp(potspread):
 physical=pot_positions[3]*rng.uniform(1-potspread,1+potspread,(N,4));sh=15000*rng.uniform(.99,1.01,(N,4));r=4270*rng.uniform(.99,1.01,(N,4))+physical*sh/(physical+sh)
 caps=220e-9*rng.uniform(.95,1.05,(N,6));cf=np.array([caps[:,0]+caps[:,1],caps[:,3]+caps[:,4]]).T;cg=caps[:,[2,5]]
 prod=np.array([r[:,0]*r[:,1],r[:,2]*r[:,3]]).T;rsum=np.array([r[:,0]+r[:,1],r[:,2]+r[:,3]]).T
 f=1/(2*np.pi*np.sqrt(prod*cf*cg));q=np.sqrt(prod*cf*cg)/(cg*rsum);s=2j*np.pi*70;gain=np.prod(1/(1+s*cg*rsum+s*s*prod*cf*cg),axis=1)
 return {'f0_stage1_Hz':stats(f[:,0]),'Q_stage1':stats(q[:,0]),'stage_frequency_ratio':stats(f[:,0]/f[:,1]),'LP24_70Hz_dB':stats(20*np.log10(abs(gain)))}
data['MonteCarlo']={'trials':N,'distribution':'Independent uniform within stated tolerances; not confidence guarantees. Pot sensitivity example assumes linear scaling, not guaranteed Bourns rheostat tracking.','matched_pot_R1pct_C5pct':sampled_lp(0),'pot_resistance_20pct_example':sampled_lp(.2)}
a=12700*rng.uniform(.99,1.01,N);b=25500*rng.uniform(.99,1.01,N);c1=220e-9*(rng.uniform(.95,1.05,N)+rng.uniform(.95,1.05,N));c2=220e-9*(rng.uniform(.95,1.05,N)+rng.uniform(.95,1.05,N))
data['MonteCarlo']['HP20']={'f0_Hz':stats(1/(2*np.pi*np.sqrt(a*b*c1*c2))),'Q':stats(np.sqrt(a*b*c1*c2)/(a*(c1+c2)))}
# U4A feedback factor with input grounded and CS 10k || 10p load.
# Two-pole illustrative opamp model: 300k DC gain, 7MHz unity, 50deg native PM.
fs=np.geomspace(100,100e6,20000);fu=7e6;f2=fu/math.tan(math.radians(40));f1=fu*math.sqrt(1+(fu/f2)**2)/300000
loop=[];zsrc=[]
for f in fs:
 s=2j*np.pi*f;gm=1/10000;gs=1/2200;gi=1/20000;gc=1/10000+s*10e-12;cc=s*100e-12
 beta=np.linalg.solve(np.array([[gm+gi+cc,-gm],[-gm,gm+gs+gc]]),[cc,gs])[0]
 A=300000/((1+s/(2*np.pi*f1))*(1+s/(2*np.pi*f2)))
 loop.append(A*beta)
 # Closed-loop source impedance at CS pin for small injected load current.
 # M node: (gi+gm+cc) M -gm Y -cc X =0; X=-A M.
 m_y=gm/(gi+gm+cc*(1+A));x_y=-A*m_y
 zsrc.append(1/(gs*(1-x_y)+gm*(1-m_y)))
ix=int(np.argmin(abs(np.log(abs(np.array(loop))))));data['U4A_feedback_model']={'model_limit':'Illustrative two-pole fit, not manufacturer macromodel or PCB stability qualification','unity_loop_Hz':float(fs[ix]),'phase_margin_deg':float(180+np.angle(loop[ix],deg=True)),'CS_source_ohms':{str(f):float(abs(zsrc[np.argmin(abs(fs-f))])) for f in [100,120,1000,20000]}}
# Precision ratio common-mode error of Kelvin ground-sensing output.
cm=[]
for a,b,c,d in itertools.product([.999,1.001],repeat=4):cm.append((1+2*b/a)*(d/(2*c+d))-1)
data['remote_ground']={'max_ratio_common_mode_error':max(map(abs,cm)),'ratio_CMR_dB':-20*math.log10(max(map(abs,cm))),'P68_10R_parallel_30k_ohm':1/(1/10+1/30000)}
# Regulated-supply / reference / relay conservative DC budgets (not measured).
# U7 +/- analog 7mA typical, 9mA max, digital .45/.8mA plus pullups.
# Budget +5A 12mA, -5A 10mA; each 4570 max8mA, 6 packages.
iop_typ=.030;iop_max=.048;icontrol_typ=.018;icontrol_max=.030
rail_budget={}
for mode,n in [('REF',2),('AV',5)]:
 coil_typ=(5-.15)/145*n;coil_max=5.25/(145*.9)*n
 i5typ=coil_typ+icontrol_typ;i5max=coil_max+icontrol_max
 iptyp=iop_typ+.010+i5typ+.005;intyp=iop_typ+.008
 ipmax=iop_max+.012+i5max+.008+.012;inmax=iop_max+.010+.010
 rail_budget[mode]={'coils':n,'coil_typ_mA':coil_typ*1000,'coil_cold_upper_mA':coil_max*1000,'plus15_typ_mA':iptyp*1000,'minus15_typ_mA':intyp*1000,'plus15_budget_mA':ipmax*1000,'minus15_budget_mA':inmax*1000,'board_typ_W':15*(iptyp+intyp),'board_budget_W':15.75*(ipmax+inmax),'U13_typ_W':10*i5typ+15*.005,'U13_budget_W':(15.75-4.75)*i5max+15.75*.008}
data['supply']=rail_budget
data['LM4040']={'nominal_shunt_mA':((5-2.5)/680-2.5/20000-17.5/195000-7.5/106600)*1000,'min_shunt_mA':((4.75-2.5025)/(680*1.01)-2.5025/19980-18.2525/194805-7.7525/106493.4)*1000,'max_shunt_mA':(5.25-2.4975)/(680*.99)*1000,'R74_upper_mW':(5.25-2.4975)**2/(680*.99)*1000}
# Rail trip exhaustive resistor/ref/offset bounds at 25C. Input bias 0..250nA;
# shared VREF loading 0..4*250nA; clamp leakage 0..2uA conservative datasheet limit.
trip={}
for label,r1,r2,tol,neg in [('pos15',100000,10000,.01,False),('pos5',24000,10000,.01,False),('neg15',15000,180000,.001,True),('neg5',20000,86600,.001,True)]:
 vals=[]
 for e1,e2,ez,et,eb,ib,ir,vos,leak in itertools.product([-1,1],[-1,1],[-1,1],[-1,1],[-1,1],[0,250e-9],[0,1e-6],[-.005,.005],[0,2e-6] if neg else [0]):
  a=r1*(1+e1*tol);b=r2*(1+e2*tol);vz=2.5*(1+ez*.001);top=10000*(1+et*.001);bot=10000*(1+eb*.001);vr=vz*bot/(top+bot)+ir*top*bot/(top+bot);v=vr+vos
  vals.append((vz*b/a-(1+b/a)*v+b*(ib-leak)) if neg else v*(1+a/b)-ib*a)
 trip[label]=[min(vals),max(vals)]
data['rail_trip_25C_V_magnitudes']=trip
data['DC_block']={'C63_nominal_uF':10,'charging_tau_s':10e-6*(22000+100),'worst_tau_with_C20pct_R1pct_s':12e-6*(22220+101),'residual_fraction_after_2s_worst':math.exp(-2/(12e-6*(22220+101))),'loaded_pole_Hz_approx':1/(2*np.pi*10e-6*(100+1/(1/22000+1/23000)))}
(out/'engineering-calculations.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({k:data[k] for k in ['stage_2Vrms','U4A_feedback_model','supply','rail_trip_25C_V_magnitudes','DC_block']},indent=2))
