-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-incoming_data_unmatch-static.sql,v 1.1 2008-02-26 16:20:58 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.incoming_data_unmatched
	add column gender text;

alter table clin.incoming_data_unmatched
	add column requestor text;


alter table clin.incoming_data_unmatchable
	add column gender text;

alter table clin.incoming_data_unmatchable
	add column requestor text;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-incoming_data_unmatch-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-clin-incoming_data_unmatch-static.sql,v $
-- Revision 1.1  2008-02-26 16:20:58  ncq
-- - add gender/requestor
--
--
