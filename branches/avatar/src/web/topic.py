# -*- encoding: utf-8 -*-
from datetime import datetime

from nevow import loaders, url, tags as t, liveevil, rend
from formless import webform, annotate, iformless

from utils import util, napalm
from main import MasterPage, BaseContent
from database import interfaces as idb #import IS, ITopicsDatabase
from users import interfaces as iusers #interfaces import IA
from web import interfaces as iweb #import IMainTitle
from web import getTemplate, forms

def pptime(date):
    return date.strftime('%b %d, %Y @ %I:%M %p')

def clean(title):
    title = ' '.join([word.strip() for word in title.split()])
    if title.startswith('Re: '):
        return title
    else: return "Re: "+title

def fillReply(ctx, d):
    ctx.tag.fillSlots('id', d.get('pid'))
    ctx.tag.fillSlots('edit', '/edit.xhtml')
    ctx.tag.fillSlots('title', d.get('ttitle'))
    ctx.tag.fillSlots('body', t.xml(d.get('pparsed_body')))
    ctx.tag.fillSlots('userpref', url.root.clear().child('user').child(str(d.get('ulogin'))))
    ctx.tag.fillSlots('owner', d.get('powner'))
    ctx.tag.fillSlots('when', pptime(d.get('pmodification')))

class QuickForm(rend.Fragment):
    def title(self, ctx, data):
        title = data.get('ptitle')
        if title == '':
            title = data.get('ttitle')
        title = clean(title)
        hd_inpt = t.input(type="hidden", id="reply_to",
                          name="reply_to", value=data.get('pid'))
        inpt = t.input(type="text", id="title_", name="title",
                       maxlength="70", size="60", value=title)
        return t.invisible[hd_inpt, inpt]

    def body(self, ctx, data):
        d = data.get('pbody').split('\r\n')
        text_content = '\n> '.join(d)
        if not text_content.startswith('>'):
            text_content = '> '+text_content
        text = t.textarea(id="content_", name="content",
                          cols="70", rows="8", size="70")[
                text_content
            ]
        return text

    def onclick(self, ctx, data):
        return t.a(href="#", onclick="removeNode('replform_%s');return false;" % (data.get('pid')))[t.img(src="/theme/close.png")]

    def form(self, ctx, data):
        return t.div(_class="quick", id="replform_%s" % data.get('pid'))[
            t.form(action="./freeform_post!!quick_reply", method="post")[
                t.h3["Quote & Reply ",
                     self.onclick
                ],
                t.fieldset[
                    t.label(_for="title_")["Title"],
                    self.title,
                    t.label(_for="content_")["Message",
                        t.span[" (Markdown formatting rules are supported)"]
                    ],
                    self.body                    
                ],
                t.fieldset[
                    t.input(type="submit", name="Post Reply", value="Post Reply")
                ]   
            ]
        ]
    

    docFactory = loaders.stan(
         form
    )
    
class IQuickReply(annotate.TypedInterface):
    def quick_reply(self,
       ctx=annotate.Context(),
       reply_to=annotate.Integer(hidden=True, default=0),
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
    try:
        t = result[0]
    except (IndexError, KeyError):
        try:
            t = result
        except AttributeError:
            return result
    title = t.get('ptitle')
    if title == '':
        title = t.get('ttitle')
    ctx.remember(title, iweb.IMainTitle)
    return result

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
        def sendReplyForm(client):
            current = d.get('pid')
            client.append('reply_%s' % current, QuickForm(d))
            
        if d:
            ctx.tag.fillSlots('quote', liveevil.handler(sendReplyForm))
            ctx.tag.fillSlots('permalink', url.root.clear().child('topic').child(d.get('pid')))
            ##
            fillReply(ctx, d)
            ##
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
        def sendReplyForm(client):
            current = data.get('pid')
            client.append('reply_%s' % current, QuickForm(data))

        ctx.tag.fillSlots('progression', self.start)
        ctx.tag.fillSlots('ptitle', data.get('ptitle'))
        ctx.tag.fillSlots('quote', liveevil.handler(sendReplyForm))
        ctx.tag.fillSlots('permalink', url.root.clear().child('post').child(data.get('pid')))
        ##
        fillReply(ctx, data)
        ##
        self.start = self.start + 1
        #  margin-left:10px  margin-left:20px  margin-left:30px con un
        #  max(x, 40)
        indent_level = data.get('indent_level')
        return t.div(style="margin-left: %spx" % min(indent_level*10, 40))[ctx.tag]

    def render_divider(self, ctx, data):
        return ctx.tag

    def render_nextPosts(self, ctx, data):
        # self.start is initialized to 1, posts_num
        # someone MUST fix this -1 +1 jungle.
        if (self.start-1) < self.posts_num:
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
        else:
            print self.start, self.posts_num
            return ctx.tag.clear()

    def render_form(self, ctx, data):
        defaults=iformless.IFormDefaults(ctx).getAllDefaults('quick_reply')
        defaults['title'] = "Re: "+iweb.IMainTitle(ctx, '')
        return webform.renderForms()[ctx.tag]

class Topic(MasterPage):
    content = TopicContent
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
        return Topic(self.args)
    
    def quick_reply(self, ctx, reply_to, title, content):
        if not iusers.IA(ctx).get('uid'):
            raise WebException("You must login first")
        text = loaders.stan(napalm.MarkdownParser(content).parse()).load()[0]
        properties = dict(reply_to=reply_to or self.args[0],
                          owner_id=iusers.IA(ctx)['uid'],
                          creation=datetime.now(),
                          modification=datetime.now(),
                          title=title,
                          body=content,
                          parsed_body=unicode(text.decode('utf-8'))
                         )
        d = idb.ITopicsDatabase(idb.IS(ctx)).addPost(properties)
        return d
util.backwardsCompatImplements(Topic)


