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

	-- convert vaccines from substance to indication links
	RAISE NOTICE ''converting in-use vaccines:'';
	FOR _vaccine_rec IN (SELECT * FROM ref.vaccine) LOOP
		RAISE NOTICE ''- vaccine [%] (product [%])'', _vaccine_rec.pk, _vaccine_rec.fk_drug_product;
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
		END LOOP;
		IF _vaccine_rec.brandname IS NOT NULL THEN
			CONTINUE;
		END IF;
		UPDATE ref.vaccine SET brandname = (SELECT description FROM ref.drug_product WHERE pk = _vaccine_rec.fk_drug_product AND is_fake IS FALSE);
	END LOOP;

	-- remove vaccine drug products, now stored in ref.vaccine.brandname
	-- remove substances/doses/components previously abused as indications
	RAISE NOTICE ''removing old substance-indications from ref.lnk_dose2drug'';
	-- remove from dose2drug link table links to ...
	DELETE FROM ref.lnk_dose2drug WHERE
		-- ... any doses ...
		fk_dose = ANY (
			-- ... which represent substances ...
			SELECT pk FROM ref.dose WHERE fk_substance = ANY (
				-- ... having an ATC that is listed as a vaccination indication ...
				SELECT pk FROM ref.substance WHERE atc = ANY(SELECT atc FROM ref.vacc_indication)
			)
		) AND
		-- ... and which are linked to a drug product ...
		fk_drug_product = ANY (
			-- being referenced as a vaccine
			SELECT fk_drug_product FROM ref.vaccine
		)
	;
	RAISE NOTICE ''removing old substance-indications from ref.dose'';
	-- remove any doses ...
	DELETE FROM ref.dose WHERE fk_substance = ANY (
		-- ... having an ATC that is listed as a vaccination indication ...
		SELECT pk FROM ref.substance WHERE atc = ANY(SELECT atc FROM ref.vacc_indication)
	);
	RAISE NOTICE ''removing old substance-indications from ref.substance'';
	-- remove any substances ...
	DELETE FROM ref.substance WHERE atc = ANY (
		-- ... having an ATC that is listed as a vaccination indication ...
		SELECT atc FROM ref.vacc_indication
	);
	RAISE NOTICE ''removing "vaccine" drug products from ref.drug_product'';
	-- need to break FK from vaccine to product first
	-- (the column gets dropped later on)
	UPDATE ref.vaccine set fk_drug_product = NULL;
	-- remove drug products listed as brands of vaccines
	-- (need to use brand name because fk_drug_product now NULL)
	DELETE FROM ref.drug_product WHERE description = ANY(SELECT brandname FROM ref.vaccine);
	-- remove dummy dose, not needed anymore
	RAISE NOTICE ''removing vaccine dummy dose from ref.dose'';
	DELETE FROM ref.dose WHERE fk_substance = (
		SELECT pk FROM ref.substance WHERE description = ''vaccine'' AND atc = ''J07''
	);
	-- remove dummy substance, not needed anymore
	RAISE NOTICE ''removing vaccine dummy substance from ref.substance'';
	DELETE FROM ref.substance WHERE description = ''vaccine'' AND atc = ''J07'';

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

alter table ref.vaccine
	alter column fk_drug_product
	drop not null;

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
-- .fk_drug_product
alter table ref.vaccine
	drop column if exists fk_drug_product cascade;

alter table audit.log_vaccine
	drop column if exists fk_drug_product cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-convert_vaccines.sql', '23.0');
