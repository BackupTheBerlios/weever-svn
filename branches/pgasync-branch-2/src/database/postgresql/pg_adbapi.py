from nevow import util
import pgasync

class ConnectionPool(object):
    
        self.params = dsn
        

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
        
        return error