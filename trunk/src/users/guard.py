import md5
import random
import time

from twisted.application import service
from twisted.cred import credentials
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import reactor, task
from twisted.python import components, log
from twisted.web import util

from nevow import compy
from nevow import inevow


# TODO:
#
# * Message on login failure.
# * Remove hard-coded root url on logout and cookie path (see guard)
# * Support cookie-less mode (not much point unless we have a way to
#   encode URLs).
# * Add a session manager service that can be persisted.
# * Install a session factory on the request
# * General compatability with "real" guard
#
# * http auth
# * cookie path (i.e. url.root, not '/')
#
# * provide a way to store the sessions on a database, proposed
#   architecture:
#   - write an ISessionContainer that acts like self.sessions dict
#    but knows how to expire its content to avoid calling:
#    self.sessions[sessionID].expire() but rather:
#    ISessionContainer(self.sessions).expire(sessionID)
#   - discuss about this stuff with other people

# TEST:
# * mind support

## My idea for a useful session interface:
##
## class ISession(Interface):
##     def notifyOnExpire(self, callback):
##         """Install a callback that will be called when the session
##         expires.
##         """
##     def expire(self):
##         """Expire the session.
##         """
##     def encodeURL(self, url):
##         pass


class ISessionManager(compy.Interface):
    """Session manager interface.

    A session manager is responsible for creating new sessions and
    locating existing sessions by session ID. A session manager should
    also manage the lifetime of sessions, removing any sessions that
    have expired.
    """

    def createSession(self):
        """Create a new session.
        """

    def getSession(self, uid):
        """Locate the session by session ID and .touch() the session.
        """

class IMind(compy.Interface):
    """Mind interface.

    Used to retrieve and to set the mind in the session
    """

#SESSION_KEY = '__session_key__'
LOGIN_AVATAR = '__login__'
LOGOUT_AVATAR = '__logout__'


class Session(compy.Componentized):
    """I represent a user's session with the application.

    Session is componentized to avoid setting attributes directly on
    the session object (you have no way of knowing what attributes
    other parts of the application are setting).

    Attributes:

        uid: session id
        creationTime: time (GMT) the session was created
        lastAccessed: time (GMT) of last access
    """

    __implements__ = inevow.ISession,
    
    def __init__(self, uid):
        compy.Componentized.__init__(self)
        self.uid = uid
        self.creationTime = self.lastAccessed = time.gmtime()
        self.expireCallbacks = []

    def touch(self):
        self.lastAccessed = time.gmtime()

    def notifyOnExpire(self, callback):
        self.expireCallbacks.append(callback)
    
    def expire(self):
        for callback in self.expireCallbacks:
            callback()
        del self.expireCallbacks[:]
        # Need to tell my session manager too

    def encodeURL(self, url):
        raise NotImplementedError()


class SessionManagerService(service.Service):
    """I have this idea that by wrapping a session manager in a
    service that sessions can be persisted across restarts. Haven't
    tried it yet though.
    """

    def __init__(self, sessionManager):
        self.sessionManager = sessionManager


class SessionManager:

    __implements__ = ISessionManager

    tickTime = 60.0
    sessionLifetime = 900.0

    def __init__(self):
        self.sessions = {}
        self.tick = task.LoopingCall(self._tick)

    def createSession(self):

        session = Session(self.createSessionID())
        self.sessions[session.uid] = session
        log.msg('Session %r created' % session.uid)

        if len(self.sessions) == 1:
            self.tick.start(self.tickTime)

        return session

    def getSession(self, uid):
        session = self.sessions.get(uid)
        if session:
            session.touch()
        return session

    def createSessionID(self):
        """Generate a new session ID.
        """
        data = "%s_%s" % (str(random.random()) , str(time.time()))
        return md5.new(data).hexdigest()

    def _tick(self):
        """Remove expired sessions.
        """

        now = time.mktime(time.gmtime())

        for sessionID, session in self.sessions.items():
            age = now - time.mktime(session.lastAccessed)
            if age > self.sessionLifetime:
                log.msg('Session %r expired' % sessionID)
                self.sessions[sessionID].expire()
                del self.sessions[sessionID]
                
        if not self.sessions:
            self.tick.stop()


_defaultSessionManager = SessionManager()


class IPortalRecorder(compy.Interface):
    """A component of a Session used to record portals that are
    connected to the session.

    Attributes:
        portals - dictionary of portal, portal detail pairs
    """

class PortalRecorder(compy.Adapter):

    __implements__ = IPortalRecorder,

    def __init__(self, *args):
        compy.Adapter.__init__(self, *args)
        self.portals = {}


compy.registerAdapter(PortalRecorder, Session, IPortalRecorder)

def nomind(*args): return None

class SessionWrapper:
    """I provide session-based authentication for web aspects of an
    application.
    """
    
    __implements__ = inevow.IResource

    sessionCookieName = 'nevow_session'
    sessionManager = _defaultSessionManager

    def __init__(self, portal, sessionCookieName=None, sessionManager=None, mindFactory=None):
        self.portal = portal
        if sessionCookieName is not None:
            self.sessionCookieName = sessionCookieName
        if sessionManager is not None:
            self.sessionManager = sessionManager
        if not mindFactory:
            mindFactory = nomind
        self.mindFactory = mindFactory

    def getSessionID(self, ctx):
        """Find the session key.
        """
        request = inevow.IRequest(ctx)
        return request.getCookie(self.sessionCookieName)
        
    def getSession(self, ctx, createIfNone=False):
        """Get the session for this user. If createIfNone is True then
        a new session will be created if an existing session cannot be
        found.
        """
        request = inevow.IRequest(ctx)
        session = self.sessionManager.getSession(self.getSessionID(ctx))
        if session is None and createIfNone:
            session = self.sessionManager.createSession()
            request.addCookie(self.sessionCookieName, session.uid, path='/')
        return session    

    def locateChild(self, ctx, segments):
        """Locate a child for the request and user.
        """

        request = inevow.IRequest(ctx)
        request.site.makeSession = lambda: self.getSession(ctx, True)

        # Try to find the session
        session = self.getSession(ctx)
        
        # Logout attempt
        if segments[-1] == LOGOUT_AVATAR:
            return self.logout(ctx, segments, session)

        # Login attempt
        if segments[0] == LOGIN_AVATAR:
            return self.login(ctx, segments[1:])

        # There is no session
        if not session:
            return self.requestAuthentication(ctx, segments)
        
        # This portal is not connected with the session
        if self.portal not in IPortalRecorder(session).portals:
            return self.requestAuthentication(ctx, segments)

        # The user seems to be connected to the portal so we should be
        # able to ask for the resource.
        return self.locateResource(ctx, segments, session)

    def requestAuthentication(self, ctx, segments):
        """Initiate authentication, used when there is no
        authenticated user.
        """

        def success(avatar, ctx, segments):
            iface, resource, logout = avatar
            return resource, segments

        creds = credentials.Anonymous()
        session = inevow.ISession(ctx)
        mind = IMind(session, None)
        if not mind:
            mind = self.mindFactory(inevow.IRequest(ctx), creds)
            session.setComponent(IMind, mind)
        
        d = self.portal.login(
            creds,
            mind,
            inevow.IResource
            )
        d.addCallback(success, ctx, segments)
        
        return d

    def login(self, ctx, segments):
        """Handle a login request.
        """

        def success(avatar, ctx, segments, creds):

            iface, resource, logout = avatar

            # Record the credentials and portal details
            session = self.getSession(ctx, True)
            session.addComponent(creds, ignoreClass=True)
            IPortalRecorder(session).portals[self.portal] = logout
            session.notifyOnExpire(lambda: self.logoutPortal(session))
            referrer = inevow.IRequest(ctx).getHeader('referer')

            ##
            ## FIX THIS STUFF
            ##
            print segments
            
            if segments != () and segments != ('',): to = '/'.join(segments)
            elif segments == ('',) or segments == (): to = '/'
            elif referrer: to = referrer
            else: to = '/'
            print "@@@@", to
            return util.Redirect(to), ()

        def failure(error, ctx, segment):
            error.trap(UnauthorizedLogin)
            error.printTraceback()
            return util.Redirect(inevow.IRequest(ctx).getHeader('referer') or '/'), ()
            
        request = inevow.IRequest(ctx)
        username = request.args.get('username', [''])[0]
        password = request.args.get('password', [''])[0]
        creds = credentials.UsernamePassword(username, password)
       
        session = inevow.ISession(ctx)
        mind = IMind(session, None)
        if not mind:
            mind = self.mindFactory(inevow.IRequest(ctx), creds)
            session.setComponent(IMind, mind)
        
        log.msg(
            'User %r attempting login to %r' % (username, self.portal)
            )
        
        d = self.portal.login(creds, mind, inevow.IResource)
        d.addCallback(success, ctx, segments, creds)
        d.addErrback(failure, ctx, segments)
        
        return d

    def locateResource(self, ctx, segments, session):
        """Locate the resource for an authenticated session.
        """

        def success(avatar, ctx, segments):
            iface, resource, logout = avatar
            return resource, segments

        # This shouldn't happen if we have an already existing
        # resource we should instead gather the resource from the
        # portal or from whatever we stored it in

        session = inevow.ISession(ctx)        
        creds = session.getComponent(credentials.IUsernamePassword)

        mind = IMind(session, None)
        if not mind:
            mind = self.mindFactory(inevow.IRequest(ctx), creds)
            session.setComponent(IMind, mind)

        d = self.portal.login(creds, mind, inevow.IResource)
        d.addCallback(success, ctx, segments)
        return d

    def logout(self, ctx, segments, session):
        if session:
            self.logoutPortal(session)
        return util.Redirect('/'), ()

    def logoutPortal(self, session):
        pr = IPortalRecorder(session)
        if self.portal in pr.portals:
            logout = pr.portals[self.portal]
            logout()
            del pr.portals[self.portal]
        log.msg('Logout of portal %r'%self.portal)
