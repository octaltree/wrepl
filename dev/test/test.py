import dill
from code import InteractiveInterpreter
import pdb
import pickler


#a = 2
#b = 1
#print(globals())
#def foo():
#    global a
#    a *= 3
#    return (a, b)
#
##pdb.runeval('dill.dumps(foo)', globals=globals())
#store = dill.dumps(foo)
#del a
#del b
#del foo
#a = 5
#b = 7
##pdb.runeval('dill.loads(store)', globals=globals())
#foo = dill.loads(store)
#print(foo.__globals__)
#print(foo()) # (15, 7)



i = InteractiveInterpreter({
            '__name__': '__main__',
            '__pickle__': pickler})
i.runsource('__pickle__.globs = globals()', symbol='exec')
#i.runsource('import dill', symbol='exec')
i.runsource('import pdb', symbol='exec')
#i.runsource('dill.settings["recurse"] = False', symbol='exec')
i.runsource('''
a = 2
b = 1
''', symbol='exec')
#i.runsource('print(globals())', symbol='exec')
i.runsource('''
def foo():
    global a
    a *= 3
    return (a, b)
#print(foo.__globals__)
#pdb.runeval('dill.dumps(foo)', globals=globals())
store = __pickle__.dumps(foo)
del a
del b
del foo
        ''', symbol='exec')

i.runsource('''
#a = 5
#b = 7
#pdb.runeval('dill.loads(store)', globals=globals())
foo = __pickle__.loads(store)
print(foo.__globals__)
print(foo())
        ''', symbol='exec')
