all_users = """ SELECT uid, uname_surname, ulogin, upassword,
ugroup_id, uemail, uhomepage, gdescription, gpermissionlevel
FROM  users_permissions
"""

add_user = """
INSERT INTO users(name_surname, login, password, group_id, email, homepage) 
VALUES(%(name_surname)s, %(login)s, %(password)s, %(group_id)d, %(email)s, %(homepage));
"""

user = """ SELECT uid, uname_surname, ulogin, upassword,
ugroup_id, uemail, uhomepage, gdescription, gpermissionlevel
FROM users_permissions WHERE ulogin=%s
"""

all_users_stats = """ SELECT uid, uname, usurname, ulogin,
upassword, ugroup_id, uemail, uhomepage, gdescription,
gpermissionlevel, total_posts
FROM users_permissions_posts
"""

user_stats = """ SELECT uid, uname_surname, ulogin,
upassword, ugroup_id, uemail, uhomepage, gdescription,
gpermissionlevel, total_posts
FROM users_permissions_posts
     WHERE ulogin = %s
"""

all_sections = """ SELECT sid, stitle, sdescription, thread_num, lastmod
FROM all_sections
"""

top_threads = """ SELECT sid, stitle, sdescription, tid, ttitle,
towner, tnoise, tcreation, tmodification, posts_num
FROM all_threads LIMIT %s
"""

section = """ SELECT sid, stitle, sdescription, tid, ttitle,
towner, tnoise, tcreation, posts_num
FROM all_threads WHERE sid=%s """

topic = """ SELECT ttitle, tcreation, pmodification, pid, ptid,
pcreation, pnoise, ptitle, pbody, powner

FROM discussion WHERE ptid=%s LIMIT %s OFFSET %s"""

add_topic = """
INSERT INTO thread (title, owner_id, section_id, noise, creation, modification)
VALUES(%(title)s,%(owner_id)d,%(section_id)d,%(noise)d,%(creation)s,%(modification)s);
"""

add_post = """
INSERT INTO posts (thread_id, owner_id, creation, modification, title, body)
VALUES(%(thread_id)d, %(owner_id)d, %(creation)s, %(modification)s, %(title)s, %(body)s);
"""

posts_num = """ SELECT COUNT(*) AS posts_num FROM posts p WHERE p.thread_id = %s """

