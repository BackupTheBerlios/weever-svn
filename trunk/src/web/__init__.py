import os.path as op
import sys

from utils import util


try: __file__
except NameError: __file__ = sys.executable

template_path = util.sibpath(__file__,'templates')
images_path = util.sibpath(__file__,'images')
styles_path = util.sibpath(__file__,'styles')

def getTemplate(name):
    return op.join(template_path, name)

def getImages():
    return images_path

def getStyles():
    return styles_path

class WebException(Exception): pass