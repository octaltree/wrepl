a = 0
def foo():
    global a
    a += 3

bar = foo

bar()
