-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-clin-test_type-dynamic.sql,v 1.3 2009-08-03 20:53:59 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.test_org
	alter column fk_org
		drop not null;

-- --------------------------------------------------------------
alter table clin.test_type
	alter column abbrev
		set not null;


alter table clin.test_type
	alter column name
		set not null;


alter table clin.test_type
	alter column code
		drop not null;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_test_types cascade;
\set ON_ERROR_STOP 1

create view clin.v_test_types as
select
	ctt.pk
		 as pk_test_type,
	ctt.abbrev,
	ctt.name,
	ctt.loinc,
	ctt.code,
	ctt.coding_system,
	ctt.conversion_unit,
	ctt.comment
		as comment_type,
	cto.internal_name
		as internal_name_org,
	cto.comment
		as comment_org,
	-- admin links
	ctt.fk_test_org
		 as pk_test_org,
	cto.fk_org
		as pk_org,
	cto.fk_adm_contact
		as pk_adm_contact_org,
	cto.fk_med_contact
		as pk_med_contact_org,
	ctt.xmin
		as xmin_test_type
from
	clin.test_type ctt
		left join clin.test_org cto on (cto.pk = ctt.fk_test_org)
;


comment on view clin.v_test_types is
'denormalizes test types with test orgs';


grant select on clin.v_test_types to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-test_type-dynamic.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: v11-clin-test_type-dynamic.sql,v $
-- Revision 1.3  2009-08-03 20:53:59  ncq
-- - drop not null on clin.test_org.fk_org
--
-- Revision 1.2  2009/05/24 16:31:35  ncq
-- - new v_test_types
--
-- Revision 1.1  2009/05/22 10:57:49  ncq
-- - new
--
--