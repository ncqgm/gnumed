-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- sanity check: fk_result may only exist once in clin.lnk_result2lab_req
--
-- if this fails with "division by zero" you must fix the data in
-- clin.lnk_result2lab_req so that each result is linked to one and
-- only one lab_request
select
	case
		when ((select max(cnt) from (select count(1) as cnt from clin.lnk_result2lab_req lnk group by lnk.fk_result) as result_counts) > 1) then
			1 / (select 1 - 1)
		else
			1
	end;



-- .fk_request
alter table clin.test_result
	add column fk_request integer;

alter table audit.log_test_result
	add column fk_request integer;



-- transfer data from clin.lnk_result2lab_req to clin.test_result.fk_request
update clin.test_result ctr set
	fk_request = (
		select fk_request
		from clin.lnk_result2lab_req lnk
		where lnk.fk_result = ctr.pk
	)
;



-- drop old table
drop table clin.lnk_result2lab_req cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-clin-test_result-static.sql', 'Revision: 1.1');
