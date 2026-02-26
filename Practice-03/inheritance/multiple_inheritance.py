class A:
    def method_a(self):
        print("Method from class A")


class B:
    def method_b(self):
        print("Method from class B")


class C(A, B):
    pass


obj = C()
obj.method_a()
obj.method_b()
