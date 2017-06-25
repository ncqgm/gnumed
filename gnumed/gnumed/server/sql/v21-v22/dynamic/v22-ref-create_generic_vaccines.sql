-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- THIS IS A GENERATED FILE. DO NOT EDIT.
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- indications mapping helper table
-- --------------------------------------------------------------
-- set up helper table for conversion of vaccines from using
-- linked indications to using linked substances,
-- to be dropped after converting vaccines
DROP TABLE IF EXISTS staging.lnk_vacc_ind2subst_dose CASCADE;

CREATE UNLOGGED TABLE staging.lnk_vacc_ind2subst_dose (
	fk_indication INTEGER
		NOT NULL
		REFERENCES ref.vacc_indication(id)
			ON UPDATE CASCADE
			ON DELETE RESTRICT,
	fk_dose INTEGER
		NOT NULL
		REFERENCES ref.dose(pk)
			ON UPDATE CASCADE
			ON DELETE RESTRICT,
	is_live
		BOOLEAN
		NOT NULL
		DEFAULT false,
	UNIQUE(fk_indication, fk_dose),
	UNIQUE(fk_indication, is_live)
);


DROP VIEW IF EXISTS staging.v_lnk_vacc_ind2subst_dose CASCADE;

CREATE VIEW staging.v_lnk_vacc_ind2subst_dose AS
SELECT
	s_lvi2sd.is_live
		as mapping_is_for_live_vaccines,
	r_vi.id
		as pk_indication,
	r_vi.description
		as indication,
	r_vi.atcs_single_indication,
	r_vi.atcs_combi_indication,
	r_d.pk
		as pk_dose,
	r_d.amount,
	r_d.unit,
	r_d.dose_unit,
	r_s.pk
		as pk_substance,
	r_s.description
		as substance,
	r_s.atc
		as atc_substance
FROM
	staging.lnk_vacc_ind2subst_dose s_lvi2sd
		inner join ref.vacc_indication r_vi on (r_vi.id = s_lvi2sd.fk_indication)
		inner join ref.dose r_d on (r_d.pk = s_lvi2sd.fk_dose)
			inner join ref.substance r_s on (r_s.pk = r_d.fk_substance)
;

-- --------------------------------------------------------------
-- generic vaccine "substances" (= indications)
-- --------------------------------------------------------------
-- in case <menY> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AH0Y' WHERE lower(description) = lower('meningococcus Y antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'meningococcus Y antigen',
		'J07AH0Y'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AH0Y'
				AND
			description = 'meningococcus Y antigen'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AH0Y-target', 'meningococcus Y');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AH0Y-target', 'meningococcus Y');

-- in case <yellow_fever-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BL01' WHERE lower(description) = lower('yellow fever virus, live') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'yellow fever virus, live',
		'J07BL01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BL01'
				AND
			description = 'yellow fever virus, live'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BL01-target', 'yellow fever');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BL01-target', 'yellow fever');

-- in case <menBmem> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AH06' WHERE lower(description) = lower('meningococcus B membrane') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'meningococcus B membrane',
		'J07AH06'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AH06'
				AND
			description = 'meningococcus B membrane'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AH06-target', 'meningococcus B');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AH06-target', 'meningococcus B');

-- in case <HiB> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AG01' WHERE lower(description) = lower('hemophilus influenzae B antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'hemophilus influenzae B antigen',
		'J07AG01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AG01'
				AND
			description = 'hemophilus influenzae B antigen'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AG01-target', 'HiB');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AG01-target', 'HiB');

-- in case <menA> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AH01' WHERE lower(description) = lower('meningococcus A antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'meningococcus A antigen',
		'J07AH01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AH01'
				AND
			description = 'meningococcus A antigen'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AH01-target', 'meningococcus A');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AH01-target', 'meningococcus A');

-- in case <tetanus> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AM01' WHERE lower(description) = lower('tetanus toxoid') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'tetanus toxoid',
		'J07AM01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AM01'
				AND
			description = 'tetanus toxoid'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AM01-target', 'tetanus');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AM01-target', 'tetanus');

-- in case <polio-inact> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BF0' WHERE lower(description) = lower('poliomyelitis, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'poliomyelitis, inactivated',
		'J07BF0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BF0'
				AND
			description = 'poliomyelitis, inactivated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BF0-target', 'poliomyelitis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BF0-target', 'poliomyelitis');

-- in case <fsme> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BA01' WHERE lower(description) = lower('flavivirus, tick-borne') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'flavivirus, tick-borne',
		'J07BA01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BA01'
				AND
			description = 'flavivirus, tick-borne'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BA01-target', 'tick-borne encephalitis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BA01-target', 'tick-borne encephalitis');

-- in case <qfever> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AXQF' WHERE lower(description) = lower('coxiella burnetii') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'coxiella burnetii',
		'J07AXQF'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AXQF'
				AND
			description = 'coxiella burnetii'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AXQF-target', 'Q fever');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AXQF-target', 'Q fever');

-- in case <mumps-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BE01' WHERE lower(description) = lower('mumps, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'mumps, live, attenuated',
		'J07BE01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BE01'
				AND
			description = 'mumps, live, attenuated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BE01-target', 'mumps');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BE01-target', 'mumps');

-- in case <salmo-typh+ent> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AP1' WHERE lower(description) = lower('salmonella typhi, enterica') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'salmonella typhi, enterica',
		'J07AP1'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AP1'
				AND
			description = 'salmonella typhi, enterica'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AP1-target', 'typhoid, paratyphus');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AP1-target', 'typhoid, paratyphus');

-- in case <polio-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BF0' WHERE lower(description) = lower('poliomyelitis, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'poliomyelitis, live, attenuated',
		'J07BF0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BF0'
				AND
			description = 'poliomyelitis, live, attenuated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BF0-target', 'poliomyelitis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BF0-target', 'poliomyelitis');

-- in case <pneumococcus> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AL0' WHERE lower(description) = lower('pneumococcus antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'pneumococcus antigen',
		'J07AL0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AL0'
				AND
			description = 'pneumococcus antigen'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AL0-target', 'pneumococcus');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AL0-target', 'pneumococcus');

-- in case <menW> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AH0W' WHERE lower(description) = lower('meningococcus W-135 antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'meningococcus W-135 antigen',
		'J07AH0W'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AH0W'
				AND
			description = 'meningococcus W-135 antigen'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AH0W-target', 'meningococcus W');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AH0W-target', 'meningococcus W');

-- in case <cholera> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AE0' WHERE lower(description) = lower('cholera, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'cholera, inactivated',
		'J07AE0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AE0'
				AND
			description = 'cholera, inactivated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AE0-target', 'cholera');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AE0-target', 'cholera');

-- in case <rubella-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BJ01' WHERE lower(description) = lower('rubella, live') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'rubella, live',
		'J07BJ01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BJ01'
				AND
			description = 'rubella, live'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BJ01-target', 'rubella');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BJ01-target', 'rubella');

-- in case <japEnc-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BA0J' WHERE lower(description) = lower('flavivirus, japanese, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'flavivirus, japanese, live, attenuated',
		'J07BA0J'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BA0J'
				AND
			description = 'flavivirus, japanese, live, attenuated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BA0J-target', 'japanese encephalitis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BA0J-target', 'japanese encephalitis');

-- in case <plague> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AK01' WHERE lower(description) = lower('yersinia pestis, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'yersinia pestis, inactivated',
		'J07AK01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AK01'
				AND
			description = 'yersinia pestis, inactivated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AK01-target', 'plague');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AK01-target', 'plague');

-- in case <salmo-inact> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AP0' WHERE lower(description) = lower('salmonella typhi, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'salmonella typhi, inactivated',
		'J07AP0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AP0'
				AND
			description = 'salmonella typhi, inactivated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AP0-target', 'typhoid');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AP0-target', 'typhoid');

-- in case <japEnc> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BA0J' WHERE lower(description) = lower('flavivirus, japanese') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'flavivirus, japanese',
		'J07BA0J'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BA0J'
				AND
			description = 'flavivirus, japanese'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BA0J-target', 'japanese encephalitis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BA0J-target', 'japanese encephalitis');

-- in case <tbc-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AN01' WHERE lower(description) = lower('tuberculosis, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'tuberculosis, live, attenuated',
		'J07AN01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AN01'
				AND
			description = 'tuberculosis, live, attenuated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AN01-target', 'tbc');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AN01-target', 'tbc');

-- in case <rota-live-atten> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BH0' WHERE lower(description) = lower('rotavirus, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'rotavirus, live, attenuated',
		'J07BH0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BH0'
				AND
			description = 'rotavirus, live, attenuated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BH0-target', 'rotavirus diarrhea');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BH0-target', 'rotavirus diarrhea');

-- in case <pap6-11-16-18-31-33-45-52-58> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BM03' WHERE lower(description) = lower('papillomavirus 6,11,16,18,31,33,45,52,58') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'papillomavirus 6,11,16,18,31,33,45,52,58',
		'J07BM03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BM03'
				AND
			description = 'papillomavirus 6,11,16,18,31,33,45,52,58'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BM03-target', 'HPV');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BM03-target', 'HPV');

-- in case <hepB> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BC01' WHERE lower(description) = lower('hepatitis B antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'hepatitis B antigen',
		'J07BC01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BC01'
				AND
			description = 'hepatitis B antigen'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BC01-target', 'hepatitis B');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BC01-target', 'hepatitis B');

-- in case <pertussis> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AJ0' WHERE lower(description) = lower('pertussis') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'pertussis',
		'J07AJ0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AJ0'
				AND
			description = 'pertussis'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AJ0-target', 'pertussis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AJ0-target', 'pertussis');

-- in case <hepA-inact> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BC0' WHERE lower(description) = lower('hepatitis A, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'hepatitis A, inactivated',
		'J07BC0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BC0'
				AND
			description = 'hepatitis A, inactivated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BC0-target', 'hepatitis A');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BC0-target', 'hepatitis A');

-- in case <brucellosis> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AD01' WHERE lower(description) = lower('brucella antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'brucella antigen',
		'J07AD01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AD01'
				AND
			description = 'brucella antigen'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AD01-target', 'brucellosis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AD01-target', 'brucellosis');

-- in case <salmo-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AP0' WHERE lower(description) = lower('salmonella typhi, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'salmonella typhi, live, attenuated',
		'J07AP0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AP0'
				AND
			description = 'salmonella typhi, live, attenuated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AP0-target', 'typhoid');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AP0-target', 'typhoid');

-- in case <anthrax> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AC01' WHERE lower(description) = lower('bacillus anthracis antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'bacillus anthracis antigen',
		'J07AC01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AC01'
				AND
			description = 'bacillus anthracis antigen'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AC01-target', 'anthrax');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AC01-target', 'anthrax');

-- in case <smallpox> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BX01' WHERE lower(description) = lower('variola virus, live') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'variola virus, live',
		'J07BX01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BX01'
				AND
			description = 'variola virus, live'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BX01-target', 'variola (smallpox)');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BX01-target', 'variola (smallpox)');

-- in case <influ-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BB0' WHERE lower(description) = lower('influenza, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'influenza, live, attenuated',
		'J07BB0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BB0'
				AND
			description = 'influenza, live, attenuated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BB0-target', 'influenza');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BB0-target', 'influenza');

-- in case <influ-inact> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BB0' WHERE lower(description) = lower('influenza, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'influenza, inactivated',
		'J07BB0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BB0'
				AND
			description = 'influenza, inactivated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BB0-target', 'influenza');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BB0-target', 'influenza');

-- in case <menC> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AH07' WHERE lower(description) = lower('meningococcus C antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'meningococcus C antigen',
		'J07AH07'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AH07'
				AND
			description = 'meningococcus C antigen'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AH07-target', 'meningococcus C');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AH07-target', 'meningococcus C');

-- in case <pap-generic> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BM0' WHERE lower(description) = lower('papillomavirus') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'papillomavirus',
		'J07BM0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BM0'
				AND
			description = 'papillomavirus'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BM0-target', 'HPV');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BM0-target', 'HPV');

-- in case <pap6-11-16-18> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BM01' WHERE lower(description) = lower('papillomavirus 6,11,16,18') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'papillomavirus 6,11,16,18',
		'J07BM01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BM01'
				AND
			description = 'papillomavirus 6,11,16,18'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BM01-target', 'HPV');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BM01-target', 'HPV');

-- in case <shingles-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BK0' WHERE lower(description) = lower('herpes virus (shingles), live') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'herpes virus (shingles), live',
		'J07BK0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BK0'
				AND
			description = 'herpes virus (shingles), live'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BK0-target', 'zoster (shingles)');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BK0-target', 'zoster (shingles)');

-- in case <rabies> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BG01' WHERE lower(description) = lower('rabies, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'rabies, inactivated',
		'J07BG01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BG01'
				AND
			description = 'rabies, inactivated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BG01-target', 'rabies');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BG01-target', 'rabies');

-- in case <typh-exanth> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AR01' WHERE lower(description) = lower('rickettsia prowazekii, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'rickettsia prowazekii, inactivated',
		'J07AR01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AR01'
				AND
			description = 'rickettsia prowazekii, inactivated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AR01-target', 'typhus exanthematicus');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AR01-target', 'typhus exanthematicus');

-- in case <cholera-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AE0' WHERE lower(description) = lower('cholera, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'cholera, live, attenuated',
		'J07AE0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AE0'
				AND
			description = 'cholera, live, attenuated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AE0-target', 'cholera');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AE0-target', 'cholera');

-- in case <pap16-18> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BM02' WHERE lower(description) = lower('papillomavirus 16,18') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'papillomavirus 16,18',
		'J07BM02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BM02'
				AND
			description = 'papillomavirus 16,18'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BM02-target', 'HPV');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BM02-target', 'HPV');

-- in case <chickenpox-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BK0' WHERE lower(description) = lower('herpes virus (chickenpox), live') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'herpes virus (chickenpox), live',
		'J07BK0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BK0'
				AND
			description = 'herpes virus (chickenpox), live'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BK0-target', 'varicella (chickenpox)');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BK0-target', 'varicella (chickenpox)');

-- in case <diphtheria> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AF01' WHERE lower(description) = lower('diphtheria toxoid') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'diphtheria toxoid',
		'J07AF01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07AF01'
				AND
			description = 'diphtheria toxoid'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AF01-target', 'diphtheria');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AF01-target', 'diphtheria');

-- in case <measles-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BD01' WHERE lower(description) = lower('measles, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'measles, live, attenuated',
		'J07BD01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE
			atc = 'J07BD01'
				AND
			description = 'measles, live, attenuated'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BD01-target', 'measles');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BD01-target', 'measles');

-- --------------------------------------------------------------
-- generic vaccines
-- --------------------------------------------------------------
-- new-style vaccines are not linked to indications, so drop
-- trigger asserting that condition,
DROP FUNCTION IF EXISTS clin.trf_sanity_check_vaccine_has_indications() CASCADE;


-- need to disable trigger before running
ALTER TABLE ref.drug_product
	DISABLE TRIGGER tr_assert_product_has_components
;

-- --------------------------------------------------------------
-- in case <generic influenza vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BB01' WHERE
	atc_code IS NULL
		AND
	description = 'generic influenza vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic influenza vaccine',
		'vaccine',
		TRUE,
		'J07BB01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic influenza vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BB01'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BB0' AND description = 'influenza, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BB0' AND description = 'influenza, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BB0' AND description = 'influenza, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic influenza vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BB01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BB0' AND description = 'influenza, inactivated' LIMIT 1)
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
					description = 'generic influenza vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BB01'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic influenza vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BB01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic influenza vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BB01'
			)
	);

-- --------------------------------------------------------------
-- in case <generic measles-mumps vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BD51' WHERE
	atc_code IS NULL
		AND
	description = 'generic measles-mumps vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic measles-mumps vaccine, live',
		'vaccine',
		TRUE,
		'J07BD51'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic measles-mumps vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD51'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic measles-mumps vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD51'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
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
					description = 'generic measles-mumps vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD51'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic measles-mumps vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD51'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
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
					description = 'generic measles-mumps vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD51'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic measles-mumps vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD51'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic measles-mumps vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD51'
			)
	);

-- --------------------------------------------------------------
-- in case <generic tetanus vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AM' WHERE
	atc_code IS NULL
		AND
	description = 'generic tetanus vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic tetanus vaccine',
		'vaccine',
		TRUE,
		'J07AM'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic tetanus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AM'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic tetanus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AM'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
					description = 'generic tetanus vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AM'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic tetanus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AM'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic tetanus vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AM'
			)
	);

-- --------------------------------------------------------------
-- in case <generic TdaPPol-HepB vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA12' WHERE
	atc_code IS NULL
		AND
	description = 'generic TdaPPol-HepB vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic TdaPPol-HepB vaccine',
		'vaccine',
		TRUE,
		'J07CA12'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA12'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA12'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
					description = 'generic TdaPPol-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA12'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA12'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
					description = 'generic TdaPPol-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA12'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA12'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
					description = 'generic TdaPPol-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA12'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA12'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
					description = 'generic TdaPPol-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA12'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA12'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
					description = 'generic TdaPPol-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA12'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA12'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic TdaPPol-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA12'
			)
	);

-- --------------------------------------------------------------
-- in case <generic TdaP-Hib-HepB vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA11' WHERE
	atc_code IS NULL
		AND
	description = 'generic TdaP-Hib-HepB vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic TdaP-Hib-HepB vaccine',
		'vaccine',
		TRUE,
		'J07CA11'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic TdaP-Hib-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA11'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP-Hib-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA11'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
					description = 'generic TdaP-Hib-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA11'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP-Hib-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA11'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
					description = 'generic TdaP-Hib-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA11'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP-Hib-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA11'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
					description = 'generic TdaP-Hib-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA11'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP-Hib-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA11'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
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
					description = 'generic TdaP-Hib-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA11'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP-Hib-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA11'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
					description = 'generic TdaP-Hib-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA11'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP-Hib-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA11'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic TdaP-Hib-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA11'
			)
	);

-- --------------------------------------------------------------
-- in case <generic HiB vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AG' WHERE
	atc_code IS NULL
		AND
	description = 'generic HiB vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic HiB vaccine',
		'vaccine',
		TRUE,
		'J07AG'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic HiB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AG'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic HiB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AG'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
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
					description = 'generic HiB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AG'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic HiB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AG'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic HiB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AG'
			)
	);

-- --------------------------------------------------------------
-- in case <generic influenza vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BB03' WHERE
	atc_code IS NULL
		AND
	description = 'generic influenza vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic influenza vaccine, live',
		'vaccine',
		TRUE,
		'J07BB03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic influenza vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BB03'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BB0' AND description = 'influenza, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BB0' AND description = 'influenza, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BB0' AND description = 'influenza, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic influenza vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BB03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BB0' AND description = 'influenza, live, attenuated' LIMIT 1)
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
					description = 'generic influenza vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BB03'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic influenza vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BB03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic influenza vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BB03'
			)
	);

-- --------------------------------------------------------------
-- in case <generic MMR vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BD52' WHERE
	atc_code IS NULL
		AND
	description = 'generic MMR vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic MMR vaccine, live',
		'vaccine',
		TRUE,
		'J07BD52'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic MMR vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD52'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic MMR vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD52'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
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
					description = 'generic MMR vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD52'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic MMR vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD52'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
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
					description = 'generic MMR vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD52'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic MMR vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD52'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
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
					description = 'generic MMR vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD52'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic MMR vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD52'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic MMR vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD52'
			)
	);

-- --------------------------------------------------------------
-- in case <generic yellow fever vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BL' WHERE
	atc_code IS NULL
		AND
	description = 'generic yellow fever vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic yellow fever vaccine',
		'vaccine',
		TRUE,
		'J07BL'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic yellow fever vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BL'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BL01' AND description = 'yellow fever virus, live' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BL01' AND description = 'yellow fever virus, live' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BL01' AND description = 'yellow fever virus, live' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic yellow fever vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BL'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BL01' AND description = 'yellow fever virus, live' LIMIT 1)
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
					description = 'generic yellow fever vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BL'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic yellow fever vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BL'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic yellow fever vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BL'
			)
	);

-- --------------------------------------------------------------
-- in case <generic tick-borne encephalitis vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BA' WHERE
	atc_code IS NULL
		AND
	description = 'generic tick-borne encephalitis vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic tick-borne encephalitis vaccine',
		'vaccine',
		TRUE,
		'J07BA'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic tick-borne encephalitis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BA'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BA01' AND description = 'flavivirus, tick-borne' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA01' AND description = 'flavivirus, tick-borne' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA01' AND description = 'flavivirus, tick-borne' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic tick-borne encephalitis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BA'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA01' AND description = 'flavivirus, tick-borne' LIMIT 1)
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
					description = 'generic tick-borne encephalitis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BA'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic tick-borne encephalitis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BA'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic tick-borne encephalitis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BA'
			)
	);

-- --------------------------------------------------------------
-- in case <generic typhus exanthematicus vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AR' WHERE
	atc_code IS NULL
		AND
	description = 'generic typhus exanthematicus vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic typhus exanthematicus vaccine',
		'vaccine',
		TRUE,
		'J07AR'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic typhus exanthematicus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AR'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AR01' AND description = 'rickettsia prowazekii, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AR01' AND description = 'rickettsia prowazekii, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AR01' AND description = 'rickettsia prowazekii, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic typhus exanthematicus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AR'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AR01' AND description = 'rickettsia prowazekii, inactivated' LIMIT 1)
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
					description = 'generic typhus exanthematicus vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AR'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic typhus exanthematicus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AR'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic typhus exanthematicus vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AR'
			)
	);

-- --------------------------------------------------------------
-- in case <generic varicella vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BK01' WHERE
	atc_code IS NULL
		AND
	description = 'generic varicella vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic varicella vaccine, live',
		'vaccine',
		TRUE,
		'J07BK01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic varicella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BK01'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BK0' AND description = 'herpes virus (chickenpox), live' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK0' AND description = 'herpes virus (chickenpox), live' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK0' AND description = 'herpes virus (chickenpox), live' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic varicella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BK01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK0' AND description = 'herpes virus (chickenpox), live' LIMIT 1)
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
					description = 'generic varicella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BK01'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic varicella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BK01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic varicella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BK01'
			)
	);

-- --------------------------------------------------------------
-- in case <generic variola vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BX01' WHERE
	atc_code IS NULL
		AND
	description = 'generic variola vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic variola vaccine, live',
		'vaccine',
		TRUE,
		'J07BX01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic variola vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BX01'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BX01' AND description = 'variola virus, live' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BX01' AND description = 'variola virus, live' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BX01' AND description = 'variola virus, live' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic variola vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BX01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BX01' AND description = 'variola virus, live' LIMIT 1)
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
					description = 'generic variola vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BX01'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic variola vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BX01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic variola vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BX01'
			)
	);

-- --------------------------------------------------------------
-- in case <generic mumps-rubella vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BJ51' WHERE
	atc_code IS NULL
		AND
	description = 'generic mumps-rubella vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic mumps-rubella vaccine, live',
		'vaccine',
		TRUE,
		'J07BJ51'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic mumps-rubella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BJ51'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic mumps-rubella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BJ51'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
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
					description = 'generic mumps-rubella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BJ51'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic mumps-rubella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BJ51'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
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
					description = 'generic mumps-rubella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BJ51'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic mumps-rubella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BJ51'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic mumps-rubella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BJ51'
			)
	);

-- --------------------------------------------------------------
-- in case <generic poliomyelitis vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BF01' WHERE
	atc_code IS NULL
		AND
	description = 'generic poliomyelitis vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic poliomyelitis vaccine, live',
		'vaccine',
		TRUE,
		'J07BF01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic poliomyelitis vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BF01'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic poliomyelitis vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BF01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, live, attenuated' LIMIT 1)
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
					description = 'generic poliomyelitis vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BF01'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic poliomyelitis vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BF01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic poliomyelitis vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BF01'
			)
	);

-- --------------------------------------------------------------
-- in case <generic typhoid-hepA vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA10' WHERE
	atc_code IS NULL
		AND
	description = 'generic typhoid-hepA vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic typhoid-hepA vaccine',
		'vaccine',
		TRUE,
		'J07CA10'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic typhoid-hepA vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA10'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic typhoid-hepA vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA10'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, inactivated' LIMIT 1)
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
					description = 'generic typhoid-hepA vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA10'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC0' AND description = 'hepatitis A, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC0' AND description = 'hepatitis A, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC0' AND description = 'hepatitis A, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic typhoid-hepA vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA10'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC0' AND description = 'hepatitis A, inactivated' LIMIT 1)
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
					description = 'generic typhoid-hepA vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA10'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic typhoid-hepA vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA10'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic typhoid-hepA vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA10'
			)
	);

-- --------------------------------------------------------------
-- in case <generic mumps vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BE' WHERE
	atc_code IS NULL
		AND
	description = 'generic mumps vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic mumps vaccine, live',
		'vaccine',
		TRUE,
		'J07BE'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic mumps vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BE'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic mumps vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BE'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
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
					description = 'generic mumps vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BE'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic mumps vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BE'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic mumps vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BE'
			)
	);

-- --------------------------------------------------------------
-- in case <generic Tbc vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AN' WHERE
	atc_code IS NULL
		AND
	description = 'generic Tbc vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic Tbc vaccine',
		'vaccine',
		TRUE,
		'J07AN'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic Tbc vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AN'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AN01' AND description = 'tuberculosis, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AN01' AND description = 'tuberculosis, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AN01' AND description = 'tuberculosis, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Tbc vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AN'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AN01' AND description = 'tuberculosis, live, attenuated' LIMIT 1)
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
					description = 'generic Tbc vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AN'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Tbc vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AN'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic Tbc vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AN'
			)
	);

-- --------------------------------------------------------------
-- in case <generic meningococcus A vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AH01' WHERE
	atc_code IS NULL
		AND
	description = 'generic meningococcus A vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic meningococcus A vaccine',
		'vaccine',
		TRUE,
		'J07AH01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic meningococcus A vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH01'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus A vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1)
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
					description = 'generic meningococcus A vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH01'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus A vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic meningococcus A vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH01'
			)
	);

-- --------------------------------------------------------------
-- in case <generic meningococcus B vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AH06' WHERE
	atc_code IS NULL
		AND
	description = 'generic meningococcus B vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic meningococcus B vaccine',
		'vaccine',
		TRUE,
		'J07AH06'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic meningococcus B vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH06'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH06' AND description = 'meningococcus B membrane' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH06' AND description = 'meningococcus B membrane' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH06' AND description = 'meningococcus B membrane' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus B vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH06'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH06' AND description = 'meningococcus B membrane' LIMIT 1)
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
					description = 'generic meningococcus B vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH06'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus B vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH06'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic meningococcus B vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH06'
			)
	);

-- --------------------------------------------------------------
-- in case <generic cholera vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AE01' WHERE
	atc_code IS NULL
		AND
	description = 'generic cholera vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic cholera vaccine',
		'vaccine',
		TRUE,
		'J07AE01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic cholera vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE01'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AE0' AND description = 'cholera, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE0' AND description = 'cholera, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE0' AND description = 'cholera, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic cholera vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE0' AND description = 'cholera, inactivated' LIMIT 1)
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
					description = 'generic cholera vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AE01'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic cholera vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic cholera vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AE01'
			)
	);

-- --------------------------------------------------------------
-- in case <generic DTPol vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA01' WHERE
	atc_code IS NULL
		AND
	description = 'generic DTPol vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic DTPol vaccine',
		'vaccine',
		TRUE,
		'J07CA01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic DTPol vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA01'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic DTPol vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
					description = 'generic DTPol vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA01'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic DTPol vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
					description = 'generic DTPol vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA01'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic DTPol vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
					description = 'generic DTPol vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA01'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic DTPol vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic DTPol vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA01'
			)
	);

-- --------------------------------------------------------------
-- in case <generic plague vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AK' WHERE
	atc_code IS NULL
		AND
	description = 'generic plague vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic plague vaccine',
		'vaccine',
		TRUE,
		'J07AK'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic plague vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AK'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AK01' AND description = 'yersinia pestis, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AK01' AND description = 'yersinia pestis, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AK01' AND description = 'yersinia pestis, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic plague vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AK'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AK01' AND description = 'yersinia pestis, inactivated' LIMIT 1)
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
					description = 'generic plague vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AK'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic plague vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AK'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic plague vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AK'
			)
	);

-- --------------------------------------------------------------
-- in case <generic TdaPPol vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA02' WHERE
	atc_code IS NULL
		AND
	description = 'generic TdaPPol vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic TdaPPol vaccine',
		'vaccine',
		TRUE,
		'J07CA02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic TdaPPol vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA02'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
					description = 'generic TdaPPol vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA02'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
					description = 'generic TdaPPol vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA02'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
					description = 'generic TdaPPol vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA02'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
					description = 'generic TdaPPol vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA02'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic TdaPPol vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA02'
			)
	);

-- --------------------------------------------------------------
-- in case <generic rotavirus vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BH01' WHERE
	atc_code IS NULL
		AND
	description = 'generic rotavirus vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic rotavirus vaccine, live',
		'vaccine',
		TRUE,
		'J07BH01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic rotavirus vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BH01'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BH0' AND description = 'rotavirus, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BH0' AND description = 'rotavirus, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BH0' AND description = 'rotavirus, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic rotavirus vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BH01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BH0' AND description = 'rotavirus, live, attenuated' LIMIT 1)
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
					description = 'generic rotavirus vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BH01'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic rotavirus vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BH01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic rotavirus vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BH01'
			)
	);

-- --------------------------------------------------------------
-- in case <generic pneumococcus vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AL0' WHERE
	atc_code IS NULL
		AND
	description = 'generic pneumococcus vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic pneumococcus vaccine',
		'vaccine',
		TRUE,
		'J07AL0'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic pneumococcus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AL0'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AL0' AND description = 'pneumococcus antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AL0' AND description = 'pneumococcus antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AL0' AND description = 'pneumococcus antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic pneumococcus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AL0'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AL0' AND description = 'pneumococcus antigen' LIMIT 1)
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
					description = 'generic pneumococcus vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AL0'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic pneumococcus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AL0'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic pneumococcus vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AL0'
			)
	);

-- --------------------------------------------------------------
-- in case <generic typhoid vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AP01' WHERE
	atc_code IS NULL
		AND
	description = 'generic typhoid vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic typhoid vaccine, live',
		'vaccine',
		TRUE,
		'J07AP01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic typhoid vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP01'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic typhoid vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, live, attenuated' LIMIT 1)
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
					description = 'generic typhoid vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AP01'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic typhoid vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic typhoid vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AP01'
			)
	);

-- --------------------------------------------------------------
-- in case <generic TdaP vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA' WHERE
	atc_code IS NULL
		AND
	description = 'generic TdaP vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic TdaP vaccine',
		'vaccine',
		TRUE,
		'J07CA'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic TdaP vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
					description = 'generic TdaP vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
					description = 'generic TdaP vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
					description = 'generic TdaP vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic TdaP vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA'
			)
	);

-- --------------------------------------------------------------
-- in case <generic zoster vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BK02' WHERE
	atc_code IS NULL
		AND
	description = 'generic zoster vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic zoster vaccine, live',
		'vaccine',
		TRUE,
		'J07BK02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic zoster vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BK02'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BK0' AND description = 'herpes virus (shingles), live' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK0' AND description = 'herpes virus (shingles), live' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK0' AND description = 'herpes virus (shingles), live' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic zoster vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BK02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK0' AND description = 'herpes virus (shingles), live' LIMIT 1)
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
					description = 'generic zoster vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BK02'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic zoster vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BK02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic zoster vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BK02'
			)
	);

-- --------------------------------------------------------------
-- in case <generic MMRV vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BD54' WHERE
	atc_code IS NULL
		AND
	description = 'generic MMRV vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic MMRV vaccine, live',
		'vaccine',
		TRUE,
		'J07BD54'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic MMRV vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD54'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic MMRV vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD54'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
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
					description = 'generic MMRV vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD54'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic MMRV vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD54'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' AND description = 'mumps, live, attenuated' LIMIT 1)
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
					description = 'generic MMRV vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD54'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic MMRV vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD54'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
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
					description = 'generic MMRV vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD54'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BK0' AND description = 'herpes virus (chickenpox), live' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK0' AND description = 'herpes virus (chickenpox), live' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK0' AND description = 'herpes virus (chickenpox), live' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic MMRV vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD54'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK0' AND description = 'herpes virus (chickenpox), live' LIMIT 1)
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
					description = 'generic MMRV vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD54'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic MMRV vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD54'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic MMRV vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD54'
			)
	);

-- --------------------------------------------------------------
-- in case <generic pertussis vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AJ01' WHERE
	atc_code IS NULL
		AND
	description = 'generic pertussis vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic pertussis vaccine',
		'vaccine',
		TRUE,
		'J07AJ01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic pertussis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AJ01'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic pertussis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AJ01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
					description = 'generic pertussis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AJ01'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic pertussis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AJ01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic pertussis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AJ01'
			)
	);

-- --------------------------------------------------------------
-- in case <generic brucellosis vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AD' WHERE
	atc_code IS NULL
		AND
	description = 'generic brucellosis vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic brucellosis vaccine',
		'vaccine',
		TRUE,
		'J07AD'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic brucellosis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AD'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AD01' AND description = 'brucella antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AD01' AND description = 'brucella antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AD01' AND description = 'brucella antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic brucellosis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AD'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AD01' AND description = 'brucella antigen' LIMIT 1)
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
					description = 'generic brucellosis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AD'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic brucellosis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AD'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic brucellosis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AD'
			)
	);

-- --------------------------------------------------------------
-- in case <generic cholera vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AE02' WHERE
	atc_code IS NULL
		AND
	description = 'generic cholera vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic cholera vaccine, live',
		'vaccine',
		TRUE,
		'J07AE02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic cholera vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE02'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AE0' AND description = 'cholera, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE0' AND description = 'cholera, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE0' AND description = 'cholera, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic cholera vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE0' AND description = 'cholera, live, attenuated' LIMIT 1)
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
					description = 'generic cholera vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AE02'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic cholera vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic cholera vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AE02'
			)
	);

-- --------------------------------------------------------------
-- in case <generic TdaP-HepB vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA05' WHERE
	atc_code IS NULL
		AND
	description = 'generic TdaP-HepB vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic TdaP-HepB vaccine',
		'vaccine',
		TRUE,
		'J07CA05'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic TdaP-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA05'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA05'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
					description = 'generic TdaP-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA05'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA05'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
					description = 'generic TdaP-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA05'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA05'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
					description = 'generic TdaP-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA05'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA05'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
					description = 'generic TdaP-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA05'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaP-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA05'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic TdaP-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA05'
			)
	);

-- --------------------------------------------------------------
-- in case <generic Td-HepB vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA07' WHERE
	atc_code IS NULL
		AND
	description = 'generic Td-HepB vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic Td-HepB vaccine',
		'vaccine',
		TRUE,
		'J07CA07'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic Td-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA07'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Td-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA07'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
					description = 'generic Td-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA07'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Td-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA07'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
					description = 'generic Td-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA07'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Td-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA07'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
					description = 'generic Td-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA07'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Td-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA07'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic Td-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA07'
			)
	);

-- --------------------------------------------------------------
-- in case <generic TdaPPol-HiB-HepB-MenAC vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA13' WHERE
	atc_code IS NULL
		AND
	description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic TdaPPol-HiB-HepB-MenAC vaccine',
		'vaccine',
		TRUE,
		'J07CA13'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA13'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA13'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA13'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA13'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA13'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA13'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA13'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA13'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA13'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA13'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA13'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA13'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA13'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA13'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA13'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA13'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA13'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA13'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic TdaPPol-HiB-HepB-MenAC vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA13'
			)
	);

-- --------------------------------------------------------------
-- in case <generic anthrax vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AC' WHERE
	atc_code IS NULL
		AND
	description = 'generic anthrax vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic anthrax vaccine',
		'vaccine',
		TRUE,
		'J07AC'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic anthrax vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AC'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AC01' AND description = 'bacillus anthracis antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AC01' AND description = 'bacillus anthracis antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AC01' AND description = 'bacillus anthracis antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic anthrax vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AC'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AC01' AND description = 'bacillus anthracis antigen' LIMIT 1)
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
					description = 'generic anthrax vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AC'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic anthrax vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AC'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic anthrax vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AC'
			)
	);

-- --------------------------------------------------------------
-- in case <generic poliomyelitis vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BF03' WHERE
	atc_code IS NULL
		AND
	description = 'generic poliomyelitis vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic poliomyelitis vaccine',
		'vaccine',
		TRUE,
		'J07BF03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic poliomyelitis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BF03'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic poliomyelitis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BF03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
					description = 'generic poliomyelitis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BF03'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic poliomyelitis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BF03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic poliomyelitis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BF03'
			)
	);

-- --------------------------------------------------------------
-- in case <generic measles-rubella vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BD53' WHERE
	atc_code IS NULL
		AND
	description = 'generic measles-rubella vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic measles-rubella vaccine, live',
		'vaccine',
		TRUE,
		'J07BD53'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic measles-rubella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD53'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic measles-rubella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD53'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
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
					description = 'generic measles-rubella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD53'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic measles-rubella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD53'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
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
					description = 'generic measles-rubella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD53'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic measles-rubella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD53'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic measles-rubella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD53'
			)
	);

-- --------------------------------------------------------------
-- in case <generic Q fever vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AXQF' WHERE
	atc_code IS NULL
		AND
	description = 'generic Q fever vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic Q fever vaccine',
		'vaccine',
		TRUE,
		'J07AXQF'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic Q fever vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AXQF'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AXQF' AND description = 'coxiella burnetii' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AXQF' AND description = 'coxiella burnetii' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AXQF' AND description = 'coxiella burnetii' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Q fever vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AXQF'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AXQF' AND description = 'coxiella burnetii' LIMIT 1)
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
					description = 'generic Q fever vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AXQF'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Q fever vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AXQF'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic Q fever vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AXQF'
			)
	);

-- --------------------------------------------------------------
-- in case <generic typhoid/paratyphus vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AP10' WHERE
	atc_code IS NULL
		AND
	description = 'generic typhoid/paratyphus vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic typhoid/paratyphus vaccine',
		'vaccine',
		TRUE,
		'J07AP10'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic typhoid/paratyphus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP10'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AP1' AND description = 'salmonella typhi, enterica' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP1' AND description = 'salmonella typhi, enterica' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP1' AND description = 'salmonella typhi, enterica' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic typhoid/paratyphus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP10'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP1' AND description = 'salmonella typhi, enterica' LIMIT 1)
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
					description = 'generic typhoid/paratyphus vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AP10'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic typhoid/paratyphus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP10'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic typhoid/paratyphus vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AP10'
			)
	);

-- --------------------------------------------------------------
-- in case <generic meningococcus ACYW135 vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AH04' WHERE
	atc_code IS NULL
		AND
	description = 'generic meningococcus ACYW135 vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic meningococcus ACYW135 vaccine',
		'vaccine',
		TRUE,
		'J07AH04'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic meningococcus ACYW135 vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH04'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus ACYW135 vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH04'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1)
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
					description = 'generic meningococcus ACYW135 vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH04'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus ACYW135 vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH04'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1)
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
					description = 'generic meningococcus ACYW135 vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH04'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH0Y' AND description = 'meningococcus Y antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH0Y' AND description = 'meningococcus Y antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH0Y' AND description = 'meningococcus Y antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus ACYW135 vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH04'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH0Y' AND description = 'meningococcus Y antigen' LIMIT 1)
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
					description = 'generic meningococcus ACYW135 vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH04'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH0W' AND description = 'meningococcus W-135 antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH0W' AND description = 'meningococcus W-135 antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH0W' AND description = 'meningococcus W-135 antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus ACYW135 vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH04'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH0W' AND description = 'meningococcus W-135 antigen' LIMIT 1)
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
					description = 'generic meningococcus ACYW135 vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH04'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus ACYW135 vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH04'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic meningococcus ACYW135 vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH04'
			)
	);

-- --------------------------------------------------------------
-- in case <generic hepatitis A vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BC02' WHERE
	atc_code IS NULL
		AND
	description = 'generic hepatitis A vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic hepatitis A vaccine',
		'vaccine',
		TRUE,
		'J07BC02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic hepatitis A vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BC02'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC0' AND description = 'hepatitis A, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC0' AND description = 'hepatitis A, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC0' AND description = 'hepatitis A, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic hepatitis A vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BC02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC0' AND description = 'hepatitis A, inactivated' LIMIT 1)
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
					description = 'generic hepatitis A vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BC02'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic hepatitis A vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BC02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic hepatitis A vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BC02'
			)
	);

-- --------------------------------------------------------------
-- in case <generic hepatitis B vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BC01' WHERE
	atc_code IS NULL
		AND
	description = 'generic hepatitis B vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic hepatitis B vaccine',
		'vaccine',
		TRUE,
		'J07BC01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic hepatitis B vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BC01'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic hepatitis B vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BC01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
					description = 'generic hepatitis B vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BC01'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic hepatitis B vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BC01'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic hepatitis B vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BC01'
			)
	);

-- --------------------------------------------------------------
-- in case <generic meningococcus C vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AH' WHERE
	atc_code IS NULL
		AND
	description = 'generic meningococcus C vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic meningococcus C vaccine',
		'vaccine',
		TRUE,
		'J07AH'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic meningococcus C vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus C vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1)
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
					description = 'generic meningococcus C vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus C vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic meningococcus C vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH'
			)
	);

-- --------------------------------------------------------------
-- in case <generic rubella vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BJ' WHERE
	atc_code IS NULL
		AND
	description = 'generic rubella vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic rubella vaccine, live',
		'vaccine',
		TRUE,
		'J07BJ'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic rubella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BJ'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic rubella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BJ'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
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
					description = 'generic rubella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BJ'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic rubella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BJ'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic rubella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BJ'
			)
	);

-- --------------------------------------------------------------
-- in case <generic rabies vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BG' WHERE
	atc_code IS NULL
		AND
	description = 'generic rabies vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic rabies vaccine',
		'vaccine',
		TRUE,
		'J07BG'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic rabies vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BG'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BG01' AND description = 'rabies, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BG01' AND description = 'rabies, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BG01' AND description = 'rabies, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic rabies vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BG'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BG01' AND description = 'rabies, inactivated' LIMIT 1)
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
					description = 'generic rabies vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BG'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic rabies vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BG'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic rabies vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BG'
			)
	);

-- --------------------------------------------------------------
-- in case <generic typhoid vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AP02' WHERE
	atc_code IS NULL
		AND
	description = 'generic typhoid vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic typhoid vaccine',
		'vaccine',
		TRUE,
		'J07AP02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic typhoid vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP02'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic typhoid vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, inactivated' LIMIT 1)
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
					description = 'generic typhoid vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AP02'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic typhoid vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic typhoid vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AP02'
			)
	);

-- --------------------------------------------------------------
-- in case <generic HPV vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BM' WHERE
	atc_code IS NULL
		AND
	description = 'generic HPV vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic HPV vaccine',
		'vaccine',
		TRUE,
		'J07BM'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic HPV vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BM'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BM0' AND description = 'papillomavirus' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BM0' AND description = 'papillomavirus' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BM0' AND description = 'papillomavirus' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic HPV vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BM'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BM0' AND description = 'papillomavirus' LIMIT 1)
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
					description = 'generic HPV vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BM'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic HPV vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BM'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic HPV vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BM'
			)
	);

-- --------------------------------------------------------------
-- in case <generic Td-rubella vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA03' WHERE
	atc_code IS NULL
		AND
	description = 'generic Td-rubella vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic Td-rubella vaccine',
		'vaccine',
		TRUE,
		'J07CA03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic Td-rubella vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA03'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Td-rubella vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
					description = 'generic Td-rubella vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA03'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Td-rubella vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
					description = 'generic Td-rubella vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA03'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Td-rubella vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' AND description = 'rubella, live' LIMIT 1)
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
					description = 'generic Td-rubella vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA03'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Td-rubella vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic Td-rubella vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA03'
			)
	);

-- --------------------------------------------------------------
-- in case <generic Td vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AM51' WHERE
	atc_code IS NULL
		AND
	description = 'generic Td vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic Td vaccine',
		'vaccine',
		TRUE,
		'J07AM51'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic Td vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AM51'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Td vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AM51'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
					description = 'generic Td vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AM51'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Td vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AM51'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
					description = 'generic Td vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AM51'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic Td vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AM51'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic Td vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AM51'
			)
	);

-- --------------------------------------------------------------
-- in case <generic cholera-typhoid vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AE51' WHERE
	atc_code IS NULL
		AND
	description = 'generic cholera-typhoid vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic cholera-typhoid vaccine',
		'vaccine',
		TRUE,
		'J07AE51'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic cholera-typhoid vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE51'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AE0' AND description = 'cholera, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE0' AND description = 'cholera, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE0' AND description = 'cholera, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic cholera-typhoid vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE51'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE0' AND description = 'cholera, inactivated' LIMIT 1)
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
					description = 'generic cholera-typhoid vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AE51'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic cholera-typhoid vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE51'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP0' AND description = 'salmonella typhi, inactivated' LIMIT 1)
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
					description = 'generic cholera-typhoid vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AE51'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic cholera-typhoid vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE51'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic cholera-typhoid vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AE51'
			)
	);

-- --------------------------------------------------------------
-- in case <generic TdaPPol-HiB-HepB vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA09' WHERE
	atc_code IS NULL
		AND
	description = 'generic TdaPPol-HiB-HepB vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic TdaPPol-HiB-HepB vaccine',
		'vaccine',
		TRUE,
		'J07CA09'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA09'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA09'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA09'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA09'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA09'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA09'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA09'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA09'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA09'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA09'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA09'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA09'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' AND description = 'hepatitis B antigen' LIMIT 1)
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
					description = 'generic TdaPPol-HiB-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA09'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic TdaPPol-HiB-HepB vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA09'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic TdaPPol-HiB-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA09'
			)
	);

-- --------------------------------------------------------------
-- in case <generic japanese encephalitis vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BA03' WHERE
	atc_code IS NULL
		AND
	description = 'generic japanese encephalitis vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic japanese encephalitis vaccine, live',
		'vaccine',
		TRUE,
		'J07BA03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic japanese encephalitis vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BA03'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BA0J' AND description = 'flavivirus, japanese, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA0J' AND description = 'flavivirus, japanese, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA0J' AND description = 'flavivirus, japanese, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic japanese encephalitis vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BA03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA0J' AND description = 'flavivirus, japanese, live, attenuated' LIMIT 1)
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
					description = 'generic japanese encephalitis vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BA03'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic japanese encephalitis vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BA03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic japanese encephalitis vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BA03'
			)
	);

-- --------------------------------------------------------------
-- in case <generic DTaPPol-Hib vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA06' WHERE
	atc_code IS NULL
		AND
	description = 'generic DTaPPol-Hib vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic DTaPPol-Hib vaccine',
		'vaccine',
		TRUE,
		'J07CA06'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic DTaPPol-Hib vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA06'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic DTaPPol-Hib vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA06'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' AND description = 'tetanus toxoid' LIMIT 1)
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
					description = 'generic DTaPPol-Hib vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA06'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic DTaPPol-Hib vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA06'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
					description = 'generic DTaPPol-Hib vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA06'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic DTaPPol-Hib vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA06'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' AND description = 'pertussis' LIMIT 1)
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
					description = 'generic DTaPPol-Hib vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA06'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic DTaPPol-Hib vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA06'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF0' AND description = 'poliomyelitis, inactivated' LIMIT 1)
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
					description = 'generic DTaPPol-Hib vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA06'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic DTaPPol-Hib vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA06'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' AND description = 'hemophilus influenzae B antigen' LIMIT 1)
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
					description = 'generic DTaPPol-Hib vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA06'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic DTaPPol-Hib vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07CA06'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic DTaPPol-Hib vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA06'
			)
	);

-- --------------------------------------------------------------
-- in case <generic diphtheria vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AF' WHERE
	atc_code IS NULL
		AND
	description = 'generic diphtheria vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic diphtheria vaccine',
		'vaccine',
		TRUE,
		'J07AF'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic diphtheria vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AF'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic diphtheria vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AF'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' AND description = 'diphtheria toxoid' LIMIT 1)
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
					description = 'generic diphtheria vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AF'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic diphtheria vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AF'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic diphtheria vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AF'
			)
	);

-- --------------------------------------------------------------
-- in case <generic measles vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BD' WHERE
	atc_code IS NULL
		AND
	description = 'generic measles vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic measles vaccine, live',
		'vaccine',
		TRUE,
		'J07BD'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic measles vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic measles vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' AND description = 'measles, live, attenuated' LIMIT 1)
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
					description = 'generic measles vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic measles vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BD'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic measles vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD'
			)
	);

-- --------------------------------------------------------------
-- in case <generic meningococcus AC vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AH03' WHERE
	atc_code IS NULL
		AND
	description = 'generic meningococcus AC vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic meningococcus AC vaccine',
		'vaccine',
		TRUE,
		'J07AH03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic meningococcus AC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH03'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus AC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' AND description = 'meningococcus A antigen' LIMIT 1)
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
					description = 'generic meningococcus AC vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH03'
			)
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus AC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' AND description = 'meningococcus C antigen' LIMIT 1)
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
					description = 'generic meningococcus AC vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH03'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic meningococcus AC vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AH03'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic meningococcus AC vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH03'
			)
	);

-- --------------------------------------------------------------
-- in case <generic japanese encephalitis vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BA02' WHERE
	atc_code IS NULL
		AND
	description = 'generic japanese encephalitis vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'generic japanese encephalitis vaccine',
		'vaccine',
		TRUE,
		'J07BA02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'generic japanese encephalitis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BA02'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BA0J' AND description = 'flavivirus, japanese' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA0J' AND description = 'flavivirus, japanese' LIMIT 1)
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
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA0J' AND description = 'flavivirus, japanese' LIMIT 1)
				AND
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic japanese encephalitis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BA02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA0J' AND description = 'flavivirus, japanese' LIMIT 1)
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
					description = 'generic japanese encephalitis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BA02'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'generic japanese encephalitis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BA02'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'generic japanese encephalitis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BA02'
			)
	);

-- want to re-enable trigger as now all inserted
-- vaccines satisfy the conditions
ALTER TABLE ref.drug_product
	ENABLE TRIGGER tr_assert_product_has_components
;

-- --------------------------------------------------------------
-- indications mapping data
-- --------------------------------------------------------------
-- map old style
--		(clin|ref).vacc_indication.description
-- to new style
--		ref.v_substance_doses.substance

-- old-style "meningococcus Y" => "meningococcus Y antigen"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'meningococcus Y'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'meningococcus Y antigen'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'meningococcus Y'
	);

-- old-style "yellow fever" => "yellow fever virus, live"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'yellow fever'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'yellow fever virus, live'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'yellow fever'
	);

-- old-style "haemophilus influenzae b" => "hemophilus influenzae B antigen"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'haemophilus influenzae b'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'hemophilus influenzae B antigen'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'haemophilus influenzae b'
	);

-- old-style "meningococcus A" => "meningococcus A antigen"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'meningococcus A'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'meningococcus A antigen'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'meningococcus A'
	);

-- old-style "tetanus" => "tetanus toxoid"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'tetanus'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'tetanus toxoid'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'tetanus'
	);

-- old-style "poliomyelitis" => "poliomyelitis, inactivated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'poliomyelitis'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'poliomyelitis, inactivated'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'poliomyelitis'
	);

-- old-style "tick-borne meningoencephalitis" => "flavivirus, tick-borne"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'tick-borne meningoencephalitis'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'flavivirus, tick-borne'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'tick-borne meningoencephalitis'
	);

-- old-style "coxiella burnetii (Q fever)" => "coxiella burnetii"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'coxiella burnetii (Q fever)'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'coxiella burnetii'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'coxiella burnetii (Q fever)'
	);

-- old-style "mumps" => "mumps, live, attenuated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'mumps'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'mumps, live, attenuated'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'mumps'
	);

-- old-style "salmonella typhi (typhoid)" => "salmonella typhi, enterica"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'salmonella typhi (typhoid)'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'salmonella typhi, enterica'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'salmonella typhi (typhoid)'
	);

-- old-style "poliomyelitis" => "poliomyelitis, live, attenuated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'poliomyelitis'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'poliomyelitis, live, attenuated'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'poliomyelitis'
	);

-- old-style "pneumococcus" => "pneumococcus antigen"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'pneumococcus'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'pneumococcus antigen'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'pneumococcus'
	);

-- old-style "meningococcus W" => "meningococcus W-135 antigen"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'meningococcus W'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'meningococcus W-135 antigen'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'meningococcus W'
	);

-- old-style "cholera" => "cholera, inactivated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'cholera'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'cholera, inactivated'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'cholera'
	);

-- old-style "rubella" => "rubella, live"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'rubella'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'rubella, live'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'rubella'
	);

-- old-style "japanese B encephalitis" => "flavivirus, japanese, live, attenuated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'japanese B encephalitis'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'flavivirus, japanese, live, attenuated'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'japanese B encephalitis'
	);

-- old-style "yersinia pestis" => "yersinia pestis, inactivated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'yersinia pestis'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'yersinia pestis, inactivated'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'yersinia pestis'
	);

-- old-style "japanese B encephalitis" => "flavivirus, japanese"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'japanese B encephalitis'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'flavivirus, japanese'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'japanese B encephalitis'
	);

-- old-style "tuberculosis" => "tuberculosis, live, attenuated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'tuberculosis'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'tuberculosis, live, attenuated'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'tuberculosis'
	);

-- old-style "hepatitis B" => "hepatitis B antigen"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'hepatitis B'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'hepatitis B antigen'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'hepatitis B'
	);

-- old-style "pertussis" => "pertussis"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'pertussis'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'pertussis'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'pertussis'
	);

-- old-style "hepatitis A" => "hepatitis A, inactivated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'hepatitis A'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'hepatitis A, inactivated'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'hepatitis A'
	);

-- old-style "salmonella typhi (typhoid)" => "salmonella typhi, live, attenuated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'salmonella typhi (typhoid)'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'salmonella typhi, live, attenuated'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'salmonella typhi (typhoid)'
	);

-- old-style "bacillus anthracis (Anthrax)" => "bacillus anthracis antigen"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'bacillus anthracis (Anthrax)'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'bacillus anthracis antigen'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'bacillus anthracis (Anthrax)'
	);

-- old-style "variola virus (smallpox)" => "variola virus, live"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'variola virus (smallpox)'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'variola virus, live'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'variola virus (smallpox)'
	);

-- old-style "influenza (seasonal)" => "influenza, live, attenuated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'influenza (seasonal)'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'influenza, live, attenuated'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'influenza (seasonal)'
	);

-- old-style "influenza (H3N2)" => "influenza, live, attenuated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'influenza (H3N2)'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'influenza, live, attenuated'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'influenza (H3N2)'
	);

-- old-style "influenza (H1N1)" => "influenza, live, attenuated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'influenza (H1N1)'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'influenza, live, attenuated'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'influenza (H1N1)'
	);

-- old-style "influenza (seasonal)" => "influenza, inactivated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'influenza (seasonal)'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'influenza, inactivated'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'influenza (seasonal)'
	);

-- old-style "influenza (H3N2)" => "influenza, inactivated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'influenza (H3N2)'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'influenza, inactivated'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'influenza (H3N2)'
	);

-- old-style "influenza (H1N1)" => "influenza, inactivated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'influenza (H1N1)'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'influenza, inactivated'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'influenza (H1N1)'
	);

-- old-style "meningococcus C" => "meningococcus C antigen"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'meningococcus C'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'meningococcus C antigen'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'meningococcus C'
	);

-- old-style "human papillomavirus" => "papillomavirus"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'human papillomavirus'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'papillomavirus'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'human papillomavirus'
	);

-- old-style "rabies" => "rabies, inactivated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'rabies'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'rabies, inactivated'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'rabies'
	);

-- old-style "cholera" => "cholera, live, attenuated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'cholera'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'cholera, live, attenuated'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'cholera'
	);

-- old-style "varicella (chickenpox, shingles)" => "herpes virus (chickenpox), live"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'varicella (chickenpox, shingles)'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'herpes virus (chickenpox), live'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'varicella (chickenpox, shingles)'
	);

-- old-style "diphtheria" => "diphtheria toxoid"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'diphtheria'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'diphtheria toxoid'
		),
		false
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'diphtheria'
	);

-- old-style "measles" => "measles, live, attenuated"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'measles'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'measles, live, attenuated'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'measles'
	);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-create_generic_vaccines.sql', '22.0');
