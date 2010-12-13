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


grant select, insert, update, delete on
	ref.lnk_substance2brand
to group "gm-doctors";

grant select, select, update on
	ref.lnk_substance2brand_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
-- .fk_brand
\unset ON_ERROR_STOP
alter table ref.lnk_substance2brand drop constraint lnk_substance2brand_fk_brand_fkey cascade;
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

-- --------------------------------------------------------------
-- .fk_substance
\unset ON_ERROR_STOP
alter table ref.lnk_substance2brand drop constraint lnk_substance2brand_fk_substance_fkey cascade;
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

-- --------------------------------------------------------------
-- table constraints
\unset ON_ERROR_STOP
alter table ref.lnk_substance2brand drop constraint ref_lnk_s2b_subst_uniq_per_brand cascade;
\set ON_ERROR_STOP 1

alter table ref.lnk_substance2brand
	add constraint ref_lnk_s2b_subst_uniq_per_brand
		unique(fk_brand, fk_substance);

-- --------------------------------------------------------------
-- must not devoid non-fake brands of all components
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
-- must not modify fk_brand/fk_substance/amount/unit from under a patient
\unset ON_ERROR_STOP
drop function ref.trf_do_not_update_component_if_taken_by_patient() cascade;
\set ON_ERROR_STOP 1

create or replace function ref.trf_do_not_update_component_if_taken_by_patient()
	returns trigger
	language 'plpgsql'
	as '
BEGIN
	if OLD.fk_brand = NEW.fk_brand then
		if OLD.fk_substance = NEW.fk_substance then
			return NEW;
		end if;
	end if;

	perform 1 from clin.substance_intake c_si
	where c_si.fk_drug_component = OLD.pk
	limit 1;

	if NOT FOUND then
		return NEW;
	end if;

	raise exception ''[ref.trf_do_not_update_component_if_taken_by_patient]: as long as drug component <%> is taken by a patient you cannot modify it'', OLD.pk;

	return NEW;
END;';

comment on function ref.trf_do_not_update_component_if_taken_by_patient() is
'If this drug component is taken by any patient do not modify it (
amount, unit, substance, brand).';

create trigger tr_do_not_update_component_if_taken_by_patient
	before update
	on ref.lnk_substance2brand
	for each row execute procedure ref.trf_do_not_update_component_if_taken_by_patient()
;

-- --------------------------------------------------------------
-- test data
delete from ref.branded_drug
where
	description like '% Starship Enterprises';

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

delete from ref.lnk_substance2brand
where
	fk_brand = (
		select pk from ref.branded_drug where description = 'IbuStrong Starship Enterprises'
	);

insert into ref.lnk_substance2brand (
	fk_brand,
	fk_substance
) values (
	(select pk from ref.branded_drug where description = 'IbuStrong Starship Enterprises'),
	(select pk from ref.consumable_substance where description = 'Ibuprofen-Starship')
);

-- --------------------------------------------------------------
-- transfer old components of brands from ...

-- ... ref.substance_in_brand
insert into ref.lnk_substance2brand (
	fk_brand,
	fk_substance
) select
	rsib.fk_brand,
	(select rcs.pk from ref.consumable_substance rcs where rcs.description = rsib.description)
from
	ref.substance_in_brand rsib
;



-- ... clin.consumed_substance
insert into ref.lnk_substance2brand (
	fk_brand,
	fk_substance
) select
	csi.fk_brand,
	(select rcs.pk from ref.consumable_substance rcs where rcs.description = ccs.description)
from
	clin.substance_intake csi
		left join clin.consumed_substance ccs on (ccs.pk = csi.fk_substance)
where
	csi.fk_brand is not null
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-lnk_substance2brand-dynamic.sql', 'Revision: 1.1');

-- ==============================================================
