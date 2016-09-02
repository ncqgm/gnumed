-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to on;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop function if exists clin.trf_update_intake_must_link_all_drug_components() cascade;
drop function if exists clin.trf_upd_intake_must_link_all_drug_components() cascade;

create or replace function clin.trf_upd_intake_must_link_all_drug_components()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_intake_count integer;
	_component_count integer;
	_pk_patient integer;
	_pk_brand integer;
	_msg text;
BEGIN
	select fk_patient into _pk_patient
	from clin.encounter
	where pk = NEW.fk_encounter;

	-- get the brand we were linking to
	select fk_brand into _pk_brand
	from ref.lnk_dose2drug
	where pk = OLD.fk_drug_component;

	-- How many substance intake links for this drug have we got ?
	select count(1) into _intake_count
	from clin.substance_intake
	where
		fk_drug_component in (
			select pk from ref.lnk_dose2drug where fk_brand = _pk_brand
		)
			and
		fk_encounter in (
			select pk from clin.encounter where fk_patient = _pk_patient
		);

	-- unlinking completely would be fine but else:
	if _intake_count != 0 then
		-- How many components *are* there in the drug in question ?
		select count(1) into _component_count
		from ref.lnk_dose2drug
		where fk_brand = _pk_brand;

		-- substance intake link count and number of components must match
		if _component_count != _intake_count then
			_msg := ''[clin.trf_upd_intake_must_link_all_drug_components]: re-linking brand must unlink all components of old brand ['' || _pk_brand || ''] ''
				|| ''(component ['' || OLD.fk_drug_component || '' -> '' || NEW.fk_drug_component || ''])'';
			raise exception check_violation using message = _msg;
		end if;
	end if;

	-- check the NEW brand

	-- get the brand we were linking to
	select fk_brand into _pk_brand
	from ref.lnk_dose2drug
	where fk_substance = NEW.fk_drug_component;

	-- How many substance intake links for this drug have we got ?
	select count(1) into _intake_count
	from clin.substance_intake
	where
		fk_drug_component in (
			select pk from ref.lnk_dose2drug where fk_brand = _pk_brand
		)
			and
		fk_encounter in (
			select pk from clin.encounter where fk_patient = _pk_patient
		);

	-- unlinking completely would be fine but else:
	if _intake_count != 0 then
		-- How many components *are* there in the drug in question ?
		select count(1) into _component_count
		from ref.lnk_dose2drug
		where fk_brand = _pk_brand;

		-- substance intake link count and number of components must match
		if _component_count != _intake_count then
			_msg := ''[clin.trf_upd_intake_must_link_all_drug_components]: re-linking brand must link all components of new brand ['' || _pk_brand || ''] ''
				|| ''(component ['' || OLD.fk_drug_component || '' -> '' || NEW.fk_drug_component || ''])'';
			raise exception check_violation using message = _msg;
		end if;
	end if;

	return NEW;
END;';

comment on function clin.trf_upd_intake_must_link_all_drug_components() is
	'If a patient is put on a different multi-component drug ALL components thereof must be updated.';

create constraint trigger tr_upd_intake_must_link_all_drug_components
	after update on
		clin.substance_intake
	deferrable
	initially deferred
	for
		each row
	when
		(NEW.fk_drug_component is distinct from OLD.fk_drug_component)
	execute procedure
		clin.trf_upd_intake_must_link_all_drug_components();

-- --------------------------------------------------------------
drop function if exists clin.trf_upd_intake_updates_all_drug_components() cascade;

create or replace function clin.trf_upd_intake_updates_all_drug_components()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_pk_brand integer;
	_component_count integer;
	_pk_patient integer;
BEGIN
	-- which drug ?
	select fk_brand into _pk_brand
	from ref.lnk_dose2drug
	where pk = NEW.fk_drug_component;

	-- how many components therein ?
	select count(1) into _component_count
	from ref.lnk_dose2drug
	where fk_brand = _pk_brand;

	-- only one component ?
	if _component_count = 1 then
		return NEW;
	end if;

	-- which patient ?
	select fk_patient into _pk_patient
	from clin.encounter
	where pk = NEW.fk_encounter;

	-- update all substance instake fields shared by drug components ...
	update clin.substance_intake set
		clin_when = NEW.clin_when,				-- started
		fk_encounter = NEW.fk_encounter,
		soap_cat = NEW.soap_cat,
		schedule = NEW.schedule,
		duration = NEW.duration,
		intake_is_approved_of = NEW.intake_is_approved_of,
		is_long_term = NEW.is_long_term,
		discontinued = NEW.discontinued
	where
		-- ... which belong to this drug ...
		fk_drug_component in (
			select pk from ref.lnk_dose2drug where fk_brand = _pk_brand
		)
			AND
		-- ... but are not THIS component ...
		fk_drug_component != NEW.fk_drug_component
			AND
		-- ... this patient ...
		fk_encounter in (
			select pk from clin.encounter where fk_patient = _pk_patient
		)
			AND
		-- ... are different in value (this will stop recursion as soon as all are equal)
		(
			clin_when is distinct from NEW.clin_when
				OR
			fk_encounter is distinct from NEW.fk_encounter
				OR
			soap_cat is distinct from NEW.soap_cat
				OR
			schedule is distinct from NEW.schedule
				OR
			duration is distinct from NEW.duration
				OR
			intake_is_approved_of is distinct from NEW.intake_is_approved_of
				OR
			is_long_term is distinct from NEW.is_long_term
				OR
			discontinued is distinct from NEW.discontinued
		)
	;
	return NEW;
END;';

comment on function clin.trf_upd_intake_updates_all_drug_components() is
	'If a drug component substance intake is updated all sibling components must receive some values thereof.';

create constraint trigger tr_upd_intake_updates_all_drug_components
	after update on clin.substance_intake
		deferrable
		initially deferred
	for each row when (
		(pg_trigger_depth() = 0)
	)
	execute procedure clin.trf_upd_intake_updates_all_drug_components();

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-substance_intake-update_triggers.sql', '22.0');
