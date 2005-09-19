-- GnuMed table change notification functionality
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/gmNotifications.sql,v $
-- $Revision: 1.6 $
-- license: GPL
-- author: Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
create table notifying_tables (
	pk serial primary key,
	schema name default null,
	table_name name not null,
	notification_name name not null,
	unique(table_name, notification_name)
);

comment on table notifying_tables is
	'All tables that want to send standard notifications
	 must be recorded in this table. Notification triggers
	 will be generated automatically for all tables recorded
	 here.';

-- ===================================================================
\unset ON_ERROR_STOP
drop function add_table_for_notifies (name);
drop function add_table_for_notifies (name, name);
\set ON_ERROR_STOP 1

create function add_table_for_notifies (name) returns unknown as '
DECLARE
	tbl_name ALIAS FOR $1;
	dummy RECORD;
BEGIN
	-- does table exist ?
	select relname into dummy from pg_class where relname = tbl_name;
	if not found then
		raise exception ''add_table_for_notifies: Table [%] does not exist.'', tbl_name;
		return false;
	end if;
	-- add definition
	insert into notifying_tables (
		table_name,
		notification_name
	) values (
		tbl_name,
		tbl_name
	);
	return true;
END;' language 'plpgsql';

comment on function add_table_for_notifies (name) is
	'sanity-checking convenience function for marking tables for notifying';

create function add_table_for_notifies (name, name) returns unknown as '
DECLARE
	tbl_name ALIAS FOR $1;
	sig_name ALIAS FOR $2;
	dummy RECORD;
BEGIN
	-- does table exist ?
	select relname into dummy from pg_class where relname = tbl_name;
	if not found then
		raise exception ''add_table_for_notifies: Table [%] does not exist.'', tbl_name;
		return false;
	end if;
	-- add definition
	insert into notifying_tables (
		table_name,
		notification_name
	) values (
		tbl_name,
		sig_name
	);
	return true;
END;' language 'plpgsql';

comment on function add_table_for_notifies (name, name) is
	'sanity-checking convenience function for marking tables for notifying';

-- ===================================================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmNotifications.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmNotifications.sql,v $', '$Revision: 1.6 $');

-- ===================================================================
-- $Log: gmNotifications.sql,v $
-- Revision 1.6  2005-09-19 16:38:51  ncq
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
