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

    def countSameStmts(self, s):
        cs = (self.cells, s.cells)
        num = 0
        for (p, n) in zip_longest(*cs):
            if not p.equalAst(n): break
            num += 1
        return num
