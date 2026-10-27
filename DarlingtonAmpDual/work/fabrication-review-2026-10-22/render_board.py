from sexpr import *
from PIL import Image,ImageDraw,ImageFont
b=parse('DarlingtonAmpDual.kicad_pcb');data=json.loads((D/'board.json').read_text());scale=16
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
def pt(p):return ((float(p[0])-180)*scale,(float(p[1])-12)*scale)
def arcpts(st,mi,en):
 ax,ay=st;bx,by=mi;cx,cy=en;dd=2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by))
 ux=((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/dd
 uy=((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/dd
 aa,am,ae=[math.atan2(y-uy,x-ux) for x,y in [st,mi,en]];sweep=(ae-aa)%(2*math.pi)
 if (am-aa)%(2*math.pi)>sweep:sweep-=2*math.pi
 rad=math.hypot(ax-ux,ay-uy);n=max(2,int(abs(sweep)*rad/.04));return [(ux+rad*math.cos(aa+sweep*i/n),uy+rad*math.sin(aa+sweep*i/n)) for i in range(n+1)]
for layer in ['F.Cu','B.Cu']:
 im=Image.new('RGB',(1400,1690),'#fdfdfb');d=ImageDraw.Draw(im)
 for z in all(b,'zone'):
  if val(z,'layer')!=layer:continue
  for poly in all(z,'filled_polygon'):
   d.polygon([pt(v[1:]) for v in one(poly,'pts')[1:]],fill='#f0b4b4' if layer=='F.Cu' else '#b9d0ec')
 for s in data['segments']:
  if s['layer']!=layer:continue
  pts=arcpts(s['start'],s['mid'],s['end']) if s['kind']=='arc' else [s['start'],s['end']]
  d.line([pt(p) for p in pts],fill='#b74747' if layer=='F.Cu' else '#3268a5',width=round(s['width']*scale),joint='curve')
 for f in all(b,'footprint'):
  a=one(f,'at');x,y=map(float,a[1:3]);rot=float(a[3]) if len(a)>3 else 0;r=math.radians(rot)
  def trans(p):
   px,py=map(float,p);return pt([x+px*math.cos(r)+py*math.sin(r),y-px*math.sin(r)+py*math.cos(r)])
  for k in ['fp_line','fp_rect','fp_circle']:
   for g in all(f,k):
    if val(g,'layer')!='F.SilkS':continue
    if k=='fp_line':d.line([trans(one(g,'start')[1:]),trans(one(g,'end')[1:])],fill='#888888',width=1)
    elif k=='fp_rect':
     (x1,y1),(x2,y2)=[trans(one(g,j)[1:]) for j in ['start','end']];d.rectangle((min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2)),outline='#888888',width=1)
 for p in data['pads']:
  if p['type']=='smd' and layer not in p['layers']:continue
  x,y=pt(p['xy']);sx,sy=[float(v)*scale for v in p['size']];ang=p['angle']%180
  if abs(ang-90)<.01:sx,sy=sy,sx
  box=(x-sx/2,y-sy/2,x+sx/2,y+sy/2);color='#baa348' if p['type']!='np_thru_hole' else '#fafafa'
  if p['shape'] in ['circle','oval']:d.rounded_rectangle(box,radius=min(sx,sy)/2,fill=color)
  else:d.rectangle(box,fill=color)
  drill=p['drill']
  if drill:
   dia=float(drill[1])*scale;d.ellipse((x-dia/2,y-dia/2,x+dia/2,y+dia/2),fill='white',outline='#444444')
  if p['pin']:d.text((x+sx/2+1,y-8),p['pin'],fill='#444444',font=font)
 for f in data['footprints']:
  x,y=pt(f['xy']);d.text((x-15,y+14),f['ref'],fill='black',font=font,stroke_width=1,stroke_fill='white')
 d.rectangle([pt([183.134,15.875]),pt([264.287,114.808])],outline='black',width=3)
 d.text((60,12),layer+' - viewed from front; saved zone fill; reference labels added for review',fill='black',font=font)
 im.save(D/(layer+'.png'))
