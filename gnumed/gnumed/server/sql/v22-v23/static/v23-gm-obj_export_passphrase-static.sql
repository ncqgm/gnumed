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
drop table if exists gm.obj_export_passphrase cascade;

create table gm.obj_export_passphrase (
	pk
		integer generated always as identity primary key,
	digest_type
		text,
	digest
		text,
	phrase
		text,
	description
		gm.nonempty_text
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-gm-obj_export_passphrase-static.sql', '23.0');
