# -*- encoding: utf-8 -*-
import sys

from twisted.python import util

from nevow import rend, loaders, url, inevow
from nevow import tags as t, guard

from web import main, topic, newtopic, post
from web import getTemplate, register, section, admin
from web import WebException

from web import interfaces as iweb
from users import interfaces as iusers
from database import interfaces as idb

def pptime(date):
    return date.strftime('%b %d, %Y @ %I:%M %p')

class IndexContent(main.BaseContent):
    docFactory = loaders.xmlfile(getTemplate('index_content.html'), ignoreDocType=True)

    def data_HotTopics(self, ctx, data):
        return idb.ITopicsDatabase(idb.IS(ctx)).getTopTopics(15)

    def render_topicHead(self, ctx, data):
        link = url.root.clear().child('topic').child(data['tid']).child('')
        title = data['ttitle']
        if len(title) > 20 and len(title.split()) < 2:
            title = title[:20]+"&hellip;"
        elif len(title.split()) >= 2 and len(title) > 35:
            title = title[:35]+"&hellip;"
        ctx.tag.fillSlots('title', t.a(href=link)[t.xml(title)])
        ctx.tag.fillSlots('posts_num', int(data['posts_num'])-1)
        ctx.tag.fillSlots('author', data['towner'])
        ctx.tag.fillSlots('section', data['stitle'])
        ctx.tag.fillSlots('modification', pptime(data['tmodification']))
        return ctx.tag

    def data_Sections(self, ctx, data):
        return idb.ISectionsDatabase(idb.IS(ctx)).getAllSections()

    def render_section(self, ctx, data):
        link = url.root.clear().child('section').child(data['sid']).child('')
        if data['lastmod']: tm = pptime(data['lastmod'])
        else: tm = "-"
        if data['thread_num']: n = data['thread_num']
        else: n = "0"
        ctx.tag.fillSlots('title', t.a(href=link)[data['stitle']])        
        ctx.tag.fillSlots('thread_num', n)
        ctx.tag.fillSlots('description', t.p(_class="desc")[data['sdescription']])
        ctx.tag.fillSlots('lastMod', tm)
        return ctx.tag

class Main(main.MasterPage):
    content = IndexContent
    def child_topic(self, ctx, data=None):
        reload(topic)
        return topic.Topic(data)

    def child_newtopic(self, ctx, data=None):
        reload(newtopic)
        return newtopic.NewTopic(data)

    def child_login(self, ctx, data=None):
        return Login(data)
    
    def child_register(self, ctx, data=None):
        reload(register)
        return register.Register(data)
    
    def child_section(self, ctx, data=None):
        reload(section)
        return section.Section(data)

    def child_post(self, ctx, data=None):
        reload(post)
        return post.Post(data)
    
    def child_admin(self, ctx, data=None):
        reload(admin)
        # Need to make 2 dynamic
        if iusers.IA(ctx).get('gpermission_level', sys.maxint) > 1:
            raise WebException("Not Enough Permissions to enter this section")
        else:
            return admin.Admin(data)

class LoginContent(main.BaseContent):
    docFactory = loaders.xmlfile(getTemplate('login_content.html'), ignoreDocType=True)

    def render_login(self, ctx, data):
        referer = iweb.ILastURL(inevow.ISession(ctx), None)
        if referer:
            inevow.ISession(ctx).unsetComponent(iweb.ILastURL)
            referer = "/%s%s" % (guard.LOGIN_AVATAR, referer)
        else:
            last_url = inevow.IRequest(ctx).getHeader('referer')
            if last_url:
                referer = url.URL.fromString(last_url)
                referer.pathList(copy=False).insert(0, guard.LOGIN_AVATAR)
            else: 
                referer = url.root.clear().child(guard.LOGIN_AVATAR).child('')
        ctx.tag.fillSlots('action', referer)
        return ctx.tag


class Login(main.MasterPage):
    content = LoginContent
    def data_head(slf, ctx, data):
        return [dict(ttitle='Login -- Weever')]        

