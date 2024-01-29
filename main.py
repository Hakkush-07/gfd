from sys import argv
from functools import wraps

from geometry.objects import Obj
from geometry.functions import construction_functions

line_counter = 0
objects = {}

object_name = (f"__obj{str(i).zfill(3)}" for i in range(1000))

class GFDException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(f"Error in line {line_counter}: " + self.message)

def interpret_check(check_expression):
    pass

def interpret_function(function_expression):
    pass

def interpret_construction(construction_line):
    if "=" not in construction_line:
        raise GFDException(f"no = in line {line_counter}: {construction_line}")
    equal_sign_index = construction_line.index("=")
    lhs = construction_line[:equal_sign_index]
    rhs = interpret_construction_expression(construction_line[equal_sign_index + 1:])
    if len(lhs) != len(rhs):
        raise GFDException(f"lhs ({len(lhs)}) and rhs ({len(rhs)}) do not have the same number of elements")
    for variable_name, obj in zip(lhs, rhs):
        if variable_name == ".":
            continue
        if variable_name in objects:
            raise GFDException(f"{variable_name} is already defined")
        if not issubclass(type(obj), Obj):
            raise GFDException(f"not Obj return in expression")
        obj.name = variable_name
        objects[variable_name] = obj

def interpret_construction_expression(construction_expression):
    stack = []
    for token in construction_expression:
        update_stack(token, stack)
    return stack

def update_stack(token, stack):
    if "*" in token:
        # this token should be in form <function_name>* or <function_name>*<variable_name>
        add_to_figure = True
        asterisk_index = token.index("*")
        name = token[asterisk_index + 1:] if token[asterisk_index + 1:] else next(object_name)
        token = token[:asterisk_index]
    else:
        add_to_figure = False
    if token in construction_functions:
        construction_function = construction_functions[token]
        args = []
        for arg_type in construction_function.parameters:
            arg = stack.pop()
            if not issubclass(type(arg), arg_type):
                raise GFDException(f"{arg} is not of type {arg_type.__name__} for construction function {construction_function.name}")
            args.append(arg)
        args = args[::-1]
        result = construction_function(*args)
        result_lst = list(result) if type(result) == tuple else [result]
        stack.extend(result_lst)
    # elif token in custom functions
    else:
        if token not in objects:
            raise GFDException(f"{token} is not defined")
        stack.append(objects[token])

def main():
    global line_counter
    if len(argv) < 2:
        raise GFDException("need a .gfd file")
    filename = argv[1]
    with open(filename, "r+") as file:
        # reverse the lines so that we can use it as a stack
        lines = file.read().splitlines()[::-1]
    while len(lines) > 0:
        line = lines.pop()
        line_counter += 1
        if not line:
            # blank line, ignore
            continue
        tokens = line.split()
        if tokens[0] == "#":
            # comment line, ignore
            continue
        elif tokens[0] == "%":
            # import line, extend the execution stack with the new lines
            if len(tokens) < 2:
                continue
            import_file = tokens[1] if tokens[1].endswith(f".gfd") else tokens[1] + ".gfd"
            with open(import_file, "r+") as file:
                lines.extend(file.read().splitlines()[::-1])
        elif tokens[0] == "?":
            # check line, get a boolean result
            interpret_check(tokens[1:])
        elif tokens[0] == ">":
            # function line, define a function
            interpret_function(tokens[1:])
        else:
            # construction line, define objects
            interpret_construction(tokens)
    # write asy file
    with open("templates/template.asy", "r+") as file:
        template = file.read().replace("FIGURE", "\n".join([obj.asy() for obj in objects.values()]))
    with open(f"{filename[:-4]}.asy", "w+") as file:
        file.write(template)

if __name__ == "__main__":
    main()
