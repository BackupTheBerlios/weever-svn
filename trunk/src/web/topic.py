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
                    self.start = int(self.args[1])
                except ValueError:
                    self.start = 0
            else:
                self.start = 0
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
        ctx.tag.fillSlots('progression', self.start)
        ctx.tag.fillSlots('quote', '/reply.xhtml')
        ctx.tag.fillSlots('edit', '/edit.xhtml')
        ctx.tag.fillSlots('permalink', '/permalink.xhtml')
        ctx.tag.fillSlots('ptitle', data.get('ptitle'))
        ctx.tag.fillSlots('body', data.get('pbody'))
        ctx.tag.fillSlots('userpref', data.get('powner')+'.xhtml')
        ctx.tag.fillSlots('owner', data.get('powner'))
        ctx.tag.fillSlots('when', pptime(data.get('pmodification')))
        return ctx.tag

    def render_nextPosts(self, ctx, data):
        if self.start < self.posts_num:
            if self.offset == '1': 
                link = url.here.child(self.start)
            else:
                link = url.here.parent().child(self.start)
            link = link.anchor("replies")                
            remaining = self.posts_num-self.start+1
            toDisplay = ("Last "+str(remaining), "Next "+self.LIMIT)[int(self.LIMIT)<remaining]
            ctx.tag.fillSlots('num', toDisplay)
            ctx.tag.fillSlots('href', link)
            return ctx.tag
        else: return ctx.tag.clear()
