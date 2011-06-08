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
create table ref.tag_image (
	pk serial primary key,
	description text,
	filename text,
	image bytea
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-tag_image-static.sql', 'Revision: 1.1');

-- ==============================================================
