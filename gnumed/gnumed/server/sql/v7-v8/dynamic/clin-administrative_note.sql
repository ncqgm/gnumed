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
-- $Id: clin-administrative_note.sql,v 1.1 2007-11-04 22:57:56 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
--\unset ON_ERROR_STOP
--drop forgot_to_edit_drops;
--\set ON_ERROR_STOP 1

comment on table clin.administrative_note is
	'Narrative related to patients that is not of the clinical
	 but rather of the administrative variety (and thus does not
	 lend itself to SOAP classification).';

comment on column clin.administrative_note.fk_episode is
	'can explicitely be NULL to allow for non-episoded data';

select gm.add_table_for_notifies('clin', 'administrative_note', 'adm_note');

-- --------------------------------------------------------------
grant select, insert, update, delete on
	clin.administrative_note
	, clin.administrative_note_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: clin-administrative_note.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-administrative_note.sql,v $
-- Revision 1.1  2007-11-04 22:57:56  ncq
-- - new table
--
--