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
drop view clin.v_pat_narrative_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_narrative_journal as
select
	cenc.fk_patient
		as pk_patient,
	cn.modified_when
		as modified_when,
	case
		when cn.soap_cat in ('s','o') then cenc.started
		when cn.soap_cat is NULL then cenc.last_affirmed
		when cn.soap_cat in ('a','p') then cenc.last_affirmed
	end
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cn.modified_by),
		'<' || cn.modified_by || '>'
	)
		as modified_by,
	cn.soap_cat
		as soap_cat,
	cn.narrative
		as narrative,
	cn.fk_encounter
		as pk_encounter,
	cn.fk_episode
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = cn.fk_episode)
		as pk_health_issue,
	cn.pk as src_pk,
	'clin.clin_narrative'::text as src_table,
	cn.row_version
from
	clin.clin_narrative cn
		inner join clin.encounter cenc on (cn.fk_encounter = cenc.pk)
;


grant select on clin.v_pat_narrative_journal TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-v_pat_narrative_journal.sql', '16.0');

-- ==============================================================
