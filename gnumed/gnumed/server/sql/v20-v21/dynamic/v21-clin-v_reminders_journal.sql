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
drop view if exists clin.v_reminders_journal cascade;


create view clin.v_reminders_journal as

	-- clin_when: due date
	select
		d_mi.fk_patient
			as pk_patient,
		d_mi.modified_when
			as modified_when,
		d_mi.due_date
			as clin_when,
		coalesce (
			(select short_alias from dem.staff where db_user = d_mi.modified_by),
			'<' || d_mi.modified_by || '>'
		)
			as modified_by,
		NULL::text
			as soap_cat,
		_('Due today') || ' (' || d_vit.l10n_category || ' - ' || d_vit.l10n_type || ')' || E'\n'
			|| coalesce(' ' || d_mi.comment || E'\n', '')
			|| coalesce(' ' || _('Will expire:') || ' ' || to_char(d_mi.expiry_date, 'YYYY-MM-DD') || E'\n', '')
			|| ' ' || _('Importance:') || ' ' || d_mi.importance || E'\n'
			|| coalesce(' ' || _('Context:') || ' ' || array_to_string(d_mi.ufk_context, ',', '?') || E'\n', '')
			|| coalesce(' ' || _('Data:') || ' ' || d_mi.data || E'\n', '')
			|| coalesce(' ' || _('Provider:') || ' ' || d_st.short_alias, '')
		as narrative,
		(
			select c_e.pk
			from clin.encounter c_e
			where c_e.fk_patient = d_mi.fk_patient
			order by started desc
			limit 1
		)
			as pk_encounter,
		null::integer
			as pk_episode,
		null::integer
			as pk_health_issue,
		d_mi.pk
			as src_pk,
		'dem.message_inbox'::text
			as src_table,
		d_mi.row_version
			as row_version,

		-- issue
		null::text
			as health_issue,
		null::text
			as issue_laterality,
		null::boolean
			as issue_active,
		null::boolean
			as issue_clinically_relevant,
		null::boolean
			as issue_confidential,

		-- episode
		null::text
			as episode,
		null::boolean
			as episode_open,

		-- encounter
		(
			select c_e.started
			from clin.encounter c_e
			where c_e.fk_patient = d_mi.fk_patient
			order by started desc
			limit 1
		)
			as encounter_started,
		(
			select c_e.last_affirmed
			from clin.encounter c_e
			where c_e.fk_patient = d_mi.fk_patient
			order by started desc
			limit 1
		)
			as encounter_last_affirmed,
		null::text
			as encounter_type,
		null::text
			as encounter_l10n_type
	from
		dem.message_inbox d_mi
			inner join dem.v_inbox_item_type d_vit on (d_mi.fk_inbox_item_type = d_vit.pk_type)
			left join dem.staff d_st on (d_mi.fk_staff = d_st.pk)
	where
		d_mi.fk_patient is not null
			and
		d_vit.category = 'clinical'
			and
		d_mi.due_date is not null

UNION

	-- clin_when: expiry date
	select
		d_mi.fk_patient
			as pk_patient,
		d_mi.modified_when
			as modified_when,
		d_mi.expiry_date
			as clin_when,
		coalesce (
			(select short_alias from dem.staff where db_user = d_mi.modified_by),
			'<' || d_mi.modified_by || '>'
		)
			as modified_by,
		NULL::text
			as soap_cat,
		_('Epires today') || ' (' || d_vit.l10n_category || ' - ' || d_vit.l10n_type || ')' || E'\n'
			|| coalesce(' ' || d_mi.comment || E'\n', '')
			|| coalesce(' ' || _('Was due:') || ' ' || to_char(d_mi.due_date, 'YYYY-MM-DD') || E'\n', '')
			|| ' ' || _('Importance:') || ' ' || d_mi.importance || E'\n'
			|| coalesce(' ' || _('Context:') || ' ' || array_to_string(d_mi.ufk_context, ',', '?') || E'\n', '')
			|| coalesce(' ' || _('Data:') || ' ' || d_mi.data || E'\n', '')
			|| coalesce(' ' || _('Provider:') || ' ' || d_st.short_alias, '')
		as narrative,
		(
			select c_e.pk
			from clin.encounter c_e
			where c_e.fk_patient = d_mi.fk_patient
			order by started desc
			limit 1
		)
			as pk_encounter,
		null::integer
			as pk_episode,
		null::integer
			as pk_health_issue,
		d_mi.pk
			as src_pk,
		'dem.message_inbox'::text
			as src_table,
		d_mi.row_version
			as row_version,

		-- issue
		null::text
			as health_issue,
		null::text
			as issue_laterality,
		null::boolean
			as issue_active,
		null::boolean
			as issue_clinically_relevant,
		null::boolean
			as issue_confidential,

		-- episode
		null::text
			as episode,
		null::boolean
			as episode_open,

		-- encounter
		(
			select c_e.started
			from clin.encounter c_e
			where c_e.fk_patient = d_mi.fk_patient
			order by started desc
			limit 1
		)
			as encounter_started,
		(
			select c_e.last_affirmed
			from clin.encounter c_e
			where c_e.fk_patient = d_mi.fk_patient
			order by started desc
			limit 1
		)
			as encounter_last_affirmed,
		null::text
			as encounter_type,
		null::text
			as encounter_l10n_type
	from
		dem.message_inbox d_mi
			inner join dem.v_inbox_item_type d_vit on (d_mi.fk_inbox_item_type = d_vit.pk_type)
			left join dem.staff d_st on (d_mi.fk_staff = d_st.pk)
	where
		d_mi.fk_patient is not null
			and
		d_vit.category = 'clinical'
			and
		d_mi.expiry_date is not null

UNION

	-- clin_when: modified_when (= message received)
	select
		d_mi.fk_patient
			as pk_patient,
		d_mi.modified_when
			as modified_when,
		d_mi.modified_when
			as clin_when,
		coalesce (
			(select short_alias from dem.staff where db_user = d_mi.modified_by),
			'<' || d_mi.modified_by || '>'
		)
			as modified_by,
		NULL::text
			as soap_cat,
		_('Clinical reminder') || ' (' || d_vit.l10n_category || ' - ' || d_vit.l10n_type || ')' || E'\n'
			|| coalesce(' ' || d_mi.comment || E'\n', '')
			|| coalesce(' ' || _('Due:') || ' ' || to_char(d_mi.due_date, 'YYYY-MM-DD') || E'\n', '')
			|| coalesce(' ' || _('Expires:') || ' ' || to_char(d_mi.expiry_date, 'YYYY-MM-DD') || E'\n', '')
			|| ' ' || _('Importance:') || ' ' || d_mi.importance || E'\n'
			|| coalesce(' ' || _('Context:') || ' ' || array_to_string(d_mi.ufk_context, ',', '?') || E'\n', '')
			|| coalesce(' ' || _('Data:') || ' ' || d_mi.data || E'\n', '')
			|| coalesce(' ' || _('Provider:') || ' ' || d_st.short_alias, '')
		as narrative,
		(
			select c_e.pk
			from clin.encounter c_e
			where c_e.fk_patient = d_mi.fk_patient
			order by started desc
			limit 1
		)
			as pk_encounter,
		null::integer
			as pk_episode,
		null::integer
			as pk_health_issue,
		d_mi.pk
			as src_pk,
		'dem.message_inbox'::text
			as src_table,
		d_mi.row_version
			as row_version,

		-- issue
		null::text
			as health_issue,
		null::text
			as issue_laterality,
		null::boolean
			as issue_active,
		null::boolean
			as issue_clinically_relevant,
		null::boolean
			as issue_confidential,

		-- episode
		null::text
			as episode,
		null::boolean
			as episode_open,

		-- encounter
		(
			select c_e.started
			from clin.encounter c_e
			where c_e.fk_patient = d_mi.fk_patient
			order by started desc
			limit 1
		)
			as encounter_started,
		(
			select c_e.last_affirmed
			from clin.encounter c_e
			where c_e.fk_patient = d_mi.fk_patient
			order by started desc
			limit 1
		)
			as encounter_last_affirmed,
		null::text
			as encounter_type,
		null::text
			as encounter_l10n_type
	from
		dem.message_inbox d_mi
			inner join dem.v_inbox_item_type d_vit on (d_mi.fk_inbox_item_type = d_vit.pk_type)
			left join dem.staff d_st on (d_mi.fk_staff = d_st.pk)
	where
		d_mi.fk_patient is not null
			and
		d_vit.category = 'clinical'
			and
		(
			(d_mi.due_date is not null)
				or
			(d_mi.expiry_date is not null)
		)
;


grant select on clin.v_reminders_journal to group "gm-doctors";

-- --------------------------------------------------------------
select i18n.upd_tx('de', 'Clinical reminder', 'Medizinische Erinnerung');

select i18n.upd_tx('de', 'Due today', 'Heute fällig');
select i18n.upd_tx('de', 'Due:', 'Fällig:');
select i18n.upd_tx('de', 'Was due:', 'War fällig:');

select i18n.upd_tx('de', 'Epires today', 'Läuft heute ab');
select i18n.upd_tx('de', 'Expires:', 'Läuft ab:');
select i18n.upd_tx('de', 'Will expire:', 'Wird ablaufen:');

select i18n.upd_tx('de', 'Importance:', 'Bedeutsamkeit:');
select i18n.upd_tx('de', 'Context:', 'Kontext:');
select i18n.upd_tx('de', 'Data:', 'Daten:');
select i18n.upd_tx('de', 'Provider:', 'Mitarbeiter:');

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_reminders_journal.sql', '21.0');
