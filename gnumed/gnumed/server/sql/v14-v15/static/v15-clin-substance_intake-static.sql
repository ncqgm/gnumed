-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
alter table clin.substance_intake
	add column fk_drug_component integer;

alter table audit.log_substance_intake
	add column fk_drug_component integer;


-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-lnk_substance2brand-static.sql', 'Revision: 1.1');

-- ==============================================================
