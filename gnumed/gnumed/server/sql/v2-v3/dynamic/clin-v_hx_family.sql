-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: 
-- 
-- ==============================================================
-- $Id: clin-v_hx_family.sql,v 1.1 2006-12-11 16:59:47 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop view clin.v_hx_family cascade;
\set ON_ERROR_STOP 1


create view clin.v_hx_family as
-- those not linked to another patient as relative
select
	vpi.pk_patient as pk_patient,
	vpi.pk_health_issue as pk_health_issue,

	chxf.clin_when as clin_when,
	chxf.modified_when as modified_when,
	chxf.modified_by as modified_by,
	chxf.fk_encounter as pk_encounter,
	chxf.fk_episode as pk_episode,
	chxf.narrative as relationship,
	chxf.soap_cat as soap_cat,
	chxf.pk as pk_clin_hx_family,
	chxf.fk_hx_family_item as pk_hx_family_item,

	null::integer as pk_narrative_condition,
	null::integer as pk_relative_identity,
	hxfi.name_relative as name_relative,
	hxfi.dob_relative as dob_relative,
	hxfi.condition as condition,
	hxfi.age_noted as age_noted,
	hxfi.age_of_death as age_of_death,
	hxfi.is_cause_of_death as is_cause_of_death
from
	clin.v_pat_items vpi,
	clin.clin_hx_family chxf,
	clin.hx_family_item hxfi
where
	vpi.pk_item = chxf.pk_item
		and
	hxfi.pk = chxf.fk_hx_family_item
		and
	hxfi.fk_narrative_condition is null
		and
	hxfi.fk_relative is null

UNION

-- those linked to another patient as relative
select
	vpi.pk_patient as pk_patient,
	vpi.pk_health_issue as pk_health_issue,

	chxf.clin_when as clin_when,
	chxf.modified_when as modified_when,
	chxf.modified_by as modified_by,
	chxf.fk_encounter as pk_encounter,
	chxf.fk_episode as pk_episode,
	chxf.narrative as relationship,
	chxf.soap_cat as soap_cat,
	chxf.pk as pk_clin_hx_family,
	chxf.fk_hx_family_item as pk_hx_family_item,

	null::integer as pk_narrative_condition,
	hxfi.fk_relative as pk_relative_identity,
	vbp.firstnames || ' ' || vbp.lastnames as name_relative,
	vbp.dob as dob_relative,
	hxfi.condition as condition,
	hxfi.age_noted as age_noted,
	hxfi.age_of_death as age_of_death,
	hxfi.is_cause_of_death as is_cause_of_death
from
	clin.v_pat_items vpi,
	clin.clin_hx_family chxf,
	clin.hx_family_item hxfi,
	dem.v_basic_person vbp
where
	vpi.pk_item = chxf.pk_item
		and
	hxfi.pk = chxf.fk_hx_family_item
		and
	hxfi.fk_narrative_condition is null
		and
	hxfi.fk_relative = vbp.pk_identity

UNION

-- those linked to a condition of another patient being a relative
select
	vpn.pk_patient as pk_patient,
	vpn.pk_health_issue as pk_health_issue,

	chxf.clin_when as clin_when,
	chxf.modified_when as modified_when,
	chxf.modified_by as modified_by,
	chxf.fk_encounter as pk_encounter,
	chxf.fk_episode as pk_episode,
	chxf.narrative as relationship,
	chxf.soap_cat as soap_cat,
	chxf.pk as pk_clin_hx_family,
	chxf.fk_hx_family_item as pk_hx_family_item,

	hxfi.fk_narrative_condition as pk_narrative_condition,
	vpn.pk_patient as pk_relative_identity,
	vbp.firstnames || ' ' || vbp.lastnames as name_relative,
	vbp.dob as dob_relative,
	vpn.narrative as condition,
	hxfi.age_noted as age_noted,
	hxfi.age_of_death as age_of_death,
	hxfi.is_cause_of_death as is_cause_of_death
from
	clin.clin_hx_family chxf,
	clin.hx_family_item hxfi,
	dem.v_basic_person vbp,
	clin.v_pat_narrative vpn
where
	hxfi.pk = chxf.fk_hx_family_item
		and
	hxfi.fk_narrative_condition = vpn.pk_narrative
		and
	hxfi.fk_relative is null
		and
	vbp.pk_identity = vpn.pk_patient
;


comment on view clin.v_hx_family is
	'family history denormalized';

-- --------------------------------------------------------------
-- don't forget appropriate grants
grant select on clin.v_hx_family to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-v_hx_family.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-v_hx_family.sql,v $
-- Revision 1.1  2006-12-11 16:59:47  ncq
-- - use dem.v_staff -> dem.staff in provider resolution
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
