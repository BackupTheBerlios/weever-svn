from time import time as now
from datetime import datetime

from nevow import loaders, inevow, url
from formless import webform, annotate, iformless

from utils import util, markdown
from main import MasterPage, BaseContent
from users import interfaces as iusers #import IA
from database import interfaces as idb
from web import getTemplate, WebException, forms
from web import interfaces as iweb

def gatherSections(ctx, data):
    return idb.ISectionsDatabase(idb.IS(ctx)).simpleGetAllSections()

def stringify(x):
    return x['stitle']

def valueToKey(x):
    # When the error renders only the key is passed and not the complete dict.
    try:
        return str(x['sid'])
    except TypeError:
        return str(x)

def keyToValue(x):
    return int(x)

class INewTopic(annotate.TypedInterface):
    def post_topic(self,
        ctx=annotate.Context(),
        title=forms.StyleString(required=True,
                                strip=True,
                                requiredFailMessage="Evey topic must have a title",
                                maxlength="70",
                                size="50"),
        content=annotate.Text(required=True,
                              requiredFailMessage="Missing body in this post"),
        section=annotate.Choice(gatherSections, 
                                stringify=stringify, 
                                valueToKey=valueToKey,
                                keyToValue=keyToValue)
    ):
        """ """
    post_topic = annotate.autocallable(post_topic, action="Post Topic")

class NewTopicContent(BaseContent):
    
    docFactory = loaders.xmlfile(getTemplate('newtopic_content.html'),
            ignoreDocType=True)

    def render_form(self, ctx, data):
        return webform.renderForms()[ctx.tag]

class NewTopic(MasterPage):
    util.implements(INewTopic)
    content = NewTopicContent
    
    def beforeRender(self, ctx):
        if not iusers.IA(ctx).get('uid'):
            inevow.ISession(ctx).setComponent(iweb.ILastURL, '/newtopic/')
            return inevow.IRequest(ctx).redirect('/login/')

    def data_head(self, ctx, data):
        return [{'ttitle':'New Topic -- Weever'}]

    def post_topic(self, ctx, title, content, section):
        if not iusers.IA(ctx).get('uid'):
            raise WebException("You must login first")
        curr = datetime.now()
        properties = dict(title=title,
                          owner_id=iusers.IA(ctx)['uid'],
                          creation=curr,
                          modification=curr,
                          section_id=section,
                          body=content,
                          parsed_body=markdown.Markdown(content).toString()
                          )
        def redirectTo(result):
            req = inevow.IRequest(ctx)
            req.setComponent(iformless.IRedirectAfterPost,'/topic/%s/' % result)
            return result
        d = idb.ITopicsDatabase(idb.IS(ctx)
                                ).addTopic(properties)
        d.addCallback(redirectTo)
        return d

util.backwardsCompatImplements(NewTopic)


