from copy import deepcopy

def getter(copy):
    def decorator(f):
        def res(self, *args, **kwargs):
            name = f.__name__
            try:
                tmp =  getattr(self, '_' + name)
                return deepcopy(tmp) if copy else tmp
            except AttributeError:
                val = f(self, *args, **kwargs)
                setattr(self, '_' + name, val)
                return val
        return property(res)
    return decorator

if __name__ == '__main__':
    from time import sleep

    class Hoge:
        def __init__(self):
            pass

        @getter(True)
        def asdf(self):
            sleep(1)
            return 3

    hoge = Hoge()
    print(hoge.asdf)
    print(hoge.asdf)
    print(hoge._asdf)
