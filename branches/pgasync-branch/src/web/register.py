from nevow import loaders, url, tags as t
from formless import annotate, webform
from nevow.compy import newImplements as implements

from main import MasterPage, BaseContent
from web import getTemplate
from database.interfaces import IS, ITopicsDatabase, IUsersDatabase

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
        d = IUsersDatabase(IS(ctx)).addUser(properties)
        return d


class RegisterContent(BaseContent):
    
    docFactory = loaders.xmlfile(getTemplate('register_content.html'),
                                 ignoreDocType=True)

    def render_form(self, ctx, data):
        return webform.renderForms()[ctx.tag]
