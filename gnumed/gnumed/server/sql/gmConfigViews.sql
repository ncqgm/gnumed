-- ===================================================
-- GnuMed configuration views

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmConfigViews.sql,v $
-- $Revision: 1.6 $
-- ======================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ======================================================
\unset ON_ERROR_STOP
drop view v_cfg_options;
\set ON_ERROR_STOP 1

create view v_cfg_options as
select
	cfg_t.name as option,
	cfg_t.description as description,
	cfg_i.owner as owner,
	cfg_i.workplace as workplace,
	cfg_i.cookie as cookie,
	cfg_t.type as type,
	cfg_t.cfg_group as group,
	cfg_t.id as pk_cfg_template,
	cfg_i.id as pk_cfg_item
from
	cfg_template cfg_t,
	cfg_item cfg_i
where
	cfg_i.id_template = cfg_t.id
;

-- ======================================================
\unset ON_ERROR_STOP
drop view v_cfg_opts_numeric;
\set ON_ERROR_STOP 1

create view v_cfg_opts_numeric as
select
	cfg_t.name as option,
	cfg_v.value as value,
	cfg_t.description as description,
	cfg_i.owner as owner,
	cfg_i.workplace as workplace,
	cfg_i.cookie as cookie,
	cfg_t.cfg_group as group,
	cfg_t.id as pk_cfg_template,
	cfg_i.id as pk_cfg_item
from
	cfg_template cfg_t,
	cfg_item cfg_i,
	cfg_numeric cfg_v
where
	cfg_i.id_template = cfg_t.id
		and
	cfg_v.id_item = cfg_i.id
;

-- ======================================================
\unset ON_ERROR_STOP
drop view v_cfg_opts_string;
\set ON_ERROR_STOP 1

create view v_cfg_opts_string as
select
	cfg_t.name as option,
	cfg_v.value as value,
	cfg_t.description as description,
	cfg_i.owner as owner,
	cfg_i.workplace as workplace,
	cfg_i.cookie as cookie,
	cfg_t.cfg_group as group,
	cfg_t.id as pk_cfg_template,
	cfg_i.id as pk_cfg_item
from
	cfg_template cfg_t,
	cfg_item cfg_i,
	cfg_string cfg_v
where
	cfg_i.id_template = cfg_t.id
		and
	cfg_v.id_item = cfg_i.id
;

-- ======================================================
\unset ON_ERROR_STOP
drop view v_cfg_opts_str_array;
\set ON_ERROR_STOP 1

create view v_cfg_opts_str_array as
select
	cfg_t.name as option,
	cfg_v.value as value,
	cfg_t.description as description,
	cfg_i.owner as owner,
	cfg_i.workplace as workplace,
	cfg_i.cookie as cookie,
	cfg_t.cfg_group as group,
	cfg_t.id as pk_cfg_template,
	cfg_i.id as pk_cfg_item
from
	cfg_template cfg_t,
	cfg_item cfg_i,
	cfg_str_array cfg_v
where
	cfg_i.id_template = cfg_t.id
		and
	cfg_v.id_item = cfg_i.id
;

-- ======================================================
\unset ON_ERROR_STOP
drop view v_cfg_opts_data;
\set ON_ERROR_STOP 1

create view v_cfg_opts_data as
select
	cfg_t.name as option,
	cfg_v.value as value,
	cfg_t.description as description,
	cfg_i.owner as owner,
	cfg_i.workplace as workplace,
	cfg_i.cookie as cookie,
	cfg_t.cfg_group as group,
	cfg_t.id as pk_cfg_template,
	cfg_i.id as pk_cfg_item
from
	cfg_template cfg_t,
	cfg_item cfg_i,
	cfg_data cfg_v
where
	cfg_i.id_template = cfg_t.id
		and
	cfg_v.id_item = cfg_i.id
;

-- ======================================================
GRANT SELECT ON
	db
	, distributed_db
	, config
	, cfg_type_enum
	, cfg_template
	, cfg_item
	, cfg_string
	, cfg_str_array
	, cfg_numeric
	, cfg_data
	, v_cfg_options
	, v_cfg_opts_numeric
	, v_cfg_opts_string
	, v_cfg_opts_str_array
	, v_cfg_opts_data
TO GROUP "gm-public";

GRANT select, insert, update, delete on
	cfg_type_enum
	, cfg_template
	, cfg_template_id_seq
	, cfg_item
	, cfg_item_id_seq
	, cfg_string
	, cfg_str_array
	, cfg_numeric
	, cfg_data
to group "gm-doctors";
-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmConfigViews.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmConfigViews.sql,v $', '$Revision: 1.6 $');

--=====================================================================
-- $Log: gmConfigViews.sql,v $
-- Revision 1.6  2005-09-19 16:38:51  ncq
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
