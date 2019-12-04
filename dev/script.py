import ast
from itertools import zip_longest
from cell import Cell
from getter import getter

class Script:
    def __init__(self, path, raw):
        self.path = path
        self.raw = raw
        self.ast = ast.parse(raw, filename=path)

    def read(path):
        return Script(path, path.read_text())

    def composeWith(path, cells):
        return Script(path, '\n'.join((c.raw for c in cells)))

    @getter
    def cells(self):
        def extract(raw, current, next):
            cli = current.lineno - 1
            off = '\n'.join(raw.splitlines()[cli:])[current.col_offset:]
            if next is None: return off + '\n'
            nli = next.lineno - 1 - cli
            lines = off.splitlines()
            s = '\n'.join(lines[:nli]) + '\n' + lines[nli][:next.col_offset]
            return s
        return  [
                Cell(self.path, extract(self.raw, c, n), c)
                for (c, n) in zip_longest(self.ast.body, self.ast.body[1:])]

    def countSameStmts(self, s):
        cs = (self.cells, s.cells)
        num = 0
        for (p, n) in zip_longest(*cs):
            if not p: break
            if not p.equalAst(n): break
            num += 1
        return num

    def after(self, s):
        n = self.countSameStmts(s)
        return (self.cells[:n], self.cells[n:], s.cells[n:])

    def addCells(self, cs):
        self._cells += cs
        return self
