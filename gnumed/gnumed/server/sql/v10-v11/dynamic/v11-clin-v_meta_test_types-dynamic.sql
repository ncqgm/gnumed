-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists clin.v_test_type_unified cascade;
drop view if exists clin.v_meta_test_types cascade;

create view clin.v_meta_test_types as
select
	ttm.pk as pk_meta_test_type,
	ltt2mt.fk_test_type as pk_test_type,
	ttm.abbrev as abbrev_meta,
	ttm.name as name_meta,
	ttm.loinc as loinc_meta,
	ttm.comment as comment_meta,
	ltt2mt.pk as pk_lnk_ttype2meta_type,
	ttm.xmin as xmin_meta_test_type
from
	clin.meta_test_type ttm,
	clin.lnk_ttype2unified_type ltt2mt
where
	ltt2mt.fk_test_type_unified = ttm.pk
;


comment on view clin.v_meta_test_types is
'denormalized view of meta_test_type + link table to test_type,
 shows all meta test types to which a test type is linked';


grant select on clin.v_meta_test_types to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-v_meta_test_types-dynamic.sql,v $', '$Revision: 1.2 $');
