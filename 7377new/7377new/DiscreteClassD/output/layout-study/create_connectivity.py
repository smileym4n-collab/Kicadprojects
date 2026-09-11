"""Review drawings from study pad coordinates, not routed copper."""
from pathlib import Path
import json, math, collections, hashlib, csv
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
import pypdfium2 as pdf

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
data=json.loads((OUT/'placement.json').read_text())
F={f['ref']:f for f in data['footprints']}
INK=HexColor('#182c40');MUTED=HexColor('#526373');BLUE=HexColor('#2272ac');ORANGE=HexColor('#be591d');GREEN=HexColor('#168273');PURPLE=HexColor('#8565ab')
def pad(ref,num):return next(p for p in F[ref]['pads'] if p['number']==str(num))['xy']
def dist(a,b):return math.dist(a,b)
def distance(r,p,s,q):return round(dist(pad(r,p),pad(s,q)),3)
metrics=[]
for off,side in [(0,'LEFT'),(100,'RIGHT')]:
 for j in range(2):
  q=5+2*j+off;u=[2,6][j]+off;c=1+6*j+off;r=1+6*j+off
  z=lambda k,n:k+str(n)
  row={'channel':side,'bridge':'AB'[j],
   'HO_to_R_mm':distance(z('U',u),4,z('R',r),1),'R_to_high_gate_mm':distance(z('R',r),2,z('Q',q),1),
   'LO_to_R_mm':distance(z('U',u),10,z('R',r+3),1),'R_to_low_gate_mm':distance(z('R',r+3),2,z('Q',q+1),1),
   'HB_to_boot_mm':distance(z('U',u),3,z('C',c),1),'HS_to_boot_mm':distance(z('U',u),5,z('C',c),2),
   'VDD_to_100n_mm':distance(z('U',u),1,z('C',c+1),1),'VSS_to_100n_mm':distance(z('U',u),9,z('C',c+1),2),
   'HS_Kelvin_to_high_source_mm':distance(z('U',u),5,z('Q',q),3),
   'VSS_Kelvin_to_low_source_mm':distance(z('U',u),9,z('Q',q+1),3),
   'high_source_to_low_drain_mm':distance(z('Q',q),3,z('Q',q+1),2),
   'high_source_to_inductor_mm':distance(z('Q',q),3,z('L',6+off),[1,4][j]),
   'low_drain_to_inductor_mm':distance(z('Q',q+1),2,z('L',6+off),[1,4][j])}
  for v,ci in [('100n',c+3),('1u',c+4),('10u',c+5)]:
   row['PVDD_'+v+'_to_high_drain_mm']=distance(z('C',ci),1,z('Q',q),2)
   row['PVDD_'+v+'_to_low_source_mm']=distance(z('C',ci),2,z('Q',q+1),3)
  metrics.append(row)
(OUT/'local-distances.json').write_text(json.dumps(metrics,indent=2)+'\n')
with (OUT/'placement-coordinates.csv').open('w') as h:
 w=csv.writer(h);w.writerow(['Reference','Value','Footprint','X_from_left_mm','Y_from_top_mm','Rotation_deg'])
 for f in sorted(F.values(),key=lambda f:f['ref']):w.writerow([f[k] for k in ['ref','value','footprint','x','y','angle']])

W,H=420*mm,297*mm
c=canvas.Canvas(str(OUT/'DiscreteClassD-connectivity-study.pdf'),pagesize=(W,H))
c.setTitle('DiscreteClassD - placement and selected connectivity study')
def header(title,subtitle,page):
 c.setFillColor(INK);c.setFont('Helvetica-Bold',19);c.drawString(15*mm,H-17*mm,title)
 c.setFont('Helvetica',9);c.setFillColor(MUTED);c.drawString(15*mm,H-24*mm,subtitle)
 c.setFont('Helvetica',8);c.drawString(15*mm,10*mm,'PLACEMENT STUDY ONLY  |  Straight connection lines are not routing  |  2026-09-09')
 c.drawRightString(W-15*mm,10*mm,str(page))
def prose(text,x,y,width=145,size=10,color=INK):
 c.setFont('Helvetica',size);c.setFillColor(color)
 for s in simpleSplit(text,'Helvetica',size,width*mm): c.drawString(x*mm,y*mm,s);y-=size*.46
 return y-3
def card(title,body,x,y,width=145):
 c.setFillColor(INK);c.setFont('Helvetica-Bold',11);c.drawString(x*mm,y*mm,title)
 return prose(body,x,y-6,width)
def transform(x0,y0,scale,top=265,left=15):
 return lambda xy:((left+(xy[0]-x0)*scale)*mm,(top-(xy[1]-y0)*scale)*mm)
def rect(T,x1,y1,x2,y2,fill,stroke=white):
 x,y=T([x1,y2]);xr,yt=T([x2,y1]);c.setFillColor(fill);c.setStrokeColor(stroke);c.setLineWidth(.4);c.rect(x,y,xr-x,yt-y,fill=1,stroke=1)
def footprints(T,refs,scale,fontsize=5):
 for ref in refs:
  f=F[ref]
  if ref=='G***':continue
  a,b=f['bbox'];rect(T,*a,*b,Color(1,1,1,alpha=.72),HexColor('#9da8b0'))
  for p in f['pads']:
   if p['number'] in ['10','11','12','13'] and ref in ['U11','U12']:continue
   x,y=T(p['xy']);c.setFillColor(MUTED);c.circle(x,y,.18*mm,fill=1,stroke=0)
 for ref in refs:
  f=F[ref]
  if ref=='G***':continue
  x,y=T(f['reference_xy']);c.setFillColor(INK);c.setFont('Helvetica',fontsize);c.drawCentredString(x,y-fontsize*.3,ref)
def connection(T,a,b,color=BLUE,width=.6,dash=None):
 c.setStrokeColor(color);c.setLineWidth(width);c.setDash(dash or [])
 c.line(*T(a),*T(b));c.setDash([])
 for xy in [a,b]:c.setFillColor(color);c.circle(*T(xy),.28*mm,stroke=0,fill=1)
def mst(points):
 points=list(dict.fromkeys(tuple(x) for x in points))
 if not points:return []
 done=[points.pop(0)];edges=[]
 while points:
  _,i,a=min((dist(a,b),i,a) for i,b in enumerate(points) for a in done)
  b=points.pop(i);edges.append((a,b));done.append(b)
 return edges
def netlines(T,names,refs=None):
 for name,col in names:
  pts=[p['xy'] for f in F.values() if refs is None or f['ref'] in refs for p in f['pads'] if p['net']==name]
  for a,b in mst(pts):connection(T,a,b,col,.65)

header('Stereo floorplan and signal distribution','Actual study coordinates; simplified footprint bounds and pad centres. Production PCB is unchanged.',1)
T=transform(0,0,2.32)
rect(T,0,0,100,100,HexColor('#f7f9fa'),INK)
rect(T,33,8,67,51,HexColor('#e8f2fa'))
rect(T,1,44,34,80,HexColor('#fff0e5'));rect(T,61,44,96,80,HexColor('#fff0e5'))
rect(T,35,54,65,88,HexColor('#fff6d9'))
footprints(T,F,2.32,5)
signals=[('/LEFT_IN',GREEN),('/RIGHT_IN',GREEN),('/AUDIO_L',BLUE),('/AUDIO_R',BLUE),('/TRIANGLE_400K',PURPLE),('/L_DRIVE_P',ORANGE),('/L_DRIVE_N',ORANGE),('/R_DRIVE_P',ORANGE),('/R_DRIVE_N',ORANGE)]
netlines(T,signals)
y=260
y=card('Mirrored floorplan, matching power cells','Left and right power blocks face the lower edge. Their 60 mm translation preserves the same MOSFET and driver orientation and the same local geometry.',255,y)
y=card('Quiet upper centre','J1 feeds C40/C45 and dual buffer U1. U8 contains both PWM comparators. U3 and U7 form the shared VREF / triangle section below them, well above the bridges.',255,y)
y=card('Control fans out','U4/U5 serve the left channel; U9/U10 serve the right. Orange lines show selected drive nets to the gate drivers. They are airwires, not proposed trace paths.',255,y)
y=card('Power enters at the lower centre','J16 sits below C17/C20. U11 and U12 sit above the bulk capacitors. R43/C50/C51 sit beside the analogue section. The centre is kept available for supply distribution.',255,y)
y=card('Colour key','Green: line input. Blue: buffered audio. Purple: triangle. Orange: drive signals. GND and power airwires are omitted for clarity.',255,y)
y=card('Fixed-outline compromise','The original 100 x 100 mm outline is preserved. Local PVDD / Kelvin paths need further placement refinement before this idea is copied into a routed board.',255,y)
c.showPage()

header('Power-stage connections: left channel','Right channel repeats the same cell geometry. Bounds are simplified; the native placement PDF shows exact footprint artwork.',2)
T=transform(0,43,4.8,top=264,left=15)
refs={r for r,f in F.items() if f['x']<35 and 43<=f['y']<=89}
rect(T,0,43,36,90,HexColor('#fafbfc'),INK)
footprints(T,refs,4.8,7)
for j in range(2):
 q=5+2*j;u=[2,6][j];r=1+6*j;cap=1+6*j
 pairs=[('U'+str(u),4,'R'+str(r),1),('R'+str(r),2,'Q'+str(q),1),('U'+str(u),10,'R'+str(r+3),1),('R'+str(r+3),2,'Q'+str(q+1),1),('U'+str(u),3,'C'+str(cap),1),('U'+str(u),5,'C'+str(cap),2)]
 for a,p,b,q2 in pairs:connection(T,pad(a,p),pad(b,q2),BLUE,1)
 for pin,qref,qpin in [(5,q,3),(9,q+1,3)]:connection(T,pad('U'+str(u),pin),pad('Q'+str(qref),qpin),PURPLE,.9,[2,2])
 for a,p,b,q2 in [('C'+str(cap+3),1,'Q'+str(q),2),('C'+str(cap+3),2,'Q'+str(q+1),3)]:connection(T,pad(a,p),pad(b,q2),GREEN,1)
netlines(T,[('/LEFT OUTPUT/SW_A',ORANGE),('/LEFT OUTPUT/SW_B',ORANGE),('/LEFT OUTPUT/OUT_A',HexColor('#21807a')),('/LEFT OUTPUT/OUT_B',HexColor('#21807a'))],refs-{'C13','C14','R13','R14','TP1','TP4'})
y=260
y=card('Connection key','Blue: gate and bootstrap connections. Purple dashed: separate HS / VSS source references. Green: 100 nF PVDD connections. Orange: switch nodes. Teal: filtered differential outputs.',210,y,190)
y=card('What is close','Series gate resistors are 1.84 mm from their MOSFET gate pads. Driver-to-resistor distances are 3.06 mm (HO) and 2.17 mm (LO). Bootstrap connections are 2.00 / 2.41 mm.',210,y,190)
y=card('What still needs refinement','HS and VSS source-reference distances are 6.54 / 6.57 mm. The 100 nF PVDD legs are 6.01 / 6.59 mm; 1 uF legs reach 9.84 mm. These are compromises, not a claim of a tight finished switching loop.',210,y,190)
y=card('Switch-node reach','Bridge A to inductor: 10.44 mm from the high-side source and 8.48 mm from the low-side drain. Bridge B: 7.70 / 4.94 mm. Equal stereo channels do not imply equal A/B geometry.',210,y,190)
y=card('Clean side of the filter','C15 sits immediately below L6, with its two legs on OUT_A and OUT_B. R15/C16, C18/C19, TP7/TP8 and J15 remain on the filtered side. Neither speaker pin is assigned to GND.',210,y,190)
y=card('Review the optional networks','D1-D4 and the alternate gate resistors occupy the upper reserve area. Their DNP paths are not optimised. Relocate them locally if populated. No switching or thermal measurements have been performed.',210,y,190)
y=prose('All numbers are straight pad-centre distances, not routed lengths or loop inductance. See local-distances.json for the complete measurements.',210,y,190,9,MUTED)
c.showPage();c.save()

doc=pdf.PdfDocument(str(OUT/'DiscreteClassD-connectivity-study.pdf'))
for i,page in enumerate(doc):page.render(scale=1.6).to_pil().save(str(OUT/f'connectivity-page-{i+1}.png'))
print(json.dumps(metrics,indent=2))
