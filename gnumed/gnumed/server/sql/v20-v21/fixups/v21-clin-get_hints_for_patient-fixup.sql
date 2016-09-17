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
drop function if exists clin.hint_suppression_exists(IN _pk_identity integer, IN _pk_hint integer, OUT _o_exists BOOLEAN, OUT _o_md5 TEXT, OUT _o_rationale TEXT) cascade;

create function clin.hint_suppression_exists(IN _pk_identity integer, IN _pk_hint integer, OUT _o_exists BOOLEAN, OUT _o_md5 TEXT, OUT _o_rationale TEXT)
	returns RECORD
	language 'plpgsql'
	as '
--DECLARE
--	_md5_suppressed text;
--	_old_rationale4suppression text;
BEGIN
	SELECT
		md5_sum,
		rationale
			INTO
		_o_md5,
		_o_rationale
	FROM clin.suppressed_hint WHERE
		fk_hint = _pk_hint
			AND
		fk_encounter IN (
			SELECT pk FROM clin.encounter WHERE fk_patient = _pk_identity
		);
	IF FOUND THEN
		_o_exists := TRUE;
	ELSE
		_o_exists := FALSE;
	END IF;
END;';

-- --------------------------------------------------------------
drop function if exists clin.run_hint_query(IN _title text, IN _query text, OUT _o_applies boolean, OUT _o_title TEXT) cascade;

create function clin.run_hint_query(IN _title text, IN _query text, OUT _o_applies boolean, OUT _o_title TEXT)
	returns RECORD
	language 'plpgsql'
	as '
BEGIN
	BEGIN
		EXECUTE _query INTO STRICT _o_applies;
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
			_o_applies := NULL;
			_o_title := (''ERROR checking for ['' || _title || ''] !'')::TEXT;
			RETURN;
	END;
	_o_title := _title;
END;';

-- --------------------------------------------------------------
drop function if exists clin.get_hints_for_patient(integer) cascade;
drop function if exists clin.get_hints_for_patient(IN _pk_identity integer) cascade;

create function clin.get_hints_for_patient(IN _pk_identity integer)
	returns setof ref.v_auto_hints
	language 'plpgsql'
	as '
DECLARE
	_hint ref.v_auto_hints%rowtype;
	_query text;
	_suppression_exists boolean;		-- does not mean that the suppression applies
	_md5_at_suppression text;
	_old_rationale4suppression text;
	_hint_currently_applies boolean;	-- regardless of whether suppressed or not
	_hint_recommendation text;
	_title text;
--	_exc_state text;
--	_exc_msg text;
--	_exc_detail text;
--	_exc_hint text;
--	_exc_context text;
BEGIN
	-- loop over all defined hints
	FOR _hint IN SELECT * FROM ref.v_auto_hints WHERE is_active LOOP

		--raise NOTICE ''checking hint for patient %: %'', _pk_identity, _hint.title;

		-- is the hint suppressed ?
		SELECT (clin.hint_suppression_exists(_pk_identity, _hint.pk_auto_hint)).*
			INTO STRICT _suppression_exists, _md5_at_suppression, _old_rationale4suppression;

		-- does the hint currently apply ? (regardless of whether it is suppressed)
		_query := replace(_hint.query, ''ID_ACTIVE_PATIENT'', _pk_identity::text);
		_query := replace(_query, ''clin.v_emr_journal'', ''staging.journal_without_suppressed_hints'');
		SELECT (clin.run_hint_query(_hint.title, _query)).*
			INTO STRICT _hint_currently_applies, _title;

		-- error ?
		IF _hint_currently_applies IS NULL THEN
			--raise NOTICE '' error -> return'';
			_hint.title := _title;
			_hint.hint := _query;
			RETURN NEXT _hint;
			-- process next hint
			CONTINUE;
		END IF;

		-- hint does not apply
		IF _hint_currently_applies IS FALSE THEN
			-- does a (previously stored) suppression exist ?
			IF _suppression_exists IS FALSE THEN
				-- no, so skip this hint
				--raise NOTICE '' does not apply -> skip'';
				CONTINUE;
			END IF;
			--raise NOTICE '' does not apply but suppression invalid -> return for invalidation'';
			-- hint suppressed but does NOT apply:
			-- skip hint but invalidate suppression, because:
			-- * previously the hint must have applied and the user suppressed it,
			-- * then patient data (or hint definition) changed such that
			--   the hint does not apply anymore (but the suppression is
			--   still valid),
			-- * when patient data changes again, the hint might apply again
			-- * HOWEVER - since the suppression would still be valid - the
			--   hint would magically get suppressed again (which is
			--   medically unsafe) ...
			-- after invalidation, the hint will no longer be suppressed,
			-- however - since it does not currently apply - it will
			-- still not be returned and shown until it applies again ...
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
			_hint.rationale4suppression := ''magic_tag::does_not_apply::suppression_needs_invalidation'';
			RETURN NEXT _hint;
			CONTINUE;
		END IF;

		--raise NOTICE '' applies'';

		-- but is there a suppression ?
		IF _suppression_exists IS FALSE THEN
			--raise NOTICE '' return'';
			-- no: retrieve recommendation
			SELECT clin._get_recommendation_for_patient_hint(_hint.recommendation_query, _pk_identity) INTO STRICT _hint_recommendation;
			_hint.recommendation := _hint_recommendation;
			-- return hint
			RETURN NEXT _hint;
			CONTINUE;
		END IF;

		-- yes, is suppressed
		--raise NOTICE '' is suppressed'';

		-- is the suppression still valid ?
		-- -> yes, suppression valid
		IF _md5_at_suppression = _hint.md5_sum THEN
			--raise NOTICE ''-> suppression valid, ignoring hint'';
			-- hint applies, suppressed, suppression valid: skip this hint
			CONTINUE;
		END IF;

		-- -> no, suppression not valid
		-- hint definition must have changed so ignore the suppression but
		-- provide previous rationale for suppression to the user
		_hint.rationale4suppression := _old_rationale4suppression;
		-- retrieve recommendation
		SELECT clin._get_recommendation_for_patient_hint(_hint.recommendation_query, _pk_identity) INTO STRICT _hint_recommendation;
		_hint.recommendation := _hint_recommendation;
		RETURN NEXT _hint;
		CONTINUE;

	END LOOP;
	RETURN;
END;';

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-get_hints_for_patient-fixup.sql', '21.10');
