from zope.interface import Interface
from nevow.compy import Interface as InterfaceN

class IS(InterfaceN):
    """ Store interface """

class IUsersDatabase(Interface):
    def findAllUsers():
        """ Returns all users in the database with a sequence of
        dicts.
        
        return = {'id':id,
                  'name':name,
                  'surname':surname,
                  'login':login,
                  'password':password,
                  'gid':gid,
                  'email':email,
                  'homepage':homepage,
                  'gdesc':gdesc,
                  'gpermissions':gpermissions
                 }
        """
        
    def findUser(username):
        """ Returns the user with the corresponding username in a
            sequence of dicts which is the same returned from
            method findAllUsers
        """

    def getUsersWithStats():
        """ Returns all the users with all the posting stats in a dict
        like the one from findAllUsers but with a total_posts key
        added.

        return = {'id':id,
                  'name':name,
                  'surname':surname,
                  'login':login,
                  'password':password,
                  'gid':gid,
                  'email':email,
                  'homepage':homepage,
                  'gdesc':gdesc,
                  'gpermissions':gpermissions
                  'total_posts':total_posts
                 }
        """
        
    def getUserWithStats(username):
        """ Returns the user with all the posting stats in a sequence
        of dicts like getUsersWithStats method.
        """

class ISectionsDatabase(Interface):
    def getAllSections():
        """ Returns a list of all sections in a sequence of dicts
        build with these keys:

        return = {'sid':sid,
                  'stitle':stitle,
                  'sdesc':sdesc,
                  'topics_num':topics_num,
                 }
        """
    def getSection(sid):
        """ Returns the topics in the section number sid in a sequence
        of dicts, ordered by modification date:

        return = {'sid':sid,
                  'stitle':stitle,
                  'sdesc':sdesc,
                  'tid':tid,
                  'ttitle':ttitle,
                  'towner':towner,
                  'tnoise':tnoise,
                  'tcreation':tcreation,
                  'tmodification':tmodification,
                  'posts_num':posts_num,
                 }
        """

class ITopicsDatabase(Interface):
    def getAllPosts(tid, num, offset):
        """ Returns all posts ordered by post_id, inside the current
        thread numbered tid, as usual, in a sequence of dicts:

        return = {'ttitle':ttitle,
                  'tcreation':tcreation,
                  'tmodification':tmodification,
                  'pid':pid,
                  'ptid':ptid,
                  'powner':powner,
                  'pcreation':pcreation,
                  'pmodification':pmodification,
                  'pnoise':pnoise,
                  'pbody':pbody
                 }        
        """
    def getTopTopics(num):
        """ Returns all posts ordered by modification, inside the 
        database in a sequence of dicts:

        return = {'sid':sid,
                  'stitle':stitle,
                  'sdesc':sdesc,
                  'tid':tid,
                  'ttitle':ttitle,
                  'towner':towner,
                  'tnoise':tnoise,
                  'tcreation':tcreation,
                  'tmodification':tmodification,
                  'posts_num':posts_num,
                 }

        """
        
