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
alter table ref.auto_hint
	drop constraint if exists ref_auto_hint_sane_rec_query;

alter table ref.auto_hint
	add constraint ref_auto_hint_sane_rec_query check (
		gm.is_null_or_non_empty_string(recommendation_query)
	);

-- --------------------------------------------------------------
drop view if exists ref.v_auto_hints cascade;

create view ref.v_auto_hints as
select
	pk
		as pk_auto_hint,
	query
		as query,
	recommendation_query
		as recommendation_query,
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
	-- it only exists in this view in order to enable the syntax
	-- "returns setof ref.v_auto_hints" in that function
	null::text
		as rationale4suppression,
	-- this column is set from clin.get_hints_for_patient(),
	-- it only exists in this view in order to enable the syntax
	-- "returns setof ref.v_auto_hints" in that function
	null::text
		as recommendation,
	md5(
		coalesce(query, '')
		|| coalesce(recommendation_query, '')
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


-- there is no need to update existing suppressions because initially
-- all ref.auto_hint.recommendation_query's will be NULL and thusly
-- add an empty string to the md5 summing input which does not change
-- the md5 sum ...

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

		-- does the hint currently apply ?
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
			_hint.rationale4suppression := ''please_invalidate_suppression'';
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
drop function if exists clin._get_recommendation_for_patient_hint(text,integer) cascade;

create function clin._get_recommendation_for_patient_hint(text,integer)
	returns text
	language 'plpgsql'
	as '
DECLARE
	_raw_query ALIAS FOR $1;
	_pk_identity ALIAS FOR $2;
	_query text;
	_recommendation text;
BEGIN
	IF _raw_query IS NULL THEN
		RETURN NULL::text;
	END IF;
	_query := replace(_raw_query, ''ID_ACTIVE_PATIENT'', _pk_identity::text);
	BEGIN
		EXECUTE _query INTO STRICT _recommendation;
	EXCEPTION
		--WHEN insufficient_privilege THEN RAISE WARNING ''auto hint recommendation query failed: %'', _query;
		WHEN others THEN
			RAISE WARNING ''auto hint recommendation query failed: %'', _query;
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
			_recommendation := ''ERROR running hint recommendation query ['' || _query || '']'';
	END;
	RETURN _recommendation;
END;';

-- --------------------------------------------------------------
DELETE FROM ref.auto_hint WHERE title = 'Lack of smoking status documentation';

INSERT INTO ref.auto_hint(query, title, hint, source, lang) VALUES (
	'SELECT NOT EXISTS(SELECT 1 FROM clin.v_nonbrand_intakes WHERE pk_patient = ID_ACTIVE_PATIENT AND atc_substance = ''N07BA01'' AND harmful_use_type IS NOT NULL)',
	'Lack of smoking status documentation',
	'There has never been any smoking status recorded for this patient.',
	'AWMF NVL Schädlicher Tabakgebrauch',
	'en'
);


DELETE FROM ref.auto_hint WHERE title = 'Outdated smoking status documentation';

INSERT INTO ref.auto_hint(title, hint, source, lang, query, recommendation_query) VALUES (
	'Outdated smoking status documentation',
	'Smoking status was last recorded more than one year ago for this smoker.',
	'AWMF NVL Schädlicher Tabakgebrauch',
	'en',
	'SELECT EXISTS (
		SELECT 1 FROM clin.v_nonbrand_intakes WHERE
			(pk_patient = ID_ACTIVE_PATIENT)
				AND
			(atc_substance = ''N07BA01'')
				AND
			(coalesce(harmful_use_type, -1) > 0)
				AND
			((discontinued IS NULL) OR (discontinued > now()))
				AND
			(last_checked_when < now() - ''1 year''::interval)
	);',
	'SELECT
		_(''Smoking status'') || E''\n''
		|| '' '' || _(''Last checked:'') || '' '' || to_char(last_checked_when, ''Mon YYYY'')
		|| (case
				when harmful_use_type = 1 then E''\n'' || _(''harmful use'')
				when harmful_use_type = 2 then E''\n'' || _(''addiction'')
				when harmful_use_type = 3 then E''\n'' || _(''previous addiction'')
			end)
		|| coalesce(E''\n '' || _(''Quit date:'') || '' '' || to_char(discontinued, ''YYYY Mon DD''), '''')
		|| coalesce(E''\n '' || _(''Notes:'') || '' '' || notes, '''')
	FROM
		clin.v_nonbrand_intakes
	WHERE pk_patient = ID_ACTIVE_PATIENT;'
);

-- --------------------------------------------------------------
DELETE FROM ref.auto_hint WHERE title = 'Kontraindikation: ACE/Sartan <-> Schwangerschaft';
DELETE FROM ref.auto_hint WHERE title = 'Contraindication: ACEI/Sartan <-> Pregnancy';

insert into ref.auto_hint(query, title, hint, url, source, lang, recommendation_query) values (
	'SELECT EXISTS (
	-- substance check
	SELECT 1 FROM clin.v_substance_intakes WHERE
		pk_patient = ID_ACTIVE_PATIENT
			AND
		-- on Sartan or ACEI
		(
			substance ~* ''.*sartan.*''
				OR
			substance ~* ''.*angiotensin.*''
				OR
			substance ~ ''.*ACE.*''
				OR
			-- might result in false positives (.Prilocarpin)
			substance ~* ''.+pril.*''
				OR
			atc_brand ~* ''^C09.*''
				OR
			atc_substance ~* ''^C09.*''
	)
) AND EXISTS (
	-- pregnancy check
	SELECT 1 FROM clin.patient WHERE
		fk_identity = ID_ACTIVE_PATIENT
			AND
		coalesce(edc BETWEEN now() - ''1 month''::interval AND now() + ''11 months''::interval, FALSE)
);',
	'Contraindication: ACEI/Sartan <-> Pregnancy',
	'ACEI and Sartans can cause severe fetopathies if used during 2nd and 3rd trimenon.',
	'http://www.akdae.de/Arzneimittelsicherheit/Bekanntgaben/Archiv/2010/201010151.pdf',
	'GNUmed default (AkdÄ 2012)',
	'en',
	'SELECT _(''EDC: '') || to_char(edc, ''YYYY Mon DD'') FROM clin.patient WHERE fk_identity = ID_ACTIVE_PATIENT;'
);

-- --------------------------------------------------------------
DELETE FROM ref.auto_hint WHERE title = 'Outdated or questionable EDC';

insert into ref.auto_hint(title, hint, source, lang, query, recommendation_query) values (
	'Outdated or questionable EDC',
	'The EDC documented for this patient is outdated or too far in the future.',
	'GNUmed default',
	'en',
	'SELECT EXISTS (
	SELECT 1 FROM clin.patient WHERE
		fk_identity = ID_ACTIVE_PATIENT
			AND
		coalesce((
			-- longer than 3 months ago
			edc < now() - ''3 months''::interval
				OR
			-- 2 years in the future
			edc > now() + ''2 years''::interval
		), FALSE)
);',
	'SELECT _(''EDC: '') || to_char(edc, ''YYYY Mon DD'') FROM clin.patient WHERE fk_identity = ID_ACTIVE_PATIENT;'
);

-- --------------------------------------------------------------
DELETE FROM ref.auto_hint WHERE title = 'Questionable EDC';

insert into ref.auto_hint(title, hint, source, lang, query, recommendation_query) values (
	'Questionable EDC',
	'There is an EDC documented for this MALE patient.',
	'GNUmed default',
	'en',
	'SELECT (
	SELECT d_i.gender = ''m'' FROM dem.identity d_i WHERE
		d_i.pk = ID_ACTIVE_PATIENT
) AND EXISTS (
	SELECT 1 FROM clin.patient WHERE
		fk_identity = ID_ACTIVE_PATIENT
			AND
		edc IS NOT NULL
);',
	'SELECT _(''EDC: '') || to_char(edc, ''YYYY Mon DD'') FROM clin.patient WHERE fk_identity = ID_ACTIVE_PATIENT;'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-ref-v_auto_hints.sql', '21.0');
