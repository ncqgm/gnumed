-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v6
-- Target database version: v7
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_pat_allergies cascade;


create view clin.v_pat_allergies as

select
	a.pk as pk_allergy,
	(select fk_patient from clin.encounter where pk = a.fk_encounter) as pk_patient,
	a.soap_cat as soap_cat,
	case when coalesce(trim(both from a.allergene), '') = ''
		then a.substance
		else a.allergene
	end as descriptor,
	a.allergene as allergene,
	a.substance as substance,
	a.substance_code as substance_code,
	a.generics as generics,
	a.generic_specific as generic_specific,
	a.atc_code as atc_code,
	at.value as type,
	_(at.value) as l10n_type,
	a.definite as definite,
	a.narrative as reaction,
	a.fk_type as pk_type,
	a.pk_item as pk_item,
	a.clin_when as date,
	(select fk_health_issue from clin.episode where pk = a.fk_episode)
		as pk_health_issue,
	a.fk_episode as pk_episode,
	a.fk_encounter as pk_encounter,
	a.modified_when as modified_when,
	a.modified_by as modified_by,
	a.xmin as xmin_allergy
from
	clin.allergy a,
	clin._enum_allergy_type at
where
	at.pk = a.fk_type
;


comment on view clin.v_pat_allergies is
	'denormalizes clin.allergy';


grant select on clin.v_pat_allergies to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_pat_allergies.sql,v $', '$Revision: 1.1 $');
