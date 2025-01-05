-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
-- data conversion
-- --------------------------------------------------------------
drop function if exists staging.v22_v23_convert_vaccines() cascade;

create function staging.v22_v23_convert_vaccines()
	returns void
	language plpgsql
	as '
DECLARE
	_vaccine_rec record;
	_ind_json json;
	_product_rec record;
	_pk_indication integer;
	_pk_dummy_subst integer;
	_pk_dummy_dose integer;
	_ind_rec record;
	_pk_generic_vaccine integer;
BEGIN
	-- remove unused vaccines, including generic ones
	RAISE NOTICE ''removing unused vaccines/vaccine brands'';
	FOR _vaccine_rec IN (SELECT * FROM ref.vaccine) LOOP
		-- vaccine in use ?
		PERFORM 1 FROM clin.vaccination WHERE fk_vaccine = _vaccine_rec.pk;
		IF FOUND THEN
			CONTINUE;
		END IF;
		RAISE NOTICE ''removing unused vaccine [pk=%] [fk_drug_product=%]'', _vaccine_rec.pk, _vaccine_rec.fk_drug_product;
		DELETE FROM ref.vaccine WHERE pk = _vaccine_rec.pk;
		RAISE NOTICE ''removing unused vaccine brand [fk_drug_product=%]'', _vaccine_rec.fk_drug_product;
		DELETE FROM ref.drug_product WHERE pk = _vaccine_rec.fk_drug_product;
	END LOOP;

	-- update ATCs as appopriate
	RAISE NOTICE ''updating unspecific Hep [J07BC0] to HepA [J07BC02]'';
	UPDATE ref.substance SET atc = ''J07BC02'' WHERE atc = ''J07BC0'';

	-- brands require a component, so:
	-- INSERT dummy substance
	INSERT INTO ref.substance (description, atc, intake_instructions)
		SELECT ''vaccine'', ''J07'', ''vaccination''
		WHERE NOT EXISTS (
			SELECT 1 FROM ref.substance WHERE description = ''vaccine'' AND atc = ''J07''
		);
	SELECT pk INTO _pk_dummy_subst FROM ref.substance WHERE description = ''vaccine'' AND atc = ''J07'';
	RAISE NOTICE ''dummy vaccine substance: [%]'', _pk_dummy_subst;
	-- insert dummy dose
	INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
		SELECT
			(SELECT pk FROM ref.substance WHERE description = ''vaccine'' AND atc = ''J07''),
			1, ''dose'', ''shot''
		WHERE NOT EXISTS (
			SELECT 1 FROM ref.dose WHERE fk_substance = (
				SELECT pk FROM ref.substance WHERE description = ''vaccine'' AND atc = ''J07''
			)
		);
	SELECT pk INTO _pk_dummy_dose FROM ref.dose WHERE fk_substance = _pk_dummy_subst;
	RAISE NOTICE ''dummy vaccine substance dose: [%]'', _pk_dummy_dose;

	-- convert vaccines from substance to indication links
	RAISE NOTICE ''converting in-use vaccines:'';
	FOR _vaccine_rec IN (SELECT * FROM ref.vaccine) LOOP
		RAISE NOTICE ''- vaccine [%] (brand [%])'', _vaccine_rec.pk, _vaccine_rec.fk_drug_product;
		FOR _product_rec IN (SELECT * from ref.v_drug_products WHERE pk_drug_product = _vaccine_rec.fk_drug_product) LOOP
			RAISE NOTICE ''- vaccine brand [%] [%]'', _product_rec.pk_drug_product, _product_rec.product;
			FOREACH _ind_json IN ARRAY _product_rec.components LOOP
				RAISE NOTICE ''-- indication [%]: [%]'', _ind_json->''atc_substance'', _ind_json->''substance'';
				-- does indication exist ?
				SELECT pk INTO _pk_indication FROM ref.vacc_indication WHERE atc = trim(BOTH FROM (_ind_json->''atc_substance'')::text, ''"'');
				IF NOT FOUND THEN
					RAISE EXCEPTION ''-- indication [%] not found in ref.vacc_indication'', _ind_json->''atc_substance'';

				END IF;
				-- link indication to vaccine
				RAISE NOTICE ''-- ATC of indication found in ref.vacc_indication under pk [%], linking'', _pk_indication;
				INSERT INTO ref.lnk_indic2vaccine (fk_indication, fk_vaccine) VALUES (_pk_indication, _vaccine_rec.pk);
			END LOOP;
			-- link product to dummy component
			RAISE NOTICE ''-- linking product [%] to dummy dose [%]'', _product_rec.pk_drug_product, _pk_dummy_dose;
			INSERT INTO ref.lnk_dose2drug (fk_dose, fk_drug_product)
				SELECT _pk_dummy_dose, _product_rec.pk_drug_product
				WHERE NOT EXISTS (
					SELECT 1 FROM ref.lnk_dose2drug
					WHERE fk_dose = _pk_dummy_dose AND fk_drug_product = _product_rec.pk_drug_product
				);
		END LOOP;
	END LOOP;

	-- remove from ref.substance any rows the ATC code of which
	-- now exists in ref.vacc_indication -- those had been used
	-- as indication entries but have been transferred by now
	RAISE NOTICE ''removing old substance-indications from ref.lnk_dose2drug'';
	DELETE FROM ref.lnk_dose2drug WHERE
		fk_dose = ANY (
			SELECT pk FROM ref.dose WHERE fk_substance = ANY (
				SELECT pk FROM ref.substance WHERE atc = ANY(SELECT atc FROM ref.vacc_indication)
			)
		) AND
		fk_drug_product = ANY (
			SELECT fk_drug_product FROM ref.vaccine
		)
	;
	RAISE NOTICE ''removing old substance-indications from ref.dose'';
	DELETE FROM ref.dose WHERE fk_substance = ANY (
		SELECT pk FROM ref.substance WHERE atc = ANY(SELECT atc FROM ref.vacc_indication)
	);
	RAISE NOTICE ''removing old substance-indications from ref.substance'';
	DELETE FROM ref.substance WHERE atc = ANY (
		SELECT atc FROM ref.vacc_indication
	);
	-- re-add generic vaccines
	RAISE NOTICE ''adding generic vaccine for each indication'';
	FOR _ind_rec IN (SELECT * FROM ref.vacc_indication) LOOP
		RAISE NOTICE '' [%] - [%]'', _ind_rec.atc, _ind_rec.target;
		INSERT INTO ref.vaccine (atc, comment, is_live)
			SELECT _ind_rec.atc, ''generic vaccine for '' || _ind_rec.target, False
			WHERE NOT EXISTS (
				SELECT 1 FROM ref.vaccine WHERE atc = _ind_rec.atc
			);
		SELECT pk INTO _pk_generic_vaccine FROM ref.vaccine WHERE atc = _ind_rec.atc;
		RAISE NOTICE '' linking indication to generic vaccine [%]'', _pk_generic_vaccine;
		INSERT INTO ref.lnk_indic2vaccine (fk_vaccine, fk_indication)
			SELECT _pk_generic_vaccine,	_ind_rec.pk
			WHERE NOT EXISTS (
				SELECT 1 FROM ref.lnk_indic2vaccine
				WHERE fk_vaccine = _pk_generic_vaccine AND fk_indication = _ind_rec.pk
			);
	END LOOP;
	RAISE NOTICE ''done'';
END;';

comment on function staging.v22_v23_convert_vaccines() is 'Temporary function to convert vaccines to have indications in ref.vacc_indication rather than as substances.';

select staging.v22_v23_convert_vaccines();

drop function if exists staging.v22_v23_convert_vaccines() cascade;

-- --------------------------------------------------------------
-- .id_route
alter table ref.vaccine
	drop column if exists id_route cascade;

drop index if exists ref.idx_c_vaccine_id_route cascade;

alter table audit.log_vaccine
	drop column if exists id_route cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-convert_vaccines.sql', '23.0');
