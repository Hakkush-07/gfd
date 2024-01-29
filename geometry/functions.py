from functools import wraps
from inspect import signature

from geometry.objects import Point, Line, Circle, Obj

construction_functions = {}

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

def construction_function(with_checks=True):
    def construction_function_decorator(func):
        @wraps(func)
        def checked_construction_function(*args, **kwargs):
            result = func(*args, **kwargs)
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
def midpoint(a, b):
    return Point((a.x + b.x) / 2, (a.y + b.y) / 2)
