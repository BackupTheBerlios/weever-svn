DROP TABLE groups CASCADE;
DROP TABLE users CASCADE;
DROP TABLE sections CASCADE;
DROP TABLE posts CASCADE;
DROP TYPE posts_num CASCADE;
DROP TYPE discussion_row CASCADE;
DROP TYPE lmt_row CASCADE;

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
    preferences bytea default NULL,
    
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
    references_ ltree default '', 
    creation timestamp NOT NULL,
    modification timestamp NOT NULL,
    noise smallint NOT NULL default 0,
    title VARCHAR(100) default '',
    body TEXT,
    parsed_body TEXT,
    
    FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(section_id) REFERENCES sections(id) ON DELETE CASCADE
);

CREATE TYPE posts_num AS (tid int, posts_num int);
CREATE TYPE lmt_row AS (tid int, pmodification timestamp);
CREATE TYPE discussion_row AS (
    ttitle varchar(100),
    tcreation timestamp,
    pmodification timestamp,
    pid int,
    tid int,
    pcreation timestamp,
    pnoise int,
    ptitle varchar(100),
    pbody text,
    pparsed_body text,
    powner varchar(100),
    preferences_ ltree
);

-- OK
CREATE OR REPLACE FUNCTION reply(int, int, timestamp, timestamp, varchar(100), text, text) RETURNS int AS '
DECLARE
    reply_to_ ALIAS FOR $1;
    owner_id_ ALIAS FOR $2;
    creation_ ALIAS FOR $3;
    modification_ ALIAS FOR $4;
    title_ ALIAS FOR $5;
    body_ ALIAS for $6;
    parsed_body_ ALIAS FOR $7;
    origin RECORD;
    query varchar(500);
    new int;
BEGIN
    SELECT INTO origin * FROM posts WHERE id = reply_to_;

    INSERT INTO posts (section_id, owner_id, creation, modification,
                       title, body, parsed_body, references_)
         VALUES (origin.section_id, owner_id_, creation_, modification_,
                 title_, body_, parsed_body_, origin.references_);

    SELECT INTO new MAX(id) FROM posts;
    RETURN new;
END;
' LANGUAGE plpgsql;

-- OK
CREATE OR REPLACE FUNCTION discussion(int) RETURNS SETOF discussion_row AS '
DECLARE
  row RECORD;
  r discussion_row%rowtype;
  query varchar(500);
BEGIN
  query := ''SELECT t.title AS ttitle, t.creation AS tcreation, p.modification AS pmodification, 
                    p.id AS pid, t.id as tid, p.creation AS pcreation, p.noise AS pnoise, 
                    p.title AS ptitle, p.body AS pbody, p.parsed_body as pparsed_body, 
                    u.name AS powner, p.references_ AS preferences_
               FROM threads t, posts p, users u
              WHERE u.id = p.owner_id AND p.references_ <@ '''''' 
            || $1
            || '''''' AND t.id=''
            || $1
            || ''ORDER BY p.references_'';

  FOR row IN EXECUTE query LOOP
      r.ttitle := row.ttitle;
      r.tcreation := row.tcreation;
      r.pmodification := row.pmodification;
      r.pid := row.pid;
      r.tid := row.tid;
      r.pnoise := row.pnoise;
      r.ptitle := row.ptitle;
      r.pbody := row.pbody;
      r.pparsed_body := row.pparsed_body;
      r.powner := row.powner;
      r.preferences_ := row.preferences_;
      RETURN NEXT r;
  END LOOP;
  RETURN;
END;
' LANGUAGE plpgsql;

-- OK
CREATE OR REPLACE FUNCTION posts_in_thread() RETURNS SETOF posts_num AS '
DECLARE
   r posts_num%rowtype;
   thread RECORD;
   res RECORD;
   query varchar(200);
BEGIN
   query := ''SELECT COUNT(p.id) AS posts_num FROM posts p WHERE p.references_ <@ '''''';

   FOR thread IN SELECT id FROM threads LOOP
       FOR res IN EXECUTE query || thread.id || '''''''' LOOP
           r.tid := thread.id;
           r.posts_num := res.posts_num;
           RETURN NEXT r;
       END LOOP;
   END LOOP;
   RETURN;
END;
' LANGUAGE plpgsql;

-- OK
CREATE OR REPLACE FUNCTION last_modified_in_thread() RETURNS SETOF lmt_row AS '
DECLARE
   r lmt_row%rowtype;
   row RECORD;
   maxtime RECORD;
   query varchar(200);
BEGIN
   query := ''SELECT MAX(modification) AS pmodification
                FROM posts
               WHERE references_ <@ '''''';
   FOR row IN SELECT id FROM threads LOOP
       FOR maxtime IN EXECUTE query || row.id || '''''''' LOOP
           r.tid := row.id;
           r.pmodification := maxtime.pmodification;
           RETURN NEXT r;
       END LOOP;
   END LOOP;
   RETURN;
END;
' LANGUAGE plpgsql;

-- OK
CREATE OR REPLACE FUNCTION on_insert_post() RETURNS trigger AS '
   BEGIN
        UPDATE posts SET references_ = NEW.references_ || NEW.id WHERE id = NEW.id;
        RETURN NEW;
   END;
' LANGUAGE plpgsql;

CREATE TRIGGER on_insert_post AFTER INSERT ON posts
       FOR EACH ROW EXECUTE PROCEDURE on_insert_post();   

-- OK
CREATE VIEW user_posts AS
    SELECT u.id AS uid, COUNT(*) AS posts_num
      FROM users u JOIN posts p ON (u.id = p.owner_id)
  GROUP BY uid;

-- OK
--CREATE TYPE threads_row(
--       id int, 
--       section_id int, 
--       owner_id int, 
--       references_ ltree, 
--       creation timestamp, 
--       modification timestamp, 
 --      noise int, 
  --     title varchar(100)
--);

--CREATE OR REPLACE FUNCTION threads() RETURNS SETOF threads_row AS '
--DECLARE
--   r threads_row%rowtype;
--   row RECORD;
--BEGIN
--   FOR row IN SELECT id, section_id, owner_id, references_, creation, modification, noise, title FROM posts LOOP
--       if row.references_ = ''::ltree||id THEN
--          r.id := row.id;
--          r.section_id := row.section_id
--          r.owner_id := row.owner_id;
--          r.references_ := row.references_;
--          r.creation := row.creation;
--          r.modification := row.modification;
--          r.noise := row.noise;
--          r.title := row.title;
--          RETURN NEXt r;
--    END LOOP;
--    RETURN;
--END;
--' LANGUAGE plpgsql;

-- OK
CREATE VIEW threads AS
    SELECT id, section_id, owner_id, references_, 
           creation, noise, title
      FROM posts
     WHERE references_ = ''::ltree || id;

-- OK
CREATE VIEW last_modified AS
    SELECT section_id AS sid, MAX(modification) as lastmod
      FROM posts 
  GROUP BY section_id;

-- OK
CREATE VIEW threads_in_section AS
    SELECT section_id AS sid, COUNT(*) AS thread_num
      FROM threads
  GROUP BY section_id;

-- OK
CREATE VIEW users_permissions_posts AS
    SELECT u.id AS uid, u.name AS name, u.login AS ulogin, 
           u.password AS upassword, u.group_id AS ugroup_id, u.email AS uemail, 
           u.homepage AS uhomepage, g.description AS gdescription, u.preferences AS upreferences,
           g.permission_level AS gpermission_level, up.posts_num AS uposts_num
      FROM groups g 
      JOIN users u ON (u.group_id = g.id) 
 LEFT JOIN user_posts up ON (u.id = up.uid);

-- OK
CREATE VIEW users_permissions AS
    SELECT u.id AS uid, u.name AS uname, u.login AS ulogin, u.preferences AS upreferences,
           u.password AS upassword, u.group_id AS ugroup_id, u.email AS uemail, 
           u.homepage AS uhomepage, g.description AS gdescription, 
           g.permission_level AS gpermission_level
      FROM groups g 
      JOIN users u ON (u.group_id = g.id);

-- OK
CREATE VIEW all_sections AS
    SELECT s.id AS sid, s.title AS stitle, s.description AS sdescription, 
           ts.thread_num AS thread_num, lm.lastmod AS lastmod, 
           s.permission_required AS spermission_required
      FROM sections s 
 LEFT JOIN last_modified lm ON (lm.sid = s.id) 
 LEFT JOIN threads_in_section ts ON (ts.sid = s.id)
  ORDER BY lastmod;

--OK
CREATE VIEW all_threads AS
    SELECT s.id AS sid, s.title AS stitle, s.description AS sdescription, t.id AS tid, t.title AS ttitle, 
           u.name AS towner, t.noise AS tnoise, t.creation AS tcreation, lmt.pmodification AS tmodification, 
           pt.posts_num AS posts_num, s.permission_required AS spermission_required
      FROM sections s, threads t, users u, posts_in_thread() pt, last_modified_in_thread() lmt
     WHERE s.id = t.section_id AND t.owner_id = u.id 
           AND pt.tid = t.id AND lmt.tid = t.id
  ORDER BY tmodification DESC;
 
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
       VALUES (1, 1, ''::ltree, '2005-01-30', '2005-01-30', 0, '1Foo', 'sticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, '1'::ltree, '2005-01-30', '2005-01-30', 0, 'Foo', '1.sticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, '1.2'::ltree, '2005-01-30', '2005-01-30', 0, 'Foo', '1.2sticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, '1.2'::ltree, '2005-01-30', '2005-01-30', 0, 'Foo', '1..sticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, ''::ltree, '2005-01-30', '2005-01-30', 0, '2Foo', 'BBsticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, '5'::ltree, '2005-01-30', '2005-01-30', 0, 'Foo', '5.sticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, '5.6'::ltree, '2005-01-30', '2005-01-30', 0, 'Foo', '5.6sticaz', 'sticaz');

INSERT INTO posts (section_id, owner_id, references_, creation, 
                  modification, noise, title, body, parsed_body)
       VALUES (1, 1, ''::ltree, '2005-01-30', '2005-01-30', 0, '3Foo', 'BBsticaz', 'sticaz');

SELECT reply(2, 1, '2005-02-01', '2005-02-01', 'Too', '1.234.234sticazz', '2342sticazzazz');
