-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-v_hx_family_journal.sql,v 1.1 2008-09-02 15:41:20 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop view clin.v_hx_family_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_hx_family_journal as
select
	vhxf.pk_patient
		as pk_patient,
	vhxf.modified_when
		as modified_when,
	vhxf.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = vhxf.modified_by),
		'<' || vhxf.modified_by || '>'
	)
		as modified_by,
	vhxf.soap_cat
		as soap_cat,
	_('Family Hx') || ': '
		|| _(vhxf.relationship) || ' '
		|| vhxf.name_relative || ' @ '
		|| vhxf.age_noted || ': '
		|| vhxf.condition || ';'
		as narrative,
	vhxf.pk_encounter
		as pk_encounter,
	vhxf.pk_episode
		as pk_episode,
	vhxf.pk_health_issue
		as pk_health_issue,
	vhxf.pk_hx_family_item
		as src_pk,
	'clin.hx_family_item'::text
		as src_table
from
	clin.v_hx_family vhxf
;


grant select on clin.v_hx_family_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_hx_family_journal.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-v_hx_family_journal.sql,v $
-- Revision 1.1  2008-09-02 15:41:20  ncq
-- - new
--
--