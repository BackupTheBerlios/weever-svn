# -*- encoding: utf-8 -*-

from nevow import loaders, url, tags as t

from main import MasterPage, BaseContent
from database.interfaces import IS, ITopicsDatabase

def pptime(date):
    return date.strftime('%b %d, %Y @ %I:%M %p')

class NewTopic(MasterPage):
    def data_head(self, ctx, data):
        return [{'ttitle':'New Topic -- Weever'}]

class NewTopicContent(BaseContent):
    docFactory = loaders.xmlfile('templates/newtopic_content.html',
            ignoreDocType=True)

class Topic(MasterPage):
    def data_head(self, ctx, data):
        # It's the first post of the whole query (even if it's a 200
        # results query.
        LIMIT = '1'
        OFFSET = '0'
        return ITopicsDatabase(IS(ctx)).getAllPosts(self.args[0], LIMIT, OFFSET)

class TopicContent(BaseContent):
    docFactory = loaders.xmlfile('templates/topic_content.html',
            ignoreDocType=True)

    def __init__(self, args, data=None):
        BaseContent.__init__(self, args, data)
        if len(self.args) == 1:
            self.start = 0
        else:
            if self.args[1] != '':
                try:
                    self.start = self.counter = int(self.args[1])
                except ValueError:
                    self.start = self.counter = 0
            else:
                self.start = self.counter = 0
        if not self.start: self.offset = '1'
        else: self.offset = str(self.start)

        self.LIMIT = '10'

    def render_firstTopic(self, ctx, data):
        d = self.data
        ctx.tag.fillSlots('quote', '/reply.xhtml')
        ctx.tag.fillSlots('edit', '/edit.xhtml')
        ctx.tag.fillSlots('permalink', '/permalink.xhtml')
        ctx.tag.fillSlots('title', d.get('ttitle'))
        ctx.tag.fillSlots('body', d.get('pbody'))
        ctx.tag.fillSlots('userpref', d.get('powner')+'.xhtml')
        ctx.tag.fillSlots('owner', d.get('powner'))
        ctx.tag.fillSlots('when', pptime(d.get('pmodification')))
        return ctx.tag

    def data_posts(self, ctx, data):
        return ITopicsDatabase(IS(ctx)).getAllPosts(self.args[0], self.LIMIT, self.offset)

    def data_numPosts(self, ctx, data):
        return ITopicsDatabase(IS(ctx)).getPostsNum(self.args[0])

    def render_repliesnum(self, ctx, data):
        self.posts_num = int(data[0].get('posts_num'))-1
        return ctx.tag.clear()[self.posts_num]

    def render_reply(self, ctx, data):
        self.start = self.start + 1
        ctx.fillSlots('progression', self.start)
        ctx.fillSlots('quote', '/reply.xhtml')
        ctx.fillSlots('edit', '/edit.xhtml')
        ctx.fillSlots('permalink', '/permalink.xhtml')
        ctx.fillSlots('ptitle', data.get('ptitle'))
        ctx.fillSlots('body', data.get('pbody'))
        ctx.fillSlots('userpref', data.get('powner')+'.xhtml')
        ctx.fillSlots('owner', data.get('powner'))
        ctx.fillSlots('when', pptime(data.get('pmodification')))
        return ctx.tag

    def render_nextPosts(self, ctx, data):
        if self.start < self.posts_num:
            if self.offset == '1': 
                link = url.here.child(self.start)
            else:
                link = url.here.parent().child(self.start)
            remaining = self.posts_num-self.start+1
            toDisplay = (remaining, self.LIMIT)[int(self.LIMIT)<remaining]
            ctx.tag.fillSlots('num', toDisplay)
            ctx.tag.fillSlots('href', link)
            return ctx.tag
        else: return ctx.tag.clear()
