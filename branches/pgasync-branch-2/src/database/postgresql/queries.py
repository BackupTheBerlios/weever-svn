all_users = """ SELECT uid, uscreename, ulogin, upassword,
ugroup_id, uemail, uhomepage, gdescription, gpermissionlevel
FROM  users_permissions
"""

add_user = """
INSERT INTO users(screename, login, password, group_id, email, homepage) 
VALUES(%(screename)s, %(login)s, %(password)s, %(group_id)s, %(email)s, %(homepage)s);
"""

user = """ SELECT uid, uscreename, ulogin, upassword,
ugroup_id, uemail, uhomepage, gdescription, gpermissionlevel
FROM users_permissions WHERE ulogin=%s
"""

all_users_stats = """ SELECT uid, uname, usurname, ulogin,
upassword, ugroup_id, uemail, uhomepage, gdescription,
gpermissionlevel, total_posts
FROM users_permissions_posts
"""

user_stats = """ SELECT uid, uscreename, ulogin,
upassword, ugroup_id, uemail, uhomepage, gdescription,
gpermissionlevel, total_posts
FROM users_permissions_posts
     WHERE ulogin = %s
"""

all_sections = """ SELECT sid, stitle, sdescription, thread_num, lastmod
FROM all_sections
"""

simple_all_sections = """ SELECT id AS sid, title AS stitle, description AS sdescription FROM sections """

simple_section = """ SELECT id as sid, title as stitle, description as sdescription FROM sections WHERE id = %s """

top_threads = """ SELECT sid, stitle, sdescription, tid, ttitle,
towner, tnoise, tcreation, tmodification, posts_num
FROM all_threads LIMIT %s
"""

section = """ SELECT sid, stitle, sdescription, tid, ttitle,
towner, tnoise, tcreation, tmodification, posts_num
FROM all_threads WHERE sid=%s """

topic = """ SELECT ttitle, tcreation, pmodification, pid, ptid,
pcreation, pnoise, ptitle, pbody, powner, pparsed_body

FROM discussion WHERE ptid=%s LIMIT %s OFFSET %s"""

add_topic = """
INSERT INTO thread (title, owner_id, section_id, noise, creation)
VALUES(%(title)s,%(owner_id)s,%(section_id)s,%(noise)s,%(creation)s);
"""

add_post = """
INSERT INTO posts (thread_id, owner_id, creation, modification, title, body)
VALUES(%(thread_id)s, %(owner_id)s, %(creation)s, %(modification)s, %(title)s, %(body)s);
"""

add_section = """
INSERT INTO sections (title, description) VALUES (%(title)s, %(description)s);
"""

del_section = """
DELETE FROM sections WHERE id = %(sid)s
"""

posts_num = """ SELECT COUNT(*) AS posts_num FROM posts p WHERE p.thread_id = %s """

