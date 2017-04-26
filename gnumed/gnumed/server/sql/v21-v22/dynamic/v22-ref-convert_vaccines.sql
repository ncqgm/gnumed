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
-- documentation
-- clin.vaccination links to ref.vaccine

-- ref.vaccine links to indications via ref.lnk_vaccine2inds
-- ref.vaccine links to drug_product

-- drug_product links to substance via dose via component

-- --------------------------------------------------------------
-- fix faulty old data

-- Tbc is live
update ref.vaccine set
	is_live = TRUE
where
	pk IN (
		select fk_vaccine from ref.lnk_vaccine2inds where fk_indication = (
			select id from ref.vacc_indication where description = 'tuberculosis'
		)
	)
;

-- measles is live
update ref.vaccine set
	is_live = TRUE
where
	pk IN (
		select fk_vaccine from ref.lnk_vaccine2inds where fk_indication = (
			select id from ref.vacc_indication where description = 'measles'
		)
	)
;

-- rubella is live
update ref.vaccine set
	is_live = TRUE
where
	pk IN (
		select fk_vaccine from ref.lnk_vaccine2inds where fk_indication = (
			select id from ref.vacc_indication where description = 'rubella'
		)
	)
;

-- --------------------------------------------------------------
-- drop assertion trigger which accesses old tables and
-- is better done in client code
drop function if exists clin.trf_warn_on_duplicate_vaccinations() cascade;

-- --------------------------------------------------------------
drop function if exists staging.v22_convert_vaccines() cascade;

create function staging.v22_convert_vaccines()
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_row_old_vacc_prod record;
	_pk_old_vacc_prod integer;
	_pk_old_vacc_indication integer;
	_pk_old_vaccine integer;
	_old_is_live boolean;

	_pk_new_vacc_prod integer;
	_pk_new_vaccine integer;
	_new_is_live boolean;
	_pk_new_vacc_dose integer;
	_new_vacc_doses integer[];

BEGIN

	-- loop over old-style generic vaccines
	FOR _row_old_vacc_prod IN
		SELECT * FROM ref.v_drug_products
		WHERE
			product ILIKE ''% - generic vaccine''
	LOOP
		_pk_old_vacc_prod := _row_old_vacc_prod.pk_drug_product;
		-- get list of linked indications
		RAISE NOTICE ''converting old-style generic vaccine [%]'', _row_old_vacc_prod;
		_new_vacc_doses := ARRAY[]::integer[];
		-- loop over indications of this vaccine
		FOR _pk_old_vacc_indication IN
			SELECT fk_indication FROM ref.lnk_vaccine2inds WHERE
				fk_vaccine = (
					SELECT pk FROM ref.vaccine WHERE fk_drug_product = _pk_old_vacc_prod
				)
		LOOP
			-- translate indication to substance dose
			RAISE NOTICE ''mapping old indication [%] to dose'', _pk_old_vacc_indication;
			SELECT fk_dose INTO STRICT _pk_new_vacc_dose
			FROM staging.lnk_vacc_ind2subst_dose
			WHERE
				fk_indication = _pk_old_vacc_indication
					AND
				is_live = (
					SELECT is_live FROM ref.vaccine
					WHERE fk_drug_product = _pk_old_vacc_prod
				)
			;
			RAISE NOTICE ''mapping to dose [%]'', _pk_new_vacc_dose;
			_new_vacc_doses := _new_vacc_doses ||_pk_new_vacc_dose;
		END LOOP;
		RAISE NOTICE ''found doses: %'', _new_vacc_doses;

		-- find new vaccine drug product with same list of substance doses
		SELECT fk_drug_product INTO STRICT _pk_new_vacc_prod FROM (
			SELECT fk_drug_product, doses, preparation, is_fake_product, product FROM (
				select fk_drug_product, array_agg(fk_dose) AS doses from ref.lnk_dose2drug group by fk_drug_product
			) as agged_products
				join ref.v_drug_products on (ref.v_drug_products.pk_drug_product = agged_products.fk_drug_product)
		)
			AS products_w_doses
		WHERE
			preparation = ''vaccine''
				AND
			is_fake_product IS TRUE
				AND
			product LIKE ''% vaccine%''
				AND
			-- better safe than sorry
			NOT product LIKE ''% - generic vaccine''
				AND
			doses = _new_vacc_doses
		;

		SELECT pk, is_live INTO STRICT _pk_old_vaccine, _old_is_live
		FROM ref.vaccine WHERE fk_drug_product = _pk_old_vacc_prod;

		SELECT pk, is_live INTO STRICT _pk_new_vaccine, _new_is_live
		FROM ref.vaccine WHERE fk_drug_product = _pk_new_vacc_prod;

		RAISE NOTICE ''updating clin.vaccination with fk_vaccine=% to point to fk_vaccine=%'', _pk_old_vaccine, _pk_new_vaccine;

		IF _old_is_live IS DISTINCT FROM _new_is_live THEN
			RAISE EXCEPTION ''<live> status of old and new vaccine are different'';
			RETURN FALSE;
		END IF;

		UPDATE clin.vaccination SET
			fk_vaccine = _pk_new_vaccine
		WHERE
			fk_vaccine = _pk_old_vaccine
		;

--		-- update ref.vaccine to point to the new fk_drug_product
--		RAISE NOTICE ''updating vaccine with fk_drug_product=% to point to fk_drug_product=%'', _pk_old_vacc_prod, _pk_new_vacc_prod;
--		UPDATE ref.vaccine SET
--			fk_drug_product = _pk_new_vacc_prod
--		WHERE
--			fk_drug_product = _pk_old_vacc_prod
--		;

		-- delete old vaccine product
		RAISE NOTICE ''deleting old-style generic vaccine product %'', _pk_old_vacc_prod;
		DELETE FROM ref.vaccine WHERE pk = _pk_old_vaccine;
		DELETE FROM ref.drug_product WHERE pk = _pk_old_vacc_prod;

	END LOOP;


	-- loop over real, user-entered or previously bootstrapped vaccines
	FOR _row_old_vacc_prod IN
		SELECT * FROM ref.v_drug_products r_vdp WHERE
			(
				(array_length(r_vdp.components, 1) = 0)
					OR
				(array_length(r_vdp.components, 1) IS NULL)
			) AND EXISTS (
				SELECT 1 FROM ref.vaccine r_v WHERE r_v.fk_drug_product = r_vdp.pk_drug_product
			)
	LOOP
		_pk_old_vacc_prod := _row_old_vacc_prod.pk_drug_product;
		-- get list of linked indications
		RAISE NOTICE ''converting old-style real vaccine [%]'', _row_old_vacc_prod;
		-- loop over indications of this vaccine
		FOR _pk_old_vacc_indication IN
			SELECT fk_indication FROM ref.lnk_vaccine2inds WHERE
				fk_vaccine = (
					SELECT pk FROM ref.vaccine WHERE fk_drug_product = _pk_old_vacc_prod
				)
		LOOP
			-- translate indication to substance dose
			RAISE NOTICE ''mapping old indication [%] to dose'', _pk_old_vacc_indication;
			SELECT fk_dose INTO STRICT _pk_new_vacc_dose
			FROM staging.lnk_vacc_ind2subst_dose
			WHERE
				fk_indication = _pk_old_vacc_indication
					AND
				is_live = coalesce (
					(	SELECT r_v.is_live FROM ref.vaccine r_v
						WHERE r_v.fk_drug_product = _pk_old_vacc_prod
					),
					staging.lnk_vacc_ind2subst_dose.is_live
				)
			-- prefer inactive over live vaccine mapping if
			-- a) original vaccine entry dose not specify and
			-- b) there are mapping entries for both active and
			--    inactive vaccines for this indication
			ORDER BY staging.lnk_vacc_ind2subst_dose.is_live ASC
			LIMIT 1;
			RAISE NOTICE ''mapping to dose [%]'', _pk_new_vacc_dose;
			-- link dose to old-style vaccine product as component
			INSERT INTO ref.lnk_dose2drug (fk_drug_product, fk_dose) (
				SELECT
					_pk_old_vacc_prod,
					_pk_new_vacc_dose
				-- better safe than sorry ...
				WHERE NOT EXISTS (
					SELECT 1 FROM ref.lnk_dose2drug WHERE
						fk_drug_product = _pk_old_vacc_prod
							AND
						fk_dose = _pk_new_vacc_dose
				)
			);
		END LOOP;
		-- drop all indication links for this vaccine
		DELETE FROM ref.lnk_vaccine2inds WHERE
			fk_vaccine = (
				SELECT pk FROM ref.vaccine WHERE fk_drug_product = _pk_old_vacc_prod
			)
		;
	END LOOP;

	RETURN TRUE;
END;';

-- --------------------------------------------------------------
-- actually convert
select staging.v22_convert_vaccines();

-- and clean up
drop function if exists staging.v22_convert_vaccines() cascade;
drop table if exists staging.lnk_vacc_ind2subst_dose cascade;
drop view if exists staging.v_lnk_vacc_ind2subst_dose cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-convert_vaccines.sql', '22.0');
