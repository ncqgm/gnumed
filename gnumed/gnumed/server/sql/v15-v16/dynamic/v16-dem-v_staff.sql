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
grant usage on sequence dem.enum_comm_types_id_seq to group "gm-public";

-- fix the sequence, no idea how it got there
select setval('dem.enum_comm_types_id_seq'::regclass, (select max(pk) from dem.enum_comm_types));

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_staff cascade;
\set ON_ERROR_STOP 1


create view dem.v_staff as
select
	vbp.pk_identity as pk_identity,
	s.pk as pk_staff,
	vbp.title as title,
	vbp.firstnames as firstnames,
	vbp.lastnames as lastnames,
	s.short_alias as short_alias,
	sr.name as role,
	_(sr.name) as l10n_role,
	vbp.dob as dob,
	vbp.gender as gender,
	s.db_user as db_user,
	s.comment as comment,
	s.is_active as is_active,
	(select (
		select exists (
			SELECT 1
			from pg_group
			where
				(SELECT usesysid from pg_user where usename = s.db_user) = any(grolist)
					and
				groname = current_database()
		)
	) AND (
		select exists (
			SELECT 1
			from pg_group
			where
				(SELECT usesysid from pg_user where usename = s.db_user) = any(grolist)
					and
				groname = 'gm-logins'
		)
	)) as can_login,
	s.xmin as xmin_staff,
	s.fk_role as pk_role
from
	dem.staff s
		join dem.staff_role sr on s.fk_role = sr.pk
			join dem.v_basic_person vbp on s.fk_identity = vbp.pk_identity
;


comment on view dem.v_staff is 'Denormalized staff data.';


revoke all on dem.v_staff from public;
grant select on dem.v_staff to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-dem-v_staff.sql', 'Revision 1');

-- ==============================================================
