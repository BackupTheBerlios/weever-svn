from itertools import izip

from database import interfaces as idb
from utils import util

from nevow import util as u

class Store(object):

    util.implements(idb.IS)

    def __init__(self, db_adapter, db_params):
        if db_adapter == 'pgasync':
            import pg_adbapi as adbapi
            database_dsn = db_params
            
        else:    
            from twisted.enterprise import adbapi

            database_dsn = "dbname=%(dbname)s user=%(user)s password=%(password)s" % (db_params)
            if db_params.has_key('host'):
                host_dsn = " host=%(host)s port=%(port)s" % (db_params)
            database_dsn = database_dsn + host_dsn
        self.__pool = adbapi.ConnectionPool(db_adapter,
                                            dsn=database_dsn,
                                            cp_min=3, cp_max=10)

    def runQuery(self, query, *args):
        d = self.__pool.runInteraction(self._mapQuery, query, args)
        return d

    def _mapQuery(self, curs, query, *args):
        curs.execute(query, *args)
        dx = u.maybeDeferred(curs.fetchall)
        def mapper(result, xcurs):
            columns = [d[0] for d in xcurs.description]
            return [dict(zip(columns, r)) for r in result]  
        def _error(error):
            print error      
        dx.addCallback(mapper, curs)
        dx.addErrback(_error)
        return dx

    def runOperation(self, query, *args):
        d = self.__pool.runOperation(query, args[0])
        return d

    def runInteraction(self, fun, queries=(), args=()):
        d = self.__pool.runInteraction(fun, queries, args)
        return d

util.backwardsCompatImplements(Store)
