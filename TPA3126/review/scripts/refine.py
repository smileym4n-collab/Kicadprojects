from schlib import *
# Restore power flags where passive elements interrupt ERC's driven-power inference.
n=load('Power.kicad_sch');orig=load('review/original/Power.kicad_sch')
n.append(copy.deepcopy(next(s for s in many(orig,'symbol') if val(s,'Reference')=='#FLG017')))
s=next(s for s in many(n,'symbol') if val(s,'Reference')=='D2');get(s,'lib_id')[1]='Device:D_Zener'
# Exact safety fuse part to be assigned after catalogue verification.
prop(next(s for s in many(n,'symbol') if val(s,'Reference')=='F2'),'MPN')[2]=''
save('Power.kicad_sch',n)
# DAC fixed I2C/VREF mode gives these multiplexed pins their actual input/passive function.
n=load('DAC.kicad_sch');l=next(s for s in many(get(n,'lib_symbols'),'symbol') if s[1]=='Audio:PCM5122PW')
l[1]='Custom:PCM5122_I2C_VREF'
for un in many(l,'symbol'):
 for p in many(un,'pin'):
  if get(p,'number')[1] in ['16','24']:p[1]=S('input')
  if get(p,'number')[1]=='10':p[1]=S('passive')
s=next(s for s in many(n,'symbol') if val(s,'Reference')=='U2');get(s,'lib_id')[1]='Custom:PCM5122_I2C_VREF'
# A flag is justified after R1: this is a supply supplied through a passive RC filter.
f=copy.deepcopy(next(s for s in many(orig,'symbol') if val(s,'Reference')=='#FLG017'))
prop(f,'Reference')[2]='#FLG020';get(f,'at')[1:]=[S('48.26'),S('49.53'),S('0')];get(f,'uuid')[1]=str(uuid.uuid4())
# Set new flag instance reference/path to the DAC instance.
for pr in many(get(f,'instances'),'project'):
 for pa in many(pr,'path'):
  pa[1]='/2d28c68d-56c4-4741-9a6a-addc853f62c3/943be2e2-92ad-4344-a732-c8333bc6627c';get(pa,'reference')[1]='#FLG020'
for p in many(f,'property'):
 get(p,'at')[1:]=[S('48.26'),S('49.53'),S('0')]
n.append(f)
t=next(s for s in many(n,'symbol') if val(s,'Reference')=='TP5');old=get(t,'at');dx=175.26-float(old[1]);dy=45.72-float(old[2]);old[1:3]=[S('175.26'),S('45.72')]
for p in many(t,'property'):
 at=get(p,'at');at[1]=S(str(float(at[1])+dx));at[2]=S(str(float(at[2])+dy))
for w in list(many(n,'wire')):
 if any(abs(float(p[1])-203.2)<.001 for p in get(w,'pts')[1:]):n.remove(w)
for j in list(many(n,'junction')):
 if abs(float(get(j,'at')[1])-203.2)<.001:n.remove(j)
save('DAC.kicad_sch',n)
# Remove a pre-existing dangling stub on BOOT switch pin 2.
n=load('ESP32.kicad_sch')
for w in list(many(n,'wire')):
 pts=[tuple(map(float,p[1:3])) for p in get(w,'pts')[1:]]
 if set(pts)=={(257.81,73.66),(259.08,73.66)}:n.remove(w)
save('ESP32.kicad_sch',n)
# Join the left positive bootstrap return to the actual switched output segment.
n=load('Amp.kicad_sch')
n.append(parse('(wire (pts (xy 203.2 96.52) (xy 203.2 106.68)) (stroke (width 0) (type default)) (uuid "'+str(uuid.uuid4())+'"))'))
n.append(parse('(junction (at 203.2 106.68) (diameter 0) (color 0 0 0 0) (uuid "'+str(uuid.uuid4())+'"))'))
# Ground mode pins using one bus, avoiding stacked ground glyphs.
for s in list(many(n,'symbol')):
 if val(s,'Value')=='GND' and abs(float(get(s,'at')[1])-99.06)<.001:n.remove(s)
for w in list(many(n,'wire')):
 pp=[tuple(map(float,p[1:3])) for p in get(w,'pts')[1:]]
 if any(abs(p[0]-99.06)<.001 for p in pp):
  for p in get(w,'pts')[1:]:
   if abs(float(p[1])-99.06)<.001:p[1]=S('93.98')
n.append(parse('(wire (pts (xy 93.98 101.6) (xy 93.98 127)) (stroke (width 0) (type default)) (uuid "'+str(uuid.uuid4())+'"))'))
g=copy.deepcopy(next(s for s in many(n,'symbol') if val(s,'Value')=='GND'));get(g,'uuid')[1]=str(uuid.uuid4());get(g,'at')[1:3]=[S('93.98'),S('127')]
for p in many(g,'property'):get(p,'at')[1:3]=[S('93.98'),S('130.81')]
n.append(g)
for yy in [101.6,114.3,116.84,119.38]:n.append(parse(f'(junction (at 93.98 {yy}) (diameter 0) (color 0 0 0 0) (uuid "{uuid.uuid4()}"))'))
save('Amp.kicad_sch',n)
# Power references must be globally unique across hierarchy; no functional changes.
i=500
for fn in ['TPA3126','ESP32','DAC','Amp','Power']:
 n=load(fn+'.kicad_sch')
 for s in many(n,'symbol'):
  if (val(s,'Reference') or '').startswith('#PWR'):
   i+=1;r='#PWR'+str(i);prop(s,'Reference')[2]=r
   for pr in many(get(s,'instances'),'project'):
    for pa in many(pr,'path'):get(pa,'reference')[1]=r
 save(fn+'.kicad_sch',n)
# Synchronize local symbols with the final embedded definitions.
symbols={}
for fn in ['ESP32','DAC','Amp','Power','TPA3126']:
 for s in many(get(load(fn+'.kicad_sch'),'lib_symbols'),'symbol'):
  if s[1].split(':')[0] in ['Custom','TPA3126']:
   q=copy.deepcopy(s);q[1]=q[1].split(':')[1];symbols[q[1]]=q
save('TPA3126.kicad_sym',[S('kicad_symbol_lib'),[S('version'),S('20241209')],[S('generator'),'kicad_symbol_editor'],*symbols.values()])
