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

    def addTopic(self, args1, args2):        
        return self.store.runInteraction(self._addTopic, \
                                         queries=(q.add_topic,q.add_post),
                                         args=(args1, args2)
                                         )
    addTopic = cleanCache(getTopTopics)(addTopic)

    def addPost(self, properties):
        return self.store.runOperation(q.add_post, properties)

    def getPost(self, id):
        d = self.store.runQuery(q.get_post, id)
        d.addCallback(_transformResult)
        return d
    
    def _addTopic(self, curs, queries, args):
        add_topic = queries[0]
        add_post = queries[1]
        topic_args = args[0]
        post_args = args[1]
        curs.execute(add_topic, topic_args)
        curs.execute("SELECT MAX(t.id) FROM thread t")
        lid = curs.fetchone()
        post_args['thread_id'] = lid[0]
        curs.execute(add_post, post_args)
        return lid[0]
        
util.backwardsCompatImplements(TopicsDatabase)                 
