from twisted.trial import unittest
from twisted.trial.util import deferredResult
from twisted.python import failure

from twisted.internet import reactor, defer

from database import store, interfaces

database_adapter = 'psycopg'

#parameters are:
# dbname, host, user, password, sslmode, port
database_dsn = 'dbname=weever user=testuser password=test'
class DbTestCase(unittest.TestCase):

    def testReturnTypes(self):
        db_bknd = store.Store(database_adapter, database_dsn)

        def println(r):
            print r
        
        def parseResults(r):
            for element in r:
                success, result = element
                if not success:
                    raise failure.Failure()
                
                else:
                    # We should test for results here
                    if type(result) == dict:
                        continue
                    else: raise failure.Failure()
                     
        
        a = interfaces.IUsersDatabase(db_bknd).findAllUsers()
        b = interfaces.IUsersDatabase(db_bknd).findUser('dialtone')
        h = interfaces.IUsersDatabase(db_bknd).getUserWithStats('dialtone')
        d = interfaces.IUsersDatabase(db_bknd).getUsersWithStats()
        e = interfaces.ITopicsDatabase(db_bknd).getAllPosts(3, 10, 1)
        f = interfaces.ISectionsDatabase(db_bknd).getAllSections()
        g = interfaces.ISectionsDatabase(db_bknd).getSection(2)

        dl = defer.DeferredList([a,b,h,d,e,f,g])
        dl.addCallback(parseResults)
        dl.addCallback(lambda r: reactor.stop())
        reactor.run()

