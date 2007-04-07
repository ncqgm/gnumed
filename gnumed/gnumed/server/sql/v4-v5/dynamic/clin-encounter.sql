-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: 
-- 
-- ==============================================================
-- $Id: clin-encounter.sql,v 1.2 2007-04-07 22:49:06 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
--\unset ON_ERROR_STOP
--drop forgot_to_edit_drops;
--\set ON_ERROR_STOP 1

-- adjust data
update clin.encounter
	set last_affirmed = (started + '1 second'::interval
where
	started > last_affirmed;
;


alter table clin.encounter
	add constraint encounter_must_start_before_it_ends
		check (started <= last_affirmed);

--comment on forgot_to_edit_comment is
--	'';

-- --------------------------------------------------------------
-- don't forget appropriate grants
--grant select on forgot_to_edit_grants to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-encounter.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: clin-encounter.sql,v $
-- Revision 1.2  2007-04-07 22:49:06  ncq
-- - need to adjust data before adding constraint
--
-- Revision 1.1  2007/02/04 15:31:40  ncq
-- - add check for END after START
--
-- Revision 1.6  2007/01/27 21:16:08  ncq
-- - the begin/commit does not fit into our change script model
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
