from nevow import loaders, url, liveevil

from web import topic, getTemplate
from database import interfaces as idb

class PostContent(topic.TopicContent):
    docFactory = loaders.xmlfile(getTemplate('post_content.html'),
            ignoreDocType=True)

    def render_firstTopic(self, ctx, data):
        d = self.data
        def sendReplyForm(client):
            current = d.get('pid')
            client.append('reply_%s' % current, topic.QuickForm(d))
            
        if d:
            ctx.tag.fillSlots('quote', liveevil.handler(sendReplyForm))
            ctx.tag.fillSlots('permalink', url.root.clear().child('post').child(d.get('pid')))
            rp = d.get('preferences_').split('.')[0]
            
            ctx.tag.fillSlots('thread', url.root.clear().child('topic').child(rp))
            ##
            topic.fillReply(ctx, d)
            ##
            return ctx.tag
        return ctx.tag.clear()["Sorry, this page is not available yet"]


class Post(topic.Topic):
    content = PostContent

    def data_head(self, ctx, data):
        if len(self.args):
            return idb.ITopicsDatabase(idb.IS(ctx)
                                       ).getPost(self.args[0]
                                       ).addCallback(topic.rememberTitle,ctx)
        return None

    def childFactory(self, ctx, segment):
        if segment != '':
            try:
                start = int(segment)
            except ValueError:
                return super(Post, self).childFactory(ctx, segment)
        else:
            start = 1
        self.args.append(start)
        return Post(self.args)
