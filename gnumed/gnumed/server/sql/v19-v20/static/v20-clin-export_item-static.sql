-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table clin.export_item (
	pk serial primary key,
	fk_identity integer,
	created_by name,							-- not null default CURRENT_USER,
	created_when timestamp with time zone,		-- not null default NOW
	designation text,							-- "print" -> print manager
	description text,
	fk_doc_obj integer,
	data bytea,
	filename text
);
-- inherits (audit.audit_fields)

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-export_item-static.sql', '20.0');
