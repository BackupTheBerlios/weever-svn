# -*- encoding: utf-8 -*-
from datetime import datetime

from nevow import loaders, url, tags as t
from formless import webform, annotate, iformless
from nevow.compy import newImplements as implements
from nevow.compy import backwardsCompatImplements as bkwImplements

from main import MasterPage, BaseContent
from web import getTemplate
from database.interfaces import IS, ITopicsDatabase
from users.interfaces import IA
from web.interfaces import IMainTitle

def pptime(date):
    return date.strftime('%b %d, %Y @ %I:%M %p')

class IQuickReply(annotate.TypedInterface):
    def quick_reply(self,
       ctx=annotate.Context(),
       title=annotate.String(required=True,
                             requiredFailMessage="Missing Title",
                             maxlength="70",
                             size="70"),
       content=annotate.Text(required=True,
                             requiredFailMessage="Missing body",
                             cols="80",
                             rows="8")
    ):
        """Quick Reply
        """
    quick_reply = annotate.autocallable(quick_reply,
                                        action="Post Reply")

def rememberTitle(result, ctx):
    ctx.remember(result[0].get('ptitle'), IMainTitle)
    return result

class Topic(MasterPage):
    implements(IQuickReply)

    ## TOREMOVE:
    __implements__ = MasterPage.__implements__, IQuickReply


    def data_head(self, ctx, data):
        # It's the first post of the whole query (even if it's a 200
        # results query.
        LIMIT = '1'
        OFFSET = '0'
        if len(self.args):
            return ITopicsDatabase(IS(ctx)).getAllPosts(self.args[0],
                                                        LIMIT, OFFSET
                      ).addCallback(rememberTitle, ctx)
        return MasterPage.data_head(self, ctx, data)

    def childFactory(self, ctx, segment):
        if segment != '':
            try:
                start = int(segment)
            except ValueError:
                return super(Topic, self).childFactory(ctx, segment)
        else:
            start = 1
        self.args.append(start)
        return Topic(self.args, ctnt=TopicContent)
    
    def quick_reply(self, ctx, title, content):
        properties = dict(thread_id=self.args[0],
                          owner_id=IA(ctx)['uid'],
                          creation=datetime.now(),
                          modification=datetime.now(),
                          title=title,
                          body=content
                         )
        d = ITopicsDatabase(IS(ctx)).addPost(properties)
        return d


class TopicContent(BaseContent):

    docFactory = loaders.xmlfile(getTemplate('topic_content.html'),
            ignoreDocType=True)

    def __init__(self, args, data=None):
        super(TopicContent, self).__init__(args, data)
        if len(args) <= 1:
            self.offset = '1'
            self.start = 1
        else:
            self.offset = str(args[1])
            self.start = args[1]
        self.LIMIT = '10'

    def render_firstTopic(self, ctx, data):
        d = self.data
        if d:
            ctx.tag.fillSlots('quote', '/reply.xhtml')
            ctx.tag.fillSlots('edit', '/edit.xhtml')
            ctx.tag.fillSlots('permalink', '/permalink.xhtml')
            ctx.tag.fillSlots('title', d.get('ttitle'))
            ctx.tag.fillSlots('body', d.get('pbody'))
            ctx.tag.fillSlots('userpref', d.get('powner')+'.xhtml')
            ctx.tag.fillSlots('owner', d.get('powner'))
            ctx.tag.fillSlots('when', pptime(d.get('pmodification')))
            return ctx.tag
        return ctx.tag.clear()["Sorry, this page is not available yet"]

    def data_posts(self, ctx, data):
        # remember to remove this ugly stuff once there is a
        # 'all topics' page
        for topic_id in self.args:
            return ITopicsDatabase(IS(ctx)).getAllPosts(topic_id, self.LIMIT, self.offset)
        return []

    def data_numPosts(self, ctx, data):
        for topic_id in self.args:
            return ITopicsDatabase(IS(ctx)).getPostsNum(topic_id)
        return []

    def render_repliesnum(self, ctx, data):
        self.posts_num = 0
        for d in data:
            self.posts_num = int(d.get('posts_num'))-1
            break
        return ctx.tag.clear()[self.posts_num]

    def render_empty(self, ctx, data):
        return ctx.tag

    def render_reply(self, ctx, data):
        ctx.tag.fillSlots('progression', self.start)
        ctx.tag.fillSlots('quote', '/reply.xhtml')
        ctx.tag.fillSlots('edit', '/edit.xhtml')
        ctx.tag.fillSlots('permalink', '/permalink.xhtml')
        ctx.tag.fillSlots('ptitle', data.get('ptitle'))
        ctx.tag.fillSlots('body', data.get('pbody'))
        ctx.tag.fillSlots('userpref', data.get('powner')+'.xhtml')
        ctx.tag.fillSlots('owner', data.get('powner'))
        ctx.tag.fillSlots('when', pptime(data.get('pmodification')))
        self.start = self.start + 1
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

    def render_form(self, ctx, data):
        defaults=iformless.IFormDefaults(ctx).getAllDefaults('quick_reply')
        defaults['title'] = "Re: "+IMainTitle(ctx, '')
        return webform.renderForms()[ctx.tag]

