from time import time as now

from zope.interface import implements

from nevow import rend, loaders, static, url
from nevow import inevow, tags as t

from web import interfaces as iweb
from database.interfaces import IS


class MasterPage(rend.Page):
    docFactory = loaders.xmlfile('templates/index.html')
    child_styles = static.File('styles/')
    child_images = static.File('images/')
    addSlash = True

    def __init__(self, data=None, ctnt=None):
        rend.Page.__init__(self)
        self.content = ctnt

        self.args = data

        if not self.content:
            from web.index import IndexContent
            self.content = IndexContent

    def locateChild(self, ctx, segments):        
        ctx.remember(IS(ctx), IS)
        
        ctx.remember(notFound, inevow.ICanHandleNotFound)
        #ctx.remember(Page500, inevow.ICanHandleException)

        # This is a redirect to root for style and design stuff
        # This must be kept as the first thing in locateChild
        # to avoid errors while rendering links with final slashes
        for special_dir in 'styles images'.split():
            if special_dir in segments:
                segments = segments[list(segments).index(special_dir):]

        if len(segments) >= 2:
            pag = segments[0]
            pivot = segments[1]
            if pivot.isdigit():
                page = getattr(self, "child_"+pag, None)
                if page:
                    return page(ctx, segments[1:]), ()

        return rend.Page.locateChild(self, ctx, segments)

    def data_head(self, ctx, data):
        return [{'ttitle':'Weever'}]

    def render_title(self, ctx, data):
        for item in data: 
            if not item.get("ttitle").endswith('Weever'):
                return ctx.tag.clear()[data[0].get("ttitle") + '  --  Weever']
            else:
                return ctx.tag.clear()[data[0].get("ttitle")]
            break
        
    def render_startTimer(self, ctx, data):
        ctx.remember(now(), iweb.ITimer)
        return ctx.tag

    def render_stopTimer(self, ctx, data):
        startTime = iweb.ITimer(ctx)
        return ctx.tag["%.0f" % ((now()-startTime)*1000,)]

    def render_content(self, ctx, data):
        if data != 'Weever':
            ctx.fillSlots('content', self.content(self.args, data[0]))
        else:
            ctx.fillSlots('content', self.content(self.args))
        return ctx.tag


class BaseContent(rend.Fragment):
    def __init__(self, args, data=None):
        rend.Fragment.__init__(self)
        self.args = args
        self.data = data

class Page404(rend.Page):
    implements(inevow.ICanHandleNotFound,)
    docFactory = loaders.xmlfile('templates/404.html')

    def __init__(self):
        rend.Page.__init__(self)

    def renderHTTP_notFound(self, ctx):
        inevow.IRequest(ctx).setResponseCode(404)
        return self.renderHTTP(ctx)

    def render_startTimer(self, ctx, data):
        ctx.remember(now(), iweb.ITimer)
        return ctx.tag

    def render_stopTimer(self, ctx, data):
        startTime = iweb.ITimer(ctx)
        return ctx.tag["%.0f" % ((now()-startTime)*1000,)]

    def locateChild(self, ctx, segments):
        for special_dir in 'styles images'.split():
            if special_dir in segments:
                segments = segments[list(segments).index(special_dir):]
        return rend.Page.locateChild(self, ctx, segments)

    def render_lastLink(self, ctx, data):
        referer = inevow.IRequest(ctx).getHeader('referer')
        if referer:
            return ctx.tag[t.a(href=referer)['Back']]
        else:
            return ctx.tag[t.a(href=url.root)['To Main Page']]

notFound = Page404()
