-- ===================================================
-- GnuMed configuration views

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmConfigViews.sql,v $
-- $Revision: 1.7 $
-- ======================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ======================================================
-- cfg.distributed_db
COMMENT ON TABLE cfg.distributed_db IS
	'Enumerate all known GNUmed service names.
	 Naming new services needs approval by GNUmed administrators !

	I18N note to translators: do NOT change these values !!!

	services:
		default: GNUmed configuration
		personalia: person/address related tables (demographic and identity data)
		historica: contains medical data
		pharmaceutica: pharmaceutical information (drugref.org, mainly)
		reference: "external", "read-only" information such as coding
		           and patient education material
		blobs: large binary objects
		administrivia: administrative data for the practice: forms
		               queue, roster, waiting room, billing etc.
	';

-- cfg.config --
COMMENT ON TABLE cfg.config IS
	'maps a service name to a database location
	 for a particular user, includes user
	 credentials for that database';

COMMENT ON COLUMN cfg.config.profile IS
	'allows multiple profiles per user/
	 pseudo user, one user may have different
	 configuration profiles depending on role,
	 need and location';
COMMENT ON COLUMN cfg.config.username IS
	'user name as used within the GNUmed system';
COMMENT ON COLUMN cfg.config.ddb IS
	'which GNUmed service are we mapping to a database here';
COMMENT ON COLUMN cfg.config.db IS
	'how to reach the database host for this service';
COMMENT ON COLUMN cfg.config.crypt_pwd IS
	'password for user and database, encrypted';
COMMENT ON COLUMN cfg.config.crypt_algo IS
	'encryption algorithm used for password encryption';
COMMENT ON COLUMN cfg.config.pwd_hash IS
	'hash of the unencrypted password';
COMMENT ON COLUMN cfg.config.hash_algo IS
	'algorithm used for password hashing';

-- cfg.db --
COMMENT ON TABLE cfg.db IS
	'information on where to find the databases known to GnuMed';

comment on column cfg.db.id is
	'the database with id == 0 is the "default" database';
COMMENT ON COLUMN cfg.db.name IS
	'name of the database';
COMMENT ON COLUMN cfg.db.port IS
	'port number of the server hosting the database';
COMMENT ON COLUMN cfg.db.host IS
	'host name or IP number of the server hosting the database';

-- cfg.cfg_type_enum --
comment on table cfg.cfg_type_enum is
	'enumeration of config option data types';

-- cfg.cfg_template --
comment on table cfg.cfg_template is
	'meta definition of config items';
comment on column cfg.cfg_template.name is
	'the name of the option; this MUST be set to something meaningful';
comment on column cfg.cfg_template.type is
	'type of the value';
comment on column cfg.cfg_template.cfg_group is
	'just for logical grouping of options according to task sets to facilitate better config management';
comment on column cfg.cfg_template.description is
	'arbitrary description (user visible)';

-- cfg.cfg_item --
comment on table cfg.cfg_item is
	'this table holds all "instances" of cfg.cfg_template';
comment on column cfg.cfg_item.fk_template is
	'this points to the class of this option, think of this as a base object, this also defines the data type';
comment on column cfg.cfg_item.owner is
	'the database level user this option belongs to; this
	 is the "role" of the user from the perspective of
	 the database; can be "default" at the application
	 level to indicate that it does not care';
comment on column cfg.cfg_item.workplace is
	'- the logical workplace this option pertains to
	 - can be a hostname but should be a logical rather
	   than a physical identifier as machines get moved,
	   workplaces do not, kind of like a "role" for the
	   machine
	 - associate this with a physical workplace through
	   a local config file or environment variable';
comment on column cfg.cfg_item.cookie is
	'an arbitrary, opaque entity the client code can use
	 to associate this config item with even finer grained
	 context; could be the pertinent patient ID for patient
	 specific options';

-- cfg.cfg_data
comment on table cfg.cfg_data is
	'stores opaque configuration data, either text or binary,
	 note that it will be difficult to share such options
	 among different types of clients';

-- ======================================================
\unset ON_ERROR_STOP
drop view cfg.v_cfg_options;
\set ON_ERROR_STOP 1

create view cfg.v_cfg_options as
select
	cfg_t.name as option,
	cfg_t.description as description,
	cfg_i.owner as owner,
	cfg_i.workplace as workplace,
	cfg_i.cookie as cookie,
	cfg_t.type as type,
	cfg_t.cfg_group as group,
	cfg_t.pk as pk_cfg_template,
	cfg_i.pk as pk_cfg_item
from
	cfg.cfg_template cfg_t,
	cfg.cfg_item cfg_i
where
	cfg_i.fk_template = cfg_t.pk
;

-- ======================================================
\unset ON_ERROR_STOP
drop view cfg.v_cfg_opts_numeric;
\set ON_ERROR_STOP 1

create view cfg.v_cfg_opts_numeric as
select
	cfg_t.name as option,
	cfg_v.value as value,
	cfg_t.description as description,
	cfg_i.owner as owner,
	cfg_i.workplace as workplace,
	cfg_i.cookie as cookie,
	cfg_t.cfg_group as group,
	cfg_t.pk as pk_cfg_template,
	cfg_i.pk as pk_cfg_item
from
	cfg.cfg_template cfg_t,
	cfg.cfg_item cfg_i,
	cfg.cfg_numeric cfg_v
where
	cfg_i.fk_template = cfg_t.pk
		and
	cfg_v.fk_item = cfg_i.pk
;

-- ======================================================
\unset ON_ERROR_STOP
drop view cfg.v_cfg_opts_string;
\set ON_ERROR_STOP 1

create view cfg.v_cfg_opts_string as
select
	cfg_t.name as option,
	cfg_v.value as value,
	cfg_t.description as description,
	cfg_i.owner as owner,
	cfg_i.workplace as workplace,
	cfg_i.cookie as cookie,
	cfg_t.cfg_group as group,
	cfg_t.pk as pk_cfg_template,
	cfg_i.pk as pk_cfg_item
from
	cfg.cfg_template cfg_t,
	cfg.cfg_item cfg_i,
	cfg.cfg_string cfg_v
where
	cfg_i.fk_template = cfg_t.pk
		and
	cfg_v.fk_item = cfg_i.pk
;

-- ======================================================
\unset ON_ERROR_STOP
drop view cfg.v_cfg_opts_str_array;
\set ON_ERROR_STOP 1

create view cfg.v_cfg_opts_str_array as
select
	cfg_t.name as option,
	cfg_v.value as value,
	cfg_t.description as description,
	cfg_i.owner as owner,
	cfg_i.workplace as workplace,
	cfg_i.cookie as cookie,
	cfg_t.cfg_group as group,
	cfg_t.pk as pk_cfg_template,
	cfg_i.pk as pk_cfg_item
from
	cfg.cfg_template cfg_t,
	cfg.cfg_item cfg_i,
	cfg.cfg_str_array cfg_v
where
	cfg_i.fk_template = cfg_t.pk
		and
	cfg_v.fk_item = cfg_i.pk
;

-- ======================================================
\unset ON_ERROR_STOP
drop view cfg.v_cfg_opts_data;
\set ON_ERROR_STOP 1

create view cfg.v_cfg_opts_data as
select
	cfg_t.name as option,
	cfg_v.value as value,
	cfg_t.description as description,
	cfg_i.owner as owner,
	cfg_i.workplace as workplace,
	cfg_i.cookie as cookie,
	cfg_t.cfg_group as group,
	cfg_t.pk as pk_cfg_template,
	cfg_i.pk as pk_cfg_item
from
	cfg.cfg_template cfg_t,
	cfg.cfg_item cfg_i,
	cfg.cfg_data cfg_v
where
	cfg_i.fk_template = cfg_t.pk
		and
	cfg_v.fk_item = cfg_i.pk
;

-- ======================================================
-- schema
grant usage on schema cfg to group "gm-doctors";

GRANT SELECT ON
	cfg.db
	, cfg.distributed_db
	, cfg.config
	, cfg.cfg_type_enum
	, cfg.cfg_template
	, cfg.cfg_item
	, cfg.cfg_string
	, cfg.cfg_str_array
	, cfg.cfg_numeric
	, cfg.cfg_data
	, cfg.v_cfg_options
	, cfg.v_cfg_opts_numeric
	, cfg.v_cfg_opts_string
	, cfg.v_cfg_opts_str_array
	, cfg.v_cfg_opts_data
TO GROUP "gm-public";

GRANT select, insert, update, delete on
	cfg.cfg_type_enum
	, cfg.cfg_template
	, cfg.cfg_template_pk_seq
	, cfg.cfg_item
	, cfg.cfg_item_pk_seq
	, cfg.cfg_string
	, cfg.cfg_str_array
	, cfg.cfg_numeric
	, cfg.cfg_data
to group "gm-doctors";
-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmConfigViews.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmConfigViews.sql,v $', '$Revision: 1.7 $');

--=====================================================================
-- $Log: gmConfigViews.sql,v $
-- Revision 1.7  2005-11-18 15:40:13  ncq
-- - add lots of rerunnable things from gmconfiguration.sql
-- - create adjusted views in cfg.* schema
-- - adjust grants/include schema grants
--
-- Revision 1.6  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.5  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.4  2005/01/10 11:53:28  ncq
-- - add missing grant
--
-- Revision 1.3  2005/01/09 19:52:52  ncq
-- - include cfg_data in v_cfg_opts_data
-- - add grants
--
-- Revision 1.2  2004/09/06 22:15:45  ncq
-- - add v_cfg_opts_numeric/string/str_array + grants
--
-- Revision 1.1  2004/09/02 00:42:33  ncq
-- - add v_cfg_options
-- - move grants to volatile DDL file
--
