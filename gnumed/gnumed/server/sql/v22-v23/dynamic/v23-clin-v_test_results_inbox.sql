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
drop view if exists clin.v_test_results_inbox cascade;

create view clin.v_test_results_inbox as
select
	now()
		as received_when,
	c_tr.modified_by
		as modified_by,
	d_s.short_alias
		as provider,
	1
		as importance,
	'clinical'
		as category,
	_('clinical')
		as l10n_category,
	'review results'
		as type,
	_('review results')
		as l10n_type,
	(select _('unreviewed (abnormal) results for patient') || ' ['
		|| d_n.lastnames || ', '
		|| d_n.firstnames || ']'
	)
		as comment,
	NULL::integer[]
		as pk_context,
	NULL::text
		as data,
	NULL::integer
		as pk_inbox_message,
	c_tr.fk_intended_reviewer
		as pk_staff,
	(select pk_category from dem.v_inbox_item_type where type = 'review results')
		as pk_category,
	(select pk_type from dem.v_inbox_item_type where type = 'review results')
		as pk_type,
	c_enc.fk_patient
		as pk_patient,
	TRUE
		as is_virtual,
	now()::timestamp with time zone - '1 hour'::interval
		as due_date,
	NULL::timestamp with time zone
		as expiry_date,
	TRUE::boolean
		as is_overdue,
	FALSE::boolean
		as is_expired,
	'1 hour'::interval
		as interval_due,
	NULL::integer
		as xmin_message_inbox
from
	clin.test_result c_tr
		left join dem.staff d_s on (c_tr.fk_intended_reviewer = d_s.pk)
		left join clin.encounter c_enc on (c_tr.fk_encounter = c_enc.pk)
			left join (select * from dem.names where active is TRUE) as d_n on (c_enc.fk_patient = d_n.id_identity)
		left join clin.reviewed_test_results c_rtr on (c_tr.pk = c_rtr.fk_reviewed_row)
		left join clin.v_test_types c_vtt on (c_tr.fk_type = c_vtt.pk_test_type)
		left join clin.episode epi on (c_tr.fk_episode = epi.pk)
			left join clin.health_issue chi on (epi.fk_health_issue = chi.pk)
where
	coalesce(c_rtr.fk_reviewed_row, 0)::bool IS FALSE
		and
	(
		(c_rtr.is_technically_abnormal is true)
			or
		((c_rtr.is_technically_abnormal is null) and (c_tr.abnormality_indicator is not null))
	)
-- ---------------
		UNION
-- ---------------
select
	now()
		as received_when,
	c_tr.modified_by
		as modified_by,
	d_s.short_alias
		as provider,
	1
		as importance,
	'clinical'
		as category,
	_('clinical')
		as l10n_category,
	'review results'
		as type,
	_('review results')
		as l10n_type,
	(select _('unreviewed (normal) results for patient') || ' ['
		|| d_n.lastnames || ', '
		|| d_n.firstnames || ']'
	)
		as comment,
	NULL::integer[]
		as pk_context,
	NULL::text
		as data,
	NULL::integer
		as pk_inbox_message,
	c_tr.fk_intended_reviewer
		as pk_staff,
	(select pk_category from dem.v_inbox_item_type where type = 'review results')
		as pk_category,
	(select pk_type from dem.v_inbox_item_type where type = 'review results')
		as pk_type,
	c_enc.fk_patient
		as pk_patient,
	TRUE
		as is_virtual,
	now()::timestamp with time zone - '1 hour'::interval
		as due_date,
	NULL::timestamp with time zone
		as expiry_date,
	TRUE::boolean
		as is_overdue,
	FALSE::boolean
		as is_expired,
	'1 hour'::interval
		as interval_due,
	NULL::integer
		as xmin_message_inbox
from
	clin.test_result c_tr
		left join dem.staff d_s on (c_tr.fk_intended_reviewer = d_s.pk)
		left join clin.encounter c_enc on (c_tr.fk_encounter = c_enc.pk)
			left join (select * from dem.names where active is TRUE) as d_n on (c_enc.fk_patient = d_n.id_identity)
		left join clin.reviewed_test_results c_rtr on (c_tr.pk = c_rtr.fk_reviewed_row)
		left join clin.v_test_types c_vtt on (c_tr.fk_type = c_vtt.pk_test_type)
		left join clin.episode epi on (c_tr.fk_episode = epi.pk)
			left join clin.health_issue chi on (epi.fk_health_issue = chi.pk)
where
	coalesce(c_rtr.fk_reviewed_row, 0)::bool IS FALSE
		and
	(
		(c_rtr.is_technically_abnormal is false)		-- therefore UNION works
			or
		((c_rtr.is_technically_abnormal is null) and (c_tr.abnormality_indicator is null))
	)
;


comment on view clin.v_test_results_inbox is
	'denormalized unreviewed test results for the message inbox';


grant select on clin.v_test_results_inbox to group "gm-doctors";
grant select on clin.v_test_results_inbox to group "gm-staff";

-- ==============================================================
select gm.log_script_insertion('v23-clin-v_test_results_inbox.sql', '23.0');
