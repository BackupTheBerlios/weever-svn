from time import time as now

from zope.interface import implements

from nevow import rend, loaders, static, url, util, compy
from nevow.rend import _CARRYOVER
from nevow import inevow, tags as t
from formless import iformless

from web import interfaces as iweb, getTemplate
from web import getStyles, getImages, WebException
from database.interfaces import IS
from users.interfaces import IA
from users import guard

FIRST_POST = 0
SUBMIT = '_submit'
BUTTON = 'post_btn'

class RememberWrapper:
    __implements__ = inevow.IResource,

    def __init__(self, resource, remember, avatarId={}):
        self.resource = resource
        self.remember = remember
        if avatarId == ():
            self.avatarId = {}
        else: self.avatarId = avatarId

    def locateChild(self, ctx, segments):
        inevow.ISession(ctx).setComponent(IA, self.avatarId)
        for interface, adapter in self.remember:
            ctx.remember(adapter, interface)
        return self.resource, segments

    def renderHTTP(self, ctx):
        for interface, adapter in self.remember:
            ctx.remember(adapter, interface)
        return self.resource.renderHTTP(ctx)
    
class ManualFormMixin(rend.Page):
    def locateChild(self, ctx, segments):
        # Handle the form post
        if segments[0].startswith(SUBMIT):
            # Get a method name from the action in the form plus
            # the firt word in the button name (or simply the form action if
            # no button name is specified
            kwargs = {}
            args = inevow.IRequest(ctx).args
            bindingName = ''
            for key in args:
                if key != BUTTON: 
                    if args[key] != ['']: 
                        kwargs[key] = (args[key][0], args[key])[len(args[key])>1]
                else: 
                    bindingName = args[key][0]
            name_prefix = segments[0].split('!!')[1]
            if bindingName == '': name = name_prefix
            else: name = name_prefix + '_' + bindingName.split()[0].lower()
            method = getattr(self, 'form_'+name, None)            
            if method is not None:
                return self.onManualPost(ctx, method, bindingName, kwargs)
            else: 
                raise WebException("You should define a form_action_button method")
        return super(ManualFormMixin, self).locateChild(ctx, segments)    

class MasterPage(ManualFormMixin, rend.Page):
    docFactory = loaders.xmlfile(getTemplate('index.html'))
    child_styles = static.File(getStyles())
    child_images = static.File(getImages())
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
        ctx.remember(IA(inevow.ISession(ctx)), IA)

    def locateChild(self, ctx, segments):
        ctx.remember(Page404(), inevow.ICanHandleNotFound)
        return super(MasterPage, self).locateChild(ctx, segments)
    
    def onManualPost(self, ctx, method, bindingName, kwargs):
        # This is copied from rend.Page.onWebFormPost
        def redirectAfterPost(aspects):
            redirectAfterPost = request.getComponent(iformless.IRedirectAfterPost, None)
            if redirectAfterPost is None:
                ref = request.getHeader('referer') or ''
            else:
                ## Use the redirectAfterPost url
                ref = str(redirectAfterPost)
            from nevow import url
            refpath = url.URL.fromString(ref)
            magicCookie = str(now())
            refpath = refpath.replace('_nevow_carryover_', magicCookie)
            _CARRYOVER[magicCookie] = C = compy.Componentized(aspects)
            request.redirect(str(refpath))
            from nevow import static
            return static.Data('You posted a form to %s' % bindingName, 'text/plain'), ()
        request = inevow.IRequest(ctx)
        return util.maybeDeferred(method, **kwargs
            ).addCallback(self.onPostSuccess, request, ctx, bindingName,redirectAfterPost
            ).addErrback(self.onPostFailure, request, ctx, bindingName,redirectAfterPost)

    def data_head(self, ctx, data):
        return [{'ttitle':'Weever'}]

    def render_title(self, ctx, data):
        for item in data: 
            if not item.get("ttitle").endswith('Weever'):
                return ctx.tag.clear()[item.get("ttitle") + '  --  Weever']
            else:
                return ctx.tag.clear()[item.get("ttitle")]
            break

    def render_welcome(self, ctx, data):
        user = IA(ctx).get('ulogin', None)
        if user:
            ctx.tag.fillSlots('status', 'Logout (%s)' % (user,))
            ctx.tag.fillSlots('link', url.here.child(guard.LOGOUT_AVATAR))
        else:
            ctx.tag.fillSlots('status', 'Login')
            ctx.tag.fillSlots('link', url.root.child('login'))
        return ctx.tag
        
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
    docFactory = loaders.xmlfile(getTemplate('404.html'))

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
