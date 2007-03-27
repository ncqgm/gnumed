-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: cfg-cfg_str_array.sql,v 1.2 2007-03-27 17:38:39 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
insert into cfg.cfg_str_array
	(fk_item, value)
values (
	(select pk from cfg.cfg_item where workplace = 'Release 0.2.5'),
	'{"gmProviderInboxPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmNotebookedProgressNoteInputPlugin","gmEMRJournalPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmXdtViewer","gmManual","gmConfigRegistry"}'
);

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: cfg-cfg_str_array.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: cfg-cfg_str_array.sql,v $
-- Revision 1.2  2007-03-27 17:38:39  ncq
-- - backported from branch
--
-- Revision 1.1.2.1  2007/03/27 17:30:57  ncq
-- - added workplace
--
--