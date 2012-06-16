-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-allergy_state-static.sql,v 1.4 2009-01-27 12:41:30 ncq Exp $
-- $Revision: 1.4 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .comment
alter table clin.allergy_state
	add column comment
		text;

alter table audit.log_allergy_state
	add column comment
		text;


-- .last_confirmed
alter table clin.allergy_state
	add column last_confirmed
		timestamp with time zone;

alter table audit.log_allergy_state
	add column last_confirmed
		timestamp with time zone;


-- .fk_encounter
alter table clin.allergy_state
	add column fk_encounter
		integer
		references clin.encounter(pk);

alter table audit.log_allergy_state
	add column fk_encounter
		integer;


-- transform data
-- remove allergy state for patients without encounters
delete from clin.allergy_state
where
	fk_patient not in (
		select fk_patient from clin.encounter
	)
;

update clin.allergy_state
set
	has_allergy = 0,
	comment = 'undisclosed'
where
	has_allergy = -1
;

update clin.allergy_state
set
	last_confirmed = modified_when
where
	has_allergy in (0,1);

update clin.allergy_state
set
	fk_encounter = (
		select cle.pk
		from clin.encounter cle
		where
			cle.fk_patient = clin.allergy_state.fk_patient
		limit 1
	)
where
	clin.allergy_state.fk_encounter is null
;


-- .fk_patient
alter table clin.allergy_state
	drop column fk_patient;

alter table audit.log_allergy_state
	drop column fk_patient;


-- .id
alter table clin.allergy_state
	rename column id to pk;

alter table audit.log_allergy_state
	rename column id to pk;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-allergy_state-static.sql,v $', '$Revision: 1.4 $');

-- ==============================================================
-- $Log: v10-clin-allergy_state-static.sql,v $
-- Revision 1.4  2009-01-27 12:41:30  ncq
-- - reorder allergy state status change
--
-- Revision 1.3  2009/01/27 12:14:45  ncq
-- - remove dummy allergy state entries
--
-- Revision 1.2  2009/01/23 11:36:03  ncq
-- - don't use alias in update for the benefit of older PGs
--
-- Revision 1.1  2008/10/12 14:59:25  ncq
-- - new
--
--