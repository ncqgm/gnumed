-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: dem-idx_identity_dob_ymd.sql,v 1.4 2007-02-19 16:41:00 ncq Exp $
-- $Revision: 1.4 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop function dem.date_trunc_utc(text, timestamp with time zone) cascade;
drop index dem.idx_identity_dob cascade;
drop index dem.idx_identity_dob_ymd cascade;
\set ON_ERROR_STOP 1


create function dem.date_trunc_utc(text, timestamp with time zone)
	returns timestamp
	immutable
	language SQL
	as 'select date_trunc($1, $2 at time zone ''UTC'');'
;

comment on function dem.date_trunc_utc(text, timestamp with time zone) is
	'date_trunc() is not immutable because it depends on the timezone
	 setting, hence need to use this in index creation, but also need
	 to use it in queries which want to use that index, so make it
	 generally available as a function';


create index idx_identity_dob_ymd on dem.identity(dem.date_trunc_utc('day'::text, dob));

comment on index dem.idx_identity_dob_ymd is
	'When searching for patients per DOB this will usually
	 happen with no more precision than "day". Need to
	 normalize to UTC zone, however.';


-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: dem-idx_identity_dob_ymd.sql,v $', '$Revision: 1.4 $');

-- ==============================================================
-- $Log: dem-idx_identity_dob_ymd.sql,v $
-- Revision 1.4  2007-02-19 16:41:00  ncq
-- - add dem.date_trunc_utc() as a convenience
--
-- Revision 1.3  2007/02/19 15:01:47  ncq
-- - make date_trunc() index immutable as per discussion on postgresql list
--
-- Revision 1.2  2007/02/19 11:10:02  ncq
-- - fix index creation - function needs to be immutable
--
-- Revision 1.1  2007/02/10 23:42:47  ncq
-- - fix return type on rule function
-- - add date_trunc('day', dob) index
--
