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
-- $Id: cfg-cfg_str_array.sql,v 1.2 2007-01-24 10:56:35 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
insert into cfg.cfg_str_array
	(fk_item, value)
values (
	(select pk from cfg.cfg_item where workplace = 'Release 0.2.4'),
	'{"gmProviderInboxPlugin","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmNotebookedProgressNoteInputPlugin","gmEMRJournalPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmXdtViewer","gmManual","gmConfigRegistry"}'
);

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: cfg-cfg_str_array.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: cfg-cfg_str_array.sql,v $
-- Revision 1.2  2007-01-24 10:56:35  ncq
-- - setup workplace for 0.2.4
--
-- Revision 1.1.2.1  2007/01/23 15:07:35  ncq
-- - add "Release 0.2.4" workplace
--
-- Revision 1.3  2006/12/29 11:33:19  ncq
-- - Release 0.2.3 default workplace is called just that, "Release 0.2.3"
--
