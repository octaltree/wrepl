import symtable
from collections import deque
from getter import getter
import ast
import json
from functools import reduce

class Cell:
    def __init__(self, path, raw, stmt):
        self.raw = raw
        self.stmt = stmt
        self.table = symtable.symtable(raw, filename=path, compile_type='exec')

    def simpleTarget(self):
        s = self.stmt
        if any([isinstance(s, t) for t in [ast.AugAssign, ast.AnnAssign]]):
            return _names([s.target])
        if isinstance(s, ast.Assign):
            return _names(s.targets)
        return []

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
        if not cell: return False
        return _equal(self.stmt, cell.stmt)

    def allChanged(self, cells): # -> set(name)
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

    def allNeeded(self, cells): # -> [(idx, name)]
        rev = list(reversed(list(enumerate(cells))))
        load = set() # 実際に必要な(idx, name)
        needed = deque(self.needed) # 再帰に必要なname
        found = set() # 再帰が無限ループしないように
        while len(needed) > 0:
            n = needed.popleft()
            found.add(n)
            for (i, c) in rev:
                if n not in c.changed: continue
                needed.extend([n for n in c.needed if n not in found])
                load.add((i, n))
                if c.isLazy:
                    needed.extend([n for n in c.willNeeded if n not in found])
        # loadは{(0, 'foo'), (1, 'foo')}だが読み込むのは(1, 'foo')だけでいい
        tmp = sorted(list(load), key=lambda t: -t[0])
        uniq = set()
        res = []
        for t in tmp:
            if t[1] in uniq: continue
            uniq.add(t[1])
            res.append(t)
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

def _names(exprs):
    if isinstance(exprs, ast.AST): return _names([exprs])
    if len(exprs) == 0: return []
    if len(exprs) > 1: return reduce(
            lambda a, b: a + b,
            [_names(expr) for expr in exprs],
            [])
    expr = exprs[0]
    if isinstance(expr, ast.Name): return [expr.id]
    if not isinstance(expr, ast.AST): return []
    return reduce(
            lambda a, b: a + b,
            [_names(getattr(expr, fn)) for fn in expr._fields],
            [])


if __name__ == '__main__':
    assert _equal(ast.parse('3\n2'), ast.parse('3;2'))
    assert not _equal(ast.parse('b = 3'), ast.parse('a = 3'))
    assert not _equal(ast.parse('a = [1,3]\na'), ast.parse('a= [2,3]; a'))
    from script import Script
    from pathlib import Path
    cs = Script.read(Path('example.py')).cells
    for i in range(len(cs)):
        c = cs[i]
        print(c)
        print((c.needed, c.changed, c.willNeeded, c.willChanged))
        print((c.allNeeded(cs[:i]), c.allChanged(cs[:i])))
    for c in cs:
        print((c, c.simpleTarget()))
