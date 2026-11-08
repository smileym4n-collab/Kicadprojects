"""Scoped 2x15W-at-16V revision. Run once; preserve unrelated source text."""
from schlib import *
import re
p=Path('Amp.kicad_sch');src=p.read_text()
# Identify top-level forms without reformatting the user's KiCad save.
def spans(text):
 depth=0;quoted=False;escaped=False;start=None
 for i,c in enumerate(text):
  if quoted:
   if escaped:escaped=False
   elif c=='\\':escaped=True
   elif c=='"':quoted=False
   continue
  if c=='"':quoted=True
  elif c=='(':
   if depth==1:start=i
   depth+=1
  elif c==')':
   depth-=1
   if depth==1 and start is not None:yield start,i+1;start=None
changes=[]
vals={'R12':('1k2','RMCF0805FT1K20'),'R14':('1k2','RMCF0805FT1K20'),'R13':('1k5','RMCF0805FT1K50'),'R15':('1k5','RMCF0805FT1K50'),'R19':('10k','RK73B2ATTD103J'),'R20':('33k DNP',None)}
for a,b in spans(src):
 raw=src[a:b];n=parse(raw);new=raw
 if n[0]=='symbol' and val(n,'Reference') in vals:
  ref=val(n,'Reference');value,mpn=vals[ref]
  def replaceprop(text,key,value):
   text,count=re.subn(r'(\(property\s+'+re.escape(json.dumps(key))+r'\s+)"(?:\\.|[^"\\])*"',lambda m:m[1]+json.dumps(value),text,count=1)
   assert count,(ref,key)
   return text
  new=replaceprop(new,'Value',value)
  if mpn:new=replaceprop(new,'MPN',mpn)
  if ref in ['R12','R13','R14','R15']:
   new=re.sub(r'\s*\(property\s+"Inventory_ID".*?(?=\n\s*\(property|\n\s*\(pin|\n\s*\(instances)', '', new,flags=re.S) if False else new
   # Keep the field as an explicit non-stock marker, rather than old inventory allocation.
   if prop(n,'Inventory_ID'):new=replaceprop(new,'Inventory_ID','')
   if prop(n,'Assembly_Note'):new=replaceprop(new,'Assembly_Note','1%, 2012 metric, 125mW. Purchase required; stock package/value does not match.')
  if ref=='R19':
   new=replaceprop(new,'Inventory_ID','194')
   if prop(n,'Assembly_Note'):new=replaceprop(new,'Assembly_Note','10k 5% RC filter from regulated 3V3-ESP to PLIMIT; inventory ID194.')
  if ref=='R20':
   new=new.replace('(dnp no)','(dnp yes)')
   if prop(n,'Assembly_Note'):new=replaceprop(new,'Assembly_Note','DNP. Optional PLIMIT tuning shunt; no fitted divider.')
 elif n[0]=='label' and n[1]=='GVDD' and list(map(float,get(n,'at')[1:3]))==[45.72,200.66]:
  new=raw.replace('"GVDD"','"3V3-ESP"',1)
 elif n[0]=='text' and n[1]=='PLIMIT IS PROVISIONAL':new=raw.replace(json.dumps(n[1]),json.dumps('15 W / CHANNEL TARGET AT 16 V'),1)
 elif n[0]=='text' and list(map(float,get(n,'at')[1:3]))==[119.38,207.01]:
  t='PLIMIT: 3V3-ESP -> 10k / 1u RC; R20 DNP.\nTI peak-rail model ~19W unclipped / 4 ohm nominal.\nHeadroom for 15W; not an exact 15W protection limit.\nInput pad 1k2 / 1k5 plus DAC 470R -> 0.466 gain.\n15W / 4 ohm = 7.75Vrms: calibrate DSP per channel.\nPower derates below 16V; measure clipping / thermals.'
  new=raw.replace(json.dumps(n[1],ensure_ascii=False),json.dumps(t,ensure_ascii=False),1)
 if new!=raw:changes.append((a,b,new))
assert len(changes)==9,[(parse(src[a:b])[0],parse(src[a:b])[1]) for a,b,_ in changes]
for a,b,new in reversed(changes):src=src[:a]+new+src[b:]
p.write_text(src)
print('Changed six resistor instances, one rail label, two explanatory texts.')
