import os.path as op
def sibpath(from, to):
    parent = op.split(op.split(from)[0])[0]
    if op.isfile(parent): path = util.sibpath(parent, to)
    else: path = op.join(parent, to)
    return path
