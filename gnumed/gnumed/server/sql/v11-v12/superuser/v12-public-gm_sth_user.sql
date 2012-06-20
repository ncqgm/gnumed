-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v12-public-gm_sth_user.sql,v 1.1 2009-08-28 12:44:36 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_other_access('database upgrade v11 -> v12');


\unset ON_ERROR_STOP
drop function public.gm_create_user(name, text) cascade;
drop function public.gm_disable_user(name) cascade;
drop function public.gm_drop_user(name) cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-public-gm_sth_user.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-public-gm_sth_user.sql,v $
-- Revision 1.1  2009-08-28 12:44:36  ncq
-- - drop the gm_user functions we missed
--
--