from nevow import util
import pgasync

class ConnectionPool(object):
        def __init__(self, junk, dsn, *args, **kwargs):
        self.params = dsn
            def runOperation(self, query, args={}):                    conn = pgasync.connect(**self.params)        cur = conn.cursor()        cursor.execute(query, args).addErrback(self._error)        d = conn.commit()        d.addErrback(self._error)        cur.release()        return d             def runQuery(self, query, args={}):        conn = pgasync.connect(**self.params)        cur = conn.cursor()        d = cur.exFetch(query,args)        d.addErrback(self._error)        cur.release()        return d

    def runInteraction(self, fun, query, args={}):
        print "r before pgasync.connect", fun, query, args
        conn = pgasync.connect(**self.params)
        print "r after pgasync.connect/before conn.cursor", fun
        cur = conn.cursor()
        print "r after conn.cursor", fun, cur
        d = util.maybeDeferred(fun, cur, query, args)
        print "r after maybeDeferred fun", fun, cur
        def commit(_, xconn, xcur):
            print "r before conn.commit", xconn, xcur
            xconn.commit()
            print "r after conn.commit", xconn, xcur
            xcur.release()
            print "r after cur.release", xconn, xcur
            return _
        d.addCallback(commit, conn, cur)
        d.addErrback(self._error)
        return d
            def _error(self, error):        print error
        return error