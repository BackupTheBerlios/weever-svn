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

def reorderThread(thread):
    try:
        first = thread[0]
    except IndexError:
        return thread
    else:
        first_indent = len(first.get('preferences_').split('.'))-1
        for post in thread:
            indent = len(post.get('preferences_').split('.'))-1
            indent_level = indent - first_indent
            if indent_level < 0:
                indent_level = 0
            post['indent_level'] = indent_level
        return thread

##     r = [[x.get('preferences_') or '{}', x] for x in thread]
##     #t = [x[1] for x in r]
##     # Get a list of ints from a string
##     for el in r:
##         tmp = []
##         for x in el[0][1:-1].split(','):
##             if x:
##                 tmp.append(int(x))
##         el[0] = tmp

##     tree = []
##     r.sort()
##     base = len(r[0][0])
##     for idx, node in enumerate(r):
##         appended = 0
##         if idx == 0:
##             tree.append(node)
##             node[1]['indent_level'] = 0
##             appended = 1
##         else:
##             if len(node[0]) == base:
##                 tree.append(node)
##                 node[1]['indent_level'] = 0
##                 appended = 1
##             else:
##                 for i, t in enumerate(tree):
##                     if t[0] == node[0][:-1]:
##                         if t[1].get('pid') == node[0][-1]:
##                             tree.insert(i+1, node)
##                             node[1]['indent_level'] = len(t[0])+1-base
##                             appended = 1
##                             break
##         if not appended:
##             tree.append(node)
##             node[1]['indent_level'] = 0
##     return [x[1] for x in tree]

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
        return self.store.runQuery(q.topic, tid, num, offset
                                   ).addCallback(reorderThread)

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
