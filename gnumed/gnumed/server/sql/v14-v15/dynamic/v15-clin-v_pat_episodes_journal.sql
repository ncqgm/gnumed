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
drop view clin.v_pat_episodes_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_episodes_journal as
select
--	(select fk_patient from clin.encounter where pk = cep.fk_encounter)
	cenc.fk_patient
		as pk_patient,
	cep.modified_when
		as modified_when,
--	cep.modified_when
	cenc.started
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cep.modified_by),
		'<' || cep.modified_by || '>'
	)
		as modified_by,
	'a'::text
		as soap_cat,
	_('Episode') || coalesce((' (' || cep.diagnostic_certainty_classification || ')'), '') || ': '
		|| cep.description || ' ('
		|| case when cep.is_open
			then _('open')
			else _('closed')
			end
		|| ')'
		as narrative,
	cep.fk_encounter
		as pk_encounter,
	cep.pk
		as pk_episode,
	cep.fk_health_issue
		as pk_health_issue,
	cep.pk
		as src_pk,
	'clin.episode'::text
		as src_table,
	cep.row_version
from
	clin.episode cep
		inner join
	clin.encounter cenc
		on cep.fk_encounter = cenc.pk
;


grant select on clin.v_pat_episodes_journal TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v15-clin-v_pat_episodes_journal.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
