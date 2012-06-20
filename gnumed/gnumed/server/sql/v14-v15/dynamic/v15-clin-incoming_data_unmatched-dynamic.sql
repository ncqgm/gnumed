-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on column clin.incoming_data_unmatched.comment is
'a free text comment on this row, eg. why is it here';



\unset ON_ERROR_STOP
alter table clin.incoming_data_unmatched drop constraint unmatched_data_sane_comment cascade;
\set ON_ERROR_STOP 1


alter table clin.incoming_data_unmatched
	add constraint unmatched_data_sane_comment check (
		gm.is_null_or_non_empty_string(comment) is true
	);


-- --------------------------------------------------------------
select gm.log_script_insertion('v15-clin-incoming_data_unmatched-dynamic.sql', 'Revision: 1.1');
