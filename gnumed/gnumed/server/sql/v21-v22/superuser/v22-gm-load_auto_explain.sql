-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
drop function if exists gm.load_auto_explain(IN _min_duration integer) cascade;

create or replace function gm.load_auto_explain(IN _min_duration integer)
	returns boolean
	language 'plpgsql'
	security definer
	as '
BEGIN
	IF _min_duration < 2000 THEN
		_min_duration := 2000;
	END IF;
	LOAD ''auto_explain'';
	PERFORM set_config(''auto_explain.log_min_duration''::TEXT, _min_duration::TEXT, false);
	PERFORM set_config(''auto_explain.log_analyze''::TEXT, ''ON''::TEXT, false);
	PERFORM set_config(''auto_explain.log_verbose''::TEXT, ''ON''::TEXT, false);
	PERFORM set_config(''auto_explain.log_timing''::TEXT, ''ON''::TEXT, false);
	RETURN TRUE;
END;';

COMMENT ON FUNCTION gm.load_auto_explain(IN _min_duration integer) IS
'Load and configure auto_explain.
.
Integer argument = auto_explain.log_min_duration in milliseconds with a lower bound of 2000.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-gm-load_auto_explain.sql', '22.25');
