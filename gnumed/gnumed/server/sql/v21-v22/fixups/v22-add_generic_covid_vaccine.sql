-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- Add generic CoViD-2019 vaccine.
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- generic vaccine "substance" (= indications)
-- --------------------------------------------------------------
-- in case <sars-cov-2-mrna> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BX03' WHERE lower(description) = lower('SARS-CoV-2 spike protein mRNA') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'SARS-CoV-2 spike protein mRNA',
		'J07BX03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BX03'
				AND
			description = 'SARS-CoV-2 spike protein mRNA'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BX03-target', 'CoViD-2019');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BX03-target', 'CoViD-2019');

-- --------------------------------------------------------------
-- generic vaccine
-- --------------------------------------------------------------
-- need to disable trigger before running
ALTER TABLE ref.drug_product
	DISABLE TRIGGER tr_assert_product_has_components
;

-- --------------------------------------------------------------
-- in case <generic covid vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BX03' WHERE
	atc_code IS NULL
		AND
	description = 'generic covid vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic covid vaccine',
		'vaccine',
		TRUE,
		'J07BX03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic covid vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BX03'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BX03' AND description = 'SARS-CoV-2 spike protein mRNA' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BX03' AND description = 'SARS-CoV-2 spike protein mRNA' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
	);

-- link dose to product
INSERT INTO ref.lnk_dose2drug (fk_dose, fk_drug_product)
	SELECT
		(SELECT pk from ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BX03' AND description = 'SARS-CoV-2 spike protein mRNA' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic covid vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BX03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BX03' AND description = 'SARS-CoV-2 spike protein mRNA' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
			)
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic covid vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BX03'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic covid vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BX03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic covid vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BX03'
			)
	);

-- --------------------------------------------------------------
-- Comirnaty

-- in case <Comirnaty> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BX03' WHERE
	atc_code IS NULL
		AND
	description = 'Comirnaty'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS FALSE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'Comirnaty',
		'vaccine',
		FALSE,
		'J07BX03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'Comirnaty'
				AND
			preparation = 'vaccine'
				AND
			is_fake = FALSE
				AND
			atc_code = 'J07BX03'
	);

-- link dose to product
INSERT INTO ref.lnk_dose2drug (fk_dose, fk_drug_product)
	SELECT
		(SELECT pk from ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BX03' AND description = 'SARS-CoV-2 spike protein mRNA' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'Comirnaty'
				AND
			preparation = 'vaccine'
				AND
			is_fake = FALSE
				AND
			atc_code = 'J07BX03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BX03' AND description = 'SARS-CoV-2 spike protein mRNA' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
			)
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'Comirnaty'
						AND
					preparation = 'vaccine'
						AND
					is_fake = FALSE
						AND
					atc_code = 'J07BX03'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'Comirnaty'
				AND
			preparation = 'vaccine'
				AND
			is_fake = FALSE
				AND
			atc_code = 'J07BX03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'Comirnaty'
						AND
					preparation = 'vaccine'
						AND
					is_fake = FALSE
						AND
					atc_code = 'J07BX03'
			)
	);

-- --------------------------------------------------------------
-- mRNA-1273-Moderna

-- in case <mRNA-1273-Moderna> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BX03' WHERE
	atc_code IS NULL
		AND
	description = 'mRNA-1273-Moderna'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS FALSE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'mRNA-1273-Moderna',
		'vaccine',
		FALSE,
		'J07BX03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'mRNA-1273-Moderna'
				AND
			preparation = 'vaccine'
				AND
			is_fake = FALSE
				AND
			atc_code = 'J07BX03'
	);

-- link dose to product
INSERT INTO ref.lnk_dose2drug (fk_dose, fk_drug_product)
	SELECT
		(SELECT pk from ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BX03' AND description = 'SARS-CoV-2 spike protein mRNA' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'mRNA-1273-Moderna'
				AND
			preparation = 'vaccine'
				AND
			is_fake = FALSE
				AND
			atc_code = 'J07BX03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BX03' AND description = 'SARS-CoV-2 spike protein mRNA' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
			)
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'mRNA-1273-Moderna'
						AND
					preparation = 'vaccine'
						AND
					is_fake = FALSE
						AND
					atc_code = 'J07BX03'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'mRNA-1273-Moderna'
				AND
			preparation = 'vaccine'
				AND
			is_fake = FALSE
				AND
			atc_code = 'J07BX03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'mRNA-1273-Moderna'
						AND
					preparation = 'vaccine'
						AND
					is_fake = FALSE
						AND
					atc_code = 'J07BX03'
			)
	);

-- --------------------------------------------------------------
-- want to re-enable trigger as now all inserted
-- vaccines satisfy the conditions
ALTER TABLE ref.drug_product
	ENABLE TRIGGER tr_assert_product_has_components
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-add_generic_covid_vaccine.sql', '22.5');
