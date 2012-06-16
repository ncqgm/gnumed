-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v13-clin-test_org-static.sql,v 1.1 2010-02-02 13:32:43 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.test_org
	add column contact text;

alter table audit.log_test_org
	add column contact text;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v13-clin-test_org-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v13-clin-test_org-static.sql,v $
-- Revision 1.1  2010-02-02 13:32:43  ncq
-- - add .contact
--
--