-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_other_access('database upgrade v11 -> v12');


drop function if exists public.gm_create_user(name, text) cascade;
drop function if exists public.gm_disable_user(name) cascade;
drop function if exists public.gm_drop_user(name) cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-public-gm_sth_user.sql,v $', '$Revision: 1.1 $');
