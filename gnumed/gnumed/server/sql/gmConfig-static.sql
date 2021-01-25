--=====================================================================
-- GNUmed distributed database configuration tables

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmConfig-static.sql,v $
-- $Revision: 1.2 $

-- structure of configuration database for GNUmed
-- necessary to allow for distributed servers

-- Copyright by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL v2 or later)
-- For details regarding GPL v2 or later licensing see http://gnu.org

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

--=====================================================================
create schema cfg authorization "gm-dbo";

comment on schema cfg is
	'This schema holds all the configuration data.';

--=====================================================================
CREATE TABLE cfg.db (
    id SERIAL PRIMARY KEY,
    name CHAR(35),
    port INT DEFAULT 5432,
    host text DEFAULT 'localhost',
    opt text DEFAULT '',
    tty text DEFAULT ''
);

--=====================================================================
CREATE TABLE cfg.distributed_db (
	id SERIAL PRIMARY KEY,
	name char(35)
);

--=====================================================
CREATE TABLE cfg.config (
    id SERIAL PRIMARY KEY,
    profile CHAR(25) DEFAULT 'default',
    username CHAR(25) DEFAULT CURRENT_USER,
    ddb INT REFERENCES cfg.distributed_db(id)
		DEFAULT NULL,
    db INT REFERENCES cfg.db(id),
    crypt_pwd text DEFAULT NULL,
    crypt_algo text DEFAULT NULL,
    pwd_hash text DEFAULT NULL,
    hash_algo text DEFAULT NULL
);

-- ======================================================
create table cfg.db_logon_banner (
	message text
		check (trim(message) != ''),
	singularizer boolean
		unique
		default true
		check (singularizer is true)
);

-- ======================================================
-- generic program options storage space
-- ======================================================
create table cfg.cfg_type_enum (
	name text
		unique
		not null
);

-- ======================================================
create table cfg.cfg_template (
	pk serial primary key,
	name text
		NOT NULL
		DEFAULT 'must set this !',
	type text
		not null
		references cfg.cfg_type_enum(name),
	cfg_group text
		not null
		default 'xxxDEFAULTxxx',
	description text
		not null
		default 'programmer is an avid Camel Book Reader'
);

-- ======================================================
create table cfg.cfg_item (
	pk SERIAL PRIMARY KEY,
	fk_template integer
		not null
		references cfg.cfg_template(pk),
	owner name
		not null
		default CURRENT_USER,
	workplace text
		not null
		default 'xxxDEFAULTxxx',
	cookie text
		not null
		default 'xxxDEFAULTxxx',
	unique (fk_template, owner, workplace, cookie)
);

-- ======================================================
create table cfg.cfg_string (
	fk_item integer
		not null
		references cfg.cfg_item(pk)
		on update cascade
		on delete cascade,
	value text not null
);

-- ======================================================
create table cfg.cfg_numeric (
	fk_item integer
		not null
		references cfg.cfg_item(pk)
		on update cascade
		on delete cascade,
	value numeric not null
);

-- ======================================================
create table cfg.cfg_str_array (
	fk_item integer
		not null
		references cfg.cfg_item(pk)
		on update cascade
		on delete cascade,
	value text[] not null
);

-- ======================================================
create table cfg.cfg_data (
	fk_item integer
		not null
		references cfg.cfg_item(pk)
		on update cascade
		on delete cascade,
	value bytea
		not null
);

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmConfig-static.sql,v $', '$Revision: 1.2 $');

--=====================================================================
