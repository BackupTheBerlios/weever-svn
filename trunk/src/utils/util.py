import os.path as op
from twisted.python import util

def sibpath(fro, to):
    parent = op.split(op.split(fro)[0])[0]
    if op.isfile(parent): path = util.sibpath(parent, to)
    else: path = op.join(parent, to)
    return path

### ZI forward compatibility crap, to make the switch easier.

usingZI = False
try:
    from zope.interface import implements, Interface, InterfaceClass
    if isinstance(components.Interface, InterfaceClass):
        usingZI = False
    else:
        usingZI = True
except ImportError:
    usingZI = False

if not usingZI:
    import inspect
    from twisted.python.components import Interface
    _IMPLS = '__setup_implements__'
    def backwardsCompatImplements(X):
        i = getattr(X, _IMPLS)
        delattr(X, _IMPLS)
        L = list(i)
        for base in X.__bases__:
            L.extend(getattr(base,'__implements__', ()))
        X.__implements__ = tuple(L)
    def implements(*ifaces):
        locs = inspect.currentframe().f_back.f_locals
        locs[_IMPLS] = locs.get(_IMPLS, ()) + ifaces
    def Attribute(doc):
        return property(doc=doc)
else:
    from twisted.python.components import backwardsCompatImplements
    from zope.interface import implements, Attribute