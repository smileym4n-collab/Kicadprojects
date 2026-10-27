"""Scoped property/text edits; preserves every electrical and graphical object."""
import re,json,sys
from pathlib import Path
sys.path.insert(0,'review/scripts')
from schlib import parse,val,get,many
out=Path('review/revisions/preorder-corrections-2026-10-23')
def q(s):return json.dumps(str(s),ensure_ascii=False)
def children(s):
 depth=0;quoted=False;esc=False;start=None
 for i,c in enumerate(s):
  if quoted:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quoted=False
   continue
  if c=='"':quoted=True
  elif c=='(':
   if depth==1:start=i
   depth+=1
  elif c==')':
   depth-=1
   if depth==1 and start is not None:yield start,i+1;start=None

def setprops(block,changes):
 parsed=parse(block); at=get(parsed,'at');edits=[];found=set()
 for a,b in children(block):
  t=parse(block[a:b])
  if t[0]=='property' and t[1] in changes:
   found.add(t[1]);pattern=r'^(\(property\s+"(?:\\.|[^"\\])*"\s+)"(?:\\.|[^"\\])*"'
   new=re.sub(pattern,lambda m:m[1]+q(changes[t[1]]),block[a:b],count=1);edits.append((a,b,new))
 for a,b,new in reversed(edits):block=block[:a]+new+block[b:]
 extra=''
 for k,v in changes.items():
  if k not in found:extra+='\n\t\t(property '+q(k)+' '+q(v)+' (at '+str(at[1])+' '+str(at[2])+' 0) (effects (font (size 1.27 1.27)) (hide yes)))'
 if extra:block=block[:-1]+extra+'\n\t)'
 return block

changes={}
def select(refs,mpn,mfr,iid,volt='',dielectric='',power='',tol='',note='',ds=''):
 for ref in refs.split(','):
  d={'MPN':mpn,'Manufacturer_Name':mfr,'Manufacturer_Part_Number':mpn,'Inventory_ID':str(iid) if iid else '', 'Assembly_Note':note,'Datasheet':ds}
  if volt:d['Voltage_Rating']=volt
  if dielectric:d['Dielectric']=dielectric
  if power:d['Power_Rating']=power
  if tol:d['Tolerance']=tol
  changes[ref]=d
select('C28','C0805C105K3RACTU','KEMET',728,'25 V','X7R',tol='10%',note='1u / 25 V X7R, 2012 metric. GVDD decoupling; matches retained footprint. MCP: 0 physical, 100 on order (23 Oct 2026).',ds='https://search.kemet.com/component-documentation/download/specsheet/C0805C105K3RACTU')
select('C30,C31,C33,C34','MC0603B104K500CT','Multicomp Pro',698,'50 V','X7R',tol='10%',note='100n / 50 V X7R, 1608 metric; matches retained footprint. MCP: 0 physical, 1000 on order (23 Oct 2026).',ds='https://cpc.farnell.com/multicomp-pro/mc0603b104k500ct/mlcc-0603-x7r-50v-100nf/dp/CA06380')
select('C56,C57','CL10B102KB8NNNC','Samsung Electro-Mechanics',509,'50 V','X7R',tol='10%',note='1n / 50 V X7R, 1608 metric. Supply bypass, not audio-path filtering. MCP physical stock 100 (23 Oct 2026).',ds='https://product.samsungsem.com/mlcc/CL10B102KB8NNN.do')
select('C45','CL31A106KBHNNNE','Samsung Electro-Mechanics',505,'50 V','X5R',tol='10%',note='10u / 50 V X5R, 3216 metric; retains PCB footprint. MCP stock 10. Typical DC bias: about 3u at 16 V. At 1 A buck output, estimated input ripple ~0.13 Vpp; bulk C47 retained. Validate ripple on bench. See scoped correction report.',ds='https://product.samsungsem.com/mlcc/CL31A106KBHNNN.do')
# Owned part with manufacturer-authored specifications; no need for precision filtering here.
select('C32,C54,C59,C60','MC0805N103F500CT','Multicomp Pro',297,'50 V','C0G/NP0',tol='1%',note='10n / 50 V C0G, 2012 metric. Fitted post-filter series RC branch with 3R3. MCP stock 10 (23 Oct 2026).',ds='https://www.farnell.com/datasheets/4417444.pdf')
select('R6,R20,R34,R40','CRCW08053R30FKEAHP','Vishay',None,power='0.5 W',tol='1%',note='3R3, 1%, 0.5 W P70, pulse-proof thick film, 2012 metric. Fitted output RC resistor; not DNP. Power rating requires suitable board cooling; verify temperature on bench. No MCP stock match.',ds='https://www.vishay.com/docs/20043/crcwhpe3.pdf')
select('C21','UES1H470MPM','Nichicon',None,'50 V','Bipolar electrolytic',tol='20%',note='47u / 50 V bipolar UES, diameter 10 mm x 20 mm, pitch 5 mm. Onboard tweeter series capacitor. JP1 OPEN = capacitor active; JP1 linked = bypass/stereo. User confirmed C21 checked on 23 Oct 2026. Ripple/heating qualification is separate.',ds='https://www.nichicon.co.jp/english/products/pdfs/e-ues.pdf')
select('C1,C2,C5,C6','R82DC4100AA60J','KEMET',132,'63 V','Metallized polyester film',tol='5%',note='1u / 63 V film, 5 mm pitch, body 7.2 x 5 x 10 mm. Exact MCP stock identity confirmed: 43 physical (23 Oct 2026). Matches retained 7.2 x 5 mm footprint; replaces former WIMA purchase fallback metadata only.',ds='https://search.kemet.com/download/specsheet/R82DC4100AA60J')
changes['J2']={'MPN':'B8B-XH-A(LF)(SN)','Manufacturer_Name':'JST','Manufacturer_Part_Number':'B8B-XH-A(LF)(SN)','Datasheet':'https://www.jst-mfg.com/product/pdf/eng/eXH.pdf','Assembly_Note':'8-position top-entry XH, 2.50 mm pitch, matching retained footprint. Mating housing XHP-8 with suitable SXH contacts. No MCP stock match for B8B-XH-A.'}
changes['HS1']={'MPN':'ATS-TI1OP-521-C1-R1','Assembly_Note':'User confirmed heatsink fit/clearance checked on 23 Oct 2026. Retain existing mechanical placement. Bench enclosure thermal qualification remains required.'}


# Remove conflicting inherited manufacturer fields without changing selected parts.
for ref,mpn,mfr in [
 ('R24','RC0603FR-0716K2L','Yageo'),('C49','CL31A226KAHNNNE','Samsung Electro-Mechanics'),('C50','CL31A226KAHNNNE','Samsung Electro-Mechanics'),
 ('D1','1N4740ATR','onsemi'),('D2','SMBJ16A','Littelfuse'),('J1','09-65-2028','Molex'),
 ('C51','CL21A106KOQNNNF','Samsung Electro-Mechanics'),('C52','CL21A106KOQNNNF','Samsung Electro-Mechanics'),
 ('C46','MC0603B104K500CT','Multicomp Pro'),('C48','MC0603B104K500CT','Multicomp Pro'),('C53','MC0603B104K500CT','Multicomp Pro'),
 ('IC5','ESP32-WROVER-IE-N16R8','Espressif Systems')]:
 changes[ref]={'Manufacturer_Part_Number':mpn,'Manufacturer_Name':mfr}

replacements={
'DAC.kicad_sch':{
'PCM5122 - left woofer, right tweeter, register controlled':'PCM5122 - L tweeter / R woofer',
'OUTL -> woofer (TPA right bridge); OUTR -> tweeter (TPA left bridge).':'OUTL -> tweeter / J17 (TPA left bridge); OUTR -> woofer / J16 (TPA right bridge).'},
'TPA3126.kicad_sch':{
'PCM5122 LEFT = woofer / CH1; RIGHT = tweeter / CH2. Both speaker returns are active.':'PCM5122 LEFT = tweeter / J17; RIGHT = woofer / J16. Both speaker returns are active.',
'External Nichicon UES capacitor on J18; replace with shorting link for stereo use.':'C21: onboard 47u / 50V bipolar Nichicon UES; JP1 shorts it for stereo use.',
'Enable SDZ, wait >=50 ms, release DAC mute, then amplifier mute; ramp DAC volume.':'Release DAC XSMT with valid muted I2S; enable SDZ, wait >=50 ms, release MUTE; ramp volume.'},
'Amp.kicad_sch':{
'TPA3126D2 - stereo BTL, bypassable CH2 capacitor':'TPA3126D2 - stereo BTL / C21 bypass',
'C54 = Nichicon UES1H470MPM, 47u / 50V bipolar, 10 x 20 mm.\nWire across J18 pins 1-2. It is in series with CH2 positive.\nFor stereo: remove capacitor harness and fit a rated shorting link.\nWith neither cap nor link, CH2 positive is OPEN (safe no-output).\nPin 1 = filtered bridge positive; pin 2 = speaker connector positive.\nNeither pin is ground. Change link only with power off.\nNominal 4 ohm pole ~847 Hz; actual response follows tweeter impedance.\nAccount for capacitor phase/response in the DSP crossover.':
'C21 = Nichicon UES1H470MPM, 47u / 50V bipolar, 10 x 20 mm.\nOnboard in series with filtered tweeter positive -> J17 pin 1.\nJP1 OPEN: capacitor active; JP1 LINKED: bypass for stereo use.\nUse a short insulated wire link rated >=3 A; change only with power off.\nNeither speaker terminal is ground. Without cap or link, output is open.\nNominal 4 ohm pole ~847 Hz; actual response follows tweeter impedance.\nAccount for capacitor phase/response in the DSP crossover.\nHeatsink and C21 fit checked by user (23 Oct 2026); bench thermal test remains.',
'EXTERNAL TWEETER CAPACITOR / STEREO BYPASS':'ONBOARD TWEETER CAPACITOR / JP1 STEREO BYPASS',
'WOOFER: DAC LEFT -> AMPLIFIER RIGHT BRIDGE':'WOOFER / J16: DAC RIGHT -> AMPLIFIER RIGHT BRIDGE',
'TWEETER: DAC RIGHT -> AMPLIFIER LEFT BRIDGE':'TWEETER / J17: DAC LEFT -> AMPLIFIER LEFT BRIDGE',
'SNUBBERS C41-C44 / R35-R38: DNP, tune on bench.\nTI starting point 330p / 18R; no copied TPA3220 snubber.\nAll filtered speaker terminals float relative to GND.':
'OUTPUT RC: C32/C54/C59/C60 = 10n C0G / 50V, FITTED.\nR6/R20/R34/R40 = 3R3 / 0.5W pulse-proof, FITTED.\nPost-filter branches to GND; check resistor heating on bench.',
'Keep 20 x 18 x 10 mm heatsink clearance over U1; top PowerPAD, no PCB EP copper.':'ATS-TI1OP-521-C1-R1 over U1; fit checked by user. Top PowerPAD, no PCB EP copper.',
'PLIMIT: 3V3-ESP -> 10k / 1u RC; R20 DNP.':'PLIMIT: 3V3-ESP -> R19 10k / C29 1u RC; no lower divider resistor.'},
'ESP32.kicad_sch':{
'VOLUME POT: J2 pins 2=GND, 3=wiper, 4=3V3. Use 10k linear.':'VOLUME POT: J2 pins 1 or 5=GND, 3=wiper, 4=3V3. Use 10k linear.',
'J2 system: 2=GND, 3=volume wiper, 4=3V3. Suggested pot: 10k linear.\nJ3 is the separate programming header; use 3.3 V UART logic.\nModule custom pads 39-47 are segments of the common exposed GND area.\nFit a compatible external antenna to the IE module; keep RF connector/feed away from switch nodes.':
'J2: 1=GND, 2=MODEBTN, 3=pot wiper, 4=3V3, 5=GND.\nJ2: 6=BT LED drive, 7=GND, 8=Wi-Fi LED drive (both drives via 1k).\nMODEBTN: GPIO22 / module pin 36, R35=10k pull-up; switch pin 2 to pin 5 GND.\nDebounce in firmware. J3 is 3.3 V UART; module pads 39-47 are GND.\nIE module requires an external antenna; keep RF feed away from switch nodes.'},
'Power.kicad_sch':{
'L1 6u8: ripple ~0.93 A p-p at 16 V, nominal 500 kHz. Local ceramics at VIN/SW.':'L1 6u8: ripple ~0.93 A p-p at 16 V, nominal 500 kHz. Local ceramics at VIN/SW.\nC45 10u / 50V X5R: ~3u typical at 16V; estimated VIN ripple ~0.13Vpp at 1A output.'}}
modified=[]
for fn in ['TPA3126.kicad_sch','ESP32.kicad_sch','DAC.kicad_sch','Amp.kicad_sch','Power.kicad_sch']:
 p=Path(fn);s=p.read_text();before=s;edits=[]
 for a,b in children(s):
  block=s[a:b]
  if block.startswith('(symbol\n') or block.startswith('(symbol '):
   ref=val(parse(block),'Reference')
   if ref in changes:edits.append((a,b,setprops(block,changes[ref])))
 for a,b,new in reversed(edits):s=s[:a]+new+s[b:]
 for old,new in replacements.get(fn,{}).items():
  # Multiline texts can contain the old sentence inside a larger quoted string.
  encodedold=q(old)[1:-1];encodednew=q(new)[1:-1]
  assert encodedold in s or encodednew in s,(fn,old)
  if encodednew not in s:s=s.replace(encodedold,encodednew)
 s=s.replace('(date "2026-10-19")','(date "2026-10-23")').replace('(rev "Schematic review A")','(rev "Pre-order B")')
 if s!=before:p.write_text(s);modified.append(fn)
(out/'selections.json').write_text(json.dumps(changes,indent=2)+'\n')
print('Updated:',', '.join(modified))
