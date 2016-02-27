-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
comment on column clin.substance_intake.comment_on_start is 'Comment (uncertainty level) on .clin_when = started. "?" = "entirely unknown".';

alter table clin.substance_intake
	alter column comment_on_start
		set default NULL;

alter table clin.substance_intake
	drop constraint if exists clin_substance_intake_sane_start_comment;

alter table clin.substance_intake
	add constraint clin_substance_intake_sane_start_comment check (
		gm.is_null_or_non_empty_string(comment_on_start)
	);

-- --------------------------------------------------------------
comment on column clin.substance_intake.harmful_use_type is
	'NULL=not considered=medication, 0=no or not considered harmful, 1=presently harmful use, 2=presently addicted, 3=previously addicted';


alter table clin.substance_intake
	drop constraint if exists clin_patient_sane_use_type;

alter table clin.substance_intake
	add constraint clin_patient_sane_use_type check (
		(harmful_use_type IS NULL)
			OR
		(harmful_use_type between 0 and 3)
	);

-- --------------------------------------------------------------
-- .fk_substance / .fk_drug_component
drop function if exists clin.trf_update_intake_updates_all_drug_components() cascade;
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
	from ref.lnk_substance2brand
	where pk = NEW.fk_drug_component;

	-- how many components therein ?
	select count(1) into _component_count
	from ref.lnk_substance2brand
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
			select pk from ref.lnk_substance2brand where fk_brand = _pk_brand
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
			and
		(NEW.fk_drug_component is not null)
	)
	execute procedure clin.trf_upd_intake_updates_all_drug_components();

-- --------------------------------------------------------------
drop function if exists clin.trf_insert_update_intake_prevent_duplicate_substance_links() cascade;
drop function if exists clin.trf_ins_upd_intake_prevent_duplicate_substance_links() cascade;

create or replace function clin.trf_ins_upd_intake_prevent_duplicate_substance_links()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_pk_patient integer;
	_link_count integer;
	_msg text;
BEGIN
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
		-- either already linked as component OR
		-- already linked as substance
		fk_drug_component IS NOT DISTINCT FROM NEW.fk_drug_component
			and
		-- in this one patient
		fk_encounter in (
			select pk from clin.encounter where fk_patient = _pk_patient
		)
	;

	if _link_count > 1 then
		_msg := ''[clin.trf_ins_upd_intake_prevent_duplicate_substance_links]: substance ref.consumable_substance.pk=('' || NEW.fk_substance || '') ''
			|| ''already linked to patient=('' || _pk_patient || '') '';
		raise exception unique_violation using message = _msg;
	end if;

	return NEW;
END;';

comment on function clin.trf_ins_upd_intake_prevent_duplicate_substance_links() is
	'Prevent patient from being put on a particular substance more than once.';

create constraint trigger tr_ins_upd_intake_prevent_duplicate_substance_links
	after insert or update on clin.substance_intake
	deferrable
	initially deferred
		for each row execute procedure clin.trf_ins_upd_intake_prevent_duplicate_substance_links()
;

-- --------------------------------------------------------------
drop function if exists clin.trf_ins_intake_set_substance_from_component() cascade;

create function clin.trf_ins_intake_set_substance_from_component()
	returns trigger
	language 'plpgsql'
	as '
BEGIN
	-- load fk_substance from drug_component table
	select
		r_ls2b.fk_substance into strict NEW.fk_substance
	from
		ref.lnk_substance2brand r_ls2b
	where
		r_ls2b.pk = NEW.fk_drug_component
	;
	return NEW;
END;';

comment on function clin.trf_ins_intake_set_substance_from_component() is
	'On INSERT of a substance intake set fk_substance from fk_drug_component if the latter is NOT NULL.';

create trigger tr_ins_intake_set_substance_from_component
	before INSERT on clin.substance_intake
	for each row when (NEW.fk_drug_component is not null)
	execute procedure clin.trf_ins_intake_set_substance_from_component();

-- --------------------------------------------------------------
drop function if exists clin.trf_upd_intake_set_substance_from_component() cascade;

create function clin.trf_upd_intake_set_substance_from_component()
	returns trigger
	language 'plpgsql'
	as '
BEGIN
	-- load fk_substance from drug_component table
	select
		r_ls2b.fk_substance into strict NEW.fk_substance
	from
		ref.lnk_substance2brand r_ls2b
	where
		r_ls2b.pk = NEW.fk_drug_component
	;
	return NEW;
END;';

comment on function clin.trf_upd_intake_set_substance_from_component() is
	'On UPDATE of a substance intake set fk_substance from fk_drug_component if the latter changes.';

create trigger tr_upd_intake_set_substance_from_component
	before UPDATE on clin.substance_intake
	for each row when (
		(NEW.fk_drug_component is not null)
			and
		(NEW.fk_drug_component is distinct from OLD.fk_drug_component)
	)
	execute procedure clin.trf_upd_intake_set_substance_from_component();

-- --------------------------------------------------------------
alter table clin.substance_intake
	drop constraint if exists clin_subst_intake_either_drug_or_substance cascade;

-- --------------------------------------------------------------
-- normalize existing records
update clin.substance_intake set
	fk_substance = (
		select r_ls2b.fk_substance
		from ref.lnk_substance2brand r_ls2b
		where r_ls2b.pk = fk_drug_component
	)
where
	fk_substance is null
;

-- --------------------------------------------------------------
alter table clin.substance_intake
	alter column fk_substance
		set not null;

-- --------------------------------------------------------------
-- DELETE substance intake
drop function if exists clin.trf_delete_intake_document_deleted() cascade;

create function clin.trf_delete_intake_document_deleted()
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

comment on function clin.trf_delete_intake_document_deleted() is
	'Document the deletion of a substance intake.';

create trigger tr_delete_intake_document_deleted
	before delete on clin.substance_intake
	for each row execute procedure clin.trf_delete_intake_document_deleted();

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-substance_intake-dynamic.sql', '21.0');
