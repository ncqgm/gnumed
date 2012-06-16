-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-clin-episode-static.sql,v 1.2 2009-09-01 22:44:15 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.episode
	add column diagnostic_certainty_classification text;


alter table audit.log_episode
	add column diagnostic_certainty_classification text;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-episode-static.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v12-clin-episode-static.sql,v $
-- Revision 1.2  2009-09-01 22:44:15  ncq
-- - diagnostic-certainty -> *-classification
--
-- Revision 1.1  2009/08/28 12:42:37  ncq
-- - add diagnostic certainty
--
--
