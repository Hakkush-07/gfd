from main import Figure, construction_functions
from random import choice, sample

names = "ABCDEFGHIJKLMNOPQRSTUVXYZ"
name_index = 3
name_round = 0

def get_name():
    global name_index, name_round
    name = names[name_index] + (str(name_round) if name_round > 0 else "")
    name_index += 1
    if name_index >= len(names):
        name_round += 1
        name_index = 0
    return name

def main():
    gfd_lines = ["A B C = triangle"]
    figure = Figure()
    for gfd_line in gfd_lines:
        figure.interpret_line(gfd_line)
    number_of_constructions = 150
    i = 0
    while i < number_of_constructions:
        construction_function = choice(list(construction_functions.values()))
        print(construction_function)
        p1, l1, c1 = len(figure.p), len(figure.l), len(figure.c)
        p2, l2, c2 = construction_function.p, construction_function.l, construction_function.c
        print(p1, l1, c1)
        print(p2, l2, c2)
        if p1 < p2 or l1 < l2 or c1 < c2:
            continue
        points = sample(figure.p, k=p2)
        lines = sample(figure.l, k=l2)
        circles = sample(figure.c, k=c2)
        obj_names = [n for n, o in points] + [n for n, o in lines] + [n for n, o in circles]
        args = [o for n, o in points] + [o for n, o in lines] + [o for n, o in circles]
        try:
            result = construction_function(*args)
        except:
            continue
        result_lst = list(result) if type(result) == tuple else [result]
        result_names = [get_name() for _ in range(len(result_lst))]
        for n, o in zip(result_names, result_lst):
            o.name = n
            figure.objects[n] = o
        gfd_lines.append(f"{' '.join(result_names)} = {' '.join(obj_names)} {construction_function.name}")
        
        if result_lst[0].depth > 4:
            break

        i += 1
    with open("result.gfd", "w+") as file:
        file.write("\n".join(gfd_lines) + "\n")
    figure = Figure()
    figure.interpret("result.gfd")

if __name__ == "__main__":
    main()

