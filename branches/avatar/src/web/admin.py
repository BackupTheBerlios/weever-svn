from nevow import loaders
from web import main, getTemplate

import admin_sections

class AdminContent(main.BaseContent):
    docFactory = loaders.xmlfile(getTemplate('admin_index_content.html'),
                                 ignoreDocType=True)


class Admin(main.MasterPage):
    content = AdminContent
    def data_head(self, ctx, data):
        return [{'ttitle':'Admin -- Weever'}]
    
    def child_sections(self, ctx, data=None):
        reload(admin_sections)
        return admin_sections.ASections(data)

