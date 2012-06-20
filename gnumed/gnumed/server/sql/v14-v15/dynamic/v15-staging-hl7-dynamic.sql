-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on schema staging is
'A schema used for staging data imports.';


grant usage on schema staging to group "gm-doctors";

-- --------------------------------------------------------------
comment on table staging.lab_request is
'Used to stage lab requests (from hl7 files, currently).';



grant select, insert, update, delete on staging.lab_request to group "gm-doctors";



alter table staging.lab_request
	alter column soap_cat
		set default 'p'::text;



alter table staging.lab_request
	alter column fk_incoming_data_unmatched
		set not NULL;



alter table staging.lab_request
	alter column fk_test_org
		set not NULL;

alter table staging.lab_request
	add foreign key (fk_test_org)
		references clin.test_org(pk)
		on update cascade
		on delete restrict;



--alter table staging.lab_request
--	alter column request_id
--		set NOT NULL;

\unset ON_ERROR_STOP
alter table staging.lab_request drop constraint staging_request_sane_request_id cascade;
\set ON_ERROR_STOP 1

alter table staging.lab_request
	add constraint staging_request_sane_request_id check (
		(gm.is_null_or_blank_string(request_id) is False)
	);



alter table staging.lab_request
	alter column fk_requestor
		set default NULL;



--alter table staging.lab_request
--	alter column orig_requestor
--		set default NULL;



alter table staging.lab_request
	alter column request_status
		set NOT NULL;

\unset ON_ERROR_STOP
alter table staging.lab_request drop constraint staging_request_sane_status cascade;
\set ON_ERROR_STOP 1

alter table staging.lab_request
	add constraint staging_request_sane_status check (
		(request_status = ANY (ARRAY['pending'::text, 'preliminary'::text, 'partial'::text, 'final'::text]))
	);



alter table staging.lab_request
	alter column is_pending
		set NOT NULL;



alter table staging.lab_request
	alter column is_pending
		set default true;

-- --------------------------------------------------------------
comment on table staging.test_result is
'Used to stage test results (from hl7 files, currently).';



grant select, insert, update, delete on staging.test_result to group "gm-doctors";



alter table staging.test_result
	alter column soap_cat
		set default 'p'::text;



-- should be FK, actually
alter table staging.test_result
	alter column fk_type
		set NOT NULL;



alter table staging.test_result
	alter column fk_intended_reviewer
		set default null;



alter table staging.test_result
	alter column orig_intended_reviewer
		set default null;



\unset ON_ERROR_STOP
alter table staging.test_result drop constraint staging_numval_needs_unit cascade;
\set ON_ERROR_STOP 1

alter table staging.test_result
	add constraint staging_numval_needs_unit check (
		(((val_num IS NOT NULL) AND (btrim(COALESCE(val_unit, ''::text)) <> ''::text)) OR (val_num IS NULL))
	);



\unset ON_ERROR_STOP
alter table staging.test_result drop constraint staging_sane_value cascade;
\set ON_ERROR_STOP 1

alter table staging.test_result
	add constraint staging_sane_value check (
		(
			((val_num IS NOT NULL) OR (val_alpha IS NOT NULL))
				OR
			(((val_num IS NULL) AND (val_alpha <> ''::text)) AND (val_alpha IS NOT NULL))
		)
	);



alter table staging.test_result
	alter column fk_request
		set NOT NULL;

alter table staging.test_result
	add foreign key (fk_request)
		references staging.lab_request(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-staging-hl7-dynamic.sql', 'Revision: 1.1');
