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
drop extension if exists btree_gist cascade;
create extension btree_gist;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-reinstall-btree_gist.sql', '23.0');
