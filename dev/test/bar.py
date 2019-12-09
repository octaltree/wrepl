from code import InteractiveInterpreter
import __main__ as m

i = InteractiveInterpreter(m)
i.runsource('print(type(globals()))', symbol='exec')
