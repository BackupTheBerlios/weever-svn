from twisted.application import service, strports, internet
from twisted.manhole import telnet
from twisted.cred import portal
from twisted.cred import checkers
from twisted.cred import credentials
from twisted.python import util, log, reflect

import warnings
import twisted.python.components
warnings.filterwarnings('ignore', '',
                        twisted.python.components.ComponentsDeprecationWarning)

from nevow import appserver
from users import auth, guard
from config import parser as cfgFile
#
# Don't touch anything above this line
#

#You may provide different filenames under config/ directory
#or directly modify those files.
DATABASE_CFG='weever.ini'
NETWORK_CFG='weever.ini'
REMOTE_CFG='weever.ini'

dbms, adapter, dsn = cfgFile.getDatabaseParameters(DATABASE_CFG)
netString = cfgFile.getNetworkParameters(NETWORK_CFG)
remoteEnabled, remoteShellP = cfgFile.getRemoteShParameters(REMOTE_CFG)

#
# Don't touch anything below this line
#
log.msg(dbms)
log.msg(adapter)
log.msg(dsn)
log.msg(netString)
log.msg(remoteEnabled)
log.msg(remoteShellP)
application = service.Application('weever')
store_module = reflect.namedAny('database.'+dbms+'.store')
store = store_module.Store(adapter, dsn)
log.msg("Database initialization succeeded")
realm = auth.SimpleRealm(store)
portal = portal.Portal(realm)
myChecker = auth.SimpleChecker(store)
portal.registerChecker(checkers.AllowAnonymousAccess(), credentials.IAnonymous)
portal.registerChecker(myChecker)
log.msg("Auth Layer initialization succeeded")
site = appserver.NevowSite (
            resource = guard.SessionWrapper(portal)
            )
log.msg("Site initialization succeeded")
webservice = strports.service(netString, site)
webservice.setServiceParent(application)
log.msg("Server initialization succeeded")
if remoteEnabled:
    sh = telnet.ShellFactory()
    sh.setService(webservice)
    shell = internet.TCPServer(remoteShellP, sh)
    shell.setServiceParent(application)
    log.msg("Remote Shell initialization succeeded")
# vim:filetype=python
