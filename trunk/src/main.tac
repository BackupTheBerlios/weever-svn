import ConfigParser as cp
import os

from twisted.application import service, internet
from twisted.manhole import telnet
from twisted.cred import portal
from twisted.cred import checkers
from twisted.cred import credentials
from twisted.python import util, log


import warnings
import twisted.python.components
warnings.filterwarnings('ignore', '',
                        twisted.python.components.ComponentsDeprecationWarning)


from nevow import appserver
from web import index, main
from users import auth, guard
from database import store
from database.interfaces import IS


parser = cp.ConfigParser()
config_file = os.path.join(util.sibpath(__file__,'config'),'general.ini')
log.msg(config_file)
parser.read(config_file)

adapter = parser.get('Database', 'adapter')

dsn = ''
for entry in 'dbname user password host port'.split():
    if parser.has_option('Database', entry):
        el = parser.get('Database', entry)
        dsn = '%s %s=%s' % (dsn, entry, el)

application = service.Application('weever')

store = store.Store(adapter, dsn)

realm = auth.SimpleRealm(store)
portal = portal.Portal(realm)
myChecker = auth.SimpleChecker(store)
portal.registerChecker(checkers.AllowAnonymousAccess(), credentials.IAnonymous)
portal.registerChecker(myChecker)

mainPage = index.Main()
site = appserver.NevowSite (
            resource = guard.SessionWrapper(portal)
#            resource = main.RememberWrapper(mainPage, [(IS, store)])
            )

webservice = internet.TCPServer(8080, site, backlog=511)
webservice.setServiceParent(application)

sh = telnet.ShellFactory()
sh.setService(webservice)
shell = internet.TCPServer(8081, sh)
shell.setServiceParent(application)

# vim:filetype=python
