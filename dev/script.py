import ast
from itertools import zip_longest
from cell import Cell
from getter import getter

class Script:
    def __init__(self, fileName, raw):
        self.fileName = fileName
        self.raw = raw
        self.ast = ast.parse(raw, filename=fileName)

    @getter(False)
    def cells(self):
        def extract(raw, current, next):
            cli = current.lineno - 1
            off = '\n'.join(raw.splitlines()[cli:])[current.col_offset:]
            if next is None: return off
            nli = next.lineno - 1 - cli
            lines = off.splitlines()
            s = '\n'.join(lines[:nli]) + '\n' + lines[nli][:next.col_offset]
            return s.strip()
        return  [
                Cell(self.fileName, extract(self.raw, c, n), c)
                for (c, n) in zip_longest(self.ast.body, self.ast.body[1:])]

def _equal(na, nb):
    if type(na) is not type(nb): return False
    if isinstance(na, list):
        if len(na) != len(nb): return False
        for i in range(len(na)):
            if not _equal(na[i], nb[i]):
                return False
        return True
    if not isinstance(na, ast.AST): return na == nb
    # only AST
    if set(na._fields) != set(nb._fields): return False
    for fn in na._fields:
        va = getattr(na, fn)
        vb = getattr(nb, fn)
        if _equal(va, vb): continue
        return False
    return True

class Differ:
    def __init__(self, before, after):
        self.before = before
        self.after = after

    @getter(False)
    def numSameStmts(self):
        stmts = ([c.stmt for c in self.before.cells], [c.stmt for c in self.after.cells])
        num = 0
        for (p, n) in zip_longest(*stmts):
            if not _equal(p, n): break
            num += 1
        return num

    def deleted(self):
        return self.before.cells[self.numSameStmts:]
    def added(self):
        return self.after.cells[self.numSameStmts:]

if __name__ == '__main__':
    assert _equal(ast.parse('3\n2'), ast.parse('3;2'))
    assert not _equal(ast.parse('b = 3'), ast.parse('a = 3'))
    assert not _equal(ast.parse('a = [1,3]\na'), ast.parse('a= [2,3]; a'))
    print(Differ(Script('foo', 'a = [1,3]\na'), Script('foo', 'a=[2,3]; a')).added())
