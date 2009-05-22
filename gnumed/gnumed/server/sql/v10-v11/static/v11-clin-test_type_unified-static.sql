-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-clin-test_type_unified-static.sql,v 1.1 2009-05-22 10:59:01 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.test_type_unified
	rename column code to abbrev;


alter table clin.test_type_unified
	rename column coding_system to loinc;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-test_type_unified-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-clin-test_type_unified-static.sql,v $
-- Revision 1.1  2009-05-22 10:59:01  ncq
-- - new
--
--