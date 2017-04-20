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
-- remove courses and patient-course links which might
-- restrict indications from getting deleted
delete from clin.lnk_pat2vaccination_course;
delete from clin.vaccination_course;


-- allow brands to be dropped by dropping the vaccine,
alter table ref.vaccine
	drop constraint if exists vaccine_fk_brand_fkey cascade;
alter table ref.vaccine
	drop constraint if exists ref_vaccine_fk_drug_product cascade;
alter table ref.vaccine
	add constraint ref_vaccine_fk_drug_product
		foreign key(fk_drug_product) references ref.drug_product(pk)
			on update cascade
			on delete cascade
;

-- remove vaccines not in use (will cascade to
-- vaccine<->indication links and linked drug products)
delete from ref.vaccine where
	pk not in (
		select fk_vaccine from clin.vaccination
	);

-- remove dangling indications not linked to any vaccine
delete from ref.vacc_indication where
	id not in (
		select fk_indication from ref.lnk_vaccine2inds
	);

-- remove dangling generic vaccine products not linked to
-- any defined vaccine (and thusly not to any vaccinations)
delete from ref.drug_product r_dp where
	r_dp.description ilike '% - generic vaccine'
		and
	not exists (
		select 1 from ref.vaccine r_v where r_v.fk_drug_product = r_dp.pk
	)
;

-- restrict, again, brands from being dropped by dropping the vaccine
alter table ref.vaccine
	drop constraint if exists ref_vaccine_fk_drug_product cascade;
alter table ref.vaccine
	add constraint ref_vaccine_fk_drug_product
		foreign key(fk_drug_product) references ref.drug_product(pk)
			on update cascade
			on delete restrict
;

-- delete vaccine products which don't have vaccine details
-- data available (such as aren't linked to indications
-- via a vaccine row)
delete from ref.drug_product r_dp where
	r_dp.preparation like 'vaccine%'
		and
	not exists (
		select 1 from clin.v_substance_intakes where pk_brand = r_dp.pk
	)
		and
	not exists (
		select 1 from ref.vaccine r_v where r_v.fk_drug_product = r_dp.pk
	);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-remove_unused_vaccines.sql', '22.0');
