from nevow import loaders

from web import topic, getTemplate
from database import interfaces as idb

class PostContent(topic.TopicContent):
    docFactory = loaders.xmlfile(getTemplate('post_content.html'),
            ignoreDocType=True)


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
