from functools import wraps # lru_cache
from itertools import product
from inspect import signature
from math import sqrt, atan, pi, sin, cos
from random import random

from objects import Obj, Point, Line, Circle
from exceptions import FigureException

# sets for properties that will be filled by the check functions
point_on_line = set()
point_on_circle = set()
line_tangent_to_circle = set()
line_perpendicular = set()
line_parallel = set()
circle_tangent_to_circle = set()
collinear = set()
concyclic = set()
concurrent = set()

# dictionary of the properties imported from main.py
properties = {
    "point on line": point_on_line,
    "point on circle": point_on_circle,
    "line tangent to circle": line_tangent_to_circle,
    "line perpendicular to line": line_perpendicular,
    "line parallel to line": line_parallel,
    "circle tangent to circle": circle_tangent_to_circle,
    "collinear points": collinear,
    "concyclic points": concyclic,
    "concurrent lines": concurrent,
}

# dict<function_name: str, function: ConstructionFunction> imported from main.py
construction_functions = {}

check_functions = {}

# construction and check functions always use the this predefined set of parameter names, they indicate the type
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
    """
    represents a construction function and is created when a construction function (which is a function with the decorator @construction_function(), it performs some geometrical operations on the inputs and outputs another objects) is defined

    function: function
        the actual function
    name: str
        name of the function
    parameters: list[Point/Line/Circle/Obj]
        parameter types of the function extracted from the signature
    """
    def __init__(self, func):
        self.function = func
        self.name = self.function.__name__
        self.parameters = [parameter_mapping[x] for x in signature(self.function).parameters]
    
    def __repr__(self):
        return f"Construction Function {self.name} that takes {len(self)} parameters, {[cls.__name__ for cls in self.parameters]}"
    
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
    
    def __len__(self):
        return len(self.parameters)

# construction function decorator
def construction_function(cache=4):
    def construction_function_decorator(func):
        # @lru_cache(maxsize=cache)
        @wraps(func)
        def checked_construction_function(*args, **kwargs):
            result = func(*args, **kwargs)

            # result is either a single Obj or a tuple of Objs, convert it to a list
            result_lst = list(result) if type(result) == tuple else [result]

            # for input and output objects, make every claim and check if true, this will be the known properties
            combined = list(args) + result_lst
            for check_function in check_functions.values():
                for check_function_arguments in product(*[[x for x in combined if type(x) == cls] for cls in check_function.parameters]):
                    if len(set(check_function_arguments)) != len(check_function_arguments):
                        # not all different
                        continue
                    check_function(*check_function_arguments)
            return result
        construction_functions[func.__name__] = ConstructionFunction(checked_construction_function)
        return checked_construction_function
    return construction_function_decorator

class CheckFunction:
    """
    represents a check function and is created when a check function (which is a function with the decorator @check_function(), it performs some calculations to check if a property is satisfied) is defined

    function: function
        the actual function
    name: str
        name of the function
    parameters: list[Point/Line/Circle/Obj]
        parameter types of the function extracted from the signature
    """
    def __init__(self, func):
        self.function = func
        self.name = self.function.__name__
        self.parameters = [parameter_mapping[x] for x in signature(self.function).parameters]
    
    def __repr__(self):
        return f"Check Function {self.name} that takes {len(self)} parameters, {[cls.__name__ for cls in self.parameters]}"
    
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
    
    def __len__(self):
        return len(self.parameters)

# check function decorator
def check_function(s):
    def check_function_decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            if result:
                s.add(tuple(sorted(args, key=lambda obj: obj.criteria())))
            return result
        check_functions[func.__name__] = CheckFunction(inner)
        return inner
    return check_function_decorator

# since we are dealing with computer floats, use epsilon instead of hard 0
EPSILON = 1e-5

# helper function
def solve_quadratic(a, b, c):
    d = b * b - 4 * a  *c
    if abs(d) < EPSILON:
        return True, 1, -b / 2 * a, -b / 2 * a
    if d < 0:
        return False, 0, None, None
    return True, 2, (-b - sqrt(d)) / (2 * a), (-b + sqrt(d)) / (2 * a)

# calculation functions

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

def pc(a, s):
    """
    1  if a is outside of s
    0  if a is on s
    -1 if a is inside of s
    """
    d = distance_pp(s.o, a)
    if abs(s.r - d) < EPSILON:
        return 0
    if d > s.r:
        return 1
    return -1

def lc(u, s):
    """
    1  if l doesnt intersect s
    0  if l is tangent to s
    -1 if l intersects s at two points
    """
    d = distance_pl(s.o, u)
    if abs(s.r - d) < EPSILON:
        return 0
    if d > s.r:
        return 1
    return -1

def cc(s, t):
    """
    1  if s and t dont intersect
    0  if s and t are tangent
    -1 if s and t intersect at two points
    """
    d = distance_pp(s.o, t.o)
    if abs(d - s.r - t.r) < EPSILON:
        return 0
    if abs(d - abs(s.r - t.r)) < EPSILON:
        return 0
    if d > s.r + t.r or d < abs(s.r - t.r):
        return 1
    return -1

# construction functions

## no arguments

@construction_function()
def triangle():
    """predefined triangle"""
    a = Point(-0.256, 0.966)
    b = Point(-0.905, -0.426)
    c = Point(0.943, -0.333)
    return a, b, c

@construction_function()
def unit_circle():
    """unit circle"""
    return Circle(Point(0, 0), 1)

## random

@construction_function(cache=0)
def random_point_on_circle(s):
    """random point on circle"""
    t = random() * 2 * pi
    return Point(s.o.x + s.r * cos(t), s.o.y + s.r * sin(t))

@construction_function(cache=0)
def random_point_on_unit_circle():
    """random point on unit circle"""
    return random_point_on_circle(unit_circle())

@construction_function(cache=0)
def random_point_on_segment(a, b):
    """random point on the line segment ab"""
    t = random()
    return Point(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t)

def random_point_on_arc(s, angle1, angle2, radian=True):
    t = angle1 + random() * (angle2 - angle1)
    t = t if radian else t * pi / 180
    return Point(s.o.x + s.r * cos(t), s.o.y + s.r * sin(t))

@construction_function(cache=0)
def random_point_on_arc2(s, a, b):
    """random point on the arc ab of circle s, requires a and b to be on s"""
    pass

@construction_function(cache=0)
def random_point():
    """random point on unit circle"""
    return random_point_on_unit_circle()

@construction_function(cache=0)
def random_line():
    """random line passing through two random points on the unit circle"""
    return line(random_point(), random_point())

@construction_function(cache=0)
def random_circle():
    """random circle whose center is on the unit circle and has a radius between 0 and 1"""
    return Circle(random_point(), random())

@construction_function(cache=0)
def random_triangle_on_circle(s):
    """random triangle on circle s"""
    a = random_point_on_circle(s)
    b = random_point_on_circle(s)
    c = random_point_on_circle(s)
    return a, b, c

@construction_function(cache=0)
def random_triangle_on_unit_circle():
    """random triangle on unit circle"""
    return random_triangle_on_circle(unit_circle())

@construction_function(cache=0)
def random_nice_triangle():
    """random nice triangle, angles close to 60, 45, 75"""
    x = 5
    a = random_point_on_arc(unit_circle(), 120 - x, 120 + x, radian=False)
    b = random_point_on_arc(unit_circle(), 210 - x, 210 + x, radian=False)
    c = random_point_on_arc(unit_circle(), 330 - x, 330 + x, radian=False)
    return a, b, c

## c

@construction_function()
def center(s):
    """center of s"""
    return s.o

## pp

@construction_function()
def midpoint(a, b):
    """midpoint of ab"""
    return Point((a.x + b.x) / 2, (a.y + b.y) / 2)

@construction_function()
def line(a, b):
    """line ab"""
    return Line(b.y - a.y, a.x - b.x, a.x * b.y - a.y * b.x)

@construction_function()
def perpendicular_bisector(a, b):
    """perpendicular bisector of ab"""
    return Line(a.x - b.x, a.y - b.y, (a.x ** 2 + a.y ** 2 - b.x ** 2 - b.y ** 2) / 2)

@construction_function()
def circle_diameter(a, b):
    """circle with diameter ab"""
    return Circle(midpoint(a, b), distance_pp(a, b) / 2)

@construction_function()
def reflection_pp(a, b):
    """reflection of a over b"""
    return Point(2 * b.x - a.x, 2 * b.y - a.y)

@construction_function()
def perpendicular_through(a, b):
    """line through a perpendicular to ab"""
    return Line(a.x - b.x, a.y - b.y, a.x ** 2 + a.y ** 2 - a.x * b.x - a.y * b.y)

@construction_function()
def circle_centered(a, b):
    """circle centered a through b"""
    return Circle(a, distance_pp(a, b))

## pl

@construction_function()
def reflection_pl(a, u):
    """reflection of a over u"""
    return reflection_pp(a, foot(a, u))

@construction_function()
def foot(a, u):
    """foot of a on u"""
    return intersection_ll(u, perpendicular_line(a, u))

@construction_function()
def perpendicular_line(a, u):
    """line through a perpendicular to u"""
    return Line(u.b, -u.a, a.x * u.b - a.y * u.a)

@construction_function()
def parallel_line(a, u):
    """line through a parallel to u"""
    return Line(u.a, u.b, a.x * u.a + a.y * u.b)

## pc

@construction_function()
def tangent_points(a, s):
    """touch points of tangents from a to s, requires a to be outside of s"""
    if pc(a, s) != 1:
        raise FigureException(f"Point {a.name} is not outside of circle {s.name} in construction function tangent_points")
    return intersections_cc(s, circle_diameter(a, s.o))

@construction_function()
def tangent_lines(a, s):
    """tangent lines from a to s, requires a to be outside of s"""
    tp1, tp2 = tangent_points(a, s)
    return line(a, tp1), line(a, tp2)

@construction_function()
def tangent_line(a, s):
    """line through a tangent to s, requires a to be on s"""
    if pc(a, s) != 0:
        raise FigureException(f"Point {a.name} is not on circle {s.name} in construction function tangent_lines")
    return perpendicular_through(a, s.o)

@construction_function()
def polar(a, s):
    """polar line of a wrt s, requires a to not be center of s"""
    if distance_pp(a, s.o) < EPSILON:
        raise FigureException(f"Point {a.name} is the center of circle {s.name} in construction function polar")
    d = (s.r / distance_pp(a, s.o)) ** 2
    p = Point(s.o.x + d * (a.x - s.o.x), s.o.y + d * (a.y - s.o.y))
    return perpendicular_through(p, s.o)

## ll

@construction_function()
def intersection_ll(u, v):
    """intersection of u and v, requires u and v to not be parallel"""
    if is_parallel(u, v):
        raise FigureException(f"Line {u.name} and {v.name} are parallel in construction function intersection_ll")
    return Point((u.c * v.b - u.b * v.c) / (u.a * v.b - u.b * v.a), (u.c * v.a - u.a * v.c) / (u.b * v.a - u.a * v.b))

@construction_function()
def angle_bisector(u, v):
    """angle bisector of u and v, considers orientation"""
    return Line(u.a / sqrt(u.a ** 2 + u.b ** 2) + v.a / sqrt(v.a ** 2 + v.b ** 2), u.b / sqrt(u.a ** 2 + u.b ** 2) + v.b / sqrt(v.a ** 2 + v.b ** 2), u.c / sqrt(u.a ** 2 + u.b ** 2) + v.c / sqrt(v.a ** 2 + v.b ** 2))

@construction_function()
def reflection_ll(u, v):
    """reflection of u over v, requires u and v to not be parallel"""
    i = intersection_ll(u, v)
    x, y = i.x, i.y
    m = u.a * v.b * v.b - u.a * v.a * v.a - 2 * u.b * v.a * v.b
    n = u.b * v.b * v.b - u.b * v.a * v.a - 2 * u.a * v.a * v.b
    return Line(m, -n, x * m - y * n)

## lc

@construction_function()
def intersections_lc(u, s):
    """intersection points of u and s, requires u and s to intersect"""
    if lc(u, s) != -1:
        raise FigureException(f"Line {u.name} does not intersect Circle {s.name} in construction function intersections_lc")
    a = u.a ** 2 + u.b ** 2
    b = 2 * (s.o.y * u.a * u.b - s.o.x * u.b * u.b - u.a * u.c)
    c = (s.o.x ** 2) * (u.b ** 2) + (u.c ** 2) - 2 * s.o.y * u.b * u.c + (s.o.y ** 2) * (u.b ** 2) - (s.r ** 2) * (u.b ** 2)
    _, _, x1, x2 = solve_quadratic(a, b, c)
    y1 = (u.c - u.a * x1) / u.b
    y2 = (u.c - u.a * x2) / u.b
    return Point(x1, y1), Point(x2, y2)

@construction_function()
def intersection_lc(u, s):
    """tangent point of u and s, requires u and s to be tangent"""
    if lc(u, s) != 0:
        raise FigureException(f"Line {u.name} is not tangent circle {s.name} in construction function tangent_points")
    return foot(s.o, u)

@construction_function()
def tangent_point(u, s):
    """tangent point of u and s, requires u and s to be tangent"""
    if lc(u, s) != 0:
        raise FigureException(f"Line {u.name} is not tangent circle {s.name} in construction function tangent_points")
    return foot(s.o, u)

@construction_function()
def pole(u, s):
    """pole point of u wrt s, requires u to not pas through center of s"""
    if distance_pl(s.o, u) < EPSILON:
        raise FigureException(f"Line {u.name} passes through the center of circle {s.name} in construction function pole")
    d = (s.r / distance_pl(s.o, u)) ** 2
    a = foot(s.o, u)
    return Point(s.o.x + d * (a.x - s.o.x), s.o.y + d * (a.y - s.o.y))

## cc

@construction_function()
def intersections_cc(s, t):
    """intersection points of s and t, requires s and t to intersect"""
    if cc(s, t) != -1:
        raise FigureException(f"Circle {s.name} and {t.name} do not intersect in construction function intersections_cc")
    return intersections_lc(radical_axis(s, t), s)

@construction_function()
def intersection_cc(s, t):
    """tangent point of s and t, requires s and t to be tangent"""
    if cc(s, t) != 0:
        raise FigureException(f"Circle {s.name} and {t.name} are not tangent in construction function intersection_cc")
    return intersection_ll(line(s.o, t.o), radical_axis(s, t))

@construction_function()
def radical_axis(s, t):
    """radical axis of s and t"""
    return Line(2 * (s.o.x - t.o.x), 2 * (s.o.y - t.o.y), t.r ** 2 - s.r ** 2 + s.o.x ** 2 - t.o.x ** 2 + s.o.y ** 2 - t.o.y ** 2)

@construction_function()
def tangent_points_external(s, t):
    """external tangent points of s and t, requires ..."""
    p1, p2 = tangent_points(tangent_intersection_external(s, t), s)
    p3, p4 = tangent_points(tangent_intersection_external(s, t), t)
    return p1, p2, p3, p4

@construction_function()
def tangent_points_internal(s, t):
    """internal tangent points of s and t, requires ..."""
    p1, p2 = tangent_points(tangent_intersection_internal(s, t), s)
    p3, p4 = tangent_points(tangent_intersection_internal(s, t), t)
    return p1, p2, p3, p4

@construction_function()
def tangent_intersection_external(s, t):
    """intersection of external tangents of s and t, requires ..."""
    return Point((s.o.x * t.r - t.o.x * s.r) / (t.r - s.r), (s.o.y * t.r - t.o.y * s.r) / (t.r - s.r))

@construction_function()
def tangent_intersection_internal(s, t):
    """intersection of internal tangents of s and t, requires ..."""
    return Point((s.o.x * t.r + t.o.x * s.r) / (t.r + s.r), (s.o.y * t.r + t.o.y * s.r) / (t.r + s.r))

@construction_function()
def tangent_lines_external(s, t):
    """external tangents of s and t, requires ..."""
    return tangent_lines(tangent_intersection_external(s, t), s)

@construction_function()
def tangent_lines_internal(s, t):
    """internal tangents of s and t, requires ..."""
    return tangent_lines(tangent_intersection_internal(s, t), s)

## ppp

@construction_function()
def internal_angle_bisector(a, b, c):
    """internal angle bisector of angle bac"""
    return angle_bisector(line(a, b), line(c, a))

@construction_function()
def external_angle_bisector(a, b, c):
    """external angle bisector of angle bac"""
    return angle_bisector(line(a, b), line(a, c))

@construction_function()
def altitude(a, b, c):
    """altitude from a to bc"""
    return perpendicular_line(a, line(b, c))

@construction_function()
def median(a, b, c):
    """median from a to bc"""
    return line(a, midpoint(b, c))

@construction_function()
def foot_ppp(a, b, c):
    """foot from a to bc"""
    return foot(a, line(b, c))

@construction_function()
def circumcenter(a, b, c):
    """circumcenter of abc"""
    return intersection_ll(perpendicular_bisector(a, b), perpendicular_bisector(a, c))

@construction_function()
def circumradius(a, b, c):
    """circumradius of abc"""
    return distance_pp(a, circumcenter(a, b, c))

@construction_function()
def circumcircle(a, b, c):
    """circumcircle of abc"""
    return Circle(circumcenter(a, b, c), circumradius(a, b, c))

@construction_function()
def incenter(a, b, c):
    """incenter of abc"""
    return intersection_ll(internal_angle_bisector(b, c, a), internal_angle_bisector(c, a, b))

@construction_function()
def inradius(a, b, c):
    """inradius of abc"""
    return distance_pl(incenter(a, b, c), line(b, c))

@construction_function()
def incircle(a, b, c):
    """incircle of abc"""
    return Circle(incenter(a, b, c), inradius(a, b, c))

@construction_function()
def excenter(a, b, c):
    """a-excenter of abc"""
    return intersection_ll(external_angle_bisector(b, c, a), external_angle_bisector(c, a, b))

@construction_function()
def exradius(a, b, c):
    """a-exradius of abc"""
    return distance_pl(excenter(a, b, c), line(b, c))

@construction_function()
def excircle(a, b, c):
    """a-excircle of abc"""
    return Circle(excenter(a, b, c), exradius(a, b, c))

@construction_function()
def orthocenter(a, b, c):
    """orthocenter of abc"""
    return intersection_ll(altitude(b, c, a), altitude(c, a, b))

@construction_function()
def centroid(a, b, c):
    """centroid of abc"""
    return Point((a.x + b.x + c.x) / 3, (a.y + b.y + c.y) / 3)

# check functions

@check_function(collinear)
def is_collinear(a, b, c):
    """a, b, c are collinear"""
    return distance_pl(a, line(b, c)) < EPSILON

@check_function(concyclic)
def is_concyclic(a, b, c, d):
    """a, b, c, d are concyclic"""
    return abs(angle(line(a, b), line(a, c)) - angle(line(d, b), line(d, c))) < EPSILON and abs(angle(line(b, a), line(b, c)) - angle(line(d, a), line(d, c))) < EPSILON

@check_function(concurrent)
def is_concurrent(u, v, w):
    """u, v, w are concurrent"""
    return abs(u.a * v.c * w.b + u.b * v.a * w.c + u.c * v.b * w.a - u.a * v.b * w.c - u.b * v. c * w.a - u.c * v.a * w.b) < EPSILON

@check_function(line_parallel)
def is_parallel(u, v):
    """u and v are parallel"""
    return angle(u, v) < EPSILON

@check_function(line_perpendicular)
def is_perpendicular(u, v):
    """u and v are perpendicular"""
    return pi / 2 - angle(u, v) < EPSILON

@check_function(circle_tangent_to_circle)
def is_tangent(s, t):
    """s and t are tangent"""
    return abs(distance_pc(s.o, t) - s.r) < EPSILON

@check_function(point_on_line)
def is_pl(a, u):
    """a is on u"""
    return distance_pl(a, u) < EPSILON

@check_function(point_on_circle)
def is_pc(a, s):
    """a is on s"""
    return distance_pc(a, s) < EPSILON

@check_function(line_tangent_to_circle)
def is_lc(u, s):
    """u is tangent to s"""
    return abs(distance_pl(s.o, u) - s.r) < EPSILON
