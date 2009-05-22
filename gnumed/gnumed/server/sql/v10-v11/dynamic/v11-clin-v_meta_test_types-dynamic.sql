-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-clin-v_meta_test_types-dynamic.sql,v 1.1 2009-05-22 10:57:50 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_test_type_unified cascade;
\set ON_ERROR_STOP 1

create view clin.v_meta_test_types as
select
	ttm.pk as pk_test_type_unified,
	ltt2ut.fk_test_type as pk_test_type,
	ttm.abbrev as abbrev_meta,
	ttm.name as name_meta,
	ttm.loinc as loinc_meta,
	ttm.comment as comment_meta,
	ltt2ut.pk as pk_lnk_ttype2unified_type
from
	clin.test_type_unified ttm,
	clin.lnk_ttype2unified_type ltt2ut
where
	ltt2ut.fk_test_type_unified = ttm.pk
;


comment on view clin.v_meta_test_types is
'denormalized view of test_type_unified + link table to test_type,
 shows all test types for which a meta type exists';


grant select on clin.v_meta_test_types to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-v_meta_test_types-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-clin-v_meta_test_types-dynamic.sql,v $
-- Revision 1.1  2009-05-22 10:57:50  ncq
-- - new
--
--