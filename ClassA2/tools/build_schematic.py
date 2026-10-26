#!/usr/bin/env python3
"""Generate the ClassA2 Rev A KiCad 10 schematic (one mono channel) from the part table below.

Writes ClassA2.kicad_sch, ClassA2.kicad_sym (project power symbols), sym-lib-table, fp-lib-table,
ClassA2.pretty/ and BOM.csv. RERUNNING OVERWRITES MANUAL SCHEMATIC EDITS. The PCB file is never
touched. tools/verify_netlist.py checks the KiCad netlist against simulation/amp.cir."""
import csv, json, math, re, shutil, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KSYM = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
PROJ = 'ClassA2'
ROOT_UUID = '9732a90e-6fb3-41ec-883b-a13a96a7b312'   # existing empty schematic uuid, kept
def U(s): return str(uuid.uuid5(uuid.NAMESPACE_URL, 'ClassA2/revA/' + s))
def q(s): return json.dumps(str(s))

# ------------------------------------------------------------------ library symbols
def sexpr_block(text, name):
    i = text.find(f'(symbol "{name}"')
    if i < 0: raise KeyError(name)
    d = 0
    for j in range(i, len(text)):
        if text[j] == '(': d += 1
        elif text[j] == ')':
            d -= 1
            if d == 0: return text[i:j+1]

LIBTXT = {}
def libtext(lib):
    if lib not in LIBTXT: LIBTXT[lib] = (KSYM / f'{lib}.kicad_sym').read_text()
    return LIBTXT[lib]

SYMS = {}      # lib_id -> (embedded text, {pin: (x, y)}, {pin name: pin number})
def load(lib_id):
    if lib_id in SYMS: return SYMS[lib_id]
    lib, name = lib_id.split(':')
    if lib == PROJ:
        base = {'+V': '+15V', '+VF': '+15V', '-V': '-15V', '-VF': '-15V'}[name]
        b = sexpr_block(libtext('power'), base)
        b = b.replace(f'"{base}"', q(name)).replace(f'"{base}_', f'"{name}_')
        b = re.sub(r'\(property "Description" "(?:\\.|[^"\\])*"', f'(property "Description" "Power rail {name} (ClassA2)"', b)
        PROJSYM[name] = b
    else:
        b = sexpr_block(libtext(lib), name)
    emb = b.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1)
    pins = {}; names = {}
    for m in re.finditer(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) \d+\)[\s\S]*?\(name "([^"]*)"[\s\S]*?\(number "([^"]*)"', b):
        pins[m.group(4)] = (float(m.group(1)), float(m.group(2))); names[m.group(3)] = m.group(4)
    SYMS[lib_id] = (emb, pins, names)
    return SYMS[lib_id]
PROJSYM = {}

# ------------------------------------------------------------------ sheet model
ITEMS, PARTS, WIRES, LABELS, PWRS, TEXTS, RECTS = [], {}, [], [], [], [], []
PWR_N = [0]

def xf(px, py, x, y, rot, mirror):
    if mirror == 'y': px = -px
    if mirror == 'x': py = -py
    a = math.radians(rot)
    rx = px*math.cos(a) - py*math.sin(a); ry = px*math.sin(a) + py*math.cos(a)
    return (round(x + rx, 3), round(y - ry, 3))

def prop(k, v, x, y, hide=False, angle=0, size=1.27, just=None):
    j = f'(justify {just})' if just else ''
    return (f'(property {q(k)} {q(v)} (at {x} {y} {angle}) (show_name no) (do_not_autoplace no)'
            f'{" (hide yes)" if hide else ""} (effects (font (size {size} {size})) {j}))')

def part(ref, lib_id, value, x, y, rot=0, mirror=None, fp='', mpn='', mfr='', ds='', desc='', stock='', notes='',
         rating='', spice=None, dnp=False, lab=None, inbom=True):
    """Place a symbol. spice = {pin number: SPICE node} for the netlist cross-check. lab = (dx, dy, justify) for Ref/Value."""
    emb, pins, names = load(lib_id)
    P = {n: xf(px, py, x, y, rot, mirror) for n, (px, py) in pins.items()}
    for nm, n in names.items():
        if nm and nm not in P: P[nm] = P[n]
    if lab is None:
        if lib_id.startswith('Transistor_BJT'):
            lab = (-12.7, -1.27, 'right') if mirror == 'y' or rot == 180 else (6.35, -1.27, 'left')
        elif lib_id in ('Device:R', 'Device:C', 'Device:C_Polarized', 'Device:L', 'Device:R_Potentiometer_Trim') and rot in (90, 270):
            lab = (0, -3.3, None)
        elif lib_id == 'Device:D' and rot in (90, 270):
            lab = (2.54, 0, 'left')
        else:
            lab = (2.54, 0, 'left')
    dx, dy, just = lab
    fa = rot if rot in (90, 270) else 0          # keeps field text horizontal on rotated symbols
    if just and ((mirror == 'y') ^ (rot in (90, 180))):
        just = {'left': 'right', 'right': 'left'}[just]   # eeschema mirrors field justification with the symbol
    if just is None:
        props = prop('Reference', ref, x+dx, y+dy-1.27, angle=fa) + prop('Value', value, x+dx, y+dy+1.27, angle=fa)
    else:
        props = prop('Reference', ref, x+dx, y+dy-1.27, angle=fa, just=just) + prop('Value', value, x+dx, y+dy+1.27, angle=fa, just=just)
    for k, v in [('Footprint', fp), ('Datasheet', ds), ('Description', desc), ('Manufacturer', mfr), ('MPN', mpn),
                 ('Rating', rating), ('Inventory', stock), ('Notes', notes)]:
        props += prop(k, v, x, y, hide=True)
    uid = U('sym/' + ref)
    ITEMS.append(f'(symbol (lib_id {q(lib_id)}) (at {x} {y} {rot}) {"(mirror " + mirror + ")" if mirror else ""} (unit 1) (body_style 1)'
                 f' (exclude_from_sim no) (in_bom {"yes" if inbom else "no"}) (on_board yes) (in_pos_files yes) (dnp {"yes" if dnp else "no"})'
                 f' (uuid {q(uid)}) {props} ' + ''.join(f'(pin {q(n)} (uuid {q(U(uid + n))}))' for n in pins) +
                 f' (instances (project {q(PROJ)} (path {q("/" + ROOT_UUID)} (reference {q(ref)}) (unit 1)))))')
    PARTS[ref] = dict(lib_id=lib_id, value=value, fp=fp, mpn=mpn, mfr=mfr, ds=ds, desc=desc, stock=stock, notes=notes,
                      rating=rating, spice=spice or {}, dnp=dnp, pins=P, inbom=inbom)
    return P

def pwr(name, pt, rot=0):
    """Power or flag symbol whose pin sits at pt. name: GND, PWR_FLAG, +V, -V, +VF, -VF."""
    lib_id = f'power:{name}' if name in ('GND', 'PWR_FLAG') else f'{PROJ}:{name}'
    load(lib_id)
    PWR_N[0] += 1
    ref = ('#FLG' if name == 'PWR_FLAG' else '#PWR') + f'{PWR_N[0]:03d}'
    x, y = pt
    vy = y + 5.08 if name in ('GND', '-V', '-VF') else y - 3.81
    props = prop('Reference', ref, x, y, hide=True) + prop('Value', name, x, vy, hide=(name == 'PWR_FLAG'))
    props += prop('Footprint', '', x, y, hide=True) + prop('Datasheet', '', x, y, hide=True) + prop('Description', '', x, y, hide=True)
    uid = U('pwr/' + ref)
    ITEMS.append(f'(symbol (lib_id {q(lib_id)}) (at {x} {y} {rot}) (unit 1) (body_style 1) (exclude_from_sim no) (in_bom no) (on_board yes)'
                 f' (in_pos_files no) (dnp no) (uuid {q(uid)}) {props} (pin "1" (uuid {q(U(uid + "1"))}))'
                 f' (instances (project {q(PROJ)} (path {q("/" + ROOT_UUID)} (reference {q(ref)}) (unit 1)))))')
    PWRS.append((name, (round(x, 3), round(y, 3))))

def W(*pts):
    pts = [(round(a, 3), round(b, 3)) for a, b in pts]
    for a, b in zip(pts, pts[1:]):
        if a != b:
            assert a[0] == b[0] or a[1] == b[1], ('non-orthogonal wire', a, b)
            WIRES.append((a, b))

def label(name, pt, angle=0, just='left'):
    LABELS.append((name, pt, angle, just))

def text(s, x, y, size=1.27, bold=False):
    TEXTS.append((s, x, y, size, bold))

def block(title, x1, y1, x2, y2):
    RECTS.append((x1, y1, x2, y2)); text(title, x1 + 1.27, y1 + 1.27, 1.6, True)

# ------------------------------------------------------------------ parts data helpers
FP_R = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal'
FP_R1W = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal'
FP_R2W = 'Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal'
FP_RPWR = f'{PROJ}:Yageo_SQP500_L22.0mm_W9.5mm_P30.48mm'
FP_C0G = 'Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
FP_R82 = 'Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2'
FP_R82_1U = 'Capacitor_THT:C_Rect_L7.2mm_W5.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2'
FP_MKS2 = 'Capacitor_THT:C_Rect_L7.2mm_W7.2mm_P5.00mm_FKS2_FKP2_MKS2_MKP2'
FP_ZLH = 'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm'
FP_FR1000 = 'Capacitor_THT:CP_Radial_D12.5mm_P5.00mm'
FP_UES = 'Capacitor_THT:C_Radial_D16.0mm_H25.0mm_P7.50mm'
FP_DO35 = 'Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal'
FP_TO92 = 'Package_TO_SOT_THT:TO-92_Inline'
FP_TO92L = 'Package_TO_SOT_THT:TO-92L_Inline'
FP_TO126 = 'Package_TO_SOT_THT:TO-126-3_Vertical'
FP_TO3P = 'Package_TO_SOT_THT:TO-3P-3_Vertical'
FP_TRIM = 'Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical'
FP_TP = 'TestPoint:TestPoint_Keystone_5000-5004_Miniature'

DS = dict(
    C5198='https://toshiba.semicon-storage.com/info/docget.jsp?did=20663&prodName=2SC5198',
    A1941='https://toshiba.semicon-storage.com/info/docget.jsp?did=20422&prodName=2SA1941',
    C2240='https://www.micros.com.pl/mediaserver/info-t2sa9702sc2240.pdf',
    A970='https://www.micros.com.pl/mediaserver/info-t2sa9702sc2240.pdf',
    C2705='https://www.ges.cz/2SC2705-2SA1145-Toshiba-par-pro-NF-vykonove-zesilovace-budice-a-rozkmitove-stupne-_a255141_10699.pdf',
    BD139='https://www.st.com/resource/en/datasheet/bd135.pdf',
    BC546='http://www.farnell.com/datasheets/2277528.pdf', BC556='https://www.onsemi.com/pdf/datasheet/bc556bta-d.pdf',
    D4148='https://www.onsemi.com/pdf/datasheet/1n914-d.pdf')

def R(ref, val, x, y, rot, a, b, mpn, stock, rating='0.6W 1% metal film', mfr='TE Connectivity', fp=FP_R, notes='', **k):
    return part(ref, 'Device:R', val, x, y, rot, fp=fp, mpn=mpn, mfr=mfr, rating=rating, stock=stock, notes=notes,
                desc='Resistor', spice={'1': a, '2': b}, **k)

def LR1(v): return 'LR1F' + v  # TE Connectivity LR1 series part number stem used in the inventory

# ================================================================== LAYOUT
Y0 = 148.59          # output / input centre line; upper and lower halves mirror about it
def M(y): return round(2*Y0 - y, 3)
TOP, BOT = 62.23, 236.22

# ---------------- supply entry and decoupling (top left)
block('SUPPLY ENTRY / LOCAL DECOUPLING', 15.24, 20.32, 157.48, 60.96)
yP, yG, yN = 33.02, 43.18, 53.34
J2 = part('J2', 'Connector_Generic:Conn_01x03', 'POWER', 25.4, yG, 0, 'y',
          fp='Connector_Molex:Molex_KK-396_A-41791-0003_1x03_P3.96mm_Vertical', mpn='09-65-2038', mfr='Molex',
          desc='KK-396 3-way header, 7 A per contact', stock='BUY (2 for stereo)', notes='1 = +V, 2 = GND, 3 = -V. External symmetrical DC from the shared PSU.',
          spice={'1': 'VP', '2': '0', '3': 'VN'}, lab=(-2.54, -5.08, 'right'))
R3 = R('R3', '10R', 104.14, yP, 90, 'VP', 'VPF', LR1('10R'), 'IN STOCK (inv 283)', notes='Front-end supply filter, ~10 mA.', lab=(0, -3.3, None))
R4 = R('R4', '10R', 104.14, yN, 90, 'VN', 'VNF', LR1('10R'), 'IN STOCK (inv 283)', notes='Front-end supply filter.', lab=(0, 3.3, None))
W(J2['1'], (35.56, J2['1'][1]), (35.56, yP), R3['1'])          # +V line
W(J2['3'], (35.56, J2['3'][1]), (35.56, yN), R4['1'])          # -V line
W(J2['2'], (116.84, yG))                                        # GND line
W(R3['2'], (134.62, yP)); W(R4['2'], (134.62, yN))               # +VF / -VF
pwr('PWR_FLAG', (40.64, yP)); pwr('+V', (48.26, yP))
pwr('PWR_FLAG', (40.64, yN), 180); pwr('-V', (48.26, yN))
pwr('PWR_FLAG', (40.64, yG), 180); pwr('GND', (48.26, yG))
TP1 = part('TP1', 'Connector:TestPoint', '+V', 55.88, yP, fp=FP_TP, mpn='5000', mfr='Keystone', stock='BUY', desc='Test point, red',
           spice={'1': 'VP'}, lab=(1.27, -3.81, 'left'))
TP3 = part('TP3', 'Connector:TestPoint', 'GND', 55.88, yG, 0, fp=FP_TP, mpn='5001', mfr='Keystone', stock='BUY', desc='Test point, black',
           spice={'1': '0'}, lab=(1.27, -3.81, 'left'))
TP2 = part('TP2', 'Connector:TestPoint', '-V', 55.88, yN, 180, fp=FP_TP, mpn='5004', mfr='Keystone', stock='BUY', desc='Test point, yellow',
           spice={'1': 'VN'}, lab=(1.27, 3.81, 'left'))
def cap_up(ref, x, **k):   # between +rail line and GND line
    P = part(ref, x=x, y=38.1, **k); W((x, yP), P['1']); W(P['2'], (x, yG)); return P
def cap_dn(ref, x, **k):   # between GND line and -rail line
    P = part(ref, x=x, y=48.26, **k); W((x, yG), P['1']); W(P['2'], (x, yN)); return P
C11 = cap_up('C11', 71.12, lib_id='Device:C_Polarized', value='1000u / 35V', fp=FP_FR1000, mpn='EEU-FR1V102', mfr='Panasonic',
             rating='35V 105C low-ESR FR', stock='IN STOCK (inv 338, 8 pcs)', desc='Electrolytic',
             notes='Place at Q12 emitter / +V entry. Local reservoir only; main PSU caps are off-board.', spice={'1': 'VP', '2': '0'})
C12 = cap_up('C12', 93.98, lib_id='Device:C', value='100n FILM', fp=FP_R82, mpn='R82DC3100DQ50J', mfr='KEMET', rating='63V PET',
             stock='IN STOCK (inv 406)', notes='At Q12 emitter pin.', spice={'1': 'VP', '2': '0'}, desc='Film capacitor')
C13 = cap_dn('C13', 71.12, lib_id='Device:C_Polarized', value='1000u / 35V', fp=FP_FR1000, mpn='EEU-FR1V102', mfr='Panasonic',
             rating='35V 105C low-ESR FR', stock='IN STOCK (inv 338)', desc='Electrolytic',
             notes='Place at Q13 emitter / -V entry. + terminal to GND.', spice={'1': '0', '2': 'VN'})
C14 = cap_dn('C14', 93.98, lib_id='Device:C', value='100n FILM', fp=FP_R82, mpn='R82DC3100DQ50J', mfr='KEMET', rating='63V PET',
             stock='IN STOCK (inv 406)', notes='At Q13 emitter pin.', spice={'1': '0', '2': 'VN'}, desc='Film capacitor')
C3 = cap_up('C3', 116.84, lib_id='Device:C_Polarized', value='220u / 35V', fp=FP_ZLH, mpn='35ZLH220MEFC8X11.5', mfr='Rubycon',
            stock='IN STOCK (inv 366)', rating='35V ZLH', desc='Electrolytic',
            notes='Front-end +VF decoupling; at the input-stage/VAS area.', spice={'1': 'VPF', '2': '0'})
C4 = cap_dn('C4', 116.84, lib_id='Device:C_Polarized', value='220u / 35V', fp=FP_ZLH, mpn='35ZLH220MEFC8X11.5', mfr='Rubycon',
            stock='IN STOCK (inv 366)', rating='35V ZLH', desc='Electrolytic',
            notes='Front-end -VF decoupling. + terminal to GND.', spice={'1': '0', '2': 'VNF'})
pwr('+VF', (127.0, yP)); pwr('PWR_FLAG', (134.62, yP))
pwr('-VF', (127.0, yN)); pwr('PWR_FLAG', (134.62, yN), 180)
text('C11-C14 at the output-pair emitters (Q12/Q13).', 142.24, 24.13, 1.27)
text('C3/C4 at the input stage and VAS.', 142.24, 27.94, 1.27)

# ---------------- input (left, centre line)
block('INPUT', 15.24, 132.08, 81.28, 167.64)
J1 = part('J1', 'Connector_Generic:Conn_01x02', 'AUDIO IN', 22.86, Y0, 0, 'y',
          fp=f'{PROJ}:Multicomp_MC34629_1x02_P2.54mm', mpn='MC34629 (+ MC34481 housing)', mfr='Multicomp Pro', stock='IN STOCK (inv 126 / 128)',
          desc='2.54 mm 2-way header to chassis RCA, screened lead', notes='1 = signal, 2 = signal ground (screen).',
          spice={'1': 'IN', '2': '0'}, lab=(-2.54, -3.81, 'right'))
W(J1['2'], (30.48, J1['2'][1]), (30.48, J1['2'][1] + 2.54)); pwr('GND', (30.48, J1['2'][1] + 2.54))
C1 = part('C1', 'Device:C', '2u2 FILM', 40.64, Y0, 90, fp=FP_MKS2, mpn='MKS2C042201K00KSSD', mfr='WIMA', rating='63V PET',
          stock='IN STOCK (inv 417, 3 pcs; 2 needed)', notes='Input DC block. With R1 = 47k: 1.54 Hz. PP film is an optional like-for-like upgrade.',
          spice={'1': 'IN', '2': 'INA'}, desc='Film capacitor', lab=(0, -3.3, None))
W(J1['1'], C1['1']); label('IN', (31.75, Y0))
R1 = R('R1', '47k', 50.8, 156.21, 0, 'INA', '0', LR1('47K'), 'IN STOCK (inv 277)', notes='Input resistance / DC reference. Equal to R26 to cancel base-current offset.')
W(C1['2'], (50.8, Y0), R1['1']); pwr('GND', R1['2'])
R2 = R('R2', '1k', 60.96, Y0, 90, 'INA', 'INB', LR1('1K'), 'IN STOCK (inv 285)', notes='Input stopper; with C2 forms a 339 kHz RF filter.', lab=(0, -3.3, None))
W((50.8, Y0), R2['1'])
C2 = part('C2', 'Device:C', '470p C0G', 71.12, 156.21, fp=FP_C0G, mpn='0805N471J500CT', mfr='Multicomp Pro', rating='50V C0G 5% 2012 metric',
          stock='IN STOCK (inv 337)', notes='RF filter to GND; return to input ground.', spice={'1': 'INB', '2': '0'}, desc='C0G capacitor')
W(R2['2'], (71.12, Y0), C2['1']); pwr('GND', C2['2'])
XB = 88.9                                      # INB bus to both input transistor bases
W((71.12, Y0), (XB, Y0))

# ---------------- input stage
block('INPUT STAGE (LTPs, TAIL CCS, OFFSET TRIM)', 82.55, TOP, 153.67, BOT)
YQ = 96.52; XE1, XE2 = 101.6, 139.7
Q1 = part('Q1', 'Transistor_BJT:Q_NPN_ECB', '2SC2240-GR', XE1 - 2.54, YQ, fp=FP_TO92, mpn='2SC2240-GR', mfr='Toshiba', ds=DS['C2240'],
          rating='120V 100mA 300mW, hFE 200-400', stock='IN STOCK (inv 609, 7 pcs; 4 needed)', notes='Pins 1E 2C 3B (2-5F1B). Match Q1/Q2 VBE and hFE; thermally couple.',
          spice={'1': 'E1', '2': 'C1N', '3': 'INB'}, lab=(-5.08, -5.08, 'right'))
Q2 = part('Q2', 'Transistor_BJT:Q_NPN_ECB', '2SC2240-GR', XE2 + 2.54, YQ, 0, 'y', fp=FP_TO92, mpn='2SC2240-GR', mfr='Toshiba', ds=DS['C2240'],
          rating='120V 100mA 300mW', stock='IN STOCK (inv 609)', notes='Feedback side. Collector straight to +VF.',
          spice={'1': 'E2', '2': 'VPF', '3': 'FB'}, lab=(3.81, -6.35, 'left'))
W((XB, YQ), Q1['B']); pwr('+VF', Q2['C'])
R9 = R('R9', '1k3', XE1, 76.2, 0, 'VPF', 'C1N', 'MF50 1K3', 'IN STOCK (inv 763, 9 pcs; 4 needed)', mfr='Multicomp Pro', rating='0.5W 1% metal film',
       notes='Q1 load; sets VAS current with R16 (~5.5 mA).', lab=(-2.54, 0, 'right'))
pwr('+VF', R9['1'])
YC = 83.82                                      # C1N horizontal to the PNP VAS
W(R9['2'], (XE1, YC), Q1['C'])
YRV = 104.14
RV2 = part('RV2', 'Device:R_Potentiometer_Trim', '500R OFFSET', 118.11, YRV, 270, fp=FP_TRIM, mpn='3296W-1-501LF (stocked generic 500R multi-turn)',
           mfr='Bourns / generic', stock='IN STOCK (inv 532, 5 pcs; 4 needed incl. RV1)', rating='multi-turn cermet',
           desc='Output offset trim', notes='Centre = untrimmed (~-15 mV sim). Open wiper falls back to R6/R7 only (safe). Range ~+17 to -47 mV in sim.',
           spice={'3': 'E1', '1': 'E2', '2': 'WP'}, lab=(0, -4.45, None))
R6 = R('R6', '220R', XE1, 110.49, 0, 'E1', 'TN', LR1('220R'), 'IN STOCK (inv 152)', notes='Emitter degeneration.', lab=(-2.54, 0, 'right'))
R7 = R('R7', '220R', XE2, 110.49, 0, 'E2', 'TN', LR1('220R'), 'IN STOCK (inv 152)', notes='Emitter degeneration.', lab=(2.54, 0, 'left'))
W(Q1['E'], (XE1, YRV), R6['1']); W(Q2['E'], (XE2, YRV), R7['1'])
W((XE1, YRV), RV2['3']); W(RV2['1'], (XE2, YRV))
R30 = R('R30', '220R', 118.11, 111.76, 0, 'WP', 'TN', LR1('220R'), 'IN STOCK (inv 152)', notes='Trim wiper feed.', lab=(2.54, 0, 'left'))
W(RV2['2'], R30['1'])
YTN = 120.65
W(R6['2'], (XE1, YTN), (XE2, YTN), R7['2']); W(R30['2'], (118.11, YTN))
# tails: column A = PNP tail Q6, column B = shared reference chain, column C = NPN tail Q5
XA, XBc, XC = 106.68, 121.92, 132.08
D1 = part('D1', 'Device:D', '1N4148', XBc, 132.08, 90, fp=FP_DO35, mpn='1N4148', mfr='onsemi', ds=DS['D4148'], stock='IN STOCK (inv 138)',
          notes='Tail reference.', spice={'2': 'VPF', '1': 'X1'}, desc='Signal diode', lab=(2.54, 0, 'left'))
D2 = part('D2', 'Device:D', '1N4148', XBc, 139.7, 90, fp=FP_DO35, mpn='1N4148', mfr='onsemi', ds=DS['D4148'], stock='IN STOCK (inv 138)',
          notes='Tail reference.', spice={'2': 'X1', '1': 'RBP'}, desc='Signal diode', lab=(2.54, 0, 'left'))
R5 = R('R5', '27k', XBc, 147.32, 0, 'RBP', 'RBN', LR1('27K'), 'IN STOCK (inv 784)', notes='Shared feed for both tail references (~1.05 mA).', lab=(2.54, 0, 'left'))
D3 = part('D3', 'Device:D', '1N4148', XBc, 154.94, 90, fp=FP_DO35, mpn='1N4148', mfr='onsemi', ds=DS['D4148'], stock='IN STOCK (inv 138)',
          notes='Tail reference.', spice={'2': 'RBN', '1': 'X2'}, desc='Signal diode', lab=(2.54, 0, 'left'))
D4 = part('D4', 'Device:D', '1N4148', XBc, 162.56, 90, fp=FP_DO35, mpn='1N4148', mfr='onsemi', ds=DS['D4148'], stock='IN STOCK (inv 138)',
          notes='Tail reference.', spice={'2': 'X2', '1': 'VNF'}, desc='Signal diode', lab=(2.54, 0, 'left'))
pwr('+VF', D1['A']); pwr('-VF', D4['K'])
Q6 = part('Q6', 'Transistor_BJT:Q_PNP_CBE', 'BC556', XA + 2.54, D2['K'][1], 180, fp=FP_TO92, mpn='BC556B', mfr='onsemi', ds=DS['BC556'],
          rating='-65V -100mA', stock='IN STOCK (inv 462)', notes='PNP tail CCS ~2.0 mA. Pins 1C 2B 3E (onsemi).',
          spice={'1': 'TP', '2': 'RBP', '3': 'E6'}, lab=(-5.08, 2.54, 'right'))
R13 = R('R13', '270R', XA, Q6['E'][1] - 5.08, 0, 'VPF', 'E6', LR1('270R'), 'IN STOCK (inv 92)', notes='PNP tail current set.', lab=(-2.54, 0, 'right'))
pwr('+VF', R13['1']); W(R13['2'], Q6['E']); W(Q6['B'], D2['K'])
Q5 = part('Q5', 'Transistor_BJT:Q_NPN_CBE', 'BC546', XC - 2.54, D3['A'][1], fp=FP_TO92, mpn='BC546B (ST BC546 stocked)', mfr='STMicroelectronics',
          ds=DS['BC546'], rating='65V 100mA', stock='IN STOCK (inv 254)', notes='NPN tail CCS ~1.95 mA. Pins 1C 2B 3E - check the fitted brand.',
          spice={'1': 'TN', '2': 'RBN', '3': 'E5'}, lab=(3.81, -5.08, 'left'))
R8 = R('R8', '270R', XC, Q5['E'][1] + 5.08, 0, 'E5', 'VNF', LR1('270R'), 'IN STOCK (inv 92)', notes='NPN tail current = (2 x Vf - Vbe)/270R.', lab=(2.54, 0, 'left'))
W(Q5['E'], R8['1']); pwr('-VF', R8['2']); W(Q5['B'], D3['A'])
W(Q5['C'], (XC, YTN))
YTP = M(YTN)
W(Q6['C'], (XA, YTP))
# lower half (PNP pair)
Q3 = part('Q3', 'Transistor_BJT:Q_PNP_ECB', '2SA970-BL', XE1 - 2.54, M(YQ), 0, 'x', fp=FP_TO92, mpn='2SA970-BL', mfr='Toshiba', ds=DS['A970'],
          rating='-120V -100mA 300mW, hFE 350-700', stock='IN STOCK (inv 614, 17 pcs; 4 needed)', notes='Pins 1E 2C 3B (2-5F1B). Match Q3/Q4.',
          spice={'1': 'E3', '2': 'C3P', '3': 'INB'}, lab=(-5.08, 5.08, 'right'))
Q4 = part('Q4', 'Transistor_BJT:Q_PNP_ECB', '2SA970-BL', XE2 + 2.54, M(YQ), 180, fp=FP_TO92, mpn='2SA970-BL', mfr='Toshiba', ds=DS['A970'],
          rating='-120V -100mA 300mW', stock='IN STOCK (inv 614)', notes='Feedback side. Collector straight to -VF.',
          spice={'1': 'E4', '2': 'VNF', '3': 'FB'}, lab=(3.81, 6.35, 'left'))
W((XB, M(YQ)), Q3['B']); W((XB, YQ), (XB, M(YQ))); pwr('-VF', Q4['C'])
R14 = R('R14', '1k3', XE1, M(76.2), 0, 'C3P', 'VNF', 'MF50 1K3', 'IN STOCK (inv 763)', mfr='Multicomp Pro', rating='0.5W 1% metal film',
        notes='Q3 load; sets VAS current with R17.', lab=(-2.54, 0, 'right'))
pwr('-VF', R14['2'])
W(R14['1'], (XE1, M(YC)), Q3['C'])
R11 = R('R11', '220R', XE1, M(110.49), 0, 'TP', 'E3', LR1('220R'), 'IN STOCK (inv 152)', notes='Emitter degeneration.', lab=(-2.54, 0, 'right'))
R12 = R('R12', '220R', XE2, M(110.49), 0, 'TP', 'E4', LR1('220R'), 'IN STOCK (inv 152)', notes='Emitter degeneration.', lab=(2.54, 0, 'left'))
W(R11['2'], Q3['E']); W(R12['2'], Q4['E'])
W(R11['1'], (XE1, YTP), (XE2, YTP), R12['1'])
XFB = 149.86
W(Q2['B'], (XFB, YQ), (XFB, M(YQ)), Q4['B'])
label('FB', (XFB, 127.0), 0)

# ---------------- VAS, compensation and feedback
block('VAS / MILLER COMP. / FEEDBACK', 154.94, TOP, 200.66, BOT)
R27 = R('R27', '3k', 157.48, 156.21, 0, 'FB', 'FBC', LR1('3K0'), 'IN STOCK (inv 796)', notes='Feedback shunt.', lab=(2.54, 0, 'left'))
C9 = part('C9', 'Device:C', '220u NP / 50V', 157.48, 168.91, fp=FP_UES, mpn='UES1H221MHM', mfr='Nichicon', rating='50V bipolar ES series',
          stock='ON ORDER (inv 501, 2 incoming)', notes='Feedback DC block: DC gain = 1. 3k x 220u = 0.24 Hz. Bipolar; ~15 mV across it.',
          spice={'1': 'FBC', '2': '0'}, desc='Bipolar electrolytic', lab=(2.54, 0, 'left'))
R26 = R('R26', '47k', 168.91, Y0, 90, 'FB', 'OUT', LR1('47K'), 'IN STOCK (inv 277)', notes='Feedback; gain = 1 + R26/R27 = 16.7 (24.4 dB).',
        lab=(0, 3.3, None))
C8 = part('C8', 'Device:C', 'DNP 10p C0G', 168.91, 140.97, 90, fp=FP_C0G, mpn='(DNP)', mfr='', dnp=True, stock='DNP',
          notes='FB LEAD DNP: optional phase-lead across R26 if bench square waves show ringing; not needed in simulation.',
          spice={'1': 'FB', '2': 'OUT'}, desc='C0G capacitor', lab=(0, -5.08, None))
W((XFB, Y0), (157.48, Y0), R26['1']); W((157.48, Y0), R27['1']); W(R27['2'], C9['1']); pwr('GND', C9['2'])
W(C8['1'], (C8['1'][0], Y0)); W(C8['2'], (C8['2'][0], Y0))
W(R26['2'], (177.8, Y0)); label('OUT', (177.8, Y0))
YBP = 101.6
C5 = part('C5', 'Device:C', '100p C0G', 177.8, 92.71, fp=FP_C0G, mpn='CL21C101JBANNNC', mfr='Samsung', rating='50V C0G 5% 2012 metric',
          stock='IN STOCK (inv 197)', notes='Miller compensation, VAS collector to base. Do not reduce without a loop re-test.',
          spice={'1': 'C1N', '2': 'VBP'}, desc='C0G capacitor', lab=(-2.54, 0, 'right'))
Q7 = part('Q7', 'Transistor_BJT:Q_PNP_ECB', '2SA1145-Y', 187.96, YC, 0, 'x', fp=FP_TO92L, mpn='2SA1145-Y', mfr='Toshiba', ds=DS['C2705'],
          rating='-150V -50mA 0.8W, Cob 2.5pF', stock='IN STOCK (inv 612, 12 pcs)',
          notes='PNP VAS ~5.5 mA. Pins 1E 2C 3B (TO-92MOD 2-5J1A, second-source sheet): CONFIRM with a meter before fitting.',
          spice={'1': 'E7', '2': 'VBP', '3': 'C1N'}, lab=(5.08, 1.27, 'left'))
W((XE1, YC), Q7['B']); W((177.8, YC), C5['1']); W(C5['2'], (177.8, YBP), (Q7['C'][0], YBP))
R16 = R('R16', '100R', Q7['E'][0], 74.93, 0, 'VPF', 'E7', LR1('100R'), 'IN STOCK (inv 150)', notes='VAS emitter degeneration.', lab=(2.54, 0, 'left'))
pwr('+VF', R16['1']); W(R16['2'], Q7['E']); W(Q7['C'], (Q7['C'][0], YBP))
YBN = M(YBP)
Q8 = part('Q8', 'Transistor_BJT:Q_NPN_ECB', '2SC2705-Y', 187.96, M(YC), fp=FP_TO92L, mpn='2SC2705-Y', mfr='Toshiba', ds=DS['C2705'],
          rating='150V 50mA 0.8W, Cob 1.8pF', stock='IN STOCK (inv 611, 12 pcs)',
          notes='NPN VAS ~5.5 mA. Pins 1E 2C 3B (TO-92MOD): CONFIRM with a meter before fitting.',
          spice={'1': 'E8', '2': 'VBN', '3': 'C3P'}, lab=(5.08, -1.27, 'left'))
C6 = part('C6', 'Device:C', '100p C0G', 177.8, M(92.71), fp=FP_C0G, mpn='CL21C101JBANNNC', mfr='Samsung', rating='50V C0G 5% 2012 metric',
          stock='IN STOCK (inv 197)', notes='Miller compensation.', spice={'1': 'VBN', '2': 'C3P'}, desc='C0G capacitor', lab=(-2.54, 0, 'right'))
W((XE1, M(YC)), Q8['B']); W((177.8, M(YC)), C6['2']); W(C6['1'], (177.8, YBN), (Q8['C'][0], YBN))
R17 = R('R17', '100R', Q8['E'][0], M(74.93), 0, 'E8', 'VNF', LR1('100R'), 'IN STOCK (inv 150)', notes='VAS emitter degeneration.', lab=(2.54, 0, 'left'))
pwr('-VF', R17['2']); W(Q8['E'], R17['1']); W(Q8['C'], (Q8['C'][0], YBN))

# ---------------- bias generator
block('BIAS GENERATOR', 201.93, TOP, 241.3, BOT)
text('Q9 on the main heatsink', 203.2, 66.04, 1.27)
text('between Q10 and Q11.', 203.2, 68.58, 1.27)
XS = 210.82
Q9 = part('Q9', 'Transistor_BJT:Q_NPN_ECB', 'BD139', XS + 10.16, Y0, fp=FP_TO126, mpn='BD139', mfr='STMicroelectronics', ds=DS['BD139'],
          rating='80V 1.5A 12.5W', stock='IN STOCK (inv 148, 13 pcs)',
          notes='VBE multiplier / thermal sensor. Mount on main heatsink between Q10 and Q11 (insulated). Pins 1E 2C 3B.',
          spice={'1': 'VBN', '2': 'VBP', '3': 'B9'}, lab=(5.08, -3.81, 'left'))
R18 = R('R18', '1k', XS, 135.89, 0, 'VBP', 'B9', LR1('1K'), 'IN STOCK (inv 285)', notes='VBE multiplier upper leg.', lab=(-2.54, 0, 'right'))
R19 = R('R19', '470R', XS, 158.75, 0, 'B9', 'X9', LR1('470R'), 'IN STOCK (inv 153, 9 pcs)',
        notes='Fixed lower leg: limits maximum bias (~0.94 A sim at RV1 = 0).', lab=(-2.54, 0, 'right'))
RV1 = part('RV1', 'Device:R_Potentiometer_Trim', '500R BIAS', XS, 172.72, fp=FP_TRIM, mpn='3296W-1-501LF (stocked generic 500R multi-turn)',
           mfr='Bourns / generic', stock='IN STOCK (inv 532)', rating='multi-turn cermet', desc='Bias (quiescent current) trim',
           notes='Rheostat in base-emitter leg: MORE resistance = LESS bias; open wiper = full 500R = minimum bias (safe). Set to 500R before first power.',
           spice={'1': 'X9', '3': 'VBN', '2': 'VBN'}, lab=(-2.54, 0, 'right'))
W((XS, YBP), R18['1']); W(R18['2'], (XS, Y0), Q9['B']); W((XS, Y0), R19['1']); W(R19['2'], RV1['1'])
W(RV1['3'], (XS, YBN)); W(RV1['2'], (RV1['2'][0], YBN))
W(Q9['C'], (Q9['C'][0], YBP)); W(Q9['E'], (Q9['E'][0], YBN))
C7 = part('C7', 'Device:C', '1u FILM', 233.68, Y0, fp=FP_R82_1U, mpn='R82DC4100AA60J', mfr='KEMET', rating='63V PET', stock='IN STOCK (inv 132)',
          notes='Ties both driver bases together at AF/HF.', spice={'1': 'VBP', '2': 'VBN'}, desc='Film capacitor', lab=(2.54, 0, 'left'))
W(C7['1'], (233.68, YBP)); W(C7['2'], (233.68, YBN))
XR20 = 251.46
W((Q7['C'][0], YBP), (XR20 - 3.81, YBP)); W((Q8['C'][0], YBN), (XR20 - 3.81, YBN))

# ---------------- output stage
block('CFP OUTPUT STAGE', 242.57, TOP, 302.26, BOT)
text('Q10-Q13 on the main heatsink, insulated.', 243.84, 66.04, 1.27)
text('Q12/Q13 tabs are EP/EN, not a rail.', 243.84, 68.58, 1.27)
R20 = R('R20', '51R', XR20, YBP, 90, 'VBP', 'B10', LR1('51R'), 'IN STOCK (inv 292)', notes='Driver base stopper, at Q10 base.', lab=(0, -3.3, None))
Q10 = part('Q10', 'Transistor_BJT:Q_NPN_ECB', 'BD139', 262.89, YBP, fp=FP_TO126, mpn='BD139', mfr='STMicroelectronics', ds=DS['BD139'],
           rating='80V 1.5A 12.5W', stock='IN STOCK (inv 148)', notes='CFP driver, ~0.17 W. Mount on main heatsink (insulated) next to Q9. Pins 1E 2C 3B.',
           spice={'1': 'EP', '2': 'BOP', '3': 'B10'}, lab=(5.08, 3.81, 'left'))
W(R20['2'], Q10['B'])
Q12 = part('Q12', 'Transistor_BJT:Q_PNP_BCE', '2SA1941', 281.94, 88.9, 0, 'x', fp=FP_TO3P, mpn='2SA1941-O (R or O rank)', mfr='Toshiba', ds=DS['A1941'],
           rating='-140V -10A 100W(Tc25), Rth(j-c) 1.25K/W', stock='IN STOCK (inv 147, 19 pcs)',
           notes='Upper output. Emitter to +V; collector/tab = EP node. Insulate from heatsink. Pins 1B 2C 3E.',
           spice={'1': 'BOP', '2': 'EP', '3': 'VP'}, lab=(5.08, 0, 'left'))
XO = Q12['C'][0]
W(Q10['C'], (Q10['C'][0], 88.9), Q12['B'])
R21 = R('R21', '100R', 271.78, 81.28, 0, 'VP', 'BOP', LR1('100R'), 'IN STOCK (inv 150)', notes='Output base-emitter resistor (CFP turn-off / driver current).',
        lab=(-2.54, 0, 'right'))
W(R21['2'], (271.78, 88.9)); pwr('+V', R21['1'])
W(Q12['E'], (XO, 77.47)); pwr('+V', (XO, 77.47))
YEP = 111.76
W(Q12['C'], (XO, YEP)); W(Q10['E'], (Q10['E'][0], YEP), (XO, YEP))
R22 = R('R22', '0R33 / 5W', XO, 123.19, 0, 'EP', 'OUT', 'SQP500JB-0R33', 'IN STOCK (inv 289, 23 pcs)', mfr='Yageo', fp=FP_RPWR,
        rating='5W 5% cement', notes='CFP emitter/sense resistor. Iq = V(TP5 - TP4) / 0.33 (231 mV at 0.70 A).', lab=(2.54, 0, 'left'))
W((XO, YEP), R22['1']); W(R22['2'], (XO, Y0))
TP5 = part('TP5', 'Connector:TestPoint', 'EP (Iq)', 292.1, 114.3, 0, fp=FP_TP, mpn='5003', mfr='Keystone', stock='BUY', desc='Test point, orange',
           spice={'1': 'EP'}, lab=(1.27, -3.81, 'left'))
W((XO, 114.3), TP5['1'])
# lower
R23 = R('R23', '51R', XR20, YBN, 90, 'VBN', 'B11', LR1('51R'), 'IN STOCK (inv 292)', notes='Driver base stopper, at Q11 base.', lab=(0, 3.3, None))
Q11 = part('Q11', 'Transistor_BJT:Q_PNP_ECB', 'BD140', 262.89, YBN, 0, 'x', fp=FP_TO126, mpn='BD140', mfr='STMicroelectronics', ds=DS['BD139'],
           rating='-80V -1.5A 12.5W', stock='IN STOCK (inv 149)', notes='CFP driver. Mount on main heatsink (insulated) next to Q9. Pins 1E 2C 3B.',
           spice={'1': 'EN', '2': 'BON', '3': 'B11'}, lab=(5.08, -3.81, 'left'))
W(R23['2'], Q11['B'])
Q13 = part('Q13', 'Transistor_BJT:Q_NPN_BCE', '2SC5198', 281.94, M(88.9), fp=FP_TO3P, mpn='2SC5198-O (R or O rank)', mfr='Toshiba', ds=DS['C5198'],
           rating='140V 10A 100W(Tc25), Rth(j-c) 1.25K/W', stock='IN STOCK (inv 141, 20 pcs)',
           notes='Lower output. Emitter to -V; collector/tab = EN node. Insulate from heatsink. Pins 1B 2C 3E.',
           spice={'1': 'BON', '2': 'EN', '3': 'VN'}, lab=(5.08, 0, 'left'))
W(Q11['C'], (Q11['C'][0], M(88.9)), Q13['B'])
R24 = R('R24', '100R', 271.78, M(81.28), 0, 'BON', 'VN', LR1('100R'), 'IN STOCK (inv 150)', notes='Output base-emitter resistor.', lab=(-2.54, 0, 'right'))
W(R24['1'], (271.78, M(88.9))); pwr('-V', R24['2'])
W(Q13['E'], (XO, M(77.47))); pwr('-V', (XO, M(77.47)))
YEN = M(YEP)
W(Q13['C'], (XO, YEN)); W(Q11['E'], (Q11['E'][0], YEN), (XO, YEN))
R25 = R('R25', '0R33 / 5W', XO, M(123.19), 0, 'OUT', 'EN', 'SQP500JB-0R33', 'IN STOCK (inv 289)', mfr='Yageo', fp=FP_RPWR,
        rating='5W 5% cement', notes='Iq = V(TP4 - TP6) / 0.33.', lab=(2.54, 0, 'left'))
W(R25['2'], (XO, YEN)); W((XO, Y0), R25['1'])
TP6 = part('TP6', 'Connector:TestPoint', 'EN (Iq)', 292.1, M(114.3), 180, fp=FP_TP, mpn='5003', mfr='Keystone', stock='BUY', desc='Test point, orange',
           spice={'1': 'EN'}, lab=(1.27, 3.81, 'left'))
W((XO, M(114.3)), TP6['1'])

# ---------------- output network
block('OUTPUT NETWORK / SPEAKER', 303.53, 130.81, 368.3, 184.15)
TP4 = part('TP4', 'Connector:TestPoint', 'OUT (offset)', 292.1, Y0, 180, fp=FP_TP, mpn='5002', mfr='Keystone', stock='BUY', desc='Test point, white',
           spice={'1': 'OUT'}, lab=(1.27, 3.81, 'left'))
XZ, XSPL, XJN = 309.88, 320.04, 340.36
W((XO, Y0), (XSPL, Y0)); label('OUT', (300.99, Y0))
R28 = R('R28', '10R / 2W', XZ, 156.21, 0, 'OUT', 'ZB', 'RSMF2JT10R0', 'ON ORDER (inv 707, 25 incoming)', mfr='Stackpole', fp=FP_R2W,
        rating='2W 5% metal oxide (non-inductive)', notes='Zobel. Do not substitute wirewound.', lab=(2.54, 0, 'left'))
C10 = part('C10', 'Device:C', '100n FILM', XZ, 167.64, fp=FP_R82, mpn='R82DC3100DQ50J', mfr='KEMET', rating='63V PET', stock='IN STOCK (inv 406)',
           notes='Zobel capacitor; GND return to output/speaker ground.', spice={'1': 'ZB', '2': '0'}, desc='Film capacitor', lab=(2.54, 0, 'left'))
W((XZ, Y0), R28['1']); W(R28['2'], C10['1'])
TP7 = part('TP7', 'Connector:TestPoint', 'GND', 322.58, 175.26, 0, fp=FP_TP, mpn='5001', mfr='Keystone', stock='BUY', desc='Test point, black',
           spice={'1': '0'}, lab=(1.27, -3.81, 'left'))
W(C10['2'], (XZ, 175.26), TP7['1']); pwr('GND', (XZ, 175.26))
L1 = part('L1', 'Device:L', '1u5 AIR', 330.2, Y0, 90, fp='Inductor_THT:L_Axial_L14.5mm_D5.8mm_P20.32mm_Horizontal_Fastron_HBCC',
          mpn='Self-wound: 17 turns 1.0 mm enamelled Cu, 10 mm former (~1.5 uH)', mfr='', stock='MAKE',
          notes='Output isolation coil; required for capacitive-load stability (sim: 1.9 MHz oscillation into 100 nF without it). Footprint is a placeholder: match the coil at layout.',
          spice={'1': 'OUT', '2': 'SPK'}, desc='Air-core inductor', lab=(0, 3.3, None))
R29 = R('R29', '2R7 / 1W', 330.2, 140.97, 90, 'OUT', 'SPK', 'RR01J2R7TB', 'IN STOCK (inv 499, 5 pcs)', rating='1W 5% metal film',
        notes='Coil damping resistor.', lab=(0, -3.3, None))
W((XSPL, Y0), L1['1']); W((XSPL, Y0), (XSPL, 140.97), R29['1'])
W(L1['2'], (XJN, Y0)); W(R29['2'], (XJN, 140.97), (XJN, Y0))
J3 = part('J3', 'Connector_Generic:Conn_01x02', 'SPEAKER', 360.68, Y0, fp='Connector_Molex:Molex_KK-396_A-41791-0002_1x02_P3.96mm_Vertical',
          mpn='09-65-2028', mfr='Molex', stock='IN STOCK (inv 722, 16 pcs)', desc='KK-396 2-way header, 7 A per contact',
          notes='1 = SPK+ (amplifier output), 2 = speaker return to GND. External speaker protection goes in series here.',
          spice={'1': 'SPK', '2': '0'}, lab=(2.54, -3.81, 'left'))
W((XJN, Y0), J3['1']); label('SPK+', (345.44, Y0))
W(J3['2'], (350.52, J3['2'][1]), (350.52, J3['2'][1] + 5.08)); pwr('GND', (350.52, J3['2'][1] + 5.08))

# ---------------- notes
text('ClassA2 Rev A - Hiraga-inspired complementary Class-A amplifier, ONE MONO CHANNEL (build two boards).', 15.24, 241.3, 1.6, True)
NOTES = [
    'Topology: complementary LTP input (Q1/Q2, Q3/Q4) -> push-pull VAS (Q7/Q8, Miller C5/C6) -> VBE multiplier Q9 -> complementary-feedback-pair output (Q10+Q12, Q11+Q13).',
    'Rails: external +V/-V ~ +/-15.6 V loaded (12-0-12 VAC 100 VA, 216-253 V mains: ~14.1 V valley to 20.3 V no-load). +VF/-VF = front-end rails via R3/C3, R4/C4.',
    'Bias: target 0.70 A per channel when warm = 231 mV across R22 (TP5-TP4) and R25 (TP4-TP6). Class A to ~7.5 W into 8 ohm; class AB above.',
    'Power-up: RV1 at maximum resistance (500R = minimum bias), current-limited supply, 8 ohm dummy load. Raise bias slowly. RV2 centred.',
    'Heatsink: Q9, Q10, Q11, Q12, Q13 on one insulated heatsink per channel, <=1.2 K/W (about 22 W per channel at idle). Q12/Q13 tabs are at EP/EN, NOT at a rail.',
    'Ground: one GND net. Return C9, R1, C2 and J1 screen to the input-ground point, C10/J3/C11-C14 to the power-ground point; join them at J2 pin 2.',
    'No output short-circuit protection. Speaker protection (relay, DC detect, turn-on delay >= 3 s) is external, between J3 and the speaker.',
    'Small C0G caps (C2, C5, C6, C8) use stocked 2012-metric SMD parts; through-hole C0G is a drop-in alternative at layout.',
]
for i, s in enumerate(NOTES):
    text('- ' + s, 15.24, 246.38 + i*3.81, 1.27)

# ================================================================== serialise
def junctions():
    pts = {}
    for a, b in WIRES:
        for p in (a, b): pts[p] = pts.get(p, 0) + 1
    for r, d in PARTS.items():
        for n, p in d['pins'].items():
            if n.isdigit(): pts[p] = pts.get(p, 0) + 1
    for _, p in PWRS: pts[p] = pts.get(p, 0) + 1
    J = set(p for p, n in pts.items() if n >= 3)
    for a, b in WIRES:          # T-junctions: an endpoint lying inside another segment
        for p in list(pts):
            if p in (a, b): continue
            if (a[0] == b[0] == p[0] and min(a[1], b[1]) < p[1] < max(a[1], b[1])) or \
               (a[1] == b[1] == p[1] and min(a[0], b[0]) < p[0] < max(a[0], b[0])):
                J.add(p)
    return J

def write():
    out = [f'(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0") (uuid {q(ROOT_UUID)}) (paper "A3")',
           '(title_block (title "ClassA2 - Hiraga-inspired Class-A amplifier, mono channel") (date "2026-10-26") (rev "A (schematic review)")'
           ' (company "Schematic only - not released for PCB") (comment 1 "Simulated with author-approximate BJT models; not bench verified")'
           ' (comment 2 "Generated by tools/build_schematic.py - rerun overwrites manual edits"))',
           '(lib_symbols ' + ' '.join(SYMS[k][0] for k in sorted(SYMS)) + ')']
    for i, (a, b) in enumerate(WIRES):
        out.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {q(U(f"w{i}{a}{b}"))}))')
    for p in sorted(junctions()):
        out.append(f'(junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid {q(U(f"j{p}"))}))')
    for name, p, ang, just in LABELS:
        out.append(f'(label {q(name)} (at {p[0]} {p[1]} {ang}) (effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid {q(U(f"l{name}{p}"))}))')
    for s, x, y, size, bold in TEXTS:
        out.append(f'(text {q(s)} (exclude_from_sim yes) (at {x} {y} 0) (effects (font (size {size} {size}) {"(bold yes)" if bold else ""}) (justify left top)) (uuid {q(U(f"t{s}{x}{y}"))}))')
    for i, (x1, y1, x2, y2) in enumerate(RECTS):
        out.append(f'(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width 0.254) (type dash) (color 72 72 72 1)) (fill (type none)) (uuid {q(U(f"r{i}"))}))')
    out += ITEMS
    out.append('(sheet_instances (path "/" (page "1"))) (embedded_fonts no))')
    (ROOT / f'{PROJ}.kicad_sch').write_text('\n'.join(out) + '\n')
    # project symbol library (power rails) and library tables
    (ROOT / f'{PROJ}.kicad_sym').write_text('(kicad_symbol_lib (version 20251024) (generator "build_schematic.py")\n' +
                                           '\n'.join(PROJSYM[k] for k in sorted(PROJSYM)) + '\n)\n')
    (ROOT / 'sym-lib-table').write_text(f'(sym_lib_table (version 7)\n  (lib (name "{PROJ}")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJ}.kicad_sym")(options "")(descr "ClassA2 power rail symbols"))\n)\n')
    (ROOT / 'fp-lib-table').write_text(f'(fp_lib_table (version 7)\n  (lib (name "{PROJ}")(type "KiCad")(uri "${{KIPRJMOD}}/{PROJ}.pretty")(options "")(descr "ClassA2 inventory footprints"))\n)\n')
    pretty = ROOT / f'{PROJ}.pretty'; pretty.mkdir(exist_ok=True)
    src = ROOT.parent / 'ClassA' / 'ClassA_Inventory.pretty'
    for f in ['Yageo_SQP500_L22.0mm_W9.5mm_P30.48mm.kicad_mod', 'Multicomp_MC34629_1x02_P2.54mm.kicad_mod']:
        shutil.copyfile(src / f, pretty / f)
    # parts table for BOM / verification
    (ROOT / 'tools' / 'parts.json').write_text(json.dumps({r: {k: v for k, v in d.items() if k != 'pins'} for r, d in PARTS.items()}, indent=1))

if __name__ == '__main__':
    write()
    print(len(PARTS), 'parts,', len(WIRES), 'wires,', len(PWRS), 'power symbols')
