from nevow import util
import pgasync

class ConnectionPool(object):
        def __init__(self, junk, dsn, *args, **kwargs):
        self.params = dsn
            def runOperation(self, query, args={}):                    conn = pgasync.connect(**self.params)        cur = conn.cursor()        cursor.execute(query, args).addErrback(self._error)        d = conn.commit()        d.addErrback(self._error)        cur.release()        return d             def runQuery(self, query, args={}):        conn = pgasync.connect(**self.params)        cur = conn.cursor()        d = cur.exFetch(query,args)        d.addErrback(self._error)        cur.release()        return d

    def runInteraction(self, fun, query, args={}):
        conn = pgasync.connect(**self.params)
        cur = conn.cursor()
        d = util.maybeDeferred(fun, cur, query, args)
        def commit(_, xconn, xcur):
            xconn.commit()
            xcur.release()
            return _
        d.addCallback(commit, conn, cur)
        d.addErrback(self._error)
        return d
            def _error(self, error):        print error
        return error