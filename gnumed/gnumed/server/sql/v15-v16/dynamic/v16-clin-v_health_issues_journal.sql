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
drop view clin.v_health_issues_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_health_issues_journal as
select
	cenc.fk_patient
		as pk_patient,
	chi.modified_when
		as modified_when,
	coalesce (
		(select dem.identity.dob + chi.age_noted
		 from dem.identity
		 where pk = (select fk_patient from clin.encounter where pk = chi.fk_encounter)
		),
		cenc.started
	)
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = chi.modified_by),
		'<' || chi.modified_by || '>'
	) 	as modified_by,
	'a'::text
		as soap_cat,
	_('Health Issue') || ' ('
			|| case when chi.is_active
				then _('active')
				else _('inactive')
			   end
			|| ', '
			|| case when chi.clinically_relevant
				then _('clinically relevant')
				else _('clinically not relevant')
			   end
			|| coalesce((', ' || chi.diagnostic_certainty_classification), '')
			|| '): '
			|| chi.description
			|| coalesce((E';\n' || _('noted at age') || ': ' || chi.age_noted::text || E';\n'), E';\n')
			|| coalesce((_('Laterality') || ': ' || chi.laterality || ' / '), '')
			|| case when chi.is_confidential
				then _('confidential') || ' / ' else ''
			   end
			|| case when chi.is_cause_of_death
				then _('cause of death') else ''
			   end
			|| coalesce((E';\n' || _('Summary') || E':\n' || chi.summary), E'')
			|| coalesce ((
					E';\n' || array_to_string (
						(select array_agg(r_csr.code || ' (' || r_ds.name_short || ' - ' || r_ds.version || ' - ' || r_ds.lang || '): ' || r_csr.term)
						 from
						 	clin.lnk_code2h_issue c_lc2h
						 		inner join
							ref.coding_system_root r_csr on c_lc2h.fk_generic_code = r_csr.pk_coding_system
								inner join
							ref.data_source r_ds on r_ds.pk = r_csr.fk_data_source
						where
							c_lc2h.fk_item = chi.pk
						),
						'; '
					) || ';'
				),
				''
			)
		as narrative,
	chi.fk_encounter
		as pk_encounter,
	-1
		as pk_episode,
	chi.pk
		as pk_health_issue,
	chi.pk
		as src_pk,
	'clin.health_issue'::text
		as src_table,
	chi.row_version
from
	clin.health_issue chi
		inner join clin.encounter cenc on chi.fk_encounter = cenc.pk
;


select i18n.upd_tx('de', 'Health Issue', 'Grunderkrankung');
select i18n.upd_tx('de', 'active', 'aktiv');
select i18n.upd_tx('de', 'inactive', 'inaktiv');
select i18n.upd_tx('de', 'clinically relevant', 'medizinisch relevant');
select i18n.upd_tx('de', 'clinically not relevant', 'medizinisch nicht relevant');
select i18n.upd_tx('de', 'noted at age', 'aufgefallen im Alter von');
select i18n.upd_tx('de', 'Laterality', 'Seite');
select i18n.upd_tx('de', 'confidential', 'vertraulich');
select i18n.upd_tx('de', 'cause of death', 'Todesursache');
select i18n.upd_tx('de', 'Summary', 'Zusammenfassung');


grant select on clin.v_health_issues_journal TO GROUP "gm-doctors";
-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-v_health_issues_journal.sql', 'v16');

-- ==============================================================
