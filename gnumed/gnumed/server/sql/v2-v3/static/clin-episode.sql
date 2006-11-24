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
-- $Id: clin-episode.sql,v 1.3 2006-11-24 09:21:50 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table clin.episode
	drop constraint "$2";
alter table clin.episode
	drop constraint "episode_fk_patient_fkey";
\set ON_ERROR_STOP 1

alter table clin.episode
	add foreign key(fk_patient)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-episode.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: clin-episode.sql,v $
-- Revision 1.3  2006-11-24 09:21:50  ncq
-- - whitespace fix
--
-- Revision 1.2  2006/10/28 23:39:18  ncq
-- - $2 -> explicit name
--
-- Revision 1.1  2006/10/24 13:08:26  ncq
-- - mainly changes due to dropped clin.xlnk_identity
--
--
