import os.path as op
import sys

from twisted.python import reflect
from nevow import compy

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

forms_adapters = """
web.forms.StyleStringRenderer       web.forms.StyleString       formless.iformless.ITypedRenderer
web.forms.StylePasswordEntryRenderer    web.forms.StylePasswordEntry     formless.iformless.ITypedRenderer
web.forms.StylePasswordRenderer     web.forms.StylePassword     formless.iformless.ITypedRenderer
web.forms.StyleFileUploadRenderer    web.forms.StyleFileUpload   formless.iformless.ITypedRenderer
"""

def load(S):
    for line in S.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            (a, o , i) = line.split()
            print a, o, i
            compy.registerAdapter(a,o,i)

load(forms_adapters)