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
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- don't forget appropriate grants
grant select, insert, update, delete on clin.operation to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-operation.sql,v $', '$Revision: 1.1 $');
