from geometry.objects import Point, Line, Circle, Obj
from geometry.checks import is_pl, is_pc, is_parallel, is_perpendicular, is_lc, is_tangent
from geometry.checks import distance_pp, distance_pl, distance_pc
from geometry.checks import EPSILON, parameter_mapping
from geometry.checks import check_functions
from math import sqrt, atan, pi, sin, cos
from functools import wraps
from itertools import product
from random import random
from inspect import signature

construction_functions = {}

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

def all_different(obj_lst):
    return len(set(obj_lst)) == len(obj_lst)

def construction_function(with_checks=True):
    def construction_function_decorator(func):
        @wraps(func)
        def checked_construction_function(*args, **kwargs):
            result = func(*args, **kwargs)
            if not with_checks:
                print("?", func.__name__)
                return result
            combined = list(args) + [result] # assuming for now that result is not tuple
            print("here for", func.__name__)
            for check_function in check_functions:
                print("checking", check_function)
                for check_function_arguments in product(*[[x for x in combined if type(x) == cls] for cls in check_function.parameters]):
                    print("trying with parameters", check_function_arguments)
                    if not all_different(check_function_arguments):
                        print("not all different, continue")
                        continue
                    if check_function(*check_function_arguments):
                        print(check_function, "for", combined)
            if type(result) == tuple:
                pass
            else:
                combined = list(args) + [result]
                if type(result) == Point:
                    for obj in combined:
                        if type(obj) == Point:
                            pass
                        elif type(obj) == Line:
                            if is_pl(result, obj):
                                result.on_lines([obj])
                        elif type(obj) == Circle:
                            if is_pc(result, obj):
                                result.on_circles([obj])
                elif type(result) == Line:
                    for obj in combined:
                        if type(obj) == Point:
                            if is_pl(obj, result):
                                result.contains_points([obj])
                        elif type(obj) == Line:
                            if is_parallel(result, obj):
                                result.parallel_to_line(obj)
                            elif is_perpendicular(result, obj):
                                result.perpendicular_to_line(obj)
                        elif type(obj) == Circle:
                            if is_lc(result, obj):
                                result.tangent_to_circles([obj])
                elif type(result) == Circle:
                    for obj in combined:
                        if type(obj) == Point:
                            if is_pc(obj, result):
                                result.contains_points([obj])
                        elif type(obj) == Line:
                            if is_lc(obj, result):
                                result.tangent_to_lines([obj])
                        elif type(obj) == Circle:
                            if is_tangent(result, obj):
                                result.tangent_to_circle(obj)
            return result
        construction_functions[func.__name__] = ConstructionFunction(checked_construction_function)
        return checked_construction_function
    return construction_function_decorator

@construction_function(with_checks=False)
def intersection(x, y):
    def f(z):
        return z.__class__.__name__.lower()[0]
    return globals()[f"intersection_{f(x)}{f(y)}"](x, y)

@construction_function(with_checks=False)
def intersections(x, y):
    def f(z):
        return z.__class__.__name__.lower()[0]
    return globals()[f"intersections_{f(x)}{f(y)}"](x, y)

@construction_function(with_checks=False)
def reflection(x, y):
    def f(z):
        return z.__class__.__name__.lower()[0]
    return globals()[f"reflection_{f(x)}{f(y)}"](x, y)

@construction_function()
def triangle():
    a = Point(-0.256, 0.966)
    b = Point(-0.905, -0.426)
    c = Point(0.943, -0.333)
    return a, b, c

@construction_function()
def triangle_with_sides():
    a = Point(-0.256, 0.966)
    b = Point(-0.905, -0.426)
    c = Point(0.943, -0.333)
    u = line(b, c)
    v = line(c, a)
    w = line(a, b)
    return a, b, c, u, v, w

@construction_function()
def unit_circle():
    return Circle(Point(0, 0), 1)

# random

@construction_function()
def random_point_on_circle(s):
    t = random() * 2 * pi
    return Point(s.o.x + s.r * cos(t), s.o.y + s.r * sin(t))

@construction_function()
def random_point_on_unit_circle():
    return random_point_on_circle(unit_circle())

@construction_function()
def random_point_on_segment(a, b):
    t = random()
    return Point(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t)

def random_point_on_arc(s, angle1, angle2, radian=True):
    t = angle1 + random() * (angle2 - angle1)
    t = t if radian else t * pi / 180
    return Point(s.o.x + s.r * cos(t), s.o.y + s.r * sin(t))

@construction_function()
def random_point_on_arc2(s, a, b):
    pass

@construction_function()
def random_point():
    return random_point_on_unit_circle()

@construction_function()
def random_line():
    return line(random_point(), random_point())

@construction_function()
def random_circle():
    return Circle(random_point(), random())

@construction_function()
def random_triangle_on_circle(s):
    a = random_point_on_circle(s)
    b = random_point_on_circle(s)
    c = random_point_on_circle(s)
    return a, b, c

@construction_function()
def random_triangle_on_unit_circle():
    return random_triangle_on_circle(unit_circle())

@construction_function()
def random_nice_triangle():
    x = 5
    a = random_point_on_arc(unit_circle(), 120 - x, 120 + x, radian=False)
    b = random_point_on_arc(unit_circle(), 210 - x, 210 + x, radian=False)
    c = random_point_on_arc(unit_circle(), 330 - x, 330 + x, radian=False)
    return a, b, c

# c

@construction_function()
def center(s):
    return s.o

# pp

@construction_function()
def midpoint(a, b):
    return Point((a.x + b.x) / 2, (a.y + b.y) / 2)

@construction_function()
def line(a, b):
    return Line(b.y - a.y, a.x - b.x, a.x * b.y - a.y * b.x)#.contains_points([a, b])

@construction_function()
def perpendicular_bisector(a, b):
    return Line(a.x - b.x, a.y - b.y, (a.x ** 2 + a.y ** 2 - b.x ** 2 - b.y ** 2) / 2)

@construction_function()
def circle_diameter(a, b):
    return Circle(midpoint(a, b), distance_pp(a, b) / 2).contains_points([a, b])

@construction_function()
def reflection_pp(a, b):
    return Point(2 * b.x - a.x, 2 * b.y - a.y)

@construction_function()
def perpendicular_through(a, b):
    return Line(a.x - b.x, a.y - b.y, a.x ** 2 + a.y ** 2 - a.x * b.x - a.y * b.y).contains_points([a])

@construction_function()
def circle_centered(a, b):
    return Circle(a, distance_pp(a, b)).contains_points([b])

# pl

@construction_function()
def reflection_pl(a, u):
    return reflection_pp(a, foot(a, u))

@construction_function()
def foot(a, u):
    return intersection_ll(u, perpendicular_line(a, u)).on_lines([u])

@construction_function()
def perpendicular_line(a, u):
    return Line(u.b, -u.a, a.x * u.b - a.y * u.a).contains_points([a]).perpendicular_to_line(u)

@construction_function()
def parallel_line(a, u):
    return Line(u.a, u.b, a.x * u.a + a.y * u.b).contains_points([a]).parallel_to_line(u)

# pc

@construction_function()
def tangent_points(a, s):
    return intersections_cc(s, circle_diameter(a, s.o))

@construction_function()
def tangent_lines(a, s):
    tp1, tp2 = tangent_points(a, s)
    return line(a, tp1).tangent_to_circles([s]), line(a, tp2).tangent_to_circles([s])

@construction_function()
def tangents(a, s):
    tp1, tp2 = tangent_points(a, s)
    return tp1, tp2, line(a, tp1).tangent_to_circles([s]), line(a, tp2).tangent_to_circles([s])

@construction_function()
def tangent_line(a, s):
    return perpendicular_through(a, s.o).tangent_to_circles([s])

@construction_function()
def polar(a, s):
    d = (s.r / distance_pp(a, s.o)) ** 2
    p = Point(s.o.x + d * (a.x - s.o.x), s.o.y + d * (a.y - s.o.y))
    return perpendicular_through(p, s.o)

# ll

@construction_function()
def intersection_ll(u, v):
    return Point((u.c * v.b - u.b * v.c) / (u.a * v.b - u.b * v.a), (u.c * v.a - u.a * v.c) / (u.b * v.a - u.a * v.b)).on_lines([u, v])

@construction_function()
def angle_bisector_1(u, v):
    return Line(u.a / sqrt(u.a ** 2 + u.b ** 2) - v.a / sqrt(v.a ** 2 + v.b ** 2), u.b / sqrt(u.a ** 2 + u.b ** 2) - v.b / sqrt(v.a ** 2 + v.b ** 2), u.c / sqrt(u.a ** 2 + u.b ** 2) - v.c / sqrt(v.a ** 2 + v.b ** 2))

@construction_function()
def angle_bisector_2(u, v):
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
def intersection_lc_1(u, s):
    a = u.a ** 2 + u.b ** 2
    b = 2 * (s.o.y * u.a * u.b - s.o.x * u.b * u.b - u.a * u.c)
    c = (s.o.x ** 2) * (u.b ** 2) + (u.c ** 2) - 2 * s.o.y * u.b * u.c + (s.o.y ** 2) * (u.b ** 2) - (s.r ** 2) * (u.b ** 2)
    e = b ** 2 - 4 * a * c
    e = 0 if abs(e) < EPSILON else e
    d = sqrt(e)
    x = (-b + d) / (2 * a)
    y = (u.c - u.a * x) / u.b
    return Point(x, y)

@construction_function()
def intersection_lc_2(u, s):
    a = u.a ** 2 + u.b ** 2
    b = 2 * (s.o.y * u.a * u.b - s.o.x * u.b * u.b - u.a * u.c)
    c = (s.o.x ** 2) * (u.b ** 2) + (u.c ** 2) - 2 * s.o.y * u.b * u.c + (s.o.y ** 2) * (u.b ** 2) - (s.r ** 2) * (u.b ** 2)
    e = b ** 2 - 4 * a * c
    e = 0 if abs(e) < EPSILON else e
    d = sqrt(e)
    x = (-b - d) / (2 * a)
    y = (u.c - u.a * x) / u.b
    return Point(x, y)

@construction_function()
def intersections_lc(u, s):
    return intersection_lc_1(u, s).on_lines([u]).on_circles([s]), intersection_lc_2(u, s).on_lines([u]).on_circles([s])

@construction_function()
def pole(u, s):
    d = (s.r / distance_pl(s.o, u)) ** 2
    a = foot(s.o, u)
    return Point(s.o.x + d * (a.x - s.o.x), s.o.y + d * (a.y - s.o.y))

# cc

@construction_function()
def intersections_cc(s, t):
    return intersections_lc(radical_axis(s, t), s)

@construction_function()
def intersection_cc(s, t):
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
    u, v = line(a, b), line(c, a)
    return Line(u.a / sqrt(u.a ** 2 + u.b ** 2) - v.a / sqrt(v.a ** 2 + v.b ** 2), u.b / sqrt(u.a ** 2 + u.b ** 2) - v.b / sqrt(v.a ** 2 + v.b ** 2), u.c / sqrt(u.a ** 2 + u.b ** 2) - v.c / sqrt(v.a ** 2 + v.b ** 2))

@construction_function()
def external_angle_bisector(a, b, c):
    u, v = line(a, b), line(c, a)
    return Line(u.a / sqrt(u.a ** 2 + u.b ** 2) + v.a / sqrt(v.a ** 2 + v.b ** 2), u.b / sqrt(u.a ** 2 + u.b ** 2) + v.b / sqrt(v.a ** 2 + v.b ** 2), u.c / sqrt(u.a ** 2 + u.b ** 2) + v.c / sqrt(v.a ** 2 + v.b ** 2)).contains_points([a])

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
