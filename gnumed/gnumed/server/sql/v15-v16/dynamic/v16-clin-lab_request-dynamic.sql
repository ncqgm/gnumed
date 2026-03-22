-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on column clin.lab_request.note_test_org is
	'A comment on this lab request by the performing organization (lab).';

alter table clin.lab_request drop constraint if exists clin_lab_req_sane_test_org_note cascade;


alter table clin.lab_request
	add constraint clin_lab_req_sane_test_org_note
		check (gm.is_null_or_non_empty_string(note_test_org) is True);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-lab_request-dynamic.sql', '16.0');
