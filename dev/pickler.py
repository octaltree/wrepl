import dill
from dill import Pickler, Unpickler
import __main__ as _main_module
from pickle import DEFAULT_PROTOCOL
from io import BytesIO as StringIO

globs = _main_module

def dump(obj, f, *args, **kwargs):
    d = Dumper(f, DEFAULT_PROTOCOL, **{
        "byref": None,
        "fmode": None,
        "recurse": None})
    d.dump(obj)

def load(file, ignore=None, **kwds):
    return Loader(file, ignore=ignore, **kwds).load()

class Dumper(Pickler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._main = globs

class Loader(Unpickler):
    def __init__(self, *args, **kwargs):
        Unpickler.__init__(self, *args, **kwargs)
        self._main = globs
        self._main.__dict__ = globs

def dumps(obj, protocol=None, byref=None, fmode=None, recurse=None, **kwds):#, strictio=None):
    """pickle an object to a string"""
    file = StringIO()
    dump(obj, file, protocol, byref, fmode, recurse, **kwds)#, strictio)
    return file.getvalue()

def loads(str, ignore=None, **kwds):
    """unpickle an object from a string"""
    file = StringIO(str)
    return load(file, ignore, **kwds)
