from distutils.core import setup
import ntsvc # this import will probably be something like
             # twisted.python.ntsvc later on
import glob

data_files = [
    ('themes/passion', glob.glob('themes/passion/*'))
    ('templates', glob.glob('templates/*.html')),
    ('files', ['files/weever.ini'])
    ]

setup(data_files = data_files,
      options = {'twistedservice':
            {'packages': ['database.postgresql','psycopg','encodings'],
            }},
      )
