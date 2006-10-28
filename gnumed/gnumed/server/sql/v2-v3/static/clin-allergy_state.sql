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
-- $Id: clin-allergy_state.sql,v 1.2 2006-10-28 12:22:48 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table clin.allergy_state
	drop constraint "$1";
alter table clin.allergy_state
	drop constraint "allergy_state_fk_patient_fkey";
\set ON_ERROR_STOP 1

alter table clin.allergy_state
	add foreign key(fk_patient)
		references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-allergy_state.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: clin-allergy_state.sql,v $
-- Revision 1.2  2006-10-28 12:22:48  ncq
-- - 8.1 prides itself in naming FKs differently -- better -- but makes
--   changing auto-named foreign keys a pain
--
-- Revision 1.1  2006/10/24 13:08:26  ncq
-- - mainly changes due to dropped clin.xlnk_identity
--
--
