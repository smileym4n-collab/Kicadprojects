from pathlib import Path
import hashlib,xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
ROOT=Path.cwd(); target=ROOT/'output/pdf/DarlingtonAmp-bias-setting-guide.pdf'
sch=ROOT/'DarlingtonAmp.kicad_sch'; digest=hashlib.sha256(sch.read_bytes()).hexdigest()
r=ET.parse(ROOT/'work/bias-guide-current.xml')
def pins(ref,pin):
 return next(n.get('name') for n in r.findall('.//nets/net') if any(v.get('ref')==ref and v.get('pin')==str(pin) for v in n.findall('node')))
assert pins('R1',2)=='/AMP_OUT'
assert pins('R1',3)==pins('Q11',3)
assert pins('R1',1)==pins('Q12',3)
assert pins('RV1',2)==pins('RV1',3)==pins('Q9',1)
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleX',fontName='Helvetica-Bold',fontSize=24,leading=28,textColor=colors.HexColor('#15344b'),spaceAfter=10))
styles.add(ParagraphStyle(name='SubX',fontName='Helvetica',fontSize=11,leading=16,textColor=colors.HexColor('#496270'),spaceAfter=13))
styles.add(ParagraphStyle(name='HeadX',fontName='Helvetica-Bold',fontSize=13,leading=17,textColor=colors.HexColor('#15344b'),spaceBefore=10,spaceAfter=6))
styles.add(ParagraphStyle(name='BodyX',fontName='Helvetica',fontSize=9.6,leading=13.2,spaceAfter=6))
styles.add(ParagraphStyle(name='SmallX',fontName='Helvetica',fontSize=8.5,leading=11,spaceAfter=6))
styles.add(ParagraphStyle(name='CellX',fontName='Helvetica',fontSize=9.4,leading=13))
story=[]
def P(text,style='BodyX'):return Paragraph(text,styles[style])
def add(text,style='BodyX'):story.append(P(text,style))
def head(text):add(text,'HeadX')
def table(rows,widths):
 t=Table([[P(str(c),'CellX') for c in row] for row in rows],colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5eef2')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#bdcdd5')),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.append(t);story.append(Spacer(1,8))
def step(n,title,body):story.append(KeepTogether([P(f'{n}. {title}','HeadX'),P(body)]))
def footer(c,doc):
 c.setStrokeColor(colors.HexColor('#bdcdd5'));c.line(18*mm,17*mm,192*mm,17*mm)
 c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#496270'));c.drawString(18*mm,12*mm,'DarlingtonAmp | Single output pair | 7 October 2026');c.drawRightString(192*mm,12*mm,f'{doc.page}')
add('Setting the bias current','TitleX')
add('DarlingtonAmp mono Class-AB amplifier\n<br/>One 2SD2390 / 2SB1560 pair, dual 0R22 emitter resistor, +/-35 V rails','SubX')
add('<b>Set current by measuring millivolts across each emitter resistor.</b> Do not adjust using speaker-output voltage, supply current or the voltage between the output bases.','BodyX')
head('The target')
add('The schematic starting target is <b>80-100 mA of idle emitter current per output transistor</b>. This is a provisional bench setting, not a measured distortion optimum. Begin at minimum bias, establish healthy operation, then approach the lower end of the range.')
table([['Idle current','Across one 0.22 ohm section','Across both sections*'],['20 mA (early check)','4.4 mV','8.8 mV'],['50 mA (intermediate)','11.0 mV','22.0 mV'],['80 mA (initial warm target)','17.6 mV','35.2 mV'],['100 mA (upper target)','22.0 mV','44.0 mV']], [57*mm,57*mm,60*mm])
add('*The outer-to-outer reading is the sum. It does not reveal unequal currents, so measure both sections separately. Values assume each section really is 0.22 ohm. I = V / R; for example, 17.6 mV / 0.22 ohm = 80 mA.','SmallX')
head('Where to put the meter probes')
table([['Reading','Red (+) probe','Black (-) probe'],['NPN Q11 current','R1 pin 3: Q11 emitter','R1 pin 2: AMP_OUT'],['PNP Q12 current','R1 pin 2: AMP_OUT','R1 pin 1: Q12 emitter'],['Combined cross-check','R1 pin 3','R1 pin 1']], [55*mm,60*mm,59*mm])
add('<b>R1 pin 2 is the centre/common terminal.</b> Pin 1 and pin 3 are the outer terminals. Use pad numbers and continuity to identify them; do not infer left/right from a board photograph. The currently saved schematic has no dedicated bias test points.')
head('Bench setup')
add('Use a DMM with a DC millivolt range, insulated clip leads, an insulated trimming tool and a current-limited split supply. A second DMM for output DC is helpful; an oscilloscope is strongly recommended for detecting oscillation. Leave the speaker, dummy load and signal source disconnected. Connect the amplifier input to its input ground so it has zero signal.')
add('<b>Fit the heatsink before powering up.</b> Q11, Q12 and the Q9 bias sensor must have proper thermal contact and electrical insulation. The heatsink must not short their collector surfaces together. This guide does not clear the outstanding PCB/mechanical review items or qualify the amplifier for 4 ohm operation.','SmallX')
story.append(PageBreak())
add('Adjustment procedure','TitleX')
add('Make all clip-lead changes with both rails switched off and the capacitors discharged.','SubX')
step(1,'Confirm the build and minimum-bias preset','Check transistor pin mapping, R1 value/common pin, rail polarity, capacitor polarity and Q9 heatsink contact. RV1 is 5k; pins 2 and 3 are tied together. <b>Maximum resistance from pin 1 to pins 2/3 gives minimum bias.</b> For the specified Bourns 3296W, turn clockwise to maximum resistance / minimum bias; counter-clockwise raises bias. Verify on the actual part, especially for a generic replacement. Do not force the end-of-travel clutch. Check resistance before fitting; parallel paths can mislead an in-circuit measurement.')
step(2,'Attach the meters before power','Set the bias meter to DC millivolts, not amps. Clip it across one R1 section using page 1. If available, connect another meter from AMP_OUT to GND to monitor output DC. Never use the current range across a resistor or output node; it would create a short.')
step(3,'First power-up at minimum bias','With both rails off, set each current limit initially to about <b>150 mA</b> for this single-pair board. Raise both rails together in stages towards +/-35 V, watching bias voltage, output DC and rail current. Do not adjust final bias at reduced rails or while either supply is current limiting. If a rail fails to track, shut down both and investigate.')
step(4,'Check that the amplifier is behaving normally','Confirm correct, balanced rails and low output DC. Use <b>|output DC| &gt;100 mV</b> as a conservative investigation threshold for this procedure, not an established design specification. Check for sustained high-frequency oscillation with the scope. A DMM alone cannot establish stability. Unexpected current, rapid heating or instability means switch off and diagnose before adding bias.')
step(5,'Raise bias slowly','At full, steady rails, turn RV1 a small fraction counter-clockwise and confirm that the millivolt reading rises. Pause after each adjustment. Approach <b>4.4 mV</b> (20 mA), then <b>11 mV</b> (50 mA). Power off before moving clips to check the other section. Stop if adjustment direction is unexpected.')
step(6,'Approach the target and warm up','Once both currents and output DC are sensible, approach <b>17.6 mV per section</b> (80 mA). If healthy operation reaches the 150 mA limit, allow 200-250 mA per rail for no-signal commissioning; keep monitoring. Allow at least <b>20-30 minutes</b>, and longer if readings still drift. Recheck both sections and make small corrections. Stay within 17.6-22 mV; prefer the lower end until distortion and thermal behaviour are measured.')
step(7,'Confirm stability and repeat from cold','If current keeps rising, reduce bias. If it does not settle, switch off and investigate Q9 thermal tracking. After a stable warm setting, let the assembly cool fully, then repeat startup and warm-up with RV1 untouched. Recheck offset and stability before signal/load tests. Connect a speaker only after DC and startup checks; no speaker protection is provided.')
story.append(PageBreak())
add('Checks, limits and bench record','TitleX')
head('What the readings mean')
add('At zero signal and low output offset, the two emitter currents should be close, allowing for resistor tolerance, meter resolution and small circuit currents. <b>One high and one low reading is not corrected by turning the common bias trimmer.</b> Verify R1 sections, probe connections, output DC and device wiring first. A combined 40 mV reading could conceal unequal section readings.')
add('Stop adjusting and switch off if the current rises uncontrollably, a section moves rapidly above 22 mV, output DC becomes excessive, a rail collapses, oscillation appears or a device heats rapidly. These are conservative commissioning checks; the supply current limit is not a substitute for stable bias tracking or transistor protection.')
head('Expected heat and supply current')
add('At +/-35 V and 80-100 mA, the output pair dissipates approximately <b>5.6-7 W total at idle</b>, roughly 2.8-3.5 W per output transistor. Each 0R22 section dissipates only about 1.4-2.2 mW at idle. Output devices will warm even with no audio. Supply meters also include VAS/front-end currents, so they are a cross-check rather than the bias-setting measurement.')
head('If the resistor value or output configuration changes')
add('For 0.33 ohm emitter resistors, 80-100 mA corresponds to <b>26.4-33 mV per resistor</b>. Do not use that range for the installed 0R22 dual part. With a second output pair, each transistor needs its own emitter resistor; measure every section and revisit total bias, sharing, thermal tracking and stability. This procedure and its supply-limit suggestions apply to the present <b>single-pair</b> build.')
head('Record your results')
table([['Item','Cold startup','After warm-up'],['Positive / negative rail voltage','',''],['R1 pins 3-2 (NPN), mV','',''],['R1 pins 2-1 (PNP), mV','',''],['AMP_OUT to GND, mV DC','',''],['Positive / negative supply current','',''],['Heatsink temperature / room temperature','',''],['Warm-up duration / observations','','']], [77*mm,48*mm,49*mm])
head('Scope and source checks')
add('Measurement connections and RV1 wiring were checked against the saved DarlingtonAmp schematic exported on 7 October 2026. No schematic or PCB changes were made. Hardware operation, thermal tracking and the final optimum bias remain unverified. The earlier pre-production review identified PCB clearance and heatsink-assembly issues; their resolution was not reassessed for this document.','SmallX')
add('Manufacturer reference: <link href="https://www.bourns.com/PDFs/3296.pdf" color="#175e82">Bourns 3296 datasheet</link> (terminal numbering, clockwise direction and end-of-travel behaviour). Local review: work/pre-production-review/Review.md.','SmallX')
add('Saved schematic SHA-256:<br/>'+digest,'SmallX')
doc=SimpleDocTemplate(str(target),pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=17*mm,bottomMargin=23*mm,title='DarlingtonAmp - Bias current setting guide',author='DarlingtonAmp project',pageCompression=1)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(target)
