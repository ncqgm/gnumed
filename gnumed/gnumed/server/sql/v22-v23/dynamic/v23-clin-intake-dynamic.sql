-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
comment on table clin.intake is 'List of consumables a patient is/was taking.';

select audit.register_table_for_auditing('clin', 'intake');
select gm.register_notifying_table('clin', 'intake');

-- --------------------------------------------------------------
-- .clin_when
comment on column clin.intake.clin_when is
	'When was this intake started.';

-- --------------------------------------------------------------
-- .fk_encounter
comment on column clin.intake.fk_encounter is
	'The encounter under which this intake was documented.';

-- --------------------------------------------------------------
-- .fk_episode
comment on column clin.intake.fk_encounter is
	'The episode under which this intake was documented.';

-- --------------------------------------------------------------
-- .narrative
comment on column clin.intake.narrative is
	'Clinical notes on this intake';

-- --------------------------------------------------------------
-- .soap_cat

-- --------------------------------------------------------------
-- .use_type
comment on column clin.intake.use_type is
	'
<NULL>: medication, intended use,
0: not used or non-harmful use,
1: presently harmful use,
2: presently addicted,
3: previously addicted';

-- --------------------------------------------------------------
-- .fk_drug
comment on column clin.intake.fk_drug is
	'Drug product/entity being taken by patient.';

alter table clin.intake
	add foreign key (fk_drug)
		references ref.drug_product(pk)
		on delete restrict
		on update cascade;

alter table clin.intake
	alter column fk_drug
		set not null;

-- --------------------------------------------------------------
-- make (patient, fk_drug) unique
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

drop index if exists clin.idx_clin_subst_intake_uniq_drug_per_pat cascade;
create index idx_clin_subst_intake_uniq_drug_per_pat on clin.intake (fk_drug, clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode));

-- --------------------------------------------------------------
-- fill in from clin.substance_intake
drop function if exists staging._fill__intake__from__substance_intake() cascade;

create function staging._fill__intake__from__substance_intake()
	returns void
	language 'plpgsql'
	as '
DECLARE
	_intake clin.v_substance_intakes%rowtype;
	_narratives TEXT;
BEGIN
	-- loop over intakes:
	-- for multi-component drugs only one intake will be updated,
	-- the other ones are deleted later on
	FOR _intake IN SELECT DISTINCT ON (pk_patient, pk_drug_product) * FROM clin.v_substance_intakes LOOP
		SELECT
			NULLIF (
				string_agg(coalesce(notes, ''''), ''//'')
				|| ''||||''
				|| string_agg(coalesce(aim, ''''), ''//''),
				''||||''
			)
			into _narratives
			-- .fk_episode cannot be concatenated
		FROM clin.v_substance_intakes
		WHERE pk_drug_product = _intake.pk_drug_product;

		INSERT INTO clin.intake (
			fk_encounter,
			fk_episode,
			clin_when,
			narrative,
			use_type,
			fk_drug,
			_fk_s_i
		) VALUES (
			_intake.pk_encounter,
			_intake.pk_episode,
			coalesce(_intake.started, now()),
			_narratives,
			_intake.harmful_use_type,
			_intake.pk_drug_product,
			_intake.pk_substance_intake
		);
	END LOOP;
END;';

select staging._fill__intake__from__substance_intake();

drop function staging._fill__intake__from__substance_intake() cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-intake-dynamic.sql', '23.0');
