# -*- encoding: utf-8 -*-
import os.path as op

from twisted.python import util

from nevow import rend, loaders, url
from nevow import tags as t

from database import interfaces as idata
from database.interfaces import IS

from web import main, topic, template_path as tp

def pptime(date):
    return date.strftime('%b %d, %Y @ %I:%M %p')

class Main(main.MasterPage):    
    def child_topic(self, ctx, data=None):
        return topic.Topic(data, ctnt=topic.TopicContent)

    def child_newtopic(self, ctx, data=None):
        return topic.NewTopic(data, ctnt=topic.NewTopicContent)
    
    #def section(self, id):
    #    return Main(id, ctnt=SectionContent)

class IndexContent(main.BaseContent):
    docFactory = loaders.xmlfile(op.join(tp, 'index_content.html'), ignoreDocType=True)

    def data_HotTopics(self, ctx, data):
        return idata.ITopicsDatabase(IS(ctx)).getTopTopics(15)

    def render_topicHead(self, ctx, data):
        link = url.root.child('topic').child(data['tid'])
        ctx.tag.fillSlots('title', t.a(href=link)[data['ttitle']])
        ctx.tag.fillSlots('posts_num', int(data['posts_num'])-1)
        ctx.tag.fillSlots('author', data['towner'])
        ctx.tag.fillSlots('section', data['stitle'])
        ctx.tag.fillSlots('modification', pptime(data['tmodification']))
        return ctx.tag

    def data_Sections(self, ctx, data):
        return idata.ISectionsDatabase(IS(ctx)).getAllSections()

    def render_section(self, ctx, data):
        link = url.root.child('section').child(data['sid'])
        ctx.tag.fillSlots('title', t.a(href=link)[data['stitle']])
        ctx.tag.fillSlots('thread_num', data['thread_num'])
        ctx.tag.fillSlots('description', t.p(_class="desc")[data['sdescription']])
        ctx.tag.fillSlots('lastMod', pptime(data['lastmod']))
        return ctx.tag

