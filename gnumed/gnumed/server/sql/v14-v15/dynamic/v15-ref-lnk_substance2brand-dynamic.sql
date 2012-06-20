-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
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
		on delete restrict;

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
	_brand_is_deleted boolean;
	_is_fake_brand boolean;
	_has_other_components boolean;
BEGIN
	-- if an UPDATE does NOT move the component to another drug
	-- there WILL be at least one component left
	if TG_OP = ''UPDATE'' then
		if NEW.fk_brand = OLD.fk_brand then
			return NEW;
		end if;
	end if;


	-- fake drugs may become devoid of components
	select
		is_fake into _is_fake_brand
	from
		ref.branded_drug
	where
		pk = OLD.fk_brand
	;
	if _is_fake_brand is TRUE then
		return OLD;
	end if;


	-- DELETEs may proceed if the drug has been deleted, too
	if TG_OP = ''DELETE'' then
		select not exists (
			select 1 from ref.branded_drug
			where pk = OLD.fk_brand
		) into _brand_is_deleted;
		if _brand_is_deleted is TRUE then
			return OLD;
		end if;
	end if;


	-- if there are other components left after the
	-- UPDATE or DELETE everything is fine
	select exists (
		select 1 from ref.lnk_substance2brand
		where
			fk_brand = OLD.fk_brand
				and
			fk_substance != OLD.fk_substance
		limit 1
	) into _has_other_components;
	if _has_other_components is TRUE then
		return OLD;
	end if;


	raise exception ''[ref.trf_true_brands_must_have_components::%] brand must have components (brand <%> component <%>)'', TG_OP, OLD.fk_brand, OLD.fk_substance;

	return OLD;
END;';

comment on function ref.trf_true_brands_must_have_components() is
	'There must always be at least one component for any existing non-fake branded drug.';

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
-- Enterprise pain killer
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
-- f6 East German cigarettes
delete from ref.branded_drug where description like 'f6 Zigaretten';

insert into ref.branded_drug (
	description,
	preparation,
	is_fake,
	external_code,
	external_code_type
) values (
	'f6 Zigaretten',
	'Zigarette',
	False,
	'4023500714150',
	'DE::EAN'
);

delete from ref.lnk_substance2brand
where
	fk_brand = (
		select pk from ref.branded_drug where description = 'f6 Zigaretten'
	);

insert into ref.lnk_substance2brand (
	fk_brand,
	fk_substance
) values
	(
		(select pk from ref.branded_drug where description = 'f6 Zigaretten'),
		(select pk from ref.consumable_substance where description = 'Nikotin' and amount = 0.8 and unit = 'mg')
	),
	(
		(select pk from ref.branded_drug where description = 'f6 Zigaretten'),
		(select pk from ref.consumable_substance where description = 'Teer' and amount = 10 and unit = 'mg')
	),
	(
		(select pk from ref.branded_drug where description = 'f6 Zigaretten'),
		(select pk from ref.consumable_substance where description = 'Kohlenmonoxid' and amount = 10 and unit = 'mg')
	)
;

-- --------------------------------------------------------------
-- generate ref.lnk_substance2brand entries from v14 database knowledge
\unset ON_ERROR_STOP
drop function tmp_transfer_drug_components() cascade;
\set ON_ERROR_STOP 1


create or replace function tmp_transfer_drug_components()
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_prev_record record;
BEGIN

	-- 1) clin.consumed_substance
	raise notice ''creating ref.lnk_substance2brand rows from clin.consumed_substance'';

	for _prev_record in
		SELECT
			*,
			ccs.description as substance,
			rbd.description as brand
		FROM ref.branded_drug rbd
			JOIN clin.substance_intake csi ON (csi.fk_brand = rbd.pk)
				JOIN clin.consumed_substance ccs ON (ccs.pk = csi.fk_substance)
		WHERE
			csi.fk_brand is not null
	loop

		if _prev_record.tmp_amount is NULL then
			_prev_record.tmp_amount := 99999.4;
		end if;

		if _prev_record.tmp_unit is NULL then
			_prev_record.tmp_amount := ''*?* (ref.substance_in_brand)'';
		end if;

		raise notice ''linking % (% %) to %'', _prev_record.substance, _prev_record.tmp_amount, _prev_record.tmp_unit, _prev_record.brand;

		perform 1 from ref.lnk_substance2brand
		where
			fk_brand = _prev_record.fk_brand
				and
			fk_substance = (
				select pk from ref.consumable_substance
				where
					description = _prev_record.substance
						and
					amount = _prev_record.tmp_amount
						and
					unit = _prev_record.tmp_unit
			)
		;

		if found then
			raise notice ''already exists'';
			continue;
		end if;

		insert into ref.lnk_substance2brand (
			fk_brand,
			fk_substance
		) values (
			_prev_record.fk_brand,
			(
				select pk from ref.consumable_substance
				where
					description = _prev_record.substance
						and
					amount = _prev_record.tmp_amount
						and
					unit = _prev_record.tmp_unit
			)
		);
	end loop;


--	-- 2) ref.substance_in_brand
--	raise notice ''creating ref.lnk_substance2brand rows from ref.substance_in_brand'';
--
--	for _prev_record in
--		SELECT
--			*,
--			rsib.description as substance,
--			rbd.description as brand
--		FROM ref.branded_drug rbd
--			JOIN ref.substance_in_brand rsib ON (rsib.fk_brand = rbd.pk)
--	loop
--
--		raise notice ''linking % to %'', _prev_record.substance, _prev_record.brand;
--
--		perform 1 from ref.lnk_substance2brand
--		where
--			fk_brand = _prev_record.fk_brand
--				and
--			fk_substance = (
--				select pk from ref.consumable_substance
--				where
--					description = _prev_record.substance
--			)
--		;
--
--		if found then
--			raise notice ''already exists'';
--			continue;
--		end if;
--
--		insert into ref.lnk_substance2brand (
--			fk_brand,
--			fk_substance
--		) values (
--			_prev_record.fk_brand,
--			(
--				select pk from ref.consumable_substance
--				where
--					description = _prev_record.substance
--						and
--					amount = _prev_record.tmp_amount
--						and
--					unit = _prev_record.tmp_unit
--			)
--		);
--	end loop;

	return True;
END;';


select tmp_transfer_drug_components();


drop function tmp_transfer_drug_components() cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-lnk_substance2brand-dynamic.sql', 'Revision: 1.1');

-- ==============================================================
