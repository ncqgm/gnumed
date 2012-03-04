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
-- .due_date
comment on column dem.message_inbox.due_date is
	'The date this message/reminder is due. If NULL then the message is not a reminder.';

-- .expiry_date
comment on column dem.message_inbox.expiry_date is
	'The date this message/reminder "expires". Must be > .due_date it not NULL.';


\unset ON_ERROR_STOP
alter table dem.message_inbox drop constraint dem_inbox_sane_expiry_date;
\set ON_ERROR_STOP 1

alter table dem.message_inbox
	add constraint dem_inbox_sane_expiry_date check (
		(expiry_date is NULL)
			or
		(due_date is NULL)
			or
		(expiry_date > due_date)
	);


\unset ON_ERROR_STOP
insert into dem.message_inbox (
	fk_staff,
	fk_patient,
	fk_inbox_item_type,
	comment,
	due_date
) values (
	(select pk from dem.staff where db_user = 'any-doc'),
	(select pk_identity from dem.v_basic_person where
		firstnames = 'James Tiberius' and
		lastnames = 'Kirk' and
		date_trunc('day', dob) = '1931-3-21'
	),
	(select pk_type from dem.v_inbox_item_type where type = 'memo' and category = 'administrative'),
	'next medical exam for renewal of Starship Pilot License',
	now() - '2 days'::interval
);
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_message_inbox cascade;
\set ON_ERROR_STOP 1


create view dem.v_message_inbox as

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
		when due_date is null then null
		when due_date > now() then false
		when expiry_date is null then true
		when expiry_date < now() then false
		else true
	end
		as is_due,
	case
		when expiry_date is null then false
		when expiry_date > now() then false
		else true
	end
		as is_expired,
	gm.xid2int(mi.xmin)
		as xmin_message_inbox
from
	dem.message_inbox mi,
	dem.v_inbox_item_type vit
where
	mi.fk_inbox_item_type = vit.pk_type

union

select
	now() as received_when,
	'<system>' as modified_by,
	(select short_alias from dem.staff where dem.staff.pk = vo4dnd.pk_intended_reviewer)
		as provider,
	0	as importance,
	'clinical'
		as category,
	_('clinical')
		as l10n_category,
	'review docs'
		as type,
	_('review docs')
		as l10n_type,
	(select _('unreviewed documents for patient') || ' ['
		|| dn.lastnames || ', '
		|| dn.firstnames || ']'
	 from dem.names dn
	 where
	 	dn.id_identity = vo4dnd.pk_patient
	 		and
	 	dn.active is True
	)
	 	as comment,
	NULL::integer[]
		as pk_context,
	NULL::text
		as data,
	NULL::integer
		as pk_inbox_message,
	vo4dnd.pk_intended_reviewer
		as pk_staff,
	(select pk_category from dem.v_inbox_item_type where type = 'review docs')
		as pk_category,
	(select pk_type from dem.v_inbox_item_type where type = 'review docs')
		as pk_type,
	vo4dnd.pk_patient as pk_patient,
	true
		as is_virtual,
	NULL::date
		as due_date,
	NULL::date
		as expiry_date,
	NULL::boolean
		as is_due,
	NULL::boolean
		as is_expired,
	NULL::integer
		as xmin_message_inbox
from
	blobs.v_obj4doc_no_data vo4dnd
where
	reviewed is False

union

select
	now() as received_when,
	vtr.modified_by as modified_by,
	(select short_alias from dem.staff where dem.staff.pk = vtr.pk_intended_reviewer)
		as provider,
	0	as importance,
	'clinical'
		as category,
	_('clinical')
		as l10n_category,
	'review results'
		as type,
	_('review results')
		as l10n_type,
	(select _('unreviewed (normal) results for patient') || ' ['
		|| dn.lastnames || ', '
		|| dn.firstnames || ']'
	 from dem.names dn
	 where
	 	dn.id_identity = vtr.pk_patient
	 		and
	 	dn.active is True
	)
		as comment,
	NULL::integer[]
		as pk_context,
	NULL::text
		as data,
	NULL::integer
		as pk_inbox_message,
	vtr.pk_intended_reviewer
		as pk_staff,
	(select pk_category from dem.v_inbox_item_type where type = 'review results')
		as pk_category,
	(select pk_type from dem.v_inbox_item_type where type = 'review results')
		as pk_type,
	vtr.pk_patient as pk_patient,
	true
		as is_virtual,
	NULL::date
		as due_date,
	NULL::date
		as expiry_date,
	NULL::boolean
		as is_due,
	NULL::boolean
		as is_expired,
	NULL::integer
		as xmin_message_inbox
from
	clin.v_test_results vtr
where
	reviewed is false
		and
	(
		(is_technically_abnormal is false)
			or
		((is_technically_abnormal is null) and (abnormality_indicator is null))
	)

union

select
	now() as received_when,
	vtr.modified_by as modified_by,
	(select short_alias from dem.staff where dem.staff.pk = vtr.pk_intended_reviewer)
		as provider,
	1	as importance,
	'clinical'
		as category,
	_('clinical')
		as l10n_category,
	'review results'
		as type,
	_('review results')
		as l10n_type,
	(select _('unreviewed (abnormal) results for patient') || ' ['
		|| dn.lastnames || ', '
		|| dn.firstnames || ']'
	 from dem.names dn
	 where
	 	dn.id_identity = vtr.pk_patient
	 		and
	 	dn.active is True
	)
		as comment,
	NULL::integer[]
		as pk_context,
	NULL::text
		as data,
	NULL::integer
		as pk_inbox_message,
	vtr.pk_intended_reviewer
		as pk_staff,
	(select pk_category from dem.v_inbox_item_type where type = 'review results')
		as pk_category,
	(select pk_type from dem.v_inbox_item_type where type = 'review results')
		as pk_type,
	vtr.pk_patient as pk_patient,
	true
		as is_virtual,
	NULL::date
		as due_date,
	NULL::date
		as expiry_date,
	NULL::boolean
		as is_due,
	NULL::boolean
		as is_expired,
	NULL::integer
		as xmin_message_inbox
from
	clin.v_test_results vtr
where
	reviewed is false
		and
	(
		(is_technically_abnormal is true)
			or
		((is_technically_abnormal is null) and (abnormality_indicator is not null))
	)

;


comment on view dem.v_message_inbox is
'Denormalized messages for the providers and/or patients.
Using UNION makes sure we get the right level of uniqueness.';


grant select on dem.v_message_inbox to group "gm-doctors";

-- ==============================================================
select gm.log_script_insertion('v17-dem-v_message_inbox.sql', '17.0');
