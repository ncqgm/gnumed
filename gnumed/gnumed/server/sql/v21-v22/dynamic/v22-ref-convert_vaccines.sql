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
drop function if exists staging.v22_convert_vaccines() cascade;

create function staging.v22_convert_vaccines()
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_old_vacc_prod_row record;
	_old_vacc_ind integer;
	_new_vacc_dose integer;
	_new_vacc_doses integer[];
	_new_vacc_prod integer;
BEGIN

	-- loop over old-style generic vaccines
	FOR _old_vacc_prod_row IN
		SELECT * FROM ref.v_drug_products
		WHERE
			product ILIKE ''% - generic vaccine''
	LOOP
		-- get list of linked indications
		RAISE NOTICE ''converting old-style generic vaccine [%]'', _old_vacc_prod_row;
		_new_vacc_doses := ARRAY[]::integer[];
		-- loop over indications of this vaccine
		FOR _old_vacc_ind IN
			SELECT fk_indication FROM ref.lnk_vaccine2inds WHERE
				fk_vaccine = (
					SELECT pk FROM ref.vaccine WHERE fk_drug_product = _old_vacc_prod_row.pk_drug_product
				)
		LOOP
			-- translate indication to substance dose
			SELECT fk_dose INTO STRICT _new_vacc_dose
			FROM staging.lnk_vacc_ind2subst_dose
			WHERE
				fk_indication = _old_vacc_ind
					AND
				is_live = (
					SELECT is_live FROM ref.vaccine
					WHERE fk_drug_product = _old_vacc_prod_row.pk_drug_product
				)
			;
			RAISE NOTICE ''mapping ind [%] to dose [%]'', _old_vacc_ind, _new_vacc_dose;
			_new_vacc_doses := _new_vacc_doses ||_new_vacc_dose;
		END LOOP;
		RAISE NOTICE ''found doses: %'', _new_vacc_doses;

		-- find new vaccine drug product with same list of substance doses
		SELECT fk_drug_product INTO STRICT _new_vacc_prod FROM (
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

		-- update ref.vaccine to point to the new fk_drug_product
		RAISE NOTICE ''updating vaccine with fk_drug_product=% to point to fk_drug_product=%'', _old_vacc_prod_row.pk_drug_product, _new_vacc_prod;
		UPDATE ref.vaccine SET
			fk_drug_product = _new_vacc_prod
		WHERE
			fk_drug_product = _old_vacc_prod_row.pk_drug_product
		;

		-- delete old vaccine product
		DELETE FROM ref.drug_product
		WHERE pk = _old_vacc_prod_row.pk_drug_product;

	END LOOP;


	-- loop over real, user-entered or previously bootstrapped vaccines
	FOR _old_vacc_prod_row IN
		SELECT * FROM ref.v_drug_products r_vdp WHERE
			(
				(array_length(r_vdp.components, 1) = 0)
					OR
				(array_length(r_vdp.components, 1) IS NULL)
			) AND EXISTS (
				SELECT 1 FROM ref.vaccine r_v WHERE r_v.fk_drug_product = r_vdp.pk_drug_product
			)
	LOOP
		-- get list of linked indications
		RAISE NOTICE ''converting old-style real vaccine [%]'', _old_vacc_prod_row;
		-- loop over indications of this vaccine
		FOR _old_vacc_ind IN
			SELECT fk_indication FROM ref.lnk_vaccine2inds WHERE
				fk_vaccine = (
					SELECT pk FROM ref.vaccine WHERE fk_drug_product = _old_vacc_prod_row.pk_drug_product
				)
		LOOP
			-- translate indication to substance dose
			SELECT fk_dose INTO STRICT _new_vacc_dose
			FROM staging.lnk_vacc_ind2subst_dose
			WHERE
				fk_indication = _old_vacc_ind
					AND
				is_live = (
					SELECT is_live FROM ref.vaccine
					WHERE fk_drug_product = _old_vacc_prod_row.pk_drug_product
				)
			;
			RAISE NOTICE ''mapping ind [%] to dose [%]'', _old_vacc_ind, _new_vacc_dose;
			-- link dose to old-style vaccine product as component
			INSERT INTO ref.lnk_dose2drug (fk_drug_product, fk_dose) (
				SELECT
					_old_vacc_prod_row.pk_drug_product,
					_new_vacc_dose
				-- better safe than sorry ...
				WHERE NOT EXISTS (
					SELECT 1 FROM ref.lnk_dose2drug WHERE
						fk_drug_product = _old_vacc_prod_row.pk_drug_product
							AND
						fk_dose = _new_vacc_dose
				)
			);
		END LOOP;
		-- drop all indication links for this vaccine
		DELETE FROM ref.lnk_vaccine2inds WHERE
			fk_vaccine = (
				SELECT pk FROM ref.vaccine WHERE fk_drug_product = _old_vacc_prod_row.pk_drug_product
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
