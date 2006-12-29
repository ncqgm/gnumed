-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: gmCreateProceduralLanguages.sql,v 1.2 2006-12-29 16:30:40 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\unset ON_ERROR_STOP

-- --------------------------------------------------------------
-- pl/pgSQL

-- 8,0+
create language 'plpgsql';


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
	WHEN (SELECT COUNT(oid) > 0 FROM pg_language WHERE lanname = 'plpgsql') THEN
		true
	ELSE
		(SELECT make_plpgsql())
    END
;

drop function make_plpgsql();

-- --------------------------------------------------------------
-- don't forget appropriate grants
--grant select on forgot_to_edit_grants to group "gm-doctors";

-- ==============================================================
-- $Log: gmCreateProceduralLanguages.sql,v $
-- Revision 1.2  2006-12-29 16:30:40  ncq
-- - drop helper function after use
--
-- Revision 1.1  2006/12/29 13:52:12  ncq
-- - factor out from bootstrapper proper
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
