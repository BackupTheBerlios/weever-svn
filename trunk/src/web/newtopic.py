from time import time as now

from nevow import loaders, inevow, url
from nevow.compy import newImplements as implements
from formless import webform, annotate

from main import MasterPage, BaseContent
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
    def data_head(self, ctx, data):
        return [{'ttitle':'New Topic -- Weever'}]

    def configurable_content(self, ctx):
        return self.content

class NewTopicContent(BaseContent):
    implements(INewTopic)

    ## TODO: remove this stuff 
    __implements__ = BaseContent.__implements__, INewTopic
    
    docFactory = loaders.xmlfile(getTemplate('newtopic_content.html'),
            ignoreDocType=True)

    def render_form(self, ctx, data):
        return webform.renderForms('content')[ctx.tag]

    def post_topic(self, ctx, title, content, section):
        print title, content, section
