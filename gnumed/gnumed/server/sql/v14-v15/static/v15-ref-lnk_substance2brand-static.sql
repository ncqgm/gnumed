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
create table ref.lnk_substance2brand (
	pk serial primary key,
	fk_brand integer,
	fk_substance integer,
	amount decimal,
	unit text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-lnk_substance2brand-static.sql', 'Revision: 1.1');

-- ==============================================================
