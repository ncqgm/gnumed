-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
create table dem.identity_tag (
	pk serial primary key,
	fk_identity integer,
	fk_tag integer,
	comment text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-dem-identity_tag-static.sql', 'Revision: 1.1');

-- ==============================================================
