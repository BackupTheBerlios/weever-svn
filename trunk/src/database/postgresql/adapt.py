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
        d = self.store.runQuery(q.user, username)
        d.addCallback(self._transformResult)
        return d
    
    def findAllUsers(self):
        return self.store.runQuery(q.all_users)

    def getUserWithStats(self, username):
        return self.store.runQuery(q.user_stats, username)

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
        return self.store.runQuery(q.section, sid)

class TopicsDatabase(object):

    implements(ITopicsDatabase)

    def __init__(self, db):
        self.store = db

    def getAllPosts(self, tid, num, offset):
        return self.store.runQuery(q.topic, tid, num, offset)

    def getPostsNum(self, tid):
        return self.store.runQuery(q.posts_num, tid)

    def getTopTopics(self, num):
        return self.store.runQuery(q.top_threads, num)

    def addTopic(self, properties):        
        return self.store.runOperation(q.add_topic, properties)

    def addPost(self, properties):
        return self.store.runOperation(q.add_post, properties)
