from code import InteractiveInterpreter
import dill
import time

i = InteractiveInterpreter({
            '__name__': '__main__',
            '__time__': time,
            '__pickle__': dill,
            '__share__': {},
            '__Logger__': None}) # TODO

#i.runsource(
#        'with open("/home/octaltree/workspace/wrepl/dev/.example2.py.d/script/stmts/0/values/a", "rb") as f:\n' +
#        '    a = __pickle__.load(f)', symbol='exec')
#i.runsource(
#        'with open("/home/octaltree/workspace/wrepl/dev/.example2.py.d/script/stmts/2/values/foo", "rb") as f:\n' +
#        '    foo = __pickle__.load(f)', symbol='exec')
#i.runsource(
#        'with open("/home/octaltree/workspace/wrepl/dev/.example2.py.d/script/stmts/2/values/bar", "rb") as f:\n' +
#        '    bar = __pickle__.load(f)', symbol='exec')
#i.runsource('print(globals())', symbol='exec')
#i.runsource('bar()', symbol='exec')

with open("/home/octaltree/workspace/wrepl/dev/.example2.py.d/script/stmts/0/values/a", "rb") as f:
    a = dill.load(f)
with open("/home/octaltree/workspace/wrepl/dev/.example2.py.d/script/stmts/2/values/foo", "rb") as f:
    foo = dill.load(f)
with open("/home/octaltree/workspace/wrepl/dev/.example2.py.d/script/stmts/2/values/bar", "rb") as f:
    bar = dill.load(f)
print(foo())
