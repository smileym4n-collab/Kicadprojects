from pathlib import Path
import math, cmath, json, csv, random
P=Path(__file__).resolve().parents[1]
freqs=[40,50,60,70,80,100,119]
LP_SERIES=4270
LP_SHUNT=15000
def effective_pot(r):return r*LP_SHUNT/(r+LP_SHUNT)
LP_K=1/(2*math.pi*math.sqrt(440e-9*220e-9))
rs=[LP_K/f for f in freqs]
pot_positions=[(r-LP_SERIES)*LP_SHUNT/(LP_SHUNT-(r-LP_SERIES)) for r in rs]
lp=[dict(label=f,R=r,pot_R=rp,f0=LP_K/r,Q=1/math.sqrt(2)) for f,r,rp in zip(freqs,rs,pot_positions)]
hp=[dict(label=f,R1=a,R2=b,f0=1/(2*math.pi*440e-9*math.sqrt(a*b)),Q=math.sqrt(a*b)/(2*a)) for f,a,b in [(15,16900,34000),(20,12700,25500),(25,10200,20500)]]
def L(f,r1,r2,cf=440e-9,cg=220e-9):
 s=2j*math.pi*f
 return 1/(1+s*cg*(r1+r2)+s*s*r1*r2*cf*cg)
def H(f,a,b,c1=440e-9,c2=440e-9):
 s=2j*math.pi*f
 return s*s*c1*c2*a*b/(1+s*a*(c1+c2)+s*s*c1*c2*a*b)
def AP(f,r): return (1-2j*math.pi*f*r*220e-9)/(1+2j*math.pi*f*r*220e-9)
rows=[]
for i in range(1201):
 f=10**(math.log10(2)+i/1200*math.log10(1000/2))
 l=L(f,LP_K/70,LP_K/70);h=H(f,12700,25500)
 rows.append([f,20*math.log10(abs(l)),20*math.log10(abs(l*l)),20*math.log10(abs(h)),20*math.log10(abs(l*h)),20*math.log10(abs(l*l*h)),math.degrees(cmath.phase(l)),math.degrees(cmath.phase(h))])
with (P/'design/filter-response.csv').open('w') as fh:
 w=csv.writer(fh);w.writerow(['Hz','LP12_dB','LP24_dB','HP20_dB','REF12_HP20_dB','REF24_HP20_dB','LP12_phase_deg','HP20_phase_deg']);w.writerows(rows)
random.seed(68)
mc=[]
for _ in range(20000):
 # Capacitor/fixed-resistor tolerance only, with nominal matched pots set to
 # 70Hz. Pot +/-20% tolerance/tracking is not a 1% resistor distribution.
 r1=LP_SERIES*random.uniform(.99,1.01)+effective_pot(pot_positions[3])
 r2=LP_SERIES*random.uniform(.99,1.01)+effective_pot(pot_positions[3])
 cf=220e-9*(random.uniform(.95,1.05)+random.uniform(.95,1.05));cg=220e-9*random.uniform(.95,1.05)
 mc.append((1/(2*math.pi*math.sqrt(r1*r2*cf*cg)), math.sqrt(r1*r2*cf*cg)/(cg*(r1+r2))))
def pct(a,p): return sorted(a)[int((len(a)-1)*p)]
result={'LP':lp,'LP_control':{'part':'PTD904-2015K-B203','series_R':LP_SERIES,'pot_shunt_R':LP_SHUNT,'gang_nominal_R':20000,'nominal_endpoints_Hz':[LP_K/(LP_SERIES+effective_pot(20000)),LP_K/LP_SERIES],'CCW_endpoint_with_16k_24k_gangs_Hz':[LP_K/(LP_SERIES+effective_pot(16000)),LP_K/(LP_SERIES+effective_pot(24000))],'limitations':'Nominal matched gangs. +/-20% total resistance and rheostat tracking require measurement; no guarantee of a 40Hz endpoint or Q across travel.'},'HP':hp,'tolerance_70Hz_matched_nominal_pot_1pct_series_R_5pct_C':{'f0_p05_p95':[pct([a for a,b in mc],.05),pct([a for a,b in mc],.95)],'Q_p05_p95':[pct([b for a,b in mc],.05),pct([b for a,b in mc],.95)]},'phase_at_70_deg':[math.degrees(cmath.phase(AP(70,r))) for r in [2200,2200+50000*47000/(50000+47000)]],'HP20_at_40_dB':20*math.log10(abs(H(40,12700,25500))),'HP20_at_80_dB':20*math.log10(abs(H(80,12700,25500))),'HP20_phase_40_deg':math.degrees(cmath.phase(H(40,12700,25500))),'max_source_rms_nominal_CS':3.5/(math.sqrt(2)*(20/22)*.5),'design_source_rms':4,'CS_input_peak_at_design':4*math.sqrt(2)*(20/22)*.5,'typical_output_noise_floor_CS_x2_uVrms':8.4}
(P/'design/calculations.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__': print(json.dumps(result,indent=2))
