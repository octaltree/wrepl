from pathlib import Path
from script import Script
import time
import json

def _stamp():
    return str(int(time.time()))

class Exec:
    def __init__(self, store):
        self.store = store

    def base(self):
        loaded = [t
                for t in (
                    (s, s.tryLoadScript())
                    for s in self.store.scripts())
                if t[1]]
        if len(loaded) == 0: return (None, 0)
        return max(
                [(t[0], self.script.countSameStmts(t[1]))
                    for t in loaded],
                key=lambda t: t[1])

    def dist(self):
        return StoredScript(self.store, _stamp()).setBase(*self.base())

    def feed(self, script):
        self.script = script
        stored = self.dist()

class Store:
    def __init__(self, fileName, dist):
        self.fileName = fileName
        self.dist = dist
        self.dist.mkdir(exist_ok=True, parents=True)

    def scripts(self):
        dist = self.dist / 'scripts'
        dist.mkdir(exist_ok=True, parents=True)
        ds = (d for d in dist.iterdir() if d.is_dir())
        return [StoredScript(self, d.name) for d in ds]


class StoredScript:
    def __init__(self, store, name):
        self.store = store
        self.name = name
        self.dist = store.dist / 'scripts' / name
        self.dist.mkdir(exist_ok=True, parents=True)

    base = None
    def setBase(self, storedScript, num):
        text = json.dumps({
            'name': storedScript.name if storedScript else '',
            'num': num})
        (self.dist / 'base').write_text(text)
        self.base = {'base': storedScript, 'num': num}
        return self
    def getBase(self):
        if self.base is not None: return self.base
        text = (self.dist / 'base').read_text()
        tmp = json.loads(text)
        self.base = {
                'base': None if not tmp['name'] else StoredScript(self.store, tmp['name']),
                'num': tmp['num']}
        return self.base

    def tryLoadScript(self, n=-1): # -> Script|None
        if n == 0: return Script(self.fileName, '')
        if self.base is None: return None
        if self.base['num'] > 0:
            baseScript = self.base['base'].tryLoadScript(self.base['num'])
            if not baseScript: return None
        dist = self.dist / 'stmts'
        dist.mkdir(exist_ok=True, parents=True)
        ds = sorted((d for d in dist.iterdir() if d.is_dir()), key=lambda d: d.name)
        limit = len(ds) if n == -1 else n - self.base['num']
        ts = ((d / 'raw').read_text() for d in ds[:limit])
        return Script(
                self.fileName,
                (baseScript.raw + '\n' if isinstance(baseScript, Script) else '') +
                '\n'.join(ts))

if __name__ == '__main__':
    e = Exec(Store('example.py', Path('.example.py.d')))
    e.feed(Script('example.py', Path('example.py').read_text()))
