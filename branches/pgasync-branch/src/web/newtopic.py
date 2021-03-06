from time import time as now
from datetime import datetime

from nevow import loaders, inevow, url
from nevow.compy import newImplements as implements
from formless import webform, annotate, iformless

from main import MasterPage, BaseContent
from users.interfaces import IA
from database import interfaces as idb
from web import getTemplate

choices = ['cazzi e ammazzi', 'prova1']
class INewTopic(annotate.TypedInterface):
    def post_topic(self,
       ctx=annotate.Context(),
       title=annotate.String(required=True,
                             strip=True,
                             requiredFailMessage="Evey topic must have a title",
                             maxlength="70",
                             size="50"),
       content=annotate.Text(required=True,
                             requiredFailMessage="Missing body in this post"),
       section=annotate.Choice(choices)
    ):
        """ """
    post_topic = annotate.autocallable(post_topic, action="Post Topic")

class NewTopic(MasterPage):
    implements(INewTopic)

    ## TODO: remove this stuff 
    __implements__ = MasterPage.__implements__, INewTopic

    def data_head(self, ctx, data):
        return [{'ttitle':'New Topic -- Weever'}]

    def post_topic(self, ctx, title, content, section):
        curr = datetime.now()
        properties_topic = dict(title=title,
                                owner_id=IA(ctx)['uid'],
                                creation=curr,
                                section_id=3,
                                noise=0,
                               )
        properties_post = dict(thread_id='',
                               owner_id=IA(ctx)['uid'],
                               creation=curr,
                               modification=curr,
                               title=title,
                               body=content
                              )
        def redirectTo(result):
            req = inevow.IRequest(ctx)
            req.setComponent(iformless.IRedirectAfterPost,'/topic/%s' % result)
            return result
        d = idb.ITopicsDatabase(idb.IS(ctx)
                                ).addTopic(properties_topic,
                                           properties_post)
        d.addCallback(redirectTo)
        return d

class NewTopicContent(BaseContent):
    
    docFactory = loaders.xmlfile(getTemplate('newtopic_content.html'),
            ignoreDocType=True)

    def render_form(self, ctx, data):
        return webform.renderForms()[ctx.tag]

