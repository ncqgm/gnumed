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
\unset ON_ERROR_STOP

alter table cfg.cfg_numeric
	add column pk serial;

alter table cfg.cfg_numeric
	add primary key (pk);



alter table cfg.cfg_string
	add column pk serial;

alter table cfg.cfg_string
	add primary key (pk);



alter table cfg.cfg_str_array
	add column pk serial;

alter table cfg.cfg_str_array
	add primary key (pk);

\set ON_ERROR_STOP 1
-- --------------------------------------------------------------
select gm.log_script_insertion('v18-cfg-cfg_-static.sql', '18.0');
