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
drop view if exists ref.v_auto_hints cascade;

create view ref.v_auto_hints as
select
	pk
		as pk_auto_hint,
	query
		as query,
	title
		as title,
	hint
		as hint,
	url
		as url,
	is_active
		as is_active,
	source
		as source,
	lang
		as lang,
	-- this column is set from clin.get_hints_for_patient(),
	-- it only exists in this view in order to enable the
	-- syntax "returns setof ref.v_auto_hints" in that
	-- function
	null::text
		as rationale4suppression,
	md5(coalesce(query, '')
		|| coalesce(title, '')
		|| coalesce(hint, '')
		|| coalesce(url, '')
	)	as md5_sum,
	xmin
		as xmin_auto_hint
from
	ref.auto_hint
;


revoke all on ref.v_auto_hints from public;
grant select on ref.v_auto_hints to group "gm-staff";

-- --------------------------------------------------------------
drop function if exists clin.get_hints_for_patient(integer) cascade;

create function clin.get_hints_for_patient(integer)
	returns setof ref.v_auto_hints
	language 'plpgsql'
	as '
DECLARE
	_pk_identity ALIAS FOR $1;
	_hint ref.v_auto_hints%rowtype;
	_query text;
	_suppressed_and_unchanged boolean;
	_md5_suppressed text;
	_rationale4suppression text;
	_applies boolean;
--	_exc_state text;
--	_exc_msg text;
--	_exc_detail text;
--	_exc_hint text;
--	_exc_context text;
BEGIN
	FOR _hint IN SELECT * FROM ref.v_auto_hints WHERE is_active LOOP

		-- is the hint suppressed ?
		SELECT md5_sum, rationale INTO _md5_suppressed, _rationale4suppression FROM clin.suppressed_hint WHERE fk_identity = _pk_identity AND fk_hint = _hint.pk_auto_hint;
		IF FOUND THEN
			-- is the hint unchanged ?
			IF _md5_suppressed = _hint.md5_sum THEN
				CONTINUE;
			END IF;
			_hint.rationale4suppression := _rationale4suppression;
		END IF;

		_query := replace(_hint.query, ''ID_ACTIVE_PATIENT'', _pk_identity::text);
		BEGIN
			EXECUTE _query INTO STRICT _applies;
			--RAISE NOTICE ''Applies: %'', _applies;
			IF _applies THEN
				RETURN NEXT _hint;
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
				_hint.title := ''ERROR checking for ['' || _hint.title || ''] !'';
				_hint.hint := _query;
				RETURN NEXT _hint;
		END;
	END LOOP;
	RETURN;
END;';

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-ref-v_auto_hints.sql', '20.0');
