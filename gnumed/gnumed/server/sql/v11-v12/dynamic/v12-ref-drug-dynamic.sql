-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-ref-drug-dynamic.sql,v 1.2 2009-12-01 21:58:21 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
select audit.add_table_for_audit('ref', 'branded_drug');
select gm.add_table_for_notifies('ref', 'branded_drug');


-- .fk_data_souce
comment on column ref.branded_drug.fk_data_source is
	'the data source this entry came from';

\unset ON_ERROR_STOP
drop index ref.idx_drug_data_source cascade;
\set ON_ERROR_STOP 1

create index idx_drug_data_source on ref.branded_drug(fk_data_source);


-- .description
comment on column ref.branded_drug.description is
	'the name of this drug it is marketed under by the manufacturer';

alter table ref.branded_drug
	alter column description
		set not null;

\unset ON_ERROR_STOP
drop index ref.idx_drug_description cascade;
\set ON_ERROR_STOP 1

create index idx_drug_description on ref.branded_drug(description);


-- .preparation
comment on column ref.branded_drug.preparation is
	'the preparation the drug is delivered in, eg liquid, cream, tablet, etc.';

alter table ref.branded_drug
	alter column preparation
		set not null;


-- .atc_code
comment on column ref.branded_drug.atc_code is
	'the Anatomic Therapeutic Chemical code for this drug, used to compute possible substitutes';


-- .is_fake
alter table ref.branded_drug
	alter column is_fake
		set default False;


-- .external_code
comment on column ref.branded_drug.external_code is
	'an opaque code from an external data source, such as "PZN" in Germany';

\unset ON_ERROR_STOP
alter table ref.branded_drug drop constraint drug_sane_external_code cascade;
drop index ref.idx_drug_ext_code cascade;
\set ON_ERROR_STOP 1

alter table ref.branded_drug
	add constraint drug_sane_external_code
		check (gm.is_null_or_non_empty_string(external_code) is True);

create index idx_drug_ext_code on ref.branded_drug(external_code);


-- grants
grant select, insert, update, delete on
	ref.branded_drug,
	ref.substance_brand_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
-- drop clin.clin_medication
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
delete from audit.audited_tables aat
where
	aat.schema = 'clin'
		and 
	aat.table_name = 'substance_brand'
;

delete from gm.notifying_tables gnt
where
	gnt.schema_name = 'clin'
		and 
	gnt.table_name = 'substance_brand'
;

\unset ON_ERROR_STOP
drop function audit.ft_ins_substance_brand() cascade;
drop function audit.ft_upd_substance_brand() cascade;
drop function audit.ft_del_substance_brand() cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-ref-drug-dynamic.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v12-ref-drug-dynamic.sql,v $
-- Revision 1.2  2009-12-01 21:58:21  ncq
-- - .is_fake better default to False rather than True
--
-- Revision 1.1  2009/11/24 21:11:39  ncq
-- - new drug tables
--
--