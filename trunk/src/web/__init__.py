import os.path as op
import sys

from utils import util
from config import parser


try: __file__
except NameError: __file__ = sys.executable

template_path = util.sibpath(__file__,'templates')
curr_theme = parser.getApplicationParameters('weever.ini')
theme_path = util.sibpath(__file__, 'themes/%s' % curr_theme)

def getTemplate(name):
    return op.join(template_path, name)

def getTheme():
    return theme_path

class WebException(Exception): pass