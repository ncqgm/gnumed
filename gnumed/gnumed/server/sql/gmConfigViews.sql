-- ===================================================
-- GnuMed configuration views

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmConfigViews.sql,v $
-- $Revision: 1.1 $
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
--	case
--		when cfg_t.type = 'numeric'
--			then (select cfg_n.value::text from cfg_numeric cfg_n where cfg_n.id_item=cfg_i.id)
--		when cfg_t.type = 'string'
--			then (select cfg_s.value::text from cfg_string cfg_s where cfg_s.id_item=cfg_i.id)
--		when cfg_t.type = 'str_array'
--			then (select cfg_sa.value::text from cfg_str_array cfg_sa where cfg_sa.id_item=cfg_i.id)
--		else 'missing'::text
--	end as value,
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
GRANT SELECT ON
	db,
	distributed_db,
	config,
	cfg_type_enum,
	cfg_template,
	cfg_item,
	cfg_string,
	cfg_str_array,
	cfg_numeric
	, v_cfg_options
TO GROUP "gm-public";

GRANT select, insert, update, delete on
	cfg_type_enum,
	cfg_template,
	cfg_template_id_seq,
	cfg_item,
	cfg_item_id_seq,
	cfg_string,
	cfg_str_array,
	cfg_numeric
	, v_cfg_options
to group "gm-doctors";
-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmConfigViews.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmConfigViews.sql,v $', '$Revision: 1.1 $');

--=====================================================================
-- $Log: gmConfigViews.sql,v $
-- Revision 1.1  2004-09-02 00:42:33  ncq
-- - add v_cfg_options
-- - move grants to volatile DDL file
--
