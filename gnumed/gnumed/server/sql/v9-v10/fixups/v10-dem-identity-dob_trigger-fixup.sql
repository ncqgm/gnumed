-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-dem-identity-dob_trigger-fixup.sql,v 1.2 2009-05-18 09:46:55 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- fix trigger
\unset ON_ERROR_STOP
drop function dem.trf_normalize_time_in_dob() cascade;
\set ON_ERROR_STOP 1


create or replace function dem.trf_normalize_time_in_dob()
	returns trigger
	language plpgsql
	as '
BEGIN
	if NEW.dob is NULL then
		return NEW;
	end if;

	NEW.dob = date_trunc(''day'', NEW.dob) + ''11 hours 11 minutes 11 seconds 111 milliseconds''::interval;

	return NEW;
END;';

create trigger tr_normalize_time_in_dob
	before insert or update on dem.identity
	for each row execute procedure dem.trf_normalize_time_in_dob()
;


-- add analysis query
delete from cfg.report_query where label = 'patients whose date of birth may be wrong by one day due to a bug in version 0.4';

insert into cfg.report_query (label, cmd) values (
	'patients whose date of birth may be wrong by one day due to a bug in version 0.4',
'select pk as pk_patient, *
from
	dem.identity
where
	modified_when between (
		-- when was the faulty script imported
		select imported from gm_schema_revision where filename like ''%v10-dem-identity-dynamic.sql%''
	) and (
		-- when was this fixup script imported
		select imported from gm_schema_revision where filename = ''$RCSfile: v10-dem-identity-dob_trigger-fixup.sql,v $''
	)
');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-dem-identity-dob_trigger-fixup.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v10-dem-identity-dob_trigger-fixup.sql,v $
-- Revision 1.2  2009-05-18 09:46:55  ncq
-- - new
--
-- Revision 1.1.2.1  2009/05/15 14:52:26  ncq
-- - fix faulty DOB trigger logic
--
--