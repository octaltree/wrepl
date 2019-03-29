# WREPL

Watch-Read-Eval-Print Loop<br>
`wrepl` watchs and eval file change, you can use your favorite text editor (nvim, vim, vi, ...).

# Usage

Watch with `wrepl foo.py`, edit foo.py.

# Keeping in mind

If target file is changed multi times while running snippet, only newest change is running.
Older changes is discarded.

# TODO

* stdout, stderrをリアルタイムにprintする
