"""Scoped replacement of the CS supply regulators, preserving rail supervision."""
import math
from pathlib import Path
from sexpr import parse,child,children

def replace_regulators(s,bom):
    remove={'U11','U12','C46','C47','C48','C49','C56','D2','D3'}
    parsed=[parse(x) for x in s.items]
    coords=set(); indices=set()
    for i,x in enumerate(parsed):
        if x[0]!='symbol':continue
        ref=next(str(p[2]) for p in children(x,'property') if p[1]=='Reference')
        if ref not in remove:continue
        indices.add(i);at=child(x,'at');xx,yy,ang=map(float,at[1:4]);a=math.radians(ang)
        lib=s.libs[str(child(x,'lib_id')[1])]
        unit=str(child(x,'unit')[1])
        for u in children(lib,'symbol'):
            if str(u[1]).rsplit('_',2)[1] not in ['0',unit]:continue
            for pin in children(u,'pin'):
                p=child(pin,'at');px,py=map(float,p[1:3])
                coords.add((round(xx+px*math.cos(a)-py*math.sin(a),5),round(yy-px*math.sin(a)-py*math.cos(a),5)))
    # All original regulator connections are isolated named-rail stubs.
    changed=True
    while changed:
        changed=False
        for i,x in enumerate(parsed):
            if i in indices or x[0]!='wire':continue
            pts={tuple(map(float,p[1:3])) for p in child(x,'pts')[1:]}
            if pts & coords:indices.add(i);coords|=pts;changed=True
    for i,x in enumerate(parsed):
        if x[0] in ['global_label','label','junction','no_connect'] and tuple(map(float,child(x,'at')[1:3])) in coords:indices.add(i)
        if x[0]=='symbol' and str(child(x,'lib_id')[1])=='power:GND' and tuple(map(float,child(x,'at')[1:3])) in coords:indices.add(i)
        if x[0]=='text' and (str(x[1]).startswith('U11 ~') or str(x[1]).startswith('Added local 47u at U12')):indices.add(i)
    s.items=[x for i,x in enumerate(s.items) if i not in indices]
    for ref in remove:bom.pop(ref,None)
    s.count=10000  # New UUIDs cannot collide with original power-sheet objects.
    p=s.sym('SubController:TPS7A3901',165.1,63.5,ref='U11')[0]
    s.wire(p['1'],(142.24,38.1),(142.24,27.94));s.label('+15V',(142.24,27.94),180,True);s.net('-15V',p['5'],-5.08)
    s.wire(p['2'],(142.24,p['2'][1]),(142.24,p['1'][1]),p['1']);s.dot((142.24,p['1'][1]))
    s.gnd(p['4']);s.gnd(p['11'])
    s.wire(p['3'],(139.7,68.58),(139.7,100.33))
    c=s.sym('Device:C',139.7,104.14,ref='C59',value='100n / 50V',foot='Capacitor_SMD:C_1206_3216Metric',note='NR/SS: nominal ~18ms ramp; X7R acceptable, not an audio capacitor.')[0]
    s.wire((139.7,100.33),c['1']);s.gnd(c['2'])
    # Owned 10k 0.1% and 22k 0.5% thin-film; series upper arms.
    def resistor(x,y,ref,v,angle=270):
        return s.sym('Device:R',x,y,ref=ref,value=v,angle=angle,foot='Resistor_SMD:R_0805_2012Metric',note='TPS feedback; owned thin-film, 2012 metric.')[0]
    r1=resistor(200.66,38.1,'R105','22k / 0.5%');r2=resistor(220.98,38.1,'R106','10k / 0.1%')
    s.wire(p['10'],r1['2']);s.wire(r1['1'],r2['2']);s.wire(r2['1'],(238.76,38.1),(238.76,48.26),p['9']);s.dot((238.76,38.1))
    lo=resistor(254,48.26,'R107','10k / 0.1%',0)
    s.wire((238.76,38.1),(254,38.1),lo['1']);s.gnd(lo['2'])
    a=resistor(195.58,78.74,'R108','22k / 0.5%');b=resistor(210.82,78.74,'R109','10k / 0.1%');d=resistor(226.06,78.74,'R110','10k / 0.1%')
    s.wire(p['6'],a['2']);s.wire(a['1'],b['2']);s.wire(b['1'],d['2']);s.wire(d['1'],(238.76,78.74),(238.76,68.58),p['7']);s.dot((238.76,78.74))
    lo=resistor(210.82,63.5,'R111','10k / 0.1%')
    s.wire(p['8'],lo['2']);s.wire(lo['1'],(238.76,63.5),(238.76,68.58));s.dot((238.76,68.58))
    # Feed-forward capacitors across the complete upper resistor arms.
    for ref,y,out,fb in [('C60',22.86,p['10'],(238.76,38.1)),('C61',116.84,p['6'],(238.76,78.74))]:
        c=s.sym('Device:C',210.82,y,ref=ref,value='10n C0G / 50V',angle=270,foot='Capacitor_SMD:C_0805_2012Metric',note='Owned Walsin 0805N103J500CT; feed-forward across total upper arm.')[0]
        s.wire(out,(187.96,out[1]),(187.96,y),c['2']);s.dot((187.96,out[1]))
        s.wire(c['1'],(238.76,y),fb)
    for ref,x,y,net in [('C46',106.68,38.1,'+15V'),('C57',106.68,63.5,'+15V'),('C48',106.68,83.82,'-15V'),('C58',106.68,111.76,'-15V'),('C47',269.24,30.48,'+5A'),('C49',279.4,88.9,'-5A')]:
        c=s.sym('Device:C',x,y,ref=ref,value='10u / 50V X5R',foot='Capacitor_SMD:C_1206_3216Metric',note='Owned Samsung CL31A106KBHNNNE. Two per input: >2.2u effective total at +/-15.75V after DC-bias/tolerance/temperature estimate. One per 5V output.')[0]
        s.net(net,c['1']);s.gnd(c['2'])
    s.label('+5A',(187.96,22.86),180,True);s.label('-5A',(187.96,116.84),180,True)
    for ref,x,inp,out in [('D2',71.12,'+15V','+5A'),('D3',104.14,'-15V','-5A')]:
        d=s.sym('Device:D',x,22.86,ref=ref,value='1N4007',foot='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal')[0]
        s.net(inp if ref=='D2' else out,d['1'],-5.08);s.net(out if ref=='D2' else inp,d['2'],5.08)
    s.text('TPS feedback: + arm (22k+10k)/10k -> +4.990V; - arm (22k+10k+10k)/10k -> -4.998V.\nNegative lower arm returns to BUF (pin8), NOT GND. EN tied to +15V; EP11 tied to GND.',139.7,132.08,1.016)
    s.text('U11 ~0.27W budget: solder EP to GND copper, thermal vias at layout. U13 +5R stays separate (~1.4W).\nC46+C57 and C48+C58: each pair directly at IN pins. C47/C49 directly at OUT pins.\nNR/SS100n; CFF10n each. Keep CS VD+ tied to VA+. Existing rail-fault/output mute retained.',20.32,119.38,1.016)

def build_footprint(path):
    name='TPS7A3901_DSC0010J_WSON10'
    s=f'(footprint "{name}" (version 20241229) (generator "pcbnew") (layer "F.Cu") (attr smd) (descr "TI TPS7A39 SBVS263B DSC0010J, drawing4221826/E03/2026. Manufacturer land-pattern example: pin pads0.6x0.24 at X+/-1.4, pitch0.5; EP11=1.65x2.4 plus four end fingers; GND. Thermal vias required at board layout, no board edits.")'
    for key,value,y,layer in [('Reference','REF**',-2.5,'F.SilkS'),('Value',name,2.5,'F.Fab')]:
        s+=f'(property "{key}" "{value}" (at 0 {y}) (layer "{layer}") (effects (font (size 0.8 0.8) (thickness 0.12))))'
    def line(a,b,layer,width):
        return f'(fp_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width {width}) (type default)) (layer "{layer}"))'
    for a,b in [((-1.1,-1.5),(1.5,-1.5)),((1.5,-1.5),(1.5,1.5)),((1.5,1.5),(-1.5,1.5)),((-1.5,1.5),(-1.5,-1.1)),((-1.5,-1.1),(-1.1,-1.5))]:s+=line(a,b,'F.Fab',.1)
    for a,b in [((-1.95,-1.95),(1.95,-1.95)),((1.95,-1.95),(1.95,1.95)),((1.95,1.95),(-1.95,1.95)),((-1.95,1.95),(-1.95,-1.95))]:s+=line(a,b,'F.CrtYd',.05)
    for y in [-1.6,1.6]:
        for x1,x2 in [(-1.5,-.6),(.6,1.5)]:s+=line((x1,y),(x2,y),'F.SilkS',.12)
    s+='(fp_circle (center -1.9 -1.25) (end -1.82 -1.25) (stroke (width 0.1) (type default)) (fill solid) (layer "F.SilkS"))'
    for i in range(5):
        for num,x,y in [(i+1,-1.4,-1+i*.5),(10-i,1.4,-1+i*.5)]:
            s+=f'(pad "{num}" smd roundrect (at {x} {y}) (size 0.6 0.24) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.208333))'
    s+='(pad "11" smd rect (at 0 0) (size 1.65 2.4) (layers "F.Cu" "F.Mask"))'
    for x in [-.25,.25]:
        for y in [-1.4125,1.4125]:s+=f'(pad "11" smd rect (at {x} {y}) (size 0.25 0.575) (layers "F.Cu" "F.Mask"))'
    for y in [-.63,.63]:s+=f'(pad "" smd roundrect (at 0 {y}) (size 1.5 1.06) (layers "F.Paste") (roundrect_rratio 0.03))'
    for x in [-.25,.25]:
        for y in [-1.53,1.53]:s+=f'(pad "" smd rect (at {x} {y}) (size 0.25 0.34) (layers "F.Paste"))'
    Path(path).write_text(s+')\n')
