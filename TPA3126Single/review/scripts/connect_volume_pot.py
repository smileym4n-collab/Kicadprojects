from schlib import *
import copy
p=Path('ESP32.kicad_sch');src=p.read_text();n=parse(src)
def uid():return str(uuid.uuid4())
def node(t):return parse(t)
def wire(x1,y1,x2,y2):return node(f'(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{uid()}"))')
def label(name,x,y,angle=0):return node(f'(label "{name}" (at {x} {y} {angle}) (effects (font (size 1.27 1.27)) (justify {"right" if angle==180 else "left"} bottom)) (uuid "{uid()}"))')
def gnd(x,y,ref):
 s=copy.deepcopy(next(s for s in many(n,'symbol') if val(s,'Reference')=='#PWR0504'))
 return move(s,x,y,0,ref,'GND')
def move(s,x,y,angle,ref,value):
 at=get(s,'at');ox,oy=float(at[1]),float(at[2]);at[1:]=list(map(S,map(str,[x,y,angle])))
 for pp in many(s,'property'):
  pa=get(pp,'at');pa[1]=S(str(round(float(pa[1])+x-ox,6)));pa[2]=S(str(round(float(pa[2])+y-oy,6)))
 prop(s,'Reference')[2]=ref;prop(s,'Value')[2]=value;get(s,'uuid')[1]=uid()
 for pp in many(s,'pin'):get(pp,'uuid')[1]=uid()
 ins=get(s,'instances');project=get(ins,'project');path=get(project,'path');get(path,'reference')[1]=ref
 return s
def setp(s,key,value):
 pp=prop(s,key)
 if pp:pp[2]=value
 else:s.append(node(f'(property {json.dumps(key)} {json.dumps(value)} (at {get(s,"at")[1]} {get(s,"at")[2]} 0) (effects (font (size 1 1)) (hide yes)))'))
# Only replace/remove individual top-level forms; preserve all unrelated formatting.
def spans(t):
 depth=0;q=False;esc=False;start=None
 for i,c in enumerate(t):
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':q=False
   continue
  if c=='"':q=True
  elif c=='(':
   if depth==1:start=i
   depth+=1
  elif c==')':
   depth-=1
   if depth==1 and start is not None:yield start,i+1;start=None
edits=[];added=[]
for a,b in spans(src):
 form=parse(src[a:b]);kind=form[0]
 if kind=='no_connect' and get(form,'at')[1:]==['128.27','52.07']:edits.append((a,b,''))
 elif kind=='wire' and get(form,'uuid')[1]=='96affdfe-ffda-490a-bde2-4b7e0434dc55':
  many(get(form,'pts'),'xy')[1][1]=S('58.42');edits.append((a,b,dump(form)))
 elif kind=='label' and form[1]=='VOL-ADC':
  get(form,'at')[1]=S('86.36');edits.append((a,b,dump(form)))
 elif kind=='text' and 'Preserved: LED Wi-Fi' in form[1]:
  form[1]=form[1].replace('GPIO36 ADC1 monitors PVDD/11.', 'GPIO36 ADC1 monitors PVDD/11. Volume pot: GPIO34 / ADC1_CH6 (module pin 6).').replace('J2: pins 2/3 go to ESP RX/TX (cross adapter TX/RX). Pin 6 is voltage reference only.\nDo not power the board through J2; adapter must use 3.3 V logic.', 'J2 system: 2=GND, 3=volume wiper, 4=3V3. Suggested pot: 10k linear.\nJ3 is the separate programming header; use 3.3 V UART logic.')
  edits.append((a,b,dump(form)))
assert len(edits)==4
rtemplate=next(s for s in many(n,'symbol') if val(s,'Reference')=='R31')
r=move(copy.deepcopy(rtemplate),62.23,87.63,90,'R39','10k');
# Use a native horizontal resistor template to preserve correct rotated field placement.
h=next(s for s in many(n,'symbol') if val(s,'Reference')=='R8');r=move(copy.deepcopy(h),62.23,87.63,90,'R39','10k')
setp(r,'MPN','RK73B2ATTD103J');setp(r,'Inventory_ID','194');setp(r,'Assembly_Note','2012 metric, 5%; volume ADC divider/filter series resistor.');setp(r,'Datasheet','https://www.koaspeer.com/pdfs/RK73B.pdf');added.append(r)
r=move(copy.deepcopy(rtemplate),73.66,99.06,0,'R40','22k');setp(r,'MPN','RR1220P-223-D');setp(r,'Inventory_ID','511');setp(r,'Assembly_Note','2012 metric, 0.5%; ADC scale and open-wiper pull-down. Owned stock.');setp(r,'Datasheet','https://www.susumu.co.jp/common/pdf/n_e_all.pdf');added.append(r)
c=move(copy.deepcopy(next(s for s in many(n,'symbol') if val(s,'Reference')=='C3')),86.36,99.06,0,'C58','100n / 50V');setp(c,'MPN','C1206C104K5RACTU');setp(c,'Inventory_ID','157');setp(c,'Assembly_Note','3216 metric X7R; place beside GPIO34, short GND return.');added.append(c)
added += [wire(66.04,87.63,73.66,87.63),wire(73.66,87.63,86.36,87.63),wire(73.66,87.63,73.66,95.25),wire(86.36,87.63,86.36,95.25),wire(73.66,102.87,73.66,106.68),wire(86.36,102.87,86.36,106.68),gnd(73.66,106.68,'#PWR0580'),gnd(86.36,106.68,'#PWR0581'),wire(128.27,52.07,120.65,52.07),label('VOL-ADC',120.65,52.07,180),node(f'(junction (at 73.66 87.63) (diameter 0) (color 0 0 0 0) (uuid "{uid()}"))')]
added.append(node(f'(text "VOLUME POT: J2 pins 2=GND, 3=wiper, 4=3V3. Use 10k linear.\\nR39/R40 scale full travel to ~2.27V; C58 filters ADC noise.\\nGPIO34 = ADC1_CH6. Firmware: highest ADC attenuation, average readings;\\ncalibrate endpoints / taper and map low or disconnected wiper to mute." (at 25.4 169.545 0) (effects (font (size 1.27 1.27)) (justify left top)) (uuid "{uid()}"))'))
for a,b,t in reversed(edits):src=src[:a]+t+src[b:]
pos=src.rfind(')');src=src[:pos]+'\n'+ '\n'.join(dump(t) for t in added)+'\n'+src[pos:];p.write_text(src)
print('Added GPIO34 volume ADC divider/filter; preserved J2 end connections.')
