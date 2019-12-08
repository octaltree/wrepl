import dill
from pathlib import Path
from script import Script
from store import Store
from code import InteractiveInterpreter
from collections import deque
from functools import reduce
import time

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
            self.runsource(source, symbol='exec')
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
        self.share = {}
        self.onMemory.loaded = []
        self.interpreter = Core({
            '__name__': '__main__',
            '__time__': time,
            '__pickle__': dill,
            '__share__': self.share,
            '__Logger__': None}) # TODO

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

    def _load(self, cells, cell):
        for (i, n) in cell.allNeeded(cells):
            if n in _unionAll(self.onMemory.loaded[i:]): continue
            success = self.interpreter.run_private(
                    'with open("{}", "rb") as f:\n'.format(self.store.valueDist(i, n)) +
                    '    {} = __pickle__.load(f)'.format(n))
            if not success:
                return i
        return None

    def _refreshIfDeleted(self, script):
        (_, deleted, _) = self._irreversible.after(script)
        if len(deleted) > 0:
            self._refresh()

    def feed(self, script):
        while True:
            self._loadMemory()
            self._refreshIfDeleted(script)
            (same, _, added) = self.onMemory.script.after(script)
            if len(added) == 0: break
            cell = added[0]
            print(cell)
            self.store.delete(len(same))
            st = self._load(same, cell)
            if st is not None:
                self.store.delete(st)
                continue
            success = self._run(same, cell)
            if not success: break

    def _save(self, dist, name):
        success = self.interpreter.run_private(
                'with open("{}", "wb") as f:'.format(dist) +
                '    __pickle__.dump({}, f)'.format(name))
        return success

    def _run(self, same, cell): # success : bool
        idx = len(same)
        # TODO log
        # TODO memo last execed expr
        self.interpreter.error = False
        self.interpreter.run_private('__share__["result"] = {}')
        self.interpreter.run_private('__share__["result"]["ready"] = __time__.time()')
        print('ready {}'.format(self.share['result']['ready']))
        self.interpreter.run_private('__share__["tmp"] = __time__.perf_counter()')
        self.interpreter.runsource(cell.format, filename=self.store.path, symbol='exec')
        print(cell.assigned)
        self.interpreter.run_private('__share__["result"]["time"] = __time__.perf_counter() - __share__["tmp"]')
        self.share['result']['success'] = not self.interpreter.error
        # TODO print assignment
        if not self.interpreter.error:
            print('time {}'.format(self.share['result']['time']))
            try:
                self._setLoaded(idx, cell.allChanged(same))
                cd = self.store.cellDist(idx)
                self.store.writeResult(idx, self.share['result'])
                for n in cell.allChanged(same):
                    s = self._save(self.store.valueDist(idx, n), n)
                    if not s: raise Exception('save error')
                self.store.saveCell(cd, cell)
                return True
            except Exception as e:
                self._refresh()
        return False

def _unionAll(ss):
    return reduce(lambda a, b: a | b, ss, set())

if __name__ == '__main__':
    p = Path('example.py')
    interpreter = Interpreter(Store(p))
    interpreter.feed(Script.read(p))
