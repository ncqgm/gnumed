-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v12-clin-procedure-static.sql,v 1.1 2009-09-13 18:20:19 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table clin.procedure (
	pk serial
		primary key,
	clin_where text,
	fk_hospital_stay integer
		references clin.hospital_stay(pk)
) inherits (clin.clin_root_item);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-procedure-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-clin-procedure-static.sql,v $
-- Revision 1.1  2009-09-13 18:20:19  ncq
-- - add new table
--
--