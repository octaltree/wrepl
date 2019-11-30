import ast
from itertools import zip_longest
from cell import Cell
from getter import getter

class Script:
    def __init__(self, fileName, raw):
        self.fileName = fileName
        self.raw = raw
        self.ast = ast.parse(raw, filename=fileName)

    @getter
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

class Differ:
    def __init__(self, before, after):
        self.before = before
        self.after = after

    @getter
    def numSameStmts(self):
        stmts = ([c for c in self.before.cells], [c for c in self.after.cells])
        num = 0
        for (p, n) in zip_longest(*stmts):
            if not p.equalAst(n): break
            num += 1
        return num

    @property
    def deleted(self):
        return self.before.cells[self.numSameStmts:]
    @property
    def added(self):
        return self.after.cells[self.numSameStmts:]

if __name__ == '__main__':
    print(Differ(Script('foo', 'a = [2,3]\nb'), Script('foo', 'a=[2,3]; a')).deleted)
