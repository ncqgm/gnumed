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
-- $Id: clin-episode.sql,v 1.3 2006-11-24 09:21:50 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.episode
	drop constraint if exists "$2";
alter table clin.episode
	drop constraint if exists "episode_fk_patient_fkey";

alter table clin.episode
	add foreign key(fk_patient)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-episode.sql,v $', '$Revision: 1.3 $');
