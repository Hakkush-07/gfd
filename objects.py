class Obj:
    """
    base class for the objects in the figure

    id: int
        id of the object, starts from 0 and increases with every object created
    order: int
        the order that this object appears in the final asy, 0 for points, 1 for lines, 2 for circles
        together with id, they define the object order in the final asy
    name: str
        name/label of the object, starts with __ for objects that are not intended to be in the figure
        later replaced by the user defined name
    """

    count = 0
    def __init__(self, asy_order):
        self.order = asy_order
        self.id = Obj.count
        Obj.count += 1
        self.name = f"o_{{{str(self.id).zfill(3)}}}"

    @property
    def name_wo_special(self):
        return self.name.replace("\\", "").replace("{", "").replace("}", "")
    
    def __hash__(self):
        return hash(self.id)
    
    def criteria(self):
        """criteria for sorting the objects, first type (Point, Line, Circle), then id"""
        return self.order, self.id

class Point(Obj):
    """
    points in the figure

    x, y: float
        x and y coordinates of the point
    """

    def __init__(self, x, y):
        super().__init__(0)
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point {self.name} [{self.id}]"
    
    def asy_definition(self, properties) -> str:
        """asy line for defining this point"""
        return f"pair {self.name_wo_special} = ({self.x}, {self.y});"
    
    def asy_draw(self, plc) -> str:
        """asy line for drawing this point"""
        if plc["p"]:
            return f"dot('${self.name_wo_special}$', {self.name}, dir(90));"
        else:
            return f"dot({self.name});"
        
class Line(Obj):
    """
    lines in the figure

    a, b, c: float
        coefficients of the line equation ax+by=c
    """

    def __init__(self, a, b, c):
        super().__init__(1)
        self.a = a
        self.b = b
        self.c = c
    
    def __repr__(self):
        return f"Line {self.name} [{self.id}]"
    
    def __call__(self, a):
        return self.a * a.x + self.b * a.y - self.c
    
    def asy_definition(self, properties) -> str:
        """asy line for defining this line"""
        points = [pl[0] for pl in properties["point on line"] if self in pl]
        if not points:
            return ""
        lm = min(points, key=lambda p: p.x)  # leftmost point on the line
        rm = max(points, key=lambda p: p.x)  # rightmost point on the line

        return f"path {self.name_wo_special} = ({lm.x}, {lm.y}) -- ({rm.x}, {rm.y});"
    
    def asy_draw(self, plc) -> str:
        """asy line for drawing this line"""
        if plc["l"]:
            return f"draw({self.name_wo_special}, L=Label('${self.name}$'));"
        else:
            return f"draw({self.name_wo_special});"

class Circle(Obj):
    """
    circles in the figure

    o: Point
        center of the circle
    r: float
        radius of the circle
    """
    def __init__(self, o, r):
        super().__init__(2)
        self.o = o
        self.r = r

    def __repr__(self):
        return f"Circle {self.name} [{self.id}]"
    
    def asy_definition(self, properties) -> str:
        """asy line for defining this circle"""
        return f"path {self.name_wo_special} = circle(({self.o.x}, {self.o.y}), {self.r});"
    
    def asy_draw(self, plc) -> str:
        """asy line for drawing this circle"""
        if plc["c"]:
            return f"draw({self.name_wo_special}, L=Label('${self.name}$'));"
        else:
            return f"draw({self.name_wo_special});"

