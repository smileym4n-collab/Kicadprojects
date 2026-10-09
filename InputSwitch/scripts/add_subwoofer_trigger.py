"""Scoped, reproducible addition from the preserved pre-change Control sheet.

Does not invoke the old full-project schematic generator.
"""
from schlib import *

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'review/subwoofer-2026-10-07'
SOURCE = OUT / 'source'
FP = 'InputSwitch:Relay_DPDT_Omron_G6K-2P-Y_Datasheet'


def identity(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'InputSwitch/subwoofer/' + name))


def top_spans(text):
    depth = 0
    quoted = escaped = False
    start = None
    for i, c in enumerate(text):
        if quoted:
            if escaped:
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == '"':
                quoted = False
            continue
        if c == '"':
            quoted = True
        elif c == '(':
            if depth == 1:
                start = i
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 1:
                yield start, i + 1, parse(text[start:i + 1])


src = (SOURCE / 'Control.kicad_sch').read_text()
t = parse(src)
root = parse((SOURCE / 'InputSwitch.kicad_sch').read_text())
added = []


def copy_symbol(sheet, ref, unit, newref, x, y, value=None, footprint=None):
    s = copy.deepcopy(next(s for s in kids(sheet, 'symbol')
                           if val(s, 'unit') == str(unit)
                           and next(p[2] for p in kids(s, 'property')
                                    if p[1] == 'Reference') == ref))
    at = child(s, 'at')
    dx, dy = x - float(at[1]), y - float(at[2])
    at[1:3] = [Atom(str(x)), Atom(str(y))]
    child(s, 'uuid')[1] = identity(newref + '/' + str(unit))
    for p in kids(s, 'property'):
        pa = child(p, 'at')
        pa[1:3] = [Atom(str(round(float(pa[1]) + dx, 4))),
                   Atom(str(round(float(pa[2]) + dy, 4)))]
        if p[1] == 'Reference': p[2] = newref
        if p[1] == 'Value' and value: p[2] = value
        if p[1] == 'Footprint' and footprint: p[2] = footprint
    for p in kids(s, 'pin'):
        child(p, 'uuid')[1] = identity(newref + '/pin/' + str(val(p, 'number')))
    inst = child(s, 'instances')
    project = child(inst, 'project')
    path = child(project, 'path')
    path[1] = '/6d54ed2e-2ae2-4573-a8b1-3b10bc28f7a1/dabaaf26-2532-5494-8858-09ead4931d51'
    child(path, 'reference')[1] = newref
    added.append(dump(s))
    return s


def item(body):
    added.append(body[:-1] + ' (uuid "' + identity(body) + '"))')


def wire(a, b):
    item(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)))')


def label(name, pos, angle=0):
    item(f'(global_label {json.dumps(name)} (shape bidirectional) (at {pos[0]} {pos[1]} {angle}) (effects (font (size 1.016 1.016)) (justify {"right" if angle == 180 else "left"})))')


def nc(pos):
    item(f'(no_connect (at {pos[0]} {pos[1]}))')


def text(value, pos, size=1.016):
    item(f'(text {json.dumps(value)} (at {pos[0]} {pos[1]} 0) (effects (font (size {size} {size})) (justify left top)))')


# K4 coil and contacts share the existing exact manufacturer pin numbers.
coil = copy_symbol(t, 'K1', 3, 'K4', 243.84, 185.42, 'G6K-2P-Y DC5', FP)
for prop in kids(coil, 'property'):
    if prop[1] in ['Reference', 'Value']:
        child(prop, 'at')[1:3] = [Atom('251.46'), Atom('185.42' if prop[1] == 'Reference' else '187.96')]
        effects = child(prop, 'effects')
        effects[:] = [e for e in effects if not (isinstance(e, list) and e[0] == 'justify')]
        effects.append([Atom('justify'), Atom('left')])
added[-1] = dump(coil)
copy_symbol(root, 'K1', 1, 'K4', 279.4, 172.72, 'G6K-2P-Y DC5', FP)
copy_symbol(root, 'K1', 2, 'K4', 279.4, 139.7, 'G6K-2P-Y DC5', FP)
copy_symbol(t, 'J10', 1, 'J13', 320.04, 172.72, 'SUB TRIGGER 12V')
copy_symbol(t, '#PWR30067', 1, '#PWR30991', 314.96, 182.88)

# U3 channel 4 is freed from its former grounded unused input.
wire((111.76, 193.04), (106.68, 193.04))
label('SOURCE_AV', (106.68, 193.04), 180)
wire((132.08, 193.04), (144.78, 193.04))
label('K4_LOW', (144.78, 193.04))
wire((243.84, 177.8), (243.84, 170.18))
label('+5V', (243.84, 170.18))
wire((243.84, 193.04), (243.84, 195.58))
label('K4_LOW', (243.84, 195.58))
nc((269.24, 170.18))  # NC A left open: REF gives no trigger.
wire((269.24, 175.26), (259.08, 175.26))
label('+12V', (259.08, 175.26), 180)  # Protected rail, after fuse/diode.
wire((289.56, 172.72), (314.96, 172.72))
item('(label "SUB_TRIGGER_12V" (at 292.1 172.72 0) (effects (font (size 0.8 0.8)) (justify left bottom)))')
wire((314.96, 175.26), (314.96, 182.88))
for pos in [(269.24, 137.16), (269.24, 142.24), (289.56, 139.7)]: nc(pos)
text('SUBWOOFER SOURCE TRIGGER', (231.14, 152.4), 1.27)
text('SOURCE_AV high: Marantz, relay ON, protected 12V at J13.1.\nLow/reset/unpowered: preamp, relay OFF, trigger disconnected.\nJ13.2 = control GND; connect only to sub J20.2 trigger return.\nSub J20.1 = positive; onboard 2k2/opto draws about 5mA.\nIsolation is at sub optocoupler; do not link to sub audio GND.', (231.14, 156.21))
text('Unused pole', (264.16, 147.32))

# Remove exactly two original objects, retaining every other original byte.
remove = {'1149bb9c-ec2c-4a74-a125-df7c12f18e99',
          'af680ba9-a9cb-40ef-bfa4-58dcbde2456b',
          'e933c68d-1879-4edf-b672-ba6d41527bbe'}
for a, b, n in reversed(list(top_spans(src))):
    if val(n, 'uuid') in remove:
        src = src[:a] + src[b:]
result = src[:src.rfind(')')] + '\n\t' + '\n\t'.join(added) + '\n)\n'
(ROOT / 'Control.kicad_sch').write_text(result)
print('Added K4, J13 and U3 channel 4; removed three obsolete unused-channel objects.')
