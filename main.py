from sys import argv
from functools import wraps # lru_cache
from itertools import product
from inspect import signature
from math import sqrt, atan, pi, sin, cos
from random import random

def concat_names(objs):
    return ", ".join(map(lambda o: o.name, objs))

def solve_quadratic(a, b, c):
    d = b * b - 4 * a  *c
    if abs(d) < EPSILON:
        return True, 1, -b / 2 * a, -b / 2 * a
    if d < 0:
        return False, 0, None, None
    return True, 2, (-b - sqrt(d)) / (2 * a), (-b + sqrt(d)) / (2 * a)

class Obj:
    count = 0
    def __init__(self, asy_order):
        self.order = asy_order
        self.id = Obj.count
        Obj.count += 1
        self.name = f"__obj{str(self.id).zfill(3)}"
    
    def __hash__(self):
        return hash(self.id)

class Point(Obj):
    collinear = set()
    concyclic = set()
    def __init__(self, x, y):
        super().__init__(0)
        self.x = x
        self.y = y

        self.lines = set()
        self.circles = set()
    
    def __repr__(self):
        return f"Point {self.name} [{self.id}]"
    
    def asy_definition(self):
        return f"pair {self.name} = ({self.x}, {self.y});"

    def asy(self):
        return f"dot('${self.name}$', {self.name}, dir(90));"
    
    def properties(self):
        lines = "on lines: " + concat_names([o for o in self.lines if not o.name.startswith("__")])
        circles = "on circles: " + concat_names([o for o in self.circles if not o.name.startswith("__")])
        collinear = "collinear: " + '; '.join([concat_names(col) for col in Point.collinear if self in col and all([not x.name.startswith("__") for x in col])])
        concyclic = "concyclic: " + '; '.join([concat_names(con) for con in Point.concyclic if self in con and all([not x.name.startswith("__") for x in con])])
        return "\n    ".join([str(self), lines, circles, collinear, concyclic])

class Line(Obj):
    concurrent = set()
    def __init__(self, a, b, c):
        super().__init__(1)
        self.a = a
        self.b = b
        self.c = c

        self.points = set()
        self.lines_perpendicular = set()
        self.lines_parallel = set()
        self.circles = set()
    
    def __repr__(self):
        return f"Line {self.name} [{self.id}]"
    
    def __call__(self, a):
        return self.a * a.x + self.b * a.y - self.c
    
    @property
    def leftmost(self):
        return min(self.points, key=lambda p: p.x) if self.points else None
    
    @property
    def rightmost(self):
        return max(self.points, key=lambda p: p.x) if self.points else None
    
    def asy(self):
        if not self.points:
            return ""
        a = f"({self.leftmost.x}, {self.leftmost.y})" if self.leftmost.name.startswith("__") else self.leftmost.name
        b = f"({self.rightmost.x}, {self.rightmost.y})" if self.rightmost.name.startswith("__") else self.rightmost.name
        return f"draw({a} -- {b});"
    
    def properties(self):
        points = "contains points: " + concat_names([o for o in self.points if not o.name.startswith("__")])
        perp_lines = "perpendicular to lines: " + concat_names([o for o in self.lines_perpendicular if not o.name.startswith("__")])
        parallel_lines = "parallel to lines: " + concat_names([o for o in self.lines_parallel if not o.name.startswith("__")])
        circles = "tanget to circles: " + concat_names([o for o in self.circles if not o.name.startswith("__")])
        concurrent = "concurrent: " + '; '.join([concat_names(con) for con in Line.concurrent if self in con])
        return "\n    ".join([str(self), points, perp_lines, parallel_lines, circles, concurrent])

class Circle(Obj):
    def __init__(self, o, r):
        super().__init__(2)
        self.o = o
        self.r = r

        self.points = set()
        self.lines = set()
        self.circles = set()

    def __repr__(self):
        return f"Circle {self.name} [{self.id}]"
    
    def asy(self):
        return f"draw(circle(({self.o.x}, {self.o.y}), {self.r}));"
    
    def properties(self):
        points = "contains points: " + concat_names([o for o in self.points if not o.name.startswith("__")])
        lines = "tangent to lines: " + concat_names([o for o in self.lines if not o.name.startswith("__")])
        circles = "tangent to circles: " + concat_names([o for o in self.circles if not o.name.startswith("__")])
        return "\n    ".join([str(self), points, lines, circles])

construction_functions = {}

known_properties = []

parameter_mapping = {
    "a": Point,
    "b": Point,
    "c": Point,
    "d": Point,
    "u": Line,
    "v": Line,
    "w": Line,
    "s": Circle,
    "t": Circle,
    "m": Circle,
    "x": Obj,
    "y": Obj,
}

class ConstructionFunction:
    def __init__(self, func):
        self.function = func
        self.name = self.function.__name__
        self.signature = signature(self.function)
        self.parameters = [parameter_mapping[x] for x in self.signature.parameters]
    
    def __repr__(self):
        return f"Construction Function {self.name} that takes {len(self)} parameters, {[cls.__name__ for cls in self.parameters]}"
    
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
    
    def __len__(self):
        return len(self.parameters)

def all_different(objects):
    return len(set(objects)) == len(objects)

def non_empty_intersection(s1, s2):
    return len([x for x in s1 if x in s2]) > 0

def construction_function(with_checks=True, cache=4):
    def construction_function_decorator(func):
        # @lru_cache(maxsize=cache)
        @wraps(func)
        def checked_construction_function(*args, **kwargs):
            result = func(*args, **kwargs)
            result_lst = list(result) if type(result) == tuple else [result]
            combined = list(args) + result_lst
            for check_function in check_functions.values():
                for check_function_arguments in product(*[[x for x in combined if type(x) == cls] for cls in check_function.parameters]):
                    if not all_different(check_function_arguments):
                        continue
                    check_function(*check_function_arguments)
            return result
        construction_functions[func.__name__] = ConstructionFunction(checked_construction_function)
        return checked_construction_function
    return construction_function_decorator

@construction_function()
def triangle():
    a = Point(-0.256, 0.966)
    b = Point(-0.905, -0.426)
    c = Point(0.943, -0.333)
    return a, b, c

@construction_function()
def unit_circle():
    return Circle(Point(0, 0), 1)

# random

@construction_function(cache=0)
def random_point_on_circle(s):
    t = random() * 2 * pi
    return Point(s.o.x + s.r * cos(t), s.o.y + s.r * sin(t))

@construction_function(cache=0)
def random_point_on_unit_circle():
    return random_point_on_circle(unit_circle())

@construction_function(cache=0)
def random_point_on_segment(a, b):
    t = random()
    return Point(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t)

def random_point_on_arc(s, angle1, angle2, radian=True):
    t = angle1 + random() * (angle2 - angle1)
    t = t if radian else t * pi / 180
    return Point(s.o.x + s.r * cos(t), s.o.y + s.r * sin(t))

@construction_function(cache=0)
def random_point_on_arc2(s, a, b):
    pass

@construction_function(cache=0)
def random_point():
    return random_point_on_unit_circle()

@construction_function(cache=0)
def random_line():
    return line(random_point(), random_point())

@construction_function(cache=0)
def random_circle():
    return Circle(random_point(), random())

@construction_function(cache=0)
def random_triangle_on_circle(s):
    a = random_point_on_circle(s)
    b = random_point_on_circle(s)
    c = random_point_on_circle(s)
    return a, b, c

@construction_function(cache=0)
def random_triangle_on_unit_circle():
    return random_triangle_on_circle(unit_circle())

@construction_function(cache=0)
def random_nice_triangle():
    x = 5
    a = random_point_on_arc(unit_circle(), 120 - x, 120 + x, radian=False)
    b = random_point_on_arc(unit_circle(), 210 - x, 210 + x, radian=False)
    c = random_point_on_arc(unit_circle(), 330 - x, 330 + x, radian=False)
    return a, b, c

@construction_function()
def center(s):
    return s.o

# pp

@construction_function()
def midpoint(a, b):
    return Point((a.x + b.x) / 2, (a.y + b.y) / 2)

@construction_function()
def line(a, b):
    return Line(b.y - a.y, a.x - b.x, a.x * b.y - a.y * b.x)

@construction_function()
def perpendicular_bisector(a, b):
    return Line(a.x - b.x, a.y - b.y, (a.x ** 2 + a.y ** 2 - b.x ** 2 - b.y ** 2) / 2)

@construction_function()
def circle_diameter(a, b):
    return Circle(midpoint(a, b), distance_pp(a, b) / 2)

@construction_function()
def reflection_pp(a, b):
    return Point(2 * b.x - a.x, 2 * b.y - a.y)

@construction_function()
def perpendicular_through(a, b):
    return Line(a.x - b.x, a.y - b.y, a.x ** 2 + a.y ** 2 - a.x * b.x - a.y * b.y)

@construction_function()
def circle_centered(a, b):
    return Circle(a, distance_pp(a, b))

# pl

@construction_function()
def reflection_pl(a, u):
    return reflection_pp(a, foot(a, u))

@construction_function()
def foot(a, u):
    return intersection_ll(u, perpendicular_line(a, u))

@construction_function()
def perpendicular_line(a, u):
    return Line(u.b, -u.a, a.x * u.b - a.y * u.a)

@construction_function()
def parallel_line(a, u):
    return Line(u.a, u.b, a.x * u.a + a.y * u.b)

# pc

@construction_function()
def tangent_points(a, s):
    if pc(a, s) != 1:
        raise GFDException(f"Point {a.name} is not outside of circle {s.name} in construction function tangent_points")
    return intersections_cc(s, circle_diameter(a, s.o))

@construction_function()
def tangent_lines(a, s):
    tp1, tp2 = tangent_points(a, s)
    return line(a, tp1), line(a, tp2)

@construction_function()
def tangent_line(a, s):
    if pc(a, s) != 0:
        raise GFDException(f"Point {a.name} is not on circle {s.name} in construction function tangent_lines")
    return perpendicular_through(a, s.o)

@construction_function()
def polar(a, s):
    if distance_pp(a, s.o) < EPSILON:
        raise GFDException(f"Point {a.name} is the center of circle {s.name} in construction function polar")
    d = (s.r / distance_pp(a, s.o)) ** 2
    p = Point(s.o.x + d * (a.x - s.o.x), s.o.y + d * (a.y - s.o.y))
    return perpendicular_through(p, s.o)

# ll

@construction_function()
def intersection_ll(u, v):
    if is_parallel(u, v):
        raise GFDException(f"Line {u.name} and {v.name} are parallel in construction function intersection_ll")
    return Point((u.c * v.b - u.b * v.c) / (u.a * v.b - u.b * v.a), (u.c * v.a - u.a * v.c) / (u.b * v.a - u.a * v.b))

@construction_function()
def angle_bisector(u, v):
    return Line(u.a / sqrt(u.a ** 2 + u.b ** 2) + v.a / sqrt(v.a ** 2 + v.b ** 2), u.b / sqrt(u.a ** 2 + u.b ** 2) + v.b / sqrt(v.a ** 2 + v.b ** 2), u.c / sqrt(u.a ** 2 + u.b ** 2) + v.c / sqrt(v.a ** 2 + v.b ** 2))

@construction_function()
def reflection_ll(u, v):
    i = intersection_ll(u, v)
    x, y = i.x, i.y
    m = u.a * v.b * v.b - u.a * v.a * v.a - 2 * u.b * v.a * v.b
    n = u.b * v.b * v.b - u.b * v.a * v.a - 2 * u.a * v.a * v.b
    return Line(m, -n, x * m - y * n)

# lc

@construction_function()
def intersections_lc(u, s):
    if lc(u, s) != -1:
        raise GFDException(f"Line {u.name} does not intersect Circle {s.name} in construction function intersections_lc")
    a = u.a ** 2 + u.b ** 2
    b = 2 * (s.o.y * u.a * u.b - s.o.x * u.b * u.b - u.a * u.c)
    c = (s.o.x ** 2) * (u.b ** 2) + (u.c ** 2) - 2 * s.o.y * u.b * u.c + (s.o.y ** 2) * (u.b ** 2) - (s.r ** 2) * (u.b ** 2)
    _, _, x1, x2 = solve_quadratic(a, b, c)
    y1 = (u.c - u.a * x1) / u.b
    y2 = (u.c - u.a * x2) / u.b
    return Point(x1, y1), Point(x2, y2)

@construction_function()
def intersection_lc(u, s):
    if lc(u, s) != 0:
        raise GFDException(f"Line {u.name} is not tangent circle {s.name} in construction function tangent_points")
    return foot(s.o, u)

@construction_function()
def tangent_point(u, s):
    if lc(u, s) != 0:
        raise GFDException(f"Line {u.name} is not tangent circle {s.name} in construction function tangent_points")
    return foot(s.o, u)

@construction_function()
def pole(u, s):
    d = (s.r / distance_pl(s.o, u)) ** 2
    a = foot(s.o, u)
    return Point(s.o.x + d * (a.x - s.o.x), s.o.y + d * (a.y - s.o.y))

# cc

@construction_function()
def intersections_cc(s, t):
    if cc(s, t) != -1:
        raise GFDException(f"Circle {s.name} and {t.name} do not intersect in construction function intersections_cc")
    return intersections_lc(radical_axis(s, t), s)

@construction_function()
def intersection_cc(s, t):
    if cc(s, t) != 0:
        raise GFDException(f"Circle {s.name} and {t.name} are not tangent in construction function intersection_cc")
    return intersection_ll(line(s.o, t.o), radical_axis(s, t))

@construction_function()
def radical_axis(s, t):
    return Line(2 * (s.o.x - t.o.x), 2 * (s.o.y - t.o.y), t.r ** 2 - s.r ** 2 + s.o.x ** 2 - t.o.x ** 2 + s.o.y ** 2 - t.o.y ** 2)

@construction_function()
def tangent_points_external(s, t):
    p1, p2 = tangent_points(tangent_intersection_external(s, t), s)
    p3, p4 = tangent_points(tangent_intersection_external(s, t), t)
    return p1, p2, p3, p4

@construction_function()
def tangent_points_internal(s, t):
    p1, p2 = tangent_points(tangent_intersection_internal(s, t), s)
    p3, p4 = tangent_points(tangent_intersection_internal(s, t), t)
    return p1, p2, p3, p4

@construction_function()
def tangent_intersection_external(s, t):
    return Point((s.o.x * t.r - t.o.x * s.r) / (t.r - s.r), (s.o.y * t.r - t.o.y * s.r) / (t.r - s.r))

@construction_function()
def tangent_intersection_internal(s, t):
    return Point((s.o.x * t.r + t.o.x * s.r) / (t.r + s.r), (s.o.y * t.r + t.o.y * s.r) / (t.r + s.r))

@construction_function()
def tangent_lines_external(s, t):
    return tangent_lines(tangent_intersection_external(s, t), s)

@construction_function()
def tangent_lines_internal(s, t):
    return tangent_lines(tangent_intersection_internal(s, t), s)

# ppp

@construction_function()
def internal_angle_bisector(a, b, c):
    return angle_bisector(line(a, b), line(c, a))

@construction_function()
def external_angle_bisector(a, b, c):
    return angle_bisector(line(a, b), line(a, c))

@construction_function()
def altitude(a, b, c):
    return perpendicular_line(a, line(b, c))

@construction_function()
def median(a, b, c):
    return line(a, midpoint(b, c))

@construction_function()
def foot_ppp(a, b, c):
    return foot(a, line(b, c))

@construction_function()
def circumcenter(a, b, c):
    return intersection_ll(perpendicular_bisector(a, b), perpendicular_bisector(a, c))

@construction_function()
def circumradius(a, b, c):
    return distance_pp(a, circumcenter(a, b, c))

@construction_function()
def circumcircle(a, b, c):
    return Circle(circumcenter(a, b, c), circumradius(a, b, c))

@construction_function()
def incenter(a, b, c):
    return intersection_ll(internal_angle_bisector(b, c, a), internal_angle_bisector(c, a, b))

@construction_function()
def inradius(a, b, c):
    return distance_pl(incenter(a, b, c), line(b, c))

@construction_function()
def incircle(a, b, c):
    return Circle(incenter(a, b, c), inradius(a, b, c))

@construction_function()
def excenter(a, b, c):
    return intersection_ll(external_angle_bisector(b, c, a), external_angle_bisector(c, a, b))

@construction_function()
def exradius(a, b, c):
    return distance_pl(excenter(a, b, c), line(b, c))

@construction_function()
def excircle(a, b, c):
    return Circle(excenter(a, b, c), exradius(a, b, c))

@construction_function()
def orthocenter(a, b, c):
    return intersection_ll(altitude(b, c, a), altitude(c, a, b))

@construction_function()
def centroid(a, b, c):
    return Point((a.x + b.x + c.x) / 3, (a.y + b.y + c.y) / 3)

check_functions = {}

class CheckFunction:
    def __init__(self, func):
        self.function = func
        self.name = self.function.__name__
        self.signature = signature(self.function)
        self.parameters = [parameter_mapping[x] for x in self.signature.parameters]
    
    def __repr__(self):
        return f"Check Function {self.name} that takes {len(self)} parameters, {[cls.__name__ for cls in self.parameters]}"
    
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
    
    def __len__(self):
        return len(self.parameters)

def check_function(func):
    @wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    check_functions[func.__name__] = CheckFunction(inner)
    return inner

def distance_pp(a, b):
    return sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def distance_pl(a, u):
    return abs(u(a)) / sqrt(u.a ** 2 + u.b ** 2)

def distance_pc(a, s):
    return abs(s.r - distance_pp(s.o, a))

def distance_lc(u, s):
    return abs(s.r - distance_pl(s.o, u))

def angle(u, v):
    x = u.a * v.a + u.b * v.b
    return abs(atan((v.a * u.b - u.a * v.b) / x)) if x else pi / 2

EPSILON = 1e-5

def is_collinear(a, b, c):
    return distance_pl(a, line(b, c)) < EPSILON

@check_function
def check_collinear(a, b, c):
    if is_collinear(a, b, c):
        Point.collinear.add(frozenset([a, b, c]))

def is_concyclic(a, b, c, d):
    return abs(angle(line(a, b), line(a, c)) - angle(line(d, b), line(d, c))) < EPSILON and abs(angle(line(b, a), line(b, c)) - angle(line(d, a), line(d, c))) < EPSILON

@check_function
def check_concyclic(a, b, c, d):
    if is_concyclic(a, b, c, d):
        Point.concyclic.add(frozenset([a, b, c, d]))

def is_concurrent(u, v, w):
    return abs(u.a * v.c * w.b + u.b * v.a * w.c + u.c * v.b * w.a - u.a * v.b * w.c - u.b * v. c * w.a - u.c * v.a * w.b) < EPSILON

@check_function
def check_concurrent(u, v, w):
    if is_concurrent(u, v, w):
        Line.concurrent.add(frozenset([u, v, w]))

def is_parallel(u, v):
    return angle(u, v) < EPSILON

@check_function
def check_parallel(u, v):
    if is_parallel(u, v):
        u.lines_parallel.add(v)
        v.lines_parallel.add(u)

def is_perpendicular(u, v):
    return pi / 2 - angle(u, v) < EPSILON

@check_function
def check_perpendicular(u, v):
    if is_perpendicular(u, v):
        u.lines_perpendicular.add(v)
        v.lines_perpendicular.add(u)

def is_tangent(s, t):
    return abs(distance_pc(s.o, t) - s.r) < EPSILON

@check_function
def check_tangent(s, t):
    if is_tangent(s, t):
        s.circles.add(t)
        t.circles.add(s)

def is_pl(a, u):
    return distance_pl(a, u) < EPSILON

@check_function
def check_pl(a, u):
    if is_pl(a, u):
        a.lines.add(u)
        u.points.add(a)

def is_pc(a, s):
    return distance_pc(a, s) < EPSILON

@check_function
def check_pc(a, s):
    if is_pc(a, s):
        a.circles.add(s)
        s.points.add(a)

def is_lc(u, s):
    return abs(distance_pl(s.o, u) - s.r) < EPSILON

@check_function
def check_lc(u, s):
    if is_lc(u, s):
        u.circles.add(s)
        s.lines.add(u)

def pc(a, s):
    d = distance_pp(s.o, a)
    if abs(s.r - d) < EPSILON:
        return 0
    if d > s.r:
        return 1
    return -1

def lc(u, s):
    d = distance_pl(s.o, u)
    if abs(s.r - d) < EPSILON:
        return 0
    if d > s.r:
        return 1
    return -1

def cc(s, t):
    d = distance_pp(s.o, t.o)
    if abs(d - s.r - t.r) < EPSILON:
        return 0
    if abs(d - abs(s.r - t.r)) < EPSILON:
        return 0
    if d > s.r + t.r or d < abs(s.r - t.r):
        return 1
    return -1

line_counter = 0
objects = {}

custom_functions = {}

class GFDException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(f"Error in line {line_counter}: " + self.message)

def interpret_check(check_expression):
    pass

def interpret_function(function_expression):
    pass

def interpret_construction(construction_line):
    if "=" not in construction_line:
        raise GFDException(f"no = in line {line_counter}: {construction_line}")
    equal_sign_index = construction_line.index("=")
    lhs = construction_line[:equal_sign_index]
    rhs = interpret_construction_expression(construction_line[equal_sign_index + 1:])
    if len(lhs) != len(rhs):
        raise GFDException(f"lhs ({len(lhs)}) and rhs ({len(rhs)}) do not have the same number of elements")
    for variable_name, obj in zip(lhs, rhs):
        if variable_name == ".":
            continue
        if variable_name in objects:
            raise GFDException(f"{variable_name} is already defined")
        if not issubclass(type(obj), Obj):
            raise GFDException(f"not Obj return in expression")
        obj.name = variable_name
        objects[variable_name] = obj

def interpret_construction_expression(construction_expression):
    stack = []
    for token in construction_expression:
        update_stack(token, stack)
    return stack

def update_stack(token, stack):
    if "*" in token:
        # this token should be in form <function_name>* or <function_name>*<variable_name>
        add_to_figure = True
        asterisk_index = token.index("*")
        name = token[asterisk_index + 1:] if token[asterisk_index + 1:] else None
        token = token[:asterisk_index]
    else:
        add_to_figure = False
    if token in construction_functions:
        construction_function = construction_functions[token]
        args = []
        for arg_type in construction_function.parameters[::-1]:
            arg = stack.pop()
            if not issubclass(type(arg), arg_type):
                raise GFDException(f"{arg} is not of type {arg_type.__name__} for construction function {construction_function.name}")
            args.append(arg)
        args = args[::-1]
        result = construction_function(*args)
        result_lst = list(result) if type(result) == tuple else [result]
        stack.extend(result_lst)
    elif token in custom_functions:
        pass
    else:
        if token not in objects:
            raise GFDException(f"{token} is not defined")
        stack.append(objects[token])

def main():
    global line_counter
    if len(argv) < 2:
        raise GFDException("need a .gfd file")
    filename = argv[1]
    with open(filename, "r+") as file:
        # reverse the lines so that we can use it as a stack
        lines = file.read().splitlines()[::-1]
    while len(lines) > 0:
        line = lines.pop()
        line_counter += 1
        if not line:
            # blank line, ignore
            continue
        tokens = line.split()
        if tokens[0] == "#":
            # comment line, ignore
            continue
        elif tokens[0] == "%":
            # import line, extend the execution stack with the new lines
            if len(tokens) < 2:
                continue
            import_file = tokens[1] if tokens[1].endswith(f".gfd") else tokens[1] + ".gfd"
            with open(import_file, "r+") as file:
                lines.extend(file.read().splitlines()[::-1])
        elif tokens[0] == "?":
            # check line, get a boolean result
            interpret_check(tokens[1:])
        elif tokens[0] == ">":
            # function line, define a function
            interpret_function(tokens[1:])
        else:
            # construction line, define objects
            interpret_construction(tokens)
    # write asy file
    with open("templates/template.asy", "r+") as file:
        point_definitions = "\n".join([p.asy_definition() for p in objects.values() if type(p) == Point])
        draw = "\n".join([obj.asy() for obj in sorted(objects.values(), key=lambda o: (o.order, o.id))])
        template = file.read().replace("FIGURE", point_definitions + "\n\n" + draw)
    with open(f"{filename[:-4]}.asy", "w+") as file:
        file.write(template)
    with open(f"{filename[:-4]}.txt", "w+") as file:
        file.write("\n\n".join(map(lambda o: o.properties(), objects.values())))

if __name__ == "__main__":
    main()
