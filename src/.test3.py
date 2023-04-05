class Test:
    def __init__(self, bla):
        self.bla = bla

    def foo(self):
        print("foo")

    def bar(self):
        print("bar")


def bar(bla):
    print(bla.bla)
