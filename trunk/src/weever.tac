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

from nevow import appserver, guard, liveevil
liveevil.debug = True

from users import auth
from config import parser as cfgFile
#
# Don't touch anything above this line
#

#You may provide different filenames under files/ directory
#or directly modify those files.
DATABASE_CFG='weever.ini'
NETWORK_CFG='weever.ini'
REMOTE_CFG='weever.ini'

dbms, adapter, dsn_params = cfgFile.getDatabaseParameters(DATABASE_CFG)
netString = cfgFile.getNetworkParameters(NETWORK_CFG)
remoteEnabled, remoteShellP = cfgFile.getRemoteShParameters(REMOTE_CFG)

#
# Don't touch anything below this line
#
log.msg("DBMS: %s" % dbms)
log.msg("Database adapter: %s" % adapter)
log.msg("DSN params: %s" % dsn_params)
log.msg("Net setup string: %s" % netString)
log.msg("Remote shell enabled: %s" % (remoteEnabled != '0'))
log.msg("Remote shell port: %s" % remoteShellP)
from time import time as now
application = service.Application('weever')
t0 = now()
store_module = reflect.namedAny('database.'+dbms+'.store')
store = store_module.Store(adapter, dsn_params)
log.msg("Database initialization succeeded in %.2f" % (now()-t0))
t = now()
realm = auth.SimpleRealm(store)
portal = portal.Portal(realm)
myChecker = auth.SimpleChecker(store)
portal.registerChecker(checkers.AllowAnonymousAccess(), credentials.IAnonymous)
portal.registerChecker(myChecker)
log.msg("Auth Layer initialization succeeded in %.2f" % (now()-t))
t = now()
site = appserver.NevowSite (
        resource = guard.SessionWrapper(portal, mindFactory=liveevil.LiveEvil)
            )
log.msg("Site initialization succeeded in %.2f" % (now()-t))
t = now()
webservice = strports.service(netString, site)
webservice.setServiceParent(application)
log.msg("Server initialization succeeded in %.2f" % (now()-t))
t = now()
if remoteEnabled:
    sh = telnet.ShellFactory()
    sh.setService(webservice)
    shell = internet.TCPServer(remoteShellP, sh)
    shell.setServiceParent(application)
    log.msg("Remote Shell initialization succeeded %.2f" % (now()-t))
log.msg("Weever Successfully initialized in %.2f" % (now()-t0))
# vim:filetype=python
