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
create table ref.person_tag (
	pk serial primary key,
	description text,
	short_description text,
	image bytea
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-person_tag-static.sql', 'Revision: 1.1');

-- ==============================================================
