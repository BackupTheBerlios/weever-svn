from nevow import util
import pgasync

class ConnectionPool(object):
        def __init__(self, junk, dsn, *args, **kwargs):
        self.params = dsn
            def runOperation(self, query, args={}):                    conn = pgasync.connect(**self.params)        cur = conn.cursor()        cursor.execute(query, args).addErrback(self._error)        d = conn.commit()        d.addErrback(self._error)        cur.release()        return d             def runQuery(self, query, args={}):        conn = pgasync.connect(**self.params)        cur = conn.cursor()        d = cur.exFetch(query,args)        d.addErrback(self._error)        cur.release()        return d

    def runInteraction(self, fun, query, args={}):
        print "r1"
        conn = pgasync.connect(**self.params)
        print "r2"
        cur = conn.cursor()
        print "r3"
        d = util.maybeDeferred(fun, cur, query, args)
        print "r4"
        def commit(_, conn, cur):
            print "r5"
            conn.commit()
            print "r5"
            cur.release()
            print "r6"
            return _
        d.addCallback(commit, conn, cur)
        d.addErrback(self._error)
        return d
            def _error(self, error):        print error
        return error