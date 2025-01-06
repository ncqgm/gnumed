# -*- coding: utf-8 -*-

"""GNUmed vaccination related definitions (only).

Based on WHO ATC data.

Interestingly, WHO does not list ATC codes for a few
vaccination indications, such as Q-fever. It also misses some
common multi-component vaccines, such as TdaP."""

#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2"

import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try:
		_
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()


_log = logging.getLogger('gm.vacc')

#============================================================
__VACCINATION__SINGLE_TARGET_ATCS = {
	# -- non-viral -------------------------------
	'anthrax (bacillus anthracis)': {'atc': 'J07AC01'},
	'brucellosis (brucella)': {'atc': 'J07AD01'},
	'cholera (vibrio cholerae)': {'atc': 'J07AE0'},
	'diphtheria (corynebacterium diphtheriae)': {'atc': 'J07AF01'},
	'HiB (hemophilus influenzae B)': {'atc': 'J07AG01'},
	'MenA (meningococcus A)': {'atc': 'J07AH01'},
	'MenB (meningococcus B)': {'atc': 'J07AH06'},
	'MenC (meningococcus C)': {'atc': 'J07AH07'},
	'MenY (meningococcus Y)': {'atc': 'J07AH0Y'},
	'MenW (meningococcus W)': {'atc': 'J07AH0W'},
	'pertussis (bordetella pertussis)': {'atc': 'J07AJ0'},
	'plague (yersinia pestis)': {'atc': 'J07AK01'},
	'pneumococcal infection (streptococcus pneumoniae)': {'atc': 'J07AL0'},
	'tetanus (clostridium tetani)': {'atc': 'J07AM01'},
	'tuberculosis (mycobacterium tuberculosis)': {'atc': 'J07AN01'},
	'typhoid (salmonella typhi)': {'atc': 'J07AP0'},
	'parathypoid (salmonella typhi)': {'atc': 'J07AP1'},
	'typhus exanthematicus (rickettsia prowazekii)': {'atc': 'J07AR01'},
	'Q fever (coxiella burnetii)': {'atc': 'J07AXQF'},
	# -- viral ------------------------------------------------
	'tick-borne meningoencephalitis (flavivirus)': {'atc': 'J07BA01'},
	'japanese B encephalitis (flavivirus)': {'atc': 'J07BA0J'},
	'influenza (seasonal, H3N2, H1N1)': {'atc': 'J07BB0'},
	'hepatitis B (HBV)': {'atc': 'J07BC01'},
	'hepatitis A (HAV)': {'atc': 'J07BC02'},
	'measles (morbillivirus hominis)': {'atc': 'J07BD01'},
	'mumps (Mumps orthorubolavirus)': {'atc': 'J07BE01'},
	'chickenpox, shingles (varicella zoster virus)': {'atc': 'J07BK0'},
	'rubella (rubivirus rubellae)': {'atc': 'J07BJ01'},
	'poliomyelitis (polio virus)': {'atc': 'J07BF0'},
	'rabies (rabies lyssavirus)': {'atc': 'J07BG01'},
	'rotavirus': {'atc': 'J07BH0'},
	'yellow fever (yellow fever virus)': {'atc': 'J07BL01'},
	'smallpox, mpox (variola virus)': {'atc': 'J07BX01'},
	'dengue fever (flavivirus)': {'atc': 'J07BX04'},
	'RSV (human respiratory syncytial virus)': {'atc': 'J07BX05'},
	'HPV (generic)': {'atc': 'J07BM0'},
	'HPV (6,11,16,18)': {'atc': 'J07BM01'},
	'HPV (16,18)': {'atc': 'J07BM02'},
	'HPV (6,11,16,18,31,33,45,52,58)': {'atc': 'J07BM03'},
	'CoViD-2019 (SARS-CoV-2)': {'atc': 'J07BX03'}
}

#============================================================
__SQL_v23_insert_vaccination_target = """-- v23: single-target vaccination indication "%(target)s"
INSERT INTO ref.vacc_indication (target, atc)
SELECT '%(target)s', '%(atc)s' WHERE NOT EXISTS (
	SELECT 1 FROM ref.vacc_indication
	WHERE target = '%(target)s' OR atc = '%(atc)s'
);
"""

# useful for creating a bootstrapper script
def v23_generate_vaccination_targets_SQL():
	lines = []
	for target, data in __VACCINATION__SINGLE_TARGET_ATCS.items():
		lines.append(__SQL_v23_insert_vaccination_target % {
			'target': target,
			'atc': data['atc']
		})
	return '\n'.join(lines)

#============================================================
__SQL_v23_insert_generic_vaccine = """-- v23: single-target generic vaccine for indication "%(target)s"
INSERT INTO ref.vaccine (atc, comment, is_live)
	SELECT '%(atc)s', 'generic vaccine for %(target)s', False
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.vaccine WHERE atc = '%(atc)s'
	);

INSERT INTO ref.lnk_indic2vaccine (fk_vaccine, fk_indication)
	SELECT
		(SELECT pk FROM ref.vaccine WHERE atc = '%(atc)s' AND fk_drug_product IS NULL),
		(SELECT pk FROM ref.vacc_indication WHERE atc = '%(atc)s')
	WHERE NOT EXISTS (
		SELECT 1 FROM ref.lnk_indic2vaccine
		WHERE
			(fk_vaccine = (SELECT pk FROM ref.vaccine WHERE atc = '%(atc)s' AND fk_drug_product IS NULL))
				AND
			(fk_indication = (SELECT pk FROM ref.vacc_indication WHERE atc = '%(atc)s'))
	);
"""

def v23_generate_generic_vaccines_SQL():
	lines = []
	for target, data in __VACCINATION__SINGLE_TARGET_ATCS.items():
		lines.append(__SQL_v23_insert_generic_vaccine % {
			'target': target,
			'atc': data['atc']
		})
	return '\n'.join(lines)

#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	#-----------------------------------------------------
	def test_v23_generate_vaccination_targets_SQL():
		print(v23_generate_vaccination_targets_SQL())

	#-----------------------------------------------------
	def test_v23_generate_generic_vaccines_SQL():
		print(v23_generate_generic_vaccines_SQL())

	#-----------------------------------------------------
	#test_v23_generate_vaccination_targets_SQL()
	test_v23_generate_generic_vaccines_SQL()
