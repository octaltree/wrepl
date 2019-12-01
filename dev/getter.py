def getter(f): # コピーしないので注意
    def res(self):
        name = f.__name__
        try:
            return getattr(self, '_' + name)
        except AttributeError:
            val = f(self)
            setattr(self, '_' + name, val)
            return val
    return property(res)

if __name__ == '__main__':
    from time import sleep

    class Hoge:
        def __init__(self):
            pass

        @getter
        def asdf(self):
            sleep(1)
            return 3

        @getter
        def foo(self):
            return [2]

    hoge = Hoge()
    print(hoge.asdf)
    print(hoge.asdf)
    print(hoge._asdf)
    hoge.foo.append(3)
    print(hoge.foo)
