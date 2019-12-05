import symtable
from collections import deque
from getter import getter
import ast
import json

class Cell:
    def __init__(self, path, raw, stmt):
        self.raw = raw
        self.stmt = stmt
        self.table = symtable.symtable(raw, filename=path, compile_type='exec')

    @property
    def format(self):
        return '\n' * (self.stmt.lineno - 1) + self.raw

    @getter
    def isLazy(self):
        return any([isinstance(self.stmt, t)
            for t in [ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]])

    @getter
    def _symbols(self):
        return self.table.get_symbols()

    @getter
    def _symbolsRecursively(self):
        ts = deque(self.table.get_children())
        ss = []
        while len(ts) > 0:
            t = ts.popleft()
            for c in t.get_children(): ts.append(c)
            ss += t.get_symbols()
        return [s for s in ss if s.is_global() or s.is_declared_global()]

    @getter
    def needed(self): # この文のために読み込む必要
        if self.isLazy:
            return [s.get_name() for s in self._symbols if s.is_referenced()]
        return [s.get_name() for s in self._symbols + self._symbolsRecursively
                if (s.is_referenced() or s.is_assigned()) and not s.is_imported()]

    @getter
    def changed(self):
        if self.isLazy:
            return [s.get_name() for s in self._symbols
                    if s.is_referenced() or s.is_assigned() or s.is_imported()]
        return [s.get_name() for s in self._symbols + self._symbolsRecursively
                if s.is_referenced() or s.is_assigned() or s.is_imported()]

    @getter
    def willNeeded(self):
        if not self.isLazy: return []
        return [s.get_name() for s in self._symbolsRecursively
                if (s.is_referenced() or s.is_assigned()) and not s.is_imported()]

    @getter
    def willChanged(self):
        if not self.isLazy: return []
        return [s.get_name() for s in self._symbolsRecursively
                if s.is_referenced() or s.is_assigned() or s.is_imported()]

    def __repr__(self):
        return '<Cell {} {}>'.format(self.stmt.lineno, json.dumps(self.raw.splitlines()[0]))

    def equalAst(self, cell):
        return _equal(self.stmt, cell.stmt)

    def allChanged(self, cells):
        rev = list(reversed(list(enumerate(cells))))
        res = set(self.changed)
        needed = deque(self.needed)
        found = set()
        while len(needed) > 0:
            n = needed.popleft()
            found.add(n)
            for (i, c) in rev:
                if n in c.changed:
                    needed.extend([n for n in c.needed if n not in found])
                    if c.isLazy:
                        res |= set(c.willChanged)
        return res

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


if __name__ == '__main__':
    assert _equal(ast.parse('3\n2'), ast.parse('3;2'))
    assert not _equal(ast.parse('b = 3'), ast.parse('a = 3'))
    assert not _equal(ast.parse('a = [1,3]\na'), ast.parse('a= [2,3]; a'))
    from script import Script
    from pathlib import Path
    for c in Script('example.py', Path('example.py').read_text()).cells:
        print(c)
        print((c.needed, c.changed, c.willNeeded, c.willChanged))
