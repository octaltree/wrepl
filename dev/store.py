from script import Script
from shutil import rmtree

def _countUp():
    i = 0
    while True:
        yield i
        i += 1


class Store:
    def __init__(self, filePath, dist=None):
        self.path = filePath
        self.dist = dist if dist is not None else filePath.parent / '.{}.d'.format(filePath.name)
        self.dist.mkdir(exist_ok=True, parents=True)

    def loadScript(self, n=-1):
        ss = self.dist / 'script' / 'stmts'
        ss.mkdir(exist_ok=True, parents=True)
        ts = []
        for i in _countUp():
            if n != -1 and i >= n: break
            d = ss / str(i)
            if not d.is_dir(): break
            f = d / 'raw'
            if not f.is_file(): break
            ts.append(f.read_text())
        return Script(self.path.name, '\n'.join(ts))

    def delete(self, idx): # idx以降を消す
        ss = self.dist / 'script' / 'stmts'
        ss.mkdir(exist_ok=True, parents=True)
        ds = sorted((d for d in ss.iterdir() if d.is_dir()), key=lambda d: d.name)
        for d in ds[idx:]:
            rmtree(d)

    def cellDist(self, idx):
        d = self.dist / 'script' / 'stmts' / str(idx)
        rmtree(d, ignore_errors=True)
        d.mkdir(exist_ok=True, parents=True)
        return d

    def saveCell(self, dist, cell):
        d = dist / 'raw'
        d.write_text(cell.raw)

    def valueDist(self, idx, name):
        d = self.dist / 'script' / 'stmts' / str(idx) / 'values'
        d.mkdir(exist_ok=True, parents=True)
        return d / name

if __name__ == '__main__':
    from pathlib import Path
    p = Path('example.py')
    print(Store(p).loadScript().cells)
