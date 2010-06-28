-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
--\unset ON_ERROR_STOP
--drop aggregate array_agg(anyelement);
--\set ON_ERROR_STOP 1

-- If the version of your PostgreSQL server is < 8.4 you will need to
-- create this aggregate in order to make vaccinations work properly:
CREATE AGGREGATE array_agg(anyelement) (
	SFUNC = array_append,
	STYPE = anyarray,
	INITCOND = ’{}’
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-array_agg.sql', 'Revision: 1.1');

