from inspect import signature
from sys import argv
from geometry.functions import construction_functions

def parameter_count_of_func(function_name):
    return len(signature(construction_functions[function_name]).parameters) # len(signature(globals()[function_name]).parameters)

extension = "gfd"
object_name = (f"__obj{str(i).zfill(3)}" for i in range(1000))

def asy(objects):
    with open("templates/template.asy", "r+") as file:
        return file.read().replace("FIGURE", "\n".join([o.asy() for o in objects]))

def update_stack(stack, token, current_objects, custom_functions):
    if token.endswith("*"):
        add_to_figure = True
        token = token[:-1]
    else:
        add_to_figure = False
    if token in construction_functions: # globals():
        construction_function = construction_functions[token]
        parameters = [stack.pop() for _ in range(len(construction_function))][::-1]
        result = construction_function(*parameters) # globals()[token](*parameters)
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
            assert tokens[3] == "="
            body = tokens[4:]
            custom_functions[function_name] = (parameter_count, body)
            continue
        if tokens[0] == "?":
            result = parse(tokens[1:], objects, custom_functions).pop()
            print(result)
            continue
        equal_sign = tokens.index("=")
        rhs = parse(tokens[equal_sign + 1:], objects, custom_functions)
        lhs = tokens[:equal_sign]
        for variable, obj in zip(lhs, rhs):
            if variable == ".":
                continue
            obj.name = variable
            objects[variable] = obj
    print(*objects.items(), sep="\n")
    print(*custom_functions.items(), sep="\n")
    s = asy(objects.values())
    with open(f"{filename}.asy", "w+") as file:
        file.write(s)

def main():
    # for f in construction_functions.values():
    #     print(f)
    from_file(argv[1])

if __name__ == "__main__":
    main()
