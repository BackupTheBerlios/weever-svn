from twisted.application import service, internet
from twisted.manhole import telnet
from twisted.cred import portal
from twisted.cred import checkers
from twisted.cred import credentials


import warnings
import twisted.python.components
warnings.filterwarnings('ignore', '',
                        twisted.python.components.ComponentsDeprecationWarning)

from nevow import appserver, guard, inevow

from web import index, main
from users import auth
from config import general as c
from database import store
from database.interfaces import IS

application = service.Application('weever')

store = store.Store(c.database_adapter, c.database_name,
              c.database_user, c.database_password)



realm = auth.SimpleRealm(store)
portal = portal.Portal(realm)
myChecker = auth.SimpleChecker(store)
portal.registerChecker(checkers.AllowAnonymousAccess(), credentials.IAnonymous)
portal.registerChecker(myChecker)

site = appserver.NevowSite (
            resource = guard.SessionWrapper(portal)
            )

webservice = internet.TCPServer(8080, site, backlog=511)
webservice.setServiceParent(application)

sh = telnet.ShellFactory()
sh.setService(webservice)
shell = internet.TCPServer(8081, sh)
shell.setServiceParent(application)

# vim:filetype=python
