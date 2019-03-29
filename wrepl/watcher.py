import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class Watcher(PatternMatchingEventHandler):
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
    def appendExed(self, text):
        with open(self.exed, 'a+') as f:
            f.write(normalizeText(text))
    def on_modified(self, evt):
        x = self.target.read_text()
        y = subText(x, self.lastText)
        if y == '' or y == '\n':
            print('no changes', file=sys.stderr)
            return None
        print(normalizeText(y, '> '), end='', flush=True)
        label = lambda utc, memo: ' '.join([
            self.ft['comment'], memo, utc.isoformat(timespec='seconds') + 'Z']) + '\n'
        startLabel = label(datetime.utcnow(), 'start')
        print(startLabel, end='')
        (sout, serr) = self.run(y)
        finishLabel = label(datetime.utcnow(), 'finish')
        print(finishLabel, end='')
        text = (y + normalizeText(startLabel) +
                normalizeText(sout, '{}1 '.format(self.ft['comment'])) +
                normalizeText(serr, '{}2 '.format(self.ft['comment'])) +
                normalizeText(finishLabel))
        self.appendExed(text)
        self.setLast(x)
    def run(self, y):
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
        return (sout, serr)

def subText(newer, older):
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
    if re.match('^[\s]+', n2[first]): # ネストされてたら遡る
        indent = len(re.match('^([\s]+)', n2[first]).group(1))
        tf = first
        for (i, r) in enumerate(reversed(n2[:first+1])):
            tf = first - i
            if re.match('^[\s]*$', r):
                continue
            mat = re.match('^([\s]*)[^\s]', r)
            if mat and len(mat.group(1)) < indent:
                break
        first = tf
    return normalizeText('\n'.join(n2[first:]) + '\n')

def normalizeText(text, c=''):
    if text == '':
        return text
    rs = text.rstrip('\n').split('\n') # 最終行改行無
    # 全行コメントアウトしてから最終行にも改行をつける
    ctext = '\n'.join([c + r for r in rs]) + '\n'
    return ctext
