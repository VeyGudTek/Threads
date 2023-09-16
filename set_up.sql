CREATE TABLE users (
    username VARCHAR(30) NOT NULL PRIMARY KEY,
    password VARCHAR(200) NOT NULL
);

CREATE TABLE posts (
    id BIGSERIAL NOT NULL PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    body VARCHAR(1000) NOT NULL,
    date_created TIMESTAMP NOT NULL,
    author VARCHAR(30) REFERENCES users(username) NOT NULL
);

CREATE TABLE replies(
    id BIGSERIAL NOT NULL PRIMARY KEY,
    body VARCHAR(500) NOT NULL,
    author VARCHAR(30) REFERENCES users(username) NOT NULL,
    parent_id BIGINT REFERENCES replies(id),
    date_created TIMESTAMP NOT NULL
);