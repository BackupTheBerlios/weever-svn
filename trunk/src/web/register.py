from nevow import loaders, url, tags as t
from formless import annotate, webform
from nevow.compy import newImplements as implements

from main import MasterPage, BaseContent
from web import getTemplate
from database.interfaces import IS, ITopicsDatabase

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
    def data_head(self, ctx, data):
        return [{'ttitle':'Register -- Weever'}]

    def configurable_content(self, ctx):
        return self.content

class RegisterContent(BaseContent):

    implements(IRegister)

    ## TODO: Remove this stuff
    __implements__ = BaseContent.__implements__, IRegister
    
    docFactory = loaders.xmlfile(getTemplate('register_content.html'),
                                 ignoreDocType=True)

    def register(self, ctx, username, email, password, screename,homepage):
        print username, email, password, screename, homepage

    def render_form(self, ctx, data):
        return webform.renderForms('content')[ctx.tag]
