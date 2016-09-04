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
-- table
comment on table ref.lnk_dose2drug is 'Links doses to drug products';

select audit.register_table_for_auditing('ref', 'lnk_dose2drug');
select gm.register_notifying_table('ref', 'lnk_dose2drug');

-- table constraints
drop index if exists ref.idx_ld2d_dose_uniq_per_brand cascade;
create unique index idx_ld2d_dose_uniq_per_brand on ref.lnk_dose2drug(fk_dose, fk_brand) where fk_brand is not NULL;

drop index if exists ref.idx_ld2d_uniq_generic_brand_by_dose cascade;
create unique index idx_ld2d_uniq_generic_brand_by_dose on ref.lnk_dose2drug(fk_dose) where fk_brand is NULL;

-- grants
grant select on ref.lnk_dose2drug to "gm-public";
grant insert, update, delete on ref.lnk_dose2drug to "gm-doctors";
grant usage on ref.lnk_dose2drug_pk_seq to "gm-public";

-- --------------------------------------------------------------
-- .fk_dose
comment on column ref.lnk_dose2drug.fk_dose is 'FK linking the dose';

alter table ref.lnk_dose2drug
	alter column fk_dose
		set not null;

alter table ref.lnk_dose2drug drop constraint if exists ref_ld2d_fk_dose cascade;

alter table ref.lnk_dose2drug
	add constraint ref_ld2d_fk_dose
		foreign key (fk_dose) references ref.dose(pk)
			on update cascade
			on delete restrict
;

-- --------------------------------------------------------------
-- .fk_brand
comment on column ref.lnk_dose2drug.fk_brand is 'FK linking the brand';

alter table ref.lnk_dose2drug
	alter column fk_brand
		set not null;

alter table ref.lnk_dose2drug drop constraint if exists ref_ld2d_fk_brand cascade;

alter table ref.lnk_dose2drug
	add constraint ref_ld2d_fk_brand
		foreign key (fk_brand) references ref.branded_drug(pk)
			on update cascade
			on delete cascade
;

-- --------------------------------------------------------------
-- trigger to maintain consistency
--	tr_do_not_update_component_if_taken_by_patient
--	tr_true_brands_must_have_components

-- --------------------------------------------------------------
-- create dose/drug links for existing brands
insert into ref.lnk_dose2drug (fk_brand, fk_dose)
	select
		pk_brand,
		(select pk from ref.dose r_d where
			r_d.fk_substance = (select pk from ref.substance r_s where r_s.description = r_vdc.substance)
				and
			r_d.amount = r_vdc.amount
				and
			r_d.unit = r_vdc.unit
		)
	from
		ref.v_drug_components r_vdc
;

-- --------------------------------------------------------------
drop view if exists ref.v_drug_components cascade;

create view ref.v_drug_components as
select
	r_ld2d.pk 
		as pk_component,
	r_bd.description
		as brand,
	r_vsd.substance,
	r_vsd.amount,
	r_vsd.unit,
	r_vsd.dose_unit,
	r_bd.preparation
		as preparation,
	r_vsd.intake_instructions,
	r_vsd.loincs,
	r_vsd.atc_substance,
	r_bd.atc_code
		as atc_brand,
	r_bd.external_code
		as external_code,
	r_bd.external_code_type
		as external_code_type,
	r_bd.is_fake
		as is_fake_brand,
	exists (
		select 1 from clin.substance_intake c_si
		where c_si.fk_drug_component = r_ld2d.pk
		limit 1
	)	as is_in_use,

	r_bd.pk
		as pk_brand,
	r_vsd.pk_dose,
	r_vsd.pk_substance,
	r_bd.fk_data_source
		as pk_data_source,
	r_ld2d.xmin
		as xmin_lnk_dose2drug
from
	ref.lnk_dose2drug r_ld2d
		inner join ref.branded_drug r_bd on (r_ld2d.fk_brand = r_bd.pk)
		inner join ref.v_substance_doses r_vsd on (r_ld2d.fk_dose = r_vsd.pk_dose)
;

grant select on ref.v_drug_components to "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-lnk_dose2drug-dynamic.sql', '22.0');
