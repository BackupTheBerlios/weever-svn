from itertools import izip

from twisted.python import components
from nevow import util

class Store(object):

    def __init__(self, db_adapter, db_params):
        if db_adapter == 'pgasync':
            import pgasyncpool as adbapi
            database_dsn = db_params
        else:
            from twisted.enterprise import adbapi
            database_dsn = "dbname=%(dbname)s user=%(user)s password=%(password)s"
            if db_params.has_key('host'):
                database_dsn = "%s host=%(host)s port=%(port)s" % (database_dsn)
            database_dsn = database_dsn % db_params
            
        self.__pool = adbapi.ConnectionPool(db_adapter,
                                            dsn=database_dsn,
                                            cp_min=3, cp_max=10)

    def runQuery(self, query, args):
        d = self.__pool.runInteraction(self.mapQuery, query, args)
        return d

#    def mapQuery(self, curs, query, *args):
#        curs.execute(query, *args)
#        result = curs.fetchall()
#        columns = [d[0] for d in curs.description]
#        return [dict(zip(columns, r)) for r in result]

    def mapQuery(self, curs, query, args):
        curs.execute(query, args)
        d = util.maybeDeferred(curs.fetchall)
        def printerror(error, curs, query, args):
            print error.printTraceback()
            print curs
            print query
            print args
        def finalize(result, curs):
            columns = [d[0] for d in curs.description]
            return [dict(zip(columns, r)) for r in result]
        d.addErrback(printerror, curs, query, args)
        d.addCallback(finalize, curs)
        d.addErrback(printerror, curs, query, args)
        return d
          
    def runOperation(self, query, *args):
        d = self.__pool.runOperation(query, args[0])
        return d

    def runInteraction(self, fun, queries=(), args=()):
        d = self.__pool.runInteraction(fun, queries, args)
        return d
