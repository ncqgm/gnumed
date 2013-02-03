-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
-- observed in the wild at least once
alter table clin.clin_narrative drop constraint clin_narrative_soap_cat_check cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-clin-clin_narrative-fixup.sql', '17.9');
