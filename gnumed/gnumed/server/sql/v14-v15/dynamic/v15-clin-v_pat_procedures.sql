-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_procedures cascade;
\set ON_ERROR_STOP 1



create view clin.v_pat_procedures as

select
	cpr.pk
		as pk_procedure,
	(select enc.fk_patient from clin.encounter enc where enc.pk = cpr.fk_encounter)
		as pk_patient,
	cpr.soap_cat,
	cpr.clin_when,
	cpr.clin_end,
	cpr.is_ongoing,
	cpr.narrative
		as performed_procedure,
	coalesce (
		(select chs.narrative from clin.hospital_stay chs where cpr.fk_hospital_stay = chs.pk),
		cpr.clin_where
	)	as clin_where,
	(select description from clin.episode where pk = cpr.fk_episode)
		as episode,
	(select description from clin.health_issue where pk = (
		select fk_health_issue from clin.episode where pk = cpr.fk_episode
	))
		as health_issue,

	cpr.modified_when
		as modified_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cpr.modified_by),
		'<' || cpr.modified_by || '>'
	)
		as modified_by,
	cpr.row_version,
	cpr.fk_encounter
		as pk_encounter,
	cpr.fk_episode
		as pk_episode,
	cpr.fk_hospital_stay
		as pk_hospital_stay,
	(select epi.fk_health_issue from clin.episode epi where epi.pk = cpr.fk_episode)
		as pk_health_issue,
	cpr.xmin as xmin_procedure
from
	clin.procedure cpr
;



grant select on
	clin.v_pat_procedures
TO GROUP "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_procedures_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_procedures_journal as
select
	(select fk_patient from clin.encounter where pk = cpr.fk_encounter)
		as pk_patient,
	cpr.modified_when
		as modified_when,
	cpr.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cpr.modified_by),
		'<' || cpr.modified_by || '>'
	)
		as modified_by,
	cpr.soap_cat
		as soap_cat,
	_('Procedure') || ' "'
		|| narrative
		|| '" ('
			|| coalesce (
				(select chs.narrative from clin.hospital_stay chs where cpr.fk_hospital_stay = chs.pk),
				cpr.clin_where
			)
			|| coalesce (
				', ' || _('until') || ' ' || to_char(cpr.clin_end, 'YYYY Mon DD'),
				case
					when (is_ongoing is True)
						then ', ' || _('ongoing')
						else ''
				end
			)
		|| ')'
		as narrative,
	cpr.fk_encounter
		as pk_encounter,
	cpr.pk
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = cpr.fk_episode)
		as pk_health_issue,
	cpr.pk
		as src_pk,
	'clin.procedure'::text
		as src_table,
	cpr.row_version
from
	clin.procedure cpr
;


grant select on clin.v_pat_procedures_journal TO GROUP "gm-doctors";


select i18n.upd_tx('de', 'until', 'bis');

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-clin-v_pat_procedures.sql', '1.1');

-- ==============================================================
