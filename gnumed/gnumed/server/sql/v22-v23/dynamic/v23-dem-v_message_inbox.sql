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
drop view if exists dem.v_message_inbox cascade;


create view dem.v_message_inbox as

SELECT
	all_msgs.*,
	d_n.lastnames,
	d_n.firstnames,
	d_n.preferred
		AS preferred_name,
	d_n.comment
		AS comment_name,
	d_i.gender,
	_(d_i.gender)
		AS l10n_gender,
	date_trunc('day'::text, d_i.dob) + COALESCE(d_i.tob, d_i.dob::time without time zone)::interval
		AS dob,
	d_i.deceased,
	d_i.title,
	d_i.comment
		AS comment_identity
FROM (

	select
		mi.modified_when
			as received_when,
		coalesce (
			(select short_alias from dem.staff where db_user = mi.modified_by),
			'<' || mi.modified_by || '>'
		)
			as modified_by,
		(select short_alias from dem.staff where dem.staff.pk = mi.fk_staff)
			as provider,
		mi.importance,
		vit.category,
		vit.l10n_category,
		vit.type,
		vit.l10n_type,
		mi.comment,
		mi.ufk_context
			as pk_context,
		mi.data
			as data,
		mi.pk
			as pk_inbox_message,
		mi.fk_staff
			as pk_staff,
		vit.pk_category,
		mi.fk_inbox_item_type
			as pk_type,
		mi.fk_patient
			as pk_patient,
		false
			as is_virtual,
		mi.due_date
			as due_date,
		mi.expiry_date
			as expiry_date,
		case
			when due_date is null then false
			 when due_date > now() then false
			  when expiry_date is null then true
			   when expiry_date < now() then false
			else true
		end
			as is_overdue,
		case
			when expiry_date is null then false
			 when expiry_date > now() then false
			else true
		end
			as is_expired,
		case
			when due_date is null then null
			 when due_date > now() then due_date - now()
			else now() - due_date
		end
			as interval_due,
		gm.xid2int(mi.xmin)
			as xmin_message_inbox
	from
		dem.message_inbox mi,
		dem.v_inbox_item_type vit
	where
		mi.fk_inbox_item_type = vit.pk_type

UNION ALL

	select * from blobs.v_unreviewed_docs_inbox

UNION ALL

	select * from clin.v_test_results_inbox

) AS all_msgs

	LEFT OUTER JOIN dem.identity d_i ON (all_msgs.pk_patient = d_i.pk)
		LEFT OUTER JOIN dem.names d_n ON (d_i.pk = d_n.id_identity)

WHERE
	-- name must be active=True or active=None (no patient)
	-- do _not_ include active=False as that would produce
	-- duplicates when there are several names for a patient
	d_n.active IS DISTINCT FROM FALSE
;


comment on view dem.v_message_inbox is
'Denormalized messages for the providers and/or patients.
Using UNION makes sure we get the right level of uniqueness.';


grant select on dem.v_message_inbox to group "gm-doctors";
grant select on dem.v_message_inbox to group "gm-staff";

-- ==============================================================
select gm.log_script_insertion('v23-dem-v_message_inbox.sql', '23.0');
