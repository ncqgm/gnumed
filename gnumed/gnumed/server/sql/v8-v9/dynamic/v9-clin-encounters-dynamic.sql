-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-encounters-dynamic.sql,v 1.2 2008-06-23 21:51:04 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_encounters cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_encounters as
select
	cle.pk as pk_encounter,
	cle.fk_patient as pk_patient,
	cle.started as started,
	et.description as type,
	_(et.description) as l10n_type,
	cle.reason_for_encounter as reason_for_encounter,
	cle.assessment_of_encounter as assessment_of_encounter,
	cle.last_affirmed as last_affirmed,
	cle.source_time_zone,
	(select started at time zone (
		select source_time_zone
		from clin.encounter cle1
		where cle1.pk = cle.pk
	)) as started_original_tz,
	(select last_affirmed at time zone (
		select source_time_zone
		from clin.encounter cle1
		where cle1.pk = cle.pk
	)) as last_affirmed_original_tz,
	cle.fk_location as pk_location,
	cle.fk_type as pk_type,
	cle.xmin as xmin_encounter
from
	clin.encounter cle,
	clin.encounter_type et
where
	cle.fk_type = et.pk
;


comment on view clin.v_pat_encounters is
	'Details on encounters.';


-- views
grant select on
	clin.v_pat_encounters
TO GROUP "gm-doctors";


-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_encounters_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_encounters_journal as
select
	cenc.fk_patient
		as pk_patient,
	cenc.modified_when
		as modified_when,
	-- FIXME: or last_affirmed ?
	cenc.started
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cenc.modified_by),
		'<' || cenc.modified_by || '>'
	) 	as modified_by,
	null::text
		as soap_cat,
	_('Encounter: ')
		|| (select _(description) from clin.encounter_type where pk = cenc.fk_type)
		|| to_char(cenc.started::timestamp with time zone, ' YYYY-MM-DD HH24:MI')
		|| to_char(cenc.last_affirmed::timestamp with time zone, ' - HH24:MI')
		|| coalesce(E'\n ' || _('RFE') || ': ' || cenc.reason_for_encounter, '')
		|| coalesce(E'\n ' || _('AOE') || ': ' || cenc.assessment_of_encounter, '')
		as narrative,
	cenc.pk
		as pk_encounter,
	-1	as pk_episode,
	-1	as pk_health_issue,
	cenc.pk
		as src_pk,
	'clin.encounter'::text as src_table
from
	clin.encounter cenc
;


grant select on clin.v_pat_encounters_journal TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-encounters-dynamic.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v9-clin-encounters-dynamic.sql,v $
-- Revision 1.2  2008-06-23 21:51:04  ncq
-- - v_pat_encounters_journal
--
-- Revision 1.1  2008/04/11 12:18:37  ncq
-- - new file
--
--
