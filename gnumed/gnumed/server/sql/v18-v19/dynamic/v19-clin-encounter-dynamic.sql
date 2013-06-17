-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
update clin.encounter set
	fk_location = NULL
where
	fk_location = -1
;


alter table clin.encounter add foreign key (fk_location)
	references dem.praxis_branch(pk)
	on update cascade
	on delete restrict
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-encounter-dynamic.sql', '19.0');
