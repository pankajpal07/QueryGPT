-- DROP SCHEMA bonga_um;

CREATE SCHEMA bonga_um AUTHORIZATION pg_database_owner;

-- Drop table

-- DROP TABLE add_date;

CREATE TABLE add_date (
	"date" date NULL,
	id bigserial NOT NULL,
	user_id int8 NULL,
	CONSTRAINT add_date_pkey PRIMARY KEY (id)
);

-- Drop table

-- DROP TABLE add_email;

CREATE TABLE add_email (
	created_on timestamp(6) NULL,
	id bigserial NOT NULL,
	user_id int8 NULL,
	email varchar(1024) NULL,
	CONSTRAINT add_email_pkey PRIMARY KEY (id)
);

-- Drop table

-- DROP TABLE address;

CREATE TABLE address (
	is_active bool NOT NULL,
	is_deleted bool NOT NULL,
	country_id int8 NULL,
	created_on timestamp(6) NULL,
	id bigserial NOT NULL,
	updated_on timestamp(6) NULL,
	user_id int8 NULL,
	address varchar(1024) NULL,
	constituency varchar(1024) NULL,
	county varchar(1024) NULL,
	region varchar(1024) NULL,
	village varchar(1024) NULL,
	ward varchar(1024) NULL,
	CONSTRAINT address_pkey PRIMARY KEY (id),
	CONSTRAINT fk6i66ijb8twgcqtetl8eeeed6v FOREIGN KEY (user_id) REFERENCES users(id),
	CONSTRAINT fke54x81nmccsk5569hsjg1a6ka FOREIGN KEY (country_id) REFERENCES country(id)
);

-- Drop table

-- DROP TABLE company;

CREATE TABLE company (
	is_active bool NOT NULL,
	is_deleted bool NOT NULL,
	admin_user_id int8 NOT NULL,
	created_on timestamp(6) NULL,
	id bigserial NOT NULL,
	updated_on timestamp(6) NULL,
	address varchar(1024) NULL,
	color_preference1 varchar(1024) NULL,
	color_preference2 varchar(1024) NULL,
	company_email varchar(1024) NOT NULL,
	constituency varchar(1024) NULL,
	country_code varchar(1024) NULL,
	country_flag varchar(1024) NULL,
	country_name varchar(1024) NULL,
	county varchar(1024) NULL,
	logo varchar(1024) NULL,
	mobile varchar(1024) NOT NULL,
	"name" varchar(1024) NOT NULL,
	"number" varchar(1024) NOT NULL,
	region varchar(1024) NULL,
	schema_name varchar(1024) NOT NULL,
	village varchar(1024) NULL,
	ward varchar(1024) NULL,
	address_id int8 NULL,
	CONSTRAINT company_company_email_key UNIQUE (company_email),
	CONSTRAINT company_number_key UNIQUE (number),
	CONSTRAINT company_pkey PRIMARY KEY (id),
	CONSTRAINT company_schema_name_key UNIQUE (schema_name),
	CONSTRAINT fk2gbmtmr9ymh80ok5qcfbk67uq FOREIGN KEY (admin_user_id) REFERENCES users(id),
	CONSTRAINT fkgfifm4874ce6mecwj54wdb3ma FOREIGN KEY (address_id) REFERENCES address(id)
);

-- Drop table

-- DROP TABLE country;

CREATE TABLE country (
	is_active bool NOT NULL,
	is_deleted bool NOT NULL,
	created_on timestamp(6) NULL,
	id bigserial NOT NULL,
	updated_on timestamp(6) NULL,
	code varchar(1024) NULL,
	flag varchar(1024) NULL,
	"name" varchar(1024) NULL,
	CONSTRAINT country_pkey PRIMARY KEY (id)
);

-- Drop table

-- DROP TABLE file;

CREATE TABLE file (
	id bigserial NOT NULL,
	user_id int8 NULL,
	img_url text NULL,
	CONSTRAINT file_pkey PRIMARY KEY (id),
	CONSTRAINT fke70ql3orpo0ghvfmqccv27ng FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Drop table

-- DROP TABLE jwt_session;

CREATE TABLE jwt_session (
	is_active bool NOT NULL,
	is_deleted bool NOT NULL,
	created_on timestamp(6) NULL,
	expiry timestamp(6) NULL,
	id bigserial NOT NULL,
	updated_on timestamp(6) NULL,
	user_id int8 NULL,
	"token" varchar(1024) NULL,
	CONSTRAINT jwt_session_pkey PRIMARY KEY (id),
	CONSTRAINT fkahvibmqkh4irq44vusgyds699 FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Drop table

-- DROP TABLE logs_history;

CREATE TABLE logs_history (
	is_active bool NOT NULL,
	is_deleted bool NOT NULL,
	created_on timestamp(6) NULL,
	entity_id int8 NULL,
	id bigserial NOT NULL,
	updated_on timestamp(6) NULL,
	user_id int8 NULL,
	entity_name varchar(1024) NULL,
	logs varchar(1024) NULL,
	voucher_number varchar(1024) NULL,
	new_json varchar(100000) NULL,
	old_json varchar(100000) NULL,
	event_name varchar(255) NULL,
	CONSTRAINT logs_history_event_name_check CHECK (((event_name)::text = ANY ((ARRAY['CREATED'::character varying, 'DELETED'::character varying, 'UPDATED'::character varying, 'IMPORTED'::character varying, 'EXPORTED'::character varying, 'LOGIN'::character varying, 'LOGOUT'::character varying])::text[]))),
	CONSTRAINT logs_history_pkey PRIMARY KEY (id),
	CONSTRAINT fkjy5c48jfrmghygtpu0eq4x9do FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Drop table

-- DROP TABLE otp;

CREATE TABLE otp (
	code_send_time timestamp(6) NOT NULL,
	id bigserial NOT NULL,
	user_id int8 NULL,
	email_code varchar(255) NULL,
	mobile_code varchar(255) NULL,
	created_on timestamp(6) NULL,
	updated_on timestamp(6) NULL,
	is_active bool DEFAULT false NOT NULL,
	is_deleted bool DEFAULT false NOT NULL,
	CONSTRAINT otp_pkey PRIMARY KEY (id),
	CONSTRAINT fks0hlsjury48cekfbfusk11lyr FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Drop table

-- DROP TABLE "permission";

CREATE TABLE "permission" (
	is_active bool NOT NULL,
	is_deleted bool NOT NULL,
	created_on timestamp(6) NULL,
	id bigserial NOT NULL,
	updated_on timestamp(6) NULL,
	"action" varchar(1024) NULL,
	CONSTRAINT permission_pkey PRIMARY KEY (id)
);

-- Drop table

-- DROP TABLE "role";

CREATE TABLE "role" (
	is_active bool NOT NULL,
	is_deleted bool NOT NULL,
	created_on timestamp(6) NULL,
	id bigserial NOT NULL,
	updated_on timestamp(6) NULL,
	"name" varchar(1024) NULL,
	CONSTRAINT role_pkey PRIMARY KEY (id)
);

-- Drop table

-- DROP TABLE "token";

CREATE TABLE "token" (
	expired bool NOT NULL,
	is_valid bool NOT NULL,
	revoked bool NOT NULL,
	id int8 NOT NULL,
	user_id int8 NULL,
	"token" varchar(255) NULL,
	token_type varchar(255) NULL,
	CONSTRAINT token_pkey PRIMARY KEY (id),
	CONSTRAINT token_token_key UNIQUE (token),
	CONSTRAINT token_token_type_check CHECK (((token_type)::text = 'BEARER'::text)),
	CONSTRAINT fkj8rfw4x0wjjyibfqq566j4qng FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Drop table

-- DROP TABLE user_info;

CREATE TABLE user_info (
	id bigserial NOT NULL,
	user_id int8 NULL,
	mobile varchar(1024) NULL,
	CONSTRAINT user_info_pkey PRIMARY KEY (id)
);

-- Drop table

-- DROP TABLE user_reset_token;

CREATE TABLE user_reset_token (
	already_used bool NOT NULL,
	is_active bool NOT NULL,
	is_deleted bool NOT NULL,
	created_on timestamp(6) NULL,
	id bigserial NOT NULL,
	updated_on timestamp(6) NULL,
	user_id int8 NULL,
	otp varchar(1024) NULL,
	CONSTRAINT user_reset_token_pkey PRIMARY KEY (id),
	CONSTRAINT fkageial0ievk4u4seividgvnrg FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Drop table

-- DROP TABLE user_role_mapping;

CREATE TABLE user_role_mapping (
	user_id int8 NOT NULL,
	role_id int8 NOT NULL,
	CONSTRAINT user_role_mapping_pkey PRIMARY KEY (user_id, role_id),
	CONSTRAINT fk3y767mrjaru6vl6ctdaaw7os9 FOREIGN KEY (user_id) REFERENCES users(id),
	CONSTRAINT fkivsrdkkmm4e9k19vgaat9upp2 FOREIGN KEY (role_id) REFERENCES "role"(id)
);

-- Drop table

-- DROP TABLE users;

CREATE TABLE users (
	"date" date NULL,
	is_2fa_enabled bool NULL,
	is_active bool NOT NULL,
	is_deleted bool NOT NULL,
	is_email_verified bool NULL,
	is_organization bool NULL,
	company_id int8 NULL,
	created_on timestamp(6) NULL,
	id bigserial NOT NULL,
	updated_on timestamp(6) NULL,
	lang_key varchar(10) NULL,
	first_name varchar(1024) NULL,
	last_name varchar(1024) NULL,
	middle_name varchar(1024) NULL,
	mobile varchar(1024) NULL,
	email varchar(255) NOT NULL,
	"password" varchar(255) NULL,
	"role" varchar(255) NULL,
	salutation varchar(255) NULL,
	secret_key2fa varchar(255) NULL,
	sex varchar(255) NULL,
	status varchar(255) NULL,
	username varchar(255) NULL,
	is_learning_service bool NULL,
	is_sms_service bool NULL,
	CONSTRAINT uk6dotkott2kjsp8vw4d0m25fb7 UNIQUE (email),
	CONSTRAINT users_email_key UNIQUE (email),
	CONSTRAINT users_pkey PRIMARY KEY (id),
	CONSTRAINT users_role_check CHECK (((role)::text = ANY ((ARRAY['USER'::character varying, 'ADMIN'::character varying])::text[]))),
	CONSTRAINT users_sex_check CHECK (((sex)::text = ANY ((ARRAY['MALE'::character varying, 'FEMALE'::character varying, 'RATHER_NOT_SAY'::character varying])::text[]))),
	CONSTRAINT fkbwv4uspmyi7xqjwcrgxow361t FOREIGN KEY (company_id) REFERENCES company(id)
);