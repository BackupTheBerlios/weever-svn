from twisted.python import reflect
from twisted.python import components

import interfaces

from config import general

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

store = reflect.namedAny('database.'+general.database+'.store')
