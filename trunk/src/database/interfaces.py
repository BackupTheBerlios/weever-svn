from nevow.compy import Interface

class IS(Interface):
    """ Store interface """

class IUsersDatabase(Interface):
    def findAllUsers(self):
        """ Returns all users in the database with a sequence of
        dicts.
        
        return = {'uid':id,
                  'uscreename':screename,
                  'ulogin':login,
                  'upassword':password,
                  'ugroup_id':gid,
                  'uemail':email,
                  'uhomepage':homepage,
                  'gdescription':gdesc,
                  'gpermissionlevel':gpermissions
                 }
        """
        
    def findUser(self, username):
        """ Returns the user with the corresponding username in a
            sequence of dicts which is the same returned from
            method findAllUsers
        """

    def getUsersWithStats(self):
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
        
    def getUserWithStats(self, username):
        """ Returns the user with all the posting stats in a sequence
        of dicts like getUsersWithStats method.
        """
    
    def addUser(self, properties):
        """ properties is a dict containing all the informations about the user """
    
    def delUser(self, username):
        """ Removes user with username 'username' """
    
    def updatePassword(self, username, newPassword, oldPassword):
        """ First verify oldPassword, then change it to newPassword, for user username """

class ISectionsDatabase(Interface):
    def getAllSections(self):
        """ Returns a list of all sections in a sequence of dicts
        build with these keys:

        return = {'sid':sid,
                  'stitle':stitle,
                  'sdesc':sdesc,
                  'thread_num':topics_num,
                  'lastmod':lastmod
                 }
        """

    def simpleGetAllSections(self):
        """ returns a list of sections' dicts with these keys:
            
            {'sid':sid,
             'stitle':stitle,
             'sdesc':sdesc
            }
        """
    
    def getSection(self, sid):
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
                  'posts_num':posts_num,
                 }
        """
    
    def addSection(self, properties):
        """ properties is a dict containing all the informations that deal with
        Section creation.
        """
        
    def delSection(self, sid):
        """ removes section 'sid' """
    
class ITopicsDatabase(Interface):
    def getAllPosts(self, tid, num, offset):
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
    def getTopTopics(self, num):
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
        
    def addTopic(self, properties):
        """ properties is a dict containing all informations to add a new topic """
    
    def allowTopicOnlyToPartecipants(self, properties):
        """ Use this option to let only users that already posted at least
        one message to see this topic """
    
    def removeTopic(self, tid):
        """ Is this really needed? """
    
    def addPost(self, properties):
        """ add a post to the posts database, properties contains all the right infos """
    
    def removePost(self, pid):
        """ is this really needed """
    
