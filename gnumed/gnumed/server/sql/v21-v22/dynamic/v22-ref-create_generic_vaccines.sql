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
-- in case <salmo-antigen> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AP03' WHERE lower(description) = lower('salmonella typhi antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'salmonella typhi antigen',
		'J07AP03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AP03'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AP03-target', 'typhoid');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AP03-target', 'typhoid');

-- in case <menY> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AH0Y' WHERE lower(description) = lower('meningococcus Y antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'meningococcus Y antigen',
		'J07AH0Y'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AH0Y'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AH0Y-target', 'meningococcus Y');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AH0Y-target', 'meningococcus Y');

-- in case <menW> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AH0W' WHERE lower(description) = lower('meningococcus W-135 antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'meningococcus W-135 antigen',
		'J07AH0W'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AH0W'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AH0W-target', 'meningococcus W');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AH0W-target', 'meningococcus W');

-- in case <menBmem> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AH06' WHERE lower(description) = lower('meningococcus B membrane') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'meningococcus B membrane',
		'J07AH06'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AH06'
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
		SELECT 1 FROM ref.substance WHERE atc = 'J07AG01'
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
		SELECT 1 FROM ref.substance WHERE atc = 'J07AH01'
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
		SELECT 1 FROM ref.substance WHERE atc = 'J07AM01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AM01-target', 'tetanus');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AM01-target', 'tetanus');

-- in case <polio-inact> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BF03' WHERE lower(description) = lower('poliomyelitis, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'poliomyelitis, inactivated',
		'J07BF03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BF03'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BF03-target', 'poliomyelitis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BF03-target', 'poliomyelitis');

-- in case <fsme> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BA01' WHERE lower(description) = lower('flavivirus, tick-borne') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'flavivirus, tick-borne',
		'J07BA01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BA01'
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
		SELECT 1 FROM ref.substance WHERE atc = 'J07AXQF'
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
		SELECT 1 FROM ref.substance WHERE atc = 'J07BE01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BE01-target', 'mumps');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BE01-target', 'mumps');

-- in case <salmo-typh+ent> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AP10' WHERE lower(description) = lower('salmonella typhi, enterica') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'salmonella typhi, enterica',
		'J07AP10'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AP10'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AP10-target', 'typhoid, paratyphus');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AP10-target', 'typhoid, paratyphus');

-- in case <polio-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BF01' WHERE lower(description) = lower('poliomyelitis, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'poliomyelitis, live, attenuated',
		'J07BF01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BF01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BF01-target', 'poliomyelitis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BF01-target', 'poliomyelitis');

-- in case <pneumococcus> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AL01' WHERE lower(description) = lower('pneumococcus antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'pneumococcus antigen',
		'J07AL01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AL01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AL01-target', 'pneumococcus');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AL01-target', 'pneumococcus');

-- in case <yellow_fever-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BL01' WHERE lower(description) = lower('yellow fever virus, live') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'yellow fever virus, live',
		'J07BL01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BL01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BL01-target', 'yellow fever');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BL01-target', 'yellow fever');

-- in case <cholera> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AE01' WHERE lower(description) = lower('cholera, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'cholera, inactivated',
		'J07AE01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AE01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AE01-target', 'cholera');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AE01-target', 'cholera');

-- in case <menA-conj> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AH10' WHERE lower(description) = lower('meningococcus A antigen, conjugated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'meningococcus A antigen, conjugated',
		'J07AH10'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AH10'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AH10-target', 'meningococcus A');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AH10-target', 'meningococcus A');

-- in case <rubella-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BJ01' WHERE lower(description) = lower('rubella, live') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'rubella, live',
		'J07BJ01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BJ01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BJ01-target', 'rubella');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BJ01-target', 'rubella');

-- in case <japEnc-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BA03' WHERE lower(description) = lower('flavivirus, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'flavivirus, live, attenuated',
		'J07BA03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BA03'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BA03-target', 'japanese encephalitis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BA03-target', 'japanese encephalitis');

-- in case <pertussis-antigen> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AJ02' WHERE lower(description) = lower('pertussis, antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'pertussis, antigen',
		'J07AJ02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AJ02'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AJ02-target', 'pertussis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AJ02-target', 'pertussis');

-- in case <plague> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AK01' WHERE lower(description) = lower('yersinia pestis, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'yersinia pestis, inactivated',
		'J07AK01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AK01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AK01-target', 'plague');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AK01-target', 'plague');

-- in case <salmo-inact> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AP02' WHERE lower(description) = lower('salmonella typhi, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'salmonella typhi, inactivated',
		'J07AP02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AP02'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AP02-target', 'typhoid');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AP02-target', 'typhoid');

-- in case <hepA-antig> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BC03' WHERE lower(description) = lower('hepatitis A antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'hepatitis A antigen',
		'J07BC03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BC03'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BC03-target', 'hepatitis A');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BC03-target', 'hepatitis A');

-- in case <japEnc> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BA02' WHERE lower(description) = lower('flavivirus, japanese') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'flavivirus, japanese',
		'J07BA02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BA02'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BA02-target', 'japanese encephalitis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BA02-target', 'japanese encephalitis');

-- in case <tbc-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AN01' WHERE lower(description) = lower('tuberculosis, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'tuberculosis, live, attenuated',
		'J07AN01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AN01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AN01-target', 'tbc');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AN01-target', 'tbc');

-- in case <influ-inact-surf> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BB02' WHERE lower(description) = lower('influenza, inactivated, surface') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'influenza, inactivated, surface',
		'J07BB02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BB02'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BB02-target', 'influenza');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BB02-target', 'influenza');

-- in case <rota-live-atten> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BH01' WHERE lower(description) = lower('rotavirus, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'rotavirus, live, attenuated',
		'J07BH01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BH01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BH01-target', 'rotavirus diarrhea');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BH01-target', 'rotavirus diarrhea');

-- in case <pap6-11-16-18-31-33-45-52-58> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BM03' WHERE lower(description) = lower('papillomavirus 6,11,16,18,31,33,45,52,58') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'papillomavirus 6,11,16,18,31,33,45,52,58',
		'J07BM03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BM03'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BM03-target', 'HPV');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BM03-target', 'HPV');

-- in case <pertussis-inactivated> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AJ01' WHERE lower(description) = lower('pertussis, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'pertussis, inactivated',
		'J07AJ01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AJ01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AJ01-target', 'pertussis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AJ01-target', 'pertussis');

-- in case <hepB> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BC01' WHERE lower(description) = lower('hepatitis B antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'hepatitis B antigen',
		'J07BC01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BC01'
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
		SELECT 1 FROM ref.substance WHERE atc = 'J07AJ0'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AJ0-target', 'pertussis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AJ0-target', 'pertussis');

-- in case <hepA-inact> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BC02' WHERE lower(description) = lower('hepatitis A, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'hepatitis A, inactivated',
		'J07BC02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BC02'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BC02-target', 'hepatitis A');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BC02-target', 'hepatitis A');

-- in case <brucellosis> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AD01' WHERE lower(description) = lower('brucella antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'brucella antigen',
		'J07AD01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AD01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AD01-target', 'brucellosis');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AD01-target', 'brucellosis');

-- in case <salmo-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AP01' WHERE lower(description) = lower('salmonella typhi, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'salmonella typhi, live, attenuated',
		'J07AP01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AP01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AP01-target', 'typhoid');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AP01-target', 'typhoid');

-- in case <anthrax> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AC01' WHERE lower(description) = lower('bacillus anthracis antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'bacillus anthracis antigen',
		'J07AC01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AC01'
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
		SELECT 1 FROM ref.substance WHERE atc = 'J07BX01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BX01-target', 'variola (smallpox)');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BX01-target', 'variola (smallpox)');

-- in case <shingles-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BK02' WHERE lower(description) = lower('herpes virus (shingles), live') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'herpes virus (shingles), live',
		'J07BK02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BK02'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BK02-target', 'zoster (shingles)');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BK02-target', 'zoster (shingles)');

-- in case <influ-inact> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BB01' WHERE lower(description) = lower('influenza, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'influenza, inactivated',
		'J07BB01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BB01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BB01-target', 'influenza');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BB01-target', 'influenza');

-- in case <menBmulti> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AH09' WHERE lower(description) = lower('meningococcus B multicomponent') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'meningococcus B multicomponent',
		'J07AH09'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AH09'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AH09-target', 'meningococcus B');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AH09-target', 'meningococcus B');

-- in case <menC> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AH07' WHERE lower(description) = lower('meningococcus C antigen') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'meningococcus C antigen',
		'J07AH07'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AH07'
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
		SELECT 1 FROM ref.substance WHERE atc = 'J07BM0'
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
		SELECT 1 FROM ref.substance WHERE atc = 'J07BM01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BM01-target', 'HPV');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BM01-target', 'HPV');

-- in case <influ-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BB03' WHERE lower(description) = lower('influenza, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'influenza, live, attenuated',
		'J07BB03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BB03'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BB03-target', 'influenza');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BB03-target', 'influenza');

-- in case <rabies> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BG01' WHERE lower(description) = lower('rabies, inactivated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'rabies, inactivated',
		'J07BG01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BG01'
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
		SELECT 1 FROM ref.substance WHERE atc = 'J07AR01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AR01-target', 'typhus exanthematicus');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AR01-target', 'typhus exanthematicus');

-- in case <rota-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BH02' WHERE lower(description) = lower('rotavirus, live') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'rotavirus, live',
		'J07BH02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BH02'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BH02-target', 'rotavirus diarrhea');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BH02-target', 'rotavirus diarrhea');

-- in case <diphtheria> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AF01' WHERE lower(description) = lower('diphtheria toxoid') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'diphtheria toxoid',
		'J07AF01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AF01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AF01-target', 'diphtheria');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AF01-target', 'diphtheria');

-- in case <cholera-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AE02' WHERE lower(description) = lower('cholera, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'cholera, live, attenuated',
		'J07AE02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AE02'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AE02-target', 'cholera');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AE02-target', 'cholera');

-- in case <pap16-18> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BM02' WHERE lower(description) = lower('papillomavirus 16,18') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'papillomavirus 16,18',
		'J07BM02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BM02'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BM02-target', 'HPV');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BM02-target', 'HPV');

-- in case <chickenpox-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BK01' WHERE lower(description) = lower('herpes virus (chickenpox), live') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'herpes virus (chickenpox), live',
		'J07BK01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BK01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BK01-target', 'varicella (chickenpox)');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BK01-target', 'varicella (chickenpox)');

-- in case <pneumococcus-conjugated> already exists: add ATC
UPDATE ref.substance SET atc = 'J07AL02' WHERE lower(description) = lower('pneumococcus antigen, conjugated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'pneumococcus antigen, conjugated',
		'J07AL02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07AL02'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07AL02-target', 'pneumococcus');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07AL02-target', 'pneumococcus');

-- in case <measles-live> already exists: add ATC
UPDATE ref.substance SET atc = 'J07BD01' WHERE lower(description) = lower('measles, live, attenuated') AND atc IS NULL;

INSERT INTO ref.substance (description, atc)
	SELECT
		'measles, live, attenuated',
		'J07BD01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.substance WHERE atc = 'J07BD01'
	);

-- generic English
SELECT i18n.upd_tx('en', 'J07BD01-target', 'measles');
-- user language, if any, fails if not set
SELECT i18n.upd_tx('J07BD01-target', 'measles');

-- --------------------------------------------------------------
-- generic vaccines
-- --------------------------------------------------------------
-- new vaccines are not linked to indications, so disable that
-- trigger for the time being
ALTER TABLE ref.vaccine
	DISABLE TRIGGER tr_sanity_check_vaccine_has_indications
;

-- need to disable trigger before running
ALTER TABLE ref.drug_product
	DISABLE TRIGGER tr_assert_product_has_components
;

-- --------------------------------------------------------------
-- in case <influenza vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BB' WHERE
	atc_code IS NULL
		AND
	description = 'influenza vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'influenza vaccine',
		'vaccine',
		TRUE,
		'J07BB'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'influenza vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BB'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BB01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BB01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BB01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'influenza vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BB'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BB01' LIMIT 1)
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
					description = 'influenza vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BB'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'influenza vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BB'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'influenza vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BB'
			)
	);

-- --------------------------------------------------------------
-- in case <measles-mumps vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BD51' WHERE
	atc_code IS NULL
		AND
	description = 'measles-mumps vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'measles-mumps vaccine, live',
		'vaccine',
		TRUE,
		'J07BD51'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'measles-mumps vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'measles-mumps vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
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
					description = 'measles-mumps vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'measles-mumps vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
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
					description = 'measles-mumps vaccine, live'
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
			description = 'measles-mumps vaccine, live'
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
					description = 'measles-mumps vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD51'
			)
	);

-- --------------------------------------------------------------
-- in case <tetanus vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AM' WHERE
	atc_code IS NULL
		AND
	description = 'tetanus vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'tetanus vaccine',
		'vaccine',
		TRUE,
		'J07AM'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'tetanus vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'tetanus vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					description = 'tetanus vaccine'
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
			description = 'tetanus vaccine'
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
					description = 'tetanus vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AM'
			)
	);

-- --------------------------------------------------------------
-- in case <TdaPPol-HepB> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA12' WHERE
	atc_code IS NULL
		AND
	description = 'TdaPPol-HepB'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'TdaPPol-HepB',
		'vaccine',
		TRUE,
		'J07CA12'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'TdaPPol-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					description = 'TdaPPol-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					description = 'TdaPPol-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					description = 'TdaPPol-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					description = 'TdaPPol-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					description = 'TdaPPol-HepB'
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
			description = 'TdaPPol-HepB'
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
					description = 'TdaPPol-HepB'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA12'
			)
	);

-- --------------------------------------------------------------
-- in case <TdaP-Hib-HepB> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA11' WHERE
	atc_code IS NULL
		AND
	description = 'TdaP-Hib-HepB'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'TdaP-Hib-HepB',
		'vaccine',
		TRUE,
		'J07CA11'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'TdaP-Hib-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaP-Hib-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					description = 'TdaP-Hib-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaP-Hib-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					description = 'TdaP-Hib-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaP-Hib-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					description = 'TdaP-Hib-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaP-Hib-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
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
					description = 'TdaP-Hib-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaP-Hib-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					description = 'TdaP-Hib-HepB'
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
			description = 'TdaP-Hib-HepB'
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
					description = 'TdaP-Hib-HepB'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA11'
			)
	);

-- --------------------------------------------------------------
-- in case <HiB vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AG' WHERE
	atc_code IS NULL
		AND
	description = 'HiB vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'HiB vaccine',
		'vaccine',
		TRUE,
		'J07AG'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'HiB vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'HiB vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
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
					description = 'HiB vaccine'
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
			description = 'HiB vaccine'
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
					description = 'HiB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AG'
			)
	);

-- --------------------------------------------------------------
-- in case <influenza vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BB' WHERE
	atc_code IS NULL
		AND
	description = 'influenza vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'influenza vaccine, live',
		'vaccine',
		TRUE,
		'J07BB'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'influenza vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BB'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BB03' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BB03' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BB03' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'influenza vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BB'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BB03' LIMIT 1)
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
					description = 'influenza vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BB'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'influenza vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BB'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'influenza vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BB'
			)
	);

-- --------------------------------------------------------------
-- in case <MMR vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BD52' WHERE
	atc_code IS NULL
		AND
	description = 'MMR vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'MMR vaccine, live',
		'vaccine',
		TRUE,
		'J07BD52'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'MMR vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'MMR vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
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
					description = 'MMR vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'MMR vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
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
					description = 'MMR vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'MMR vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
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
					description = 'MMR vaccine, live'
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
			description = 'MMR vaccine, live'
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
					description = 'MMR vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD52'
			)
	);

-- --------------------------------------------------------------
-- in case <yellow fever vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BL' WHERE
	atc_code IS NULL
		AND
	description = 'yellow fever vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'yellow fever vaccine',
		'vaccine',
		TRUE,
		'J07BL'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'yellow fever vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BL01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BL01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BL01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'yellow fever vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BL01' LIMIT 1)
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
					description = 'yellow fever vaccine'
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
			description = 'yellow fever vaccine'
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
					description = 'yellow fever vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BL'
			)
	);

-- --------------------------------------------------------------
-- in case <tick-borne encephalitis vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BA' WHERE
	atc_code IS NULL
		AND
	description = 'tick-borne encephalitis vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'tick-borne encephalitis vaccine',
		'vaccine',
		TRUE,
		'J07BA'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'tick-borne encephalitis vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BA01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'tick-borne encephalitis vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA01' LIMIT 1)
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
					description = 'tick-borne encephalitis vaccine'
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
			description = 'tick-borne encephalitis vaccine'
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
					description = 'tick-borne encephalitis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BA'
			)
	);

-- --------------------------------------------------------------
-- in case <typhus exanthematicus vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AR' WHERE
	atc_code IS NULL
		AND
	description = 'typhus exanthematicus vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'typhus exanthematicus vaccine',
		'vaccine',
		TRUE,
		'J07AR'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'typhus exanthematicus vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AR01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AR01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AR01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'typhus exanthematicus vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AR01' LIMIT 1)
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
					description = 'typhus exanthematicus vaccine'
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
			description = 'typhus exanthematicus vaccine'
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
					description = 'typhus exanthematicus vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AR'
			)
	);

-- --------------------------------------------------------------
-- in case <varicella vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BK' WHERE
	atc_code IS NULL
		AND
	description = 'varicella vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'varicella vaccine, live',
		'vaccine',
		TRUE,
		'J07BK'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'varicella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BK'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BK01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'varicella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BK'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK01' LIMIT 1)
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
					description = 'varicella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BK'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'varicella vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BK'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'varicella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BK'
			)
	);

-- --------------------------------------------------------------
-- in case <variola vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BX01' WHERE
	atc_code IS NULL
		AND
	description = 'variola vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'variola vaccine, live',
		'vaccine',
		TRUE,
		'J07BX01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'variola vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BX01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BX01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BX01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'variola vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BX01' LIMIT 1)
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
					description = 'variola vaccine, live'
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
			description = 'variola vaccine, live'
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
					description = 'variola vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BX01'
			)
	);

-- --------------------------------------------------------------
-- in case <mumps-rubella vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BJ51' WHERE
	atc_code IS NULL
		AND
	description = 'mumps-rubella vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'mumps-rubella vaccine, live',
		'vaccine',
		TRUE,
		'J07BJ51'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'mumps-rubella vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'mumps-rubella vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
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
					description = 'mumps-rubella vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'mumps-rubella vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
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
					description = 'mumps-rubella vaccine, live'
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
			description = 'mumps-rubella vaccine, live'
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
					description = 'mumps-rubella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BJ51'
			)
	);

-- --------------------------------------------------------------
-- in case <poliomyelitis vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BF' WHERE
	atc_code IS NULL
		AND
	description = 'poliomyelitis vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'poliomyelitis vaccine, live',
		'vaccine',
		TRUE,
		'J07BF'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'poliomyelitis vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BF'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'poliomyelitis vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BF'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF01' LIMIT 1)
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
					description = 'poliomyelitis vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BF'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'poliomyelitis vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BF'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'poliomyelitis vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BF'
			)
	);

-- --------------------------------------------------------------
-- in case <typhoid-hepA vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA10' WHERE
	atc_code IS NULL
		AND
	description = 'typhoid-hepA vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'typhoid-hepA vaccine',
		'vaccine',
		TRUE,
		'J07CA10'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'typhoid-hepA vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AP02' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP02' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP02' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'typhoid-hepA vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP02' LIMIT 1)
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
					description = 'typhoid-hepA vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC02' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC02' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC02' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'typhoid-hepA vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC02' LIMIT 1)
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
					description = 'typhoid-hepA vaccine'
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
			description = 'typhoid-hepA vaccine'
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
					description = 'typhoid-hepA vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA10'
			)
	);

-- --------------------------------------------------------------
-- in case <mumps vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BE' WHERE
	atc_code IS NULL
		AND
	description = 'mumps vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'mumps vaccine, live',
		'vaccine',
		TRUE,
		'J07BE'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'mumps vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'mumps vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
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
					description = 'mumps vaccine, live'
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
			description = 'mumps vaccine, live'
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
					description = 'mumps vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BE'
			)
	);

-- --------------------------------------------------------------
-- in case <Tbc vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AN' WHERE
	atc_code IS NULL
		AND
	description = 'Tbc vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'Tbc vaccine',
		'vaccine',
		TRUE,
		'J07AN'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'Tbc vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AN01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AN01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AN01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'Tbc vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AN01' LIMIT 1)
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
					description = 'Tbc vaccine'
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
			description = 'Tbc vaccine'
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
					description = 'Tbc vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AN'
			)
	);

-- --------------------------------------------------------------
-- in case <meningococcus A vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AH' WHERE
	atc_code IS NULL
		AND
	description = 'meningococcus A vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'meningococcus A vaccine',
		'vaccine',
		TRUE,
		'J07AH'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'meningococcus A vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'meningococcus A vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1)
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
					description = 'meningococcus A vaccine'
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
			description = 'meningococcus A vaccine'
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
					description = 'meningococcus A vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH'
			)
	);

-- --------------------------------------------------------------
-- in case <meningococcus B vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AH' WHERE
	atc_code IS NULL
		AND
	description = 'meningococcus B vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'meningococcus B vaccine',
		'vaccine',
		TRUE,
		'J07AH'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'meningococcus B vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH06' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH06' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH06' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'meningococcus B vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH06' LIMIT 1)
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
					description = 'meningococcus B vaccine'
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
			description = 'meningococcus B vaccine'
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
					description = 'meningococcus B vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH'
			)
	);

-- --------------------------------------------------------------
-- in case <cholera vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AE' WHERE
	atc_code IS NULL
		AND
	description = 'cholera vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'cholera vaccine',
		'vaccine',
		TRUE,
		'J07AE'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'cholera vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AE01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'cholera vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE01' LIMIT 1)
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
					description = 'cholera vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AE'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'cholera vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'cholera vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AE'
			)
	);

-- --------------------------------------------------------------
-- in case <TdPol vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA01' WHERE
	atc_code IS NULL
		AND
	description = 'TdPol vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'TdPol vaccine',
		'vaccine',
		TRUE,
		'J07CA01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'TdPol vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdPol vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					description = 'TdPol vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdPol vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					description = 'TdPol vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdPol vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					description = 'TdPol vaccine'
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
			description = 'TdPol vaccine'
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
					description = 'TdPol vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA01'
			)
	);

-- --------------------------------------------------------------
-- in case <plague vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AK' WHERE
	atc_code IS NULL
		AND
	description = 'plague vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'plague vaccine',
		'vaccine',
		TRUE,
		'J07AK'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'plague vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AK01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AK01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AK01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'plague vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AK01' LIMIT 1)
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
					description = 'plague vaccine'
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
			description = 'plague vaccine'
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
					description = 'plague vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AK'
			)
	);

-- --------------------------------------------------------------
-- in case <TdaPPol vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA02' WHERE
	atc_code IS NULL
		AND
	description = 'TdaPPol vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'TdaPPol vaccine',
		'vaccine',
		TRUE,
		'J07CA02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'TdaPPol vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					description = 'TdaPPol vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					description = 'TdaPPol vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					description = 'TdaPPol vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					description = 'TdaPPol vaccine'
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
			description = 'TdaPPol vaccine'
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
					description = 'TdaPPol vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA02'
			)
	);

-- --------------------------------------------------------------
-- in case <rotavirus vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BH' WHERE
	atc_code IS NULL
		AND
	description = 'rotavirus vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'rotavirus vaccine, live',
		'vaccine',
		TRUE,
		'J07BH'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'rotavirus vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BH'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BH01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BH01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BH01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'rotavirus vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BH'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BH01' LIMIT 1)
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
					description = 'rotavirus vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BH'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'rotavirus vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BH'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'rotavirus vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BH'
			)
	);

-- --------------------------------------------------------------
-- in case <pneumococcus vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AL' WHERE
	atc_code IS NULL
		AND
	description = 'pneumococcus vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'pneumococcus vaccine',
		'vaccine',
		TRUE,
		'J07AL'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'pneumococcus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AL'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AL01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AL01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AL01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'pneumococcus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AL'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AL01' LIMIT 1)
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
					description = 'pneumococcus vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AL'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'pneumococcus vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AL'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'pneumococcus vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AL'
			)
	);

-- --------------------------------------------------------------
-- in case <typhoid vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AP' WHERE
	atc_code IS NULL
		AND
	description = 'typhoid vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'typhoid vaccine, live',
		'vaccine',
		TRUE,
		'J07AP'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'typhoid vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AP01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'typhoid vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP01' LIMIT 1)
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
					description = 'typhoid vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AP'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'typhoid vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'typhoid vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AP'
			)
	);

-- --------------------------------------------------------------
-- in case <zoster vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BK' WHERE
	atc_code IS NULL
		AND
	description = 'zoster vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'zoster vaccine, live',
		'vaccine',
		TRUE,
		'J07BK'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'zoster vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BK'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BK02' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK02' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK02' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'zoster vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BK'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK02' LIMIT 1)
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
					description = 'zoster vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BK'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'zoster vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BK'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'zoster vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BK'
			)
	);

-- --------------------------------------------------------------
-- in case <MMRV vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BD54' WHERE
	atc_code IS NULL
		AND
	description = 'MMRV vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'MMRV vaccine, live',
		'vaccine',
		TRUE,
		'J07BD54'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'MMRV vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'MMRV vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
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
					description = 'MMRV vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'MMRV vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BE01' LIMIT 1)
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
					description = 'MMRV vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'MMRV vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
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
					description = 'MMRV vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BK01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'MMRV vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BK01' LIMIT 1)
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
					description = 'MMRV vaccine, live'
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
			description = 'MMRV vaccine, live'
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
					description = 'MMRV vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD54'
			)
	);

-- --------------------------------------------------------------
-- in case <pertussis vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AJ' WHERE
	atc_code IS NULL
		AND
	description = 'pertussis vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'pertussis vaccine',
		'vaccine',
		TRUE,
		'J07AJ'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'pertussis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AJ'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'pertussis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AJ'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					description = 'pertussis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AJ'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'pertussis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AJ'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'pertussis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AJ'
			)
	);

-- --------------------------------------------------------------
-- in case <brucellosis vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AD' WHERE
	atc_code IS NULL
		AND
	description = 'brucellosis vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'brucellosis vaccine',
		'vaccine',
		TRUE,
		'J07AD'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'brucellosis vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AD01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AD01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AD01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'brucellosis vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AD01' LIMIT 1)
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
					description = 'brucellosis vaccine'
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
			description = 'brucellosis vaccine'
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
					description = 'brucellosis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AD'
			)
	);

-- --------------------------------------------------------------
-- in case <cholera vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AE' WHERE
	atc_code IS NULL
		AND
	description = 'cholera vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'cholera vaccine, live',
		'vaccine',
		TRUE,
		'J07AE'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'cholera vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AE02' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE02' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE02' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'cholera vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE02' LIMIT 1)
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
					description = 'cholera vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AE'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		True,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'cholera vaccine, live'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AE'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS True
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'cholera vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AE'
			)
	);

-- --------------------------------------------------------------
-- in case <TdaP-HepB vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA05' WHERE
	atc_code IS NULL
		AND
	description = 'TdaP-HepB vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'TdaP-HepB vaccine',
		'vaccine',
		TRUE,
		'J07CA05'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'TdaP-HepB vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaP-HepB vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					description = 'TdaP-HepB vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaP-HepB vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					description = 'TdaP-HepB vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaP-HepB vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					description = 'TdaP-HepB vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaP-HepB vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					description = 'TdaP-HepB vaccine'
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
			description = 'TdaP-HepB vaccine'
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
					description = 'TdaP-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA05'
			)
	);

-- --------------------------------------------------------------
-- in case <Td-HepB vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA07' WHERE
	atc_code IS NULL
		AND
	description = 'Td-HepB vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'Td-HepB vaccine',
		'vaccine',
		TRUE,
		'J07CA07'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'Td-HepB vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'Td-HepB vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					description = 'Td-HepB vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'Td-HepB vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					description = 'Td-HepB vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'Td-HepB vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					description = 'Td-HepB vaccine'
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
			description = 'Td-HepB vaccine'
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
					description = 'Td-HepB vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA07'
			)
	);

-- --------------------------------------------------------------
-- in case <TdaPPol-HiB-HepB-MenAC> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA13' WHERE
	atc_code IS NULL
		AND
	description = 'TdaPPol-HiB-HepB-MenAC'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'TdaPPol-HiB-HepB-MenAC',
		'vaccine',
		TRUE,
		'J07CA13'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB-MenAC'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB-MenAC'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB-MenAC'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB-MenAC'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB-MenAC'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB-MenAC'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB-MenAC'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB-MenAC'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB-MenAC'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB-MenAC'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB-MenAC'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB-MenAC'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB-MenAC'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB-MenAC'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB-MenAC'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB-MenAC'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB-MenAC'
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
			description = 'TdaPPol-HiB-HepB-MenAC'
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
					description = 'TdaPPol-HiB-HepB-MenAC'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA13'
			)
	);

-- --------------------------------------------------------------
-- in case <anthrax vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AC' WHERE
	atc_code IS NULL
		AND
	description = 'anthrax vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'anthrax vaccine',
		'vaccine',
		TRUE,
		'J07AC'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'anthrax vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AC01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AC01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AC01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'anthrax vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AC01' LIMIT 1)
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
					description = 'anthrax vaccine'
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
			description = 'anthrax vaccine'
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
					description = 'anthrax vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AC'
			)
	);

-- --------------------------------------------------------------
-- in case <poliomyelitis vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BF' WHERE
	atc_code IS NULL
		AND
	description = 'poliomyelitis vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'poliomyelitis vaccine',
		'vaccine',
		TRUE,
		'J07BF'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'poliomyelitis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BF'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'poliomyelitis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BF'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					description = 'poliomyelitis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BF'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'poliomyelitis vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07BF'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'poliomyelitis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BF'
			)
	);

-- --------------------------------------------------------------
-- in case <measles-rubella vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BD53' WHERE
	atc_code IS NULL
		AND
	description = 'measles-rubella vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'measles-rubella vaccine, live',
		'vaccine',
		TRUE,
		'J07BD53'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'measles-rubella vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'measles-rubella vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
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
					description = 'measles-rubella vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'measles-rubella vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
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
					description = 'measles-rubella vaccine, live'
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
			description = 'measles-rubella vaccine, live'
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
					description = 'measles-rubella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD53'
			)
	);

-- --------------------------------------------------------------
-- in case <Q fever vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AXQF' WHERE
	atc_code IS NULL
		AND
	description = 'Q fever vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'Q fever vaccine',
		'vaccine',
		TRUE,
		'J07AXQF'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'Q fever vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AXQF' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AXQF' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AXQF' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'Q fever vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AXQF' LIMIT 1)
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
					description = 'Q fever vaccine'
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
			description = 'Q fever vaccine'
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
					description = 'Q fever vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AXQF'
			)
	);

-- --------------------------------------------------------------
-- in case <typhoid/paratyphus vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AP10' WHERE
	atc_code IS NULL
		AND
	description = 'typhoid/paratyphus vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'typhoid/paratyphus vaccine',
		'vaccine',
		TRUE,
		'J07AP10'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'typhoid/paratyphus vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AP10' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP10' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP10' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'typhoid/paratyphus vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP10' LIMIT 1)
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
					description = 'typhoid/paratyphus vaccine'
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
			description = 'typhoid/paratyphus vaccine'
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
					description = 'typhoid/paratyphus vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AP10'
			)
	);

-- --------------------------------------------------------------
-- in case <meningococcus ACYW135 vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AH04' WHERE
	atc_code IS NULL
		AND
	description = 'meningococcus ACYW135 vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'meningococcus ACYW135 vaccine',
		'vaccine',
		TRUE,
		'J07AH04'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'meningococcus ACYW135 vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'meningococcus ACYW135 vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1)
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
					description = 'meningococcus ACYW135 vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'meningococcus ACYW135 vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1)
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
					description = 'meningococcus ACYW135 vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH0Y' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH0Y' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH0Y' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'meningococcus ACYW135 vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH0Y' LIMIT 1)
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
					description = 'meningococcus ACYW135 vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH0W' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH0W' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH0W' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'meningococcus ACYW135 vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH0W' LIMIT 1)
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
					description = 'meningococcus ACYW135 vaccine'
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
			description = 'meningococcus ACYW135 vaccine'
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
					description = 'meningococcus ACYW135 vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH04'
			)
	);

-- --------------------------------------------------------------
-- in case <hepatitis A vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BC02' WHERE
	atc_code IS NULL
		AND
	description = 'hepatitis A vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'hepatitis A vaccine',
		'vaccine',
		TRUE,
		'J07BC02'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'hepatitis A vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC02' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC02' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC02' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'hepatitis A vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC02' LIMIT 1)
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
					description = 'hepatitis A vaccine'
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
			description = 'hepatitis A vaccine'
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
					description = 'hepatitis A vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BC02'
			)
	);

-- --------------------------------------------------------------
-- in case <hepatitis B vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BC01' WHERE
	atc_code IS NULL
		AND
	description = 'hepatitis B vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'hepatitis B vaccine',
		'vaccine',
		TRUE,
		'J07BC01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'hepatitis B vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'hepatitis B vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					description = 'hepatitis B vaccine'
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
			description = 'hepatitis B vaccine'
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
					description = 'hepatitis B vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BC01'
			)
	);

-- --------------------------------------------------------------
-- in case <meningococcus C vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AH' WHERE
	atc_code IS NULL
		AND
	description = 'meningococcus C vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'meningococcus C vaccine',
		'vaccine',
		TRUE,
		'J07AH'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'meningococcus C vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'meningococcus C vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1)
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
					description = 'meningococcus C vaccine'
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
			description = 'meningococcus C vaccine'
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
					description = 'meningococcus C vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH'
			)
	);

-- --------------------------------------------------------------
-- in case <rubella vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BJ' WHERE
	atc_code IS NULL
		AND
	description = 'rubella vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'rubella vaccine, live',
		'vaccine',
		TRUE,
		'J07BJ'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'rubella vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'rubella vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
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
					description = 'rubella vaccine, live'
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
			description = 'rubella vaccine, live'
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
					description = 'rubella vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BJ'
			)
	);

-- --------------------------------------------------------------
-- in case <rabies vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BG' WHERE
	atc_code IS NULL
		AND
	description = 'rabies vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'rabies vaccine',
		'vaccine',
		TRUE,
		'J07BG'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'rabies vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BG01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BG01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BG01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'rabies vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BG01' LIMIT 1)
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
					description = 'rabies vaccine'
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
			description = 'rabies vaccine'
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
					description = 'rabies vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BG'
			)
	);

-- --------------------------------------------------------------
-- in case <typhoid vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AP' WHERE
	atc_code IS NULL
		AND
	description = 'typhoid vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'typhoid vaccine',
		'vaccine',
		TRUE,
		'J07AP'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'typhoid vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP'
	);

-- create dose, assumes substance exists
INSERT INTO ref.dose (fk_substance, amount, unit, dose_unit)
	SELECT
		(SELECT pk FROM ref.substance WHERE atc = 'J07AP02' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP02' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP02' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'typhoid vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_dose2drug WHERE
			fk_dose = (
				SELECT PK from ref.dose WHERE
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP02' LIMIT 1)
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
					description = 'typhoid vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AP'
			)
	);

-- add vaccine if necessary
INSERT INTO ref.vaccine (is_live, fk_drug_product)
	SELECT
		False,
		(SELECT pk FROM ref.drug_product WHERE
			description = 'typhoid vaccine'
				AND
			preparation = 'vaccine'
				AND
			is_fake = TRUE
				AND
			atc_code = 'J07AP'
		)
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE
			is_live IS False
				AND
			fk_drug_product = (
				SELECT pk FROM ref.drug_product WHERE
					description = 'typhoid vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AP'
			)
	);

-- --------------------------------------------------------------
-- in case <HPV vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BM' WHERE
	atc_code IS NULL
		AND
	description = 'HPV vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'HPV vaccine',
		'vaccine',
		TRUE,
		'J07BM'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'HPV vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BM0' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BM0' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BM0' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'HPV vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BM0' LIMIT 1)
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
					description = 'HPV vaccine'
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
			description = 'HPV vaccine'
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
					description = 'HPV vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BM'
			)
	);

-- --------------------------------------------------------------
-- in case <Td-rubella vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA03' WHERE
	atc_code IS NULL
		AND
	description = 'Td-rubella vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'Td-rubella vaccine',
		'vaccine',
		TRUE,
		'J07CA03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'Td-rubella vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'Td-rubella vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					description = 'Td-rubella vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'Td-rubella vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					description = 'Td-rubella vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'Td-rubella vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BJ01' LIMIT 1)
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
					description = 'Td-rubella vaccine'
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
			description = 'Td-rubella vaccine'
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
					description = 'Td-rubella vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA03'
			)
	);

-- --------------------------------------------------------------
-- in case <DTPol vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA01' WHERE
	atc_code IS NULL
		AND
	description = 'DTPol vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'DTPol vaccine',
		'vaccine',
		TRUE,
		'J07CA01'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'DTPol vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'DTPol vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					description = 'DTPol vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'DTPol vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					description = 'DTPol vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'DTPol vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					description = 'DTPol vaccine'
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
			description = 'DTPol vaccine'
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
					description = 'DTPol vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA01'
			)
	);

-- --------------------------------------------------------------
-- in case <tetanus-diptheria vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AM51' WHERE
	atc_code IS NULL
		AND
	description = 'tetanus-diptheria vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'tetanus-diptheria vaccine',
		'vaccine',
		TRUE,
		'J07AM51'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'tetanus-diptheria vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'tetanus-diptheria vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					description = 'tetanus-diptheria vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'tetanus-diptheria vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					description = 'tetanus-diptheria vaccine'
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
			description = 'tetanus-diptheria vaccine'
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
					description = 'tetanus-diptheria vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AM51'
			)
	);

-- --------------------------------------------------------------
-- in case <cholera-typhoid vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AE51' WHERE
	atc_code IS NULL
		AND
	description = 'cholera-typhoid vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'cholera-typhoid vaccine',
		'vaccine',
		TRUE,
		'J07AE51'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'cholera-typhoid vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AE01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'cholera-typhoid vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AE01' LIMIT 1)
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
					description = 'cholera-typhoid vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AP02' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP02' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP02' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'cholera-typhoid vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AP02' LIMIT 1)
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
					description = 'cholera-typhoid vaccine'
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
			description = 'cholera-typhoid vaccine'
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
					description = 'cholera-typhoid vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AE51'
			)
	);

-- --------------------------------------------------------------
-- in case <TdaPPol-HiB-HepB> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA09' WHERE
	atc_code IS NULL
		AND
	description = 'TdaPPol-HiB-HepB'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'TdaPPol-HiB-HepB',
		'vaccine',
		TRUE,
		'J07CA09'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'TdaPPol-HiB-HepB'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BC01' LIMIT 1)
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
					description = 'TdaPPol-HiB-HepB'
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
			description = 'TdaPPol-HiB-HepB'
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
					description = 'TdaPPol-HiB-HepB'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA09'
			)
	);

-- --------------------------------------------------------------
-- in case <japanese encephalitis vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BA03' WHERE
	atc_code IS NULL
		AND
	description = 'japanese encephalitis vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'japanese encephalitis vaccine, live',
		'vaccine',
		TRUE,
		'J07BA03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'japanese encephalitis vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BA03' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA03' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA03' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'japanese encephalitis vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA03' LIMIT 1)
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
					description = 'japanese encephalitis vaccine, live'
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
			description = 'japanese encephalitis vaccine, live'
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
					description = 'japanese encephalitis vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BA03'
			)
	);

-- --------------------------------------------------------------
-- in case <DTaPPol-Hib vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07CA06' WHERE
	atc_code IS NULL
		AND
	description = 'DTaPPol-Hib vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'DTaPPol-Hib vaccine',
		'vaccine',
		TRUE,
		'J07CA06'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'DTaPPol-Hib vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'DTaPPol-Hib vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AM01' LIMIT 1)
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
					description = 'DTaPPol-Hib vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'DTaPPol-Hib vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					description = 'DTaPPol-Hib vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'DTaPPol-Hib vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AJ0' LIMIT 1)
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
					description = 'DTaPPol-Hib vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'DTaPPol-Hib vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BF03' LIMIT 1)
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
					description = 'DTaPPol-Hib vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'DTaPPol-Hib vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AG01' LIMIT 1)
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
					description = 'DTaPPol-Hib vaccine'
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
			description = 'DTaPPol-Hib vaccine'
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
					description = 'DTaPPol-Hib vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07CA06'
			)
	);

-- --------------------------------------------------------------
-- in case <diphtheria vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AF' WHERE
	atc_code IS NULL
		AND
	description = 'diphtheria vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'diphtheria vaccine',
		'vaccine',
		TRUE,
		'J07AF'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'diphtheria vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'diphtheria vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AF01' LIMIT 1)
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
					description = 'diphtheria vaccine'
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
			description = 'diphtheria vaccine'
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
					description = 'diphtheria vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AF'
			)
	);

-- --------------------------------------------------------------
-- in case <measles vaccine, live> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BD' WHERE
	atc_code IS NULL
		AND
	description = 'measles vaccine, live'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'measles vaccine, live',
		'vaccine',
		TRUE,
		'J07BD'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'measles vaccine, live'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'measles vaccine, live'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BD01' LIMIT 1)
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
					description = 'measles vaccine, live'
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
			description = 'measles vaccine, live'
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
					description = 'measles vaccine, live'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BD'
			)
	);

-- --------------------------------------------------------------
-- in case <meningococcus AC vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07AH03' WHERE
	atc_code IS NULL
		AND
	description = 'meningococcus AC vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'meningococcus AC vaccine',
		'vaccine',
		TRUE,
		'J07AH03'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'meningococcus AC vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'meningococcus AC vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH01' LIMIT 1)
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
					description = 'meningococcus AC vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'meningococcus AC vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07AH07' LIMIT 1)
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
					description = 'meningococcus AC vaccine'
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
			description = 'meningococcus AC vaccine'
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
					description = 'meningococcus AC vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07AH03'
			)
	);

-- --------------------------------------------------------------
-- in case <japanese encephalitis vaccine> exists: add ATC
UPDATE ref.drug_product SET atc_code = 'J07BA' WHERE
	atc_code IS NULL
		AND
	description = 'japanese encephalitis vaccine'
		AND
	preparation = 'vaccine'
		AND
	is_fake IS TRUE;

INSERT INTO ref.drug_product (description, preparation, is_fake, atc_code)
	SELECT
		'japanese encephalitis vaccine',
		'vaccine',
		TRUE,
		'J07BA'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.drug_product WHERE
			description = 'japanese encephalitis vaccine'
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
		(SELECT pk FROM ref.substance WHERE atc = 'J07BA02' LIMIT 1),
		1,
		'dose',
		'shot'
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.dose WHERE
			fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA02' LIMIT 1)
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA02' LIMIT 1)
						AND
					amount = 1
						AND
					unit = 'dose'
						AND
					dose_unit IS NOT DISTINCT FROM 'shot'
		),
		(SELECT pk FROM ref.drug_product WHERE
			description = 'japanese encephalitis vaccine'
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
					fk_substance = (SELECT pk FROM ref.substance WHERE atc = 'J07BA02' LIMIT 1)
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
					description = 'japanese encephalitis vaccine'
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
			description = 'japanese encephalitis vaccine'
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
					description = 'japanese encephalitis vaccine'
						AND
					preparation = 'vaccine'
						AND
					is_fake = TRUE
						AND
					atc_code = 'J07BA'
			)
	);

-- want to re-enable trigger as now all inserted
-- vaccines satisfy the conditions
ALTER TABLE ref.drug_product
	ENABLE TRIGGER tr_assert_product_has_components
;

-- --------------------------------------------------------------
-- populate helper table
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

-- old-style "japanese B encephalitis" => "flavivirus, live, attenuated"
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
			substance = 'flavivirus, live, attenuated'
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

-- old-style "rotavirus" => "rotavirus, live"
INSERT INTO staging.lnk_vacc_ind2subst_dose (fk_indication, fk_dose, is_live)
	SELECT
		(SELECT id FROM ref.vacc_indication WHERE description = 'rotavirus'),
		(SELECT pk_dose FROM ref.v_substance_doses WHERE
			amount = 1
				AND
			unit = 'dose'
				AND
			dose_unit = 'shot'
				AND
			substance = 'rotavirus, live'
		),
		true
	WHERE EXISTS (
		SELECT 1 FROM ref.vacc_indication WHERE description = 'rotavirus'
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
