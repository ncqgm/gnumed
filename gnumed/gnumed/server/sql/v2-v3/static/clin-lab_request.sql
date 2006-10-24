-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: clin-lab_request.sql,v 1.1 2006-10-24 13:08:26 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
begin;

alter table clin.lab_request
	drop constraint "$2";

alter table clin.lab_request
	add foreign key(fk_requestor)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-lab_request.sql,v $', '$Revision: 1.1 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: clin-lab_request.sql,v $
-- Revision 1.1  2006-10-24 13:08:26  ncq
-- - mainly changes due to dropped clin.xlnk_identity
--
--
