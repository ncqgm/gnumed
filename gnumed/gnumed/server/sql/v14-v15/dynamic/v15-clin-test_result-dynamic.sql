-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to 'on';

-- --------------------------------------------------------------
-- .fk_request
comment on column clin.test_result.fk_request is
'The request this result was ordered under if any.';


alter table clin.test_result
	add foreign key (fk_request)
		references clin.lab_request(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-clin-test_result-dynamic.sql', 'Revision: 1.1');
