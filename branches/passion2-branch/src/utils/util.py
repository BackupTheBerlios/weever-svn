import os.path as op
from twisted.python import util

def sibpath(fro, to):
    parent = op.split(op.split(fro)[0])[0]
    if op.isfile(parent): path = util.sibpath(parent, to)
    else: path = op.join(parent, to)
    return path
