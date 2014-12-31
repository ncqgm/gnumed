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

create view clin.v_subst_intake4narr_search as

select
	c_enc.fk_patient
		as pk_patient,
	c_si.soap_cat
		as soap_cat,
	coalesce(c_si.narrative, '')			-- comment/note/advice
		|| coalesce(' / ' || c_si.comment_on_start, '')
		|| coalesce(' / ' || c_si.schedule, '')
		|| coalesce(' / ' || c_si.aim, '')
		|| coalesce(' / ' || c_si.discontinue_reason, '')
		as narrative,
	c_si.fk_encounter
		as pk_encounter,
	c_si.fk_episode
		as pk_episode,
	c_epi.fk_health_issue
		as pk_health_issue,
	c_si.pk
		as src_pk,
	'clin.substance_intake'
		as src_table
from
	clin.substance_intake c_si
		join clin.encounter c_enc on (c_si.fk_encounter = c_enc.pk)
			join clin.episode c_epi on (c_si.fk_episode = c_epi.pk)
;

grant select on clin.v_subst_intake4narr_search to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_subst_intake4narr_search.sql', '21.0');
