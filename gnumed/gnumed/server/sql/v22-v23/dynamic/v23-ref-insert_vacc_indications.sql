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
-- insert known indications (generated from gmVaccDefs.py)

-- v23: single-target vaccination indication "anthrax (bacillus anthracis)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'anthrax (bacillus anthracis)', 'J07AC01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'anthrax (bacillus anthracis)' OR atc = 'J07AC01'
);

-- v23: single-target vaccination indication "brucellosis (brucella)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'brucellosis (brucella)', 'J07AD01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'brucellosis (brucella)' OR atc = 'J07AD01'
);

-- v23: single-target vaccination indication "cholera (vibrio cholerae)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'cholera (vibrio cholerae)', 'J07AE0' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'cholera (vibrio cholerae)' OR atc = 'J07AE0'
);

-- v23: single-target vaccination indication "diphtheria (corynebacterium diphtheriae)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'diphtheria (corynebacterium diphtheriae)', 'J07AF01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'diphtheria (corynebacterium diphtheriae)' OR atc = 'J07AF01'
);

-- v23: single-target vaccination indication "HiB (hemophilus influenzae B)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'HiB (hemophilus influenzae B)', 'J07AG01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'HiB (hemophilus influenzae B)' OR atc = 'J07AG01'
);

-- v23: single-target vaccination indication "MenA (meningococcus A)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'MenA (meningococcus A)', 'J07AH01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'MenA (meningococcus A)' OR atc = 'J07AH01'
);

-- v23: single-target vaccination indication "MenB (meningococcus B)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'MenB (meningococcus B)', 'J07AH06' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'MenB (meningococcus B)' OR atc = 'J07AH06'
);

-- v23: single-target vaccination indication "MenC (meningococcus C)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'MenC (meningococcus C)', 'J07AH07' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'MenC (meningococcus C)' OR atc = 'J07AH07'
);

-- v23: single-target vaccination indication "MenY (meningococcus Y)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'MenY (meningococcus Y)', 'J07AH0Y' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'MenY (meningococcus Y)' OR atc = 'J07AH0Y'
);

-- v23: single-target vaccination indication "MenW (meningococcus W)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'MenW (meningococcus W)', 'J07AH0W' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'MenW (meningococcus W)' OR atc = 'J07AH0W'
);

-- v23: single-target vaccination indication "pertussis (bordetella pertussis)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'pertussis (bordetella pertussis)', 'J07AJ0' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'pertussis (bordetella pertussis)' OR atc = 'J07AJ0'
);

-- v23: single-target vaccination indication "plague (yersinia pestis)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'plague (yersinia pestis)', 'J07AK01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'plague (yersinia pestis)' OR atc = 'J07AK01'
);

-- v23: single-target vaccination indication "pneumococcal infection (streptococcus pneumoniae)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'pneumococcal infection (streptococcus pneumoniae)', 'J07AL0' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'pneumococcal infection (streptococcus pneumoniae)' OR atc = 'J07AL0'
);

-- v23: single-target vaccination indication "tetanus (clostridium tetani)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'tetanus (clostridium tetani)', 'J07AM01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'tetanus (clostridium tetani)' OR atc = 'J07AM01'
);

-- v23: single-target vaccination indication "tuberculosis (mycobacterium tuberculosis)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'tuberculosis (mycobacterium tuberculosis)', 'J07AN01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'tuberculosis (mycobacterium tuberculosis)' OR atc = 'J07AN01'
);

-- v23: single-target vaccination indication "typhoid (salmonella typhi)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'typhoid (salmonella typhi)', 'J07AP0' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'typhoid (salmonella typhi)' OR atc = 'J07AP0'
);

-- v23: single-target vaccination indication "parathypoid (salmonella typhi)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'parathypoid (salmonella typhi)', 'J07AP1' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'parathypoid (salmonella typhi)' OR atc = 'J07AP1'
);

-- v23: single-target vaccination indication "typhus exanthematicus (rickettsia prowazekii)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'typhus exanthematicus (rickettsia prowazekii)', 'J07AR01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'typhus exanthematicus (rickettsia prowazekii)' OR atc = 'J07AR01'
);

-- v23: single-target vaccination indication "Q fever (coxiella burnetii)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'Q fever (coxiella burnetii)', 'J07AXQF' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'Q fever (coxiella burnetii)' OR atc = 'J07AXQF'
);

-- v23: single-target vaccination indication "tick-borne meningoencephalitis (flavivirus)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'tick-borne meningoencephalitis (flavivirus)', 'J07BA01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'tick-borne meningoencephalitis (flavivirus)' OR atc = 'J07BA01'
);

-- v23: single-target vaccination indication "japanese B encephalitis (flavivirus)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'japanese B encephalitis (flavivirus)', 'J07BA0J' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'japanese B encephalitis (flavivirus)' OR atc = 'J07BA0J'
);

-- v23: single-target vaccination indication "influenza (seasonal, H3N2, H1N1)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'influenza (seasonal, H3N2, H1N1)', 'J07BB0' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'influenza (seasonal, H3N2, H1N1)' OR atc = 'J07BB0'
);

-- v23: single-target vaccination indication "hepatitis B (HBV)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'hepatitis B (HBV)', 'J07BC01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'hepatitis B (HBV)' OR atc = 'J07BC01'
);

-- v23: single-target vaccination indication "hepatitis A (HAV)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'hepatitis A (HAV)', 'J07BC02' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'hepatitis A (HAV)' OR atc = 'J07BC02'
);

-- v23: single-target vaccination indication "measles (morbillivirus hominis)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'measles (morbillivirus hominis)', 'J07BD01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'measles (morbillivirus hominis)' OR atc = 'J07BD01'
);

-- v23: single-target vaccination indication "mumps (Mumps orthorubolavirus)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'mumps (Mumps orthorubolavirus)', 'J07BE01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'mumps (Mumps orthorubolavirus)' OR atc = 'J07BE01'
);

-- v23: single-target vaccination indication "chickenpox, shingles (varicella zoster virus)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'chickenpox, shingles (varicella zoster virus)', 'J07BK0' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'chickenpox, shingles (varicella zoster virus)' OR atc = 'J07BK0'
);

-- v23: single-target vaccination indication "rubella (rubivirus rubellae)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'rubella (rubivirus rubellae)', 'J07BJ01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'rubella (rubivirus rubellae)' OR atc = 'J07BJ01'
);

-- v23: single-target vaccination indication "poliomyelitis (polio virus)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'poliomyelitis (polio virus)', 'J07BF0' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'poliomyelitis (polio virus)' OR atc = 'J07BF0'
);

-- v23: single-target vaccination indication "rabies (rabies lyssavirus)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'rabies (rabies lyssavirus)', 'J07BG01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'rabies (rabies lyssavirus)' OR atc = 'J07BG01'
);

-- v23: single-target vaccination indication "rotavirus"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'rotavirus', 'J07BH0' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'rotavirus' OR atc = 'J07BH0'
);

-- v23: single-target vaccination indication "yellow fever (yellow fever virus)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'yellow fever (yellow fever virus)', 'J07BL01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'yellow fever (yellow fever virus)' OR atc = 'J07BL01'
);

-- v23: single-target vaccination indication "smallpox, mpox (variola virus)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'smallpox, mpox (variola virus)', 'J07BX01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'smallpox, mpox (variola virus)' OR atc = 'J07BX01'
);

-- v23: single-target vaccination indication "dengue fever (flavivirus)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'dengue fever (flavivirus)', 'J07BX04' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'dengue fever (flavivirus)' OR atc = 'J07BX04'
);

-- v23: single-target vaccination indication "RSV (human respiratory syncytial virus)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'RSV (human respiratory syncytial virus)', 'J07BX05' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'RSV (human respiratory syncytial virus)' OR atc = 'J07BX05'
);

-- v23: single-target vaccination indication "HPV (generic)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'HPV (generic)', 'J07BM0' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'HPV (generic)' OR atc = 'J07BM0'
);

-- v23: single-target vaccination indication "HPV (6,11,16,18)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'HPV (6,11,16,18)', 'J07BM01' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'HPV (6,11,16,18)' OR atc = 'J07BM01'
);

-- v23: single-target vaccination indication "HPV (16,18)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'HPV (16,18)', 'J07BM02' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'HPV (16,18)' OR atc = 'J07BM02'
);

-- v23: single-target vaccination indication "HPV (6,11,16,18,31,33,45,52,58)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'HPV (6,11,16,18,31,33,45,52,58)', 'J07BM03' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'HPV (6,11,16,18,31,33,45,52,58)' OR atc = 'J07BM03'
);

-- v23: single-target vaccination indication "CoViD-2019 (SARS-CoV-2)"
INSERT INTO ref.vacc_indication (target, atc)
SELECT 'CoViD-2019 (SARS-CoV-2)', 'J07BX03' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = 'CoViD-2019 (SARS-CoV-2)' OR atc = 'J07BX03'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-ref-insert_vacc_indications.sql', '23.0');
