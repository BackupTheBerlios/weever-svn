from nevow.compy import newImplements as implements

from database.interfaces import IUsersDatabase, ISectionsDatabase, ITopicsDatabase

import queries as q

class UsersDatabase(object):
    
    implements(IUsersDatabase)

    def __init__(self, db):
        self.store = db

    def _transformResult(self, result):
        print '#',result
        if result:
            return result[0]
        else:
            return None

    def findUser(self, username):
        d = self.store.runQuery(q.user, dict(ulogin=username))
        d.addCallback(self._transformResult)
        return d
    
    def findAllUsers(self):
        return self.store.runQuery(q.all_users)

    def getUserWithStats(self, username):
        return self.store.runQuery(q.user_stats, dict(ulogin=username))

    def getUsersWithStats(self):
        return self.store.runQuery(q.all_users_stats)

    def addUser(self, properties):
        return self.store.runOperation(q.add_user, properties)

class SectionsDatabase(object):

    implements(ISectionsDatabase)

    def __init__(self, db):
        self.store = db

    def getAllSections(self):
        return self.store.runQuery(q.all_sections)

    def getSection(self, sid):
        return self.store.runQuery(q.section, dict(sid=sid))

class TopicsDatabase(object):

    implements(ITopicsDatabase)

    def __init__(self, db):
        self.store = db

    def getAllPosts(self, tid, num, offset):
        return self.store.runQuery(q.topic, dict(tid=tid, num=num, offset=offset))

    def getPostsNum(self, tid):
        return self.store.runQuery(q.posts_num, dict(tid=tid))

    def getTopTopics(self, num):
        return self.store.runQuery(q.top_threads, dict(num=num))

    def addTopic(self, args1, args2):        
        return self.store.runInteraction(self._addTopic, \
                                         queries=(q.add_topic,q.add_post),
                                         args=(args1, args2)
                                         )

    def addPost(self, properties):
        return self.store.runOperation(q.add_post, properties)

    def _addTopic(self, curs, queries, args):
        add_topic = queries[0]
        add_post = queries[1]
        topic_args = args[0]
        post_args = args[1]
        def _add(result):
            post_args['thread_id'] = result[0]
            curs.execute(add_post, post_args)
            return result[0]
        d = util.maybeDeferred(curs.execute, add_topic, topic_args)
        d.addCallback(lambda _: curs.execute("SELECT MAX(t.id) FROM thread t"))
        d.addCallback(lambda _: curs.fetchone)
        d.addCallback(_add)
        return d
    
    #def _addTopic(self, curs, queries, args):
        #add_topic = queries[0]
        #add_post = queries[1]
        #topic_args = args[0]
        #post_args = args[1]
        #curs.execute(add_topic, topic_args)
        #curs.execute("SELECT MAX(t.id) FROM thread t")
        #lid = curs.fetchone()
        #post_args['thread_id'] = lid[0]
        #curs.execute(add_post, post_args)
        #return lid[0]
        
                 
