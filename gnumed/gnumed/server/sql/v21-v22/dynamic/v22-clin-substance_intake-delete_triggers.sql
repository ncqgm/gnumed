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
drop function if exists clin.trf_del_intake_must_unlink_all_drug_components() cascade;

create or replace function clin.trf_del_intake_must_unlink_all_drug_components()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_pk_drug_product integer;
	_component_count integer;
	_pk_patient integer;
	_intake_count integer;
	_msg text;
BEGIN
	-- which drug ?
	select fk_drug_product into _pk_drug_product
	from ref.lnk_dose2drug
	where pk = OLD.fk_drug_component;

	-- how many components therein ?
	select count(1) into _component_count
	from ref.lnk_dose2drug
	where fk_drug_product = _pk_drug_product;

	-- only one component anyways ?
	if _component_count = 1 then
		return NULL;
	end if;

	-- retrieve patient
	select fk_patient into _pk_patient
	from clin.encounter
	where pk = OLD.fk_encounter;

	-- how many intakes of this drug are linked to this patient
	select count(1) into _intake_count
	from clin.substance_intake
	where
		fk_drug_component in (
			select pk from ref.lnk_dose2drug where fk_drug_product = _pk_drug_product
		)
			and
		fk_encounter in (
			select pk from clin.encounter where fk_patient = _pk_patient
		);

	-- intake count must be 0
	if _intake_count = 0 then
		return NULL;
	end if;

	_msg := ''[clin.trf_del_intake_must_unlink_all_drug_components]: deleting a multi-component intake [''
		|| OLD.pk || ''] must unlink all components of the drug product [''
		|| _pk_drug_product || ''] ''
		|| ''(unlinked component ['' || OLD.fk_drug_component || ''])'';
	raise exception check_violation using message = _msg;

	return NULL;
END;';

comment on function clin.trf_del_intake_must_unlink_all_drug_components() is
	'If a multi-component drug intake is deleted from a patient ALL components thereof must be unlinked.';

create constraint trigger tr_del_intake_must_unlink_all_drug_components
	after delete on clin.substance_intake
	deferrable initially deferred
	for each row
	execute procedure clin.trf_del_intake_must_unlink_all_drug_components();

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-substance_intake-delete_triggers.sql', '22.0');
