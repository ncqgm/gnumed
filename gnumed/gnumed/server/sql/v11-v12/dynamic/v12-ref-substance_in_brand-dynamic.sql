-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-ref-substance_in_brand-dynamic.sql,v 1.1 2009-11-24 21:11:39 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
select audit.add_table_for_audit('ref', 'substance_in_brand');
select gm.add_table_for_notifies('ref', 'substance_in_brand');


comment on table ref.substance_in_brand is
	'lists substances being part of branded drugs';


-- .fk_brand
comment on column ref.substance_in_brand.fk_brand is
	'The drug brand this substance belongs to.';

\unset ON_ERROR_STOP
drop index ref.idx_subst_fk_brand cascade;
\set ON_ERROR_STOP 1

create index idx_subst_fk_brand on ref.substance_in_brand(fk_brand);


-- .description
comment on column ref.substance_in_brand.description is
	'The substance name.';

\unset ON_ERROR_STOP
alter table ref.substance_in_brand drop constraint subst_sane_desc cascade;
drop index ref.idx_subst_description cascade;
\set ON_ERROR_STOP 1

alter table ref.substance_in_brand
	add constraint subst_sane_desc
		check (gm.is_null_or_blank_string(description) is False);

create index idx_subst_description on ref.substance_in_brand(description);


-- .atc_code
comment on column ref.substance_in_brand.atc_code is
	'the Anatomic Therapeutic Chemical code for this substance';

\unset ON_ERROR_STOP
alter table ref.substance_in_brand drop constraint subst_sane_atc cascade;
\set ON_ERROR_STOP 1

alter table ref.substance_in_brand
	add constraint subst_sane_atc
		check (gm.is_null_or_non_empty_string(atc_code) is True);


-- .table constraints
alter table ref.substance_in_brand
	add constraint subst_unique_per_brand
		unique (fk_brand, description);


-- grants
grant select, insert, update, delete on
	ref.substance_in_brand,
	ref.substance_in_brand_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-ref-substance_in_brand-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-ref-substance_in_brand-dynamic.sql,v $
-- Revision 1.1  2009-11-24 21:11:39  ncq
-- - new drug tables
--
--