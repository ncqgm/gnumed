-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten.Hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
drop function if exists dem.trf_prevent_deletion_of_in_use_staff() cascade;

create or replace function dem.trf_prevent_deletion_of_in_use_staff()
	returns trigger
	 language 'plpgsql'
	as '
BEGIN
	-- does any audited table contain the dem.staff.db_user we are about to delete ?
	PERFORM 1 FROM audit.audit_fields WHERE modified_by = OLD.db_user LIMIT 1;
	IF FOUND THEN
		RAISE EXCEPTION
			''DELETE from dem.staff: Sanity check failed. User <%> is referenced from <.modified_by> of at least one audited table.'', OLD.db_user
			USING ERRCODE = ''foreign_key_violation''
		;
		RETURN NULL;
	END IF;

	-- does any audit table contain the dem.staff.db_user we are about to delete ?
	PERFORM 1 FROM audit.audit_trail WHERE orig_by = OLD.db_user OR audit_by = OLD.db_user LIMIT 1;
	IF FOUND THEN
		RAISE EXCEPTION
			''DELETE from dem.staff: Sanity check failed. User <%> is referenced from <.orig_by> or <.audit_by> of at least one audit table.'', OLD.db_user
			USING ERRCODE = ''foreign_key_violation''
		;
		RETURN NULL;
	END IF;

	RETURN OLD;
END;
';

comment on function dem.trf_prevent_deletion_of_in_use_staff() is
	'this function is used to prevent DELETEs of staff members which had been used to store data';


drop trigger if exists tr_prevent_deletion_of_in_use_staff on dem.staff cascade;

create trigger tr_prevent_deletion_of_in_use_staff
	before delete on dem.staff
	for each row execute procedure dem.trf_prevent_deletion_of_in_use_staff();

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
select gm.log_script_insertion('v21-dem-staff-dynamic.sql', '21.0');
