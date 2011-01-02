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
-- .fk_drug_component
comment on column clin.substance_intake.fk_drug_component is
	'Links to the component of a branded drug taken by a patient.';

\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint substance_intake_fk_drug_component_fkey cascade;
drop function audit.ft_upd_substance_intake() cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_intake
	add foreign key (fk_drug_component)
		references ref.lnk_substance2brand(pk)
		on update restrict
		on delete restrict;

update clin.substance_intake set
	fk_drug_component = (
		select pk from ref.lnk_substance2brand r_ls2b where
			r_ls2b.fk_brand = fk_brand
				and
			r_ls2b.fk_substance = (
				select pk from ref.consumable_substance r_cs where
					r_cs.description = (
						select description from clin.consumed_substance c_cs where c_cs.pk = clin.substance_intake.fk_substance
					)	and
					r_cs.amount = tmp_amount
						and
					r_cs.unit = tmp_unit
			)
	)
where
	fk_brand is not null
;
-- --------------------------------------------------------------
-- INSERT
\unset ON_ERROR_STOP
drop function ref.trf_insert_intake_must_link_all_drug_components() cascade;
\set ON_ERROR_STOP 1

create or replace function ref.trf_insert_intake_must_link_all_drug_components()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_intake_count integer;
	_component_count integer;
	_pk_patient integer;
	_pk_brand integer;
BEGIN
	if NEW.fk_drug_component is NULL then
		return NEW;
	end if;

	select fk_patient into _pk_patient
	from clin.encounter
	where pk = NEW.fk_encounter;

	-- get the brand we are linking to
	select fk_brand into _pk_brand
	from ref.lnk_substance2brand
	where fk_substance = NEW.fk_drug_component;

	-- get the number of components in the brand we are linking to
	select count(1) into _component_count
	from ref.lnk_substance2brand
	where fk_brand = _pk_brand;

	-- get the total number of intakes which are linking to the brand we are linking to
	select count(1) into _intake_count
	from clin.substance_intake
	where
		fk_drug_component in (
			select fk_substance from ref.lnk_substance2brand where fk_brand = _pk_brand
		)
			and
		fk_encounter in (
			select pk from clin.encounter where fk_patient = _pk_patient
		);

	-- they should match
	if _component_count = _intake_count then
		return NEW;
	end if;

	raise exception ''[ref.trf_insert_intake_must_link_all_drug_components] linking brand must link all components (patient <%>, component <%> of brand <%>)'', _pk_patient, NEW.fk_substance, _pk_brand;

	return NEW;
END;';

comment on function ref.trf_insert_intake_must_link_all_drug_components() is
	'If a patient is put on a multi-component drug they must be put on ALL components thereof.';

create constraint trigger tr_insert_intake_must_link_all_drug_components
	after insert
	on clin.substance_intake
	deferrable
	initially deferred
		for each row execute procedure ref.trf_insert_intake_must_link_all_drug_components();

-- --------------------------------------------------------------
-- UPDATE
\unset ON_ERROR_STOP
drop function ref.trf_update_intake_must_link_all_drug_components() cascade;
\set ON_ERROR_STOP 1

create or replace function ref.trf_update_intake_must_link_all_drug_components()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_intake_count integer;
	_component_count integer;
	_pk_patient integer;
	_pk_brand integer;
BEGIN
	if NEW.fk_drug_component is not distinct from OLD.fk_drug_component then
		return NEW;
	end if;

	select fk_patient into _pk_patient
	from clin.encounter
	where pk = NEW.fk_encounter;

	-- check the OLD brand unless it is NULL
	if OLD.fk_drug_component is not NULL then
		-- get the brand we were linking to
		select fk_brand into _pk_brand
		from ref.lnk_substance2brand
		where fk_substance = OLD.fk_drug_component;

		-- How many substance intake links for this drug have we got ?
		select count(1) into _intake_count
		from clin.substance_intake
		where
			fk_drug_component in (
				select fk_substance from ref.lnk_substance2brand where fk_brand = _pk_brand
			)
				and
			fk_encounter in (
				select pk from clin.encounter where fk_patient = _pk_patient
			);

		-- unlinking completely would be fine but else:
		if _intake_count != 0 then
			-- How many components *are* there in the drug in question ?
			select count(1) into _component_count
			from ref.lnk_substance2brand
			where fk_brand = _pk_brand;

			-- substance intake link count and number of components must match
			if _component_count != _intake_count then
				raise exception ''[ref.trf_update_intake_must_link_all_drug_components] re-linking brand must unlink all components of old brand [%] (component [% -> %])'', _pk_brand, OLD.fk_drug_component, NEW.fk_drug_component;
			end if;
		end if;
	end if;

	-- check the NEW brand unless it is NULL
	if NEW.fk_drug_component is not NULL then
		-- get the brand we were linking to
		select fk_brand into _pk_brand
		from ref.lnk_substance2brand
		where fk_substance = NEW.fk_drug_component;

		-- How many substance intake links for this drug have we got ?
		select count(1) into _intake_count
		from clin.substance_intake
		where
			fk_drug_component in (
				select fk_substance from ref.lnk_substance2brand where fk_brand = _pk_brand
			)
				and
			fk_encounter in (
				select pk from clin.encounter where fk_patient = _pk_patient
			);

		-- unlinking completely would be fine but else:
		if _intake_count != 0 then
			-- How many components *are* there in the drug in question ?
			select count(1) into _component_count
			from ref.lnk_substance2brand
			where fk_brand = _pk_brand;

			-- substance intake link count and number of components must match
			if _component_count != _intake_count then
				raise exception ''[ref.trf_update_intake_must_link_all_drug_components] re-linking brand must link all components of new brand [%] (component [% -> %])'', _pk_brand, OLD.fk_drug_component, NEW.fk_drug_component;
			end if;
		end if;
	end if;

	return NEW;
END;';

comment on function ref.trf_update_intake_must_link_all_drug_components() is
	'If a patient is put on a different multi-component drug they must be put on ALL components thereof.';

create constraint trigger tr_update_intake_must_link_all_drug_components
	after update
	on clin.substance_intake
	deferrable
	initially deferred
	for each row execute procedure ref.trf_update_intake_must_link_all_drug_components();

-- --------------------------------------------------------------
-- DELETE
\unset ON_ERROR_STOP
drop function ref.trf_delete_intake_must_unlink_all_drug_components() cascade;
\set ON_ERROR_STOP 1

create or replace function ref.trf_delete_intake_must_unlink_all_drug_components()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_intake_count integer;
	_component_count integer;
	_pk_patient integer;
	_pk_brand integer;
BEGIN
	if OLD.fk_drug_component is NULL then
		return NEW;
	end if;

	select fk_patient into _pk_patient
	from clin.encounter
	where pk = NEW.fk_encounter;

	-- get the brand we are linking to
	select fk_brand into _pk_brand
	from ref.lnk_substance2brand
	where fk_substance = OLD.fk_drug_component;

	-- How many substance intake links for this drug have we got ?
	select count(1) into _intake_count
	from clin.substance_intake
	where
		fk_drug_component in (
			select fk_substance from ref.lnk_substance2brand where fk_brand = _pk_brand
		)
			and
		fk_encounter in (
			select pk from clin.encounter where fk_patient = _pk_patient
		);

	-- unlinking completely is fine
	if _intake_count = 0 then
		return NEW;
	end if;

	-- How many components *are* there in the drug in question ?
	select count(1) into _component_count
	from ref.lnk_substance2brand
	where fk_brand = _pk_brand;

	-- substance intake link count and number of components must match
	if _component_count = _intake_count then
		return NEW;
	end if;

	raise exception ''[ref.trf_delete_intake_must_unlink_all_drug_components] unlinking brand must unlink all components (brand [%] component [%])'', _pk_brand, OLD.fk_drug_component;

	return NEW;
END;';

comment on function ref.trf_delete_intake_must_unlink_all_drug_components() is
	'If a patient is stopped from a multi-component drug they must be stopped from ALL components thereof.';

create constraint trigger tr_delete_intake_must_unlink_all_drug_components
	after delete
	on clin.substance_intake
	deferrable
	initially deferred
	for each row execute procedure ref.trf_delete_intake_must_unlink_all_drug_components();

-- --------------------------------------------------------------
-- .fk_substance
comment on column clin.substance_intake.fk_substance is
'Links to a substance the patient is taking.

********************************************* 
DO NOT TRY TO USE THIS TO FIND OUT THE BRAND.

IT WILL BE WRONG.
*********************************************';

alter table clin.substance_intake
	alter column fk_substance
		drop not null;

\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint substance_intake_fk_substance_fkey cascade;
\set ON_ERROR_STOP 1

update clin.substance_intake set
	fk_substance = (
		select rcs.pk									-- "new" pk
		from ref.consumable_substance rcs
		where rcs.description = (						-- with description =
			select ccs.description						-- "old" description
			from clin.consumed_substance ccs
			where ccs.pk = fk_substance
		)
	)
where
	fk_drug_component is null
;

update clin.substance_intake set
	fk_substance = NULL
where
	fk_drug_component is not null
;

\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint clin_subst_intake_either_drug_or_substance cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_intake
	add constraint clin_subst_intake_either_drug_or_substance
		check (
			((fk_drug_component is null) and (fk_substance is not null))
				or
			((fk_drug_component is not null) and (fk_substance is null))
		);

alter table clin.substance_intake
	add foreign key (fk_substance)
		references ref.consumable_substance(pk)
		on update cascade
		on delete cascade;

-- --------------------------------------------------------------
-- .preparation
alter table clin.substance_intake
	alter column preparation
		drop not null;

update clin.substance_intake set
	preparation = null
where
	fk_drug_component is not null
;

\unset ON_ERROR_STOP
alter table clin.substance_intake drop constraint clin_subst_intake_sane_prep cascade;
\set ON_ERROR_STOP 1

alter table clin.substance_intake
	add constraint clin_subst_intake_sane_prep
		check (
			((fk_drug_component is null) and (preparation is not null))
				or
			((fk_drug_component is not null) and (preparation is null))
		);

-- --------------------------------------------------------------
-- cleanup
\unset ON_ERROR_STOP
alter table clin.substance_intake drop column tmp_unit cascade;
alter table clin.substance_intake drop column tmp_amount cascade;
alter table clin.substance_intake drop column fk_brand cascade;
alter table audit.log_substance_intake drop column fk_brand cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-clin-substance_intake-dynamic.sql', 'Revision: 1.1');

-- ==============================================================
