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
-- .fk_test_types
drop function if exists clin.trf_ins_upd_validate_test_type_pks() cascade;

-- --------------------------------------------------------------
-- convert existing panels
drop function if exists staging.v22_convert_test_panels() cascade;

create function staging.v22_convert_test_panels()
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_row_test_panel record;
	_pk_test_type integer;
	_test_name text;
	_loinc text;
BEGIN
	-- already converted ?
	BEGIN
		PERFORM fk_test_types FROM clin.test_panel LIMIT 1;
	EXCEPTION
		-- 42703
		WHEN undefined_column THEN
			RAISE NOTICE ''staging.v22_convert_test_panels(): Column clin.test_panel.fk_test_types does not exists. Already converted ? Aborting.'';
			RETURN FALSE;
	END;

	-- loop over test panels
	FOR _row_test_panel IN
		SELECT * FROM clin.test_panel
	LOOP
		-- any types linked to this panel ?
		IF _row_test_panel.fk_test_types IS NULL THEN
			CONTINUE;
		END IF;
		RAISE NOTICE ''staging.v22_convert_test_panels(): converting test panel "%" (%)'', _row_test_panel.description, _row_test_panel.pk;
		-- loop over test types
		FOREACH _pk_test_type IN ARRAY _row_test_panel.fk_test_types LOOP
			RAISE NOTICE ''staging.v22_convert_test_panels(): transferring test type #%'', _pk_test_type;
			SELECT loinc, name INTO _loinc, _test_name FROM clin.test_type WHERE pk = _pk_test_type;
			IF FOUND IS FALSE THEN
				RAISE NOTICE ''staging.v22_convert_test_panels(): test type on panel but does not exist anymore, skipping'';
				CONTINUE;
			END IF;
			IF _loinc IS NULL THEN
				_loinc := ''pseudo LOINC ['' || _test_name || ''::'' || _pk_test_type || ''] (v21->v22 test panel conversion)'';
				RAISE NOTICE ''staging.v22_convert_test_panels(): generated pseudo LOINC for "%": %'', _test_name, _loinc;
				UPDATE clin.test_type SET loinc = _loinc WHERE pk = _pk_test_type;
			END IF;
			INSERT INTO clin.lnk_loinc2test_panel (fk_test_panel, loinc)
				SELECT
					_row_test_panel.pk, _loinc
				WHERE NOT EXISTS (
					SELECT 1 FROM clin.lnk_loinc2test_panel
					WHERE
						fk_test_panel = _row_test_panel.pk
							AND
						loinc = _loinc
				);
		END LOOP;
	END LOOP;

	RAISE NOTICE ''dropping column clin.test_panel.fk_test_types'';
	ALTER TABLE clin.test_panel DROP COLUMN fk_test_types CASCADE;

	RETURN TRUE;
END;';


-- actually convert
select staging.v22_convert_test_panels();

-- cleanup
drop function if exists staging.v22_convert_test_panels() cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-convert_test_panels.sql', '22.0');
