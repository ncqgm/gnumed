-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-clin-v_pat_allergies_journal.sql,v 1.1 2008-09-02 15:41:20 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_allergies_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_allergies_journal as

select
	(select fk_patient from clin.encounter where pk = a.fk_encounter)
		as pk_patient,
	a.modified_when
		as modified_when,
	a.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = a.modified_by),
		'<' || a.modified_by || '>'
	)
		as modified_by,
	a.soap_cat
		as soap_cat,
	_('Allergy') || ' (' || _(at.value) || '): ' || coalesce(a.narrative, '') || E'\n'
		|| _('substance') || ': ' || a.substance || '; '
		|| coalesce((_('allergene') || ': ' || a.allergene || '; '), '')
		|| coalesce((_('generic')   || ': ' || a.generics || '; '), '')
		|| coalesce((_('ATC code')  || ': ' || a.atc_code || '; '), '')
		as narrative,
	a.fk_encounter
		as pk_encounter,
	a.fk_episode
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = a.fk_episode)
		as pk_health_issue,
	a.pk
		as src_pk,
	'clin.allergy'::text
		as src_table
from
	clin.allergy a,
	clin._enum_allergy_type at
where
	at.pk = a.fk_type
;


grant select on clin.v_pat_allergies_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_pat_allergies_journal.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-v_pat_allergies_journal.sql,v $
-- Revision 1.1  2008-09-02 15:41:20  ncq
-- - new
--
--