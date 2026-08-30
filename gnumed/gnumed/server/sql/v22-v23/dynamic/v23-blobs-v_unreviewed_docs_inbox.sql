-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists blobs.v_unreviewed_docs_inbox cascade;

create view blobs.v_unreviewed_docs_inbox as
select
	now()
		as received_when,
	'<system>'::text
		as modified_by,
	NULL::text
		as provider,
	0
		as importance,
	'clinical'::text
		as category,
	(select _('clinical'))::text
		as l10n_category,
	'review docs'::text
		as type,
	(select _('review docs'))::text
		as l10n_type,
	(select
		b_vuds.no_of_docs || ' '
		|| (select _('unreviewed documents for patient'))
		|| ' ' || d_n.lastnames || ', '	|| d_n.firstnames
	)
	 	as comment,
	NULL::integer[]
		as pk_context,
	NULL::text
		as data,
	NULL::integer
		as pk_inbox_message,
	(select pk from dem.staff where dem.staff.db_user = current_user)
		as pk_staff,
	(select pk_category from dem.v_inbox_item_type where type = 'review docs')
		as pk_category,
	(select pk_type from dem.v_inbox_item_type where type = 'review docs')
		as pk_type,
	b_vuds.pk_patient as pk_patient,
	true
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
	blobs.v_unreviewed_docs_summary b_vuds
		join dem.names d_n on (b_vuds.pk_patient = d_n.id_identity)
where
	d_n.active is True
;

revoke all on blobs.v_unreviewed_docs_inbox from public;

grant select on blobs.v_unreviewed_docs_inbox to group "gm-staff";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-blobs-v_unreviewed_docs_inbox.sql', '23.0');
