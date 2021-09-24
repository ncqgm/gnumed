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
drop function if exists clin.trf_ins_intake_prevent_duplicate_component_links() cascade;
drop function if exists clin.trf_insert_intake_links_all_drug_components() cascade;

drop function if exists clin.trf_upd_intake_prevent_duplicate_component_links() cascade;
drop function if exists clin.trf_upd_intake_updates_all_drug_components() cascade;
drop function if exists clin.trf_upd_intake_must_link_all_drug_components() cascade;

drop function if exists clin.trf_del_intake_must_unlink_all_drug_components() cascade;
drop function if exists clin.trf_DEL_intake_document_deleted() cascade;

-- --------------------------------------------------------------
-- .fk_drug
comment on column clin.substance_intake.fk_drug is
	'Drug product being taken by patient.';

alter table clin.substance_intake
	add foreign key (fk_drug)
		references ref.drug_product(pk)
		on delete restrict
		on update cascade;

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
create index idx_clin_subst_intake_uniq_drug_per_pat on clin.substance_intake (fk_drug, clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode));

-- --------------------------------------------------------------
-- fill in .fk_drug from .fk_substance
drop function if exists staging._fill__fk_drug__from__fk_substance() cascade;

create function staging._fill__fk_drug__from__fk_substance()
	returns void
	language 'plpgsql'
	as '
DECLARE
	_intake clin.v_substance_intakes%rowtype;
	_narratives TEXT;
	_aims TEXT;
BEGIN
	-- loop over intakes:
	-- for multi-component drugs only one intake will be updated,
	-- the other ones are deleted later on
	FOR _intake IN SELECT DISTINCT ON (pk_drug_product) * FROM clin.v_substance_intakes LOOP
		SELECT
			NULLIF(string_agg(coalesce(notes, ''''), ''//''), ''''),
			NULLIF(string_agg(coalesce(aim, ''''), ''//''), '''')
			into _narratives, _aims
			-- .fk_episode cannot be concatenated
		FROM clin.v_substance_intakes
		WHERE pk_drug_product = _intake.pk_drug_product;

		UPDATE clin.substance_intake SET
			fk_drug = _intake.pk_drug_product,
			narrative = _narratives,
			aim = _aims
		WHERE
			pk = _intake.pk_substance_intake;
	END LOOP;
	-- remove rows for "other" substances of multi-component drugs
	DELETE FROM clin.substance_intake WHERE fk_drug IS NULL;
END;';

select staging._fill__fk_drug__from__fk_substance();

drop function staging._fill__fk_drug__from__fk_substance() cascade;

-- --------------------------------------------------------------
alter table clin.substance_intake
	alter column fk_drug
		set not null;

-- --------------------------------------------------------------
alter table clin.substance_intake
	drop column if exists fk_drug_component cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-substance_intake-dynamic_1.sql', '23.0');
