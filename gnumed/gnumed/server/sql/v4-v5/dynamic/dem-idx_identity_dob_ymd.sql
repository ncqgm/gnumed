-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependent objects possibly dropped by CASCADE
drop function if exists dem.date_trunc_utc(text, timestamp with time zone) cascade;
drop index if exists dem.idx_identity_dob cascade;
drop index if exists dem.idx_identity_dob_ymd cascade;


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
