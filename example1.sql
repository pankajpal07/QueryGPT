CREATE SCHEMA bonga_um AUTHORIZATION pg_database_owner;

CREATE TABLE users (
    id bigint NOT NULL,
    name varchar(255) NOT NULL,
    email varchar(255) NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (id),
)

CREATE TABLE company (
    id bigint NOT NULL,
    name varchar(255) NOT NULL,
    address varchar(255) NOT NULL,
    admin_user_id bigint NOT NULL,
    CONSTRAINT company_pkey PRIMARY KEY (id),
    CONSTRAINT fkbwv4uspmyi7xqjwcrgxow361t FOREIGN KEY (admin_user_id) REFERENCES users(id)
)

CREATE SCHEMA bonga_cm AUTHORIZATION pg_database_owner;

CREATE TABLE contact (
    id bigint NOT NULL,
    name varchar(255) NOT NULL,
    email varchar(255) NOT NULL,
    CONSTRAINT contact_pkey PRIMARY KEY (id),
)

CREATE TABLE list (
    id bigint NOT NULL,
    name varchar(255) NOT NULL
    CONSTRAINT list_pkey PRIMARY KEY (id),
)

CREATE TABLE contact_list (
    id bigint NOT NULL,
    contact_id bigint NOT NULL,
    list_id bigint NOT NULL,
    CONSTRAINT contact_list_pkey PRIMARY KEY (id),
    CONSTRAINT uk6dotkott2kjsp8vw4d0m25fb7 FOREIGN KEY (contact_id) REFERENCES contact(id),
    CONSTRAINT sdfdsfas34df423dsdr2poi934n FOREIGN KEY (list_id) REFERENCES list(id)
)