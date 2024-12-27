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
-- .fk_drug_product
comment on column ref.vaccine.fk_drug_product is 'Link to a vaccine brand. If NULL this is a generic vaccine entry.';

alter table ref.vaccine
	alter column fk_drug_product
		drop not null;

alter table ref.vaccine
	drop constraint if exists clin_vaccine_uniq_brand cascade;

drop index if exists ref.idx_uniq__ref__vaccine__fk_drug_product cascade;
create unique index idx_uniq__ref__vaccine__fk_drug_product on ref.vaccine(fk_drug_product);

-- --------------------------------------------------------------
-- .atc
comment on column ref.vaccine.atc is 'ATC for the vaccine, if any.';

-- --------------------------------------------------------------
-- check atc vs fk_drug_product
alter table ref.vaccine
	drop constraint if exists chk__either_fk_drug_product_or_atc cascade;

alter table ref.vaccine
	add constraint chk__either_fk_drug_product_or_atc check (
		(fk_drug_product IS NULL)
			OR
		(atc IS NULL)
	);

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-vaccine-dynamic.sql', '23.0');
