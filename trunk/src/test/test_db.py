from twisted.trial import unittest
from twisted.trial.util import deferredResult
from twisted.python import failure

from twisted.internet import reactor, defer

from database import store, interfaces
from config import general as c

class DbTestCase(unittest.TestCase):

    def testReturnTypes(self):
        db_bknd = store.Store(c.database_adapter, c.database_name,
                              c.database_user, c.database_password,
                              )
        def println(r):
            print r
        
        def parseResults(r):
            for element in r:
                success, result = element
                if not success:
                    print success
                    print result
                    raise failure.Failure("Not all deferreds where successful")
                
                else:
                    # We should test for results here
                    print result
                    
        
        a = interfaces.IUsersDatabase(db_bknd).findAllUsers()
        b = interfaces.IUsersDatabase(db_bknd).findUser('dialtone')
        h = interfaces.IUsersDatabase(db_bknd).getUserWithStats('dialtone')
        d = interfaces.IUsersDatabase(db_bknd).getUsersWithStats()
        e = interfaces.ITopicsDatabase(db_bknd).getAllPosts(3)
        f = interfaces.ISectionsDatabase(db_bknd).getAllSections()
        g = interfaces.ISectionsDatabase(db_bknd).getSection(2)

        dl = defer.DeferredList([a,b,h,d,e,f,g])
        dl.addCallback(parseResults)
        dl.addCallback(lambda r: reactor.stop())
        reactor.run()

