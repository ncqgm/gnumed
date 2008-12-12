-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v10-gm-access_log-dynamic.sql,v 1.1 2008-12-12 16:33:17 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;


-- --------------------------------------------------------------
create or replace function gm.is_null_or_blank_string(text)
	returns boolean
	language sql
	as 'select (coalesce(trim($1), '''') = '''');';


-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table gm.access_log drop constraint non_empty_user_action cascade;
\set ON_ERROR_STOP 1


alter table gm.access_log
	add constraint non_empty_user_action
		check (gm.is_null_or_blank_string(user_action) is false);


select audit.add_table_for_audit('gm', 'access_log');


comment on table gm.access_log is
'This logs access to the database and to records.
 Needed for HIPAA compliance among other things.';


-- no permissions for anyone except owner


-- document start of availability
insert into gm.access_log(user_action) values ('access log table created');

-- --------------------------------------------------------------
create or replace function gm.log_access2emr(text)
	returns void
	security definer
	language plpgsql
	as '
DECLARE
	_action alias for $1;
BEGIN

	if gm.is_null_or_blank_string(_action) then
		raise exception ''gm.log_access2emr(): action detail cannot be NULL or empty'';
	end if;

	insert into gm.access_log (user_action) values (''EMR access: '' || _action);

	return;
END;';


grant execute on function gm.log_access2emr(text) to group "gm-public";

comment on function gm.log_access2emr(text) is 'This logs access to a patient EMR.';

-- --------------------------------------------------------------
create or replace function gm.log_other_access(text)
	returns void
	security definer
	language sql
	as 'insert into gm.access_log (user_action) values ($1);';

grant execute on function gm.log_other_access(text) to group "gm-public";

comment on function gm.log_other_access(text) is 'This logs access to the database.';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-gm-access_log-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-gm-access_log-dynamic.sql,v $
-- Revision 1.1  2008-12-12 16:33:17  ncq
-- - HIPAA support
--
--