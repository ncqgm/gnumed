-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to 'on';
set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- trigger
-- --------------------------------------------------------------

-- INSERT
\unset ON_ERROR_STOP
drop function clin.trf_insert_update_intake_prevent_duplicate_substance_links() cascade;
\set ON_ERROR_STOP 1

create or replace function clin.trf_insert_update_intake_prevent_duplicate_substance_links()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_pk_patient integer;
	_link_count integer;
	_msg text;
BEGIN
	-- any substance at all (rather than drug component) ?
	if NEW.fk_substance is NULL then
		return NEW;
	end if;

	-- which patient ?
	select fk_patient into _pk_patient
	from clin.encounter
	where pk = NEW.fk_encounter;

	-- more than one link ?
	select count(1) into _link_count
	from clin.substance_intake
	where
		-- for this substance
		fk_substance = NEW.fk_substance
			and
		-- in this one patient
		fk_encounter in (
			select pk from clin.encounter where fk_patient = _pk_patient
		)
	;

	if _link_count > 1 then
		_msg := ''[clin.trf_insert_update_intake_prevent_duplicate_substance_links]: substance ref.consumable_substance.pk=('' || NEW.fk_substance || '') ''
			|| ''already linked to patient=('' || _pk_patient || '') '';
		raise exception unique_violation using message = _msg;
	end if;

	return NEW;
END;';

comment on function clin.trf_insert_update_intake_prevent_duplicate_substance_links() is
	'Prevent patient from being put on a particular substance more than once.';

create constraint trigger tr_insert_update_intake_prevent_duplicate_substance_links
	after insert or update on clin.substance_intake
	deferrable
	initially deferred
		for each row execute procedure clin.trf_insert_update_intake_prevent_duplicate_substance_links()
;

-- --------------------------------------------------------------
-- DELETE
\unset ON_ERROR_STOP
drop function clin.trf_delete_intake_turns_other_components_into_substances() cascade;
\set ON_ERROR_STOP 1

create or replace function clin.trf_delete_intake_turns_other_components_into_substances()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_pk_brand integer;
	_component_count integer;
	_pk_patient integer;
BEGIN
	-- did it at all relate to a drug (rather than substance) ?
	if OLD.fk_drug_component is NULL then
		return NULL;
	end if;

	-- which drug ?
	select fk_brand into _pk_brand
	from ref.lnk_substance2brand
	where pk = OLD.fk_drug_component;

	-- how many components therein ?
	select count(1) into _component_count
	from ref.lnk_substance2brand
	where fk_brand = _pk_brand;

	-- only one component anyways ? (which then has been deleted already)
	if _component_count = 1 then
		return NULL;
	end if;

	-- which patient ?
	select fk_patient into _pk_patient
	from clin.encounter
	where pk = OLD.fk_encounter;

	-- delete those components which cannot be converted:
	delete from clin.substance_intake c_si1 where
		-- entries which belong to the brand in question
		c_si1.fk_drug_component in (
			select pk from ref.lnk_substance2brand where fk_brand = _pk_brand
		)
			and
		-- entries for this one patient only (via proxy of encounter)
		c_si1.fk_encounter in (
			select pk from clin.encounter where fk_patient = _pk_patient
		)
			and
		-- which already exist
		exists (
			select 1 from clin.substance_intake c_si2
			where
				-- as substance-only links
				c_si2.fk_substance = (
					select fk_substance from ref.lnk_substance2brand where pk = c_si1.fk_drug_component
				)
					and
				-- for this very patient
				c_si2.fk_encounter in (
					select pk from clin.encounter where fk_patient = _pk_patient
				)
		)
	;

	-- relink all other intakes into substances
	update clin.substance_intake c_si set
		fk_drug_component = null,
		fk_substance = (
			select fk_substance from ref.lnk_substance2brand where pk = c_si.fk_drug_component
		),
		preparation = (
			select r_bd.preparation from ref.branded_drug r_bd where r_bd.pk = _pk_brand
		)
	where
		-- ... which belong to the brand in question
		c_si.fk_drug_component in (
			select pk from ref.lnk_substance2brand where fk_brand = _pk_brand
		)
			and
		-- ... which belong to this one patient (via proxy of encounter)
		c_si.fk_encounter in (
			select pk from clin.encounter where fk_patient = _pk_patient
		)
	;

	return NULL;
END;';

comment on function clin.trf_delete_intake_turns_other_components_into_substances() is
	'If a patient is stopped from a multi-component drug intake other components thereof must be turned into non-brand substance intakes.';

create trigger tr_delete_intake_turns_other_components_into_substances
	after delete on clin.substance_intake
	for each row execute procedure clin.trf_delete_intake_turns_other_components_into_substances();

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-clin-substance_intake-dynamic.sql', '17.0');
