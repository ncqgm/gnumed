-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v6
-- Target database version: v7
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: dem-dob_is_in_range.sql,v 1.1 2007-09-10 12:19:56 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create or replace function dem.dob_is_in_range(timestamp with time zone, interval, interval)
	returns boolean
	language sql
	as '
select
	($1 - (extract(year from $1) * ''1 year''::interval)) -
	(now() - (extract(year from now()) * ''1 year''::interval))
	between (-1 * $2) and $3'
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: dem-dob_is_in_range.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: dem-dob_is_in_range.sql,v $
-- Revision 1.1  2007-09-10 12:19:56  ncq
-- - new in the mix
--
--
