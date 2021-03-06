from nevow import loaders, url, tags as t, inevow
from formless import annotate, webform, iformless
from nevow.compy import newImplements as implements

from main import MasterPage, BaseContent
from web import getTemplate, interfaces as iw
import index
from database.interfaces import IS, ITopicsDatabase, IUsersDatabase
from users.interfaces import IA

noUsername = "Missing username"
noEmail = "Missing email"
noPwd = "Password Mismatch or missing password"

class IRegister(annotate.TypedInterface):
    def register(self,
                 ctx=annotate.Context(),
                 username=annotate.String(required=True,
                                          requiredFailMessage=noUsername
                                          ),
                 email=annotate.String(required=True,
                                       requiredFailMessage=noEmail
                                       ),
                 password=annotate.Password(required=True,
                                            requiredFailMessage=noPwd
                                            ),
                 screename=annotate.String(),
                 homepage=annotate.String()
                ):
        """ Register """
    register = annotate.autocallable(register, action="Register")

class Register(MasterPage):

    implements(IRegister)

    ## TODO: Remove this stuff
    __implements__ = MasterPage.__implements__, IRegister

    def beforeRender(self, ctx):
        session = inevow.ISession(ctx)
        request = inevow.IRequest(ctx)
        session.setComponent(iw.ILastURL, request.getHeader('referer') or '')

    def data_head(self, ctx, data):
        return [{'ttitle':'Register -- Weever'}]

    def register(self, ctx, username, email,
                 password, screename, homepage):
        properties = dict(screename=screename or username,
                          login=username,
                          password=password,
                          group_id=3,
                          email=email,
                          homepage=homepage
                          ) 
            
        def success(result, ctx, username):
            d = IUsersDatabase(IS(ctx)).findUser(username)
            d.addCallback(login, ctx)
            return d
        def login(avatar, ctx):
            # if using new guard
            # s = inevow.ISession(ctx)
            # creds = credentials.UsernamePassword(avatar['ulogin'], avatar['upassword'])
            # s.setComponent(creds, ignoreClass=True)
            s = inevow.ISession(ctx)
            res = index.Main()
            res.remember(avatar, IA)
            s.setResourceForPortal(res, s.guard.resource.portal, res.logout)
            #
        uri = iw.ILastURL(inevow.ISession(ctx), None)
        if uri:
            inevow.ISession(ctx).unsetComponent(iw.ILastURL)
        inevow.IRequest(ctx).setComponent(iformless.IRedirectAfterPost,uri or '')
        d = IUsersDatabase(IS(ctx)).addUser(properties)
        d.addCallback(success, ctx, username)        
        return d


class RegisterContent(BaseContent):
    
    docFactory = loaders.xmlfile(getTemplate('register_content.html'),
                                 ignoreDocType=True)

    def render_form(self, ctx, data):
        return webform.renderForms()[ctx.tag]
