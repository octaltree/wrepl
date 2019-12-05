from script import Script
from shutil import rmtree


class Store:
    def __init__(self, filePath, dist=None):
        self.path = filePath
        self.dist = dist if dist is not None else filePath.parent / '.{}.d'.format(filePath.name)
        self.dist.mkdir(exist_ok=True, parents=True)

    def loadScript(self, n=-1):
        ss = self.dist / 'script' / 'stmts'
        ss.mkdir(exist_ok=True, parents=True)
        ds = sorted((d for d in ss.iterdir() if d.is_dir()), key=lambda d: int(d.name))
        limit = len(ds) if n == -1 else n
        ts = ((d / 'raw').read_text() for d in ds[:limit])
        return Script(self.path.name, '\n'.join(ts))

    def delete(self, n): # Cellを最初のn個残して消す
        ss = self.dist / 'script' / 'stmts'
        ss.mkdir(exist_ok=True, parents=True)
        ds = sorted((d for d in ss.iterdir() if d.is_dir()), key=lambda d: d.name)
        for d in ds[n:]:
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
