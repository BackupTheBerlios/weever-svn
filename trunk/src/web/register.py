from nevow import loaders, url, tags as t

from main import MasterPage, BaseContent
from web import getTemplate
from database.interfaces import IS, ITopicsDatabase

class Register(MasterPage):
    def data_head(self, ctx, data):
        return [{'ttitle':'Register -- Weever'}]

class RegisterContent(BaseContent):
    docFactory = loaders.xmlfile(getTemplate('register_content.html'),
                                 ignoreDocType=True)