#!/usr/bin/env python3
"""Audit deliverable consistency and record hashes; not a hardware release test.
Rev 0.2: the project-file guard checks that only KiCad-initialised settings sections differ from
work/original (board/schematic defaults, an empty ERC section), instead of byte equality; the PCB must
still be byte-identical. Part count, compensation and bias-network assertions are Rev 0.2 specific."""
from pathlib import Path
import json,csv,re,hashlib,datetime,collections,subprocess
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
subprocess.run(['python3',str(P/'tools/verify_netlist.py')],cwd=P,check=True)
c=json.loads((P/'work/connectivity_verification.json').read_text())
assert c['status']=='PASS'
assert 'ERC messages: 0  Errors 0  Warnings 0' in (P/'work/ERC.rpt').read_text()
assert (P/'MOSFETAmp2.kicad_pcb').read_bytes()==(P/'work/original/MOSFETAmp2.kicad_pcb').read_bytes(),'PCB altered'
po=json.loads((P/'work/original/MOSFETAmp2.kicad_pro').read_text());pn=json.loads((P/'MOSFETAmp2.kicad_pro').read_text())
changed={k for k in set(po)|set(pn) if po.get(k)!=pn.get(k)};assert changed<={'board','schematic','erc'},changed
assert not pn.get('erc',{}).get('erc_exclusions'),'ERC exclusions present'
bom=list(csv.DictReader((P/'BOM.csv').open()));assert sum(int(r['Required'])for r in bom)==140
usage=collections.Counter();stock={}
for r in bom:
 if r['Inventory_ID'] and r['Available']:
  usage[r['Inventory_ID']]+=int(r['Required']);stock[r['Inventory_ID']]=int(r['Available'])
for k,n in usage.items():assert n<=stock[k],(k,n,stock[k])
for key in ['Q113','Q114','Q213','Q214','R123','R124','R223','R224']:assert not re.search(r'\b'+key+r'\b',(P/'work/stereo.xml').read_text()),key+' unexpected output limiter'
cir=(P/'simulation/channel.cir').read_text();assert 'CC=330p' in cir
for z in ['R12 BC BB 3.9k','R13 BB BN {R13}','Q16 BB BREF BCE BC546B','D13 BREF VN LEDR','RV1 BW VN {RV}','.include models/mosfets_infineon.lib']:assert z in cir,z
assert 'Z4V3' not in cir and 'BZX79' not in (P/'work/stereo.xml').read_text(),'Rev 0.1 Zener bias part present'
for r in bom:
 if r['References']=='C102, C202':assert r['Value']=='330p C0G'
 if r['References']=='R112, R212':assert r['Value']=='3k9'
for f in ['README.md','docs/BIAS_STUDY.md','simulation/results_bias/bias_study_infineon.json','simulation/results_bias/bias_dynamic_infineon.json','docs/DESIGN.md','docs/SIMULATION.md','docs/LAYOUT.md','docs/BENCH_TEST.md','docs/PURCHASE_LIST.md','docs/Schematic.pdf','simulation/results/summary.json','simulation/results/extended_summary.json','simulation/results/supplement_summary.json']:assert (P/f).is_file(),f
logs=list((P/'simulation/results').glob('*.log'));warnings={}
for p in logs:
 t=p.read_text()
 assert not re.search(r'(?im)(?:^Error|Timestep too small|doAnalyses:|unknown parameter)',t),p.name
 w=[line for line in t.splitlines()if 'Warning' in line]
 if w:warnings[p.name]=w
files=[]
for g in ['*.kicad_sch','*.kicad_sym','*.kicad_pro','*.kicad_pcb','*-lib-table','BOM.csv','README.md','MOSFETAmp2.pretty/*','docs/*.md','docs/*.pdf','docs/plots/*','inventory/*.json','simulation/*.py','simulation/*.cir','simulation/*.txt','simulation/models/*','simulation/models/infineon/*','simulation/results_bias/*.json','simulation/results/*','tools/*.py','tools/ngspice/bin/ngspice']:
 files.extend(p for p in P.glob(g)if p.is_file())
manifest={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'disposition':'DEVELOPMENT ONLY — NOT FABRICATION RELEASED','kicad_version':'10.0.5','erc':{'errors':0,'warnings':0,'scope':'default project severities; no new exclusions'},'connectivity':{k:v for k,v in c.items()if k!='notes'},'stereo_bom_components':140,'unique_inventory_records_reused_or_conditional':len(usage),'all_aggregate_stock_quantities_sufficient':True,'inventory_mutations':False,'revision':'0.2','original_pcb_preserved':True,'project_file':'KiCad settings sections only differ from original; no ERC exclusions','pcb':'original empty board; no layout/DRC release','simulator':'ngspice 47 macOS arm64','simulation_logs_checked':len(logs),'simulation_warnings':warnings,'models':'Infineon MODPEX MOSFET subcircuits with imposed temperature/spread; author-approximated BD139/BD140/BAT46/Zener/LED; NXP BC546B/BC556B','rev01_failed_corner_in_rev02_model':'low-threshold pair, -4 mV/K, 75 C: see supplement_summary low_threshold_warm (Rev 0.1: 263 mA)','unverified':['actual MOSFET VGS slope, R113/R114 selection and bias range','Q108 beta and LED temperature-coefficient sensitivities','bias rail sensitivity','warm-up and signal-to-idle thermal stability','hot repetitive/DC linear-mode SOA','actual THD/noise, HF stability and clipping','power transformer, reservoirs and rail envelope','owned heatsink/interface thermal resistance','pot/power-resistor/coil physical fit','PCB placement/routing/DRC and bench testing'],'sha256':{str(p.relative_to(P)):sha(p)for p in sorted(set(files))}}
(P/'work/verification_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:v for k,v in manifest.items()if k not in ['sha256','unverified']},indent=2))
