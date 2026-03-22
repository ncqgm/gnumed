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
-- $Id: clin-waiting_list.sql,v 1.2 2006-10-28 12:22:48 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.waiting_list
	drop constraint if exists "$1";
alter table clin.waiting_list
	drop constraint if exists "waiting_list_fk_patient_fkey";

alter table clin.waiting_list
	add foreign key(fk_patient)
		references dem.identity(pk)
		on update cascade
		on delete cascade;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-waiting_list.sql,v $', '$Revision: 1.2 $');
