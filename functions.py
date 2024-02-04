from functools import wraps
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

# dict[str, ConstructionFunction], name -> function, imported from main.py
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

def check_everything(objects):
    for check_function in check_functions.values():
        for check_function_arguments in product(*[[x for x in objects if type(x) == cls] for cls in check_function.parameters]):
            if len(set(check_function_arguments)) != len(check_function_arguments):
                # not all different
                continue
            check_function(*check_function_arguments)

# construction function decorator
def construction_function():
    def construction_function_decorator(func):
        @wraps(func)
        def checked_construction_function(*args, **kwargs):
            result = func(*args, **kwargs)

            # result is either a single Obj or a tuple of Objs, convert it to a list
            result_lst = list(result) if type(result) == tuple else [result]

            for obj in result_lst:
                if not obj.recipe_parent_depth_set:
                    obj.parents = args
                    obj.recipe = func.__name__
                    obj.depth = 1 + (max(map(lambda obj: obj.depth, args)) if args else -1)

            # for input and output objects, make every claim and check if true, this will be the known properties
            combined = list(args) + result_lst
            check_everything(combined)
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
def solve_quadratic(a, b, c) -> tuple[bool, int, float, float]:
    """returns (solution exists or not, number of different solutions, solution1, solution2)"""
    d = b * b - 4 * a  *c
    if abs(d) < EPSILON:
        return True, 1, -b / 2 * a, -b / 2 * a
    if d < 0:
        return False, 0, None, None
    return True, 2, (-b - sqrt(d)) / (2 * a), (-b + sqrt(d)) / (2 * a)

# calculation functions

def distance_pp(a, b) -> float:
    return sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def distance_pl(a, u) -> float:
    return abs(u(a)) / sqrt(u.a ** 2 + u.b ** 2)

def distance_pc(a, s) -> float:
    return abs(s.r - distance_pp(s.o, a))

def distance_lc(u, s) -> float:
    return abs(s.r - distance_pl(s.o, u))

def angle(u, v) -> float:
    x = u.a * v.a + u.b * v.b
    return abs(atan((v.a * u.b - u.a * v.b) / x)) if x else pi / 2

def pc(a, s) -> int:
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

def lc(u, s) -> int:
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

def cc(s, t) -> int:
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

def random_point_on_arc_angle(s, angle1, angle2, radian=True):
    """random point on circle s between angles a1 and a2"""
    k = 1 if radian else pi / 180
    angle1 = (angle1 * k) % (2 * pi)
    angle2 = (angle2 * k) % (2 * pi)
    if angle2 < angle1:
        angle2 = angle2 + 2 * pi
    t = angle1 + random() * (angle2 - angle1)
    return Point(s.o.x + s.r * cos(t), s.o.y + s.r * sin(t))

def angle_ps(s, a):
    """angle of a wrt s, requires a to be on s"""
    if not is_pc(a, s):
        raise FigureException(f"Point {a.name} is not on circle {s.name} in angle_ps")
    dx = a.x - s.o.x
    dy = a.y - s.o.y
    u = atan(dy / dx)
    if dx > 0:
        if dy > 0:
            return u
        else:
            return 2 * pi + u
    else:
        if dy > 0:
            return pi + u
        else:
            return pi + u

def same_side_of_line(a, b, u):
    """whether a and b lie on the same side of line u, requires a and b to not be on u"""
    if is_pl(a, u) or is_pl(b, u):
        raise FigureException("a or b lie on u in same_side_of_line function")
    return u(a) * u(b) > 0

# construction functions

## no arguments

@construction_function()
def triangle() -> tuple[Point, Point, Point]:
    """predefined triangle"""
    a = Point(-0.256, 0.966)
    b = Point(-0.905, -0.426)
    c = Point(0.943, -0.333)
    return a, b, c

@construction_function()
def unit_circle() -> Circle:
    """unit circle"""
    return Circle(Point(0, 0), 1)

## random

@construction_function()
def random_point_on_circle(s) -> Point:
    """random point on circle s"""
    t = random() * 2 * pi
    return Point(s.o.x + s.r * cos(t), s.o.y + s.r * sin(t))

@construction_function()
def random_point_on_unit_circle() -> Point:
    """random point on unit circle"""
    return random_point_on_circle(unit_circle())

@construction_function()
def random_point_on_segment(a, b) -> Point:
    """random point on the line segment ab"""
    t = random()
    return Point(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t)

@construction_function()
def random_point_on_arc(s, a, b):
    """random point on the arc ab of circle s, requires a and b to be on s"""
    if not is_pc(a, s) or not is_pc(b, s):
        raise FigureException(f"Points {a.name} or {b.name} is not on circle {s.name} in construction function random_point_on_arc")
    return random_point_on_arc_angle(s, angle_ps(a, s), angle_ps(b, s))

@construction_function()
def random_point() -> Point:
    """random point on unit circle"""
    return random_point_on_unit_circle()

@construction_function()
def random_line() -> Line:
    """random line passing through two random points on the unit circle"""
    return line(random_point(), random_point())

@construction_function()
def random_circle() -> Circle:
    """random circle whose center is on the unit circle and has a radius between 0 and 1"""
    return Circle(random_point(), random())

@construction_function()
def random_triangle_on_circle(s) -> tuple[Point, Point, Point]:
    """random triangle on circle s"""
    a = random_point_on_circle(s)
    b = random_point_on_circle(s)
    c = random_point_on_circle(s)
    return a, b, c

@construction_function()
def random_triangle_on_unit_circle() -> tuple[Point, Point, Point]:
    """random triangle on unit circle"""
    return random_triangle_on_circle(unit_circle())

@construction_function()
def random_nice_triangle() -> tuple[Point, Point, Point]:
    """random nice triangle, angles close to 60, 45, 75"""
    x = 5
    a = random_point_on_arc_angle(unit_circle(), 120 - x, 120 + x, radian=False)
    b = random_point_on_arc_angle(unit_circle(), 210 - x, 210 + x, radian=False)
    c = random_point_on_arc_angle(unit_circle(), 330 - x, 330 + x, radian=False)
    return a, b, c

@construction_function()
def random_line_through_point(a):
    """random line through point a"""
    b = random_point_on_circle(Circle(a, 1))
    return line(a, b)

## c

@construction_function()
def center(s) -> Point:
    """center of s"""
    return s.o

## pp

@construction_function()
def midpoint(a, b) -> Point:
    """midpoint of ab"""
    return Point((a.x + b.x) / 2, (a.y + b.y) / 2)

@construction_function()
def line(a, b) -> Line:
    """line ab"""
    return Line(b.y - a.y, a.x - b.x, a.x * b.y - a.y * b.x)

@construction_function()
def perpendicular_bisector(a, b) -> Line:
    """perpendicular bisector of ab"""
    return Line(a.x - b.x, a.y - b.y, (a.x ** 2 + a.y ** 2 - b.x ** 2 - b.y ** 2) / 2)

@construction_function()
def circle_diameter(a, b) -> Circle:
    """circle with diameter ab"""
    return Circle(midpoint(a, b), distance_pp(a, b) / 2)

@construction_function()
def reflection_pp(a, b) -> Point:
    """reflection of a over b"""
    return Point(2 * b.x - a.x, 2 * b.y - a.y)

@construction_function()
def perpendicular_through(a, b) -> Line:
    """line through a perpendicular to ab"""
    return Line(a.x - b.x, a.y - b.y, a.x ** 2 + a.y ** 2 - a.x * b.x - a.y * b.y)

@construction_function()
def circle_centered(a, b) -> Circle:
    """circle centered a through b"""
    return Circle(a, distance_pp(a, b))

## pl

@construction_function()
def reflection_pl(a, u) -> Point:
    """reflection of a over u"""
    return reflection_pp(a, foot(a, u))

@construction_function()
def foot(a, u) -> Point:
    """foot of a on u"""
    return intersection_ll(u, perpendicular_line(a, u))

@construction_function()
def perpendicular_line(a, u) -> Line:
    """line through a perpendicular to u"""
    return Line(u.b, -u.a, a.x * u.b - a.y * u.a)

@construction_function()
def parallel_line(a, u) -> Line:
    """line through a parallel to u"""
    return Line(u.a, u.b, a.x * u.a + a.y * u.b)

## pc

@construction_function()
def tangent_points(a, s) -> tuple[Point, Point]:
    """touch points of tangents from a to s, requires a to be outside of s"""
    if pc(a, s) != 1:
        raise FigureException(f"Point {a.name} is not outside of circle {s.name} in construction function tangent_points")
    return intersections_cc(s, circle_diameter(a, s.o))

@construction_function()
def tangent_lines(a, s) -> tuple[Line, Line]:
    """tangent lines from a to s, requires a to be outside of s"""
    tp1, tp2 = tangent_points(a, s)
    return line(a, tp1), line(a, tp2)

@construction_function()
def tangent_line(a, s) -> Line:
    """line through a tangent to s, requires a to be on s"""
    if not is_pc(a, s):
        raise FigureException(f"Point {a.name} is not on circle {s.name} in construction function tangent_lines")
    return perpendicular_through(a, s.o)

@construction_function()
def polar(a, s) -> Line:
    """polar line of a wrt s, requires a to not be center of s"""
    if distance_pp(a, s.o) < EPSILON:
        raise FigureException(f"Point {a.name} is the center of circle {s.name} in construction function polar")
    d = (s.r / distance_pp(a, s.o)) ** 2
    p = Point(s.o.x + d * (a.x - s.o.x), s.o.y + d * (a.y - s.o.y))
    return perpendicular_through(p, s.o)

## ll

@construction_function()
def intersection_ll(u, v) -> Point:
    """intersection of u and v, requires u and v to not be parallel"""
    if is_parallel(u, v):
        raise FigureException(f"Line {u.name} and {v.name} are parallel in construction function intersection_ll")
    return Point((u.c * v.b - u.b * v.c) / (u.a * v.b - u.b * v.a), (u.c * v.a - u.a * v.c) / (u.b * v.a - u.a * v.b))

@construction_function()
def angle_bisector(u, v) -> Line:
    """angle bisector of u and v"""
    return Line(u.a / sqrt(u.a ** 2 + u.b ** 2) + v.a / sqrt(v.a ** 2 + v.b ** 2), u.b / sqrt(u.a ** 2 + u.b ** 2) + v.b / sqrt(v.a ** 2 + v.b ** 2), u.c / sqrt(u.a ** 2 + u.b ** 2) + v.c / sqrt(v.a ** 2 + v.b ** 2))

@construction_function()
def angle_bisector2(u, v) -> Line:
    """angle bisector of u and v, other"""
    return Line(u.a / sqrt(u.a ** 2 + u.b ** 2) - v.a / sqrt(v.a ** 2 + v.b ** 2), u.b / sqrt(u.a ** 2 + u.b ** 2) - v.b / sqrt(v.a ** 2 + v.b ** 2), u.c / sqrt(u.a ** 2 + u.b ** 2) - v.c / sqrt(v.a ** 2 + v.b ** 2))

@construction_function()
def reflection_ll(u, v) -> Line:
    """reflection of u over v, requires u and v to not be parallel"""
    i = intersection_ll(u, v)
    x, y = i.x, i.y
    m = u.a * v.b * v.b - u.a * v.a * v.a - 2 * u.b * v.a * v.b
    n = u.b * v.b * v.b - u.b * v.a * v.a - 2 * u.a * v.a * v.b
    return Line(m, -n, x * m - y * n)

## lc

@construction_function()
def intersections_lc(u, s) -> tuple[Point, Point]:
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
def intersection_lc(u, s) -> Point:
    """tangent point of u and s, requires u and s to be tangent"""
    if not is_lc(u, s):
        raise FigureException(f"Line {u.name} is not tangent to circle {s.name} in construction function tangent_points")
    return foot(s.o, u)

@construction_function()
def tangent_point(u, s) -> Point:
    """tangent point of u and s, requires u and s to be tangent"""
    if not is_lc(u, s):
        raise FigureException(f"Line {u.name} is not tangent to circle {s.name} in construction function tangent_points")
    return foot(s.o, u)

@construction_function()
def pole(u, s) -> Point:
    """pole point of u wrt s, requires u to not pas through center of s"""
    if is_pl(s.o, u):
        raise FigureException(f"Line {u.name} passes through the center of circle {s.name} in construction function pole")
    d = (s.r / distance_pl(s.o, u)) ** 2
    a = foot(s.o, u)
    return Point(s.o.x + d * (a.x - s.o.x), s.o.y + d * (a.y - s.o.y))

## cc

@construction_function()
def intersections_cc(s, t) -> tuple[Point, Point]:
    """intersection points of s and t, requires s and t to intersect"""
    if cc(s, t) != -1:
        raise FigureException(f"Circle {s.name} and {t.name} do not intersect in construction function intersections_cc")
    return intersections_lc(radical_axis(s, t), s)

@construction_function()
def intersection_cc(s, t) -> Point:
    """tangent point of s and t, requires s and t to be tangent"""
    if not is_tangent(s, t):
        raise FigureException(f"Circle {s.name} and {t.name} are not tangent in construction function intersection_cc")
    return intersection_ll(line(s.o, t.o), radical_axis(s, t))

@construction_function()
def radical_axis(s, t) -> Line:
    """radical axis of s and t"""
    return Line(2 * (s.o.x - t.o.x), 2 * (s.o.y - t.o.y), t.r ** 2 - s.r ** 2 + s.o.x ** 2 - t.o.x ** 2 + s.o.y ** 2 - t.o.y ** 2)

@construction_function()
def tangent_points_external(s, t) -> tuple[Point, Point, Point, Point]:
    """external tangent points of s and t, requires ..."""
    p1, p2 = tangent_points(tangent_intersection_external(s, t), s)
    p3, p4 = tangent_points(tangent_intersection_external(s, t), t)
    return p1, p2, p3, p4

@construction_function()
def tangent_points_internal(s, t) -> tuple[Point, Point, Point, Point]:
    """internal tangent points of s and t, requires ..."""
    p1, p2 = tangent_points(tangent_intersection_internal(s, t), s)
    p3, p4 = tangent_points(tangent_intersection_internal(s, t), t)
    return p1, p2, p3, p4

@construction_function()
def tangent_intersection_external(s, t) -> Point:
    """intersection of external tangents of s and t, requires ..."""
    return Point((s.o.x * t.r - t.o.x * s.r) / (t.r - s.r), (s.o.y * t.r - t.o.y * s.r) / (t.r - s.r))

@construction_function()
def tangent_intersection_internal(s, t) -> Point:
    """intersection of internal tangents of s and t, requires ..."""
    return Point((s.o.x * t.r + t.o.x * s.r) / (t.r + s.r), (s.o.y * t.r + t.o.y * s.r) / (t.r + s.r))

@construction_function()
def tangent_lines_external(s, t) -> tuple[Line, Line]:
    """external tangents of s and t, requires ..."""
    return tangent_lines(tangent_intersection_external(s, t), s)

@construction_function()
def tangent_lines_internal(s, t) -> tuple[Line, Line]:
    """internal tangents of s and t, requires ..."""
    return tangent_lines(tangent_intersection_internal(s, t), s)

## ppp

@construction_function()
def internal_angle_bisector(a, b, c) -> Line:
    """internal angle bisector of angle bac"""
    option1 = angle_bisector(line(a, b), line(a, c))
    option2 = angle_bisector2(line(a, b), line(a, c))
    return option1 if not same_side_of_line(b, c, option1) else option2

@construction_function()
def external_angle_bisector(a, b, c) -> Line:
    """external angle bisector of angle bac"""
    option1 = angle_bisector(line(a, b), line(a, c))
    option2 = angle_bisector2(line(a, b), line(a, c))
    return option1 if same_side_of_line(b, c, option1) else option2

@construction_function()
def altitude(a, b, c) -> Line:
    """altitude from a to bc"""
    return perpendicular_line(a, line(b, c))

@construction_function()
def median(a, b, c) -> Line:
    """median from a to bc"""
    return line(a, midpoint(b, c))

@construction_function()
def foot_ppp(a, b, c) -> Point:
    """foot from a to bc"""
    return foot(a, line(b, c))

@construction_function()
def circumcenter(a, b, c) -> Point:
    """circumcenter of abc"""
    return intersection_ll(perpendicular_bisector(a, b), perpendicular_bisector(a, c))

def circumradius(a, b, c) -> float:
    """circumradius of abc"""
    return distance_pp(a, circumcenter(a, b, c))

@construction_function()
def circumcircle(a, b, c) -> Circle:
    """circumcircle of abc"""
    return Circle(circumcenter(a, b, c), circumradius(a, b, c))

@construction_function()
def incenter(a, b, c) -> Point:
    """incenter of abc"""
    return intersection_ll(internal_angle_bisector(b, a, c), internal_angle_bisector(c, a, b))

def inradius(a, b, c) -> float:
    """inradius of abc"""
    return distance_pl(incenter(a, b, c), line(b, c))

@construction_function()
def incircle(a, b, c) -> Circle:
    """incircle of abc"""
    return Circle(incenter(a, b, c), inradius(a, b, c))

@construction_function()
def excenter(a, b, c) -> Point:
    """a-excenter of abc"""
    return intersection_ll(external_angle_bisector(b, c, a), external_angle_bisector(c, a, b))

def exradius(a, b, c) -> float:
    """a-exradius of abc"""
    return distance_pl(excenter(a, b, c), line(b, c))

@construction_function()
def excircle(a, b, c) -> Circle:
    """a-excircle of abc"""
    return Circle(excenter(a, b, c), exradius(a, b, c))

@construction_function()
def orthocenter(a, b, c) -> Point:
    """orthocenter of abc"""
    return intersection_ll(altitude(b, c, a), altitude(c, a, b))

@construction_function()
def centroid(a, b, c) -> Point:
    """centroid of abc"""
    return Point((a.x + b.x + c.x) / 3, (a.y + b.y + c.y) / 3)

## extra

@construction_function()
def second_intersection_plc(a, u, s) -> Point:
    """intersection of u and s other than a, requires a to be on u and s, requires u and s to intersect"""
    if lc(u, s) != -1:
        raise FigureException(f"Line {u.name} and {s.name} do not intersect in construction function second_intersection_plc")
    if not is_pl(a, u) or not is_pc(a, s):
        raise FigureException(f"Point {a.name} is not on line {u.name} or circle {s.name} in construction function second_intersection_plc")
    b, c = intersections_lc(u, s)
    return b if distance_pp(a, c) < EPSILON else c

@construction_function()
def second_intersection_pcc(a, s, t) -> Point:
    """intersection of s and t other than a, requires a to be on s and t, requires s and t to intersect"""
    if cc(s, t) != -1:
        raise FigureException(f"Circles {s.name} and {t.name} do not intersect in construction function second_intersection_pcc")
    if not is_pc(a, s) or not is_pc(a, t):
        raise FigureException(f"Point {a.name} is not on circles {s.name} and {t.name} in construction function second_intersection_pcc")
    b, c = intersections_cc(s, t)
    return b if distance_pp(a, c) < EPSILON else c

@construction_function()
def midpoint_of_arc(a, b, s):
    """midpoint of arc ab of circle s, requires a and b to be on s"""
    if not is_pc(a, s) or not is_pc(b, s):
        raise FigureException(f"Point {a.name} or {b.name} is not on circle {s.name} in construction function midpoint_of_arc")
    return intersections_lc(perpendicular_bisector(a, b), s)[0]

# check functions

@check_function(collinear)
def is_collinear(a, b, c) -> bool:
    """a, b, c are collinear"""
    return distance_pl(a, line(b, c)) < EPSILON

@check_function(concyclic)
def is_concyclic(a, b, c, d) -> bool:
    """a, b, c, d are concyclic"""
    return abs(angle(line(a, b), line(a, c)) - angle(line(d, b), line(d, c))) < EPSILON and abs(angle(line(b, a), line(b, c)) - angle(line(d, a), line(d, c))) < EPSILON

@check_function(concurrent)
def is_concurrent(u, v, w) -> bool:
    """u, v, w are concurrent"""
    return abs(u.a * v.c * w.b + u.b * v.a * w.c + u.c * v.b * w.a - u.a * v.b * w.c - u.b * v. c * w.a - u.c * v.a * w.b) < EPSILON

@check_function(line_parallel)
def is_parallel(u, v) -> bool:
    """u and v are parallel"""
    return angle(u, v) < EPSILON

@check_function(line_perpendicular)
def is_perpendicular(u, v) -> bool:
    """u and v are perpendicular"""
    return pi / 2 - angle(u, v) < EPSILON

@check_function(circle_tangent_to_circle)
def is_tangent(s, t) -> bool:
    """s and t are tangent"""
    return abs(distance_pc(s.o, t) - s.r) < EPSILON

@check_function(point_on_line)
def is_pl(a, u) -> bool:
    """a is on u"""
    return distance_pl(a, u) < EPSILON

@check_function(point_on_circle)
def is_pc(a, s) -> bool:
    """a is on s"""
    return distance_pc(a, s) < EPSILON

@check_function(line_tangent_to_circle)
def is_lc(u, s) -> bool:
    """u is tangent to s"""
    return abs(distance_pl(s.o, u) - s.r) < EPSILON
