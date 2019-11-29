#!/usr/bin/env python
import ast
import sys
import pprint
import json

raw = sys.stdin.read()
c = ast.parse(raw)
#for a in c.body:
#    for k in a._fields:
#        print(getattr(a, k))
#    print(ast.dump(a))


def dump(node):
    if not isinstance(node, ast.AST): return node
    if isinstance(node, ast.Store): return 'Store#0x{:x}'.format(id(node))
    if isinstance(node, ast.Load): return 'Load#0x{:x}'.format(id(node))
    if isinstance(node, ast.Del): return 'Del#0x{:x}'.format(id(node))
    rec = lambda x: [dump(i) for i in x] if isinstance(x, list) else dump(x) if isinstance(x, ast.AST) else x
    return {
            'asdf': node.__class__.__name__,
            **{k: rec(getattr(node, k)) for k in node._fields}
            #**{k: getattr(node, k) for k in node._attributes}
            }

#json.dump(dump(c), sys.stdout)
pprint.PrettyPrinter(indent=4).pprint(dump(c))
