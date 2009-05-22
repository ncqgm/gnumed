-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-clin-test_type-dynamic.sql,v 1.1 2009-05-22 10:57:49 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.test_type
	alter column abbrev
		set not null;


alter table clin.test_type
	alter column name
		set not null;


alter table clin.test_type
	alter column code
		drop not null;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-test_type-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-clin-test_type-dynamic.sql,v $
-- Revision 1.1  2009-05-22 10:57:49  ncq
-- - new
--
--