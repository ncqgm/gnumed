-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-clin-v_hx_family.sql,v 1.2 2009-07-23 16:44:42 ncq Exp $
-- $Revision: 1.2 $

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
	(select fk_patient from clin.encounter where pk = chxf.fk_encounter)
		as pk_patient,
	(select fk_health_issue from clin.episode where pk = chxf.fk_episode)
		as pk_health_issue,

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
	clin.clin_hx_family chxf,
	clin.hx_family_item hxfi
where
	hxfi.pk = chxf.fk_hx_family_item
		and
	hxfi.fk_narrative_condition is null
		and
	hxfi.fk_relative is null

UNION

-- those linked to another patient as relative
select
	(select fk_patient from clin.encounter where pk = chxf.fk_encounter)
		as pk_patient,
	(select fk_health_issue from clin.episode where pk = chxf.fk_episode)
		as pk_health_issue,

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
	--vbp.firstnames || ' ' || vbp.lastnames as name_relative,
	dn.firstnames || ' ' || dn.lastnames as name_relative,
	--vbp.dob as dob_relative,
	di.dob as dob_relative,
	hxfi.condition as condition,
	hxfi.age_noted as age_noted,
	hxfi.age_of_death as age_of_death,
	hxfi.is_cause_of_death as is_cause_of_death
from
	clin.clin_hx_family chxf,
	clin.hx_family_item hxfi,
	dem.identity as di,
	dem.names as dn
where
	hxfi.pk = chxf.fk_hx_family_item
		and
	hxfi.fk_narrative_condition is null
		and
	hxfi.fk_relative = di.pk
		and
	hxfi.fk_relative = dn.id_identity

UNION

-- those linked to a condition of another patient being a relative
select
	(select fk_patient from clin.encounter where pk = chxf.fk_encounter)
		as pk_patient,
	(select fk_health_issue from clin.episode where pk = chxf.fk_episode)
		as pk_health_issue,

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
	hxfi.fk_relative as relative_identity,
	dn.firstnames || ' ' || dn.lastnames as name_relative,
	di.dob as dob_relative,
	(select clin.clin_narrative.narrative from clin.clin_narrative where pk = fk_narrative_condition) as condition,
	hxfi.age_noted as age_noted,
	hxfi.age_of_death as age_of_death,
	hxfi.is_cause_of_death as is_cause_of_death
from
	clin.clin_hx_family chxf,
	clin.hx_family_item hxfi,
	dem.identity as di,
	dem.names as dn
where
	hxfi.pk = chxf.fk_hx_family_item
		and
	hxfi.fk_relative is null
		and
	hxfi.fk_relative = di.pk
		and
	hxfi.fk_relative = dn.id_identity
;


comment on view clin.v_hx_family is
	'family history denormalized';

-- --------------------------------------------------------------
-- don't forget appropriate grants
grant select on clin.v_hx_family to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-v_hx_family.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v11-clin-v_hx_family.sql,v $
-- Revision 1.2  2009-07-23 16:44:42  ncq
-- - cleanup
--
-- Revision 1.1  2009/07/15 12:13:35  ncq
-- - need to recreate after dem.v_basic_person
--
--