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
comment on column dem.staff.public_key is 'The public GPG key for this staff member, ASCII armored.';

alter table dem.staff
	alter column public_key
		set default NULL;

-- --------------------------------------------------------------
drop view if exists dem.v_staff cascade;

create view dem.v_staff as
select
	d_vp.pk_identity
		as pk_identity,
	d_s.pk
		as pk_staff,
	d_vp.title
		as title,
	d_vp.firstnames
		as firstnames,
	d_vp.lastnames
		as lastnames,
	d_s.short_alias
		as short_alias,
	case
		when (select exists(select 1 from pg_group where
			groname = 'gm-doctors'
				and
			(select usesysid from pg_user where usename = d_s.db_user) = any(grolist)
		)) then 'full clinical access'
		when (select exists(select 1 from pg_group where
			groname = 'gm-nurses'
				and
			(select usesysid from pg_user where usename = d_s.db_user) = any(grolist)
		)) then 'limited clinical access'
		when (select exists(select 1 from pg_group where
			groname = 'gm-staff'
				and
			(select usesysid from pg_user where usename = d_s.db_user) = any(grolist)
		)) then 'non-clinical access'
		when (select exists(select 1 from pg_group where
			groname = 'gm-public'
				and
			(select usesysid from pg_user where usename = d_s.db_user) = any(grolist)
		)) then 'public access'
	end as role,
	d_vp.dob
		as dob,
	d_vp.gender
		as gender,
	d_s.db_user
		as db_user,
	d_s.comment
		as comment,
	d_s.is_active
		as is_active,
	d_s.public_key
		as public_key,
	d_vp.is_deleted
		as person_is_deleted,
	(select (
		select exists (
			SELECT 1
			from pg_group
			where
				(SELECT usesysid from pg_user where usename = d_s.db_user) = any(grolist)
					and
				groname = current_database()
		)
	) AND (
		select exists (
			SELECT 1
			from pg_group
			where
				(SELECT usesysid from pg_user where usename = d_s.db_user) = any(grolist)
					and
				groname = 'gm-logins'
		)
	)) as can_login,
	d_s.xmin
		as xmin_staff
from
	dem.staff d_s
		join dem.v_all_persons d_vp on d_s.fk_identity = d_vp.pk_identity
;

comment on view dem.v_staff is 'Denormalized staff data.';

revoke all on dem.v_staff from public;
grant select on dem.v_staff to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-dem-staff-dynamic.sql', '23.0');
