"""Build nominal AGN2004H assets from Panasonic ASCTB13E 202603, pp. 3 and 7.

No source board/schematic changes. Footprint origin = pin 1; STEP Y = -PCB Y.
STEP is a simplified mechanical envelope, not a manufacturer production model.
"""
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[1]
NAME = "Relay_DPDT_Panasonic_AGN2004H"
DATASHEET = "https://industry.panasonic.com/ac/cdn/e/control/relay/signal/catalog/mech_eng_gn.pdf"
PADS = {1: (0, 0), 2: (0, 3.2), 3: (0, 5.4), 4: (0, 7.6),
        5: (3.2, 7.6), 6: (3.2, 5.4), 7: (3.2, 3.2), 8: (3.2, 0)}


def footprint():
    out = [f'(footprint "{NAME}"', '(version 20260206)', '(generator "pcbnew")',
           '(layer "F.Cu")',
           f'(descr "Panasonic/NAIS AGN2004H; 4.5V 140mW DPDT; coil 1+ 8-; COM 3/6 NC 2/7 NO 4/5; 3.2mm row spacing; {DATASHEET}")',
           '(tags "Panasonic NAIS GN AGN2004H relay DPDT THT")', '(attr through_hole)',
           '(property "Reference" "REF**" (at 1.6 -2.65) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
           '(property "Value" "AGN2004H" (at 1.6 10.3) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))',
           f'(property "Datasheet" "{DATASHEET}" (at 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1 1) (thickness 0.15))))',
           '(fp_text user "${REFERENCE}" (at 1.6 3.8 90) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))']

    def line(a, b, layer, width):
        out.append(f'(fp_line (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width {width}) (type solid)) (layer "{layer}"))')

    def polygon(points, layer, width):
        for a, b in zip(points, points[1:] + points[:1]):
            line(a, b, layer, width)

    # Nominal case is 5.7 x 10.6 mm, centred on the terminal pattern.
    polygon([(-1.25, -0.75), (-0.5, -1.5), (4.45, -1.5), (4.45, 9.1), (-1.25, 9.1)], "F.Fab", 0.1)
    polygon([(-1.4, -1.65), (4.6, -1.65), (4.6, 9.25), (-1.4, 9.25)], "F.SilkS", 0.12)
    # Maximum case 6.0 x 10.9 mm, with 0.25 mm courtyard on all sides.
    polygon([(-1.65, -1.9), (4.85, -1.9), (4.85, 9.5), (-1.65, 9.5)], "F.CrtYd", 0.05)
    line((-1.7, 0), (-1.7, -1.95), "F.SilkS", 0.12)
    line((-1.7, -1.95), (0, -1.95), "F.SilkS", 0.12)
    for n, (x, y) in PADS.items():
        out.append(f'(pad "{n}" thru_hole {"rect" if n == 1 else "circle"} (at {x} {y}) (size 1.6 1.6) (drill 0.85) (layers "*.Cu" "*.Mask"))')
    out.append(f'(model "${{KIPRJMOD}}/InputSwitch.3dshapes/{NAME}.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))')
    out.append(')')
    dest = ROOT / 'InputSwitch.pretty' / f'{NAME}.kicad_mod'
    dest.write_text('\n'.join(out) + '\n')
    return dest


def step():
    entities = []

    def ent(s):
        entities.append(f'#{len(entities)+1}={s};')
        return f'#{len(entities)}'

    def refs(items):
        return '(' + ','.join(items) + ')'

    def vector(v):
        return '(' + ','.join(f'{n:.9f}' for n in v) + ')'

    app = ent("APPLICATION_CONTEXT('configuration controlled 3d designs of mechanical parts and assemblies')")
    ent(f"APPLICATION_PROTOCOL_DEFINITION('international standard','config_control_design',1994,{app})")
    pc = ent(f"PRODUCT_CONTEXT('',{app},'mechanical')")
    prod = ent(f"PRODUCT('AGN2004H','AGN2004H','Simplified nominal case, eight blades and orientation mark',({pc}))")
    form = ent(f"PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE('1','',{prod},.NOT_KNOWN.)")
    dc = ent(f"PRODUCT_DEFINITION_CONTEXT('part definition',{app},'design')")
    definition = ent(f"PRODUCT_DEFINITION('design','',{form},{dc})")
    shape = ent(f"PRODUCT_DEFINITION_SHAPE('','',{definition})")
    lu = ent('(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.))')
    au = ent('(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.))')
    su = ent('(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT())')
    unc = ent(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-6),{lu},'distance_accuracy_value','')")
    context = ent(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({unc})) GLOBAL_UNIT_ASSIGNED_CONTEXT(({lu},{au},{su})) REPRESENTATION_CONTEXT('','3D'))")
    solids, styles = [], []

    def prism(name, outline, z0, z1, colour):
        pts = [(x, y, z0) for x, y in outline] + [(x, y, z1) for x, y in outline]
        vertices = [ent(f"CARTESIAN_POINT('',{vector(p)})") for p in pts]
        n = len(outline)
        faces = []
        face_indices = [list(range(n-1, -1, -1)), list(range(n, 2*n))]
        face_indices += [[i, (i+1) % n, (i+1) % n+n, i+n] for i in range(n)]
        for indices in face_indices:
            a, b, c = [pts[i] for i in indices[:3]]
            u = [b[i]-a[i] for i in range(3)]
            v = [c[i]-a[i] for i in range(3)]
            normal = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
            loop = ent(f"POLY_LOOP('',{refs([vertices[i] for i in indices])})")
            bound = ent(f"FACE_OUTER_BOUND('',{loop},.T.)")
            d = ent(f"DIRECTION('',{vector(normal)})")
            r = ent(f"DIRECTION('',{vector(u)})")
            axes = ent(f"AXIS2_PLACEMENT_3D('',{vertices[indices[0]]},{d},{r})")
            plane = ent(f"PLANE('',{axes})")
            faces.append(ent(f"FACE_SURFACE('',({bound}),{plane},.T.)"))
        shell = ent(f"CLOSED_SHELL('',{refs(faces)})")
        solid = ent(f"FACETED_BREP('{name}',{shell})")
        solids.append(solid)
        col = ent(f"COLOUR_RGB('',{','.join(str(c) for c in colour)})")
        fill_col = ent(f"FILL_AREA_STYLE_COLOUR('',{col})")
        fill = ent(f"FILL_AREA_STYLE('',({fill_col}))")
        surface = ent(f"SURFACE_STYLE_FILL_AREA({fill})")
        side = ent(f"SURFACE_SIDE_STYLE('',({surface}))")
        usage = ent(f"SURFACE_STYLE_USAGE(.BOTH.,{side})")
        assignment = ent(f"PRESENTATION_STYLE_ASSIGNMENT(({usage}))")
        styles.append(ent(f"STYLED_ITEM('',({assignment}),{solid})"))

    def box(name, x0, y0, z0, x1, y1, z1, colour):
        prism(name, [(x0,y0),(x1,y0),(x1,y1),(x0,y1)], z0,z1,colour)

    # Published 9 mm mounted height includes the nominal 0.5 mm standoff.
    box('Case', -1.25, -9.1, 0.5, 4.45, 1.5, 9, (0.76,0.78,0.79))
    for n, (x, py) in PADS.items():
        y = -py
        box(f'Pin {n}', x-0.125,y-0.2,-3.5,x+0.125,y+0.2,0.5,(0.72,0.72,0.75))
    # Cosmetic orientation indication at the pin 1 corner, raised 5 um to avoid
    # coincident surfaces in viewers (not a specified mechanical feature).
    outline = [(-0.62+0.32*math.cos(i*math.tau/24),0.85+0.32*math.sin(i*math.tau/24)) for i in range(24)]
    prism('Pin 1 direction indication', outline,9.001,9.005,(0.10,0.10,0.11))
    rep = ent(f"FACETED_BREP_SHAPE_REPRESENTATION('AGN2004H',{refs(solids)},{context})")
    ent(f"SHAPE_DEFINITION_REPRESENTATION({shape},{rep})")
    ent(f"MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',{refs(styles)},{context})")
    header = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('AGN2004H nominal envelope: 10.6 x 5.7 x 9 mm mounted; eight 0.4 x 0.25 mm blades; simplified model'),'2;1');
FILE_NAME('Relay_DPDT_Panasonic_AGN2004H.step','2026-10-07T00:00:00',(''),(''),'Codex','', '');
FILE_SCHEMA(('CONFIG_CONTROL_DESIGN'));
ENDSEC;
DATA;
"""
    dest = ROOT / 'InputSwitch.3dshapes' / f'{NAME}.step'
    dest.write_text(header + '\n'.join(entities) + '\nENDSEC;\nEND-ISO-10303-21;\n')
    return dest


if __name__ == '__main__':
    print(footprint())
    print(step())
