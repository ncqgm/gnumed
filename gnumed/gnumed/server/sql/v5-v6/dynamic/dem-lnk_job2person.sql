-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v5
-- Target database version: v6
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: dem-lnk_job2person.sql,v 1.1 2007-06-01 14:32:33 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
grant select, insert, update, delete on dem.lnk_job2person_pk_seq to group "gm-doctors";
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: dem-lnk_job2person.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: dem-lnk_job2person.sql,v $
-- Revision 1.1  2007-06-01 14:32:33  ncq
-- - missing grant
--
-- Revision 1.1.2.1  2007/06/01 14:03:37  ncq
-- - needed on genuine 8.1 systems
--
--