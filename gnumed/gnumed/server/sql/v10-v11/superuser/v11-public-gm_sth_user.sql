-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_other_access('database upgrade v10 -> v11');


drop function if exists public.gm_transfer_users(text) cascade;
drop function if exists public.gm_create_user(text) cascade;
drop function if exists public.gm_disable_user(text) cascade;
drop function if exists public.gm_drop_user(text) cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-public-gm_sth_user.sql,v $', '$Revision: 1.1 $');
