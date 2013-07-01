-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table ref.paperwork_templates
	add column edit_after_substitution boolean;

alter table audit.log_paperwork_templates
	add column edit_after_substitution boolean;

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-ref-paperwork_templates-static.sql', '19.0');
