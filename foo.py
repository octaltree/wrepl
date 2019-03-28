#!/usr/bin/env python3

import argparse
import watchdog
from pathlib import Path

def main(args) -> int:
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='file', type=str, nargs=1,
            help="watcing this")
    args = parser.parse_args()
    exit(main(args))
