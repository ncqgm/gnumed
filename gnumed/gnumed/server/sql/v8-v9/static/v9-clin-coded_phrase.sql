-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-coded_phrase.sql,v 1.1 2008-01-27 21:07:05 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.coded_narrative rename to coded_phrase;
alter table audit.log_coded_narrative rename to log_coded_phrase;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-coded_phrase.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-clin-coded_phrase.sql,v $
-- Revision 1.1  2008-01-27 21:07:05  ncq
-- - new
--
--