-- Project: GnuMed - database housekeeping TODO tables
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmHousekeeping.sql,v $
-- $Revision: 1.3 $
-- license: GPL
-- author: Karsten Hilbert

-- This script provides tables used in collecting pending
-- housekeeping tasks. Demons, integrity checkers and auto-running
-- workers (say, import scripts) can use this to deliver messages
-- if they cannot count on a human user interacting with them.

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
create table housekeeping_todo (
	pk serial primary key,
	reported_when timestamp with time zone not null default CURRENT_TIMESTAMP,
	reported_by text not null,
	reported_to text
		not null
		default 'admin'
		check (reported_to in ('user', 'admin')),
	problem text not null,
	solution text
);

-- =============================================
GRANT select, insert ON
	housekeeping_todo
	, housekeeping_todo_pk_seq
TO GROUP "gm-public";

-- should be "admin" ...
GRANT select, insert, update, delete on
	housekeeping_todo
	, housekeeping_todo_pk_seq
TO GROUP "_gm-doctors";

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmHousekeeping.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmHousekeeping.sql,v $', '$Revision: 1.3 $');

-- =============================================
-- $Log: gmHousekeeping.sql,v $
-- Revision 1.3  2004-04-19 12:47:49  ncq
-- - translate request_status
-- - add housekeeping_todo.reported_to
--
-- Revision 1.2  2004/03/18 09:50:19  ncq
-- - fixed GRANTs
--
-- Revision 1.1  2004/03/16 15:55:42  ncq
-- - use for housekeeping, etc.
--
