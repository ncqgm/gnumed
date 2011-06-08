-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-clin-test_type-static.sql,v 1.1 2009-05-22 10:59:01 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.test_type
	add column
		loinc text
;

alter table audit.log_test_type
	add column
		loinc text
;


alter table clin.test_type
	add column
		abbrev text
;

alter table audit.log_test_type
	add column
		abbrev text
;


update clin.test_type
	set abbrev = code
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-test_type-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-clin-test_type-static.sql,v $
-- Revision 1.1  2009-05-22 10:59:01  ncq
-- - new
--
--