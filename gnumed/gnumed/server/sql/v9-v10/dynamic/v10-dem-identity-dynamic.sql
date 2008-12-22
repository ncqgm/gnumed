-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-dem-identity-dynamic.sql,v 1.1 2008-12-22 18:57:00 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------


-- transfer TOB from DOB
update dem.identity
	set tob = (dob at time zone 'UTC')::time ;


-- normalize time part of DOB
update dem.identity
	set dob = date_trunc('day', dob at time zone 'UTC') + '11 hours 11 minutes 11 seconds 111 milliseconds'::interval;


-- add trigger to always normalize time part of DOB
create or replace function dem.trf_normalize_time_in_dob()
	returns trigger
	language plpgsql
	as '
BEGIN
	if NEW.dob is NULL then
		return NEW;
	end if;

	NEW.dob = date_trunc(''day'', NEW.dob at time zone ''UTC'') +
		''11 hours 11 minutes 11 seconds 111 milliseconds''::interval;

	return NEW;
END;';

create trigger tr_normalize_time_in_dob
	after insert or update on dem.identity
	for each row execute procedure dem.trf_normalize_time_in_dob()
;


-- make dob nullable
\unset ON_ERROR_STOP
alter table dem.identity
	alter column dob
		drop not null;
\set ON_ERROR_STOP 1

-- FIXME: need to somehow ensure patients do get a DOB !


-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-dem-identity-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-dem-identity-dynamic.sql,v $
-- Revision 1.1  2008-12-22 18:57:00  ncq
-- - support .tob
--
--