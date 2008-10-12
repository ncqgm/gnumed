-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-allergy_state-static.sql,v 1.1 2008-10-12 14:59:25 ncq Exp $
-- $Revision: 1.1 $

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
update clin.allergy_state
set
	last_confirmed = modified_when
where
	has_allergy = 1;

update clin.allergy_state as a
set
	fk_encounter = (
		select cle.pk
		from clin.encounter cle
		where
			cle.fk_patient = a.fk_patient
		limit 1
	)
where
	a.fk_encounter is null
;

update clin.allergy_state
set
	has_allergy = 0,
	comment = 'undisclosed'
where
	has_allergy = -1
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
select gm.log_script_insertion('$RCSfile: v10-clin-allergy_state-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-allergy_state-static.sql,v $
-- Revision 1.1  2008-10-12 14:59:25  ncq
-- - new
--
--