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
alter table dem.staff
	drop column fk_role cascade;

alter table audit.log_staff
	drop column fk_role;

-- --------------------------------------------------------------
drop table dem.staff_role cascade;

drop table audit.log_staff_role;

delete from audit.audited_tables where schema = 'dem' and table_name = 'staff_role';

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-dem-staff-static.sql', '18.0');
