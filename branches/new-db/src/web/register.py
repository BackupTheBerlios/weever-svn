from nevow import loaders, url, tags as t, inevow
from formless import annotate, webform, iformless

from utils import util
from main import MasterPage, BaseContent
from web import getTemplate, interfaces as iweb
from database import interfaces as idb #import IS, ITopicsDatabase, IUsersDatabase
from users import interfaces as iusers #import IA

import index

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
                 name=annotate.String(),
                 homepage=annotate.String()
                ):
        """ Register """
    register = annotate.autocallable(register, action="Register")

class RegisterContent(BaseContent):
    
    docFactory = loaders.xmlfile(getTemplate('register_content.html'),
                                 ignoreDocType=True)

    def render_form(self, ctx, data):
        return webform.renderForms()[ctx.tag]


class Register(MasterPage):

    util.implements(IRegister)

    content = RegisterContent

    def beforeRender(self, ctx):
        session = inevow.ISession(ctx)
        request = inevow.IRequest(ctx)
        session.setComponent(iweb.ILastURL, request.getHeader('referer') or '')

    def data_head(self, ctx, data):
        return [{'ttitle':'Register -- Weever'}]

    def register(self, ctx, username, email,
                 password, name, homepage):
        properties = dict(name=name or username,
                          login=username,
                          password=password,
                          group_id=3,
                          email=email,
                          homepage=homepage
                          ) 
            
        def success(result, ctx, username):
            d = idb.IUsersDatabase(idb.IS(ctx)).findUser(username)
            d.addCallback(login, ctx)
            return d
        def errback(failure, ctx, username):
            error = 'Username: %s already existing' % username
            raise annotate.ValidateError({ 'username' : error }, 'Error: ' + error)  

        def login(avatar, ctx):
            # if using new guard
            # s = inevow.ISession(ctx)
            # creds = credentials.UsernamePassword(avatar['ulogin'], avatar['upassword'])
            # s.setComponent(creds, ignoreClass=True)
            s = inevow.ISession(ctx)
            res = index.Main()
            res.remember(avatar, iusers.IA)
            s.setResourceForPortal(res, s.guard.resource.portal, res.logout)
            #
        uri = iweb.ILastURL(inevow.ISession(ctx), None)
        if uri:
            inevow.ISession(ctx).unsetComponent(iweb.ILastURL)
        inevow.IRequest(ctx).setComponent(iformless.IRedirectAfterPost,uri or '')
        d = idb.IUsersDatabase(idb.IS(ctx)).addUser(properties)
        d.addErrback(errback, ctx, username)
        d.addCallback(success, ctx, username)
        return d
util.backwardsCompatImplements(Register)

