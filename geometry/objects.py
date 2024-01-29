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
    
    def __repr__(self):
        return f"P({self.x}, {self.y})[{self.id}]"
    
    def asy(self):
        return f"dot('${self.name}$', ({self.x}, {self.y}), dir(90));"

class Line(Obj):
    def __init__(self, a, b, c):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
    
    def __repr__(self):
        return f"L({self.a}, {self.b}, {self.c})[{self.id}] [contains {len(self.points)} points]"
    
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
        return f"draw(({self.leftmost.x}, {self.leftmost.y}) -- ({self.rightmost.x}, {self.rightmost.y}));"

class Circle(Obj):
    def __init__(self, o, r):
        super().__init__()
        self.o = o
        self.r = r

    def __repr__(self):
        return f"C({self.o}, {self.r})[{self.id}] [contains {len(self.points)} points]"
    
    def asy(self):
        return f"draw(circle(({self.o.x}, {self.o.y}), {self.r}));"
