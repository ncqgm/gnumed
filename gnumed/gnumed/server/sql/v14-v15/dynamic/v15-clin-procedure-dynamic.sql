-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .end
comment on column clin.procedure.clin_end is
	'When did this procedure end/is expected to end. Infinity if explicitely ongoing.';


\unset ON_ERROR_STOP
drop constraint procedure_sane_end cascade;
\set ON_ERROR_STOP 1


alter table clin.procedure
	add constraint procedure_sane_end check (
		(clin_end is NULL)
			OR
		(clin_end >= clin_when)
	);

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-clin-procedure-dynamic.sql', 'Revision: 1.1');
