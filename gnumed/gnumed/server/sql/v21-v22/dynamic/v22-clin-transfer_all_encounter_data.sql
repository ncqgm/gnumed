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
drop function if exists clin.transfer_all_encounter_data(IN _pk_source_encounter integer, IN _pk_target_encounter integer, OUT _o_success BOOLEAN) cascade;

-- --------------------------------------------------------------
create function clin.transfer_all_encounter_data(IN _pk_source_encounter integer, IN _pk_target_encounter integer)
	returns boolean
	security definer
	language 'plpgsql'
	as '
DECLARE
	_fk_row record;
	_success boolean;
BEGIN
	-- same patient on both encounters ?
	SELECT (
		coalesce((select fk_patient from clin.encounter where pk = _pk_source_encounter), -1)
			=
		coalesce((select fk_patient from clin.encounter where pk = _pk_target_encounter), -2)
	) INTO strict _success;
	IF _success IS FALSE THEN
		RAISE NOTICE ''source encounter (%) belongs to a patient different from target encounter (%), aborting'', _pk_source_encounter, _pk_target_encounter;
		RETURN FALSE;
	END IF;

	-- loop over foreign keys in non-clin.* tables
	FOR _fk_row IN
		SELECT
			conrelid::pg_catalog.regclass
				as referencing_table,
			(select attname from pg_attribute where attnum = pg_c.conkey[1] and attrelid = pg_c.conrelid) as referencing_column
		FROM
			pg_catalog.pg_constraint pg_c
		WHERE
			pg_c.confrelid = ''clin.encounter''::pg_catalog.regclass
				AND
			pg_c.contype = ''f''
				AND
			position(''clin.''::text in pg_c.conrelid::pg_catalog.regclass::text) = 0
	LOOP
		EXECUTE format (
			''UPDATE %1$s SET %2$I = %3$L WHERE %2$I = %4$L'',
				_fk_row.referencing_table,
				_fk_row.referencing_column,
				_pk_target_encounter,
				_pk_source_encounter
		);
	END LOOP;

	-- update clin.clin_root_item children in one go
	UPDATE clin.clin_root_item SET fk_encounter = _pk_target_encounter WHERE fk_encounter = _pk_source_encounter;

	return TRUE;
END;';

comment on function clin.transfer_all_encounter_data(IN _pk_source_encounter integer, IN _pk_target_encounter integer, OUT _o_success BOOLEAN) is
	'transfers all data linked to _pk_source_encounter into _pk_target_encounter';

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-transfer_all_encounter_data.sql', '22.0');
