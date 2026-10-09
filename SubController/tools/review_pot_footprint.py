"""Render/check actual PTD904 footprint data without creating a PCB layout."""
from pathlib import Path
import json,hashlib
from sexpr import parse,child,children
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab
P=Path(__file__).resolve().parents[1]
fp=P/'libraries/SubController.pretty/PTD904_2015K_B203_Horizontal.kicad_mod'
d=parse(fp.read_text());pads=children(d,'pad')
fontdir=Path(reportlab.__file__).parent/'fonts'
pdfmetrics.registerFont(TTFont('Vera',str(fontdir/'Vera.ttf')))
pdfmetrics.registerFont(TTFont('VeraBold',str(fontdir/'VeraBd.ttf')))
W,H=landscape(A4);c=Canvas(str(P/'design/PTD904-footprint-review.pdf'),pagesize=(W,H))
c.setFont('VeraBold',17);c.drawString(35,H-38,'PCB-mounted PTD904-2015K-B203: footprint review')
c.setFont('Vera',10);c.drawString(35,H-58,'Top/component view. Shaft points right (+X). Pattern read from the actual project-local .kicad_mod.')
scale=12;cx,cy=420,350
xy=lambda x,y:(cx+scale*x,cy-scale*y)
for ln in children(d,'fp_line'):
 layer=child(ln,'layer')[1]
 if layer not in ['F.Fab','F.CrtYd']:continue
 a,b=child(ln,'start'),child(ln,'end');c.setStrokeColor(HexColor('#98aab6') if layer=='F.CrtYd' else HexColor('#183446'));c.setLineWidth(.7);c.line(*xy(float(a[1]),float(a[2])),*xy(float(b[1]),float(b[2])))
facts=[]
for pad in pads:
 number=str(pad[1]);at=child(pad,'at');size=child(pad,'size');drill=float(child(pad,'drill')[1]);x,y=float(at[1]),float(at[2]);px,py=xy(x,y);sx,sy=float(size[1]),float(size[2])
 c.setFillColor(HexColor('#e1a341'));c.setStrokeColor(HexColor('#91591b'))
 if pad[3]=='rect':c.rect(px-sx*scale/2,py-sy*scale/2,sx*scale,sy*scale,fill=1)
 else:c.circle(px,py,sx*scale/2,fill=1)
 c.setFillColor(HexColor('#ffffff'));c.circle(px,py,drill*scale/2,fill=1)
 c.setFillColor(HexColor('#183446'));c.setFont('Vera',7);c.drawCentredString(px,py-2.5,number.rsplit('.',1)[1])
 facts.append({'pad':number,'x_mm':x,'y_mm':y,'drill_mm':drill,'copper_size_mm':[sx,sy]})
c.setStrokeColor(HexColor('#126ea7'));c.setDash(3,3);c.line(*xy(0,-6),*xy(0,6));c.setDash()
c.setFont('Vera',9);c.drawString(cx+5,cy+82,'Mounting surface: X=0')
for gang,x in [(4,-15),(3,-12.5),(2,-7.5),(1,-5)]:
 px,_=xy(x,0);c.drawCentredString(px,cy-72,f'R{gang}')
def dim(x1,x2,y,label):
 a,b=xy(x1,y),xy(x2,y);c.setStrokeColor(HexColor('#126ea7'));c.line(*a,*b)
 for x in [a[0],b[0]]:c.line(x,a[1]-3,x,a[1]+3)
 c.setFont('Vera',8);c.drawCentredString((a[0]+b[0])/2,a[1]+7,label)
dim(-15,-12.5,-8.5,'2.5');dim(-12.5,-7.5,-8.5,'5.0');dim(-7.5,-5,-8.5,'2.5');dim(-5,0,-8.5,'5.0 mm')
dim(0,15,6.8,'15 mm shaft projection')
c.setFont('Vera',10)
lines=[
 '12 plated holes: manufacturer nominal diameter 1.0 mm (+0.2/-0); chosen footprint drill 1.0 mm.',
 'Terminal rows: 1 at Y=+2.5 mm, wiper 2 at Y=0, terminal 3 at Y=-2.5 mm; total row span 5.0 mm.',
 'Section columns: R1/R2/R3/R4 at X=-5/-7.5/-12.5/-15 mm from the mounting surface.',
 'Pad IDs Rn.t preserve Bourns section Rn and terminal t. R1 is the gang nearest the shaft.',
 'Copper pads: 1.8 mm; annular ring 0.4 mm. Body 17.2 mm long, 9.5 mm wide; front lip 0.8 mm.',
 'M7 x 0.75 bushing, 6 mm knurled shaft, L=15 mm; K shaft bushing length B=5 mm.',
 'Courtyard includes the body and shaft. No extra mounting holes are shown in the manufacturer pattern.',
 'Source: Bourns PTD90 rev04/24, pages 2-4. Page 2 supplies a 1:1 template for physical sample checking.',
 'This is a footprint artifact only. No PCB placement, routing, enclosure fit or physical sample fit is claimed.'
]
for i,line in enumerate(lines):c.drawString(35,200-i*17,line)
c.showPage();c.setFont('VeraBold',17);c.drawString(35,H-38,'PTD904 actual-size template: print at 100%')
c.setFont('Vera',10);c.drawString(35,H-60,'Disable fit-to-page. Verify the 20 mm scale bar with a ruler before checking the actual part.')
scale=72/25.4;cx,cy=W/2,H/2
for ln in children(d,'fp_line'):
 if child(ln,'layer')[1]!='F.Fab':continue
 a,b=child(ln,'start'),child(ln,'end');c.setStrokeColor(HexColor('#183446'));c.setLineWidth(.4);c.line(*xy(float(a[1]),float(a[2])),*xy(float(b[1]),float(b[2])))
for pad in pads:
 at=child(pad,'at');size=child(pad,'size');px,py=xy(float(at[1]),float(at[2]));sx,sy=float(size[1]),float(size[2]);c.setFillColor(HexColor('#e1a341'));c.setStrokeColor(HexColor('#91591b'))
 if pad[3]=='rect':c.rect(px-sx*scale/2,py-sy*scale/2,sx*scale,sy*scale,fill=1)
 else:c.circle(px,py,sx*scale/2,fill=1)
 c.setFillColor(HexColor('#ffffff'));c.circle(px,py,float(child(pad,'drill')[1])*scale/2,fill=1)
c.setStrokeColor(HexColor('#183446'));c.line(60,H-110,60+20*scale,H-110)
for x in [60,60+20*scale]:c.line(x,H-114,x,H-106)
c.setFillColor(HexColor('#183446'));c.setFont('Vera',10);c.drawString(60,H-130,'20 mm')
c.drawCentredString(cx,cy-45,'Top/component view: R4 at left; R1 nearest shaft at right. Shaft points +X.')
c.drawString(35,70,'Compare all 12 lead centres and body outline. Paper fit check is still pending.')
c.save()
(P/'design/checks/PTD904-footprint.json').write_text(json.dumps({'source':'Bourns PTD90 rev04/24, p2 recommended PCB layout; p3 K shaft; p4 order code','footprint':str(fp.relative_to(P)),'sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'view':'Top/component, shaft +X','pads':facts,'physical_fit_checked':False},indent=2)+'\n')
print('Rendered actual pot footprint and recorded all pad positions/drills.')
