-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-public-gm_sth_user.sql,v 1.1 2009-03-16 15:14:45 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_other_access('database upgrade v10 -> v11');


\unset ON_ERROR_STOP
drop function public.gm_transfer_users(text) cascade;
drop function public.gm_create_user(text) cascade;
drop function public.gm_disable_user(text) cascade;
drop function public.gm_drop_user(text) cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-public-gm_sth_user.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-public-gm_sth_user.sql,v $
-- Revision 1.1  2009-03-16 15:14:45  ncq
-- - new
--
--