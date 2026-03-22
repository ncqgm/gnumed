-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-test_result-static.sql,v 1.5 2008-12-01 12:19:25 ncq Exp $
-- $Revision: 1.5 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.test_result
	rename column note_provider to note_test_org;

alter table audit.log_test_result
	rename column note_provider to note_test_org;

drop trigger zt_upd_test_result on clin.test_result;

alter table clin.test_result
	drop constraint "test_result_fk_intended_reviewer_fkey" cascade;

update clin.test_result set
	fk_intended_reviewer = (
		select pk_staff
		from dem.v_staff
		where firstnames='Leonard Horatio' and lastnames='McCoy' and dob='1920-1-20+2:00'
	)
where
	fk_intended_reviewer = (
		select pk_identity
		from dem.v_staff
		where firstnames='Leonard Horatio' and lastnames='McCoy' and dob='1920-1-20+2:00'
	)
;

alter table clin.test_result
	add foreign key (fk_intended_reviewer)
		references dem.staff(pk)
		on update cascade
		on delete restrict
;


-- clin.reviewed_test_results
alter table clin.reviewed_test_results
	add foreign key (fk_reviewer)
		references dem.staff(pk)
		on update cascade
		on delete restrict
;


alter table clin.reviewed_test_results
	drop constraint if exists "reviewed_test_results_fk_reviewed_row_fkey" cascade;
alter table clin.reviewed_test_results
	drop constraint if exists "$1" cascade;


alter table clin.reviewed_test_results
	add foreign key (fk_reviewed_row)
		references clin.test_result(pk)
		on update cascade
		on delete cascade
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-test_result-static.sql,v $', '$Revision: 1.5 $');
