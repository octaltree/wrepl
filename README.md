# WREPL

Watch-Read-Eval-Print Loop<br>
`wrepl` is REPL wrapper. Since `wrepl` watchs file change, you can use your favorite text editor (nvim, vim, vi, etc.).
`wrepl` saves and restores global vars with [uqfoundation/dill](https://github.com/uqfoundation/dill), it is able to eval only changes.

<small>[日本語版](https://qiita.com/octaltree/items/ea2ed58ffc740c622b6b)</small>

## Install
```
pip install wrepl
```

## Usage

Watch with `wrepl foo.py`, edit foo.py.

## Files
It creates `foo.py.wrepl/` in executed dir for logging.
- foo.py.wrepl/last
  * latest executed version of foo.py
- foo.py.wrepl/executed
  * whole of snippets evaled
- foo.py.wrepl/session
  * global vars persistence

## Keeping in mind

If target file is changed multi times while running snippet, only newest change is running.
Older changes is discarded.

## TODO

* preload
* on_modifiedが肥大化してるので副作用切り離してテスト
* stdout, stderrをリアルタイムにprintする
* nodeやrubyに対応
