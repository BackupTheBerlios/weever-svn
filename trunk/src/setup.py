from distutils.core import setup
import ntsvc # this import will probably be something like
             # twisted.python.ntsvc later on
import glob

data_files = [
    ('styles', ['styles/undohtml.css',]),
    ('styles/passion', glob.glob('styles/passion/*.css')),
    ('images', glob.glob('images/*')),
    ('templates', glob.glob('templates/*.html')),
    ]

setup(appconfig = 'main.tac',
      data_files = data_files,
      options = {'twistedservice':
            {'packages': ['database.postgresql','psycopg'],
            }},
      )
