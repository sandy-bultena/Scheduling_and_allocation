import yaml


class Foo:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c


with open('names.yaml', 'w') as file:
    foo = Foo(2, 4, 6)
    yaml.dump(foo, file)

print(open('names.yaml').read())
