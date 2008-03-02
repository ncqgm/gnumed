-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-episode-static.sql,v 1.1 2008-03-02 11:25:01 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.episode add column
	fk_encounter integer
		references clin.encounter(pk)
		on update cascade
		on delete restrict;

alter table audit.log_episode add column fk_encounter integer;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-episode-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-clin-episode-static.sql,v $
-- Revision 1.1  2008-03-02 11:25:01  ncq
-- - new files
--
--
