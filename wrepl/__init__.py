#!/usr/bin/env python3

import sys
import time
import argparse
from pathlib import Path
from watchdog.observers import Observer
from .watcher import Watcher, normalizeText

filetype = [
        ('python3', {
            'suffix': '.py',
            'comment': '#',
            'executable': 'python',
            'saver': lambda f: 'import dill\ndill.dump_session("{}");\n'.format(f),
            'loader': lambda f: 'import dill\nfrom pathlib import Path\nif Path("{name}").is_file():dill.load_session("{name}");\n'.format(name=f)})]

def parse() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='file', type=str, nargs=1,
            help="watcing this")
    parser.add_argument('--filetype', metavar='filetype', type=str, nargs=1,
            help="only python3 is supported now")
    args = parser.parse_args()
    return main(args)

def main(args) -> int:
    target = Path(args.file[0])
    if target.is_dir():
        print('{} not found'.format(target), file=sys.stderr)
        return 1
    elif not target.exists():
        target.touch()
    dn = Path(target.name + '.wrepl')
    dn.mkdir(exist_ok=True)
    sess = dn / 'session'
    exed = dn / 'executed'
    last = dn / 'last'
    lock = dn / '.lock'
    if lock.exists():
        print('{} is locked. check other process'.format(dn), file=sys.stderr)
        return 1
    exed.touch()
    last.touch()
    lock.touch()
    try:
        ft1 = [v for (k, v) in filetype if args.filetype[0] == k] if args.filetype else []
        ft2 = [v for (k, v) in filetype if target.suffix == v['suffix']]
        ft = ft1 + ft2
        if len(ft) > 0:
            return run(ft[0], target, last, exed, sess)
        print('filetype not supported', file=sys.stderr)
        return 1
    finally:
        if lock.exists():
            lock.unlink()

def run(ft, target, last, exed, sess):
    handler = Watcher(ft, target, last, exed, sess)
    observer = Observer()
    observer.schedule(handler, str(target.parent), recursive=False)
    print(normalizeText(Path(exed).read_text(), '> '), end='', flush=True)
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        return 1

if __name__ == "__main__":
    exit(parse())
