"""Reproducible schematic generation. Does not read or write the PCB/project settings."""
from pathlib import Path
from copy import deepcopy
import json, math, uuid, sys
from sexpr import parse,dump,Q,child,children
P=Path(__file__).resolve().parents[1]
BASE=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
ROOT='b4d45b7b-ad9d-4a36-949e-5b2f0775370b'
def uid(key): return str(uuid.uuid5(uuid.NAMESPACE_URL,'SubController-RevA/'+key))
def q(s): return json.dumps(str(s),ensure_ascii=False)
def n(v): return f'{v:.5f}'.rstrip('0').rstrip('.') if isinstance(v,float) else str(v)
def effects(size=1.27,justify='',hide=False): return f'(effects (font (size {size} {size})) '+(f'(justify {justify}) ' if justify else '')+('(hide yes) ' if hide else '')+')'
cache={};custom={}
def libsym(lib,name):
 key=lib+':'+name
 if key in cache: return cache[key]
 data=parse((BASE/(lib+'.kicad_sym')).read_text());s=deepcopy(next(s for s in children(data,'symbol') if s[1]==name))
 ext=child(s,'extends')
 if ext:
  base=deepcopy(libsym(lib,ext[1]));base[1]=Q(name)
  base=[x for x in base if not(isinstance(x,list) and x[0]=='property')]+children(s,'property')
  for sub in children(base,'symbol'): sub[1]=Q(name+'_'+str(sub[1]).rsplit('_',2)[1]+'_'+str(sub[1]).rsplit('_',2)[2])
  s=base
 cache[key]=s;return s
def pin(num,name,x,y,ang,typ='passive',length=2.54):
 return f'(pin {typ} line (at {n(x)} {n(y)} {ang}) (length {length}) (name {q(name)} {effects(1.0)}) (number {q(num)} {effects(1.0)}))'
def block(name,pins,width=15.24,height=None,foot='',desc='',datasheet=''):
 height=height or (max(abs(p[2]) for p in pins)+2.54)
 body=f'(rectangle (start {-width} {height}) (end {width} {-height}) (stroke (width 0.254) (type default)) (fill (type background)))'
 ps=''.join(pin(num,label,x,y,a,t) for num,label,x,y,a,t in pins)
 custom[name]=parse(f'(symbol {q(name)} (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 {height+2.54} 0) {effects()}) (property "Value" {q(name)} (at 0 {-height-2.54} 0) {effects()}) (property "Footprint" {q(foot)} (at 0 0 0) {effects(hide=True)}) (property "Datasheet" {q(datasheet)} (at 0 0 0) {effects(hide=True)}) (property "Description" {q(desc)} (at 0 0 0) {effects(hide=True)}) (symbol {q(name+"_0_1")} {body}) (symbol {q(name+"_1_1")} {ps}))')
op=deepcopy(libsym('Amplifier_Operational','NE5532'));op[1]=Q('uPC4570G2')
for prop in children(op,'property'):
 if prop[1]=='Value':prop[2]=Q('uPC4570G2')
 if prop[1]=='Footprint':prop[2]=Q('SubController:SOP-8_uPC4570G2_4.4x5.2mm_P1.27mm')
 if prop[1]=='Datasheet':prop[2]=Q('https://www.renesas.com/en/document/dst/upc4570-datasheet')
for sub in children(op,'symbol'):sub[1]=Q('uPC4570G2_'+str(sub[1]).rsplit('_',2)[1]+'_'+str(sub[1]).rsplit('_',2)[2])
custom['uPC4570G2']=op
stock=deepcopy(libsym('Transistor_BJT','BC337'));stock[1]=Q('BC337_stock')
for sub in children(stock,'symbol'):sub[1]=Q('BC337_stock_'+str(sub[1]).rsplit('_',2)[1]+'_'+str(sub[1]).rsplit('_',2)[2])
custom['BC337_stock']=stock
reg=deepcopy(libsym('Regulator_Linear','L7805'));reg[1]=Q('7805_stock')
for prop in children(reg,'property'):
 if prop[1]=='Value':prop[2]=Q('7805 (Diodes stock)')
 if prop[1]=='Datasheet':prop[2]=Q('https://www.diodes.com/datasheet/download/AS7805A.pdf')
for sub in children(reg,'symbol'):sub[1]=Q('7805_stock_'+str(sub[1]).rsplit('_',2)[1]+'_'+str(sub[1]).rsplit('_',2)[2])
custom['7805_stock']=reg
# Manufacturer terminal numbering, with contact units separated for readable wiring.
relaybody=''
for u,com,nc,no in [(1,'3','2','4'),(2,'6','7','5')]:
 shape='(polyline (pts (xy -2.54 0) (xy 2.54 5.08)) (stroke (width 0.254) (type default)) (fill (type none)))'
 relaybody+=f'(symbol "G6K_2P_Y_{u}_1" {shape} '+pin(com,'COM',-10.16,0,0)+pin(nc,'NC',10.16,5.08,180)+pin(no,'NO',10.16,-5.08,180)+')'
relaybody+='(symbol "G6K_2P_Y_3_1" (rectangle (start -2.54 5.08) (end 2.54 -5.08) (stroke (width 0.254) (type default)) (fill (type none))) '+pin('1','COIL+',0,7.62,270)+pin('8','COIL-',0,-7.62,90)+')'
custom['G6K_2P_Y']=parse('(symbol "G6K_2P_Y" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "K" (at 0 8.89 0) '+effects()+') (property "Value" "G6K-2P-Y / 5V" (at 0 -8.89 0) '+effects()+') (property "Footprint" "Relay_THT:Relay_DPDT_Omron_G6K-2P" (at 0 0 0) '+effects(hide=True)+') '+relaybody+')')
child(next(p for p in children(custom['G6K_2P_Y'],'property') if p[1]=='Footprint'),'at')
next(p for p in children(custom['G6K_2P_Y'],'property') if p[1]=='Footprint')[2]=Q('SubController:G6K-2P-Y_Verified')
for rows,name in [(7,'FrequencyBank_2x7'),(3,'FrequencyBank_2x3')]:
 pins=[]
 for j in range(rows):
  y=(rows-1)/2*7.62-j*7.62
  pins.extend([(2*j+1,'',-10.16,y,0,'passive'),(2*j+2,'',10.16,y,180,'passive')])
 block(name,pins,7.62,(rows-1)/2*7.62+3.81,f'Connector_PinHeader_2.54mm:PinHeader_2x{rows:02d}_P2.54mm_Vertical')
block('CS3310',[(16,'AINL',-17.78,10.16,0,'input'),(9,'AINR',-17.78,5.08,0,'input'),(14,'AOUTL',17.78,10.16,180,'output'),(11,'AOUTR',17.78,5.08,180,'output'),(2,'~{CS}',-17.78,-2.54,0,'input'),(3,'SDATAI',-17.78,-7.62,0,'input'),(6,'SCLK',-17.78,-12.7,0,'input'),(8,'~{MUTE}',17.78,-2.54,180,'input'),(1,'ZCEN',17.78,-7.62,180,'input'),(7,'SDATAO',17.78,-12.7,180,'output'),(12,'VA+',-7.62,20.32,270,'power_in'),(4,'VD+',0,20.32,270,'power_in'),(13,'VA-',7.62,20.32,270,'power_in'),(15,'AGNDL',-7.62,-20.32,90,'power_in'),(10,'AGNDR',0,-20.32,90,'power_in'),(5,'DGND',7.62,-20.32,90,'power_in')],15.24,17.78,'Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm','Analog resistor ladder and output buffer; NEVER digitises audio','https://www.mouser.com/datasheet/2/76/CS3310_F1-18400.pdf')
block('TPS7A3901',[(1,'INP',-17.78,25.4,0,'power_in'),(2,'EN',-17.78,15.24,0,'input'),(3,'NR/SS',-17.78,-5.08,0,'passive'),(5,'INN',-17.78,-15.24,0,'power_in'),(10,'OUTP',17.78,25.4,180,'power_out'),(9,'FBP',17.78,15.24,180,'input'),(8,'BUF',17.78,0,180,'output'),(7,'FBN',17.78,-5.08,180,'input'),(6,'OUTN',17.78,-15.24,180,'power_out'),(4,'GND',-5.08,-30.48,90,'power_in'),(11,'EP',5.08,-30.48,90,'power_in')],12.7,27.94,'SubController:TPS7A3901_DSC0010J_WSON10','TI dual +/-150mA LDO; negative lower feedback resistor connects to BUF, NOT GND. EP11 = GND.','https://www.ti.com/lit/ds/symlink/tps7a39.pdf')
block('VO617A-3',[(1,'A',-10.16,2.54,0,'passive'),(2,'K',-10.16,-2.54,0,'passive'),(4,'C',10.16,2.54,180,'open_collector'),(3,'E',10.16,-2.54,180,'passive')],7.62,7.62,'Package_DIP:DIP-4_W7.62mm','Isolated SELV trigger input; VO617A-3 base ordering code is through-hole DIP4.','https://www.vishay.com/docs/83430/vo617a.pdf')
# Bourns repeats terminal 1/2/3 on each R1..R4 section. Preserve both
# identifiers in symbol/pad numbers, rather than inventing a global 1..12 map.
pot=deepcopy(libsym('Device','R_Potentiometer'));pot[1]=Q('PTD904_2015K_B203')
for prop in children(pot,'property'):
 if prop[1]=='Value':prop[2]=Q('PTD904-2015K-B203')
 if prop[1]=='Footprint':prop[2]=Q('SubController:PTD904_2015K_B203_Horizontal')
 if prop[1]=='Datasheet':prop[2]=Q('https://www.bourns.com/docs/product-datasheets/ptd90.pdf')
 if prop[1]=='Description':prop[2]=Q('Four mechanically linked 20k linear gangs; R1 nearest shaft; pads Rn.1/2/3 are manufacturer section/terminal IDs.')
 if prop[1]=='ki_fp_filters':prop[2]=Q('PTD904*')
pot=[x for x in pot if not (isinstance(x,list) and x[0]=='property' and str(x[1]).startswith('Sim.'))]
common=deepcopy(children(pot,'symbol')[0]);common[1]=Q('PTD904_2015K_B203_0_1')
one=deepcopy(children(pot,'symbol')[1]);pot=[x for x in pot if not (isinstance(x,list) and x[0]=='symbol')]+[common]
for gang in range(1,5):
 sub=deepcopy(one);sub[1]=Q(f'PTD904_2015K_B203_{gang}_1')
 for pp in children(sub,'pin'):
  child(pp,'number')[1]=Q(f'R{gang}.'+str(child(pp,'number')[1]))
  child(pp,'length')[1]='2.54'
  at=child(pp,'at')
  if float(at[1]):at[1]='5.08'
  if float(at[2]):at[2]='5.08' if float(at[2])>0 else '-5.08'
  child(child(pp,'number'),'effects')[1][1:]=[['size','0.8','0.8']]
 pot.append(sub)
custom['PTD904_2015K_B203']=pot
counter={};bom={};sheets=[]
class Sheet:
 def __init__(self,file,title,page):
  short={'01_inputs.kicad_sch':'Inputs and source isolation','02_crossover.kicad_sch':'Reference low-pass crossover','03_level_phase.kicad_sch':'Level and phase','04_protection_output.kicad_sch':'Subsonic, polarity and output','05_control.kicad_sch':'Control and isolated trigger','06_power_mute.kicad_sch':'Power and rail supervision','07_drivers.kicad_sch':'Relay drivers and PSU interlock'}
  self.file=file;self.title=short.get(file,title);self.page=page;self.uuid=uid(file);self.items=[];self.libs={};self.count=0;sheets.append(self)
 def id(self,kind):self.count+=1;return uid(self.file+kind+str(self.count))
 def text(self,t,x,y,size=1.27):self.items.append(f'(text {q(t)} (at {n(x)} {n(y)} 0) {effects(size,"left top")} (uuid {self.id("text")}))')
 def wire(self,*points):
  for a,b in zip(points,points[1:]):
   if a!=b:self.items.append(f'(wire (pts (xy {n(a[0])} {n(a[1])}) (xy {n(b[0])} {n(b[1])})) (stroke (width 0) (type default)) (uuid {self.id("wire")}))')
 def dot(self,p):self.items.append(f'(junction (at {n(p[0])} {n(p[1])}) (diameter 0) (color 0 0 0 0) (uuid {self.id("junc")}))')
 def label(self,t,p,angle=0,global_=False):
  if t=='GND':return self.gnd(p)
  kind='global_label' if global_ else 'label'
  self.items.append(f'({kind} {q(t)} '+('(shape passive) ' if global_ else '')+f'(at {n(p[0])} {n(p[1])} {angle}) {effects(1.016,"left" if angle==0 else "right")} (uuid {self.id("label")}))')
 def net(self,t,p,dx=5.08):
  e=(p[0]+dx,p[1]);self.wire(p,e);self.label(t,e,0 if dx>=0 else 180,True)
 def sym(self,key,x,y,ref=None,value=None,unit=1,angle=0,foot=None,dnp=False,note=None):
  if key.startswith('SubController:'):s=deepcopy(custom[key.split(':')[1]])
  else:s=deepcopy(libsym(*key.split(':')))
  s[1]=Q(key);self.libs[key]=s
  prefix=next(p[2] for p in children(s,'property') if p[1]=='Reference')
  if ref is None:counter[prefix]=counter.get(prefix,0)+1;ref=prefix+str(counter[prefix])
  import re
  match=re.fullmatch(r'([A-Z]+)(\d+)',str(ref))
  if match:counter[match[1]]=max(counter.get(match[1],0),int(match[2]))
  val=value or next(p[2] for p in children(s,'property') if p[1]=='Value')
  fp=foot if foot is not None else next((p[2] for p in children(s,'property') if p[1]=='Footprint'),'')
  body=f'(symbol (lib_id {q(key)}) (at {n(x)} {n(y)} {angle}) (unit {unit}) (in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid {self.id("symbol")}) '
  rx,ry,vx,vy,j=x+1.27,y-5.08,x+1.27,y-2.54,'left'
  hr=hv=False
  if key.startswith('power:'):hr=True;hv=(key=='power:GND')
  if key in ['Device:R','Device:C','Device:C_Polarized','Device:D']:
   if angle in [90,270]:rx,ry,vx,vy,j=x,y-2.54,x,y+2.54,''
   else:rx,ry,vx,vy,j=x+3.81,y-1.27,x+3.81,y+1.27,'left'
  if key.startswith('Connector_Generic:') or 'FrequencyBank' in key:
   high=max(float(child(p,'at')[2]) for u in children(s,'symbol') for p in children(u,'pin'))
   rx,ry,vx,vy,j=x+2.54,y-high-6.35,x+2.54,y-high-3.81,'left'
  if key=='SubController:G6K_2P_Y':rx,ry,vx,vy,j=x-7.62,y-11.43,x-7.62,y-8.89,'left'
  if key=='SubController:CS3310':rx,ry,vx,vy,j=x,y-25.4,x,y-22.86,''
  if key=='SubController:TPS7A3901':rx,ry,vx,vy,j=x,y-33.02,x,y-30.48,''
  if key in ['MCU_Microchip_ATtiny:ATtiny412-SS','Interface_Expansion:MCP23008-xSS']:rx,ry,vx,vy,j=x-10.16,y-22.86,x-10.16,y-20.32,'left'
  if key=='SubController:BC337_stock':rx,ry,vx,vy,j=x+7.62,y+1.27,x+7.62,y+3.81,'left'
  if key=='SubController:VO617A-3':rx,ry,vx,vy,j=x-5.08,y-15.24,x-5.08,y-12.7,'left'
  if key=='SubController:PTD904_2015K_B203':rx,ry,vx,vy,j=x,y-10.16,x,y-7.62,''
  pa=90 if key in ['Device:R','Device:C','Device:C_Polarized','Device:D','SubController:PTD904_2015K_B203'] and angle in [90,270] else 0
  body+=f'(property "Reference" {q(ref)} (at {n(rx)} {n(ry)} {pa}) {effects(1.016,j,hr)}) (property "Value" {q(val)} (at {n(vx)} {n(vy)} {pa}) {effects(1.016,j,hv)}) (property "Footprint" {q(fp)} (at {n(x)} {n(y)} 0) {effects(hide=True)}) '
  ds=next((p[2] for p in children(s,'property') if p[1]=='Datasheet'),'')
  body+=f'(property "Datasheet" {q(ds)} (at {n(x)} {n(y)} 0) {effects(hide=True)}) '
  if note:body+=f'(property "Design_note" {q(note)} (at {n(x)} {n(y)} 0) {effects(hide=True)}) '
  body+=f'(instances (project "SubController" (path "/{ROOT}/{self.uuid}" (reference {q(ref)}) (unit {unit})))) )'
  self.items.append(body)
  if not ref.startswith('#'):bom.setdefault(ref,{'Reference':ref,'Value':str(val),'Footprint':str(fp),'DNP':dnp,'Sheet':self.title,'Note':note or ''})
  pins={};a=math.radians(angle)
  for sub in children(s,'symbol'):
   u=int(str(sub[1]).rsplit('_',2)[1])
   if u not in [0,unit]:continue
   for p in children(sub,'pin'):
    at=child(p,'at');px,py=float(at[1]),float(at[2]);xx=px*math.cos(a)-py*math.sin(a);yy=px*math.sin(a)+py*math.cos(a)
    pins[str(child(p,'number')[1])]=(round(x+xx,5),round(y-yy,5))
  return pins,ref
 def nc(self,p):self.items.append(f'(no_connect (at {n(p[0])} {n(p[1])}) (uuid {self.id("nc")}))')
 def gnd(self,p):self.sym('power:GND',*p)
 def resistor(self,x,y,v,angle=90,note=None):return self.sym('Device:R',x,y,value=v,angle=270 if angle==90 else angle,foot='Resistor_SMD:R_0805_2012Metric',note=note)[0]
 def cap(self,x,y,v,angle=0,film=False):return self.sym('Device:C',x,y,value=v,angle=270 if angle==90 else angle,foot='SubController:Film_7.2x2.5mm_P5.00mm' if film else 'Capacitor_SMD:C_1206_3216Metric',note='FILM; measure actual lead pitch before layout' if film else 'Supply bypass only; X7R allowed')[0]
 def conn(self,x,y,count,value,foot=None):return self.sym('Connector_Generic:Conn_01x'+str(count).zfill(2),x,y,value=value,foot=foot or f'Connector_PinHeader_2.54mm:PinHeader_1x{count:02d}_P2.54mm_Vertical')[0]
 def jumper(self,x,y,opts,value):
  ps=self.conn(x,y,3,value);self.net(opts[0],ps['1'],-5.08);self.net(opts[1],ps['2'],-5.08);self.net(opts[2],ps['3'],-5.08);return ps
 def powercap(self,x,y,net,v='100n / 50V'):
  p=self.cap(x,y,v);self.net(net,p['1']);self.gnd(p['2'])
 def op(self,x,y,ref,unit):return self.sym('SubController:uPC4570G2',x,y,ref=ref,unit=unit)[0]
 def follower(self,x,y,ref,unit,inp,out):
  p=self.op(x,y,ref,unit);a,b,c=('3','2','1') if unit==1 else ('5','6','7')
  self.net(inp,p[a],-5.08);end=(p[c][0]+7.62,p[c][1]);self.wire(p[c],end);self.label(out,end,global_=True)
  self.wire(end,(end[0],p[b][1]+10.16),(p[b][0]-2.54,p[b][1]+10.16),(p[b][0]-2.54,p[b][1]),p[b]);self.dot(end)
 def inverter(self,x,y,ref,unit,inp,out,rin='10k',rf='10k'):
  p=self.op(x,y,ref,unit);a,b,c=('3','2','1') if unit==1 else ('5','6','7')
  ri=self.resistor(p[b][0]-15.24,p[b][1],rin);self.net(inp,ri['2'],-5.08);self.wire(ri['1'],p[b]);self.gnd(p[a])
  rb=self.resistor(x,p[b][1]+12.7,rf);self.wire(p[b],(p[b][0]-5.08,p[b][1]),(p[b][0]-5.08,rb['1'][1]),rb['2']);end=(p[c][0]+10.16,p[c][1]);self.wire(p[c],end,(end[0],rb['1'][1]),rb['1']);self.label(out,end,global_=True);self.dot(end)
  self.dot((p[b][0]-5.08,p[b][1])) # Survives KiCad's merged-wire save.
 def op_power(self,x,y,ref):
  ps=self.sym('SubController:uPC4570G2',x,y,ref=ref,unit=3)[0];self.net('+15V',ps['8'],-5.08);self.net('-15V',ps['4'],-5.08)
  self.powercap(x+22.86,y-7.62,'+15V');self.powercap(x+45.72,y-7.62,'-15V');self.powercap(x+68.58,y-7.62,'+15V','1u / 50V');self.powercap(x+91.44,y-7.62,'-15V','1u / 50V');self.text(ref+': caps physically at pins 8/4',x-5.08,y+10.16,1.016)
 def save(self):
  text='(kicad_sch (version 20250114) (generator "eeschema") (generator_version "10.0") '+f'(uuid {self.uuid}) (paper "A3") (title_block (title {q(self.title)}) (date "2026-10-07") (rev "A - review") (company "DIY active subwoofer controller") (comment 1 "Audio remains analogue; no PCB layout or fabrication approval")) (lib_symbols '+' '.join(dump(s) for s in self.libs.values())+') '+' '.join(self.items)+' (embedded_fonts no))\n'
  (P/self.file).write_text(text)

# 2: Input isolation, input buffers and averaging summer.
s=Sheet('01_inputs.kicad_sch','INPUT SELECTION / SOURCE RETURN ISOLATION',2)
s.text('RCA shells MUST be insulated from plate/chassis. No upstream bias or ESD path to board GND.',20.32,15.24)
for x,y,val,a,b in [(35.56,45.72,'REF LEFT','REF_L','REF_L_RETURN'),(35.56,76.2,'REF RIGHT','REF_R','REF_R_RETURN'),(35.56,106.68,'MARANTZ LFE','LFE','LFE_RETURN')]:
 p=s.conn(x,y,2,val);s.net(a,p['1'],-5.08);s.net(b,p['2'],-5.08)
def relay(sheet,x,y,ref):
 ps=sheet.sym('SubController:G6K_2P_Y',x,y,ref=ref,unit=1,note='Bottom-view manufacturer numbering; NC=2/7, COM=3/6, NO=4/5; coil=1/8')[0]
 ps.update(sheet.sym('SubController:G6K_2P_Y',x,y+40.64,ref=ref,unit=2)[0]);return ps
p=relay(s,106.68,60.96,'K1')
for pn,net in {'2':'REF_L','7':'REF_R','4':'LFE','5':'LFE','3':'SEL_L','6':'SEL_R'}.items():s.net(net,p[pn],10.16 if pn in ['2','4','5','7'] else -10.16)
p=relay(s,106.68,167.64,'K2')
for pn,net in {'2':'REF_L_RETURN','7':'REF_R_RETURN','4':'LFE_RETURN','5':'LFE_RETURN','3':'GND','6':'GND'}.items():s.net(net,p[pn],10.16 if pn in ['2','4','5','7'] else -10.16)
s.text('NC = REFERENCE; energised = AV.\nK1/K2 switch while K4 muted. Coils on driver sheet.',66.04,129.54,1.016)
for x,y,ref,unit,inp,out in [(210.82,50.8,'U1',1,'SEL_L','BUF_L'),(210.82,101.6,'U1',2,'SEL_R','BUF_R')]:
 r=s.resistor(x-30.48,y-2.54,'1k');s.net(inp,r['2'],-5.08)
 node=(x-17.78,y-2.54);s.wire(r['1'],node)
 rb=s.resistor(node[0],y+10.16,'47k',angle=0);s.wire(node,rb['1']);s.gnd(rb['2']);s.dot(node)
 # shunt RF capacitance after 1k input series; C0G only
 cap=s.sym('Device:C',node[0]-12.7,y+10.16,value='100p C0G',foot='Capacitor_SMD:C_0805_2012Metric')[0];branch=(node[0],node[1]+5.08);s.wire(branch,(cap['1'][0],branch[1]),cap['1']);s.dot(branch);s.gnd(cap['2'])
 op=s.op(x,y,ref,unit);a,b,c=('3','2','1') if unit==1 else ('5','6','7')
 s.wire(node,op[a]);end=(op[c][0]+7.62,op[c][1]);s.wire(op[c],end);s.label(out,end,global_=True)
 s.wire(end,(end[0],y+22.86),(op[b][0]-2.54,y+22.86),(op[b][0]-2.54,op[b][1]),op[b]);s.dot(end)
s.text('Input loading: 48k incl. series resistor.\nBuffer DC gain: 47/48 = 0.979 (-0.18 dB).\n100p RF shunt: ~1.63 MHz, no bass impact.',177.8,139.7)
p=s.op(332.74,71.12,'U2',1);s.gnd(p['3'])
ra=s.resistor(292.1,p['2'][1]-7.62,'20k');rb=s.resistor(292.1,p['2'][1]+7.62,'20k');s.net('BUF_L',ra['2'],-5.08);s.net('BUF_R',rb['2'],-5.08)
node=(312.42,p['2'][1]);s.wire(ra['1'],(node[0],ra['1'][1]),node,p['2']);s.wire(rb['1'],(node[0],rb['1'][1]),node);s.dot(node)
s.dot((node[0],rb['1'][1])) # Branch into the vertical summing/feedback wire.
rf=s.resistor(332.74,101.6,'10k');end=(p['1'][0]+10.16,p['1'][1]);s.wire(p['1'],end,(end[0],101.6),rf['1']);s.wire(node,(node[0],101.6),rf['2']);s.label('SUM_INV',end,global_=True);s.dot(end)
s.inverter(332.74,152.4,'U2',2,'SUM_INV','MONO')
s.text('MONO = 0.5L + 0.5R. In AV both inputs receive LFE, so MONO=LFE.\nNo driver/enclosure boost. Main speakers remain full range.',246.38,198.12)
s.op_power(152.4,231.14,'U1');s.op_power(297.18,231.14,'U2')

# 3: two SK lowpass filters. One PCB-mounted four-gang pot tunes all four R paths.
s=Sheet('02_crossover.kicad_sch','REFERENCE LOW-PASS / FOUR-GANG CONTINUOUS CONTROL',3)
s.text('Unity SK: Cf=200n (2x100n), Cg=100n; matched total R1/R2 => Q=0.7071.\nRV1: one PCB-mounted PTD904-2015K-B203, four mechanically linked 20k linear gangs.',20.32,12.7)
def lp_stage(x,y,unit,inp,out,index):
 p=s.op(x+60.96,y+2.54,'U3',unit);a,b,c=('3','2','1') if unit==1 else ('5','6','7')
 # Four series resistor + rheostat paths are drawn together below.
 s.label(f'LP{index}_A',(x+22.86,y),global_=True);s.label(f'LP{index}_B',(x+45.72,y),global_=True)
 s.wire((x+45.72,y),p[a]);s.dot((x+45.72,y))
 s.text(f'R path {index*2-1}',x,y-7.62,1.016);s.text(f'R path {index*2}',x+25.4,y-7.62,1.016)
 cg=s.cap(x+45.72,y+15.24,'100n FILM',film=True);s.wire((x+45.72,y),cg['1']);s.gnd(cg['2'])
 e=(p[c][0]+7.62,p[c][1]);s.wire(p[c],e);s.label(out,e,global_=True)
 s.wire(e,(e[0],y+30.48),(p[b][0]-2.54,y+30.48),(p[b][0]-2.54,p[b][1]),p[b]);s.dot(e)
 for cy in [y-17.78,y-30.48]:
  cf=s.cap(x+35.56,cy,'100n FILM',angle=90,film=True);s.wire((x+22.86,y),(x+22.86,cy),cf['2']);s.wire(cf['1'],(e[0],cy),e)
  s.dot((x+22.86,cy));s.dot((e[0],cy)) # Explicit branch joints survive KiCad merged-wire saves.
 s.dot((x+22.86,y));s.text('R1/R2 paths continue through RV1 gangs below',x-2.54,y+40.64,1.016)
lp_stage(45.72,76.2,1,'MONO','LP12',1);lp_stage(233.68,76.2,2,'LP12','LP24',2)
s.jumper(373.38,154.94,['LP12','REF_LP','LP24'],'SLOPE: 1-2=12 / 2-3=24')
for i,(src,dst) in enumerate([('MONO','LP1_A'),('LP1_A','LP1_B'),('LP12','LP2_A'),('LP2_A','LP2_B')]):
 x=73.66+i*88.9;y=195.58;gang=i+1
 rr=s.sym('Device:R',x-20.32,y,ref=f'R{10+7*i}',value='9k31',angle=270,foot='Resistor_SMD:R_0805_2012Metric',note='Minimum filter R; 1% thin-film; trim only after measuring RV1 gangs.')[0]
 pp=s.sym('SubController:PTD904_2015K_B203',x,y,ref='RV1',unit=gang,angle=270,note='Owned: user reports two. Four 20k linear gangs, +/-20%; matching to be measured. Rn.1 tied to Rn.2; Rn.3 is CW end.')[0]
 s.net(src,rr['2'],-5.08);s.wire(rr['1'],pp[f'R{gang}.3'])
 out=(x+12.7,y);s.wire(pp[f'R{gang}.1'],out);s.net(dst,out,2.54)
 s.wire(pp[f'R{gang}.2'],(out[0],pp[f'R{gang}.2'][1]),out);s.dot(out)
 s.text(f'Gang R{gang}: '+src+' -> '+dst,x-40.64,y+15.24,1.016)
counter['R']=37;counter['J']=8 # Retire removed bank references; preserve all other refs.
s.text('Nominal R=9k31 + 0..20k; f0=120.9..38.4 Hz. CW increases crossover frequency.\nAt 70 Hz each rheostat is ~6k77. Match gangs and film caps; calibrate actual knob scale.\nWiper tied to unused terminal 1: loss of wiper contact leaves full track resistance.\nRV1 body/shaft needs front-edge and plate alignment during future layout; operating ambient <=50 C.',20.32,231.14,1.016)
s.op_power(180.34,269.24,'U3')

# 4: attenuator and all-pass.
s=Sheet('03_level_phase.kicad_sch','ELECTRONIC ANALOGUE LEVEL / VARIABLE ALL-PASS PHASE',4)
s.text('K3 pole A bypasses ONLY the Reference low-pass in AV. Pole B selects AV HP configuration on next sheet.',20.32,15.24)
p=relay(s,63.5,53.34,'K3')
for pn,net in {'2':'REF_LP','4':'MONO','3':'LEVEL_IN','7':'HP_OUT','5':'AV_HP_SELECT','6':'HP_SELECTED'}.items():s.net(net,p[pn],10.16 if pn in ['2','4','5','7'] else -10.16)
s.inverter(172.72,60.96,'U4',1,'LEVEL_IN','ATT_IN','20k','10k')
s.text('Fixed -0.5 = headroom protection.\nOutput -2 restores unity overall.',132.08,101.6)
p=s.sym('SubController:CS3310',304.8,71.12,'U7')[0]
for pn,net in {'16':'ATT_IN','14':'ATT_OUT','9':'GND','15':'GND','10':'GND','5':'GND','2':'CS_N','3':'CS_DATA','6':'CS_CLK','8':'CS_RUN','1':'+5A'}.items():s.net(net,p[pn],-5.08 if pn in ['16','9','2','3','6'] else 5.08)
s.nc(p['11']);s.nc(p['7'])
s.wire(p['12'],(p['12'][0],p['12'][1]-15.24),(p['4'][0],p['4'][1]-15.24),p['4']);s.net('+5A',(p['12'][0],p['12'][1]-15.24),-10.16)
s.wire(p['13'],(p['13'][0],p['13'][1]-7.62));s.net('-5A',(p['13'][0],p['13'][1]-7.62),10.16)
s.text('Left channel only. Right input grounded; right gain code=0 (mute).\nREF and AV levels stored independently by MCU.\nFirmware must prohibit all positive gain codes.',246.38,132.08)
s.powercap(261.62,175.26,'+5A');s.powercap(299.72,175.26,'-5A');s.powercap(337.82,175.26,'+5A')
s.follower(162.56,149.86,'U6',2,'ATT_OUT','ATT_BUFFER');s.text('U6B isolates CS output from the HP / all-pass network.\nCS sees only op-amp input / short trace capacitance (<100pF).',127,172.72,1.016)
# allpass with remote 50k rheostat pot; parallel resistor caps source resistance.
p=s.op(149.86,203.2,'U4',2)
ri=s.resistor(109.22,p['6'][1],'10k');s.net('ATT_BUFFER',ri['2'],-5.08);s.wire(ri['1'],p['6'])
rf=s.resistor(149.86,236.22,'10k');e=(p['7'][0]+10.16,p['7'][1]);s.wire(p['7'],e,(e[0],236.22),rf['1']);s.wire(p['6'],(p['6'][0]-5.08,p['6'][1]),(p['6'][0]-5.08,236.22),rf['2']);s.label('AP_OUT',e,global_=True);s.dot(e)
s.dot((p['6'][0]-5.08,p['6'][1]))
rs=s.resistor(58.42,p['5'][1],'2k2');s.net('ATT_BUFFER',rs['2'],-5.08);s.label('PHASE_TOP',rs['1'],global_=True)
rp=s.resistor(88.9,p['5'][1],'47k');s.net('PHASE_TOP',rp['2'],-2.54);node=(p['5'][0]-10.16,p['5'][1]);s.wire(rp['1'],node,p['5']);s.label('PHASE_WIPER',node,global_=True);s.dot(node)
cc=s.cap(node[0],node[1]-17.78,'220n FILM',film=True);s.wire(cc['2'],node);s.gnd(cc['1'])
hp=s.conn(48.26,236.22,3,'PANEL PHASE 50k LINEAR');s.net('PHASE_TOP',hp['1'],-5.08);s.net('PHASE_WIPER',hp['2'],-5.08);s.net('PHASE_WIPER',hp['3'],-5.08)
s.jumper(251.46,220.98,['ATT_BUFFER','PHASE_OUT','AP_OUT'],'PHASE BYPASS / ALLPASS')
s.text('Panel pot: pin1 top; pin2 wiper; pin3 tied wiper (fail-safe full R).\nAt 70 Hz: -24 to -137 deg; use bypass for 0 deg. Not constant time delay.',20.32,259.08)
s.op_power(299.72,231.14,'U4')

# 5: HP, polarity, output buffer/mute.
s=Sheet('04_protection_output.kicad_sch','CONFIGURABLE SUBSONIC / POLARITY / OUTPUT MUTE',5)
s.text('Default REF HP=20 Hz; AV HP bypass preserves AVR response. AV may select HP_OUT when protection required.',20.32,15.24)
p=s.op(152.4,76.2,'U5',1)
c1=s.cap(58.42,73.66,'220n FILM',90,True);c1b=s.cap(58.42,55.88,'220n FILM',90,True)
c2=s.cap(106.68,73.66,'220n FILM',90,True);c2b=s.cap(106.68,55.88,'220n FILM',90,True)
s.net('PHASE_OUT',c1['2'],-5.08);a=(81.28,73.66);b=(129.54,73.66)
s.wire(c1['1'],a,c2['2']);s.wire(c2['1'],b,p['3']);s.dot(a);s.dot(b)
s.wire(c1['2'],(c1['2'][0],55.88),c1b['2']);s.wire(c1b['1'],(a[0],55.88),a)
s.wire(c2['2'],(c2['2'][0],55.88),c2b['2']);s.wire(c2b['1'],(b[0],55.88),b)
e=(p['1'][0]+10.16,p['1'][1]);s.wire(p['1'],e);s.label('HP_OUT',e,global_=True)
s.wire(e,(e[0],104.14),(p['2'][0]-2.54,104.14),(p['2'][0]-2.54,p['2'][1]),p['2']);s.dot(e)
s.label('HP_A',a,global_=True);s.label('HP_B',b,global_=True)
s.text('R1 bank: HP_A to HP_OUT. R2 bank: HP_B to GND.\nC1=C2=440n; Q approx 0.707; unity gain above HP corner.',30.48,121.92)
for i,(src,dst,vals) in enumerate([('HP_A','HP_OUT',['16k9','12k7','10k2']),('HP_B','GND',['34k','25k5','20k5'])]):
 x=50.8+i*93.98;y=172.72
 h=s.sym('SubController:FrequencyBank_2x3',x+22.86,y,ref=f'J{11+i}',value=f'HP BANK {i+1}: 15/20/25')[0]
 for j,v in enumerate(vals):
  aa=h[str(2*j+1)];bb=h[str(2*j+2)];rr=s.resistor(aa[0]-15.24,aa[1],v);s.wire(rr['1'],aa);s.net(src,rr['2'],-2.54);s.net(dst,bb,2.54)
s.jumper(238.76,50.8,['PHASE_OUT','AV_HP_SELECT','HP_OUT'],'AV HP: BYPASS / FILTER')
s.jumper(238.76,88.9,['PHASE_OUT','HP_FINAL','HP_SELECTED'],'COMMON HP: BYPASS / MODE')
s.inverter(302.26,137.16,'U5',2,'HP_FINAL','POL_INV')
s.jumper(370.84,53.34,['HP_FINAL','POLARITY_OUT','POL_INV'],'POLARITY 0 / 180')
s.inverter(302.26,205.74,'U6',1,'POLARITY_OUT','AMP_DRIVE','10k','20k')
r=s.resistor(340.36,205.74,'100R');s.net('AMP_DRIVE',r['2'],-5.08);s.label('AMP_SERIES',r['1'],global_=True)
p=relay(s,365.76,147.32,'K4')
for pn,net in {'2':'GND','4':'AMP_SERIES','3':'AMP_OUT'}.items():s.net(net,p[pn],10.16 if pn in ['2','4'] else -10.16)
for pn in ['5','6','7']:s.nc(p[pn])
o=s.conn(386.08,208.28,2,'TO P68 INPUT');s.net('AMP_OUT',o['1'],-5.08);s.gnd(o['2'])
pd=s.resistor(363.22,236.22,'100k',0);s.net('AMP_OUT',pd['1']);s.gnd(pd['2'])
s.text('K4 OFF: P68 input grounded; buffer disconnected.\nON: 100R isolates cable capacitance.\nP68 nominal 22k / gain 23; confirm actual amplifier.',266.7,251.46,1.016)
s.op_power(35.56,233.68,'U5');s.op_power(152.4,233.68,'U6')


# Control sheet
s=Sheet('05_control.kicad_sch','ATtiny412 / PANEL ENCODERS / ISOLATED TRIGGER / RELAY DRIVERS',6)
s.text('AUDIO IS NEVER DIGITISED. MCU controls relays and analog attenuation only.\nSoftware GPIO for I2C and inverted 10 kHz serial interface; PA0 reserved UPDI.',20.32,15.24)
p=s.sym('MCU_Microchip_ATtiny:ATtiny412-SS',58.42,71.12,'U8')[0]
for pn,net in {'1':'+5R','8':'GND','6':'UPDI','4':'SER_DATA_INV','5':'SER_CLK_INV','7':'SER_CS_INV','2':'I2C_SDA','3':'I2C_SCL'}.items():s.net(net,p[pn],5.08 if pn not in ['1','8'] else -5.08)
co=s.conn(48.26,134.62,3,'UPDI / +5R / GND');s.net('UPDI',co['1'],-5.08);s.net('+5R',co['2'],-5.08);s.gnd(co['3'])
s.powercap(27.94,101.6,'+5R')
p=s.sym('Interface_Expansion:MCP23008-xSS',185.42,71.12,'U9',value='MCP23008-E/SS')[0]
mp={'1':'I2C_SCL','2':'I2C_SDA','3':'GND','4':'GND','5':'GND','6':'IO_RESET_N','9':'GND','20':'+5R','12':'REF_ENC_A','13':'REF_ENC_B','14':'AV_ENC_A','15':'AV_ENC_B','16':'TRIGGER_N','17':'AV_ENABLE','18':'RUN_REQUEST','19':'RAIL_GOOD'}
for pn,net in mp.items():s.net(net,p[pn],-5.08 if pn in ['1','2','3','4','5','6'] else 5.08)
for pn in ['7','8','10','11']:s.nc(p[pn])
s.powercap(154.94,114.3,'+5R')
for x,net in [(109.22,'I2C_SDA'),(132.08,'I2C_SCL')]:
 r=s.resistor(x,48.26,'4k7',0);s.net('+5R',r['1'],-5.08);s.net(net,r['2'],-5.08)
r=s.resistor(132.08,137.16,'10k',0);s.net('+5R',r['1'],-5.08);s.net('IO_RESET_N',r['2'],-5.08);s.powercap(154.94,139.7,'IO_RESET_N')
s.text('MCP reset: all GPIO inputs; external pulldowns keep relays OFF.\nAddress pins A2/A1/A0=0 => I2C 0x20.',129.54,160.02,1.016)
for x,val,a,b in [(266.7,'REF LEVEL ENCODER','REF_ENC_A','REF_ENC_B'),(340.36,'LFE TRIM ENCODER','AV_ENC_A','AV_ENC_B')]:
 co=s.conn(x,48.26,3,val);s.net(a,co['1'],-5.08);s.gnd(co['2']);s.net(b,co['3'],-5.08)
 for j,net in enumerate([a,b]):
  rr=s.resistor(x-20.32+22.86*j,88.9,'10k',0);s.net('+5R',rr['1'],-5.08);s.net(net,rr['2'],-5.08)
co=s.conn(322.58,137.16,2,'ISOLATED TRIGGER 12V');s.net('TRIG_PLUS',co['1'],-5.08);s.net('TRIG_MINUS',co['2'],-5.08)
op=s.sym('SubController:VO617A-3',271.78,180.34,'U10')[0]
r=s.resistor(233.68,op['1'][1],'2k2 / 0.125W');s.net('TRIG_PLUS',r['2'],-5.08);s.wire(r['1'],op['1']);s.net('TRIG_MINUS',op['2'],-5.08)
d=s.sym('Device:D',236.22,195.58,value='1N4148W',angle=90,foot='Diode_SMD:D_SOD-123')[0];s.net('TRIG_MINUS',d['2'],-5.08);s.net('TRIG_LED_A',d['1'],-5.08);s.wire((254,177.8),(254,170.18));s.dot((254,177.8));s.label('TRIG_LED_A',(254,170.18),180,True)
s.net('TRIGGER_RAW',op['4'],5.08);s.gnd(op['3']);r=s.resistor(307.34,180.34,'10k',0);s.net('+5R',r['1']);s.net('TRIGGER_N',r['2'])
s.text('Inactive/open = REF; opto ON = AV. 12V gives ~4.95mA.\nFor 5V trigger fit 750R instead of 2k2. No trigger return to GND.',270.51,251.46,1.016)
for i,(base,out,pull) in enumerate([('SER_DATA_INV','CS_DATA','+5R'),('SER_CLK_INV','CS_CLK','+5R'),('SER_CS_INV','CS_N','GND')]):
 x=48.26+i*88.9;y=218.44
 tr=s.sym('SubController:BC337_stock',x+22.86,y,value='BC337 (stock)',foot='Package_TO_SOT_THT:TO-92_Inline')[0]
 rb=s.resistor(x-2.54,y,'10k');s.net(base,rb['2'],-2.54);s.wire(rb['1'],tr['2']);s.gnd(tr['3']);s.net(out,tr['1'])
 rr=s.resistor(x+45.72,y-20.32,'10k',0);s.net('+5A',rr['1']);s.net(out,rr['2'])
 rr=s.resistor(x-15.24,y+20.32,'47k',0);s.net(base,rr['1'],-2.54);s.net(pull,rr['2'],-2.54)
s.text('Collector outputs referenced to +5A. No MCU power backfeeds CS3310.\nGPIO high => serial low; GPIO low => serial high. Clock/data default low, CS high.',20.32,264.16,1.016)

# Power + monitor + coil drivers sheet
s=Sheet('06_power_mute.kicad_sch','REGULATED SUPPLY INPUT / RAIL MONITOR / FAIL-SAFE MUTE',7)
s.text('SELV ONLY: externally regulated +/-15V input, NEVER P68 high-voltage power rails.\nNominal +/-15V; maximum +/-15.75V. Supply rating >=250mA positive / >=100mA negative.',20.32,12.7)
c=s.conn(40.64,40.64,3,'+15V / GND / -15V');s.net('+15V',c['1'],-5.08);s.gnd(c['2']);s.net('-15V',c['3'],-5.08)
for x,net in [(27.94,'+15V'),(76.2,'-15V'),(116.84,'GND')]:
 ps=s.sym('power:PWR_FLAG',x,101.6)[0];s.net(net,ps['1'])
for x,net in [(71.12,'+15V'),(104.14,'-15V')]:
 ps=s.sym('Device:C_Polarized',x,50.8,value='47u / 25V FR',foot='Capacitor_THT:CP_Radial_D5.0mm_P2.50mm')[0]
 s.net(net,ps['1'] if net=='+15V' else ps['2']);s.gnd(ps['2'] if net=='+15V' else ps['1'])
for x,y,key,ref,inp,out in [(180.34,45.72,'L7805','U11','+15V','+5A'),(180.34,88.9,'L7905','U12','-15V','-5A'),(307.34,45.72,'L7805','U13','+15V','+5R')]:
 ps=s.sym('SubController:7805_stock' if key=='L7805' else 'Regulator_Linear:'+key,x,y,ref=ref,foot='Package_TO_SOT_THT:TO-220-3_Vertical')[0]
 s.net(inp,ps['1'] if key=='L7805' else ps['2'],-5.08);s.net(out,ps['3']);s.gnd(ps['2'] if key=='L7805' else ps['1'])
 s.powercap(x-25.4,y+20.32,inp,'1u / 50V')
 pp=s.sym('Device:C_Polarized',x+30.48,y+20.32,value='47u / 25V FR',foot='Capacitor_THT:CP_Radial_D5.0mm_P2.50mm')[0];s.net(out,pp['2'] if key=='L7905' else pp['1']);s.gnd(pp['1'] if key=='L7905' else pp['2'])
 # reverse discharge protection: positive OUT->IN; negative IN->OUT
 dd=s.sym('Device:D',x,y-15.24,value='1N4007',foot='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal')[0]
 s.net(inp if key=='L7805' else out,dd['1'],-5.08);s.net(out if key=='L7805' else inp,dd['2'],5.08)
s.text('U11 ~0.15W. U12 ~0.12W. U13 up to ~1.4W: heatsink <=30C/W effective required.\nRegulator tolerance must keep CS3310 +/-5V inside +/-5%. Confirm markings before assembly.',139.7,129.54,1.016)
# Rail status is independently observable; transistor interlock overrides RUN.
ps=s.sym('Reference_Voltage:LM4040DBZ-2.5',40.64,182.88,'U14',value='LM4040A25IDBZR')[0]
for pn,pt in ps.items():
 if pn=='1':s.net('VREF_2V5',pt)
 elif pn=='2':s.gnd(pt)
 else:s.nc(pt)
r=s.resistor(30.48,152.4,'680R',0);s.net('+5R',r['1'],-5.08);s.net('VREF_2V5',r['2'],-5.08)
def div(x,y,top,bot,rt,rb,out):
 a=s.resistor(x,y,rt,0);b=s.resistor(x,y+17.78,rb,0);s.net(top,a['1'],-5.08);s.wire(a['2'],b['1']);s.net(out,a['2']);s.net(bot,b['2'],-5.08)
div(76.2,157.48,'VREF_2V5','GND','10k','10k','VREF_1V25')
# R77-R82 retired; preserve all subsequent existing designators.
counter['R']=82
div(233.68,157.48,'+15V','GND','100k','10k','SENSE_POS15')
div(269.24,157.48,'VREF_2V5','-15V','10k','120k','SENSE_NEG15')
div(304.8,157.48,'+5A','GND','24k','10k','SENSE_POS5')
div(340.36,157.48,'VREF_2V5','-5A','10k','43k','SENSE_NEG5')
for i,(pos,neg) in enumerate([('SENSE_POS15','VREF_1V25'),('VREF_1V25','SENSE_NEG15'),('SENSE_POS5','VREF_1V25'),('VREF_1V25','SENSE_NEG5')]):
 ps=s.sym('Comparator:LM339',80.01+i*86.36,231.14,ref='U15',unit=i+1,foot='Package_SO:SOIC-14_3.9x8.7mm_P1.27mm')[0]
 # identify +/- by library pin names
 lib=libsym('Comparator','LM339');sub=next(u for u in children(lib,'symbol') if str(u[1]).endswith(f'_{i+1}_1'))
 for ppin in children(sub,'pin'):
  num=str(child(ppin,'number')[1]);name=str(child(ppin,'name')[1]);s.net(pos if name=='+' else neg if name=='-' else 'RAIL_GOOD',ps[num],-5.08 if name in ['+','-'] else 5.08)
s.text('Trip nominal +13.75V / -13.75V / +4.25V / -4.125V. Shared VREF_1V25.\n+/-5V checks detect collapse, not CS3310 supply-range compliance; hardware overrides RUN.\nNo positive feedback; firmware requires 500ms stable RAIL_GOOD before rearm.',20.32,269.24,1.016)
ps=s.sym('Comparator:LM339',386.08,180.34,ref='U15',unit=5,foot='Package_SO:SOIC-14_3.9x8.7mm_P1.27mm')[0];s.net('+5R',ps['3']);s.gnd(ps['12']);s.powercap(383.54,213.36,'+5R')

s=Sheet('07_drivers.kicad_sch','RELAY COIL DRIVERS / HARDWARE MUTE / STATUS / PSU INTERLOCK',8)
s.text('Default: AV_ENABLE=0, RUN_REQUEST=0. Output stays muted until firmware sequence completed.\nRail interlock clamps RUN_HW independently; MCU requires fresh settling delay after fault.',20.32,15.24)
for x,y,inp,drain,ref,base_r in [(78.74,76.2,'AV_ENABLE','AV_COIL','Q4','470R'),(226.06,76.2,'RUN_HW','MUTE_COIL','Q5','470R')]:
 ps=s.sym('SubController:BC337_stock',x,y,ref=ref,value='BC337 (stock)',foot='Package_TO_SOT_THT:TO-92_Inline')[0]
 rb=s.resistor(x-22.86,y,base_r);s.net(inp,rb['2'],-5.08);s.wire(rb['1'],ps['2']);s.gnd(ps['3']);s.net(drain,ps['1'])
 rr=s.resistor(x-25.4,y+20.32,'100k',0);s.net(inp,rr['1'],-5.08);s.gnd(rr['2'])
 dd=s.sym('Device:D',x+33.02,y,value='1N4148W',angle=90,foot='Diode_SMD:D_SOD-123')[0];s.net('+5R',dd['1']);s.net(drain,dd['2'])
s.text('Q4 switches three 5V relay coils (~60mA).\nQ5 switches K4 coil (~20mA). Flyback diode slows release:\nwait >=30ms after mode-relay operation.\nRUN_HW ~1.7-2.1V ON (base-drive bus, not a CMOS output).',30.48,124.46)
for i in range(4):
 ps=s.sym('SubController:G6K_2P_Y',345.44+i*15.24,71.12,ref=f'K{i+1}',unit=3)[0];s.net('+5R',ps['1'],-2.54);s.net('AV_COIL' if i<3 else 'MUTE_COIL',ps['8'],-2.54)
rr=s.resistor(203.2,157.48,'1k');s.net('RUN_REQUEST',rr['2'],-5.08);s.net('RUN_HW',rr['1'])
# Two conventional inverters release CS mute only with RUN true.
ps=s.sym('SubController:BC337_stock',281.94,167.64,ref='Q6',value='BC337 (stock)',foot='Package_TO_SOT_THT:TO-92_Inline')[0]
rb=s.resistor(256.54,167.64,'10k');s.net('RUN_HW',rb['2'],-5.08);s.wire(rb['1'],ps['2']);s.gnd(ps['3']);s.net('CS_MUTE_INV',ps['1'])
rr=s.resistor(302.26,147.32,'10k',0);s.net('+5R',rr['1']);s.net('CS_MUTE_INV',rr['2'])
ps=s.sym('SubController:BC337_stock',350.52,177.8,ref='Q7',value='BC337 (stock)',foot='Package_TO_SOT_THT:TO-92_Inline')[0]
rb=s.resistor(325.12,177.8,'10k');s.net('CS_MUTE_INV',rb['2'],-5.08);s.wire(rb['1'],ps['2']);s.gnd(ps['3']);s.net('CS_RUN',ps['1'])
rr=s.resistor(373.38,152.4,'10k',0);s.net('+5A',rr['1']);s.net('CS_RUN',rr['2'])
s.text('RUN=0: Q6 OFF, Q7 ON => CS MUTE asserted.\nRUN=1: Q6 ON, Q7 OFF => CS_RUN=+5A.\nCollector interface prevents +5R backfeeding +5A.',266.7,243.84,1.016)
co=s.conn(78.74,195.58,2,'EARLY PSU POWER-FAIL');s.net('RAIL_GOOD',co['1'],-5.08);s.gnd(co['2'])
s.text('Optional open collector contact to GND. Assert before analog rails collapse.\nNO external voltage injection. Without early warning, arbitrary fast\npower loss cannot be guaranteed pop-free by a mechanical relay.',20.32,220.98,1.016)
co=s.conn(200.66,208.28,2,'RUN LED: PIN1 A / PIN2 K');rr=s.resistor(175.26,208.28,'4k7');s.net('+5R',rr['2'],-5.08);s.wire(rr['1'],co['1']);s.net('MUTE_COIL',co['2'],-5.08)
for x,net in [(35.56,'+15V'),(76.2,'-15V'),(116.84,'+5A'),(157.48,'-5A'),(198.12,'+5R'),(238.76,'RUN_HW')]:
 ps=s.sym('Connector:TestPoint',x,269.24,value=net,foot='TestPoint:TestPoint_Pad_D1.5mm')[0];s.net(net,ps['1'])

s=Sheet('08_rail_interlock.kicad_sch','HARDWARE RAIL-FAULT INTERLOCK',9)
s.text('Rail comparators / external early power fail pull RAIL_GOOD low. GP7 reads it independently of RUN_REQUEST.\nOn a fault: mute immediately in hardware; firmware clears RUN_REQUEST and waits 500ms stable RAIL_GOOD before rearm.',20.32,20.32)
rr=s.resistor(58.42,66.04,'4k7',0);s.net('+5R',rr['1']);s.net('RAIL_GOOD',rr['2'])
ps=s.sym('SubController:BC337_stock',144.78,99.06,ref='Q8',value='BC337 (stock)',foot='Package_TO_SOT_THT:TO-92_Inline')[0]
rb=s.resistor(109.22,99.06,'47k');s.net('RAIL_GOOD',rb['2'],-5.08);s.wire(rb['1'],ps['2']);s.gnd(ps['3']);s.net('RAIL_FAULT',ps['1'])
rr=s.resistor(165.1,73.66,'10k',0);s.net('+5R',rr['1']);s.net('RAIL_FAULT',rr['2'])
ps=s.sym('SubController:BC337_stock',274.32,99.06,ref='Q9',value='BC337 (stock)',foot='Package_TO_SOT_THT:TO-92_Inline')[0]
rb=s.resistor(238.76,99.06,'4k7');s.net('RAIL_FAULT',rb['2'],-5.08);s.wire(rb['1'],ps['2']);s.gnd(ps['3']);s.net('RUN_HW',ps['1'])
s.text('Good rails: Q8 ON, Q9 OFF; firmware may release RUN.\nBad rails: Q8 OFF, Q9 ON; RUN_HW clamped, Q5 OFF, K4 grounds amplifier input.\n+5R absent: all coils OFF; K4 grounds amplifier input. No MCU instruction is required for this state.',50.8,152.4)

s=sheets[4]
s.jumper(350.52,111.76,['TRIGGER_RAW','TRIGGER_N','GND'],'AUTO / REF(open) / AV')
s.text('Panel ON-OFF-ON: AUTO / REF / AV. Default shunt 1-2=AUTO.',256.54,119.38,1.016)

# Local CS rail bulk (ceramic bypass only) and conservative ST negative input electrolytic.
s=sheets[2]
for x,net in [(261.62,'+5A'),(299.72,'-5A'),(337.82,'+5A')]:s.powercap(x,190.5,net,'1u / 50V')
s=sheets[5]
pp=s.sym('Device:C_Polarized',116.84,73.66,value='47u / 25V FR',foot='Capacitor_THT:CP_Radial_D5.0mm_P2.50mm')[0];s.net('-15V',pp['2']);s.gnd(pp['1'])
s.text('Added local 47u at U12 IN: ST requires >=22u aluminium electrolytic.\nU12 metal tab = -15V. Insulate from chassis / other regulator tabs.',78.74,111.76,1.016)
for ref in ['R75','R76','R83','R84','R85','R86','R87','R88','R89','R90']:
 for sheet in sheets:
  for ii,item in enumerate(sheet.items):
   if '(property "Reference" "'+ref+'"' in item:
    old=bom[ref]['Value'];tol=' / 0.1%' if ref in ['R75','R76'] else ' / 1%';sheet.items[ii]=item.replace('(property "Value" "'+old+'"','(property "Value" "'+old+tol+'"');bom[ref]['Value']=old+tol;bom[ref]['Note']='Shared reference; owned 0.1% 10k.' if ref in ['R75','R76'] else 'Rail-collapse monitor; standard E24 sense ratio, 1% maximum tolerance.'

from tps7a3901 import replace_regulators
replace_regulators(sheets[5],bom)
crossover_only='--crossover-only' in sys.argv
power_only='--power-only' in sys.argv
dry_run='--dry-run' in sys.argv
for s in sheets:
 if not dry_run and ((not crossover_only and not power_only) or (crossover_only and s.file=='02_crossover.kicad_sch') or (power_only and s.file=='06_power_mute.kicad_sch')):s.save()
# root sheet is a readable functional index, no extra circuitry.
rootitems=[]
for i,s in enumerate(sheets):
 x=25.4+(i%2)*129.54;y=38.1+(i//2)*35.56
 rootitems.append(f'(sheet (at {x} {y}) (size 114.3 22.86) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {s.uuid}) (property "Sheetname" {q(s.title)} (at {x} {y-2.54} 0) {effects(1.016,"left")}) (property "Sheetfile" {q(s.file)} (at {x} {y+25.4} 0) {effects(1.016,"left")}) (instances (project "SubController" (path "/{ROOT}" (page {q(s.page)})))))')
rootitems.append(f'(text "REF L/R or LFE -> relay signal/return selection -> buffered mono -> REF LP / AV bypass\\n-> analogue level -> phase -> HP / AV bypass -> polarity -> output mute -> separate P68" (at 20.32 208.28 0) {effects(1.016,"left top")} (uuid {uid("roottext")}))')
if not dry_run and not crossover_only and not power_only:(P/'SubController.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (generator_version "10.0") (uuid {ROOT}) (paper "A3") (title_block (title "SUBCONTROLLER - ANALOGUE SIGNAL PROCESSING") (date "2026-10-07") (rev "A - review") (comment 1 "No PCB layout. Separate P68 amplifier unchanged.")) (lib_symbols) '+''.join(rootitems)+f' (sheet_instances (path "/" (page "1"))) (embedded_fonts no))\n')
if not dry_run:(P/'libraries/SubController.kicad_sym').write_text('(kicad_symbol_lib (version 20250114) (generator "kicad_symbol_editor") '+''.join(dump(x) for x in custom.values())+')\n')
if not dry_run and not crossover_only and not power_only:
 (P/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "SubController") (type "KiCad") (uri "${KIPRJMOD}/libraries/SubController.kicad_sym") (options "") (descr "Verified project-specific analog parts")))\n')
 (P/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "SubController") (type "KiCad") (uri "${KIPRJMOD}/libraries/SubController.pretty") (options "") (descr "SOP op-amp and preferred film capacitor")))\n')
if not dry_run:(P/'design/component-manifest.json').write_text(json.dumps(list(bom.values()),indent=2)+'\n')
print(f'{"Dry run" if dry_run else "Updated power sheet only" if power_only else "Updated crossover sheet only" if crossover_only else "Updated all sheets"}; {len(bom)} components; PCB and .kicad_pro not touched.')
