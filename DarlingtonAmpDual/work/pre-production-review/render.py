exec(open('work/pre-production-review/inspect.py').read().split('for f in fps:print')[0])
from PIL import Image,ImageDraw,ImageFont
scale=18
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
def pt(p):return ((float(p[0])-180)*scale,(float(p[1])-34)*scale)
for layer in ['F.Cu','B.Cu']:
 im=Image.new('RGB',(1560,1490),'white');d=ImageDraw.Draw(im)
 for z in all(b,'zone'):
  if val(z,'layer')!=layer:continue
  for poly in all(z,'filled_polygon'):
   pts=[pt(v[1:]) for v in one(poly,'pts')[1:]];d.polygon(pts,fill='#dba0a0' if layer=='F.Cu' else '#a5bade')
 for s in segs:
  if s['layer']==layer:d.line([pt(s['start']),pt(s['end'])],fill='#af3333' if layer=='F.Cu' else '#3366bb',width=round(s['width']*scale))
 for p in pads:
  x,y=pt(p['xy']);sx,sy=[float(v)*scale/2 for v in p['size']];d.ellipse((x-sx,y-sy,x+sx,y+sy),fill='#bca64a');d.text((x+3,y+3),p['pin'],fill='black',font=font)
 for f in fps:
  x,y=pt(f['xy']);d.text((x-12,y-23),f['ref'],fill='black',font=font)
 d.rectangle([pt([183.134,36.788]),pt([264.287,114.046])],outline='black',width=3)
 im.save(D/(layer+'.png'))
