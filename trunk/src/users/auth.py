from twisted.internet import defer
from twisted.python import failure
from twisted.cred import portal
from twisted.cred import checkers
from twisted.cred import credentials
from twisted.cred import error

from nevow import inevow

from database import interfaces as idb #import IUsersDatabase, IS
from users import interfaces as iusers
from web import index



class SimpleChecker:
    """
    A simple checker implementation. Delegates storage/retrieval to userdb object
    """
    __implements__ = checkers.ICredentialsChecker
    credentialInterfaces = (credentials.IUsernamePassword,)

    def __init__(self, store):
        self.userdb = idb.IUsersDatabase(store)

    #implements ICredentialChecker
    def requestAvatarId(self, creds):
        """Return the avatar id of the avatar which can be accessed using
        the given credentials.

        credentials will be an object with username and password attributes
        we need to raise an error to indicate failure or return a username
        to indicate success. requestAvatar will then be called with the avatar
        id we returned.
        """
        d = self.userdb.findUser(creds.username)
        return d.addCallback(self.verify, creds)
    
    def verify(self, user, creds):
        if user is not None:
            return defer.maybeDeferred(
                creds.checkPassword, user['upassword']).addCallback(
                self._cbPasswordMatch, user)
        else:
            print "No user named: ",creds.username
            raise error.UnauthorizedLogin()

    def _cbPasswordMatch(self, matched, user):
        if matched:
            return user
        else:
            print "password didn't match: ",user['ulogin']
            return failure.Failure(error.UnauthorizedLogin())

class SimpleRealm:
    """A simple implementor of cred's IRealm.
    For web, this gives us the LoggedIn page.
    """
    __implements__ = portal.IRealm,

    def requestAvatar(self, avatarId, mind, *interfaces):
        for iface in interfaces:
            if iface is inevow.IResource:
                # do web stuff
                # usually I could check if avatarId is
                # checkers.ANONYMOUS, but I can skip this
                # time since I already use avatarId stored
                # in the session to parametrize page rendering
                resc = index.Main()
                if avatarId == ():
                    avatarId = {}
                resc.remember(avatarId, iusers.IA)
                resc.remember(mind, iusers.IMind)
                resc.remember(self, iusers.IRealm)
                
                #resc = main.RememberWrapper(mainPage, avatarId)
                return (inevow.IResource, resc, resc.logout)

        raise NotImplementedError("Can't support that interface.")
