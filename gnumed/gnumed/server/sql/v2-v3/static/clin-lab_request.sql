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
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.lab_request
	drop constraint if exists "$2";
alter table clin.lab_request
	drop constraint if exists "lab_request_fk_requestor_fkey";

alter table clin.lab_request
	add foreign key(fk_requestor)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-lab_request.sql,v $', '$Revision: 1.2 $');
