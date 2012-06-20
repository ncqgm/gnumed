-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-clin-v_unified_test_types-dynamic.sql,v 1.2 2009-05-24 16:34:30 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_unified_test_types cascade;
\set ON_ERROR_STOP 1

create view clin.v_unified_test_types as
select
	ctt.pk as pk_test_type,
	-- unified test_type
	coalesce(vmtt.abbrev_meta, ctt.abbrev) as unified_abbrev,
	coalesce(vmtt.name_meta, ctt.name) as unified_name,
	coalesce(vmtt.loinc_meta, ctt.loinc) as unified_loinc,
	-- original test_type
	ctt.abbrev as abbrev_tt,
	ctt.name as name_tt,
	ctt.loinc as loinc_tt,
	ctt.comment as comment_tt,
	ctt.code as code_tt,
	ctt.coding_system as coding_system_tt,
	ctt.conversion_unit as conversion_unit,
	-- meta-version thereof
	vmtt.abbrev_meta,
	vmtt.name_meta,
	vmtt.loinc_meta,
	vmtt.comment_meta,
	-- admin links
	ctt.fk_test_org as pk_test_org,
	vmtt.pk_meta_test_type,
	vmtt.pk_lnk_ttype2meta_type,
	(vmtt.pk_meta_test_type is null) as is_fake_unified_type
from
	clin.test_type ctt left outer join clin.v_meta_test_types vmtt on (ctt.pk = vmtt.pk_test_type)
;


comment on view clin.v_unified_test_types is
'provides a "unified" view of test types aggregated under
 their corresponding unified name if any; if not linked
 to a meta test type the original name is used';


grant select on clin.v_unified_test_types to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-v_unified_test_types-dynamic.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v11-clin-v_unified_test_types-dynamic.sql,v $
-- Revision 1.2  2009-05-24 16:34:30  ncq
-- - add fake flag
--
-- Revision 1.1  2009/05/22 10:57:50  ncq
-- - new
--
--