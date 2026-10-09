"""SPU03L-05 visual STEP, using CadQuery 2.8.

Source: MEAN WELL SPU03-SPEC, 2024-08-02, page 1.
Millimetres; origin pin 1 at PCB top; STEP Y = -KiCad footprint Y.
Rounding, seam and printed lettering are cosmetic approximations.
"""
from pathlib import Path
import json
import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'review/spu03-model-2026-10-09'
DEST = ROOT / 'InputSwitch.3dshapes/SPU03L-05.step'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
PINS = {1: 0.0, 2: 2.54, 5: 10.16, 7: 15.24}

def box(w, d, h, x, y, z):
    return cq.Workplane('XY').box(w, d, h, centered=(True, True, False)).translate((x, y, z))

def build():
    assembly = cq.Assembly(name='SPU03L-05')
    parts = {}
    def add(name, part, color):
        assert part.val().isValid(), name
        assembly.add(part, name=name, color=cq.Color(*color))
        parts[name] = part

    # Nominal envelope exactly preserves the previous model placement.
    # Split base creates a subtle mould seam, kept inside the envelope.
    case = box(19.6, 7.5, 9.94, 7.62, -2.55, 0.26).edges('|Z').fillet(0.18)
    case = case.edges('>Z').fillet(0.12)
    add('Black_moulded_case', case, (0.075, 0.080, 0.085))
    base = box(19.6, 7.5, 0.25, 7.62, -2.55, 0).edges('|Z').fillet(0.18)
    add('Case_base', base, (0.095, 0.098, 0.100))
    # Shallow inner insert and terminal collars are visual details only.
    add('Underside_potting', box(18.7, 6.6, 0.02, 7.62, -2.55, 0), (0.045, 0.046, 0.047))
    for number, x in PINS.items():
        pin = box(0.50, 0.30, 4.10, x, 0, -3.81)
        pin = pin.edges('<Z').chamfer(0.035)
        add(f'Pin_{number}', pin, (0.73, 0.75, 0.78))

    def text(name, label, size, x, y):
        lettering = cq.Workplane('XY').text(label, size, 0.006, fontPath=FONT,
                                             halign='center', valign='center', combine=False)
        add(name, lettering.translate((x, y, 10.2005)), (0.94, 0.94, 0.91))
    text('Part_number_print', 'SPU03L-05', 2.30, 7.62, -4.15)
    text('Input_print', '+Vin -', 1.05, 1.45, -1.85)
    text('Output_print', '- Vout +', 1.05, 12.48, -1.85)
    for n, x in PINS.items():
        ring = cq.Workplane('XY').circle(0.20).circle(0.10).extrude(0.006)
        add(f'Printed_terminal_{n}', ring.translate((x, -0.60, 10.2005)), (0.94, 0.94, 0.91))

    DEST.parent.mkdir(exist_ok=True)
    assembly.save(str(DEST))
    imported = cq.importers.importStep(str(DEST)).val()
    assert imported.isValid()
    bb = imported.BoundingBox()
    assert abs(bb.xmin + 2.18) < 1e-5 and abs(bb.xmax - 17.42) < 1e-5
    assert abs(bb.ymin + 6.30) < 1e-5 and abs(bb.ymax - 1.20) < 1e-5
    assert abs(bb.zmin + 3.81) < 1e-5 and abs(bb.zmax - 10.2065) < 1e-5
    for n, x in PINS.items():
        pb = parts[f'Pin_{n}'].val().BoundingBox()
        assert abs((pb.xmin + pb.xmax)/2 - x) < 1e-8
        assert abs((pb.ymin + pb.ymax)/2) < 1e-8
    report = {
        'source': 'https://www.meanwell.com/Upload/PDF/SPU03/SPU03-SPEC.PDF',
        'revision': '2024-08-02 page 1',
        'body_mm': [19.6, 7.5, 10.2], 'lead_mm': [0.50, 0.30, 3.81],
        'pin_centres_model_mm': {str(n): [x, 0] for n, x in PINS.items()},
        'bbox_mm': [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax],
        'step_import_valid': imported.isValid(), 'imported_solids': len(imported.Solids()),
        'cosmetic_features': '0.18 mm corner radius, 0.12 mm top edge radius, seam, underside insert, print layout and 0.006 mm print thickness',
        'origin': 'pin 1 on PCB top; zero offset and rotation; scale 1',
    }
    REVIEW.mkdir(exist_ok=True)
    (REVIEW / 'geometry-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(DEST)
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    build()
