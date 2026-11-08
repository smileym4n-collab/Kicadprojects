from schlib import *
def N(v):return S(str(round(v,6)))
def find(n,r):return next(s for s in many(n,'symbol') if val(s,'Reference')==r)
def wire(n,p,q):n.append(parse(f'(wire (pts (xy {p[0]} {p[1]}) (xy {q[0]} {q[1]})) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))'))
def shift(s,dx,dy):
 aa=get(s,'at');aa[1]=N(float(aa[1])+dx);aa[2]=N(float(aa[2])+dy)
 for p in many(s,'property'):
  aa=get(p,'at');aa[1]=N(float(aa[1])+dx);aa[2]=N(float(aa[2])+dy)
n=load('DAC.kicad_sch')
for s in many(n,'symbol'):
 ref=val(s,'Reference') or ''
 if ref.startswith('C'):
  value=val(s,'Value')
  if ref in ['C16','C19']:prop(s,'Value')[2]='2n7 C0G'
  if ref in ['C12','C14']:prop(s,'Value')[2]='2u2 / 10V'
  x,y=map(float,get(s,'at')[1:3])
  for key,yy in [('Reference',y-1.27),('Value',y+1.27)]:
   p=prop(s,key);get(p,'at')[1:]=[N(x+3.81),N(yy),S('0')]
   ef=get(p,'effects');get(get(ef,'font'),'size')[1:]=[S('1'),S('1')]
   jj=get(ef,'justify')
   if jj:jj[1:]=[S('left')]
   else:ef.append([S('justify'),S('left')])
f=find(n,'#FLG020');shift(f,20.32,0)
for p in many(f,'property'):
 if p[1] in ['Value','Reference']:
  ef=get(p,'effects');h=get(ef,'hide')
  if not h:ef.append([S('hide'),S('yes')])
n.append(parse(f'(junction (at 68.58 49.53) (diameter 0) (color 0 0 0 0) (uuid "{uuid.uuid4()}"))'))
save('DAC.kicad_sch',n)
n=load('ESP32.kicad_sch')
for ref in ['D3','D4']:
 s=find(n,ref);x,y=map(float,get(s,'at')[1:3]);prop(s,'Value')[2]='GREEN' if ref=='D3' else 'RED'
 for key,yy in [('Reference',y-1.27),('Value',y+1.27)]:
  p=prop(s,key);get(p,'at')[1:]=[N(x+3.81),N(yy),S('90')];get(p,'effects').append([S('justify'),S('left')])
save('ESP32.kicad_sch',n)
n=load('Amp.kicad_sch')
for la in many(n,'label'):
 aa=get(la,'at')
 if la[1]=='TW_FILTER_P' and abs(float(aa[1])-261.62)<.001:get(get(la,'effects'),'justify')[1:]=[S('right'),S('bottom')]
 if la[1]=='TW_PROTECTED_P' and abs(float(aa[1])-274.32)<.001:
  aa[1:]=[N(279.4),N(100.33),S('0')];get(get(la,'effects'),'justify')[1:]=[S('left'),S('bottom')]
for w in many(n,'wire'):
 pp=[tuple(map(float,p[1:3])) for p in get(w,'pts')[1:]]
 if (274.32,106.68) in pp:
  for p in get(w,'pts')[1:]:
   if abs(float(p[1])-274.32)<.001:p[1]=N(279.4)
wire(n,(279.4,106.68),(279.4,100.33))
# Separate input reference ground glyph from PLIMIT ground glyph.
shift(find(n,'R13'),6.35,0)
for w in many(n,'wire'):
 pp=[tuple(map(float,p[1:3])) for p in get(w,'pts')[1:]]
 if all(abs(p[0]-63.5)<.001 for p in pp) and min(p[1] for p in pp)>=234.95:
  for p in get(w,'pts')[1:]:p[1]=N(69.85)
for s in many(n,'symbol'):
 if val(s,'Value')=='GND':
  aa=get(s,'at')
  if abs(float(aa[1])-63.5)<.001 and abs(float(aa[2])-234.95)<.001:shift(s,6.35,0)
for j in many(n,'junction'):
 aa=get(j,'at')
 if abs(float(aa[1])-63.5)<.001 and abs(float(aa[2])-251.46)<.001:aa[1]=N(69.85)
save('Amp.kicad_sch',n)
