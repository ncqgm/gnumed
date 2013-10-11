-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1
set check_function_bodies to on;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
create or replace function clin.get_hints_for_patient(integer)
	returns setof ref.auto_hint
	language 'plpgsql'
	as '
DECLARE
	_pk_identity ALIAS FOR $1;
	_r ref.auto_hint%rowtype;
	_query text;
	_applies boolean;
--	_exc_state text;
--	_exc_msg text;
--	_exc_detail text;
--	_exc_hint text;
--	_exc_context text;
BEGIN
	FOR _r IN SELECT * FROM ref.auto_hint WHERE is_active LOOP
		_query := replace(_r.query, ''ID_ACTIVE_PATIENT'', _pk_identity::text);
		--RAISE NOTICE ''%'', _query;
		BEGIN
			EXECUTE _query INTO STRICT _applies;
			--RAISE NOTICE ''Applies: %'', _applies;
			IF _applies THEN
				RETURN NEXT _r;
			END IF;
		EXCEPTION
			--WHEN insufficient_privilege THEN RAISE WARNING ''auto hint query failed: %'', _query;
			WHEN others THEN
				RAISE WARNING ''auto hint query failed: %'', _query;
				-- only available starting with PG 9.2:
				--GET STACKED DIAGNOSTICS
				--	_exc_state = RETURNED_SQLSTATE,
				--	_exc_msg = MESSAGE_TEXT,
				--	_exc_detail = PG_EXCEPTION_DETAIL,
				--	_exc_hint = PG_EXCEPTION_HINT,
				--	_exc_context = PG_EXCEPTION_CONTEXT;
				--RAISE WARNING ''SQL STATE: %'', _exc_state;
				--RAISE WARNING ''MESSAGE: %'', _exc_msg;
				--RAISE WARNING ''DETAIL: %'', _exc_detail;
				--RAISE WARNING ''HINT: %'', _exc_hint;
				--RAISE WARNING ''CONTEXT: %'', _exc_context;
				-- workaround for 9.1:
				RAISE WARNING ''SQL STATE: %'', SQLSTATE;
				RAISE WARNING ''MESSAGE: %'', SQLERRM;
				_r.title := ''ERROR checking for ['' || _r.title || ''] !'';
				_r.hint := _query;
				RETURN NEXT _r;
		END;
	END LOOP;
	RETURN;
END;';

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-clin-get_hints_for_patient.sql', '19.0');
