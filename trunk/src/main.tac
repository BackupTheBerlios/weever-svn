from twisted.application import service, internet
from twisted.manhole import telnet

import warnings
import twisted.python.components
warnings.filterwarnings('ignore', '',
                        twisted.python.components.ComponentsDeprecationWarning)

from nevow import appserver, guard, inevow

from web import index
from config import general as c
from database import store
from database.interfaces import IS

application = service.Application('weever')

store = store.Store(c.database_adapter, c.database_name,
              c.database_user, c.database_password)

class RememberWrapper:
    __implements__ = inevow.IResource,

    def __init__(self, resource, remember):
        self.resource = resource
        self.remember = remember

    def locateChild(self, ctx, segments):
        for interface, adapter in self.remember:
            ctx.remember(adapter, interface)
        return self.resource, segments

    def renderHTTP(self, ctx):
        for interface, adapter in self.remember:
            ctx.remember(adapter, interface)
        return self.resource.renderHTTP(ctx)

portal = index.Main()
site = appserver.NevowSite (
            resource = RememberWrapper(portal, [(IS, store)])
            )
webservice = internet.TCPServer(8080, site, backlog=511)
webservice.setServiceParent(application)

sh = telnet.ShellFactory()
sh.setService(webservice)
shell = internet.TCPServer(8081, sh)
shell.setServiceParent(application)

# vim:filetype=python
