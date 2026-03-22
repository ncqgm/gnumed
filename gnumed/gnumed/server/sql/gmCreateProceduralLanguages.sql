-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- pl/pgSQL

-- 8,0+
--create language 'plpgsql';		-- likely never worked
create or replace language plpgsql;


-- 7.4+
CREATE OR REPLACE FUNCTION make_plpgsql()
	RETURNS bool
	LANGUAGE SQL
	AS '
create or replace function plpgsql_call_handler()
	returns language_handler
	language ''C''
	as ''plpgsql'';
create trusted language "plpgsql" handler "plpgsql_call_handler";
select true;
';

SELECT CASE
	WHEN (SELECT COUNT(1) > 0 FROM pg_language WHERE lanname = 'plpgsql') THEN
		true
	ELSE
		(SELECT make_plpgsql())
    END
;

drop function if exists make_plpgsql();


-- try creating a function which will fail if it doesn't exist
drop function if exists check_plpgsql_existence();

create function check_plpgsql_existence()
	returns bool
	language 'plpgsql'
	as '
BEGIN
	return true;
END;';

drop function if exists check_plpgsql_existence();

-- --------------------------------------------------------------
