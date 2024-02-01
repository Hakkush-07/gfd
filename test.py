class A:
    def __init__(self, x):
        print("A init")
        self.x = x

class B(A):
    bs = []
    def __new__(cls, y, z):
        print("B new")
        for bx in cls.bs:
            if bx.y + bx.z == y + z:
                return bx
        return super().__new__(cls)

    def __init__(self, y, z):
        print("B init")
        super().__init__(0)
        for bx in B.bs:
            if bx.y + bx.z == y + z:
                return
        self.y = y
        self.z = z
        B.bs.append(self)

    def __repr__(self) -> str:
        return f"B[{self.x}, {self.y}, {self.z}]"

b = B(1, 2)

print(b)
print(B.bs)
b2 = B(0, 3)
print(b2)
print(B.bs)

print(b is b2)