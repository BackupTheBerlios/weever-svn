from utils import util

from database import interfaces as idb
from database import defcache
import queries as q

def _transformResult(result):
    if result:
        return result[0]
    else:
        return None

def cleanCache(*fn):
    def clear(res, fnc):
        for f in fnc:
            f.clearCache()
        return res
    def _(fun):
        def _1(self, *args, **kwargs):
            d = fun(self, *args, **kwargs)
            d.addCallback(clear, fn)
            return d
        return _1
    return _


class UsersDatabase(object):
    
    util.implements(idb.IUsersDatabase)

    def __init__(self, db):
        self.store = db

    def findUser(self, username):
        d = self.store.runQuery(q.user, username)
        d.addCallback(_transformResult)
        return d
    
    def findAllUsers(self):
        return self.store.runQuery(q.all_users)

    def getUserWithStats(self, username):
        return self.store.runQuery(q.user_stats, username)

    def getUsersWithStats(self):
        return self.store.runQuery(q.all_users_stats)

    def addUser(self, properties):
        return self.store.runOperation(q.add_user, properties)

util.backwardsCompatImplements(UsersDatabase)

class SectionsDatabase(object):

    util.implements(idb.ISectionsDatabase)

    def __init__(self, db):
        self.store = db

    def getAllSections(self):
        return self.store.runQuery(q.all_sections)
    getAllSections = defcache.DeferredCache(getAllSections)
    
    def simpleGetAllSections(self):
        return self.store.runQuery(q.simple_all_sections)
    simpleGetAllSections = defcache.DeferredCache(simpleGetAllSections)
    
    def getSectionInfo(self, sid):
        return self.store.runQuery(q.simple_section, sid) #.addCallback(_transformResult)

    def getSection(self, sid):
        return self.store.runQuery(q.section, sid)

    def addSection(self, properties):
        return self.store.runOperation(q.add_section, properties)
    addSection = cleanCache([getAllSections, simpleGetAllSections])(addSection)
    
    def delSection(self, sid):
        return self.store.runOperation(q.del_section, sid)
    delSection = cleanCache(delSection)

util.backwardsCompatImplements(SectionsDatabase)

class TopicsDatabase(object):

    util.implements(idb.ITopicsDatabase)

    def __init__(self, db):
        self.store = db

    def getAllPosts(self, tid, num, offset):
        return self.store.runQuery(q.topic, tid, num, offset)

    def getPostsNum(self, tid):
        return self.store.runQuery(q.posts_num, tid)

    def getTopTopics(self, num):
        return self.store.runQuery(q.top_threads, num)
    getTopTopics = defcache.DeferredCache(getTopTopics)

    def addTopic(self, args):        
        return self.store.runInteraction(self._addTopic, \
                                         q.add_topic,
                                         args
                                         )
    addTopic = cleanCache(getTopTopics)(addTopic)

    def addPost(self, properties):
        return self.store.runOperation(q.add_post, properties)

    def getPost(self, id):
        d = self.store.runQuery(q.get_post, id)
        d.addCallback(_transformResult)
        return d
    
    def _addTopic(self, curs, query, args):
        curs.execute(query, args)
        ## XXX
        curs.execute("SELECT max(posts.id)")
        lid = curs.fetchone()
        return lid[0]
        
util.backwardsCompatImplements(TopicsDatabase)                 
