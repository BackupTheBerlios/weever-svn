all_users = """ SELECT uid, uname, usurname, ulogin, upassword,
ugroup_id, uemail, uhomepage, gdescription, gpermissionlevel
FROM  users_permissions
"""


user = """ SELECT uid, uname, usurname, ulogin, upassword,
ugroup_id, uemail, uhomepage, gdescription, gpermissionlevel
FROM users_permissions WHERE ulogin=%s
"""

all_users_stats = """ SELECT uid, uname, usurname, ulogin,
upassword, ugroup_id, uemail, uhomepage, gdescription,
gpermissionlevel, total_posts
FROM users_permissions_posts
"""

user_stats = """ SELECT uid, uname, usurname, ulogin,
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
towner, tnoise, tcreation, tmodification, posts_num
FROM all_threads WHERE sid=%s """

topic = """ SELECT ttitle, tcreation, tmodification, pid, ptid,
pcreation, pmodification, pnoise, ptitle, pbody, powner

FROM discussion WHERE ptid=%s LIMIT %s OFFSET %s"""

posts_num = """ SELECT COUNT(*) AS posts_num FROM posts p WHERE p.thread_id = %s """

