-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: 
--
-- ==============================================================
-- $Id: v11-dem-v_staff.sql,v 1.2 2009-08-08 10:42:48 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table dem.staff
	drop constraint each_role_once_per_identity;
\set ON_ERROR_STOP 1

alter table dem.staff
	add constraint each_role_once_per_identity
		unique(fk_role, fk_identity);


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
	_(sr.name) as role,
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
select gm.log_script_insertion('$RCSfile: v11-dem-v_staff.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v11-dem-v_staff.sql,v $
-- Revision 1.2  2009-08-08 10:42:48  ncq
-- - add constraint on role/identity
--
-- Revision 1.1  2009/07/15 12:13:35  ncq
-- - need to recreate after dem.v_basic_person
--
--