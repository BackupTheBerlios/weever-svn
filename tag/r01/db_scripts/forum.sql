DROP TABLE groups CASCADE;
DROP TABLE users CASCADE;
DROP TABLE sections CASCADE;
DROP TABLE thread CASCADE;
DROP TABLE posts CASCADE;

CREATE TABLE groups (
    id serial NOT NULL PRIMARY KEY,
    description varchar(15) NOT NULL,
    permissionlevel smallint NOT NULL
);

CREATE TABLE users (
    id serial NOT NULL PRIMARY KEY,
    screename varchar(30) NOT NULL,
    login varchar(15) NOT NULL UNIQUE,
    password varchar(15) NOT NULL,
    group_id int NOT NULL default 2,
    email varchar(30) NOT NULL UNIQUE,
    homepage varchar(60) default '',
    
    FOREIGN KEY(group_id) REFERENCES groups(id)
);

CREATE TABLE sections (
    id serial NOT NULL PRIMARY KEY,
    title varchar(30) NOT NULL,
    description varchar(200) NOT NULL
);

CREATE TABLE thread (
    id serial NOT NULL PRIMARY KEY,
    title varchar(70) NOT NULL,
    owner_id int NOT NULL,
    section_id int NOT NULL,
    noise smallint NOT NULL default 0,
    creation timestamp NOT NULL,
    
    FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(section_id) REFERENCES sections(id) ON DELETE CASCADE
);


CREATE TABLE posts (
    id serial NOT NULL PRIMARY KEY,
    thread_id int NOT NULL,
    owner_id int NOT NULL,
    creation timestamp NOT NULL,
    modification timestamp NOT NULL,
    noise smallint NOT NULL default 0,
    title VARCHAR(100) default '',
    body TEXT,
    parsed_body TEXT,
    
    FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(thread_id) REFERENCES thread(id) ON DELETE CASCADE
);

CREATE VIEW user_posts AS
    SELECT u.id AS uid, COUNT(*) AS posts_num
    FROM users u JOIN posts p ON (u.id = p.owner_id)
        GROUP BY uid;

CREATE VIEW last_modified AS
    SELECT s.id AS sid, MAX(p.modification) AS lastmod 
    FROM sections s JOIN thread t ON (t.section_id = s.id)
         JOIN posts p ON (t.id = p.thread_id)
        GROUP BY sid;

CREATE VIEW threads_in_section AS
    SELECT s.id AS sid, COUNT(*) AS thread_num 
    FROM thread t JOIN sections s ON (t.section_id = s.id)
        GROUP BY sid;

CREATE VIEW posts_in_thread AS
    SELECT t.id AS tid, COUNT(*) AS posts_num 
    FROM posts p JOIN thread t ON (p.thread_id = t.id) 
    GROUP BY tid;
    --ORDER BY p.modification;

CREATE VIEW last_modified_in_thread AS
       SELECT t.id AS tid, MAX(p.modification) AS pmodification
       FROM posts p JOIN thread t ON (p.thread_id = t.id)
       GROUP BY tid;

CREATE VIEW users_permissions_posts AS
    SELECT u.id AS uid, u.screename AS uscreename, u.login AS ulogin, 
            u.password AS upassword, u.group_id AS ugroup_id, u.email AS uemail, 
            u.homepage AS uhomepage, g.description AS gdescription, 
            g.permissionlevel AS gpermissionlevel, up.posts_num
    FROM groups g JOIN users u ON (u.group_id = g.id) JOIN user_posts up ON (u.id = up.uid);

CREATE VIEW users_permissions AS
    SELECT u.id AS uid, u.screename AS uscreename, u.login AS ulogin, 
            u.password AS upassword, u.group_id AS ugroup_id, u.email AS uemail, 
            u.homepage AS uhomepage, g.description AS gdescription, 
            g.permissionlevel AS gpermissionlevel
    FROM groups g INNER JOIN users u ON (u.group_id = g.id);

CREATE VIEW all_sections AS
    SELECT s.id AS sid, s.title AS stitle, s.description AS sdescription, 
            ts.thread_num AS thread_num, lm.lastmod AS lastmod
    FROM sections s LEFT JOIN last_modified lm ON (lm.sid = s.id) 
                    LEFT JOIN threads_in_section ts ON (ts.sid = s.id);
    
CREATE VIEW discussion AS
    SELECT t.title AS ttitle, t.creation AS tcreation, p.modification AS pmodification, p.id AS pid, 
            p.thread_id AS ptid, p.creation AS pcreation, p.noise AS pnoise, 
            p.title AS ptitle, p.body AS pbody, p.parsed_body as pparsed_body, 
            u.screename AS powner
    FROM thread t JOIN posts p ON (t.id = p.thread_id) JOIN users u ON (p.owner_id = u.id) 
        ORDER BY p.id;

CREATE VIEW all_threads AS
    SELECT s.id AS sid, s.title AS stitle, s.description AS sdescription, t.id AS tid, t.title AS ttitle, 
            u.screename AS towner, t.noise AS tnoise, t.creation AS tcreation, lmt.pmodification AS tmodification, 
            pt.posts_num AS posts_num 
    FROM sections s JOIN thread t ON (s.id = t.section_id) JOIN users u ON (t.owner_id = u.id)
                    JOIN posts_in_thread pt ON (pt.tid = t.id) JOIN last_modified_in_thread lmt ON (lmt.tid = t.id)
        ORDER BY tmodification DESC;

INSERT INTO groups(description, permissionlevel) VALUES ('Owner', 0);
INSERT INTO groups(description, permissionlevel) VALUES ('Admin', 1);
INSERT INTO groups(description, permissionlevel) VALUES ('User', 2);


INSERT INTO users(screename, login, password, group_id, email, homepage) 
                  VALUES('Administrator', 'root', 'pass', 1, 'admin@weever.com', '');
