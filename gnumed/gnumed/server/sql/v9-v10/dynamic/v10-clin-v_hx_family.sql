-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-v_hx_family.sql,v 1.1 2008-09-02 15:41:19 ncq Exp $
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
	vbp.firstnames || ' ' || vbp.lastnames as name_relative,
	vbp.dob as dob_relative,
	hxfi.condition as condition,
	hxfi.age_noted as age_noted,
	hxfi.age_of_death as age_of_death,
	hxfi.is_cause_of_death as is_cause_of_death
from
	clin.clin_hx_family chxf,
	clin.hx_family_item hxfi,
	dem.v_basic_person vbp
where
	hxfi.pk = chxf.fk_hx_family_item
		and
	hxfi.fk_narrative_condition is null
		and
	hxfi.fk_relative = vbp.pk_identity

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
	vbp.firstnames || ' ' || vbp.lastnames as name_relative,
	vbp.dob as dob_relative,
	(select clin.clin_narrative.narrative from clin.clin_narrative where pk = fk_narrative_condition) as condition,
	hxfi.age_noted as age_noted,
	hxfi.age_of_death as age_of_death,
	hxfi.is_cause_of_death as is_cause_of_death
from
	clin.clin_hx_family chxf,
	clin.hx_family_item hxfi,
	dem.v_basic_person vbp
where
	hxfi.pk = chxf.fk_hx_family_item
		and
	hxfi.fk_relative is null
		and
	vbp.pk_identity = hxfi.fk_relative
;


comment on view clin.v_hx_family is
	'family history denormalized';

-- --------------------------------------------------------------
-- don't forget appropriate grants
grant select on clin.v_hx_family to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_hx_family.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-v_hx_family.sql,v $
-- Revision 1.1  2008-09-02 15:41:19  ncq
-- - new
--
--