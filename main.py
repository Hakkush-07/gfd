from sys import argv
from itertools import combinations

from functions import construction_functions, check_functions, properties, check_everything
from exceptions import GFDException, FigureException
from objects import Obj

class Figure:
    """
    represents the figure

    objects: dict[str, Obj]
        mapping from object names in the figure to their actual Obj
    custom functions: dict[str, (int, list[str])]
        custom functions defined by the user, mapping from function name to parameter count and function body tokens
    line_counters: list[(str, int)]
        stores the stack for the imported files
        last element is the current file being interpreted and line number
    """
    def __init__(self):
        self.objects = {}
        self.custom_functions = {}

        self.line_counters = []

    def interpret(self, filename):
        """starting point"""
        self.interpret_file(filename)

        with open(f"{filename[:-4]}.asy", "w+") as file:
            file.write(self.asy())

        with open(f"{filename[:-4]}.txt", "w+") as file:
            file.write(self.txt())

    def interpret_file(self, filename):
        """interprets a gfd file"""
        if filename in map(lambda x: x[0], self.line_counters):
            raise GFDException("circular import is not allowed", *self.line_counters[-1])
        self.line_counters.append([filename, 0])

        with open(filename, "r+") as file:
            for line in file.read().splitlines():
                self.line_counters[-1][1] += 1
                self.interpret_line(line)

        self.line_counters.pop()
    
    def interpret_line(self, line):
        """interprets a gfd line"""
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
        """
        interprets a check statement in a gfd line
        ? <check expression>
        """
        stack = []
        for token in tokens:
            self.update_stack(stack, token)
        result = stack.pop()
        if type(result) != bool:
            raise GFDException("non bool result for check line", *self.line_counters[-1])
        print(result)

    def interpret_function(self, tokens):
        """
        interprets a function definition in a gfd line
        > <parameter_count> <function_name> = <function_body>
        in <function_body>, use $i to refer to the ith input
        """
        if len(tokens) < 3 or tokens[2] != "=":
            raise GFDException("function line does not have enough tokens or no = in correct place", *self.line_counters[-1])
        try:
            parameter_count = int(tokens[0])
        except:
            raise GFDException("first token in function line should be the parameter count", *self.line_counters[-1])
        function_name = tokens[1]
        function_body = tokens[3:]
        self.custom_functions[function_name] = (parameter_count, function_body)

    def interpret_construction(self, tokens):
        """
        interprets a construction line in a gfd
        construction line consists of object names and function names
        function names may include * to indicate that its output should be included in the final figure
        it is used by inline calls
        """
        if "=" not in tokens:
            raise GFDException("no = in construction line", *self.line_counters[-1])
        equal_sign_index = tokens.index("=")
        lhs = tokens[:equal_sign_index]
        rhs = self.interpret_expression(tokens[equal_sign_index + 1:])
        if len(lhs) != len(rhs):
            raise GFDException(f"lhs ({len(lhs)}) and rhs ({len(rhs)}) do not have the same number of elements in construction line", *self.line_counters[-1])
        for variable_name, obj in zip(lhs, rhs):
            if variable_name == ".":
                continue
            if variable_name in self.objects:
                raise GFDException(f"{variable_name} is already defined", *self.line_counters[-1])
            if not issubclass(type(obj), Obj):
                raise GFDException(f"not Obj ({type(obj)}) return in expression", *self.line_counters[-1])
            obj.name = variable_name
            self.objects[variable_name] = obj
    
    def interpret_expression(self, expression):
        """interpret an expression consisting of object names and function names in postfix"""
        stack = []
        for token in expression:
            self.update_stack(stack, token)
        return stack
    
    def update_stack(self, stack, token):
        """updates stack based on the token in an expression"""
        add_to_figure = False
        if "*" in token:
            # output is included in the figure
            add_to_figure = True
            token = token[:token.index("*")]

        if token in construction_functions:
            construction_function = construction_functions[token]

            args = []
            for arg_type in construction_function.parameters[::-1]:
                arg = stack.pop()
                if not issubclass(type(arg), arg_type):
                    raise GFDException(f"Input {arg} is not of type {arg_type.__name__} for construction function {construction_function.name}", *self.line_counters[-1])
                args.append(arg)
            args = args[::-1]

            try:
                result = construction_function(*args)
            except FigureException as e:
                raise GFDException(e.message, *self.line_counters[-1])
            
            result_lst = []
            if type(result) == tuple:
                for r in result:
                    if not issubclass(type(r), Obj):
                        raise GFDException(f"non Obj return for construction function {construction_function.name}", *self.line_counters[-1])
                    result_lst.append(r)
            else:
                if not issubclass(type(result), Obj):
                    raise GFDException(f"non Obj return for construction function {construction_function.name}", *self.line_counters[-1])
                result_lst.append(result)

            if add_to_figure:
                for obj in result_lst:
                    self.objects[obj.name] = obj

            stack.extend(result_lst)

        elif token in check_functions.keys():
            check_function = check_functions[token]

            args = []
            for arg_type in check_function.parameters[::-1]:
                arg = stack.pop()
                if not issubclass(type(arg), arg_type):
                    raise GFDException(f"Input {arg} is not of type {arg_type.__name__} for check function {check_function.name}", *self.line_counters[-1])
                args.append(arg)
            args = args[::-1]

            try:
                result = check_function(*args)
            except FigureException as e:
                raise GFDException(e.message, *self.line_counters[-1])
            
            if not issubclass(type(result), bool):
                raise GFDException(f"non bool return for check function {check_function.name}", *self.line_counters[-1])
            
            stack.append(result)

        elif token in self.custom_functions.keys():
            parameter_count, function_body = self.custom_functions[token]
            parameters = [stack.pop().name for _ in range(parameter_count)][::-1]
            for subtoken in function_body:
                if subtoken.startswith("$"):
                    subtoken = parameters[int(subtoken[1:]) - 1]
                self.update_stack(stack, subtoken)

        elif token in self.objects:
            stack.append(self.objects[token])
            
        else:
            raise GFDException(f"{token} is not defined", *self.line_counters[-1])

    def check_trivial(self):
        """adds all trivial properties derived from existing known properties to the properties"""
        # TODO
        pass


    def asy(self) -> str:
        """asy string of the figure"""
        # plc denotes if the objects should be labeled
        plc = {"p": True, "l": False, "c": False}
        sorted_objects = sorted(self.objects.values(), key=lambda obj: obj.criteria())
        for obj in sorted_objects:
            if obj.order == 0:
                obj.set_dir(properties, sorted_objects)
            if obj.order == 1:
                obj.set_lm_rm(properties, sorted_objects)
        definitions = "\n".join([obj.asy_definition() for obj in sorted_objects])
        draws = "\n".join([obj.asy_draw(plc) for obj in sorted_objects])
        with open("templates/template.asy", "r+") as file:
            template = file.read().replace("FIGURE", definitions + "\n\n" + draws)
        return template
    
    def properties_txt(self, properties_dct):
        s = ""
        for name, prop in properties_dct.items():
            t = f"{name}\n"
            for objs in prop:
                if any([obj not in self.objects.values() for obj in objs]):
                    continue
                t += f"    {', '.join(map(str, objs))}\n"
            t += "\n"
            s += t
        return s
    
    def txt(self) -> str:
        """explanations of the figure"""
        s = ""
        s += "Object in the Figure\n"
        for obj_name, obj in self.objects.items():
            s += f"    {obj_name}: {obj}\n"

        self.check_trivial()
        known_properties = {}
        for pname, p in properties.items():
            known_properties[pname] = p.copy()

        s += "\nKnown Properties of All Objects\n"
        s += self.properties_txt(known_properties)

        check_everything(self.objects.values())
        all_properties = {}
        for pname, p in properties.items():
            all_properties[pname] = p.copy()

        for name, st in all_properties.items():
            for known in known_properties[name]:
                st.remove(known)

        s += "\nUnknown Properties of All Objects\n"
        s += self.properties_txt(all_properties)

        return s

if __name__ == "__main__":
    if len(argv) < 2:
        raise GFDException("need a .gfd file")
    filename = argv[1]
    figure = Figure()
    figure.interpret(filename)
