import os.path as op
import sys

from utils import util


try: __file__
except NameError: __file__ = sys.executable

template_path = util.sibpath(__file__,'templates')
## FIXME: make passion dynamic from weever.ini
theme_path = util.sibpath(__file__, 'themes/passion')

def getTemplate(name):
    return op.join(template_path, name)

def getTheme():
    print theme_path
    return theme_path

class WebException(Exception): pass