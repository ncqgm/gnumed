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
drop function if exists clin.map_enc_or_epi_to_patient(IN _enc integer, IN _epi INTEGER) cascade;

create function clin.map_enc_or_epi_to_patient(IN _enc_pk integer, IN _epi_pk INTEGER)
	returns INTEGER
	language 'plpgsql'
	immutable		-- not strictly true, but necessary for index use, sort of holds though because encounter/episode PKs are not supposed to be reused
	as '
DECLARE
	_identity_from_encounter INTEGER;
	_identity_from_episode INTEGER;
BEGIN
	-- check that at least one of encounter or episode is given
	-- do not ASSERT as that can be switched off via GUC
	IF _enc_pk IS NULL THEN
		if _epi_pk IS NULL THEN
			RAISE EXCEPTION
				''[clin.map_enc_or_epi_to_patient]: arguments encounter PK or episode PK must be distinct from <NULL>''
				USING ERRCODE = ''assert_failure''
			;
		END IF;
	END IF;

	IF _enc_pk IS NOT NULL THEN
		SELECT fk_patient INTO _identity_from_encounter FROM clin.encounter WHERE pk = _enc_pk;
		IF NOT FOUND THEN
			RAISE EXCEPTION
				''[clin.map_enc_or_epi_to_patient]: enc=% not found'',
					_enc_pk
				USING ERRCODE = ''assert_failure''
			;
		END IF;
		IF _epi_pk IS NULL THEN
			RETURN _identity_from_encounter;
		END IF;
	END IF;

	IF _epi_pk IS NOT NULL THEN
		SELECT fk_patient into _identity_from_episode FROM clin.encounter WHERE pk = (SELECT fk_encounter FROM clin.episode WHERE pk = _epi_pk);
		IF NOT FOUND THEN
			RAISE EXCEPTION
				''[clin.map_enc_or_epi_to_patient]: epi=% not found'',
					_epi_pk
				USING ERRCODE = ''assert_failure''
			;
		END IF;
		IF _enc_pk IS NULL THEN
			RETURN _identity_from_episode;
		END IF;
	END IF;

	IF _identity_from_encounter = _identity_from_episode THEN
		RETURN _identity_from_encounter;
	END IF;

	RAISE EXCEPTION
		''[clin.map_enc_or_epi_to_patient]: Sanity check failed. enc=% -> patient=%. epi=% -> patient=%.'',
			_enc_pk,
			_identity_from_encounter,
			_epi_pk,
			_identity_from_episode
		USING ERRCODE = ''assert_failure''
	;
	RETURN NULL;
END;';

comment on function clin.map_enc_or_epi_to_patient(IN _enc integer, IN _epi INTEGER) is
	'Get patient PK from either encounter PK or episode PK. If both are given equality is also tested for.';

-- testing:
--select clin.map_enc_or_epi_to_patient(NULL, 1);
--select clin.map_enc_or_epi_to_patient(1, 1);
--select clin.map_enc_or_epi_to_patient(1, NULL);
--select clin.map_enc_or_epi_to_patient(1, 1);
--select clin.map_enc_or_epi_to_patient(2, 1);
--select clin.map_enc_or_epi_to_patient(3, 1);
--select clin.map_enc_or_epi_to_patient(4, 1);
--selec 1;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-map_enc_or_epi_to_patient.sql', '23.0');
