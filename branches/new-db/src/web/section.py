from time import time as now
from datetime import datetime

from nevow import loaders, inevow, url, tags as t
from formless import webform, annotate, iformless

from utils import util
from main import MasterPage, BaseContent
from database import interfaces as idb
from web import getTemplate, WebException, forms
from web import interfaces as iw


def pptime(date):
    return date.strftime('%b %d, %Y @ %I:%M %p')

def rememberTitle(result, ctx):
    ctx.remember(result[0].get('stitle'), iw.IMainTitle)
    return result

class SectionContent(BaseContent):
    docFactory = loaders.xmlfile(getTemplate('section_content.html'),
            ignoreDocType=True)    
    
    def render_stitle(self, ctx, data):
        title = iw.IMainTitle(ctx)
        return ctx.tag.clear()['Section: '+title]
    
    def data_topics(self, ctx, data):
        for sid in self.args:
            return idb.ISectionsDatabase(idb.IS(ctx)).getSection(sid)
    
    def render_topic(self, ctx, data):
        link = url.root.child('topic').child(data['tid'])
        ctx.tag.fillSlots('title', t.a(href=link)[data['ttitle']])
        ctx.tag.fillSlots('posts_num', int(data['posts_num'])-1)
        ctx.tag.fillSlots('author', data['towner'])
        ctx.tag.fillSlots('modification', pptime(data['tmodification']))
        return ctx.tag

class Section(MasterPage):
    content = SectionContent
    def data_head(self, ctx, data):
        if len(self.args) >= 1:
            return idb.ISectionsDatabase(idb.IS(ctx)).getSectionInfo(self.args[0]).addCallback(rememberTitle, ctx)
        return [{'ttitle':'Section -- Weever'}]

    
    def childFactory(self, ctx, segment):
        if segment != '':
            try:
                sid = int(segment)
            except ValueError:
                return super(Section, self).childFactory(ctx, segment)
        else:
            sid = 1
        self.args.append(sid)
        return Section(self.args)

