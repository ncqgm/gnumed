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
drop function if exists clin.trf_delete_intake_document_deleted() cascade;
drop function if exists clin.trf_DEL_intake_document_deleted() cascade;

create function clin.trf_DEL_intake_document_deleted()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_row record;
	_pk_episode integer;
BEGIN
	select
		* into _row
	from
		clin.v_substance_intake_journal
	where
		src_pk = OLD.pk;

	_pk_episode := _row.pk_episode;

	-- create episode if needed
	if _pk_episode is null then
		select pk into _pk_episode
		from clin.episode
		where
			description = _(''Medication history'')
				and
			fk_encounter in (
				select pk from clin.encounter where fk_patient = _row.pk_patient
			);
		if not found then
			insert into clin.episode (
				description,
				is_open,
				fk_encounter
			) values (
				_(''Medication history''),
				FALSE,
				OLD.fk_encounter
			) returning pk into _pk_episode;
		end if;
	end if;

	insert into clin.clin_narrative (
		fk_encounter,
		fk_episode,
		soap_cat,
		narrative
	) values (
		_row.pk_encounter,
		_pk_episode,
		NULL,
		_(''Deletion of'') || '' '' || _row.narrative
	);

	return OLD;
END;';

comment on function clin.trf_DEL_intake_document_deleted() is
	'Document the deletion of a substance intake.';

create trigger tr_DEL_intake_document_deleted
	before delete on clin.substance_intake
	for each row execute procedure clin.trf_DEL_intake_document_deleted();

-- --------------------------------------------------------------
drop function if exists clin.trf_delete_intake_turns_other_components_into_substances() cascade;
drop function if exists clin.trf_DEL_intake_turns_other_components_into_substances() cascade;

create or replace function clin.trf_DEL_intake_turns_other_components_into_substances()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_pk_brand integer;
	_component_count integer;
	_pk_patient integer;
BEGIN
	return NULL;

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
--	delete from clin.substance_intake c_si1 where
--		-- entries which belong to the brand in question
--		c_si1.fk_drug_component in (
--			select pk from ref.lnk_substance2brand where fk_brand = _pk_brand
--		)
--			and
--		-- entries for this one patient only (via proxy of encounter)
--		c_si1.fk_encounter in (
--			select pk from clin.encounter where fk_patient = _pk_patient
--		)
--			and
--		-- which already exist
--		exists (
--			select 1 from clin.substance_intake c_si2
--			where
--				-- as substance-only links
--				c_si2.fk_substance = (
--					select fk_substance from ref.lnk_substance2brand where pk = c_si1.fk_drug_component
--				)
--					and
--				-- for this very patient
--				c_si2.fk_encounter in (
--					select pk from clin.encounter where fk_patient = _pk_patient
--				)
--		)
--	;

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

comment on function clin.trf_DEL_intake_turns_other_components_into_substances() is
	'If a patient is stopped from a multi-component drug intake other components thereof must be turned into non-brand substance intakes.';

create trigger tr_DEL_intake_turns_other_components_into_substances
	after delete on clin.substance_intake
	for each row execute procedure clin.trf_DEL_intake_turns_other_components_into_substances();

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-substance_intake-delete_triggers.sql', '22.0');
