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
-- $Id: v8-dem_lnk_job2person.sql,v 1.1 2007-12-09 20:43:11 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- rename columns
alter table audit.log_lnk_job2person
	rename column id to pk;

alter table audit.log_lnk_job2person
	rename column id_identity to fk_identity;

alter table audit.log_lnk_job2person
	rename column id_occupation to fk_occupation;

alter table audit.log_lnk_job2person
	rename column comment to activities;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v8-dem_lnk_job2person.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v8-dem_lnk_job2person.sql,v $
-- Revision 1.1  2007-12-09 20:43:11  ncq
-- - need to upgrade log table, too
--
-- Revision 1.1  2006/11/19 10:17:03  ncq
-- - rename columns to better reflect usage
