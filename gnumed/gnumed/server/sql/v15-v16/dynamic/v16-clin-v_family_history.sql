-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_hx_family cascade;
drop view clin.v_family_history cascade;
\set ON_ERROR_STOP 1


create view clin.v_family_history as

select
	c_fh.pk
		as pk_family_history,
	cenc.fk_patient
		as pk_patient,
	c_fh.soap_cat
		as soap_cat,
	c_fhrt.description
		as relation,
	_(c_fhrt.description)
		as l10n_relation,
	c_fh.narrative
		as condition,
	c_fh.age_noted
		as age_noted,
	c_fh.age_of_death
		as age_of_death,
	c_fh.contributed_to_death
		as contributed_to_death,
	c_fh.comment
		as comment,
	cep.description
		as episode,

	c_fh.clin_when
		as when_known_to_patient,
	c_fh.name_relative
		as name_relative,
	c_fh.dob_relative
		as dob_relative,
	c_fhrt.is_genetic
		as is_genetic_relative,

	c_fh.fk_encounter
		as pk_encounter,
	c_fh.fk_episode
		as pk_episode,
	cep.fk_health_issue
		as pk_health_issue,
	c_fhrt.pk
		as pk_fhx_relation_type,

	c_fh.modified_when
		as modified_when,
	coalesce (
		(select array_agg(c_lc2fhx.fk_generic_code) from clin.lnk_code2fhx c_lc2fhx where c_lc2fhx.fk_item = c_fh.pk),
		ARRAY[]::integer[]
	)
		as pk_generic_codes,
	c_fh.xmin
		as xmin_family_history
from
	clin.family_history c_fh
		inner join clin.encounter cenc on c_fh.fk_encounter = cenc.pk
			inner join clin.episode cep on c_fh.fk_episode = cep.pk
				left join clin.fhx_relation_type c_fhrt on c_fh.fk_relation_type = c_fhrt.pk
;


comment on view clin.v_family_history is
	'family history denormalized';


grant select on clin.v_family_history to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-v_family_history.sql', 'v16.0');

-- ==============================================================
