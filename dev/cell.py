import symtable
from collections import deque

class Symbol:
    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)
    name = ''
    imported = False

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

    def needs(self): # 読み込む必要
        ss = [s for s in self.table.get_symbols()] + [s
                for s in self._rec(self.table)
                if s.is_global() or s.is_declared_global()]
        return [s.get_name() for s in ss
                if (s.is_referenced() or s.is_assigned()) and not s.is_imported()]

    def imported(self):
        pass

    def changed(self):
        pass

    def __repr__(self):
        return '<Cell "{}">'.format(self.raw)


if __name__ == '__main__':
    from exast import Code
    from pathlib import Path
    for c in Code('example.py', Path('example.py').read_text()).cells():
        print(c.raw)
        print(c.needs())