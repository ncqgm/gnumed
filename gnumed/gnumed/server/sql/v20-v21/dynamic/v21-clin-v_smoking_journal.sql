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
drop view if exists clin.v_smoking_journal cascade;


create view clin.v_smoking_journal as
select
	c_p.fk_identity
		as pk_patient,
	c_p.modified_when
		as modified_when,
	coalesce (
		(c_p.smoking_details->>'last_confirmed')::timestamp with time zone,
		c_p.modified_when
	)
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_p.modified_by),
		'<' || c_p.modified_by || '>'
	)
		as modified_by,
	's'::text
		as soap_cat,
	_('Smoking status') || ': '
		|| case
			when c_p.smoking_ever is null then _('unknown, unasked')
			when c_p.smoking_ever is TRUE then _('never smoked')
			when c_p.smoking_ever IS FALSE then _('current or previous smoker')
		   end
		|| coalesce (
			' (' || _('last confirmed') || to_char((c_p.smoking_details->>'last_confirmed')::timestamp with time zone, ' YYYY Mon DD') || ')',
			''
		)
		|| coalesce (
			', ' || _('quit date') || ': ' || to_char((c_p.smoking_details->>'quit_when')::timestamp with time zone, ' YYYY Mon DD'),
			''
		)
		|| coalesce (
			E'\n ' || (c_p.smoking_details->'comment')::text,
			''
		)
			as narrative,
	(
		select c_e.pk
		from clin.encounter c_e
		where c_e.fk_patient = c_p.fk_identity
		order by started desc
		limit 1
	)
		as pk_encounter,
	null::integer
		as pk_episode,
	null::integer
		as pk_health_issue,
	c_p.pk
		as src_pk,
	'clin.patient'::text
		as src_table,
	c_p.row_version
		as row_version
from
	clin.patient c_p
;

grant select on clin.v_smoking_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_smoking_journal.sql', '21.0');
