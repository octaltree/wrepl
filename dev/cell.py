import symtable
from collections import deque
from getter import getter
import ast

class Cell:
    def __init__(self, fileName, raw, stmt):
        self.raw = raw
        self.stmt = stmt
        self.table = symtable.symtable(raw, filename=fileName, compile_type='exec')

    def _rec(self, root):
        ts = deque(root.get_children())
        res = []
        while len(ts) > 0:
            t = ts.popleft()
            for c in t.get_children(): ts.append(c)
            res += t.get_symbols()
        return res

    @getter
    def _global(self):
        return [s for s in self.table.get_symbols()] + [s
                for s in self._rec(self.table)
                if s.is_global() or s.is_declared_global()]

    @getter
    def needs(self): # 読み込む必要
        ss = self._global
        return [s.get_name() for s in ss
                if (s.is_referenced() or s.is_assigned()) and not s.is_imported()]

    @getter
    def imported(self): # この文でimportされるシンボル 保存する必要なし
        ss = self._global
        return [s.get_name() for s in ss if s.is_imported()]


    @getter
    def changed(self): # 保存する必要あり
        ss = self._global
        return [s.get_name() for s in ss
                if s.is_referenced() or s.is_assigned()]

    def __repr__(self):
        return '<Cell "{}">'.format(self.raw)

    def equalAst(self, cell):
        return _equal(self.stmt, cell.stmt)

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
        print(c.raw)
        print((c.needs, c.imported, c.changed))
