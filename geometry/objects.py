def dot(l1, l2):
    return sum([a * b for a, b in zip(l1, l2)])

def roundx(n):
    # return round(n, 2)
    return n

class Obj:
    count = 0
    def __init__(self):
        self.id = Obj.count
        Obj.count += 1
        self.name = "_"
    
    def __hash__(self):
        return hash(self.id)


class Point(Obj):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

        self.lines = set()
        self.circles = set()
    
    def __repr__(self):
        return f"P({self.x}, {self.y})[{self.id}]"
    
    def on_lines(self, lines):
        for u in lines:
            self.lines.add(u)
            u.points.add(self)
        return self
    
    def on_circles(self, circles):
        for s in circles:
            self.circles.add(s)
            s.points.add(self)
        return self
    
    def asy(self):
        return f"dot('${self.name}$', ({roundx(self.x)}, {roundx(self.y)}), dir(90));"

class Line(Obj):
    def __init__(self, a, b, c):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c

        self.points = set()
        self.lines_perpendicular = set()
        self.lines_parallel = set()
        self.circles = set()
    
    def __repr__(self):
        return f"L({self.a}, {self.b}, {self.c})[{self.id}] [contains {len(self.points)} points]"
    
    def __call__(self, a):
        return dot([self.a, self.b, self.c], [a.x, a.y, -1])
    
    @property
    def leftmost(self):
        return min(self.points, key=lambda p: p.x) if self.points else None
    
    @property
    def rightmost(self):
        return max(self.points, key=lambda p: p.x) if self.points else None
    
    def contains_points(self, points):
        for a in points:
            self.points.add(a)
            a.lines.add(self)
        return self
    
    def perpendicular_to_line(self, u):
        self.lines_perpendicular.add(u)
        u.lines_perpendicular.add(self)
        return self
    
    def parallel_to_line(self, u):
        self.lines_parallel.add(u)
        u.lines_parallel.add(self)
        return self
    
    def tangent_to_circles(self, circles):
        for s in circles:
            self.circles.add(s)
            s.lines.add(self)
        return self
    
    def asy(self):
        if not self.points:
            return ""
        return f"draw(({roundx(self.leftmost.x)}, {roundx(self.leftmost.y)}) -- ({roundx(self.rightmost.x)}, {roundx(self.rightmost.y)}));"

class Circle(Obj):
    def __init__(self, o, r):
        super().__init__()
        self.o = o
        self.r = r
        
        self.points = set()
        self.lines = set()
        self.circles = set()

    def __repr__(self):
        return f"C({self.o}, {self.r})[{self.id}] [contains {len(self.points)} points]"
    
    def contains_points(self, points):
        for a in points:
            self.points.add(a)
            a.circles.add(self)
        return self
    
    def tangent_to_lines(self, lines):
        for u in lines:
            self.lines.add(u)
            u.circles.add(self)
        return self

    def tangent_to_circle(self, s):
        self.circles.add(s)
        s.circles.add(self)
    
    def asy(self):
        return f"draw(circle(({roundx(self.o.x)}, {roundx(self.o.y)}), {roundx(self.r)}));"
