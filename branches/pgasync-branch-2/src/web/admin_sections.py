from nevow import loaders, tags as t, url
from formless import webform, annotate

from utils import util
from web import main, getTemplate
from database import interfaces as idb

def pptime(date):
    return date.strftime('%b %d, %Y @ %I:%M %p')

class IASections(annotate.TypedInterface):
    def insert(self,
               ctx=annotate.Context(),
               title=annotate.String(required=True,
                                     requiredFailMessage="Title Missing"),
               description=annotate.String()
               ):
        pass
    insert = annotate.autocallable(insert, action="Create")
    def delete(self, ctx=annotate.Context(), id=annotate.Integer()):
        pass
    delete = annotate.autocallable(delete, invisible=True)
    def edit(self, ctx=annotate.Context(), 
               id=annotate.Integer(), 
               oldstate=annotate.Integer()):
        pass
    edit = annotate.autocallable(edit, invisible=True)

class ASections(main.MasterPage):

    util.implements(IASections)

    def data_head(self, ctx, data):
        return [{'ttitle':'Admin Sections -- Weever'}]    
    
    def edit(self, ctx, id, oldstate):
        pass
    def insert(self, ctx, title, description):
        properties = dict(title=title, description=description)
        d = idb.ISectionsDatabase(idb.IS(ctx)).addSection(properties)
        return d
    def delete(self, ctx, id):
        d = idb.ISectionsDatabase(idb.IS(ctx)).delSection(dict(sid=id))
        return d

util.backwardsCompatImplements(ASections)

class ASectionsContent(main.BaseContent):
    docFactory = loaders.xmlfile(getTemplate('admin_sections_content.html'),
                                 ignoreDocType=True)
    
    def data_Sections(self, ctx, data):
        return idb.ISectionsDatabase(idb.IS(ctx)).simpleGetAllSections()

    def render_section(self, ctx, data):
        delete = "./freeform_post!!delete?id=%s" % data['sid']
        edit = "edit"
        
        link = url.root.clear().child('section').child(data['sid'])
        ctx.tag.fillSlots('title', t.a(href=link)[data['stitle']])
        ctx.tag.fillSlots('descr', data['sdescription'])
        ctx.tag.fillSlots('delete', delete)
        ctx.tag.fillSlots('edit', edit)
        return ctx.tag    
    
    def render_foot(self, ctx, data):
        return ctx.tag
    
    def render_empty(self, ctx, data):
        return ctx.tag
    
    def render_form(self, ctx, data):
        return webform.renderForms(bindingNames=["insert"])[ctx.tag]