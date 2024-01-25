from math import sqrt, pi, atan
from inspect import signature
from sys import argv
from itertools import combinations, permutations

def dot(l1, l2):
    return sum([a * b for a, b in zip(l1, l2)])

def roundx(n):
    return round(n, 2)

def parameter_count_of_func(function_name):
    return len(signature(globals()[function_name]).parameters)

class Obj:
    count = 0
    def __init__(self):
        self.id = Obj.count
        Obj.count += 1
        self.name = "_"
    
    def __hash__(self):
        return hash(self.id)

parallel_lines = []
perpendicular_lines = []
tangent_circles = []

class Point(Obj):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"P({self.x}, {self.y})[{self.id}]"
    
    def contained_in_lines(self, lines):
        for u in lines:
            s = Line.contains.get(u, set())
            s.add(self)
            Line.contains[u] = s
        return self
    
    def asy(self):
        return f"dot('${self.name}$', ({roundx(self.x)}, {roundx(self.y)}), dir(90));"

class Line(Obj):
    contains = {}
    def __init__(self, a, b, c):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        Line.contains[self] = set()
    
    def __repr__(self):
        return f"L({self.a}, {self.b}, {self.c})[{self.id}] [contains {len(Line.contains.get(self, 0))} points]"
    
    def __call__(self, a):
        return dot([self.a, self.b, self.c], [a.x, a.y, -1])
    
    def contains_points(self, points):
        s = Line.contains.get(self, set())
        for a in points:
            s.add(a)
        Line.contains[self] = s
        return self
    
    def perpendicular_to_line(self, u):
        perpendicular_lines.append((self, u))
        return self
    
    def parallel_to_line(self, u):
        parallel_lines.append((self, u))
        return self
    
    def asy(self):
        a = min(Line.contains[self], key=lambda p: p.x)
        b = max(Line.contains[self], key=lambda p: p.x)
        return f"draw(({roundx(a.x)}, {roundx(a.y)}) -- ({roundx(b.x)}, {roundx(b.y)}));"

class Circle(Obj):
    contains = {}
    def __init__(self, o, r):
        super().__init__()
        self.o = o
        self.r = r
        Circle.contains[self] = set()

    def __repr__(self):
        return f"C({self.o}, {self.r})[{self.id}] [contains {len(Circle.contains.get(self, 0))} points]"
    
    def contains_points(self, points):
        s = Circle.contains.get(self, set())
        for a in points:
            s.add(a)
        Circle.contains[self] = s
        return self
    
    def asy(self):
        return f"draw(circle(({roundx(self.o.x)}, {roundx(self.o.y)}), {roundx(self.r)}));"

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

def triangle():
    a = Point(-0.256, 0.966)
    b = Point(-0.905, -0.426)
    c = Point(0.943, -0.333)
    u = line(b, c)
    v = line(c, a)
    w = line(a, b)
    return a, b, c, u, v, w

def intersection(x, y):
    def f(z):
        return z.__class__.__name__.lower()[0]
    return globals()[f"intersection_{f(x)}{f(y)}"](x, y)

# pp

def midpoint(a, b):
    return Point((a.x + b.x) / 2, (a.y + b.y) / 2)

def line(a, b):
    return Line(b.y - a.y, a.x - b.x, a.x * b.y - a.y * b.x).contains_points([a, b])

def perpendicular_bisector(a, b):
    return Line(a.x - b.x, a.y - b.y, (a.x ** 2 + a.y ** 2 - b.x ** 2 - b.y ** 2) / 2)

def circle_diameter(a, b):
    return Circle(midpoint(a, b), distance_pp(a, b) / 2).contains_points([a, b])

def reflection_pp(a, b):
    return Point(2 * b.x - a.x, 2 * b.y - a.y)

def perpendicular_through(a, b):
    return Line(a.x - b.x, a.y - b.y, a.x ** 2 + a.y ** 2 - a.x * b.x - a.y * b.y).contains_points([a])

def circle_centered(a, b):
    return Circle(a, distance_pp(a, b)).contains_points([b])

# pl

def reflection_pl(a, u):
    return reflection_pp(a, foot(a, u))

def foot(a, u):
    return intersection_ll(u, perpendicular_line(a, u)).contained_in_lines([u])

def perpendicular_line(a, u):
    return Line(u.b, -u.a, a.x * u.b - a.y * u.a).contains_points([a]).perpendicular_to_line(u)

def parallel_line(a, u):
    return Line(u.a, u.b, a.x * u.a + a.y * u.b).contains_points([a]).parallel_to_line(u)

# pc

def tangent_points(a, s):
    return intersections_cc(s, circle_diameter(a, s.o))

def tangent_lines(a, s):
    tp1, tp2 = tangent_points(a, s)
    tl1 = line(a, tp1) if tp1 else None
    tl2 = line(a, tp2) if tp2 else None
    return tl1, tl2

def polar(a, s):
    d = (s.r / distance_pp(a, s.o)) ** 2
    p = Point(s.o.x + d * (a.x - s.o.x), s.o.y + d * (a.y - s.o.y))
    return perpendicular_through(p, s.o)

def circle_pc(a, s):
    return circle_diameter(a, s.o)

# ll

def intersection_ll(u, v):
    return Point((u.c * v.b - u.b * v.c) / (u.a * v.b - u.b * v.a), (u.c * v.a - u.a * v.c) / (u.b * v.a - u.a * v.b)).contained_in_lines([u, v])

def angle_bisector_1(u, v):
    return Line(u.a / sqrt(u.a ** 2 + u.b ** 2) - v.a / sqrt(v.a ** 2 + v.b ** 2), u.b / sqrt(u.a ** 2 + u.b ** 2) - v.b / sqrt(v.a ** 2 + v.b ** 2), u.c / sqrt(u.a ** 2 + u.b ** 2) - v.c / sqrt(v.a ** 2 + v.b ** 2))

def angle_bisector_2(u, v):
    return Line(u.a / sqrt(u.a ** 2 + u.b ** 2) + v.a / sqrt(v.a ** 2 + v.b ** 2), u.b / sqrt(u.a ** 2 + u.b ** 2) + v.b / sqrt(v.a ** 2 + v.b ** 2), u.c / sqrt(u.a ** 2 + u.b ** 2) + v.c / sqrt(v.a ** 2 + v.b ** 2))

def reflection_ll(u, v):
    i = intersection_ll(u, v)
    x, y = i.x, i.y
    m = u.a * v.b * v.b - u.a * v.a * v.a - 2 * u.b * v.a * v.b
    n = u.b * v.b * v.b - u.b * v.a * v.a - 2 * u.a * v.a * v.b
    return Line(m, -n, x * m - y * n)

# lc

def intersection_lc_1(u, s):
    a = u.a ** 2 + u.b ** 2
    b = 2 * (s.o.y * u.a * u.b - s.o.x * u.b * u.b - u.a * u.c)
    c = (s.o.x ** 2) * (u.b ** 2) + (u.c ** 2) - 2 * s.o.y * u.b * u.c + (s.o.y ** 2) * (u.b ** 2) - (s.r ** 2) * (u.b ** 2)
    d = (b ** 2 - 4 * a * c).sqrt()
    x = (-b + d) / (2 * a)
    y = (u.c - u.a * x) / u.b
    return Point(x, y)

def intersection_lc_2(u, s):
    a = u.a ** 2 + u.b ** 2
    b = 2 * (s.o.y * u.a * u.b - s.o.x * u.b * u.b - u.a * u.c)
    c = (s.o.x ** 2) * (u.b ** 2) + (u.c ** 2) - 2 * s.o.y * u.b * u.c + (s.o.y ** 2) * (u.b ** 2) - (s.r ** 2) * (u.b ** 2)
    d = (b ** 2 - 4 * a * c).sqrt()
    x = (-b - d) / (2 * a)
    y = (u.c - u.a * x) / u.b
    return Point(x, y)

def intersections_lc(u, s):
    return intersection_lc_1(u, s), intersection_lc_2(u, s)

def pole(u, s):
    d = (s.r / distance_pl(s.o, u)) ** 2
    a = foot(s.o, u)
    return Point(s.o.x + d * (a.x - s.o.x), s.o.y + d * (a.y - s.o.y))

# cc

def intersections_cc(s, t):
    return intersections_lc(radical_axis(s, t), s)

def intersection_cc(s, t):
    return intersection_ll(line(s.o, t.o), radical_axis(s, t))

def radical_axis(s, t):
    return Line(2 * (s.o.x - t.o.x), 2 * (s.o.y - t.o.y), t.r ** 2 - s.r ** 2 + s.o.x ** 2 - t.o.x ** 2 + s.o.y ** 2 - t.o.y ** 2)

def tangent_points_external(s, t):
    p1, p2 = tangent_points(tangent_intersection_external(s, t), s)
    p3, p4 = tangent_points(tangent_intersection_external(s, t), t)
    return p1, p2, p3, p4

def tangent_points_internal(s, t):
    p1, p2 = tangent_points(tangent_intersection_internal(s, t), s)
    p3, p4 = tangent_points(tangent_intersection_internal(s, t), t)
    return p1, p2, p3, p4

def tangent_intersection_external(s, t):
    return Point((s.o.x * t.r - t.o.x * s.r) / (t.r - s.r), (s.o.y * t.r - t.o.y * s.r) / (t.r - s.r))

def tangent_intersection_internal(s, t):
    return Point((s.o.x * t.r + t.o.x * s.r) / (t.r + s.r), (s.o.y * t.r + t.o.y * s.r) / (t.r + s.r))

def tangent_lines_external(s, t):
    return tangent_lines(tangent_intersection_external(s, t), s)

def tangent_lines_internal(s, t):
    return tangent_lines(tangent_intersection_internal(s, t), s)

# ppp

def internal_angle_bisector(a, b, c):
    u, v = line(a, b), line(c, a)
    return Line(u.a / sqrt(u.a ** 2 + u.b ** 2) - v.a / sqrt(v.a ** 2 + v.b ** 2), u.b / sqrt(u.a ** 2 + u.b ** 2) - v.b / sqrt(v.a ** 2 + v.b ** 2), u.c / sqrt(u.a ** 2 + u.b ** 2) - v.c / sqrt(v.a ** 2 + v.b ** 2))

def external_angle_bisector(a, b, c):
    u, v = line(a, b), line(c, a)
    return Line(u.a / sqrt(u.a ** 2 + u.b ** 2) + v.a / sqrt(v.a ** 2 + v.b ** 2), u.b / sqrt(u.a ** 2 + u.b ** 2) + v.b / sqrt(v.a ** 2 + v.b ** 2), u.c / sqrt(u.a ** 2 + u.b ** 2) + v.c / sqrt(v.a ** 2 + v.b ** 2)).contains_points([a])

def altitude(a, b, c):
    return perpendicular_line(a, line(b, c))

def median(a, b, c):
    return line(a, midpoint(b, c))

def foot_ppp(a, b, c):
    return foot(a, line(b, c))

def circumcenter(a, b, c):
    return intersection_ll(perpendicular_bisector(a, b), perpendicular_bisector(a, c))

def circumradius(a, b, c):
    return distance_pp(a, circumcenter(a, b, c))

def circumcircle(a, b, c):
    return Circle(circumcenter(a, b, c), circumradius(a, b, c))

def incenter(a, b, c):
    return intersection_ll(internal_angle_bisector(b, c, a), internal_angle_bisector(c, a, b))

def inradius(a, b, c):
    return distance_pl(incenter(a, b, c), line(b, c))

def incircle(a, b, c):
    return Circle(incenter(a, b, c), inradius(a, b, c))

def excenter(a, b, c):
    return intersection_ll(external_angle_bisector(b, c, a), external_angle_bisector(c, a, b))

def exradius(a, b, c):
    return distance_pl(excenter(a, b, c), line(b, c))

def excircle(a, b, c):
    return Circle(excenter(a, b, c), exradius(a, b, c))

def orthocenter(a, b, c):
    return intersection_ll(altitude(b, c, a), altitude(c, a, b))

def centroid(a, b, c):
    return Point((a.x + b.x + c.x) / 3, (a.y + b.y + c.y) / 3)

# checks

EPSILON = 1e-5

def is_collinear(a, b, c):
    return distance_pl(a, line(b, c)) < EPSILON

def is_concyclic(a, b, c, d):
    return abs(angle(line(a, b), line(a, c)) - angle(line(d, b), line(d, c))) < EPSILON and abs(angle(line(b, a), line(b, c)) - angle(line(d, a), line(d, c))) < EPSILON

def is_concurrent(u, v, w):
    return abs(u.a * v.c * w.b + u.b * v.a * w.c + u.c * v.b * w.a - u.a * v.b * w.c - u.b * v. c * w.a - u.c * v.a * w.b) < EPSILON

def is_parallel(u, v):
    return angle(u, v) < EPSILON

def is_perpendicular(u, v):
    return pi / 2 - angle(u, v) < EPSILON

def is_tangent(s, t):
    d = distance_pp(s.o, t.o)
    return abs(d - (s.r + t.r)) < EPSILON or abs(d - abs(s.r - t.r)) < EPSILON

def is_pl(a, u):
    return distance_pl(a, u) < EPSILON

def is_pc(a, s):
    return pcr(a, s) == 0

def is_lc(u, s):
    return lcr(u, s) == 0

def is_equal_length(a, b, c, d):
    return abs(distance_pp(a, b) - distance_pp(c, d)) < EPSILON

def is_equal_length(a, b, c, d):
    return abs(distance_pp(a, b) - distance_pp(c, d)) < EPSILON

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

extension = "gfd"
object_name = (f"__obj{str(i).zfill(3)}" for i in range(1000))

def asy(objects, checks):
    with open("templates/template.asy", "r+") as file:
        return file.read().replace("FIGURE", "\n".join([o.asy() for o in objects]) + "\n" + "\n".join([f"// {check_function}({', '.join(parameters)}) = {result}" for parameters, check_function, result in checks]))

def update_stack(stack, token, current_objects, custom_functions):
    if token.endswith("*"):
        add_to_figure = True
        token = token[:-1]
    else:
        add_to_figure = False
    if token in globals():
        parameters = [stack.pop() for _ in range(parameter_count_of_func(token))][::-1]
        result = globals()[token](*parameters)
        if type(result) == tuple:
            for obj in result:
                stack.append(obj)
                if add_to_figure:
                    current_objects[next(object_name)] = obj
        else:
            stack.append(result)
            if add_to_figure:
                current_objects[next(object_name)] = result
    elif token in custom_functions.keys():
        parameter_count, body = custom_functions[token]
        parameters = [stack.pop().name for _ in range(parameter_count)][::-1]
        for subtoken in body:
            if subtoken.startswith("$"):
                subtoken = parameters[int(subtoken[1:]) - 1]
            update_stack(stack, subtoken, current_objects, custom_functions)
    else:
        stack.append(current_objects[token])

def parse(expression, current_objects, custom_functions):
    stack = []
    for token in expression:
        update_stack(stack, token, current_objects, custom_functions)
    return stack

def from_file(filename):
    with open(f"{filename}.{extension}", "r+") as file:
        content = file.read().splitlines()[::-1]
    objects = {}
    custom_functions = {}
    checks = []
    while len(content) > 0:
        line = content.pop()
        if not line:
            continue
        tokens = line.split()
        if tokens[0] == "#":
            continue
        if tokens[0] == "%":
            with open(f"{tokens[1]}.{extension}", "r+") as file:
                content.extend(file.read().splitlines()[::-1])
            continue
        if tokens[0] == ">":
            parameter_count = int(tokens[1])
            function_name = tokens[2]
            assert(tokens[3] == "=")
            body = tokens[4:]
            custom_functions[function_name] = (parameter_count, body)
            continue
        if tokens[0] == "?":
            parameters = tokens[1:-1]
            check_function = tokens[-1]
            result = globals()[f"is_{check_function}"](*[objects[p] for p in parameters])
            print(result)
            checks.append((parameters, check_function, result))
            continue
        equal_sign = tokens.index("=")
        rhs = parse(tokens[equal_sign + 1:], objects, custom_functions)
        lhs = tokens[:equal_sign]
        for variable, obj in zip(lhs, rhs):
            obj.name = variable
            objects[variable] = obj
    print(*objects.items(), sep="\n")
    print(*custom_functions.items(), sep="\n")
    s = asy(objects.values(), checks)
    with open(f"{filename}.asy", "w+") as file:
        file.write(s)

def main():
    from_file(argv[1])

if __name__ == "__main__":
    main()
