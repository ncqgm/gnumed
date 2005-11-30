-- GnuMed table change notification functionality
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmNotifications-static.sql,v $
-- $Revision: 1.1 $
-- license: GPL
-- author: Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
create table public.notifying_tables (
	pk serial primary key,
	schema name default null,
	table_name name not null,
	notification_name name not null,
	-- FIXME: drop 	unique(table_name, notification_name) in update script
	unique(schema, table_name)
);

-- ===================================================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmNotifications-static.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmNotifications-static.sql,v $', '$Revision: 1.1 $');

-- ===================================================================
-- $Log: gmNotifications-static.sql,v $
-- Revision 1.1  2005-11-30 17:04:20  ncq
-- - factor into dynamic/static stuff, rename static stuff file
--
-- Revision 1.6  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.5  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.4  2004/08/16 19:58:01  ncq
-- - allow the same notification to be sent from different
--   tables (but not from the same one)
--
-- Revision 1.3  2004/03/10 00:03:52  ncq
-- - delete from schema revision table before insertion
--
-- Revision 1.2  2003/11/28 10:08:38  ncq
-- - fix typos
--
-- Revision 1.1  2003/11/28 08:30:54  ncq
-- - tables that get standard notify triggers are handled by this
--
