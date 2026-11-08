#!/usr/bin/env python3
"""Generate KiCad 10 symbol, footprints and STEP model for the ESS ES9033Q.

Source: ESS ES9033 Product Datasheet v0.4.0 (Aug 2024)
  - Pinout: Figure 2 (p.8), Table 1 (p.9-10)
  - Package: Figure 19 (p.93), 28-QFN 5x5 mm, e=0.5, b=0.18/0.23/0.30,
    L=0.45/0.55/0.65, D2=E2=3.00/3.15/3.25, A=0.70/0.75/0.80, A3=0.2 ref
  - Pin 29 = exposed pad, "not electrically connected, used for heat
    dissipation"; reference schematics (p.91/92) tie EPAD to GND.
"""
import os, sys, uuid

OUT = sys.argv[1]
LIB = "ESS"
FP_NAME = "ESS_QFN-28-1EP_5x5mm_P0.5mm_EP3.15x3.15mm"
DS_URL = "https://www.esstech.com/wp-content/uploads/2024/08/ES9033_DS_v0.4.0.pdf"
MODEL = f"${{KIPRJMOD}}/{LIB}.3dshapes/{FP_NAME}.step"

def u():
    return str(uuid.uuid4())

# ---------------------------------------------------------------- symbol
# (number, name, etype, side, position)
# Electrical types follow datasheet Table 1 pin types.
PINS = [
    # left: serial audio + control
    (26, "MCLK/GPIO",            "bidirectional", "L", 15.24),
    (25, "DATA_CLK",             "input",         "L", 12.70),
    (24, "DATA1",                "bidirectional", "L", 10.16),
    (23, "DATA2",                "bidirectional", "L", 7.62),
    (2,  "CHIP_EN",              "bidirectional", "L", 2.54),
    (3,  "MODE",                 "bidirectional", "L", 0.00),
    (21, "SCLK/SCL/HW1",         "bidirectional", "L", -5.08),
    (22, "MOSI/SDA/HW0",         "bidirectional", "L", -7.62),
    (20, "MISO/ADDR0/MUTE_CTRL", "bidirectional", "L", -10.16),
    (19, "SS/ADDR1/HW2",         "bidirectional", "L", -12.70),
    (18, "RT1",                  "input",         "L", -17.78),
    # right: outputs, charge pump, internal regulator / reference pins
    (6,  "OUT1",                 "output",        "R", 15.24),
    (7,  "GND_SNS",              "input",         "R", 12.70),
    (8,  "OUT2",                 "output",        "R", 10.16),
    (16, "C1",                   "passive",       "R", 5.08),
    (15, "C2",                   "passive",       "R", 2.54),
    (14, "PNEG",                 "power_out",     "R", -2.54),
    (12, "BG_VREF",              "passive",       "R", -7.62),
    (10, "AVCC",                 "power_out",     "R", -12.70),
    (28, "DVDD",                 "power_out",     "R", -15.24),
    # top: supplies
    (1,  "AVDD",                 "power_in",      "T", -7.62),
    (4,  "VCCA",                 "power_in",      "T", -2.54),
    (9,  "AVCC_3V3",             "power_in",      "T", 2.54),
    (17, "AVCC_CP",              "power_in",      "T", 7.62),
    # bottom: grounds + EP
    (5,  "DGND",                 "power_in",      "B", -7.62),
    (27, "DGND",                 "power_in",      "B", -5.08),
    (11, "AGND",                 "power_in",      "B", 0.00),
    (13, "AGND_CP",              "power_in",      "B", 5.08),
    (29, "EP",                   "passive",       "B", 10.16),
]
assert sorted(p[0] for p in PINS) == list(range(1, 30))

BX, BYT, BYB, PL = 20.32, 22.86, -22.86, 2.54

def font(hide=False, justify=None):
    j = f"\n\t\t\t\t\t(justify {justify})" if justify else ""
    h = "\n\t\t\t\t(hide yes)" if hide else ""
    return h, j

def prop(name, val, x, y, hide=False, justify=None, rot=0):
    j = f"\n\t\t\t\t(justify {justify})" if justify else ""
    h = "\n\t\t\t(hide yes)" if hide else ""
    return f"""\t\t(property "{name}" "{val}"
\t\t\t(at {x} {y} {rot})
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no){h}
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t){j}
\t\t\t)
\t\t)
"""

def pin(num, name, et, side, pos):
    if side == "L":
        x, y, r = -BX - PL, pos, 0
    elif side == "R":
        x, y, r = BX + PL, pos, 180
    elif side == "T":
        x, y, r = pos, BYT + PL, 270
    else:
        x, y, r = pos, BYB - PL, 90
    return f"""\t\t\t(pin {et} line
\t\t\t\t(at {x:g} {y:g} {r})
\t\t\t\t(length {PL})
\t\t\t\t(name "{name}"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "{num}"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
"""

sym = f"""(kicad_symbol_lib
\t(version 20251024)
\t(generator "claude_es9033q_gen")
\t(generator_version "10.0")
\t(symbol "ES9033Q"
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(duplicate_pin_numbers_are_jumpers no)
"""
sym += prop("Reference", "U", -BX, BYT + 3.81, justify="left")
sym += prop("Value", "ES9033Q", -BX, BYT + 1.27 + 0.0, justify="left")
sym += prop("Footprint", f"{LIB}:{FP_NAME}", 0, BYB - 6.35, hide=True)
sym += prop("Datasheet", DS_URL, 0, 0, hide=True)
sym += prop("Description", "ESS SABRE 32-bit stereo DAC with integrated 2Vrms line drivers and charge pump, I2C/SPI/hardware mode, QFN-28 5x5mm 0.5mm pitch, EP not electrically connected (tie to GND per ESS reference design)", 0, 0, hide=True)
sym += prop("ki_keywords", "audio DAC stereo 32bit I2S TDM DSD line driver ESS Sabre", 0, 0, hide=True)
sym += prop("ki_fp_filters", "*QFN*28*1EP*5x5mm*P0.5mm*", 0, 0, hide=True)
sym += prop("Manufacturer", "ESS Technology", 0, 0, hide=True)
sym += prop("MPN", "ES9033Q", 0, 0, hide=True)
sym += f"""\t\t(symbol "ES9033Q_0_1"
\t\t\t(rectangle
\t\t\t\t(start {-BX} {BYT})
\t\t\t\t(end {BX} {BYB})
\t\t\t\t(stroke
\t\t\t\t\t(width 0.254)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type background)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(symbol "ES9033Q_1_1"
"""
for p in PINS:
    sym += pin(*p)
sym += """\t\t)
\t\t(embedded_fonts no)
\t)
)
"""
with open(os.path.join(OUT, f"{LIB}.kicad_sym"), "w") as f:
    f.write(sym)

# ---------------------------------------------------------------- footprint
# Land pattern (no ESS recommendation published): pads sized like the KiCad
# generator's QFN-28 5x5 0.5mm patterns, adjusted to ESS lead dims.
#   lead: b 0.23 nom, L 0.55 nom -> inner lead edge 1.95 nom (1.85 @ Lmax)
#   pad:  0.25 x 0.95, from 1.90 to 2.85 from centre (0.35 toe beyond body)
#   EP:   3.15 x 3.15 copper (package nominal), paste 4 x 1.2 mm (~58 %)
#   pad-to-EP gap = 1.90 - 1.575 = 0.325 mm
P, PW, PIN_IN, PIN_OUT = 0.5, 0.25, 1.90, 2.85
PCX = (PIN_IN + PIN_OUT) / 2
PLEN = PIN_OUT - PIN_IN
EP = 3.15
BODY = 5.0
CRT = 3.10  # courtyard half-size (pad edge 2.85 + 0.25)

def pad_positions():
    out = []
    for i in range(7):  # pins 1-7 left, top->bottom
        out.append((1 + i, -PCX, -1.5 + i * P, PLEN, PW))
    for i in range(7):  # pins 8-14 bottom, left->right
        out.append((8 + i, -1.5 + i * P, PCX, PW, PLEN))
    for i in range(7):  # pins 15-21 right, bottom->top
        out.append((15 + i, PCX, 1.5 - i * P, PLEN, PW))
    for i in range(7):  # pins 22-28 top, right->left
        out.append((22 + i, 1.5 - i * P, -PCX, PW, PLEN))
    return out

def line(x1, y1, x2, y2, layer, w):
    return f"""\t(fp_line
\t\t(start {x1:g} {y1:g})
\t\t(end {x2:g} {y2:g})
\t\t(stroke
\t\t\t(width {w})
\t\t\t(type solid)
\t\t)
\t\t(layer "{layer}")
\t\t(uuid "{u()}")
\t)
"""

def fp_text_prop(name, val, x, y, layer, hide=False, size=1.0, th=0.15):
    h = "\n\t\t(hide yes)" if hide else ""
    return f"""\t(property "{name}" "{val}"
\t\t(at {x:g} {y:g} 0)
\t\t(layer "{layer}"){h}
\t\t(uuid "{u()}")
\t\t(effects
\t\t\t(font
\t\t\t\t(size {size} {size})
\t\t\t\t(thickness {th})
\t\t\t)
\t\t)
\t)
"""

def make_fp(vias):
    name = FP_NAME + ("_ThermalVias" if vias else "")
    s = f"""(footprint "{name}"
\t(version 20260206)
\t(generator "claude_es9033q_gen")
\t(layer "F.Cu")
\t(descr "ESS ES9033Q QFN-28 5x5mm, 0.5mm pitch, EP 3.15x3.15mm (pin 29, not electrically connected, tie to GND){' with 3x3 0.3mm thermal vias' if vias else ''}; package per ES9033 datasheet v0.4.0 Fig.19 ({DS_URL})")
\t(tags "QFN NoLead ES9033 ES9033Q ESS")
"""
    s += fp_text_prop("Reference", "REF**", 0, -3.9, "F.SilkS")
    s += fp_text_prop("Value", name, 0, 3.9, "F.Fab")
    s += fp_text_prop("Datasheet", DS_URL, 0, 0, "F.Fab", hide=True)
    s += fp_text_prop("Description", "ESS ES9033Q QFN-28 5x5mm P0.5mm EP3.15mm", 0, 0, "F.Fab", hide=True)
    s += "\t(attr smd)\n\t(duplicate_pad_numbers_are_jumpers no)\n"
    # silkscreen corner marks (body 2.5 + 0.11), keep 0.2 clear of pads
    sk = 2.61
    se = 1.625 + 0.2 + 0.06  # end of corner mark
    for sx in (-1, 1):
        for sy in (-1, 1):
            if sx == -1 and sy == -1:
                # pin-1 corner: only the top-side tick, plus a marker
                s += line(-sk, -sk, -se, -sk, "F.SilkS", 0.12)
                continue
            s += line(sx * sk, sy * sk, sx * se, sy * sk, "F.SilkS", 0.12)
            s += line(sx * sk, sy * sk, sx * sk, sy * se, "F.SilkS", 0.12)
    # pin-1 triangle on silk, outside pad row
    s += f"""\t(fp_poly
\t\t(pts
\t\t\t(xy -3.1 -1.5) (xy -3.4 -1.74) (xy -3.4 -1.26) (xy -3.1 -1.5)
\t\t)
\t\t(stroke
\t\t\t(width 0.12)
\t\t\t(type solid)
\t\t)
\t\t(fill yes)
\t\t(layer "F.SilkS")
\t\t(uuid "{u()}")
\t)
"""
    # fab outline with 1mm pin-1 chamfer
    b, c = BODY / 2, 1.0
    pts = [(-b + c, -b), (b, -b), (b, b), (-b, b), (-b, -b + c), (-b + c, -b)]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        s += line(x1, y1, x2, y2, "F.Fab", 0.1)
    # courtyard
    s += f"""\t(fp_rect
\t\t(start {-CRT} {-CRT})
\t\t(end {CRT} {CRT})
\t\t(stroke
\t\t\t(width 0.05)
\t\t\t(type solid)
\t\t)
\t\t(fill no)
\t\t(layer "F.CrtYd")
\t\t(uuid "{u()}")
\t)
"""
    s += f"""\t(fp_text user "${{REFERENCE}}"
\t\t(at 0 0 0)
\t\t(layer "F.Fab")
\t\t(uuid "{u()}")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1 1)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
"""
    # signal pads
    for n, x, y, w, h in pad_positions():
        s += f"""\t(pad "{n}" smd roundrect
\t\t(at {x:g} {y:g})
\t\t(size {w:g} {h:g})
\t\t(layers "F.Cu" "F.Mask" "F.Paste")
\t\t(roundrect_rratio 0.25)
\t\t(uuid "{u()}")
\t)
"""
    # exposed pad copper + mask, separate paste windows
    s += f"""\t(pad "29" smd rect
\t\t(at 0 0)
\t\t(size {EP} {EP})
\t\t(property pad_prop_heatsink)
\t\t(layers "F.Cu" "F.Mask")
\t\t(zone_connect 2)
\t\t(uuid "{u()}")
\t)
"""
    for px in (-0.75, 0.75):
        for py in (-0.75, 0.75):
            s += f"""\t(pad "" smd roundrect
\t\t(at {px:g} {py:g})
\t\t(size 1.2 1.2)
\t\t(layers "F.Paste")
\t\t(roundrect_rratio 0.2)
\t\t(uuid "{u()}")
\t)
"""
    if vias:
        for vx in (-1.0, 0.0, 1.0):
            for vy in (-1.0, 0.0, 1.0):
                s += f"""\t(pad "29" thru_hole circle
\t\t(at {vx:g} {vy:g})
\t\t(size 0.6 0.6)
\t\t(drill 0.3)
\t\t(property pad_prop_heatsink)
\t\t(layers "*.Cu")
\t\t(remove_unused_layers no)
\t\t(zone_connect 2)
\t\t(uuid "{u()}")
\t)
"""
        s += f"""\t(pad "29" smd rect
\t\t(at 0 0)
\t\t(size {EP} {EP})
\t\t(property pad_prop_heatsink)
\t\t(layers "B.Cu")
\t\t(zone_connect 2)
\t\t(uuid "{u()}")
\t)
"""
    s += f"""\t(embedded_fonts no)
\t(model "{MODEL}"
\t\t(offset
\t\t\t(xyz 0 0 0)
\t\t)
\t\t(scale
\t\t\t(xyz 1 1 1)
\t\t)
\t\t(rotate
\t\t\t(xyz 0 0 0)
\t\t)
\t)
)
"""
    d = os.path.join(OUT, f"{LIB}.pretty")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name + ".kicad_mod"), "w") as f:
        f.write(s)

make_fp(False)
make_fp(True)

# ---------------------------------------------------------------- STEP
# Simple AP214 B-rep of axis-aligned boxes, coloured.
# KiCad 3D coordinates: +X right, +Y up (PCB Y is flipped), +Z out of board.
class Step:
    def __init__(self):
        self.lines, self.n = [], 0
    def add(self, txt):
        self.n += 1
        self.lines.append(f"#{self.n}={txt};")
        return f"#{self.n}"

def box_solid(st, name, x0, y0, z0, x1, y1, z1):
    P = {}
    for i, x in enumerate((x0, x1)):
        for j, y in enumerate((y0, y1)):
            for k, z in enumerate((z0, z1)):
                cp = st.add(f"CARTESIAN_POINT('',({x:.4f},{y:.4f},{z:.4f}))")
                P[(i, j, k)] = (st.add(f"VERTEX_POINT('',{cp})"), (x, y, z))
    edges = {}
    def edge(a, b):
        key = tuple(sorted((a, b)))
        if key in edges:
            e, s0 = edges[key]
            return e, (s0 == a)
        (va, pa), (vb, pb) = P[a], P[b]
        d = [pb[t] - pa[t] for t in range(3)]
        L = max(abs(v) for v in d)
        dn = [v / L for v in d]
        cp = st.add(f"CARTESIAN_POINT('',({pa[0]:.4f},{pa[1]:.4f},{pa[2]:.4f}))")
        dr = st.add(f"DIRECTION('',({dn[0]:.1f},{dn[1]:.1f},{dn[2]:.1f}))")
        vec = st.add(f"VECTOR('',{dr},{L:.4f})")
        ln = st.add(f"LINE('',{cp},{vec})")
        e = st.add(f"EDGE_CURVE('',{va},{vb},{ln},.T.)")
        edges[key] = (e, a)
        return e, True
    # faces: (corner loop CCW seen from outside, normal, ref dir)
    faces = [
        ([(0,0,0),(0,1,0),(1,1,0),(1,0,0)], (0,0,-1), (1,0,0), z0),  # bottom
        ([(0,0,1),(1,0,1),(1,1,1),(0,1,1)], (0,0,1),  (1,0,0), z1),  # top
        ([(0,0,0),(1,0,0),(1,0,1),(0,0,1)], (0,-1,0), (1,0,0), y0),  # front
        ([(0,1,0),(0,1,1),(1,1,1),(1,1,0)], (0,1,0),  (1,0,0), y1),  # back
        ([(0,0,0),(0,0,1),(0,1,1),(0,1,0)], (-1,0,0), (0,1,0), x0),  # left
        ([(1,0,0),(1,1,0),(1,1,1),(1,0,1)], (1,0,0),  (0,1,0), x1),  # right
    ]
    fids = []
    for loop, nrm, ref, _ in faces:
        oes = []
        for a, b in zip(loop, loop[1:] + loop[:1]):
            e, same = edge(a, b)
            oes.append(st.add(f"ORIENTED_EDGE('',*,*,{e},{'.T.' if same else '.F.'})"))
        el = st.add(f"EDGE_LOOP('',({','.join(oes)}))")
        fb = st.add(f"FACE_OUTER_BOUND('',{el},.T.)")
        p0 = P[loop[0]][1]
        cp = st.add(f"CARTESIAN_POINT('',({p0[0]:.4f},{p0[1]:.4f},{p0[2]:.4f}))")
        dn = st.add(f"DIRECTION('',({nrm[0]:.1f},{nrm[1]:.1f},{nrm[2]:.1f}))")
        dr = st.add(f"DIRECTION('',({ref[0]:.1f},{ref[1]:.1f},{ref[2]:.1f}))")
        ax = st.add(f"AXIS2_PLACEMENT_3D('',{cp},{dn},{dr})")
        pl = st.add(f"PLANE('',{ax})")
        fids.append(st.add(f"ADVANCED_FACE('',({fb}),{pl},.T.)"))
    sh = st.add(f"CLOSED_SHELL('',({','.join(fids)}))")
    return st.add(f"MANIFOLD_SOLID_BREP('{name}',{sh})")

st = Step()
solids = []  # (id, rgb)
A, A3, BH = 0.75, 0.2, BODY / 2
BODY_RGB, METAL_RGB, MARK_RGB = (0.15, 0.15, 0.17), (0.80, 0.80, 0.82), (0.75, 0.75, 0.75)
solids.append((box_solid(st, "body", -BH, -BH, 0.01, BH, BH, A), BODY_RGB))
# leads: b=0.23, L=0.55, thickness A3, flush with body sides (+5 um)
b2, Ll, ext = 0.23 / 2, 0.55, 0.005
for n, x, y, w, h in pad_positions():
    Y = -y  # PCB -> 3D Y flip
    if abs(x) > 1.8:   # left/right rows
        sx = 1 if x > 0 else -1
        xo, xi = sx * (BH + ext), sx * (BH - Ll)
        solids.append((box_solid(st, f"pin{n}", min(xo, xi), Y - b2, 0, max(xo, xi), Y + b2, A3), METAL_RGB))
    else:              # top/bottom rows
        sy = 1 if Y > 0 else -1
        yo, yi = sy * (BH + ext), sy * (BH - Ll)
        solids.append((box_solid(st, f"pin{n}", x - b2, min(yo, yi), 0, x + b2, max(yo, yi), A3), METAL_RGB))
e2 = 3.15 / 2
solids.append((box_solid(st, "epad", -e2, -e2, 0, e2, e2, A3), METAL_RGB))
# pin-1 mark on top surface (pin 1 at PCB top-left -> 3D (-x, +y))
solids.append((box_solid(st, "pin1_mark", -1.85, 1.35, A, -1.35, 1.85, A + 0.01), MARK_RGB))

# representation context + product structure
lu = st.add("( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) )")
au = st.add("( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) )")
su = st.add("( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() )")
unc = st.add(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),{lu},'distance_accuracy_value','confusion accuracy')")
ctx = st.add(f"( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({unc})) GLOBAL_UNIT_ASSIGNED_CONTEXT(({lu},{au},{su})) REPRESENTATION_CONTEXT('Context #1','3D Context with UNIT and UNCERTAINTY') )")
o = st.add("CARTESIAN_POINT('',(0.,0.,0.))")
dz = st.add("DIRECTION('',(0.,0.,1.))")
dx = st.add("DIRECTION('',(1.,0.,0.))")
ax0 = st.add(f"AXIS2_PLACEMENT_3D('',{o},{dz},{dx})")
sr = st.add(f"ADVANCED_BREP_SHAPE_REPRESENTATION('{FP_NAME}',({ax0},{','.join(s for s, _ in solids)}),{ctx})")
appctx = st.add("APPLICATION_CONTEXT('core data for automotive mechanical design processes')")
st.add(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,{appctx})")
pc = st.add(f"PRODUCT_CONTEXT('',{appctx},'mechanical')")
prod = st.add(f"PRODUCT('ES9033Q','ES9033Q','ESS ES9033Q QFN-28 5x5mm',({pc}))")
st.add(f"PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,({prod}))")
pdf = st.add(f"PRODUCT_DEFINITION_FORMATION('','',{prod})")
pdc = st.add(f"PRODUCT_DEFINITION_CONTEXT('part definition',{appctx},'design')")
pd = st.add(f"PRODUCT_DEFINITION('design','',{pdf},{pdc})")
pds = st.add(f"PRODUCT_DEFINITION_SHAPE('','',{pd})")
st.add(f"SHAPE_DEFINITION_REPRESENTATION({pds},{sr})")
# colours
styled = []
for sid, (r, g, bb) in solids:
    col = st.add(f"COLOUR_RGB('',{r:.3f},{g:.3f},{bb:.3f})")
    fac = st.add(f"FILL_AREA_STYLE_COLOUR('',{col})")
    fa = st.add(f"FILL_AREA_STYLE('',({fac}))")
    ssfa = st.add(f"SURFACE_STYLE_FILL_AREA({fa})")
    sss = st.add(f"SURFACE_SIDE_STYLE('',({ssfa}))")
    ssu = st.add(f"SURFACE_STYLE_USAGE(.BOTH.,{sss})")
    psa = st.add(f"PRESENTATION_STYLE_ASSIGNMENT(({ssu}))")
    styled.append(st.add(f"STYLED_ITEM('color',({psa}),{sid})"))
st.add(f"MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',({','.join(styled)}),{ctx})")

hdr = f"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ESS ES9033Q QFN-28 5x5mm simplified model'),'2;1');
FILE_NAME('{FP_NAME}.step','2026-11-06T00:00:00',(''),(''),'claude_es9033q_gen','','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN {{ 1 0 10303 214 1 1 1 1 }}'));
ENDSEC;
DATA;
"""
d3 = os.path.join(OUT, f"{LIB}.3dshapes")
os.makedirs(d3, exist_ok=True)
with open(os.path.join(d3, FP_NAME + ".step"), "w") as f:
    f.write(hdr + "\n".join(st.lines) + "\nENDSEC;\nEND-ISO-10303-21;\n")
print("ok")
