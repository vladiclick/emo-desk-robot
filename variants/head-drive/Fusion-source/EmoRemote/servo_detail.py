"""Detailed colored MG90S reconstruction; vendor envelope, not official CAD.

Nominal 22.8 x 12.4 x 28.5 mm. Manufacturer product page:
https://towerpro.com.tw/product/mg90s-3/
Shaft offset, tab holes, label and case details are representative assumptions.
No printed spline is implied: the real servo uses its supplied horn and screw.
"""
import math

import adsk.core as C
import adsk.fusion as F


def _point(x, y, z):
    return C.Point3D.create(x / 10, y / 10, z / 10)


def _vector(values):
    return C.Vector3D.create(*values)


def _validate_frame(origin, u, v, w):
    values = tuple(origin) + tuple(u) + tuple(v) + tuple(w)
    if len(values) != 12 or not all(math.isfinite(x) for x in values):
        raise ValueError('Servo origin and axes must contain three finite values each')
    axes = (u, v, w)
    dot = lambda a, b: sum(x * y for x, y in zip(a, b))
    if any(abs(dot(a, a) - 1) > 1e-6 for a in axes):
        raise ValueError('Servo orientation axes must have unit length')
    if any(abs(dot(axes[i], axes[j])) > 1e-6
           for i in range(3) for j in range(i)):
        raise ValueError('Servo orientation axes must be orthogonal')
    cross = (u[1] * v[2] - u[2] * v[1],
             u[2] * v[0] - u[0] * v[2],
             u[0] * v[1] - u[1] * v[0])
    if dot(cross, w) < 1 - 1e-6:
        raise ValueError('Servo axes must form a right-handed coordinate system')


class _ServoGeometry:
    """Temporary local geometry, added only after its complete transformation."""

    def __init__(self, build, origin, u, v, w, label):
        self.b = build
        self.temp = build.temp
        self.label = str(label)
        self.bodies = []
        self.matrix = C.Matrix3D.create()
        self.matrix.setWithCoordinateSystem(
            _point(*origin), _vector(u), _vector(v), _vector(w))

    def box(self, center, size, x_axis=(1, 0, 0), y_axis=(0, 1, 0)):
        bounds = C.OrientedBoundingBox3D.create(
            _point(*center), _vector(x_axis), _vector(y_axis),
            *(value / 10 for value in size))
        return self.temp.createBox(bounds)

    def cyl(self, a, z, radius):
        return self.temp.createCylinderOrCone(
            _point(*a), radius / 10, _point(a[0], a[1], z), radius / 10)

    def combine(self, target, tools, cut=False):
        operation = (F.BooleanTypes.DifferenceBooleanType if cut
                     else F.BooleanTypes.UnionBooleanType)
        for tool in tools:
            if not self.temp.booleanOperation(target, tool, operation):
                raise RuntimeError('MG90S temporary Boolean failed: ' + self.label)
        return target

    def rounded_case(self):
        # Rounded vertical corners avoid the crude rectangular placeholder look.
        body = self.box((0, 0, 11.6), (21.2, 12.4, 23.2))
        tools = [self.box((0, 0, 11.6), (22.8, 10.8, 23.2))]
        tools += [self.cyl((x, y, 0), 23.2, .8)
                  for x in (-10.6, 10.6) for y in (-5.4, 5.4)]
        return self.combine(body, tools)

    def add(self, body, name, color, hardware=False):
        if not self.temp.transform(body, self.matrix):
            raise RuntimeError('MG90S frame transformation failed: ' + self.label)
        result = self.b.temp_body(body, 'MG90S ' + self.label + ' | ' + name)
        self.b.paint(result, 'MG90S ' + name.split(':')[0], color)
        if hardware:
            self.b.add_hardware(result, 'MG90S ' + self.label + ' | ' + name)
        else:
            result.name = 'VIS | MG90S ' + self.label + ' | ' + name
            self.b.visuals.append(result)
        self.bodies.append(result)
        return result

    def label_stroke(self, start, end, name):
        dx, dz = end[0] - start[0], end[1] - start[1]
        length = math.hypot(dx, dz)
        axis = (dx / length, 0, dz / length)
        body = self.box(((start[0] + end[0]) / 2, -6.31,
                         (start[1] + end[1]) / 2),
                        (length + .13, .045, .16), axis, (0, 1, 0))
        return self.add(body, 'Label ink:' + name, (22, 22, 20))


def _housing(g):
    case = g.rounded_case()
    # Ears sit around the case seam; each has a through mounting hole.
    ears = g.box((0, 0, 18.5), (32.5, 12.4, 2))
    case = g.combine(case, [ears])
    holes = [g.cyl((x, 0, 17), 20, 1.1) for x in (-14, 14)]
    case = g.combine(case, holes, cut=True)
    # Recognizable asymmetric gearbox lid and concentric output collar.
    humps = [g.cyl((-5.7, 0, 23.1), 25.0, 5.45),
             g.cyl((4.5, 0, 23.1), 24.45, 4.7),
             g.cyl((-5.7, 0, 24.9), 26.2, 3.65)]
    case = g.combine(case, humps)
    # Recesses represent the real case screws, not enclosure fasteners.
    recesses = [g.cyl((x, y, 22.6), 23.4, .86)
                for x in (-9, 9) for y in (-4.35, 4.35)]
    case = g.combine(case, recesses, cut=True)
    return g.add(case, 'Black nylon housing', (24, 25, 27), hardware=True)


def _spline(g):
    shaft = g.cyl((-5.7, 0, 26.2), 28.5, 2.35)
    bore = g.cyl((-5.7, 0, 26.1), 28.6, .75)
    shaft = g.combine(shaft, [bore], cut=True)
    # Longitudinal shallow flats visibly suggest the metal output spline.
    grooves = []
    for index in range(20):
        angle = index * math.tau / 20
        radial = (math.cos(angle), math.sin(angle), 0)
        tangent = (-radial[1], radial[0], 0)
        grooves.append(g.box((-5.7 + 2.35 * radial[0],
                              2.35 * radial[1], 27.35),
                             (.28, .12, 2.5), radial, tangent))
    shaft = g.combine(shaft, grooves, cut=True)
    return g.add(shaft, 'Brass output spline', (177, 137, 54))


def _case_screws_and_seams(g):
    for i, (x, y) in enumerate(((-9, -4.35), (-9, 4.35),
                                (9, -4.35), (9, 4.35))):
        head = g.cyl((x, y, 22.61), 23.0, .78)
        slots = [g.box((x, y, 22.98), (1.0, .18, .2)),
                 g.box((x, y, 22.98), (.18, 1.0, .2))]
        head = g.combine(head, slots, cut=True)
        g.add(head, 'Stock case screw:' + str(i + 1), (97, 100, 104))
    # Fine graphite seam lines lie just on the outside of the nylon case.
    for z in (4.2, 17.4):
        for y in (-6.205, 6.205):
            g.add(g.box((0, y, z), (20.9, .015, .14)),
                  'Moulding seam:' + str(z) + ':' + str(y), (60, 61, 63))


def _label(g):
    g.add(g.box((0, -6.25, 11.4), (14.5, .08, 7.0)),
          'Gold product label', (197, 161, 52))
    # Vector lettering avoids installed-font and SketchText API dependencies.
    glyphs = {
        'M': (((0, 0), (0, 1)), ((0, 1), (.4, .45)),
              ((.4, .45), (.8, 1)), ((.8, 1), (.8, 0))),
        'G': (((.8, 1), (0, 1)), ((0, 1), (0, 0)),
              ((0, 0), (.8, 0)), ((.8, 0), (.8, .45)),
              ((.8, .45), (.4, .45))),
        '9': (((0, 1), (.8, 1)), ((.8, 1), (.8, 0)),
              ((0, 1), (0, .5)), ((0, .5), (.8, .5))),
        '0': (((0, 0), (0, 1)), ((0, 1), (.8, 1)),
              ((.8, 1), (.8, 0)), ((.8, 0), (0, 0))),
        'S': (((.8, 1), (0, 1)), ((0, 1), (0, .5)),
              ((0, .5), (.8, .5)), ((.8, .5), (.8, 0)),
              ((.8, 0), (0, 0)))
    }
    for index, letter in enumerate('MG90S'):
        for segment, (start, end) in enumerate(glyphs[letter]):
            world = lambda p: (-5.9 + index * 2.45 + p[0] * 2,
                               10.3 + p[1] * 2.6)
            g.label_stroke(world(start), world(end),
                           letter + str(index) + ':' + str(segment))


def _leads(g):
    for index, (name, color) in enumerate((('Brown ground lead', (85, 44, 24)),
                                          ('Red power lead', (178, 34, 31)),
                                          ('Orange signal lead', (232, 113, 22)))):
        x = (index - 1) * 1.05
        a, end = _point(x, -6.2, 2.1), _point(x, -10.8, 2.1)
        wire = g.temp.createCylinderOrCone(a, .045, end, .045)
        g.add(wire, name, color)
    g.add(g.box((0, -6.47, 2.1), (3.6, .6, 1.6)),
          'Rubber cable strain relief', (18, 18, 19))


def make_servo(b, origin, u, v, w, label):
    """Create MG90S with case base at origin; output along positive w.

    Supply right-handed unit axes in the parent component coordinates.
    Local case: u +/-11.4, v +/-6.2, w 0..23.2 mm.
    Tabs extend to u +/-16.25; spline center u=-5.7 and w=28.5.
    Only the main nylon housing is hardware for collision checking; all small
    cosmetics and loose wire stubs are explicitly marked VIS and should be
    excluded from enclosure collision reports. Shaft is returned separately
    so the caller can include it in a purposeful spindle-clearance audit.
    """
    _validate_frame(origin, u, v, w)
    g = _ServoGeometry(b, origin, u, v, w, label)
    housing = _housing(g)
    spline = _spline(g)
    _case_screws_and_seams(g)
    _label(g)
    _leads(g)
    transform_point = lambda p: tuple(origin[i] + sum(
        p[j] * (u, v, w)[j][i] for j in range(3)) for i in range(3))
    return {'housing': housing, 'spline': spline, 'bodies': tuple(g.bodies),
            'axis_point_mm': transform_point((-5.7, 0, 28.5)),
            'axis_direction': tuple(w),
            'case_size_mm': (22.8, 12.4, 23.2),
            'total_axis_height_mm': 28.5,
            'source': 'TowerPro MG90S nominal envelope; cosmetic reconstruction'}
