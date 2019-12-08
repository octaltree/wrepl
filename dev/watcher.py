from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from datetime import datetime


class Watcher(PatternMatchingEventHandler):
    def __init__(self, path, f):
        super(Watcher, self).__init__(patterns=[str(path)])
        self.path = path
        self.f = f
    def on_modified(self, evt):
        self.f(evt)

    def start(self):
        self.observer = Observer()
        self.observer.schedule(self, str(self.path.parent), recursive=False)
        self.observer.start()

if __name__ == '__main__':
    import time
    from pathlib import Path
    import os
    path = Path('example.py').resolve()
    handler = Watcher(path, lambda e: e)
    observer = Observer()
    observer.schedule(handler, str(path.parent), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        exit(1)
