from pathlib import Path
import csv,math,sys
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor,Color
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab
from analyse import L,H,AP,LP_K,LP_SERIES
fontdir=Path(reportlab.__file__).parent/'fonts'
pdfmetrics.registerFont(TTFont('Helvetica',str(fontdir/'Vera.ttf')))
pdfmetrics.registerFont(TTFont('Helvetica-Bold',str(fontdir/'VeraBd.ttf')))
P=Path(__file__).resolve().parents[1];W,HT=landscape(A4)
cs=[HexColor(x) for x in ['#126ea7','#ce521e','#258856','#7d49a8','#ba8215','#c32f62','#385176']]
c=Canvas(str(P/'design/response-plots.pdf'),pagesize=(W,HT))
def chart(title,subtitle,curves,ymin=-50,ymax=2,xmin=5,xmax=300,unit='dB'):
 c.setFillColor(HexColor('#183446'));c.setFont('Helvetica-Bold',18);c.drawString(48,HT-44,title);c.setFont('Helvetica',10);c.drawString(48,HT-65,subtitle)
 x0,y0,pw,ph=70,112,W-130,HT-217
 def xy(f,v):return x0+pw*math.log(f/xmin)/math.log(xmax/xmin),y0+ph*(v-ymin)/(ymax-ymin)
 c.setStrokeColor(HexColor('#dce3e7'));c.setLineWidth(.5)
 for f in [5,10,15,20,30,40,50,60,70,80,100,120,150,200,300]:
  if xmin<=f<=xmax:
   x,_=xy(f,ymin);c.line(x,y0,x,y0+ph);c.setFont('Helvetica',8);c.setFillColor(HexColor('#183446'));c.drawCentredString(x,y0-16,str(f))
 for v in range(math.ceil(ymin/10)*10,int(ymax)+1,10):
  _,y=xy(xmin,v);c.line(x0,y,x0+pw,y);c.drawRightString(x0-10,y-3,str(v))
 c.setStrokeColor(HexColor('#183446'));c.rect(x0,y0,pw,ph);c.setFont('Helvetica',10);c.drawCentredString(x0+pw/2,y0-34,'Frequency (Hz)');c.drawString(26,y0+ph/2,unit)
 for i,(name,fn) in enumerate(curves):
  c.setStrokeColor(cs[i%len(cs)]);c.setLineWidth(1.6);p=c.beginPath();started=False
  for k in range(600):
   f=xmin*(xmax/xmin)**(k/599);v=max(ymin,min(ymax,fn(f)));x,y=xy(f,v)
   if not started:p.moveTo(x,y);started=True
   else:p.lineTo(x,y)
  c.drawPath(p);yy=70-(i//4)*17;xx=70+(i%4)*185;c.line(xx,yy,xx+22,yy);c.setFillColor(HexColor('#183446'));c.setFont('Helvetica',9);c.drawString(xx+29,yy-3,name)
 c.setFont('Helvetica',8);c.drawString(48,20,'Ideal electrical responses; exclude driver, enclosure, GR10 response, room and propagation delay.');c.showPage()
db=lambda z:20*math.log10(abs(z))
R70=LP_K/70
chart('70 Hz calibration: slope and protection','LP pole 70.000 Hz with matched gangs; HP pole 20.100 Hz. Curves normalised to nominal passband gain.',[('LP 12 dB/oct',lambda f:db(L(f,R70,R70))),('LP 24 dB/oct',lambda f:db(L(f,R70,R70)**2)),('HP 20 Hz',lambda f:db(H(f,12700,25500))),('REF 12 + HP',lambda f:db(L(f,R70,R70)*H(f,12700,25500))),('REF 24 + HP',lambda f:db(L(f,R70,R70)**2*H(f,12700,25500)))])
chart('Continuous crossover: illustrative calibrations','Matched PTD904 gangs; nominal end stops 38.4-120.9 Hz. These curves are examples, not switch positions.',[(str(f)+' Hz',lambda x,r=LP_K/f:db(L(x,r,r)**2)) for f in [40,50,60,70,80,100,120]])
chart('Optional all-pass phase','Unity amplitude; phase varies with frequency. Bypass gives 0 degrees; polarity switch adds 180 degrees.',[(label,lambda f,r=r:-2*math.degrees(math.atan(2*math.pi*f*r*220e-9))) for label,r in [('Minimum R: 2.2k',2200),('Mid pot: 18.52k',2200+25000*47000/(25000+47000)),('Maximum R: 26.43k',2200+50000*47000/(50000+47000))]],-180,0,5,300,'deg')
c.save()
# Signal and grounding block diagram, explicitly including shared averaging/bypass paths.
c=Canvas(str(P/'design/block-diagram.pdf'),pagesize=(W,HT));c.setFillColor(HexColor('#183446'));c.setFont('Helvetica-Bold',18);c.drawString(35,HT-38,'SubController: analogue audio, digital control');c.setFont('Helvetica',10);c.drawString(35,HT-58,'All audio remains continuous analogue. Main speakers remain full range. P68 amplifier is separate.')
def box(x,y,w,h,lines):
 c.setStrokeColor(HexColor('#126ea7'));c.setFillColor(HexColor('#eef5f8'));c.roundRect(x,y,w,h,5,fill=1);c.setFillColor(HexColor('#183446'));c.setFont('Helvetica',10)
 for i,line in enumerate(lines):c.drawCentredString(x+w/2,y+h/2+7*(len(lines)-1)-14*i,line)
def arrow(a,b):
 c.setStrokeColor(HexColor('#183446'));c.setLineWidth(1);c.line(*a,*b);ang=math.atan2(b[1]-a[1],b[0]-a[0]);c.line(*b,b[0]-6*math.cos(ang-.5),b[1]-6*math.sin(ang-.5));c.line(*b,b[0]-6*math.cos(ang+.5),b[1]-6*math.sin(ang+.5))
box(35,405,115,55,['REF L / R','Insulated RCA']);box(35,330,115,55,['Marantz LFE','Insulated RCA']);box(200,355,155,80,['K1 signal selection','K2 return selection','Inactive source open']);arrow((150,432),(200,411));arrow((150,357),(200,381))
box(405,355,155,80,['U1 buffers','U2 averaging sum','LFE feeds both inputs']);arrow((355,395),(405,395));box(605,355,190,80,['REF: continuous LP 12 / 24','PCB pot: nominal 38-121 Hz','AV: low-pass bypass']);arrow((560,395),(605,395))
box(605,220,190,80,['U4A gain -0.5','CS3310 analogue level','U6B buffer']);arrow((700,355),(700,300));box(390,220,160,80,['U4B all-pass / bypass','Phase varies with frequency','Unity amplitude']);arrow((605,260),(550,260));box(190,220,155,80,['U5A HP 15 / 20 / 25','REF default 20 Hz','AV default bypass']);arrow((390,260),(345,260));box(35,220,110,80,['0 / 180 polarity','U5B inverter','Selectable sign']);arrow((190,260),(145,260))
# Actual polarity follows HP; description groups phase/polarity here, amend two labels to avoid misleading order.
c.setFont('Helvetica',8);c.setFillColor(HexColor('#183446'));c.drawString(190,202,'Electrical order after level: all-pass -> HP -> polarity -> output. See detailed schematic.')
box(35,108,140,70,['U6A gain -2','100R + K4 output mute','Low-impedance output']);arrow((90,220),(90,178));box(220,108,140,70,['Separate P68','Nominal input 22k','Amplifier unchanged']);arrow((175,143),(220,143));box(405,96,390,82,['ATtiny412 + MCP23008: encoders / isolated trigger','Relays, attenuation, startup / rail-fault mute','Separate control +5R; CS VDD tied to +5A','External regulated +/-15 V; PA0 for UPDI']);c.setFont('Helvetica',10);c.drawString(35,54,'GND: one board net. Selected RCA return connects to it; inactive source has no board-ground path.');c.drawString(35,36,'Protective earth bonds directly to chassis outside this SELV PCB. RCA shells must remain insulated.');c.save()
print('Created block-diagram.pdf and response-plots.pdf')
