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
drop view if exists blobs.v_unreviewed_docs cascade;

create view blobs.v_unreviewed_docs as
select distinct on (b_do.fk_doc)
	b_do.fk_doc
		as pk_doc,
	-- (not strictly per-doc but usually so)
	min(b_do.fk_intended_reviewer)
		as pk_intended_reviewer,
	min(c_e.fk_patient)
		as pk_patient
from
	blobs.doc_obj b_do
		join blobs.doc_med b_dm on (b_dm.pk = b_do.fk_doc)
			join clin.encounter c_e on (b_dm.fk_encounter = c_e.pk)
where
	NOT EXISTS (
		SELECT 1 FROM blobs.reviewed_doc_objs b_rdo
		WHERE b_rdo.fk_reviewed_row = b_do.pk
	)
group by
	b_do.fk_doc
;


revoke all on blobs.v_unreviewed_docs from public;

grant select on blobs.v_unreviewed_docs to group "gm-staff";

-- --------------------------------------------------------------
drop view if exists blobs.v_unreviewed_docs_summary cascade;

create view blobs.v_unreviewed_docs_summary as
select
	b_vud.pk_patient,
	count(1)
		as no_of_docs
from
	blobs.v_unreviewed_docs b_vud
group by
	b_vud.pk_patient
;


revoke all on blobs.v_unreviewed_docs_summary from public;

grant select on blobs.v_unreviewed_docs_summary to group "gm-staff";

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
	_('clinical')::text
		as l10n_category,
	'review docs'::text
		as type,
	_('review docs')::text
		as l10n_type,
	(select
		b_vuds.no_of_docs || ' '
		|| _('unreviewed documents for patient')
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
select gm.log_script_insertion('v20-blobs-doc_obj-dynamic.sql', '20.0');
