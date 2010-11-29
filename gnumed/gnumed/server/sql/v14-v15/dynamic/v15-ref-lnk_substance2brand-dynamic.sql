-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to 'on';
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
select audit.add_table_for_audit('ref', 'lnk_substance2brand');
select gm.add_table_for_notifies('ref', 'lnk_substance2brand');



comment on table ref.lnk_substance2brand is
'This table links substances (INNs, mostly) as components into drugs.';



-- .fk_brand
\unset ON_ERROR_STOP
--alter table ref.lnk_substance2brand drop foreign key  cascade;
\set ON_ERROR_STOP 1

alter table ref.lnk_substance2brand
	alter column fk_brand
		set not null;

alter table ref.lnk_substance2brand
	add foreign key (fk_brand)
		references ref.branded_drug(pk)
		on update cascade
		on delete cascade;

\unset ON_ERROR_STOP
drop index ref.idx_lnk_s2b_fk_brand cascade;
\set ON_ERROR_STOP 1

create index idx_lnk_s2b_fk_brand on ref.lnk_substance2brand(fk_brand);



-- .fk_substance
\unset ON_ERROR_STOP
--alter table ref.lnk_substance2brand drop foreign key  cascade;
\set ON_ERROR_STOP 1

alter table ref.lnk_substance2brand
	alter column fk_substance
		set not null;

alter table ref.lnk_substance2brand
	add foreign key (fk_substance)
		references ref.consumable_substance(pk)
		on update cascade
		on delete restrict;

\unset ON_ERROR_STOP
drop index ref.idx_lnk_s2b_fk_substance cascade;
\set ON_ERROR_STOP 1

create index idx_lnk_s2b_fk_substance on ref.lnk_substance2brand(fk_substance);



-- .amount
comment on column ref.lnk_substance2brand.amount is
	'The amount of substance in the linked branded drug.';

\unset ON_ERROR_STOP
alter table ref.lnk_substance2brand drop constraint ref_lnk_s2b_sane_amount cascade;
\set ON_ERROR_STOP 1

alter table ref.lnk_substance2brand
	alter column amount
		set not null;

alter table ref.lnk_substance2brand
	add constraint ref_lnk_s2b_sane_amount
		check (amount > 0);



-- .unit
comment on column ref.lnk_substance2brand.unit is
	'The unit of the amount of substance linked to the branded drug.';

\unset ON_ERROR_STOP
alter table ref.lnk_substance2brand drop constraint ref_lnk_s2b_sane_unit cascade;
\set ON_ERROR_STOP 1

alter table ref.lnk_substance2brand
	add constraint ref_lnk_s2b_sane_unit
		check (gm.is_null_or_blank_string(unit) is False);



-- table constraints
\unset ON_ERROR_STOP
alter table ref.lnk_substance2brand drop constraint ref_lnk_s2b_subst_uniq_per_brand cascade;
\set ON_ERROR_STOP 1

alter table ref.lnk_substance2brand
	add constraint ref_lnk_s2b_subst_uniq_per_brand
		unique(fk_brand, fk_substance);



\unset ON_ERROR_STOP
alter table ref.lnk_substance2brand drop constraint ref_lnk_s2b_amount_unit_uniq_per_subst cascade;
\set ON_ERROR_STOP 1

alter table ref.lnk_substance2brand
	add constraint ref_lnk_s2b_amount_unit_uniq_per_subst
		unique (fk_substance, amount, unit);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function ref.trf_true_brands_must_have_components() cascade;
\set ON_ERROR_STOP 1

create or replace function ref.trf_true_brands_must_have_components()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_is_fake_brand boolean;
	_has_other_components boolean;
BEGIN
	if TG_OP = ''UPDATE'' then
		if NEW.fk_brand = OLD.fk_brand then
			return NEW;
		end if;
	end if;

	select
		is_fake into _is_fake_brand
	from
		ref.branded_drug
	where
		pk = OLD.fk_brand
	;

	if _is_fake_brand is TRUE then
		return NEW;
	end if;

	select exists (
		select 1
		from ref.lnk_substance2brand
		where
			fk_brand = OLD.fk_brand
				and
			fk_substance != OLD.fk_substance
	) into _has_other_components;

	if _has_other_components is TRUE then
		return NEW;
	end if;

	raise exception ''[ref.trf_true_brands_must_have_components::%] brand must have components (brand <%> component <%>)'', TG_OP, OLD.fk_brand, OLD.fk_substance;

	return NEW;
END;';

comment on function ref.trf_true_brands_must_have_components() is
	'There must always be at least one component for any non-fake branded drug.';

create constraint trigger tr_true_brands_must_have_components
	after update or delete
	on ref.lnk_substance2brand
	deferrable
	initially deferred
	for each row execute procedure ref.trf_true_brands_must_have_components()
;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view ref.v_drug_components cascade;
\set ON_ERROR_STOP 1

create view ref.v_drug_components as

select
	r_ls2b.fk_brand
		as pk_brand,
	r_cs.pk
		as pk_consumable_substance,
	r_bd.description
		as brand,
	r_cs.description
		as substance,
	r_ls2b.amount
		as strength,
	r_ls2b.unit
		as unit,
	r_bd.preparation
		as preparation,
	r_cs.atc_code
		as atc_substance,
	r_bd.atc_code
		as atc_brand,
	r_bd.external_code
		as external_code_brand,
	r_bd.external_code_type
		as external_code_type_brand,
	r_bd.is_fake
		as is_fake_brand,
	r_bd.fk_data_source
		as pk_data_source
from
	ref.consumable_substance r_cs
		inner join ref.lnk_substance2brand r_ls2b on (r_cs.pk = r_ls2b.fk_substance)
			left join ref.branded_drug r_bd on (r_ls2b.fk_brand = r_bd.pk)
;


grant select on
	ref.v_drug_components
to group "gm-doctors";

-- --------------------------------------------------------------
-- test data
delete from ref.branded_drug where description like '% Starship Enterprises';

insert into ref.branded_drug (
	description,
	preparation,
	atc_code,
	is_fake
) values (
	'IbuStrong Starship Enterprises',
	'tablet',
	'M01AE01',
	True
);

delete from ref.lnk_substance2brand where fk_brand = (select pk from ref.branded_drug where description = 'IbuStrong Starship Enterprises');

insert into ref.lnk_substance2brand (
	fk_brand,
	fk_substance,
	amount,
	unit
) values (
	(select pk from ref.branded_drug where description = 'IbuStrong Starship Enterprises'),
	(select pk from ref.consumable_substance where description = 'Ibuprofen-Starship'),
	800,
	'mg/tablet'
);

-- --------------------------------------------------------------
-- transfer old components of brands from ...

-- ... ref.substance_in_brand
insert into ref.lnk_substance2brand (
	fk_brand,
	fk_substance,
	amount,
	unit
) select
	rsib.fk_brand,
	(select rcs.pk from ref.consumable_substance rcs where rcs.description = rsib.description),
	coalesce (
		(select trim((regexp_matches(trim(strength), E'\\d+[.,]{0,1}\\d*'))[1])
		 from clin.substance_intake where fk_brand = rsib.fk_brand
		)::decimal,
		999
	),
	coalesce (
		(select trim(regexp_replace(trim(strength), E'\\d+[.,]{0,1}\\d*', ''))
		 from clin.substance_intake where fk_brand = rsib.fk_brand),
		'dt'
	)
from
	ref.substance_in_brand rsib
;

-- ... clin.consumed_substance
insert into ref.lnk_substance2brand (
	fk_brand,
	fk_substance,
	amount,
	unit
) select
	csi.fk_brand,
	(select rcs.pk from ref.consumable_substance rcs where rcs.description = ccs.description),
	-- amount:
	coalesce (
		(select trim((regexp_matches(trim(csi.strength), E'\\d+[.,]{0,1}\\d*'))[1]))::decimal,
		999
	),
	-- unit:
	coalesce (
		trim(regexp_replace(trim(csi.strength), E'\\d+[.,]{0,1}\\d*', '')),
		'dt'
	)
from
	clin.substance_intake csi
		left join clin.consumed_substance ccs on (ccs.pk = csi.fk_substance)
where
	csi.fk_brand is not null
;

-- --------------------------------------------------------------
-- cleanup
\unset ON_ERROR_STOP
drop view ref.v_substance_in_brand cascade;
\set ON_ERROR_STOP 1

comment on table ref.substance_in_brand is 'Remove this table in gnumed_v16';
truncate ref.substance_in_brand cascade;
revoke all on ref.substance_in_brand from "gm-doctors", "gm-public";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view ref.v_branded_drugs cascade;
\set ON_ERROR_STOP 1

create view ref.v_branded_drugs as

select
	r_bd.pk
		as pk_brand,
	r_bd.description
		as brand,
	r_bd.preparation
		as preparation,
	r_bd.atc_code
		as atc,
	r_bd.external_code
		as external_code_brand,
	r_bd.external_code_type
		as external_code_type_brand,
	r_bd.is_fake
		as is_fake_brand,

	(select array_agg(r_cs.description || '::' || r_ls2b.amount || '::' || r_ls2b.unit || '::' || coalesce(r_cs.atc_code, ''))
	 from
	 	ref.lnk_substance2brand r_ls2b
	 		inner join ref.consumable_substance r_cs on (r_ls2b.fk_substance = r_cs.pk)
	 	where r_ls2b.fk_brand = r_bd.pk
	) as components,

	r_bd.fk_data_source
		as pk_data_source
from
	ref.branded_drug r_bd
;


grant select on
	ref.v_drug_components
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-lnk_substance2brand-dynamic.sql', 'Revision: 1.1');

-- ==============================================================
