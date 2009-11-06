-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-clin-substance_brand-dynamic.sql,v 1.2 2009-11-06 15:36:51 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
comment on column clin.substance_brand.external_code is
'an opaque code from an external data source, such as "PZN" in Germany';


\unset ON_ERROR_STOP
alter table clin.substance_brand drop constraint sane_external_code cascade;
drop index clin.idx_subst_brand_ext_code cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_brand
	add constraint sane_external_code check (
		gm.is_null_or_non_empty_string(external_code) is True
	);

create index idx_subst_brand_ext_code on clin.substance_brand (external_code);

-- --------------------------------------------------------------
delete from audit.audited_tables aat
where
	aat.schema = 'clin'
		and 
	aat.table_name = 'clin_medication'
;

delete from gm.notifying_tables gnt
where
	gnt.schema_name = 'clin'
		and 
	gnt.table_name = 'clin_medication'
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-substance_brand-dynamic.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v12-clin-substance_brand-dynamic.sql,v $
-- Revision 1.2  2009-11-06 15:36:51  ncq
-- - drop old clin.medication
--
-- Revision 1.1  2009/10/21 08:52:57  ncq
-- - .external_code
--
--