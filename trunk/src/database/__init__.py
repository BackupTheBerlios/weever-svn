import ConfigParser as cp
import os

from twisted.python import reflect
from twisted.python import components
from twisted.python import util, log

import interfaces



database_adapters = """
database.postgresql.adapt.UsersDatabase       database.postgresql.store.Store      database.interfaces.IUsersDatabase
database.postgresql.adapt.SectionsDatabase    database.postgresql.store.Store      database.interfaces.ISectionsDatabase
database.postgresql.adapt.TopicsDatabase      database.postgresql.store.Store      database.interfaces.ITopicsDatabase
"""

def load(S):
    for line in S.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            (a, o , i) = line.split()
            a = reflect.namedAny(a)
            o = reflect.namedAny(o)
            i = reflect.namedAny(i)
            components.registerAdapter(a,o,i)

load(database_adapters)

parser = cp.ConfigParser()
config_file = os.path.join(util.sibpath(os.path.split(__file__)[0],'config'),'weever.ini')
log.msg(config_file)
parser.read(config_file)
dbms = parser.get('Database', 'dbms')

store = reflect.namedAny('database.'+dbms+'.store')
