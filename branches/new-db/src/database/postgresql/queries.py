all_users = """ SELECT uid, uname, ulogin, upassword,
ugroup_id, uemail, uhomepage, gdescription, gpermission_level
FROM  users_permissions
"""

add_user = """
INSERT INTO users(name, login, password, group_id, email, homepage) 
VALUES(%(name)s, %(login)s, %(password)s, %(group_id)s, %(email)s, %(homepage)s);
"""

user = """ SELECT uid, uname, ulogin, upassword,
ugroup_id, uemail, uhomepage, gdescription, gpermission_level
FROM users_permissions WHERE ulogin=%s
"""

all_users_stats = """ SELECT uid, uname, usurname, ulogin,
upassword, ugroup_id, uemail, uhomepage, gdescription,
gpermission_level, total_posts
FROM users_permissions_posts
"""

user_stats = """ SELECT uid, uname, ulogin,
upassword, ugroup_id, uemail, uhomepage, gdescription,
gpermission_level, total_posts
FROM users_permissions_posts
     WHERE ulogin = %s
"""

all_sections = """ SELECT sid, stitle, sdescription, thread_num, lastmod
FROM all_sections
"""

simple_all_sections = """ SELECT id AS sid, title AS stitle, description AS sdescription FROM sections """

simple_section = """ SELECT id as sid, title as stitle, description as sdescription FROM sections WHERE id = %s """

top_threads = """ SELECT sid, stitle, sdescription, tid, ttitle,
towner, tnoise, tcreation, tmodification, posts_num, spermission_required
FROM all_threads LIMIT %s
"""

section = """ SELECT sid, stitle, sdescription, tid, ttitle,
towner, tnoise, tcreation, tmodification, posts_num, spermission_required
FROM all_threads WHERE sid=%s """

topic = """ SELECT preferences_, ttitle, tcreation, pmodification, pid, tid,
pcreation, pnoise, ptitle, pbody, powner, pparsed_body

FROM discussion WHERE tid=%s LIMIT %s OFFSET %s"""

add_topic = """
INSERT INTO posts (section_id, owner_id, creation, modification,
title, body, parsed_body)
VALUES (%(section_id)s,%(owner_id)s,%(creation)s,%(modification)s,
%(title)s,%(body)s,%(parsed_body)s);
"""

add_post = """SELECT reply(%(reply_to)s,%(owner_id)s,%(creation)s,%(modification)s,
%(title)s,%(body)s,%(parsed_body)s);
"""

add_section = """
INSERT INTO sections (title, description) VALUES (%(title)s, %(description)s);
"""

del_section = """
DELETE FROM sections WHERE id = %(sid)s
"""

posts_num = """ SELECT posts_num FROM posts_in_thread WHERE tid=%s """

get_post = """ SELECT id, thread_id, owner_id, creation, modification, references_
noise, title, body, parsed_body FROM posts WHERE id = %s """
