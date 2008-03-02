-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-test_result-static.sql,v 1.1 2008-03-02 11:25:01 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.test_result
	rename column note_provider to note_test_org;

alter table audit.log_test_result
	rename column note_provider to note_test_org;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-test_result-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-clin-test_result-static.sql,v $
-- Revision 1.1  2008-03-02 11:25:01  ncq
-- - new files
--
-- Revision 1.1  2008/02/26 16:24:01  ncq
-- - note_provider -> note_test_org
-- - fk_test_org -> nullable
--
--
