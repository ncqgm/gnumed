-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-test_result-dynamic.sql,v 1.2 2008-03-02 11:28:18 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on column clin.test_result.note_test_org is
	'A comment on the test result provided by the tester or testing entity.';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-test_result-dynamic.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v9-clin-test_result-dynamic.sql,v $
-- Revision 1.2  2008-03-02 11:28:18  ncq
-- - renaming col must be done in static
--
-- Revision 1.1  2008/02/26 16:24:01  ncq
-- - note_provider -> note_test_org
-- - fk_test_org -> nullable
--
--
