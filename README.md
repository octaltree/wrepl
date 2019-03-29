# WREPL

Watch-Read-Eval-Print Loop<br>
Since `wrepl` watchs file change, you can use your favorite text editor (nvim, vim, vi, etc.).
`wrepl` saves and restores global vars with [uqfoundation/dill](https://github.com/uqfoundation/dill), it is able to eval only changes.

## Install
```
pip install wrepl
```

## Usage

Watch with `wrepl foo.py`, edit foo.py.

## Files
- foo.py.wrepl/executed
  * whole of snippets evaled

## Keeping in mind

If target file is changed multi times while running snippet, only newest change is running.
Older changes is discarded.

## TODO

* stdout, stderrをリアルタイムにprintする
