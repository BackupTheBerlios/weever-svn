# -*- encoding: utf-8 -*-
from datetime import datetime

from nevow import loaders, url, tags as t, liveevil
from formless import webform, annotate, iformless

from utils import util
from main import MasterPage, BaseContent
from database import interfaces as idb #import IS, ITopicsDatabase
from users import interfaces as iusers #interfaces import IA
from web import interfaces as iweb #import IMainTitle
from web import getTemplate, forms

def pptime(date):
    return date.strftime('%b %d, %Y @ %I:%M %p')


liveevil.DEBUG = True

QUICK_REPLY = t.div(_class='quick', id="replform")[
    t.form(action="", method="post")[
        t.h3["Quote & Reply ",
            t.a(href="#")[
                t.img(src="/theme/close.png")
            ]
        ],
        t.fieldset[
            t.label(_for="title_")["Title"],
            t.input(type="text", id="title_", name="title", maxlength="70", size="70", value="Re: Donec eu tellus nec risus"),
            t.label(_for="content_")["Message",
                t.span[" (reST formatting rules are supported)"]
            ],
            t.textarea(id="content_", name="content", cols="70", rows="8", size="70", maxlength="70")["Your reply here."
            ]
        ],
        t.fieldset[
            t.input(type="submit", name="", value="Post Reply")
        ]   
    ]
]

def sendReplyForm(client, current):
    client.append('reply_%s' % current, QUICK_REPLY)

def fillReply(ctx, d):
    ctx.tag.fillSlots('quote', liveevil.handler(sendReplyForm, d.get('pid')))
    ctx.tag.fillSlots('id', d.get('pid'))
    ctx.tag.fillSlots('edit', '/edit.xhtml')
    ctx.tag.fillSlots('permalink', '/permalink.xhtml')
    ctx.tag.fillSlots('title', d.get('ttitle'))
    ctx.tag.fillSlots('body', d.get('pbody'))
    ctx.tag.fillSlots('userpref', d.get('powner')+'.xhtml')
    ctx.tag.fillSlots('owner', d.get('powner'))
    ctx.tag.fillSlots('when', pptime(d.get('pmodification')))


class IQuickReply(annotate.TypedInterface):
    def quick_reply(self,
       ctx=annotate.Context(),
       title=forms.StyleString(required=True,
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
    ctx.remember(result[0].get('ptitle'), iweb.IMainTitle)
    return result

class Topic(MasterPage):
    util.implements(IQuickReply)

    def data_head(self, ctx, data):
        # It's the first post of the whole query (even if it's a 200
        # results query.
        LIMIT = '1'
        OFFSET = '0'
        if len(self.args):
            return idb.ITopicsDatabase(idb.IS(ctx)).getAllPosts(self.args[0],
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
        if not iusers.IA(ctx).get('uid'):
            raise WebException("You must login first")
        properties = dict(thread_id=self.args[0],
                          owner_id=iusers.IA(ctx)['uid'],
                          creation=datetime.now(),
                          modification=datetime.now(),
                          title=title,
                          body=content
                         )
        d = idb.ITopicsDatabase(idb.IS(ctx)).addPost(properties)
        return d
util.backwardsCompatImplements(Topic)

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
            fillReply(ctx, d)
            return ctx.tag
        return ctx.tag.clear()["Sorry, this page is not available yet"]

    def data_posts(self, ctx, data):
        # remember to remove this ugly stuff once there is a
        # 'all topics' page
        for topic_id in self.args:
            return idb.ITopicsDatabase(idb.IS(ctx)).getAllPosts(topic_id, self.LIMIT, self.offset)
        return []

    def data_numPosts(self, ctx, data):
        for topic_id in self.args:
            return idb.ITopicsDatabase(idb.IS(ctx)).getPostsNum(topic_id)
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
        ctx.tag.fillSlots('ptitle', data.get('ptitle'))
        fillReply(ctx, data)
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
        defaults['title'] = "Re: "+iweb.IMainTitle(ctx, '')
        return webform.renderForms()[ctx.tag]

