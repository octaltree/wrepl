#!/usr/bin/env python
import sys
import symtable
import pprint

raw = sys.stdin.read()
tmp = symtable.symtable(raw, filename="<input>", compile_type='exec')
#for sc in tmp.get_children():
#    for s in sc.get_symbols():
#        print(s.is_global())
#for s in tmp.get_symbols():
#    print(s)
#    print(s.is_global())

def dumpTable(table):
    return  list({
            'name': table.get_name(),
            'type': table.get_type(),
            #'id': table.get_id(),
            'lineno': table.get_lineno(),
            #'optimized': table.is_optimized(),
            #'nested': table.is_nested(),
            'symbols': [dumpSymbol(s) for s in table.get_symbols()],
            'children': [dumpTable(c) for c in table.get_children()]}.items())

def dumpSymbol(symbol):
    return list({
            'name': symbol.get_name(),
            'global': symbol.is_global(),
            'declared_global': symbol.is_declared_global(),
            'local': symbol.is_local(),
            'imported': symbol.is_imported(),
            'parameter': symbol.is_parameter(),
            'referenced': symbol.is_referenced(),
            'assigned': symbol.is_assigned(),
            'free': symbol.is_free(),
            'namespaces': symbol.get_namespaces()}.items())

pprint.PrettyPrinter(indent=4).pprint(dumpTable(tmp))
