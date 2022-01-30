-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists clin.v_subst_intake4narr_search cascade;
drop view if exists clin.v_intake4narr_search cascade;


create view clin.v_intake4narr_search as

select
	c_enc.fk_patient
		as pk_patient,
	c_i.soap_cat
		as soap_cat,
	coalesce(c_i.narrative, '')		-- aka notes4provider
		|| coalesce(' / ' || c_i.notes4patient, '')
		as narrative,
	c_i.fk_encounter
		as pk_encounter,
	c_i.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	c_i.pk
		as src_pk,
	'clin.intake'
		as src_table
from
	clin.intake c_i
		join clin.encounter c_enc on (c_i.fk_encounter = c_enc.pk)
			join clin.episode c_epi on (c_i.fk_episode = c_epi.pk)
;

grant select on clin.v_intake4narr_search to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_intake4narrative_search.sql', '23.0');
