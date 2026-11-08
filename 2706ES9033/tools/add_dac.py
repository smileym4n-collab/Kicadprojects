#!/usr/bin/env python3
"""Add ES9033Q support circuit, DAC LDO, ATtiny412 control and line output
to 2706ES9033.kicad_sch.  Usage: add_dac.py <in.kicad_sch> <out.kicad_sch>"""
import re, sys, uuid

SRC, DST = sys.argv[1], sys.argv[2]
LIBDIR = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/"
ROOT_UUID = "38bf17a7-0851-4df1-8df7-1c8ac1c1974f"
PROJECT = "2706ES9033"
G = 1.27

def U():
    return str(uuid.uuid4())

def r2(v):
    return round(v / 0.01) * 0.01

def fmt(v):
    v = round(v, 4)
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s

sch = open(SRC).read()

# ------------------------------------------------------------ s-expr helpers
def match_paren(s, i):
    d, j = 0, i
    while j < len(s):
        c = s[j]
        if c == '"':
            j += 1
            while s[j] != '"':
                j += 2 if s[j] == '\\' else 1
        elif c == '(':
            d += 1
        elif c == ')':
            d -= 1
            if d == 0:
                return j
        j += 1
    raise ValueError

def lib_block(text, name):
    i = text.find(f'\n\t(symbol "{name}"\n') + 2
    assert i > 1, name
    return text[i:match_paren(text, i) + 1]

def top_children(block):
    """Return list of (start,end) for direct children of block."""
    out, i = [], block.find('(', 1)
    while i != -1 and i < len(block) - 1:
        j = match_paren(block, i)
        out.append((i, j + 1))
        i = block.find('(', j + 1)
    return out

def embed(libfile, name, prefix):
    text = open(LIBDIR + libfile).read()
    blk = lib_block(text, name)
    m = re.search(r'\(extends "([^"]+)"\)', blk)
    if m:
        parent = lib_block(text, m.group(1))
        child_props = [blk[a:b] for a, b in top_children(blk) if blk[a:].startswith('(property')]
        kids = top_children(parent)
        parts, first_prop = [], True
        for a, b in kids:
            seg = parent[a:b]
            if seg.startswith('(property'):
                if first_prop:
                    parts.extend(child_props)
                    first_prop = False
                continue
            parts.append(seg)
        pname = m.group(1)
        body = "\n\t\t".join(parts)
        body = body.replace(f'(symbol "{pname}_', f'(symbol "{name}_')
        blk = f'(symbol "{name}"\n\t\t' + body + '\n\t)'
    blk = blk.replace(f'(symbol "{name}"', f'(symbol "{prefix}:{name}"', 1)
    # indent one extra tab
    return "\n".join("\t" + ln for ln in blk.split("\n"))

def lib_pins(block_text):
    pins = {}
    for m in re.finditer(r'\(pin (\w+) \w+\s+\(at ([-\d.]+) ([-\d.]+) (\d+)\)\s+\(length [\d.]+\)(?:\s+\(hide yes\))?\s+\(name "([^"]*)".*?\(number "([^"]*)"', block_text, re.S):
        pins[m.group(6)] = (float(m.group(2)), float(m.group(3)))
    return pins

# ------------------------------------------------------------ lib symbols
needed = [
    ("Device.kicad_sym", "LED", "Device"),
    ("Device.kicad_sym", "NetTie_2", "Device"),
    ("Connector_Generic.kicad_sym", "Conn_01x03", "Connector_Generic"),
    ("power.kicad_sym", "PWR_FLAG", "power"),
    ("MCU_Microchip_ATtiny.kicad_sym", "ATtiny412-SS", "MCU_Microchip_ATtiny"),
]
li = sch.find("\t(lib_symbols")
le = match_paren(sch, li + 1)
libsec = sch[li:le + 1]
new_libs = []
for f, n, p in needed:
    if f'(symbol "{p}:{n}"' not in libsec:
        new_libs.append(embed(f, n, p))
sch = sch[:le] + "\n".join(new_libs) + "\n\t" + sch[le:]
li = sch.find("\t(lib_symbols"); le = match_paren(sch, li + 1)
libsec = sch[li:le + 1]

PIN_DB = {}
def pins_of(lib_id):
    if lib_id not in PIN_DB:
        i = libsec.find(f'(symbol "{lib_id}"')
        assert i >= 0, lib_id
        PIN_DB[lib_id] = lib_pins(libsec[i:match_paren(libsec, i) + 1])
    return PIN_DB[lib_id]

def xform(px, py, rot):
    if rot == 0:   return px, py
    if rot == 90:  return -py, px
    if rot == 180: return -px, -py
    if rot == 270: return py, -px
    raise ValueError

# ------------------------------------------------------------ model
syms, wires, labels, texts, ncs = [], [], [], [], []
PINPTS = {}          # (ref,pin) -> (x,y)
ALLPINPTS = []       # all new pin connection points

class Sym:
    def __init__(s, ref, lib_id, x, y, rot=0, value="", fp="", ds="", desc="",
                 extra=None, fields=None, hide_val=False, hide_ref=False):
        s.__dict__.update(locals()); del s.__dict__["s"]
        syms.append(s)
        for num, (px, py) in pins_of(lib_id).items():
            rx, ry = xform(px, py, rot)
            pt = (r2(x + rx), r2(y - ry))
            PINPTS[(ref, num)] = pt
            ALLPINPTS.append(pt)

def P(ref, pin):
    return PINPTS[(ref, pin)]

def W(*pts):
    pts = [(r2(a), r2(b)) for a, b in pts]
    for a, b in zip(pts, pts[1:]):
        if a != b:
            assert a[0] == b[0] or a[1] == b[1], (a, b)
            wires.append([a, b])

def L(name, x, y, ang=0):
    labels.append((name, r2(x), r2(y), ang))

def T(txt, x, y, size=1.27, bold=False, color=None):
    texts.append((txt, x, y, size, bold))

PWR_N = [30]
def gnd(x, y, rot=0):
    ref = f"#PWR{PWR_N[0]:03d}"; PWR_N[0] += 1
    Sym(ref, "power:GND", x, y, rot, "GND", hide_ref=True)

def pwrflag(x, y):
    ref = f"#FLG{PWR_N[0]:03d}"; PWR_N[0] += 1
    Sym(ref, "power:PWR_FLAG", x, y, 0, "PWR_FLAG", hide_ref=True)

# footprints / parts
FP_C1608 = "Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder"
FP_C2012 = "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder"
FP_C3216 = "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder"
FP_R2012 = "Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"
FP_KK3 = "Connector_Molex:Molex_KK-254_AE-6410-03A_1x03_P2.54mm_Vertical"

PART = {
    "100n":  ("100nF", FP_C1608, "MC0603B104K500CT", "Multicomp Pro", "100nF 50V X7R 1608", "STOCK"),
    "1u":    ("1uF", FP_C2012, "C0805C105K3RACTU", "KEMET", "1uF 25V X7R 2012", "STOCK"),
    "10u":   ("10uF", FP_C3216, "TMK316B7106KL-TD", "Taiyo Yuden", "10uF 25V X7R 3216", "STOCK"),
    "2u2":   ("2.2uF/10V", FP_C2012, "CL21B225KPFNNNE", "Samsung", "2.2uF 10V X7R 2012, charge-pump flying cap", "STOCK"),
    "4u7":   ("4.7uF", FP_C2012, "CL21A475KAQNNNE", "Samsung", "4.7uF 25V X5R 2012, BG_VREF", "STOCK"),
    "47u":   ("47uF/10V", FP_C3216, "CL31A476MPHNNNE", "Samsung", "47uF 10V X5R 3216, PNEG reservoir (ESS ref value)", "ORDER"),
    "2n2":   ("2.2nF C0G", FP_C2012, "GCM2165C2A222FA16D", "Murata", "2.2nF 100V C0G 1% 2012, output filter", "STOCK"),
    "300R":  ("300R", FP_R2012, "ERA-6AEB301V", "Panasonic", "300R 0.1% thin film 2012 (ESS ref: 300R thin film)", "ORDER"),
    "4k7":   ("4K7", FP_R2012, "RMCF0805FT4K70", "Stackpole", "4K7 1% thick film 2012", "STOCK"),
    "100k":  ("100K", FP_R2012, "RK73B2ATTE104J", "KOA Speer", "100K 5% thick film 2012", "STOCK"),
    "10k":   ("10K", FP_R2012, "RK73B2ATTD103J", "KOA Speer", "10K 5% thick film 2012", "STOCK"),
    "470R":  ("470R", FP_R2012, "ASC0805-470RFT5", "TT Electronics", "470R 1% thick film 2012", "STOCK"),
}

def RC(ref, kind, x, y, rot=0):
    val, fp, mpn, mfr, desc, src = PART[kind]
    lib = "Device:R" if kind[-1] in "Rk" and kind not in ("4k7x",) and not kind.endswith("u") and "n" not in kind else "Device:C"
    if kind in ("300R", "4k7", "100k", "10k", "470R"):
        lib = "Device:R"
    else:
        lib = "Device:C"
    Sym(ref, lib, x, y, rot, val, fp, "", desc,
        extra={"MPN": mpn, "Manufacturer": mfr, "Source": src})

# =========================================================== placement
X0, Y0 = 215.9, 228.6          # U2 (moved from 360.68,101.6)
Sym("U2", "ESS:ES9033Q", X0, Y0, 0, "ES9033Q")   # placeholder for pins only
syms.pop()                                         # U2 already exists; keep pins
RX, LX = X0 + 22.86, X0 - 22.86
TOPY, BOTY = Y0 - 25.4, Y0 + 25.4
RAIL = Y0 - 38.1

# ---------------- DAC LDO (IC4) ----------------
IX, IY = X0 - 71.12, RAIL - 2.54
Sym("IC4", "Custom:TPS7A2033PDBVR", IX, IY, 0, "TPS7A2033",
    "Custom:SOT95P280X145-5N", "https://www.ti.com/lit/ds/symlink/tps7a20.pdf",
    "300mA low-noise LDO, 3.3V fixed - ES9033Q + ATtiny rail",
    extra={"MPN": "TPS7A2033PDBVR", "Manufacturer": "Texas Instruments", "Source": "STOCK"})
inx, iny = P("IC4", "1")
W((inx, iny), (inx - 17.78, iny))
L("VIN", inx - 17.78, iny, 180)
RC("C20", "1u", inx - 12.7, iny + 3.81)
gnd(inx - 12.7, iny + 7.62)
enx, eny = P("IC4", "3")
W((enx, eny), (enx - 5.08, eny), (enx - 5.08, iny))
gx, gy = P("IC4", "2")
W((gx, gy), (gx - 7.62, gy), (gx - 7.62, gy + 7.62))
gnd(gx - 7.62, gy + 7.62)
ncs.append(P("IC4", "4"))
ox, oy = P("IC4", "5")
assert abs(oy - RAIL) < 0.01
T("DAC 3V3 LDO", IX - 2.54, IY - 17.78, 2.54, True)

# ---------------- 3V3_DAC rail + top-pin decoupling ----------------
top = {n: P("U2", n) for n in ("1", "4", "9", "17")}
rail_end = X0 + 48.26
W((ox, RAIL), (rail_end, RAIL))
L("3V3_DAC", ox + 2.54, RAIL)
for n, (px, py) in top.items():
    W((px, RAIL), (px, py))
RC("C21", "10u", X0 - 38.1, RAIL + 3.81); gnd(X0 - 38.1, RAIL + 7.62)
pwrflag(X0 - 22.86, RAIL)
RC("C22", "100n", X0 - 27.94, RAIL + 3.81); gnd(X0 - 27.94, RAIL + 7.62)    # AVDD pin 1
RC("C23", "1u", X0 - 17.78, RAIL + 3.81); gnd(X0 - 17.78, RAIL + 7.62)      # AVDD pin 1
RC("C24", "1u", X0 + 17.78, RAIL + 3.81); gnd(X0 + 17.78, RAIL + 7.62)      # VCCA pin 4
RC("C25", "1u", X0 + 27.94, RAIL + 3.81); gnd(X0 + 27.94, RAIL + 7.62)      # AVCC_3V3 pin 9
RC("C26", "100n", X0 + 38.1, RAIL + 3.81); gnd(X0 + 38.1, RAIL + 7.62)      # AVCC_CP pin 17
RC("C27", "1u", X0 + 48.26, RAIL + 3.81); gnd(X0 + 48.26, RAIL + 7.62)      # AVCC_CP pin 17
T("Place at pins: C22,C23 -> pin 1 AVDD;  C24 -> pin 4 VCCA;  C25 -> pin 9 AVCC_3V3;  C26,C27 -> pin 17 AVCC_CP",
  X0 - 30.48, RAIL - 8.89, 1.27)

# ---------------- U2 left side: I2S, control, straps ----------------
for n, net in (("26", "I2S_MCLK"), ("25", "I2S_BCK"), ("24", "I2S_LRCK"), ("23", "I2S_DATA"),
               ("2", "DAC_EN"), ("21", "I2C_SCL"), ("22", "I2C_SDA")):
    px, py = P("U2", n)
    W((px, py), (px - 5.08, py))
    L(net, px - 5.08, py, 180)
mx, my = P("U2", "3")                       # MODE -> GND = I2C mode
W((mx, my), (mx - 5.08, my)); gnd(mx - 5.08, my, 270)
bx = LX - 5.08
for n in ("20", "19", "18"):                # ADDR0, ADDR1 -> GND (0x90); RT1 -> GND
    px, py = P("U2", n)
    W((px, py), (bx, py))
W((bx, P("U2", "20")[1]), (bx, P("U2", "18")[1] + 2.54))
gnd(bx, P("U2", "18")[1] + 2.54)
T("U2 straps: MODE=GND -> I2C,  ADDR1/ADDR0=GND -> 0x90 (0x98 sync)\nRT1 must be tied to DGND", LX - 7.62, BOTY + 10.16, 1.27)

# ---------------- U2 bottom grounds ----------------
bot = [P("U2", n) for n in ("5", "27", "11", "13", "29")]
for px, py in bot:
    W((px, py), (px, py + 2.54))
W((bot[0][0], BOTY + 2.54), (bot[-1][0], BOTY + 2.54))
gnd(X0, BOTY + 2.54)

# ---------------- U2 right side: charge pump, refs ----------------
c1x, c1y = P("U2", "16"); c2x, c2y = P("U2", "15")
RC("C28", "2u2", RX + 10.16, Y0 - 3.81)
W((c1x, c1y), (RX + 5.08, c1y), (RX + 5.08, Y0 - 7.62), (RX + 10.16, Y0 - 7.62))
W((c2x, c2y), (RX + 2.54, c2y), (RX + 2.54, Y0), (RX + 10.16, Y0))
for n, kind, ref, col in (("28", "1u", "C32", 7.62), ("10", "1u", "C31", 17.78),
                          ("12", "4u7", "C30", 27.94), ("14", "47u", "C29", 38.1)):
    px, py = P("U2", n)
    W((px, py), (RX + col, py))
    RC(ref, kind, RX + col, py + 3.81)
    gnd(RX + col, py + 7.62)
T("C29 returns to pin 13 AGND_CP\nC28 tight across pins 15/16", RX + 2.54, BOTY + 16.51, 1.27)

# ---------------- line output ----------------
o1x, o1y = P("U2", "6"); gsx, gsy = P("U2", "7"); o2x, o2y = P("U2", "8")
JX, JY = RX + 93.98, Y0
Sym("J4", "Connector_Generic:Conn_01x03", JX, JY, 0, "LINE OUT", FP_KK3, "https://www.farnell.com/datasheets/1751313.pdf",
    "Line out header: 1=LEFT 2=GND (star) 3=RIGHT",
    extra={"MPN": "MC34631", "Manufacturer": "Multicomp Pro", "Source": "STOCK"})
j1, j2, j3 = P("J4", "1"), P("J4", "2"), P("J4", "3")
# left
W((o1x, o1y), (RX + 57.15, o1y))
L("DAC_OUT_L", RX + 20.32, o1y)
RC("R20", "300R", RX + 60.96, o1y, 90)
W((RX + 64.77, o1y), (RX + 81.28, o1y), (RX + 81.28, j1[1]), j1)
RC("C33", "2n2", RX + 73.66, o1y + 3.81); gnd(RX + 73.66, o1y + 7.62)
L("LINE_OUT_L", RX + 66.04, o1y)
# right
rrow = Y0 + 7.62
W((o2x, o2y), (RX + 48.26, o2y), (RX + 48.26, rrow), (RX + 57.15, rrow))
L("DAC_OUT_R", RX + 20.32, o2y)
RC("R21", "300R", RX + 60.96, rrow, 90)
W((RX + 64.77, rrow), (RX + 81.28, rrow), (RX + 81.28, j3[1]), j3)
RC("C34", "2n2", RX + 73.66, rrow + 3.81); gnd(RX + 73.66, rrow + 7.62)
L("LINE_OUT_R", RX + 66.04, rrow)
# ground sense -> net tie at the connector ground
Sym("NT1", "Device:NetTie_2", RX + 60.96, Y0, 0, "NetTie_2", "NetTie:NetTie-2_SMD_Pad0.5mm", "",
    "GND_SNS star-point tie at J4 pin 2", extra={"Source": "PCB copper"})
nt1, nt2 = P("NT1", "1"), P("NT1", "2")
W((gsx, gsy), (RX + 50.8, gsy), (RX + 50.8, Y0), nt1)
L("GND_SNS", RX + 20.32, gsy)
W(nt2, j2)
gnd(RX + 68.58, Y0)
T("LINE OUT", JX - 7.62, Y0 - 27.94, 2.54, True)
T("J4: 1=LEFT  2=GND  3=RIGHT (ch1=L, ch2=R)\nNT1 sits at J4 pin 2 = star point:\nroute GND_SNS as its own trace from U2 pin 7.\nC33/C34 GND also at the star point.",
  RX + 50.8, RAIL - 6.35, 1.27)

# ---------------- ATtiny412 control ----------------
AX, AY = X0 - 76.2, Y0 + 10.16
Sym("U3", "MCU_Microchip_ATtiny:ATtiny412-SS", AX, AY, 0, "ATtiny412-SS",
    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
    "https://ww1.microchip.com/downloads/en/DeviceDoc/ATtiny212-214-412-414-416-DataSheet-DS40002287A.pdf",
    "ES9033Q I2C configuration, CHIP_EN sequencing",
    extra={"MPN": "ATTINY412-SSN", "Manufacturer": "Microchip", "Source": "STOCK"})
vx, vy = P("U3", "1")
W((vx, vy), (vx, vy - 12.7), (vx + 7.62, vy - 12.7))
W((vx, vy - 12.7), (vx - 7.62, vy - 12.7))
L("3V3_DAC", vx - 7.62, vy - 12.7, 180)
RC("C35", "100n", vx + 7.62, vy - 8.89); gnd(vx + 7.62, vy - 5.08)
gx, gy = P("U3", "8"); gnd(gx, gy)
for n, net in (("6", "UPDI"), ("4", "I2C_SDA"), ("5", "I2C_SCL")):
    px, py = P("U3", n)
    W((px, py), (px + 7.62, py))
    L(net, px + 7.62, py)
ncs.append(P("U3", "7"))                 # PA3 spare
# PA6: PCM2706 3V3 rail sense through R25
px, py = P("U3", "2")
sx = px + 12.7
W((px, py), (sx, py), (sx, py + 3.81))
RC("R25", "10k", sx, py + 7.62)
W((sx, py + 11.43), (sx, py + 13.97))
L("3V3", sx, py + 13.97, 270)
# PA7: DAC_EN with pull-down
px, py = P("U3", "3")
dx = px + 2.54
W((px, py), (dx, py), (dx, py + 3.81))
L("DAC_EN", dx, py)
RC("R24", "100k", dx, py + 7.62)
gnd(dx, py + 11.43)
T("CONTROL", AX - 45.72, AY - 33.02, 2.54, True)
T("U3 holds DAC_EN low until the PCM2706 3V3 rail is up and MCLK is stable,\nthen CHIP_EN high, wait 100 ms, clock setup at 0x98, then config at 0x90.\nPA6 senses the PCM2706 rail (3V3) via R25.  PA3 spare.",
  AX - 22.86, AY + 33.02, 1.27)
# I2C pull-ups
for ref, x, net in (("R22", AX + 25.4, "I2C_SDA"), ("R23", AX + 33.02, "I2C_SCL")):
    RC(ref, "4k7", x, RAIL + 17.78)
    W((x, RAIL + 13.97), (x, RAIL + 11.43))
    W((x, RAIL + 21.59), (x, RAIL + 24.13))
    L(net, x, RAIL + 24.13, 270)
W((AX + 25.4, RAIL + 11.43), (AX + 33.02, RAIL + 11.43))
L("3V3_DAC", AX + 25.4, RAIL + 11.43, 180)
# UPDI header
UX, UY = AX - 38.1, AY
Sym("J5", "Connector_Generic:Conn_01x03", UX, UY, 0, "UPDI", FP_KK3, "https://www.farnell.com/datasheets/1751313.pdf",
    "UPDI programming: 1=UPDI 2=3V3_DAC 3=GND",
    extra={"MPN": "MC34631", "Manufacturer": "Multicomp Pro", "Source": "STOCK"})
for n, net in (("1", "UPDI"), ("2", "3V3_DAC")):
    px, py = P("J5", n)
    W((px, py), (px - 5.08, py))
    L(net, px - 5.08, py, 180)
px, py = P("J5", "3")
W((px, py), (px - 2.54, py), (px - 2.54, py + 2.54)); gnd(px - 2.54, py + 2.54)
T("J5 pin 2 is the 3.3V DAC rail:\nprogrammer must NOT drive 5V", UX - 15.24, UY + 12.7, 1.27)

# ---------------- VIN label on existing input net ----------------
W((48.26, 48.26), (48.26, 43.18))
L("VIN", 48.26, 43.18, 90)

T("ES9033Q DAC", X0 - 15.24, RAIL - 15.24, 5.08, True)

# =========================================================== wire splitting / junctions
pts = set(ALLPINPTS)
for a, b in wires:
    pts.add(a); pts.add(b)
for _, x, y, _ in labels:
    pts.add((x, y))
for x, y in ncs:
    pts.add((x, y))

def on_seg(p, a, b):
    if a[0] == b[0] == p[0]:
        return min(a[1], b[1]) < p[1] < max(a[1], b[1])
    if a[1] == b[1] == p[1]:
        return min(a[0], b[0]) < p[0] < max(a[0], b[0])
    return False

changed = True
while changed:
    changed = False
    for i, (a, b) in enumerate(wires):
        for p in pts:
            if on_seg(p, a, b):
                wires[i] = [a, p]
                wires.append([p, b])
                changed = True
                break
        if changed:
            break

deg = {}
for a, b in wires:
    deg[a] = deg.get(a, 0) + 1
    deg[b] = deg.get(b, 0) + 1
for p in ALLPINPTS:
    if p in deg:
        deg[p] += 1
junctions = [p for p, d in deg.items() if d >= 3]

# =========================================================== emit
def prop(name, val, x, y, ang=0, hide=False, justify=None):
    h = "\n\t\t\t(hide yes)" if hide else ""
    j = f"\n\t\t\t\t(justify {justify})" if justify else ""
    return f"""\t\t(property "{name}" "{val}"
\t\t\t(at {fmt(x)} {fmt(y)} {ang}){h}
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t){j}
\t\t\t)
\t\t)
"""

def field_pos(s):
    """reference/value positions + angle per symbol type."""
    x, y, r = s.x, s.y, s.rot
    fa = (360 - r) % 360
    if s.lib_id in ("Device:R", "Device:C"):
        if r == 0:
            return (x + 2.54, y - 1.27, 0, "left"), (x + 2.54, y + 1.27, 0, "left")
        return (x, y - 2.54, fa, None), (x, y + 2.54, fa, None)
    if s.lib_id == "power:GND":
        dx, dy = {0: (0, 5.08), 270: (-5.08, 0), 90: (5.08, 0)}[r]
        return (x, y + 6.35, 0, None), (x + dx, y + dy, 0, None)
    if s.lib_id == "power:PWR_FLAG":
        return (x, y - 5.08, 0, None), (x, y - 3.81, 0, None)
    if s.lib_id == "Device:LED":
        return (x + 3.81, y - 1.27, 0, "left"), (x + 3.81, y + 1.27, 0, "left")
    if s.lib_id == "Device:NetTie_2":
        return (x, y - 2.54, 0, None), (x, y + 2.54, 0, None)
    if s.lib_id == "Connector_Generic:Conn_01x03":
        return (x, y - 7.62, 0, None), (x, y - 5.08, 0, None)
    if s.lib_id.startswith("MCU_"):
        return (x - 12.7, y - 16.51, 0, "left"), (x + 2.54, y + 16.51, 0, "left")
    if s.lib_id.startswith("Custom:TPS7A"):
        return (x + 12.7, y - 7.62, 0, None), (x + 12.7, y - 5.08, 0, None)
    raise ValueError(s.lib_id)

out = []
for s in syms:
    (rx_, ry_, ra, rj), (vx_, vy_, va, vj) = field_pos(s)
    body = f"""\t(symbol
\t\t(lib_id "{s.lib_id}")
\t\t(at {fmt(s.x)} {fmt(s.y)} {s.rot})
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom {'no' if s.ref.startswith('#') or s.lib_id == 'Device:NetTie_2' else 'yes'})
\t\t(on_board {'no' if s.ref.startswith('#') else 'yes'})
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(uuid "{U()}")
"""
    body += prop("Reference", s.ref, rx_, ry_, ra, s.hide_ref, rj)
    body += prop("Value", s.value, vx_, vy_, va, s.hide_val, vj)
    body += prop("Footprint", s.fp, s.x, s.y, 0, True)
    body += prop("Datasheet", s.ds, s.x, s.y, 0, True)
    body += prop("Description", s.desc, s.x, s.y, 0, True)
    for k, v in (s.extra or {}).items():
        body += prop(k, v, s.x, s.y, 0, True)
    for num in pins_of(s.lib_id):
        body += f'\t\t(pin "{num}"\n\t\t\t(uuid "{U()}")\n\t\t)\n'
    body += f"""\t\t(instances
\t\t\t(project "{PROJECT}"
\t\t\t\t(path "/{ROOT_UUID}"
\t\t\t\t\t(reference "{s.ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)
"""
    out.append(body)

for a, b in wires:
    out.append(f"""\t(wire
\t\t(pts
\t\t\t(xy {fmt(a[0])} {fmt(a[1])}) (xy {fmt(b[0])} {fmt(b[1])})
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{U()}")
\t)
""")
for x, y in junctions:
    out.append(f"""\t(junction
\t\t(at {fmt(x)} {fmt(y)})
\t\t(diameter 0)
\t\t(color 0 0 0 0)
\t\t(uuid "{U()}")
\t)
""")
for x, y in ncs:
    out.append(f'\t(no_connect\n\t\t(at {fmt(x)} {fmt(y)})\n\t\t(uuid "{U()}")\n\t)\n')
for name, x, y, ang in labels:
    just = {0: "left bottom", 90: "left bottom", 180: "right bottom", 270: "right bottom"}[ang]
    out.append(f"""\t(label "{name}"
\t\t(at {fmt(x)} {fmt(y)} {ang})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify {just})
\t\t)
\t\t(uuid "{U()}")
\t)
""")
for txt, x, y, size, bold in texts:
    th = f"\n\t\t\t\t(thickness {fmt(size / 5)})\n\t\t\t\t(bold yes)" if bold else ""
    txt = txt.replace("\n", "\\n")
    out.append(f"""\t(text "{txt}"
\t\t(exclude_from_sim no)
\t\t(at {fmt(x)} {fmt(y)} 0)
\t\t(effects
\t\t\t(font
\t\t\t\t(size {fmt(size)} {fmt(size)}){th}
\t\t\t)
\t\t\t(justify left top)
\t\t)
\t\t(uuid "{U()}")
\t)
""")

# move U2 and its Reference/Value fields
ui = sch.find('(lib_id "ESS:ES9033Q")')
us = sch.rfind("\t(symbol\n", 0, ui)
ue = match_paren(sch, us + 1)
ublk = sch[us:ue + 1]
ublk = ublk.replace("(at 360.68 101.6 0)", f"(at {fmt(X0)} {fmt(Y0)} 0)", 1)
ublk = ublk.replace("(fields_autoplaced yes)\n", "")
ublk = re.sub(r'(\(property "Reference" "U2"\n\t\t\t\(at )[-\d.]+ [-\d.]+ 0\)', rf'\g<1>{fmt(X0 + 15.24)} {fmt(BOTY + 2.54)} 0)', ublk)
ublk = re.sub(r'(\(property "Value" "ES9033Q"\n\t\t\t\(at )[-\d.]+ [-\d.]+ 0\)', rf'\g<1>{fmt(X0 + 15.24)} {fmt(BOTY + 5.08)} 0)', ublk)
ublk = re.sub(r'(\(property "(?:Footprint|Datasheet|Description|Manufacturer|MPN)" "[^"]*"\n\t\t\t\(at )360.68 101.6', rf'\g<1>{fmt(X0)} {fmt(Y0)}', ublk)
sch = sch[:us] + ublk + sch[ue + 1:]

ins = sch.rfind("\t(sheet_instances")
sch = sch[:ins] + "".join(out) + sch[ins:]
open(DST, "w").write(sch)
print(f"symbols {len(syms)}  wires {len(wires)}  junctions {len(junctions)}  labels {len(labels)}")
