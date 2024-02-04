from math import atan, pi

EPSILON = 1e-5

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
        self.name = f"o_{{{str(self.id)}}}"

        self.recipe_parent_depth_set = False
        self.parents = []
        self.recipe = ""
        self.depth = 0

    @property
    def name_wo_special(self):
        return self.name.replace("\\", "").replace("{", "").replace("}", "")
    
    @property
    def description(self):
        return f"is {self.recipe} for {', '.join(map(lambda obj: obj.name, self.parents))}"
    
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
    
    points: list[Point]
        points created so far, if the same point is created again just return the already existing one
    """

    points = []
    def __new__(cls, x, y):
        for point in cls.points:
            if abs(x - point.x) < EPSILON and abs(y - point.y) < EPSILON:
                return point
        return super().__new__(cls)

    def __init__(self, x, y):
        for point in Point.points:
            if abs(x - point.x) < EPSILON and abs(y - point.y) < EPSILON:
                self.recipe_parent_depth_set = True
                return
        super().__init__(0)
        self.x = x
        self.y = y
        Point.points.append(self)
    
    def __repr__(self):
        return f"Point {self.name} [{self.id}](depth {self.depth}) {self.description}"
    
    def set_dir(self, properties, objects):
        """find the emptiest part around the point to put the label"""
        occupied_directions = []
        lines = [pl[1] for pl in properties["point on line"] if self in pl if pl[1] in objects]
        circles = [pc[1] for pc in properties["point on circle"] if self in pc if pc[1] in objects]
        for line in lines:
            u = atan(line.slope)
            points = [pl[0] for pl in properties["point on line"] if line in pl if pl[0] in objects if pl[0] is not self]
            if not points:
                continue
            lm = min(points, key=lambda p: p.x)
            rm = max(points, key=lambda p: p.x)
            if (self.x - lm.x) * (self.x - rm.x) > 0:
                # not line, but ray, so include only one direction
                if u > 0:
                    # positive slope
                    if self.x - lm.x > 0:
                        # self is the rightmost
                        occupied_directions.append(u + pi)
                    else:
                        # self is the leftmost
                        occupied_directions.append(u)
                else:
                    # negative slope
                    if self.x - lm.x > 0:
                        # self is the rightmost
                        occupied_directions.append(u + pi)
                    else:
                        # self is the leftmost
                        occupied_directions.append(u + 2 * pi)
            else:
                # line, so include both directions
                occupied_directions.append(u)
                occupied_directions.append(u + pi)
        for circle in circles:
            dx = self.x - circle.o.x
            dy = self.y - circle.o.y
            u = atan(dy / dx)
            occupied_directions.append(u + pi / 2)
            occupied_directions.append(u - pi / 2)
        for i, o in enumerate(occupied_directions):
            occupied_directions[i] = o % (2 * pi)
        if not occupied_directions:
            self.direction = 90
            return
        occupied_directions.sort()
        occupied_directions.append(occupied_directions[0] + 2 * pi)
        diffs = [j - i for i, j in zip(occupied_directions[:-1], occupied_directions[1:])]
        max_diff = max(diffs)
        max_diff_index = diffs.index(max_diff)
        middle_of_max_diff = (occupied_directions[max_diff_index] + occupied_directions[max_diff_index + 1]) / 2
        middle_of_max_diff %= 2 * pi
        self.direction = middle_of_max_diff * 180 / pi
    
    def asy_definition(self) -> str:
        """asy line for defining this point"""
        return f"pair {self.name_wo_special} = ({self.x}, {self.y});"
    
    def asy_draw(self, plc) -> str:
        """asy line for drawing this point"""
        if plc["p"]:
            return f"dot(\"${self.name}$\", {self.name_wo_special}, dir({self.direction}));"
        else:
            return f"dot({self.name_wo_special});"
        
class Line(Obj):
    """
    lines in the figure

    a, b, c: float
        coefficients of the line equation ax+by=c

    lines: list[Line]
        lines created so far, if the same line is created again just return the already existing one
    """

    lines = []
    def __new__(cls, a, b, c):
        for line in cls.lines:
            ka = line.a / a
            kb = line.b / b
            kc = line.c / c
            if abs(ka - kb) < EPSILON and abs(ka - kc) < EPSILON:
                return line
        return super().__new__(cls)

    def __init__(self, a, b, c):
        for line in Line.lines:
            ka = line.a / a
            kb = line.b / b
            kc = line.c / c
            if abs(ka - kb) < EPSILON and abs(ka - kc) < EPSILON:
                self.recipe_parent_depth_set = True
                return
        super().__init__(1)
        self.a = a
        self.b = b
        self.c = c
        Line.lines.append(self)
    
    def __repr__(self):
        if not self.lmrmf:
            return f"Line {self.name} [{self.id}](depth {self.depth}) {self.description}"
        return f"Line {self.name} = {self.lmf.name}{self.rmf.name} [{self.id}](depth {self.depth}) {self.description}"
    
    def __call__(self, a):
        return self.a * a.x + self.b * a.y - self.c

    @property    
    def slope(self):
        return -self.a / self.b
    
    def set_lm_rm(self, properties, objects):
        """based on the properties, find the leftmost and rightmost points on the line, used for drawing in asy"""
        points = [pl[0] for pl in properties["point on line"] if self in pl]
        self.lmrm = False
        if not points:
            return
        self.lmrm = True
        self.lm = min(points, key=lambda p: p.x)  # leftmost point on the line
        self.rm = max(points, key=lambda p: p.x)  # rightmost point on the line
        self.lm_in_figure = self.lm in objects
        self.rm_in_figure = self.rm in objects
        points_in_figure = [p for p in points if p in objects]
        self.lmrmf = False
        if len(points_in_figure) < 2:
            return
        self.lmrmf = True
        self.lmf = min(points_in_figure, key=lambda p: p.x)
        self.rmf = max(points_in_figure, key=lambda p: p.x)
    
    def asy_definition(self) -> str:
        """asy line for defining this line"""
        if not self.lmrm:
            return ""
        str_lm = f"{self.lm.name_wo_special}" if self.lm_in_figure else f"({self.lm.x}, {self.lm.y})"
        str_rm = f"{self.rm.name_wo_special}" if self.rm_in_figure else f"({self.rm.x}, {self.rm.y})"
        return f"path {self.name_wo_special} = {str_lm} -- {str_rm};"
    
    def asy_draw(self, plc) -> str:
        """asy line for drawing this line"""
        if plc["l"]:
            return f"draw({self.name_wo_special}, L=Label(\"${self.name}$\"));"
        else:
            return f"draw({self.name_wo_special});"

class Circle(Obj):
    """
    circles in the figure

    o: Point
        center of the circle
    r: float
        radius of the circle
    
    circles: list[Circle]
        circles created so far, if the same circle is created again just return the already existing one
    """

    circles = []
    def __new__(cls, o, r):
        for circle in cls.circles:
            if abs(circle.o.x - o.x) < EPSILON and abs(circle.o.y - o.y) < EPSILON and abs(circle.r - r) < EPSILON:
                return circle
        return super().__new__(cls)

    def __init__(self, o, r):
        for circle in Circle.circles:
            if abs(circle.o.x - o.x) < EPSILON and abs(circle.o.y - o.y) < EPSILON and abs(circle.r - r) < EPSILON:
                self.recipe_parent_depth_set = True
                return
        super().__init__(2)
        self.o = o
        self.r = r
        Circle.circles.append(self)

    def __repr__(self):
        return f"Circle {self.name} [{self.id}](depth {self.depth}) {self.description}"
    
    def asy_definition(self) -> str:
        """asy line for defining this circle"""
        return f"path {self.name_wo_special} = circle(({self.o.x}, {self.o.y}), {self.r});"
    
    def asy_draw(self, plc) -> str:
        """asy line for drawing this circle"""
        if plc["c"]:
            return f"draw({self.name_wo_special}, L=Label(\"${self.name}$\"));"
        else:
            return f"draw({self.name_wo_special});"

