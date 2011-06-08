-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-clin-v_pat_allergy_state_journal.sql,v 1.1 2009-04-01 15:55:40 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_allergy_state_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_allergy_state_journal as

select
	(select fk_patient from clin.encounter where pk = a.fk_encounter)
		as pk_patient,
	a.modified_when
		as modified_when,
	a.last_confirmed
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = a.modified_by),
		'<' || a.modified_by || '>'
	)
		as modified_by,
	'o'::text
		as soap_cat,
	_('Allergy state') || ': '
		|| case
			when a.has_allergy is null then _('unknown, unasked')
			when a.has_allergy = 0 then _('no known allergies')
			when a.has_allergy = 1 then _('does have allergies')
		   end
		|| coalesce (
			' (' || _('last confirmed') || to_char(a.last_confirmed, ' YYYY-MM-DD HH24:MI') || ')',
			''
		) || coalesce (
			E'\n ' || a.comment,
			''
		) as narrative,
	a.fk_encounter
		as fk_encounter,
	null::integer
		as fk_episode,
	null::integer
		as pk_health_issue,
	a.pk
		as src_pk,
	'clin.allergy_state'::text
		as src_table,
	a.row_version
		as row_version
from
	clin.allergy_state a
;

grant select on clin.v_pat_allergy_state_journal to group "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-v_pat_allergy_state_journal.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-clin-v_pat_allergy_state_journal.sql,v $
-- Revision 1.1  2009-04-01 15:55:40  ncq
-- - new
--
--