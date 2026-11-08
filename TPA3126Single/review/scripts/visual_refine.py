from schlib import *
def N(x):return S(str(round(x,6)))
def properties(s):
 a=get(s,'at');x,y,ang=map(float,a[1:]);ref=val(s,'Reference') or ''
 if ref.startswith('#'):return
 # KiCad text uses the instance orientation to keep horizontal parts readable.
 for p in many(s,'property'):
  if p[1] not in ['Reference','Value']:continue
  pp=get(p,'at');pp[3]=N(ang)
  if ang in [90,270]:pp[1:3]=[N(x),N(y+(-2.54 if p[1]=='Reference' else 2.54))]
  else:pp[1:3]=[N(x+3.81),N(y+(-1.27 if p[1]=='Reference' else 1.27))]
  ef=get(p,'effects');j=get(ef,'justify')
  if j:ef.remove(j)
  if ang not in [90,270]:ef.append([S('justify'),S('left')])
  ft=get(ef,'font');get(ft,'size')[1:]=[S('1'),S('1')]
def shift(s,dx,dy):
 aa=get(s,'at');aa[1]=N(float(aa[1])+dx);aa[2]=N(float(aa[2])+dy)
 for p in many(s,'property'):
  aa=get(p,'at');aa[1]=N(float(aa[1])+dx);aa[2]=N(float(aa[2])+dy)
def wire(n,p,q):n.append(parse(f'(wire (pts (xy {p[0]} {p[1]}) (xy {q[0]} {q[1]})) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))'))
def label(n,name,x,y,ang=0):n.append(parse(f'(label "{name}" (at {x} {y} {ang}) (effects (font (size 1 1)) (justify left bottom)) (uuid "{uuid.uuid4()}"))'))
def find(n,r):return next(s for s in many(n,'symbol') if val(s,'Reference')==r)
def sync_libs():
 syms={}
 for fn in ['ESP32','DAC','Amp','Power','TPA3126']:
  for l in many(get(load(fn+'.kicad_sch'),'lib_symbols'),'symbol'):
   if l[1].split(':')[0] in ['Custom','TPA3126']:
    q=copy.deepcopy(l);q[1]=q[1].split(':')[1];syms[q[1]]=q
 save('TPA3126.kicad_sym',[S('kicad_symbol_lib'),[S('version'),S('20260306')],[S('generator'),'kicad_symbol_editor'],*syms.values()])
# Top level A3 gives control wiring and sequence notes clear of the title box.
n=load('TPA3126.kicad_sch');get(n,'paper')[1]='A3'
for item in n:
 if not isinstance(item,list) or item[0]=='lib_symbols':continue
 def trans(q):
  if not isinstance(q,list):return
  if q and q[0] in ['at','xy'] and len(q)>=3:q[1]=N(float(q[1])+12.7)
  for z in q:
   if isinstance(z,list):trans(z)
 trans(item)
get(get(n,'title_block'),'title')[1]='Bluetooth / Snapcast active speaker'
save('TPA3126.kicad_sch',n)
# ESP32 support blocks: move local decoupling away from signal labels.
n=load('ESP32.kicad_sch')
for ref,x,y in [('C3',233.68,120.65),('C55',213.36,120.65)]:
 s=find(n,ref);old=tuple(map(float,get(s,'at')[1:3]));dx=x-old[0];dy=y-old[1]
 if ref=='C3':
  # Keep the horizontal module supply wire; discard only this capacitor's old ground stub.
  for w in list(many(n,'wire')):
   pp=[tuple(map(float,p[1:3])) for p in get(w,'pts')[1:]]
   if any(abs(p[0]-old[0])<.001 and p[1]>41.91 for p in pp):n.remove(w)
  for ss in list(many(n,'symbol')):
   if val(ss,'Value')=='GND' and abs(float(get(ss,'at')[1])-old[0])<.001:n.remove(ss)
 else:
  for w in list(many(n,'wire')):
   if any(abs(float(p[1])-old[0])<.001 for p in get(w,'pts')[1:]):n.remove(w)
  for la in list(many(n,'label')):
   if abs(float(get(la,'at')[1])-old[0])<.001:n.remove(la)
  for ss in list(many(n,'symbol')):
   if val(ss,'Value')=='GND' and abs(float(get(ss,'at')[1])-old[0])<.001:n.remove(ss)
 shift(s,dx,dy);properties(s);wire(n,(x,116.84),(x,111.76));label(n,'3V3-ESP',x,111.76)
 wire(n,(x,124.46),(x,129.54))
 g=copy.deepcopy(find(n,'#PWR505'));get(g,'uuid')[1]=str(uuid.uuid4());get(g,'at')[1:]=[N(x),N(129.54),S('0')]
 for p in many(g,'property'):
  if p[1]=='Value':get(p,'at')[1:]=[N(x),N(133.35),S('0')]
 n.append(g)
# Widen the EN/BOOT resistor spacing, preserving their branch topology.
for oldx,newx in [(52.07,30.48),(63.5,55.88)]:
 for w in many(n,'wire'):
  for pp in get(w,'pts')[1:]:
   if abs(float(pp[1])-oldx)<.001 and float(pp[2])<51:pp[1]=N(newx)
 for la in many(n,'label'):
  aa=get(la,'at')
  if abs(float(aa[1])-oldx)<.001 and float(aa[2])<51:aa[1]=N(newx);aa[3]=S('0');ef=get(la,'effects');jj=get(ef,'justify');jj[1:]=[S('left'),S('bottom')]
 for s in many(n,'symbol'):
  aa=get(s,'at')
  if abs(float(aa[1])-oldx)<.001 and float(aa[2])<51:shift(s,newx-oldx,0);properties(s)
# I2C/LED block labels use horizontal text.
for la in many(n,'label'):
 aa=get(la,'at')
 if float(aa[2])>=100 and la[1] in ['3V3-ESP','SCL','SDA','BT_LED','WIFI_LED']:
  aa[3]=S('0');get(get(la,'effects'),'justify')[1:]=[S('left'),S('bottom')]
# Move SDA pullup for readable supply labels.
s=find(n,'R33');shift(s,7.62,0)
for w in many(n,'wire'):
 for p in get(w,'pts')[1:]:
  if abs(float(p[1])-114.3)<.001 and float(p[2])>=109:p[1]=N(121.92)
for la in many(n,'label'):
 aa=get(la,'at')
 if abs(float(aa[1])-114.3)<.001 and float(aa[2])>=109:aa[1]=N(121.92)
# UART pin 1 ground points upward above the header, away from RX/TX labels.
for s in many(n,'symbol'):
 if val(s,'Value')=='GND' and abs(float(get(s,'at')[1])-35.56)<.001:
  get(s,'at')[2:]=[N(99.06),S('180')];get(prop(s,'Value'),'at')[1:]=[N(35.56),N(95.25),S('0')];wire(n,(35.56,99.06),(35.56,106.68))
for ref,value in [('D3','WIFI GREEN'),('D4','BT RED')]:prop(find(n,ref),'Value')[2]=value
for s in many(n,'symbol'):
 if val(s,'Reference') in ['R31','R33','D3','D4','C3','C55']:properties(s)
get(get(n,'title_block'),'title')[1]='ESP32-WROVER-IE - retained firmware GPIOs'
save('ESP32.kicad_sch',n)
# Amplifier component field orientation, label size and capacitor spacing.
n=load('Amp.kicad_sch')
for s in many(n,'symbol'):
 ref=val(s,'Reference') or ''
 if ref not in ['U1','L2','L3'] and not ref.startswith('#'):properties(s)
 if ref in ['C1','C2','C5','C6']:prop(s,'Value')[2]='1u FILM / 63V'
 if ref in ['C41','C42','C43','C44']:prop(s,'Value')[2]='330p DNP'
 if ref in ['R35','R36','R37','R38']:prop(s,'Value')[2]='18R DNP'
 if ref in ['TP9','TP10','TP11','TP12']:prop(s,'Value')[2]={'TP9':'W+','TP10':'W-','TP11':'T+','TP12':'T-'}[ref]
 if ref in ['TP6','TP7','TP8','TP9','TP10','TP11','TP12']:
  x,y=map(float,get(s,'at')[1:3]);get(prop(s,'Reference'),'at')[1:]=[N(x+2.54),N(y-3.81),S('0')];get(prop(s,'Value'),'at')[1:]=[N(x+2.54),N(y-1.27),S('0')]
# Change only the C39 branch and its upward ground to x=266.7.
c=find(n,'C39');shift(c,15.24,0)
for w in many(n,'wire'):
 pp=[tuple(map(float,p[1:3])) for p in get(w,'pts')[1:]]
 if all(abs(p[0]-251.46)<.001 for p in pp) and min(p[1] for p in pp)>=90 and max(p[1] for p in pp)<=106.68:
  for p in get(w,'pts')[1:]:p[1]=N(266.7)
for s in many(n,'symbol'):
 if val(s,'Value')=='GND':
  aa=get(s,'at')
  if abs(float(aa[1])-251.46)<.001 and abs(float(aa[2])-90.17)<.001 and aa[3]=='180':shift(s,15.24,0)
wire(n,(261.62,106.68),(266.7,106.68))
# Horizontal names on external capacitor wires.
for la in many(n,'label'):
 aa=get(la,'at')
 if abs(float(aa[1])-355.6)<.001:aa[3]=S('0');get(get(la,'effects'),'justify')[1:]=[S('left'),S('bottom')]
# Move far-left input/control ports inside the drawing boundary.
for la in many(n,'hierarchical_label'):
 if la[1] in ['AMP_ENABLE','AMP_MUTE_CMD','WOOFER_AUDIO']:
  aa=get(la,'at');ox=float(aa[1]);oy=float(aa[2]);aa[1]=N(30.48)
  for w in many(n,'wire'):
   for p in get(w,'pts')[1:]:
    if abs(float(p[1])-ox)<.001 and abs(float(p[2])-oy)<.001:p[1]=N(30.48)
for la in many(n,'label')+many(n,'hierarchical_label'):
 get(get(la,'effects'),'font')[1]=[S('size'),S('1'),S('1')]
get(get(n,'title_block'),'title')[1]='TPA3126D2 - stereo BTL, bypassable CH2 capacitor'
# Move startup notes to a wider area above the snubber bank so PLIMIT has its own clear block.
for t in many(n,'text'):
 if t[1].startswith('SDZ default'):
  get(t,'at')[1:3]=[N(121.92),N(137.16)]
 if t[1].startswith('PLIMIT IS'):get(t,'at')[1:3]=[N(119.38),N(200.66)]
# Start PLIMIT source resistor below the startup circuit, away from note text.
# The new position already has clear space once the note block is moved.
save('Amp.kicad_sch',n)
# Shorter titles and correct fuse catalogue rating, footprint series share the TE5 case.
n=load('Power.kicad_sch');s=find(n,'F2');prop(s,'Value')[2]='T3.15A / 125V';prop(s,'MPN')[2]='39613150000'
prop(s,'Datasheet')[2]='https://www.littelfuse.com/assetdocs/littelfuse-fuse-396-datasheet?assetguid=28004c2f-992c-4d86-8a35-f495c62803a6'
# Zener and TVS fields must be horizontal and separate from their bodies.
for ref in ['D1','D2']:
 s=find(n,ref);x,y=map(float,get(s,'at')[1:3])
 for key,yy in [('Reference',y-1.27),('Value',y+1.27)]:get(prop(s,key),'at')[1:]=[N(x+3.81),N(yy),S('90')]
get(get(n,'title_block'),'title')[1]='Power - protected input, 4.05 V, 3.3 V'
save('Power.kicad_sch',n)
# Reassign unique power references after copied ground symbols.
i=500
for fn in ['TPA3126','ESP32','DAC','Amp','Power']:
 n=load(fn+'.kicad_sch')
 for s in many(n,'symbol'):
  if (val(s,'Reference') or '').startswith('#PWR'):
   i+=1;r='#PWR'+str(i);prop(s,'Reference')[2]=r
   for pr in many(get(s,'instances'),'project'):
    for pa in many(pr,'path'):get(pa,'reference')[1]=r
 save(fn+'.kicad_sch',n)
sync_libs()
