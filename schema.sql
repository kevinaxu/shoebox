DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id integer primary key autoincrement, 
    email varchar(100) not null,
    password varchar (50) not null
);

DROP TABLE IF EXISTS files; 
CREATE TABLE files (
    user_id integer not null, 
    files text
);

-- oauth_tokens? 
-- DROP TABLE IF EXISTS api_keys; 
-- CREATE TABLE api_keys (
    -- api_key_id integer primary key autoincrement,
    -- user_id integer not null, 
    -- api_key varchar(32) not null, 
    -- platform varchar(100) not null,
-- );

