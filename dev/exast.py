import ast
from itertools import zip_longest

def equal(na, nb):
    if type(na) is not type(nb): return False
    if isinstance(na, list):
        if len(na) != len(nb): return False
        for i in range(len(na)):
            if not equal(na[i], nb[i]):
                return False
        return True
    if not isinstance(na, ast.AST): return na == nb
    # only AST
    if set(na._fields) != set(nb._fields): return False
    for fn in na._fields:
        va = getattr(na, fn)
        vb = getattr(nb, fn)
        if equal(va, vb): continue
        return False
    return True

def countSameLines(before, after):
    stmts = (before.body, after.body)
    num = 0
    for (p, n) in zip_longest(*stmts):
        if not equal(p, n): break
        num += 1
    return num

if __name__ == '__main__':
    assert equal(ast.parse('3\n2'), ast.parse('3;2'))
    assert not equal(ast.parse('b = 3'), ast.parse('a = 3'))
    assert not equal(ast.parse('a = [1,3]\na'), ast.parse('a= [2,3]; a'))
