from pathlib import Path
from script import Script
from code import InteractiveInterpreter
import time
import json
import dill
from getter import getter

def _stamp():
    return str(int(time.time()))


class Store:
    def __init__(self, filePath, dist=None):
        self.path = filePath
        self.dist = dist if dist is not None else filePath.parent / '.{}.d'.format(filePath.name)
        self.dist.mkdir(exist_ok=True, parents=True)

    @getter
    def fileName(self):
        return self.path.name

    def loadScript(self, n=-1):
        ss = self.dist / 'script' / 'stmts'
        ss.mkdir(exist_ok=True, parents=True)
        ds = sorted((d for d in ss.iterdir() if d.is_dir()), key=lambda d: d.name)
        limit = len(ds) if n == -1 else n
        ts = ((d / 'raw').read_text() for d in ds[:limit])
        return Script(self.path.name, '\n'.join(ts))

class Interpreter:
    def __init__(self, store):
        self.store = store
        self._refresh()

    def _refresh(self):
        self.executed = Script(self.store.fileName, '')
        self.interpreter = InteractiveInterpreter({
            '__dill__': dill,
            '__Logger__': None})

    def feed(self, script):
        ondisk = self.store.loadScript()
        (same, deleted, added) = ondisk.after(script)

#class Kernel:
#    def __init__(self, interpreter):
#        self.interpreter = interpreter
#
#    def feed(self, script):
#        self

if __name__ == '__main__':
    pass
