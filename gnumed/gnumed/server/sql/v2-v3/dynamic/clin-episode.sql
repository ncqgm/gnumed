-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - modify clin.episode
--
-- License: GPL
-- Author: Karsten Hilbert/Syan Tan
-- 
-- ==============================================================
-- $Id: clin-episode.sql,v 1.1 2006-09-25 10:55:01 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index clin.idx_episode_valid_issue;
drop index clin.idx_episode_with_issue;
drop index clin.idx_episode_without_issue;
\set ON_ERROR_STOP 1

create index idx_episode_with_issue on clin.episode(fk_health_issue) where fk_health_issue is not null;
comment on index clin.idx_episode_with_issue is
	'index episodes with associated health issue by their issue';

create index idx_episode_without_issue on clin.episode(fk_health_issue) where fk_health_issue is null;
comment on index clin.idx_episode_without_issue is
	'index episodes without associated health issue';

-- --------------------------------------------------------------
-- don't forget appropriate grants
--grant select on forgot_to_edit_grants to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-episode.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-episode.sql,v $
-- Revision 1.1  2006-09-25 10:55:01  ncq
-- - added here
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
