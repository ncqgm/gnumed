-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function blobs.trf_set_intended_reviewer() cascade;
\set ON_ERROR_STOP 1


create function blobs.trf_set_intended_reviewer()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_pk_patient integer;
	_pk_provider integer;
BEGIN
	-- explicitly set ?
	if NEW.fk_intended_reviewer is not NULL then
		return NEW;
	end if;

	-- find patient via document
	select
		fk_patient into _pk_patient
	from
		clin.encounter
	where
		clin.encounter.pk = (
			select fk_encounter from blobs.doc_med where pk = NEW.fk_doc
		);

	-- does patient have primary provider ?
	select
		fk_primary_provider into _pk_provider
	from
		dem.identity
	where
		dem.identity.pk = _pk_patient;

	if _pk_provider is not NULL then
		NEW.fk_intended_reviewer := _pk_provider;
		return NEW;
	end if;

	-- else use CURRENT_USER
	select
		pk into _pk_provider
	from
		dem.staff
	where
		dem.staff.db_user = current_user;

	NEW.fk_intended_reviewer := _pk_provider;
	return NEW;
END;';


comment on function blobs.trf_set_intended_reviewer() is
	'Set the default on blobs.doc_obj.fk_intended_reviewer.';


create trigger tr_set_default_intended_reviewer
	before insert or update on blobs.doc_obj
		for each row execute procedure blobs.trf_set_intended_reviewer()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-blobs-doc_obj-dynamic.sql', 'v16');

-- ==============================================================
