-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-clin-v_pat_hospital_stays_journal.sql,v 1.1 2009-04-01 15:55:39 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_hospital_stays_journal cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_hospital_stays_journal as
select
	(select fk_patient from clin.encounter where pk = chs.fk_encounter)
		as pk_patient,
	chs.modified_when
		as modified_when,
	chs.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = chs.modified_by),
		'<' || chs.modified_by || '>'
	)
		as modified_by,
	chs.soap_cat
		as soap_cat,
	_('hospital stay') || ': '
		|| to_char(clin_when, 'YYYY-MM-DD') || ' - '
		|| coalesce(to_char(discharge, 'YYYY-MM-DD'), '?')
		|| coalesce((' "' || chs.narrative) || '"', '')
		as narrative,
	chs.fk_encounter
		as pk_encounter,
	chs.fk_episode
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = chs.fk_episode)
		as pk_health_issue,
	chs.pk
		as src_pk,
	'clin.hospital_stay'::text
		as src_table,
	chs.row_version
		as row_version
from
	clin.hospital_stay chs
;


select i18n.upd_tx('de_DE', 'hospital stay', 'Krankenhausaufenthalt');

-- --------------------------------------------------------------
grant select on clin.v_pat_hospital_stays_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-v_pat_hospital_stays_journal.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
--