DROP TABLE groups CASCADE;
DROP TABLE users CASCADE;
DROP TABLE sections CASCADE;
DROP TABLE posts CASCADE;

CREATE TABLE groups (
    id serial NOT NULL PRIMARY KEY,
    description varchar(15) NOT NULL,
    permission_level smallint NOT NULL
);

CREATE TABLE users (
    id serial NOT NULL PRIMARY KEY,
    name varchar(30) NOT NULL,
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
    description varchar(200) NOT NULL,
    permission_required int default 100
);

CREATE TABLE posts (
    id serial NOT NULL PRIMARY KEY,
    section_id int NOT NULL,
    owner_id int NOT NULL,
    references_ int[], 
    creation timestamp NOT NULL,
    modification timestamp NOT NULL,
    noise smallint NOT NULL default 0,
    title VARCHAR(100) default '',
    body TEXT,
    parsed_body TEXT,
    
    FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(section_id) REFERENCES sections(id) ON DELETE CASCADE
);

CREATE VIEW user_posts AS
    SELECT u.id AS uid, COUNT(*) AS posts_num
      FROM users u JOIN posts p ON (u.id = p.owner_id)
  GROUP BY uid;

CREATE VIEW threads AS
    SELECT id, section_id, owner_id, references_, 
           creation, modification, noise, title
    FROM posts
    WHERE references_ is NULL;

CREATE VIEW last_modified AS
    SELECT section_id AS sid, MAX(modification) as lastmod
      FROM posts 
  GROUP BY section_id;

CREATE VIEW threads_in_section AS
    SELECT section_id AS sid, COUNT(*) AS thread_num
      FROM threads 
  GROUP BY section_id;

CREATE VIEW posts_in_thread AS
    SELECT t.id AS tid, COUNT(p.id) AS posts_num
      FROM threads t, posts p
     WHERE t.id = any (p.references_) OR t.id = p.id
  GROUP BY t.id;

CREATE VIEW last_modified_in_thread AS
    SELECT t.id AS tid, MAX(p.modification) AS pmodification
      FROM threads t, posts p
     WHERE t.id = any (p.references_) OR t.id = p.id
  GROUP BY t.id;

CREATE VIEW users_permissions_posts AS
    SELECT u.id AS uid, u.name AS name, u.login AS ulogin, 
           u.password AS upassword, u.group_id AS ugroup_id, u.email AS uemail, 
           u.homepage AS uhomepage, g.description AS gdescription, 
           g.permission_level AS gpermission_level, up.posts_num AS uposts_num
      FROM groups g 
      JOIN users u ON (u.group_id = g.id) 
 LEFT JOIN user_posts up ON (u.id = up.uid);

CREATE VIEW users_permissions AS
    SELECT u.id AS uid, u.name AS uname, u.login AS ulogin, 
           u.password AS upassword, u.group_id AS ugroup_id, u.email AS uemail, 
           u.homepage AS uhomepage, g.description AS gdescription, 
           g.permission_level AS gpermission_level
      FROM groups g 
      JOIN users u ON (u.group_id = g.id);

CREATE VIEW all_sections AS
    SELECT s.id AS sid, s.title AS stitle, s.description AS sdescription, 
           ts.thread_num AS thread_num, lm.lastmod AS lastmod, 
           s.permission_required AS spermission_required
      FROM sections s 
 LEFT JOIN last_modified lm ON (lm.sid = s.id) 
 LEFT JOIN threads_in_section ts ON (ts.sid = s.id)
  ORDER BY lastmod;
    
CREATE VIEW discussion AS
    SELECT t.title AS ttitle, t.creation AS tcreation, p.modification AS pmodification, 
           p.id AS pid, t.id as tid, p.creation AS pcreation, p.noise AS pnoise, 
           p.title AS ptitle, p.body AS pbody, p.parsed_body as pparsed_body, 
           u.name AS powner, p.references_ AS preferences_
      FROM threads t, posts p, users u
     WHERE u.id = p.owner_id AND (t.id = any (p.references_) OR t.id = p.id)
  ORDER BY p.id;

CREATE VIEW all_threads AS
    SELECT s.id AS sid, s.title AS stitle, s.description AS sdescription, t.id AS tid, t.title AS ttitle, 
           u.name AS towner, t.noise AS tnoise, t.creation AS tcreation, lmt.pmodification AS tmodification, 
           pt.posts_num AS posts_num, s.permission_required AS spermission_required
      FROM sections s, threads t, users u, posts_in_thread pt, last_modified_in_thread lmt
     WHERE s.id = t.section_id AND t.owner_id = u.id 
           AND pt.tid = t.id AND lmt.tid = t.id
  ORDER BY tmodification DESC;
 
-- 
-- select id... from posts where %(root_post)s = any (references_);
--

INSERT INTO groups(description, permission_level) VALUES ('Owner', 0);
INSERT INTO groups(description, permission_level) VALUES ('Admin', 1);
INSERT INTO groups(description, permission_level) VALUES ('User', 2);


INSERT INTO users(name, login, password, group_id, email, homepage) 
                  VALUES('Valentino Volonghi', 'dialtone', 'fooo1', 1, 'dialtone@gmail.com', 'http://vvolonghi.blogspot.com');
                  INSERT INTO users(name, login, password, group_id, email, homepage) 
                  VALUES('Andrea Peltrin', 'dee', 'pwd', 1, 'deelan@gmail.com', 'http://www.deelan.com');
INSERT INTO users(name, login, password, group_id, email) 
                  VALUES('Fuffo Tone', 'admin', 'passw', 2, 'fuffo.tone@provider.com');
INSERT INTO users(name, login, password, group_id, email) 
                  VALUES('Mario Rossi', 'guest', 'guest', 3, 'mario.rossi@provider.com');

INSERT INTO sections (title, description) VALUES ('Test', 'Qua si fanno tante belle prove prove');
INSERT INTO sections (title, description) VALUES ('Intro', 'Qui ci vanno gli iniziati');
INSERT INTO sections (title, description) VALUES ('Sticazzi', 'Discussioni con le palle');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, NULL, '2005-01-30', '2005-01-30', 0, '1Foo', 'sticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, ARRAY[1], '2005-01-30', '2005-01-30', 0, 'Foo', '1.sticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, ARRAY[1,2], '2005-01-30', '2005-01-30', 0, 'Foo', '1.2sticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, ARRAY[1], '2005-01-30', '2005-01-30', 0, 'Foo', '1..sticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, NULL, '2005-01-30', '2005-01-30', 0, '2Foo', 'BBsticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, ARRAY[5], '2005-01-30', '2005-01-30', 0, 'Foo', '5.sticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, ARRAY[5,6], '2005-01-30', '2005-01-30', 0, 'Foo', '5.6sticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, NULL, '2005-01-30', '2005-01-30', 0, '3Foo', 'BBsticaz', 'sticaz');
