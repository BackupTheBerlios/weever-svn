# -*- encoding: utf-8 -*-

from nevow import rend, loaders, url
from nevow import tags as t

from database import interfaces as idata
from database.interfaces import IS

from web import main, topic

def pptime(date):
    return date.strftime('%b %d, %Y @ %I:%M %p')

class Main(main.MasterPage):    
    def child_topic(self, ctx, data=None):
        return topic.Topic(data, ctnt=topic.TopicContent)
    
    #def section(self, id):
    #    return Main(id, ctnt=SectionContent)

class IndexContent(main.BaseContent):
    docFactory = loaders.xmlfile('templates/index_content.html', ignoreDocType=True)

    def data_HotTopics(self, ctx, data):
        return idata.ITopicsDatabase(IS(ctx)).getTopTopics(15)

    def render_topicHead(self, ctx, data):
        link = url.root.child('topic').child(data['tid'])
        ctx.fillSlots('title', t.a(href=link)[data['ttitle']])
        ctx.fillSlots('posts_num', data['posts_num'])
        ctx.fillSlots('author', data['towner'])
        ctx.fillSlots('section', data['stitle'])
        ctx.fillSlots('modification', pptime(data['tmodification']))
        return ctx.tag

    def data_Sections(self, ctx, data):
        return idata.ISectionsDatabase(IS(ctx)).getAllSections()

    def render_section(self, ctx, data):
        link = url.root.child('section').child(data['sid'])
        ctx.fillSlots('title', t.a(href=link)[data['stitle']])
        ctx.fillSlots('thread_num', data['thread_num'])
        ctx.fillSlots('description', t.p(_class="desc")[data['sdescription']])
        ctx.fillSlots('lastMod', pptime(data['lastmod']))
        return ctx.tag

