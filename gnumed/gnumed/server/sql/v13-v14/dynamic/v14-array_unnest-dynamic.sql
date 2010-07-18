-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

set check_function_bodies to on;
set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function public.unnest(anyarray) cascade;
\set ON_ERROR_STOP 1


-- If the version of your PostgreSQL server is < 8.4 you will need to
-- create this function in order to make vaccinations work properly:
CREATE OR REPLACE FUNCTION public.unnest(anyarray)
	RETURNS SETOF anyelement
	AS '
SELECT $1[i] FROM
	generate_series (
		array_lower($1,1),
		array_upper($1,1)
	) i
;'
	LANGUAGE 'sql'
	IMMUTABLE
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-array_unnest-dynamic.sql', 'Revision: 1.1');
