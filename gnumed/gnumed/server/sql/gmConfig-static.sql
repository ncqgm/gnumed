--=====================================================================
-- GNUmed distributed database configuration tables

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmConfig-static.sql,v $
-- $Revision: 1.2 $

-- structure of configuration database for GNUmed
-- neccessary to allow for distributed servers

-- Copyright by Dr. Horst Herb
-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org

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
-- $Log: gmConfig-static.sql,v $
-- Revision 1.2  2005-12-27 19:11:54  ncq
-- - add comment on cfg. schema
-- - add cfg.db_logon_banner
--
-- Revision 1.1  2005/11/18 15:51:30  ncq
-- - better naming
--
-- Revision 1.38  2005/11/18 15:36:28  ncq
-- - cleanup, some id -> pk and foreign keys to fk_*
-- - now store objects in schema cfg.
-- - factor out reloadable DDL
--
-- Revision 1.37  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.36  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.35  2005/03/01 20:38:19  ncq
-- - varchar -> text
--
-- Revision 1.34  2005/01/09 19:51:24  ncq
-- - cleanup, improved docs
-- - add cfg_data to store arbitrary binary config data
--
-- Revision 1.33  2004/09/06 22:15:07  ncq
-- - tighten constraints in cfg_item
--
-- Revision 1.32  2004/09/02 00:42:33  ncq
-- - add v_cfg_options
-- - move grants to volatile DDL file
--
-- Revision 1.31  2004/07/19 11:50:43  ncq
-- - cfg: what used to be called "machine" really is "workplace", so fix
--
-- Revision 1.30  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.29  2004/03/10 00:06:20  ncq
-- - remove stale service defs
--
-- Revision 1.28  2004/01/06 23:44:40  ncq
-- - __default__ -> xxxDEFAULTxxx
--
-- Revision 1.27  2003/10/27 13:54:05  ncq
-- - cleanup
--
-- Revision 1.26  2003/10/26 23:02:22  hinnef
-- - changed config param name length to 80
--
-- Revision 1.25  2003/07/27 22:01:48  ncq
-- - comment out unused service names
--
-- Revision 1.24  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.23  2003/02/04 12:22:53  ncq
-- - valid until in create user cannot do a sub-query :-(
-- - columns "owner" should really be of type "name" if defaulting to "CURRENT_USER"
-- - new functions set_curr_lang(*)
--
-- Revision 1.22  2003/01/05 13:05:51  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.21  2003/01/05 10:07:15  ncq
-- - default "__default__"
-- - adjusted ACLs
--
-- Revision 1.20  2002/12/26 15:44:42  ncq
-- - added string array
--
-- Revision 1.19  2002/12/01 13:53:09  ncq
-- - missing ; at end of schema tracking line
--
-- Revision 1.18  2002/11/28 11:53:44  ncq
-- - added client configuration tables to work with database config library
-- - adjusted ACLs
--
-- Revision 1.17  2002/11/16 01:03:20  ncq
-- - add simple revision tracking
--
-- Revision 1.16  2002/11/12 17:04:10  ncq
-- - remove a ; in a '' since this currently foo-bars bootstrapping
--
-- Revision 1.15  2002/11/01 16:53:27  ncq
-- - still errors in here, darn it !
--
-- Revision 1.14  2002/11/01 16:35:38  ncq
-- - still some grant errors lurking
--
-- Revision 1.13  2002/11/01 16:11:07  ncq
-- - fixed grants, comments, quoting
--
-- Revision 1.12  2002/10/29 23:08:08  ncq
-- - some cleanup
-- - started work on GnuMed user/group ACL structure
--
-- Revision 1.11  2002/09/27 00:35:03  ncq
-- - janitorial work
-- - comments for clarification

-- last changes: 26.10.2001 hherb drastic simplification of entities and relationships
-- introduction of the new services
