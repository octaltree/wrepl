#!/usr/bin/env python3

import sys
import time
import argparse
import readchar
import subprocess
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

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
    args = parser.parse_args()
    return main(args)

def main(args) -> int:
    target = Path(args.file[0])
    if not target.is_file():
        print('{} not found'.format(target), file=sys.stderr)
        return 1
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
        for (k, v) in filetype:
            if target.suffix == v['suffix']:
                run(v, target, last, exed, sess)
                return 0
        print('filetype not supported', file=sys.stderr)
        return 1
    finally:
        lock.unlink()

class Watcher(PatternMatchingEventHandler):
    processing = False
    que = []
    def __init__(self, ft, target, last, exed, sess):
        super(Watcher, self).__init__(patterns=['*' + target.name])
        self.ft = ft
        self.target = target
        self.last = last
        self.exed = exed
        self.sess = sess
        self.lastText = last.read_text()
    def setLast(self, text):
        self.lastText = text
        self.last.write_text(text)
    def appendExed(self, sin, sout, serr):
        raw = self.exed.read_text()
        text = (raw + normalizeText(sin, '')
                + normalizeText(sout, '{}1 '.format(self.ft['comment']))
                + normalizeText(serr, '{}2 '.format(self.ft['comment'])))
        self.exed.write_text(text)
    def on_modified(self, evt):
        self.que += [self.target.read_text()]
        print('rest queue count: {}'.format(len(self.que)), file=sys.stderr)
        if self.processing:
            return
        self.processing = True
        self.process()
        self.processing = False
    def process(self):
        while len(self.que) > 0:
            x = self.que.pop(0)
            y = self.subText(x, self.lastText)
            if y == '':
                continue
            label = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
            script = normalizeText('\n'.join([
                self.ft['loader'](str(self.sess)), y,
                self.ft['saver'](str(self.sess))]))
            repl = subprocess.Popen(self.ft['executable'], shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            repl.stdin.write(script.encode('utf-8'))
            repl.stdin.flush()
            repl.stdin.close()
            repl.wait()
            sout = repl.stdout.read().decode('utf-8')
            serr = repl.stderr.read().decode('utf-8')
            print(sout, end='', flush=True)
            print(serr, file=sys.stderr, end='', flush=True)
            # ログ
            z = '\n'.join([self.ft['comment'] + ' ' + label, y])
            self.appendExed(z, sout, serr)
            self.setLast(x)
    def subText(self, newer, older):
        # 最終行の改行
        n1 = normalizeText(newer)
        o1 = normalizeText(older)
        if n1 == o1:
            return ''
        # padding
        n2 = n1.split('\n') + [''] * (len(o1) - len(n1))
        o2 = o1.split('\n') + [''] * (len(n1) - len(o1))
        first = None
        for (i, (n, o)) in enumerate(zip(n2, o2)):
            if first is None and n != o:
                first = i
        return '\n'.join(n2[first:]) + '\n'
    def on_created(self, evt):
        pass
    def on_deleted(self, evt):
        pass # TODO

def normalizeText(text, c=''):
    if text == '':
        return text
    rs = text.rstrip('\n').split('\n') # 最終行改行無
    # 全行コメントアウトしてから最終行にも改行をつける
    ctext = '\n'.join([c + r for r in rs]) + '\n'
    return ctext

def run(ft, target, last, exed, sess):
    handler = Watcher(ft, target, last, exed, sess)
    observer = Observer()
    observer.schedule(handler, str(target.parent), recursive=False)
    observer.start()
    while True:
        time.sleep(10)

if __name__ == "__main__":
    exit(parse())
