from twisted.internet import defer
import pgasync

class ConnectionPool(object):
    def __init__(self, dbadapter, dsn, *args, **kwargs):
        self.params = dsn

    def runOperation(self, query, args={}):            
        d = defer.Deferred()
        conn = pgasync.connect(**self.params)
        dd = conn.cursor()
        dd.addCallback(self._runOperation, conn, d, query, args)
        return d
         
    def _runOperation(self, cursor, conn, d, query, args):
        cursor.execute(query, **args)
        dd = conn.commit()
        dd.addCallback(self._finish, d, cursor)
        dd.addErrback(self._finish, d, cursor)

    def runQuery(self, query, args={}):
        d = defer.Deferred()
        conn = pgasync.connect(**self.params)
        dd = conn.cursor()
        dd.addCallback(self._runQuery, conn, d, query, args)
        return d

    def _runQuery(self, cursor, conn, d, query, args):
        dx = cursor.exFetch(query, **args)
        dx.addCallback(self._finish, d, cursor)
        dx.addErrback(self._finish, d, cursor)
    
    def runInteraction(self, fun, query, args={}):
        d = defer.Deferred()
        conn = pgasync.connect(**self.params)
        dd = conn.cursor()
        dd.addCallback(self._runInteraction, fun, conn, d, query, args)
        return d
    
    def _runInteraction(self, cursor, fun, conn, d, query, args):
        def commit(result, conn, d, cursor):
            d = conn.commit()
            d.addCallback(lambda _: self._finish(result, d, cursor))
            d.addErrback(lambda _: self._finish(result, d, cursor))
        d = fun(cursor, query, args)
        d.addCallback(commit, conn, d, cursor)

    def _finish(self, result, d, cursor):
        cursor.release()
        d.callback(result)