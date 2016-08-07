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
drop view if exists staging.journal_without_suppressed_hints cascade;

create view staging.journal_without_suppressed_hints as
select * from clin.v_emr_journal
where
	src_table != 'clin.suppressed_hint'
;

grant select on staging.journal_without_suppressed_hints to group "gm-staff";

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
	_sanitized_query text;
	_md5_suppressed text;
	_rationale4suppression text;
	_suppression_exists boolean;		-- does not mean that the suppression applies
	_hint_currently_applies boolean;	-- regardless of whether suppressed or not
	_hint_recommendation text;
--	_exc_state text;
--	_exc_msg text;
--	_exc_detail text;
--	_exc_hint text;
--	_exc_context text;
BEGIN
	-- loop over all defined hints
	FOR _hint IN SELECT * FROM ref.v_auto_hints WHERE is_active LOOP

		-- is the hint suppressed ?
		SELECT
			md5_sum,
			rationale
				INTO
			_md5_suppressed,
			_rationale4suppression
		FROM clin.suppressed_hint WHERE
			fk_hint = _hint.pk_auto_hint
				AND
			fk_encounter IN (
				SELECT pk FROM clin.encounter WHERE fk_patient = _pk_identity
			);
		IF FOUND THEN
			_suppression_exists := TRUE;
		ELSE
			_suppression_exists := FALSE;
		END IF;

		-- does the hint currently apply ? (regardless of whether it is suppressed)
		_query := replace(_hint.query, ''ID_ACTIVE_PATIENT'', _pk_identity::text);
		BEGIN
			EXECUTE _query INTO STRICT _hint_currently_applies;
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
				-- process next hint
				CONTINUE;
		END;

		-- does it _really_ apply ?
		-- re-run against staging.journal_without_suppressed_hints which does
		-- not contain suppressed hints -- because it may have applied only
		-- because clin.v_emr_journal does contain formatted suppressed hints
		IF _hint_currently_applies THEN
			_sanitized_query := replace(_query, ''clin.v_emr_journal'', ''staging.journal_without_suppressed_hints'');
			-- but only re-run if actually different
			IF _sanitized_query <> _query THEN
				BEGIN
					EXECUTE _sanitized_query INTO STRICT _hint_currently_applies;
				EXCEPTION
					--WHEN insufficient_privilege THEN RAISE WARNING ''sanitized auto hint query failed: %'', _sanitized_query;
					WHEN others THEN
						RAISE WARNING ''sanitized auto hint query failed: %'', _sanitized_query;
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
						_hint.hint := _sanitized_query;
						RETURN NEXT _hint;
						-- process next hint
						CONTINUE;
				END;
			END IF;
		END IF;

		IF _suppression_exists THEN
			-- is the hint definition still the same as at the time of suppression ?
			IF _md5_suppressed = _hint.md5_sum THEN
				-- yes, but does this hint currently apply ?
				IF _hint_currently_applies THEN
					-- suppressed, suppression valid, and hint applies: skip this hint
					CONTINUE;
				END IF;
				-- suppressed, suppression valid, hint does NOT apply:
				-- skip but invalidate suppression, because:
				-- * previously the hint applied and the user suppressed it,
				-- * then the patient changed such that the hint does not
				--    apply anymore (but the suppression is still valid),
				-- * when the patient changes again, the hint might apply again
				-- * HOWEVER - since the suppression would still be valid - the
				--   hint would magically get suppressed again (which is
				--   medically unsafe) ...
				-- after invalidation, the hint will no longer be suppressed,
				-- however - since it does not currently apply it - it will
				-- still not be returned until it applies again ...
				--
				-- -----------------------------------------------------------------------
				-- UNFORTUNATELY, the following is currently not _possible_ because
				-- we are running inside a READONLY transaction (due to inherent
				-- security risks when running arbitrary user queries [IOW the hint
				-- SQL] against the database) and we cannot execute a
				-- sub-transaction as READWRITE :-/
				--
				--UPDATE clin.suppressed_hint
				--SET md5_sum = ''invalidated''::text		-- will not ever match any md5 sum
				--WHERE
				--	fk_encounter IN (
				--		SELECT pk FROM clin.encounter WHERE fk_patient = _pk_identity
				--	)
				--		AND
				--	fk_hint = _hint.pk_auto_hint;
				-- -----------------------------------------------------------------------
				--
				-- hence our our workaround is to, indeed, return the hint but
				-- tag it with a magic rationale, by means of which the client
				-- can detect it to be in need of invalidation:
				_hint.title := ''HINT DOES NOT APPLY BUT NEEDS INVALIDATION OF EXISTING SUPPRESSION ['' || _hint.title || ''].'';
				_hint.rationale4suppression := ''magic_tag::please_invalidate_suppression'';
				RETURN NEXT _hint;
				CONTINUE;
			END IF;
			-- suppression exists but hint definition must have changed
			-- does the new hint apply ?
			IF _hint_currently_applies THEN
				-- yes: ignore the suppression but provide previous
				-- rationale for suppression to the user
				_hint.rationale4suppression := _rationale4suppression;
				-- retrieve recommendation
				SELECT clin._get_recommendation_for_patient_hint(_hint.recommendation_query, _pk_identity) INTO STRICT _hint_recommendation;
				_hint.recommendation := _hint_recommendation;
				RETURN NEXT _hint;
				CONTINUE;
			END IF;
			-- no, new hint does not apply, so ask for
			-- invalidation of suppression (see above)
			_hint.title := ''HINT DOES NOT APPLY BUT NEEDS INVALIDATION OF EXISTING SUPPRESSION ['' || _hint.title || ''].'';
			_hint.rationale4suppression := ''magic_tag::please_invalidate_suppression'';
			RETURN NEXT _hint;
			CONTINUE;
		END IF;

		-- hint is not suppressed
		-- does the hint currently apply ?
		IF _hint_currently_applies THEN
			-- yes: retrieve recommendation
			SELECT clin._get_recommendation_for_patient_hint(_hint.recommendation_query, _pk_identity) INTO STRICT _hint_recommendation;
			_hint.recommendation := _hint_recommendation;
			RETURN NEXT _hint;
		END IF;
		-- no: ignore it and process next hint in LOOP

	END LOOP;
	RETURN;
END;';

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-get_hints_for_patient-fixup.sql', '21.9');
