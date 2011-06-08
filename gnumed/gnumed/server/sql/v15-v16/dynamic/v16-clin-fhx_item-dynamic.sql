-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table clin.fhx_item is
	'This table stores family history items on persons not otherwise in the database.';


-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-fhx_item-dynamic.sql', 'Revision: 1.1');
