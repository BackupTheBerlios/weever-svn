from time import time as now

from nevow import rend, loaders, static, url, util, compy, guard, liveevil
from nevow.rend import _CARRYOVER
from nevow import inevow, tags as t

from web import interfaces as iweb, getTemplate
from web import getTheme, WebException
from users import interfaces as iusers #import IA

FIRST_POST = 0
SUBMIT = '_submit'
BUTTON = 'post_btn'

def render_isLogged(self, ctx, data):
    true_pattern = inevow.IQ(ctx).onePattern('True')
    false_pattern = inevow.IQ(ctx).onePattern('False')
    if iusers.IA(ctx).get('uid'): return true_pattern or ctx.tag().clear()
    else: return false_pattern or ctx.tag().clear()

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
    child_theme = static.File(getTheme())
    child_glue = liveevil.glueJS
    addSlash = True
    buffered = True
    content = None

    def __init__(self, data=[]):
        super(MasterPage, self).__init__()

        self.args = []
        if data:
            self.args.extend(data)

    def logout(self):
        return None
        
    render_isLogged = render_isLogged
    
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
            title = item.get("ttitle", None) or item.get("stitle", None)
            if not title.endswith('Weever'):
                return ctx.tag.clear()[title + '  --  Weever']
            else:
                return ctx.tag.clear()[title]
            break

    def render_welcome(self, ctx, data):
        user = iusers.IA(ctx).get('ulogin', None)
        if user:         
            uri = url.URL.fromContext(ctx)
            uri.pathList(copy=False).insert(0, guard.LOGOUT_AVATAR)
            ctx.tag.fillSlots('status', 'Logout (%s)' % (user,))
            ctx.tag.fillSlots('link', uri)
        else:
            ctx.tag.fillSlots('status', 'Login')
            ctx.tag.fillSlots('link', url.root.clear().child('login').child(''))
        return ctx.tag
        
    def render_startTimer(self, ctx, data):
        ctx.remember(now(), iweb.ITimer)
        return ctx.tag

    def render_stopTimer(self, ctx, data):
        startTime = iweb.ITimer(ctx)
        return ctx.tag["%.0f" % ((now()-startTime)*1000,)]

    def render_content(self, ctx, data):
        try:
            ct = self.content(self.args, data[FIRST_POST])
        except IndexError:
            ct = self.content(self.args, data)
        #ct = t.cached(key=str(self.__class__), lifetime=30, scope=inevow.ISession)[ct]
        ctx.tag.fillSlots('content', ct)
        return ctx.tag
    
    def render_glue(self, ctx, data):
        ctx.tag.fillSlots('glue', liveevil.glue)
        return ctx.tag


class BaseContent(rend.Fragment):
    def __init__(self, args=[], data=None):
        rend.Fragment.__init__(self)
        self.args = args
        self.data = data
    
    render_isLogged = render_isLogged

from utils.util import implements
class Page404(rend.Page):
    implements(inevow.ICanHandleNotFound)
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
