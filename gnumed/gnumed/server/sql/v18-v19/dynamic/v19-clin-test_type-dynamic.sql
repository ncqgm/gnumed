-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten.Hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;
-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index clin.idx_test_type_loinc;
\set ON_ERROR_STOP 1

create index idx_test_type_loinc on clin.test_type(loinc);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index clin.idx_test_result_unit;
\set ON_ERROR_STOP 1

create index idx_test_result_unit on clin.test_result(val_unit);

-- --------------------------------------------------------------
-- deduplicate rows
update clin.test_type set
	name = name || ' [org:' || coalesce(fk_test_org::text, '?') || ';pk:' || pk || ']'
where name in (
	select name from clin.test_type group by name having count(*) > 1
);

\unset ON_ERROR_STOP
alter table clin.test_type drop constraint clin_test_type_uniq_name_per_org cascade;
\set ON_ERROR_STOP 1

alter table clin.test_type
	add constraint clin_test_type_uniq_name_per_org
		unique(fk_test_org, name)
;

-- --------------------------------------------------------------
-- deduplicate rows
update clin.test_type set
	abbrev = abbrev || ' [org:' || coalesce(fk_test_org::text, '?') || ';pk:' || pk || ']'
where abbrev in (
	select abbrev from clin.test_type group by abbrev having count(*) > 1
);

\unset ON_ERROR_STOP
alter table clin.test_type drop constraint clin_test_type_uniq_abbrev_per_org cascade;
\set ON_ERROR_STOP 1

alter table clin.test_type
	add constraint clin_test_type_uniq_abbrev_per_org
		unique(fk_test_org, abbrev)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-test_type-dynamic.sql', '19.0');
