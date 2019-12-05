import dill
from pathlib import Path
from script import Script
from store import Store
from code import InteractiveInterpreter
from collections import deque

class Core(InteractiveInterpreter):
    error = False
    inner = False
    def showsyntaxerror(self, *args, **kwargs):
        self.error = True
        return super().showsyntaxerror(*args, **kwargs)

    def showtraceback(self, *args, **kwargs):
        self.error = True
        return super().showtraceback(*args, **kwargs)

    def run_private(self, source):
        origError = self.error
        self.inner = True
        self.error = False
        try:
            self.runsource(source, symbol='single')
            res = not self.error
            return res
        except Exception as e:
            raise e
        finally:
            self.error = origError
            self.inner = False

    def write(self, *args, **kwargs):
        #if self.inner: return None # TODO
        return super().write(*args, **kwargs)

class Interpreter:
    def __init__(self, store):
        self.store = store
        self.onMemory = type('', (), {
            'script': Script(self.store.path, ''),
            'loaded': []}) # [set(name)]
        self._refresh()

    def _refresh(self):
        self.onMemory.loaded = []
        self.interpreter = Core({
            '__pickle__': dill,
            '__Logger__': None})

    def _setLoaded(self, idx, s):
        self.onMemory.loaded += [set()
                for _ in range(idx + 1 - len(self.onMemory.loaded))]
        self.onMemory.loaded[idx] = s

    @property
    def _irreversible(self):
        loaded = [i for (i, l) in enumerate(self.onMemory.loaded) if l]
        if len(loaded) == 0: return Script(self.store.path, '')
        return Script.composeWith(
                self.store.path,
                self.onMemory.script.cells[:max(loaded) + 1])

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
        while True:
            #self._loadMemory()
            self._refreshIfDeleted(script)
            (same, _, added) = self.onMemory.script.after(script)
            if len(added) == 0: break
            cell = added[0]
            print(cell)
            self.store.delete(len(same))
            success = self._run(same, cell)
            if not success: break
            else:
                self.onMemory.script = Script.composeWith(script.path, script.cells[:len(same) + 1])
        #self._loadMemory()
        #self._refreshIfDeleted(script)
        #(same, _, added) = self.onMemory.script.after(script)
        #for c in added:
        #    print(self._run(same, c))

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

    def _save(self, dist, name):
        success = self.interpreter.run_private(
                'with open("{}", "wb") as f:'.format(dist) +
                '    __pickle__.dump({}, f)'.format(name))
        return success

    def _run(self, same, cell): # success : bool
        idx = len(same)
        # TODO 準備
        self.interpreter.error = False
        self.interpreter.runsource(cell.format, filename=self.store.path, symbol='exec')
        if not self.interpreter.error:
            self._setLoaded(idx, cell.allChanged(same))
            try:
                cd = self.store.cellDist(idx)
                for n in cell.allChanged(same):
                    s = self._save(self.store.valueDist(idx, n), n)
                    if not s: raise Exception('save error')
                self.store.saveCell(cd, cell)
                return True
            except Exception:
                self._refresh()
        return False

if __name__ == '__main__':
    p = Path('example.py')
    interpreter = Interpreter(Store(p))
    interpreter.feed(Script.read(p))
