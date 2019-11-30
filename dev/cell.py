import symtable

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

    def needs(self): # 読み込む必要
        pass

    def used(self): # 保存される必要
        pass

    def __repr__(self):
        return '<Cell "{}">'.format(self.raw)



def symbolsNeedLoading(stmt, symtable):
    res = []
    symtable.get_symbols()
    pass

def symbolsNeedSaving(stmt, symtable):
    pass

if __name__ == '__main__':
    pass
