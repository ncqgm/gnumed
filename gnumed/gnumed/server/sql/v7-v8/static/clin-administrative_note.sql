-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v7
-- Target database version: v8
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: clin-administrative_note.sql,v 1.1 2007-11-04 22:58:21 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
--\unset ON_ERROR_STOP
--drop forgot_to_edit_drops;
--\set ON_ERROR_STOP 1

create table clin.administrative_note (
	pk serial primary key,
	fk_encounter integer
		not null
		references clin.encounter(pk)
		on update cascade
		on delete restrict,
	fk_episode integer
--		not null
		references clin.episode(pk)
		on update cascade
		on delete restrict,
	clin_when timestamp with time zone
		not null
		default CURRENT_TIMESTAMP,
	narrative text
		not null
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: clin-administrative_note.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-administrative_note.sql,v $
-- Revision 1.1  2007-11-04 22:58:21  ncq
-- - new table
--
--