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
drop domain if exists gm.nonempty_text restrict;

create domain gm.nonempty_text as text
	-- a subsequent column default overrides this domain/type default
	default NULL
	constraint chk__verify_nonempty_text check (
		-- do not concern ourselves with NULLness, leave that to SET (NOT) NULL
		(VALUE IS NULL)
			or
		trim(VALUE) != ''
	)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-gm-nonempty_text-domain.sql', '23.0');
