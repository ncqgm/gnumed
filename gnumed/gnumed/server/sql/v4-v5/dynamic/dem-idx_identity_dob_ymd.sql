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
-- $Id: dem-idx_identity_dob_ymd.sql,v 1.2 2007-02-19 11:10:02 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop index dem.idx_identity_dob cascade;
drop index dem.idx_identity_dob_ymd cascade;
\set ON_ERROR_STOP 1


create index idx_identity_dob_ymd on dem.identity(date_trunc('day', dob at time zone 'UTC'));


comment on index dem.idx_identity_dob_ymd is
	'When searching for patients per DOB this will usually
	 happen with no more precision than "day". Need to
	 normalize to UTC zone, however.';

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: dem-idx_identity_dob_ymd.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: dem-idx_identity_dob_ymd.sql,v $
-- Revision 1.2  2007-02-19 11:10:02  ncq
-- - fix index creation - function needs to be immutable
--
-- Revision 1.1  2007/02/10 23:42:47  ncq
-- - fix return type on rule function
-- - add date_trunc('day', dob) index
--
-- Revision 1.6  2007/01/27 21:16:08  ncq
-- - the begin/commit does not fit into our change script model
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
