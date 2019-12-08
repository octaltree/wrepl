#!/usr/bin/env python3

import argparse
import time
from pathlib import Path
from watcher import Watcher
from store import Store
from script import Script
from interpreter import Interpreter
import traceback

interpreter = None

def main():
    global interpreter
    args = parseArgs()
    path = Path(args.file[0]).resolve()
    interpreter = Interpreter(Store(path))
    if args.once:
        return once(path, args)
    else:
        once(path, args)
        Watcher(path, lambda _: once(path, args)).start()
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            return 1
    return 0

def once(path, args):
    try:
        s = Script.read(path)
    except SyntaxError as e:
        traceback.print_exc(limit=0)
        return 1
    return interpreter.feed(s)

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='file', type=str, nargs=1,
            help="watcing this")
    parser.add_argument('--once', action='store_true',
            help="execute once and exit")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    exit(main())
