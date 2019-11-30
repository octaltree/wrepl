def getter(f):
    def res(self, *args, **kwargs):
        name = f.__name__
        try:
            return getattr(self, '_' + name)
        except AttributeError:
            val = f(self, *args, **kwargs)
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

    hoge = Hoge()
    print(hoge.asdf)
    print(hoge.asdf)
    print(hoge._asdf)
