from pathlib import Path
from script import Script
from code import InteractiveInterpreter
import time
import json
import dill
from getter import getter
from shutil import rmtree
from collections import deque

def _stamp():
    return str(int(time.time()))


class Store:
    def __init__(self, filePath, dist=None):
        self.path = filePath
        self.dist = dist if dist is not None else filePath.parent / '.{}.d'.format(filePath.name)
        self.dist.mkdir(exist_ok=True, parents=True)

    def loadScript(self, n=-1):
        ss = self.dist / 'script' / 'stmts'
        ss.mkdir(exist_ok=True, parents=True)
        ds = sorted((d for d in ss.iterdir() if d.is_dir()), key=lambda d: d.name)
        limit = len(ds) if n == -1 else n
        ts = ((d / 'raw').read_text() for d in ds[:limit])
        return Script(self.path.name, '\n'.join(ts))

    def delete(self, n):
        ss = self.dist / 'script' / 'stmts'
        ss.mkdir(exist_ok=True, parents=True)
        ds = sorted((d for d in ss.iterdir() if d.is_dir()), key=lambda d: d.name)
        for d in ds[n:]:
            rmtree(d)

class Interpreter:
    def __init__(self, store):
        self.store = store
        self.onMemory = type('', (), {
            'script': Script(self.store.path, ''),
            'indexes': []})
        self._refresh()

    def _refresh(self):
        self.onMemory.indexes = []
        self.interpreter = InteractiveInterpreter({
            '__dill__': dill,
            '__Logger__': None})

    @property
    def _irreversible(self):
        return (Script(self.store.path, '')
                if len(self.onMemory.indexes) == 0 else
                Script.composeWith(
                    self.store.fileName,
                    self.onMemory.script.cells[:max(self.onMemory.indexes)]))

    def _loadMemory(self):
        onDisk = self.store.loadScript()
        (_, deleted, _) = self._irreversible.after(onDisk)
        if len(deleted) > 0:
            self._refresh()
        self.onMemory.script = onDisk

    def _refreshIfDeleted(self, script):
        (_, deleted, _) = self._irreversible.after(script)
        if len(deleted) > 0:
            self._refresh()

    def feed(self, script):
        #while True:
        #    self._loadMemory()
        #    self._refreshIfDeleted(script)
        #    (same, _, added) = self.onMemory.script.after(script)
        #    if len(added) == 0: break
        #    cell = added[0]
        #    self._run(same, cell)
        self._loadMemory()
        self._refreshIfDeleted(script)
        (same, _, added) = self.onMemory.script.after(script)
        for c in added:
            self._run(same, c)

    def _prepare(self, same, cell):
        pre = list(reversed(list(enumerate(same))))
        def lines(ts, c): # -> [idx]
            needed = deque()
            res = set()
            while len(needed) > 0:
                n = needed.popleft()
                for (i, c) in ts:
                    if n in c.changed:
                        res.add(i)
                        if c.isLazy:
                            for name in c.willChanged:
                                needed.append(name)
                        break
            return res
        load = sorted(list(lines(pre, cell)), key=lambda i: -i)
        # TODO このインデックスから上書きしないように全てのnameを読み込む

    def _run(self, same, cell):
        # TODO 準備
        # TODO エラーハンドリング
        self.interpreter.runsource(cell.format, filename=self.store.path, symbol='exec')
        # TODO 片付け

if __name__ == '__main__':
    p = Path('example.py')
    interpreter = Interpreter(Store(p))
    interpreter.feed(Script.read(p))
