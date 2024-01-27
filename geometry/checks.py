from geometry.objects import Point, Line, Circle, Obj
from math import pi, sqrt, atan
from itertools import combinations, permutations
from inspect import signature
from functools import wraps

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

check_functions = []

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
    # check_functions[func.__name__] = CheckFunction(inner)
    check_functions.append(CheckFunction(inner))
    return inner

def distance(x, y):
    def f(z):
        return z.__class__.__name__.lower()[0]
    return globals()[f"distance_{f(x)}{f(y)}"](x, y)

def distance_pp(a, b):
    return sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

def distance_pl(a, u):
    return abs(u(a)) / sqrt(u.a ** 2 + u.b ** 2)

def distance_pc(a, s):
    return abs(s.r - distance_pp(a, s.o))

def angle(u, v):
    x = u.a * v.a + u.b * v.b
    return abs(atan((v.a * u.b - u.a * v.b) / x)) if x else pi / 2

# from functions

def line(a, b):
    return Line(b.y - a.y, a.x - b.x, a.x * b.y - a.y * b.x)

def radical_axis(s, t):
    return Line(2 * (s.o.x - t.o.x), 2 * (s.o.y - t.o.y), t.r ** 2 - s.r ** 2 + s.o.x ** 2 - t.o.x ** 2 + s.o.y ** 2 - t.o.y ** 2)

# checks

EPSILON = 1e-5

@check_function
def is_collinear(a, b, c):
    return distance_pl(a, line(b, c)) < EPSILON

@check_function
def is_concyclic(a, b, c, d):
    return abs(angle(line(a, b), line(a, c)) - angle(line(d, b), line(d, c))) < EPSILON and abs(angle(line(b, a), line(b, c)) - angle(line(d, a), line(d, c))) < EPSILON

@check_function
def is_concurrent(u, v, w):
    return abs(u.a * v.c * w.b + u.b * v.a * w.c + u.c * v.b * w.a - u.a * v.b * w.c - u.b * v. c * w.a - u.c * v.a * w.b) < EPSILON

@check_function
def is_parallel(u, v):
    return angle(u, v) < EPSILON

@check_function
def is_perpendicular(u, v):
    return pi / 2 - angle(u, v) < EPSILON

@check_function
def is_tangent(s, t):
    d = distance_pp(s.o, t.o)
    return abs(d - (s.r + t.r)) < EPSILON or abs(d - abs(s.r - t.r)) < EPSILON

@check_function
def is_pl(a, u):
    return distance_pl(a, u) < EPSILON

@check_function
def is_pc(a, s):
    return pcr(a, s) == 0

@check_function
def is_lc(u, s):
    return lcr(u, s) == 0

@check_function
def is_equal_length(a, b, c, d):
    return abs(distance_pp(a, b) - distance_pp(c, d)) < EPSILON

# preconditions

def different_points(*points):
    for a, b in combinations(points, 2):
        if abs(a.x - b.x) < EPSILON and abs(a.y - b.y) < EPSILON:
            return False
    return True

def different_lines(*lines):
    for u, v in combinations(lines, 2):
        if abs(u.a * v.c - u.c * v.a) < EPSILON and abs(u.b * v.c - u.c * v.b) < EPSILON:
            return False
    return True

def different_circles(*circles):
    for s, t in combinations(circles, 2):
        if not different_points(s.o, t.o) and abs(s.r - t.r) < EPSILON:
            return False
    return True

def not_three_collinear(*points):
    return not any([is_collinear(a, b, c) for a, b, c in combinations(points, 3)])

def not_two_parallel(*lines):
    return not any([is_parallel(u, v) for u, v in combinations(lines, 2)])

def not_isosceles_trapezoid_or_parallelogram(a, b, c, d):
    for aa, bb, cc, dd in permutations((a, b, c, d), 4):
        if is_parallel(line(aa, bb), line(cc, dd)) and abs(distance_pp(aa, cc) - distance_pp(bb, dd)) < EPSILON:
            return False
    return True

def not_deltoid(a, b, c, d):
    for aa, bb, cc, dd in permutations((a, b, c, d), 4):
        if is_perpendicular(line(aa, cc), line(bb, dd)) and (abs(distance_pp(aa, bb) - distance_pp(aa, dd)) < EPSILON or abs(distance_pp(bb, aa) - distance_pp(bb, cc))):
            return False
    return True

def pcr(a, s):
    x = distance_pp(s.o, a) - s.r
    if abs(x) < EPSILON:
        return 0
    return -1 if x < 0 else 1

def lcr(u, s):
    x = distance_pl(s.o, u) - s.r
    if abs(x) < EPSILON:
        return 0
    return -1 if x < 0 else 1

def ccr(s, t):
    # -2: out inside, -1: on inside, 0: on outside, 1: out outside, 2: in
    reg = lcr(radical_axis(s, t), s)
    ins = distance_pp(s.o, t.o) - abs(s.r - t.r) < EPSILON
    if ins:
        if reg == 1:
            return -2
        elif reg == 0:
            return -1
    else:
        if reg == 1:
            return 1
        elif reg == 0:
            return 0
        elif reg == -1:
            return 2

def not_pl(a, u):
    return not is_pl(a, u)

def out_pc(a, s):
    return pcr(a, s) == 1

def intersecting_lc(u, s):
    return lcr(u, s) == -1

def not_through_center(u, s):
    return not_pl(s.o, u)

def different_radius(*circles):
    for s, t in combinations(circles, 2):
        if abs(s.r - t.r) < EPSILON:
            return False
    return True

def different_center(*circles):
    for s, t in combinations(circles, 2):
        if not different_points(s.o, t.o):
            return False
    return True

def nice_circles(s, t):
    return different_center(s, t) and different_radius(s, t)

def cc_1(s, t):
    return ccr(s, t) == 2

def cc_2(s, t):
    return ccr(s, t) == 1

def cc_3(s, t):
    return ccr(s, t) == 0

def cc_4(s, t):
    return ccr(s, t) == -1

def not_centers_collinear(s, t, m):
    return not is_collinear(s.o, t.o, m.o)
