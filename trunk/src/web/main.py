from time import time as now
import os.path as op

from zope.interface import implements

from nevow import rend, loaders, static, url
from nevow import inevow, tags as t

from web import interfaces as iweb, template_path as tp
from web import images_path as ip, styles_path as sp
from database.interfaces import IS
from users.interfaces import IA

FIRST_POST,_ = range(2)

class RememberWrapper:
    __implements__ = inevow.IResource,

    def __init__(self, resource, remember, avatarId=None):
        self.resource = resource
        self.remember = remember
        self.avatarId = avatarId

    def beforeRender(self, ctx):
        inevow.ISession(ctx).setComponent(IA, self.avatarId)

    def locateChild(self, ctx, segments):
        for interface, adapter in self.remember:
            ctx.remember(adapter, interface)
        return self.resource, segments

    def renderHTTP(self, ctx):
        for interface, adapter in self.remember:
            ctx.remember(adapter, interface)
        return self.resource.renderHTTP(ctx)
    

class MasterPage(rend.Page):
    docFactory = loaders.xmlfile(op.join(tp, 'index.html'))
    child_styles = static.File(sp)
    child_images = static.File(ip)
    addSlash = True
    

    def __init__(self, data=[], ctnt=None):
        rend.Page.__init__(self)
        self.content = ctnt

        self.args = []
        if data:
            self.args.extend(data)

        if not self.content:
            from web.index import IndexContent
            self.content = IndexContent

    def beforeRender(self, ctx): 
        ctx.remember(IS(ctx), IS)

    def locateChild(self, ctx, segments):
        ctx.remember(Page404(), inevow.ICanHandleNotFound)
        return rend.Page.locateChild(self, ctx, segments)

    def data_head(self, ctx, data):
        return [{'ttitle':'Weever'}]

    def render_title(self, ctx, data):
        for item in data: 
            if not item.get("ttitle").endswith('Weever'):
                return ctx.tag.clear()[item.get("ttitle") + '  --  Weever']
            else:
                return ctx.tag.clear()[item.get("ttitle")]
            break
        
    def render_startTimer(self, ctx, data):
        ctx.remember(now(), iweb.ITimer)
        return ctx.tag

    def render_stopTimer(self, ctx, data):
        startTime = iweb.ITimer(ctx)
        return ctx.tag["%.0f" % ((now()-startTime)*1000,)]

    def render_content(self, ctx, data):
        ctx.tag.fillSlots('content', self.content(self.args, data[FIRST_POST]))
        return ctx.tag


class BaseContent(rend.Fragment):
    def __init__(self, args=[], data=None):
        rend.Fragment.__init__(self)
        self.args = args
        self.data = data

class Page404(rend.Page):
    implements(inevow.ICanHandleNotFound,)
    docFactory = loaders.xmlfile(op.join(tp, '404.html'))

    def renderHTTP_notFound(self, ctx):
        inevow.IRequest(ctx).setResponseCode(404)
        return self.renderHTTP(ctx)

    def render_startTimer(self, ctx, data):
        ctx.remember(now(), iweb.ITimer)
        return ctx.tag

    def render_stopTimer(self, ctx, data):
        startTime = iweb.ITimer(ctx)
        return ctx.tag["%.0f" % ((now()-startTime)*1000,)]

    def render_lastLink(self, ctx, data):
        referer = inevow.IRequest(ctx).getHeader('referer')
        if referer:
            return ctx.tag[t.a(href=referer)['Back']]
        else:
            return ctx.tag[t.a(href=url.root)['To Main Page']]
