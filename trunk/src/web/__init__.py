import os.path as op
import sys

from utils import util


try: __file__
except NameError: __file__ = sys.executable

template_path = op.join(util.sibpath(op.split(__file__)[0],'templates'))
images_path = op.join(util.sibpath(op.split(__file__)[0],'images'))
styles_path = op.join(util.sibpath(op.split(__file__)[0],'styles'))

def getTemplate(name):
    return op.join(template_path, name)

def getImages():
    return images_path

def getStyles():
    return styles_path
