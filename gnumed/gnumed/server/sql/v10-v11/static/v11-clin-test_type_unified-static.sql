-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-clin-test_type_unified-static.sql,v 1.2 2009-05-24 16:35:55 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.test_type_unified
	rename to meta_test_type;


alter table clin.meta_test_type
	rename column code to abbrev;


alter table clin.meta_test_type
	rename column coding_system to loinc;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-test_type_unified-static.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v11-clin-test_type_unified-static.sql,v $
-- Revision 1.2  2009-05-24 16:35:55  ncq
-- - rename table to "meta"
--
-- Revision 1.1  2009/05/22 10:59:01  ncq
-- - new
--
--