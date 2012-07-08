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
GRANT USAGE ON SEQUENCE
	cfg.cfg_numeric_pk_seq,
	cfg.cfg_string_pk_seq,
	cfg.cfg_str_array_pk_seq
to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-cfg-cfg_-dynamic.sql', '18.0');
