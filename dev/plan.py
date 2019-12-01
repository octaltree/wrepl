from itertools import zip_longest
from getter import getter

class Plan:
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

    def plan(self):
        execed = self.before.cells[:self.numSameStmts]
        added = self.after.cells[self.numSameStmts:]
        pass

class Operation:
    pass

class Storage(Operation):
    def __init__(self, name):
        self.name = name

class Load(Storage):
    pass

class Save(Storage):
    pass

class Run(Operation):
    def __init__(self, cell):
        pass

if __name__ == '__main__':
    from script import Script
    print(Plan(Script('foo', 'a = [2,3]\nb'), Script('foo', 'a=[2,3]; a')).deleted)
