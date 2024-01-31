from sys import argv

from functions import construction_functions, properties
from exceptions import GFDException, FigureException
from objects import Obj

class Figure:
    def __init__(self):
        self.objects = {}
        self.custom_functions = {}

        self.line_counters = []

    def interpret(self, filename):
        self.interpret_file(filename)
        with open(f"{filename[:-4]}.asy", "w+") as file:
            file.write(self.asy())
        with open(f"{filename[:-4]}.txt", "w+") as file:
            file.write(self.txt())

    def interpret_file(self, filename):
        if filename in map(lambda x: x[0], self.line_counters):
            raise GFDException("circular import is not allowed") # TODO: fix
        self.line_counters.append([filename, 0])

        with open(filename, "r+") as file:
            for line in file.read().splitlines():
                self.line_counters[-1][1] += 1
                self.interpret_line(line)

        self.line_counters.pop()
    
    def interpret_line(self, line):
        tokens = line.split()
        if not tokens or tokens[0] == "#":
            return
        elif tokens[0] == "%":
            if len(tokens) < 2:
                return
            imported_file = tokens[1] if tokens[1].endswith(".gfd") else tokens[1] + ".gfd"
            self.interpret_file(imported_file)
        elif tokens[0] == "?":
            self.interpret_check(tokens[1:])
        elif tokens[0] == ">":
            self.interpret_function(tokens[1:])
        else:
            self.interpret_construction(tokens)
    
    def interpret_check(self, tokens):
        pass

    def interpret_function(self, tokens):
        pass

    def interpret_construction(self, tokens):
        if "=" not in tokens:
            raise GFDException("no = in construction line")
        equal_sign_index = tokens.index("=")
        lhs = tokens[:equal_sign_index]
        rhs = self.interpret_expression(tokens[equal_sign_index + 1:])
        if len(lhs) != len(rhs):
            raise GFDException(f"lhs ({len(lhs)}) and rhs ({len(rhs)}) do not have the same number of elements in construction line")
        for variable_name, obj in zip(lhs, rhs):
            if variable_name == ".":
                continue
            if variable_name in self.objects:
                raise GFDException(f"{variable_name} is already defined")
            if not issubclass(type(obj), Obj):
                raise GFDException(f"not Obj ({type(obj)}) return in expression")
            obj.name = variable_name
            self.objects[variable_name] = obj
    
    def interpret_expression(self, expression):
        stack = []
        for token in expression:
            self.update_stack(stack, token)
        return stack
    
    def update_stack(self, stack, token):
        # TODO: check * in token
        if token in construction_functions:
            construction_function = construction_functions[token]
            args = []
            for arg_type in construction_function.parameters[::-1]:
                arg = stack.pop()
                if not issubclass(type(arg), arg_type):
                    raise GFDException(f"{arg} is not of type {arg_type.__name__} for construction function {construction_function.name}")
                args.append(arg)
            args = args[::-1]
            try:
                result = construction_function(*args)
            except FigureException as e:
                raise GFDException(e.message, *self.line_counters[-1])
            result_lst = list(result) if type(result) == tuple else [result]
            stack.extend(result_lst)
        elif token in self.custom_functions:
            pass
        elif token in self.objects:
            stack.append(self.objects[token])
        else:
            raise GFDException(f"{token} is not defined")

    def asy(self):
        sorted_objects = sorted(self.objects.values(), key=lambda obj: obj.criteria())
        definitions = "\n".join([obj.asy_definition(properties) for obj in sorted_objects])
        draws = "\n".join([obj.asy_draw() for obj in sorted_objects])
        with open("templates/template.asy", "r+") as file:
            template = file.read().replace("FIGURE", definitions + "\n\n" + draws)
        return template
    
    def txt(self):
        s = ""
        for name, prop in properties.items():
            t = f"{name}\n"
            for objs in prop:
                t += f"    {', '.join(map(str, objs))}\n"
            t += "\n"
            s += t
        return s

if __name__ == "__main__":
    if len(argv) < 2:
        raise GFDException("need a .gfd file")
    filename = argv[1]
    figure = Figure()
    figure.interpret(filename)
