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
drop function if exists clin.trf_insert_intake_prevent_duplicate_component_links() cascade;
drop function if exists clin.trf_ins_intake_prevent_duplicate_component_links() cascade;

create or replace function clin.trf_ins_intake_prevent_duplicate_component_links()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_pk_patient integer;
	_pk_intake integer;
	_msg text;
BEGIN
	-- which patient ?
	select fk_patient into _pk_patient
	from clin.encounter
	where pk = NEW.fk_encounter;

	-- already exists ?
	select pk into _pk_intake
	from clin.substance_intake
	where
		fk_encounter in (
			select pk from clin.encounter where fk_patient = _pk_patient
		)
			and
		fk_drug_component = NEW.fk_drug_component
	;

	if FOUND then
		_msg := ''[clin.trf_ins_intake_prevent_duplicate_component_links]: drug component ref.lnk_dose2drug.pk=('' || NEW.fk_drug_component || '') ''
			|| ''already linked to patient=('' || _pk_patient || '') ''
			|| ''as clin.substance_intake.pk=('' || _pk_intake || '')'';
		raise exception unique_violation using message = _msg;
	end if;

	return NEW;
END;';

comment on function clin.trf_ins_intake_prevent_duplicate_component_links() is
	'Prevent patient from being put on a particular component twice.';

create trigger tr_insert_intake_prevent_duplicate_component_links
	before insert
	on clin.substance_intake
		for each row execute procedure clin.trf_ins_intake_prevent_duplicate_component_links();

-- --------------------------------------------------------------
drop function if exists clin.trf_insert_intake_links_all_drug_components() cascade;

create or replace function clin.trf_insert_intake_links_all_drug_components()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_component_count integer;
	_pk_patient integer;
	_pk_drug_product integer;
	_pk_component integer;
BEGIN
	-- get the product we are linking to
	select fk_drug_product into _pk_drug_product
	from ref.lnk_dose2drug
	where pk = NEW.fk_drug_component;

	-- how many components therein ?
	select count(1) into _component_count
	from ref.lnk_dose2drug
	where fk_drug_product = _pk_drug_product;

	-- only one component ?
	if _component_count = 1 then
		return NEW;
	end if;

	-- which patient ?
	select fk_patient into _pk_patient
	from clin.encounter
	where pk = NEW.fk_encounter;

	-- INSERT all components
	for _pk_component in
		select pk from ref.lnk_dose2drug where fk_drug_product = _pk_drug_product
	loop
		-- already there ?
		perform 1 from clin.substance_intake where
			fk_encounter in (
				select pk from clin.encounter where fk_patient = _pk_patient
			)
				and
			fk_drug_component = _pk_component
		;
		if FOUND then
			continue;
		end if;

		-- insert
		insert into clin.substance_intake (
			fk_drug_component,				-- differentiate
			clin_when,						-- harmonize (started)
			fk_encounter,					-- harmonize
			fk_episode,						-- required
			soap_cat,						-- harmonize
			schedule,						-- harmonize
			duration,						-- harmonize
			intake_is_approved_of,			-- harmonize
			is_long_term,					-- harmonize
			discontinued,					-- harmonize
			narrative,
			aim,
			discontinue_reason,
			comment_on_start,
			harmful_use_type
		) values (
			_pk_component,
			NEW.clin_when,
			NEW.fk_encounter,
			NEW.fk_episode,
			NEW.soap_cat,
			NEW.schedule,
			NEW.duration,
			NEW.intake_is_approved_of,
			NEW.is_long_term,
			NEW.discontinued,
			NEW.narrative,
			NEW.aim,
			NEW.discontinue_reason,
			NEW.comment_on_start,
			NEW.harmful_use_type
		);
	end loop;

	return NEW;
END;';

comment on function clin.trf_insert_intake_links_all_drug_components() is
	'If a patient is put on a multi-component drug they must be put on ALL components thereof.';

create trigger tr_insert_intake_links_all_drug_components
	after insert on clin.substance_intake
		for each row execute procedure clin.trf_insert_intake_links_all_drug_components();

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-substance_intake-insert_triggers.sql', '22.0');
