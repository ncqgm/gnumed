# -*- coding: utf-8 -*-

from __future__ import print_function

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
from Gnumed.pycommon import gmI18N
if __name__ == '__main__':
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')


_log = logging.getLogger('gm.vacc')

#============================================================
_VACCINE_SUBSTANCES = {

	# bacterial

	'anthrax': {
		'name': u'bacillus anthracis antigen',
		'atc4target': u'J07AC01',
		'target': _(u'J07AC01-target::anthrax'),
		'v21_indications': [u'bacillus anthracis (Anthrax)']
	},

	'brucellosis': {
		'name': u'brucella antigen',
		'atc4target': u'J07AD01',
		'target': _(u'J07AD01-target::brucellosis')
	},

	'cholera': {
		'name': u'cholera, inactivated',
		'atc4target': u'J07AE0',
		'target': _(u'J07AE0-target::cholera'),
		'v21_indications': [u'cholera']
	},
	'cholera-live': {
		'name': u'cholera, live, attenuated',
		'atc4target': u'J07AE0',
		'target': _(u'J07AE0-target::cholera'),
		'v21_indications_live': [u'cholera']
	},

	'diphtheria': {
		'name': u'diphtheria toxoid',
		'atc4target': u'J07AF01',
		'target': _(u'J07AF01-target::diphtheria'),
		'v21_indications': [u'diphtheria']
	},

	'HiB': {
		'name': u'hemophilus influenzae B antigen',
		'atc4target': u'J07AG01',
		'target': _(u'J07AG01-target::HiB'),
		'v21_indications': [u'haemophilus influenzae b']
	},

	'menA': {
		'name': u'meningococcus A antigen',
		'atc4target': u'J07AH01',
		'target': _(u'J07AH01-target::meningococcus A'),
		'v21_indications': [u'meningococcus A']
	},
#	'menA-conj': {
#		'name': u'meningococcus A antigen, conjugated',
#		'atc4target': u'J07AH10',
#		'target': _(u'J07AH10-target::meningococcus A')
#	},
	'menBmem': {
		'name': u'meningococcus B membrane',
		'atc4target': u'J07AH06',
		'target': _(u'J07AH06-target::meningococcus B')
	},
#	'menBmulti': {
#		'name': u'meningococcus B multicomponent',
#		'atc4target': u'J07AH09',
#		'target': _(u'J07AH09-target::meningococcus B'),
#	},
	'menC': {
		'name': u'meningococcus C antigen',
		'atc4target': u'J07AH07',
		'target': _(u'J07AH07-target::meningococcus C'),
		'v21_indications': [u'meningococcus C']
	},
	'menY': {		# fake
		'name': u'meningococcus Y antigen',
		'atc4target': u'J07AH0Y',
		'target': _(u'J07AH0Y-target::meningococcus Y'),
		'v21_indications': [u'meningococcus Y']
	},
	'menW': {		# fake
		'name': u'meningococcus W-135 antigen',
		'atc4target': u'J07AH0W',
		'target': _(u'J07AH0W-target::meningococcus W'),
		'v21_indications': [u'meningococcus W']
	},

	'pertussis': {		# fake
		'name': u'pertussis',
		'atc4target': u'J07AJ0',
		'target': _(u'J07AJ0-target::pertussis'),
		'v21_indications': [u'pertussis']
	},
#	'pertussis-inactivated': {
#		'name': u'pertussis, inactivated',
#		'atc4target': u'J07AJ01',
#		'target': _(u'J07AJ01-target::pertussis')
#	},
#	'pertussis-antigen': {
#		'name': u'pertussis, antigen',
#		'atc4target': u'J07AJ02',
#		'target': _(u'J07AJ02-target::pertussis')
#	},

	'plague': {
		'name': u'yersinia pestis, inactivated',
		'atc4target': u'J07AK01',
		'target': _(u'J07AK01-target::plague'),
		'v21_indications': [u'yersinia pestis']
	},

	'pneumococcus': {
		'name': u'pneumococcus antigen',
		'atc4target': u'J07AL0',
		'target': _(u'J07AL0-target::pneumococcus'),
		'v21_indications': [u'pneumococcus']
	},
#	'pneumococcus-conjugated': {
#		'name': u'pneumococcus antigen, conjugated',
#		'atc4target': u'J07AL02',
#		'target': _(u'J07AL02-target::pneumococcus'),
#	},

	'tetanus': {
		'name': u'tetanus toxoid',
		'atc4target': u'J07AM01',
		'target': _(u'J07AM01-target::tetanus'),
		'v21_indications': [u'tetanus']
	},

	'tbc-live': {
		'name': u'tuberculosis, live, attenuated',
		'atc4target': u'J07AN01',
		'target': _(u'J07AN01-target::tbc'),
		'v21_indications_live': [u'tuberculosis']
	},

	'salmo-live': {
		'name': u'salmonella typhi, live, attenuated',
		'atc4target': u'J07AP0',
		'target': _(u'J07AP0-target::typhoid'),
		'v21_indications_live': [u'salmonella typhi (typhoid)']
	},
	'salmo-inact': {
		'name': u'salmonella typhi, inactivated',
		'atc4target': u'J07AP0',
		'target': _(u'J07AP0-target::typhoid')
	},
#	'salmo-antigen': {
#		'name': u'salmonella typhi antigen',
#		'atc4target': u'J07AP03',
#		'target': _(u'J07AP03-target::typhoid')
#	},
	'salmo-typh+ent': {
		'name': u'salmonella typhi, enterica',
		'atc4target': u'J07AP1',
		'target': _(u'J07AP1-target::typhoid, paratyphus'),
		'v21_indications': [u'salmonella typhi (typhoid)']
	},

	'typh-exanth': {
		'name': u'rickettsia prowazekii, inactivated',
		'atc4target': u'J07AR01',
		'target': _(u'J07AR01-target::typhus exanthematicus')
	},

	'qfever': {		# fake
		'name': u'coxiella burnetii',
		'atc4target': u'J07AXQF',
		'target': _(u'J07AXQF-target::Q fever'),
		'v21_indications': [u'coxiella burnetii (Q fever)']
	},

	# viral

	'fsme': {
		'name': u'flavivirus, tick-borne',
		'atc4target': u'J07BA01',
		'target': _(u'J07BA01-target::tick-borne encephalitis'),
		'v21_indications': [u'tick-borne meningoencephalitis']
	},

	'japEnc': {
		'name': u'flavivirus, japanese',
		'atc4target': u'J07BA0J',		# fake
		'target': _(u'J07BA0J-target::japanese encephalitis'),
		'v21_indications': [u'japanese B encephalitis']
	},
	'japEnc-live': {
		'name': u'flavivirus, japanese, live, attenuated',
		'atc4target': u'J07BA0J',		# fake
		'target': _(u'J07BA0J-target::japanese encephalitis'),
		'v21_indications_live': [u'japanese B encephalitis']
	},

	'influ-inact': {
		'name': u'influenza, inactivated',
		'atc4target': u'J07BB0',
		'target': _(u'J07BB0-target::influenza'),
		'v21_indications': [u'influenza (seasonal)', u'influenza (H3N2)', u'influenza (H1N1)']
	},
#	'influ-inact-surf': {
#		'name': u'influenza, inactivated, surface',
#		'atc4target': u'J07BB0',
#		'target': _(u'J07BB0-target::influenza')
#	},
	'influ-live': {
		'name': u'influenza, live, attenuated',
		'atc4target': u'J07BB0',
		'target': _(u'J07BB0-target::influenza'),
		'v21_indications_live': [u'influenza (seasonal)', u'influenza (H3N2)', u'influenza (H1N1)']
	},

	'hepB': {
		'name': u'hepatitis B antigen',
		'atc4target': u'J07BC01',
		'target': _(u'J07BC01-target::hepatitis B'),
		'v21_indications': [u'hepatitis B']
	},

	'hepA-inact': {
		'name': u'hepatitis A, inactivated',
		'atc4target': u'J07BC0',	# 02
		'target': _(u'J07BC0-target::hepatitis A'),
		'v21_indications': [u'hepatitis A']
	},
#	'hepA-antig': {
#		'name': u'hepatitis A antigen',
#		'atc4target': u'J07BC0', # 03
#		'target': _(u'J07BC0-target::hepatitis A')
#	},

	'measles-live': {
		'name': u'measles, live, attenuated',
		'atc4target': u'J07BD01',
		'target': _(u'J07BD01-target::measles'),
		'v21_indications_live': [u'measles']
	},

	'mumps-live': {
		'name': u'mumps, live, attenuated',
		'atc4target': u'J07BE01',
		'target': _(u'J07BE01-target::mumps'),
		'v21_indications_live': [u'mumps']
	},

	'polio-live': {
		'name': u'poliomyelitis, live, attenuated',
		'atc4target': u'J07BF0',	# 01
		'target': _(u'J07BF0-target::poliomyelitis'),
		'v21_indications_live': [u'poliomyelitis']
	},
	'polio-inact': {
		'name': u'poliomyelitis, inactivated',
		'atc4target': u'J07BF0',
		'target': _(u'J07BF0-target::poliomyelitis'),
		'v21_indications': [u'poliomyelitis']
	},

	'rabies': {
		'name': u'rabies, inactivated',
		'atc4target': u'J07BG01',
		'target': _(u'J07BG01-target::rabies'),
		'v21_indications': [u'rabies']
	},

	'rota-live-atten': {
		'name': u'rotavirus, live, attenuated',
		'atc4target': u'J07BH0',		# 01
		'target': _(u'J07BH0-target::rotavirus diarrhea')
	},
#	'rota-live': {
#		'name': u'rotavirus, live',
#		'atc4target': u'J07BH0',		# 02
#		'target': _(u'J07BH0-target::rotavirus diarrhea'),
#		'v21_indications_live': [u'rotavirus']
#	},

	'rubella-live': {
		'name': u'rubella, live',
		'atc4target': u'J07BJ01',
		'target': _(u'J07BJ01-target::rubella'),
		'v21_indications_live': [u'rubella']
	},

	'chickenpox-live': {
		'name': u'herpes virus (chickenpox), live',
		'atc4target': u'J07BK0',	# 01
		'target': _(u'J07BK0-target::varicella (chickenpox)'),
		'v21_indications_live': [u'varicella (chickenpox, shingles)']
	},
	'shingles-live': {
		'name': u'herpes virus (shingles), live',
		'atc4target': u'J07BK0',	# 02
		'target': _(u'J07BK0-target::zoster (shingles)')
	},

	'yellow_fever-live': {
		'name': u'yellow fever virus, live',
		'atc4target': u'J07BL01',
		'target': _(u'J07BL01-target::yellow fever'),
		'v21_indications_live': [u'yellow fever']
	},

	'pap-generic': {		# fake
		'name': u'papillomavirus',
		'atc4target': u'J07BM0',
		'target': _(u'J07BM0-target::HPV'),
		'v21_indications': [u'human papillomavirus']
	},
	'pap6-11-16-18': {
		'name': u'papillomavirus 6,11,16,18',
		'atc4target': u'J07BM01',
		'target': _(u'J07BM01-target::HPV')
	},
	'pap16-18': {
		'name': u'papillomavirus 16,18',
		'atc4target': u'J07BM02',
		'target': _(u'J07BM02-target::HPV')
	},
	'pap6-11-16-18-31-33-45-52-58': {
		'name': u'papillomavirus 6,11,16,18,31,33,45,52,58',
		'atc4target': u'J07BM03',
		'target': _(u'J07BM03-target::HPV')
	},

	'smallpox': {
		'name': u'variola virus, live',
		'atc4target': u'J07BX01',
		'target': _(u'J07BX01-target::variola (smallpox)'),
		'v21_indications_live': [u'variola virus (smallpox)']
	}

}

#------------------------------------------------------------
# J07 - vaccines
_GENERIC_VACCINES = {

	# J07A - antibacterial vaccines

	'anthrax': {
		'name': _(u'generic anthrax vaccine'),
		'atc': u'J07AC',
		'live': False,
		'ingredients': ['anthrax']
	},

	'brucellosis': {
		'name': _(u'generic brucellosis vaccine'),
		'atc': u'J07AD',
		'live': False,
		'ingredients': ['brucellosis']
	},

	'cholera': {
		'name': _(u'generic cholera vaccine'),
		'atc': u'J07AE01',
		'live': False,
		'ingredients': ['cholera']
	},
	'cholera, live': {
		'name': _(u'generic cholera vaccine, live'),
		'atc': u'J07AE02',
		'live': True,
		'ingredients': ['cholera-live']
	},

	'diphtheria': {
		'name': _(u'generic diphtheria vaccine'),
		'atc': u'J07AF',
		'live': False,
		'ingredients': ['diphtheria']
	},

	'HiB': {
		'name': _(u'generic HiB vaccine'),
		'atc': u'J07AG',
		'live': False,
		'ingredients': ['HiB']
	},

	'meningococcus A': {
		'name': _(u'generic meningococcus A vaccine'),
		'atc': u'J07AH01',
		'live': False,
		# for generic vaccine do not differentiate between conjugated or not
		'ingredients': ['menA']
	},
	'meningococcus B': {
		'name': _(u'generic meningococcus B vaccine'),
		'atc': u'J07AH06',
		'live': False,
		# do not differentiate membrane vs multicomponent in generic vaccine
		'ingredients': ['menBmem']
	},
	'meningococcus C': {
		'name': _(u'generic meningococcus C vaccine'),
		'atc': u'J07AH',
		'live': False,
		'ingredients': ['menC']
	},

	'pertussis': {
		'name': _(u'generic pertussis vaccine'),
		'atc': u'J07AJ01',
		'live': False,
		'ingredients': ['pertussis']
	},

	'plague': {
		'name': _(u'generic plague vaccine'),
		'atc': u'J07AK',
		'live': False,
		'ingredients': ['plague']
	},

	'pneumococcus': {
		'name': _(u'generic pneumococcus vaccine'),
		'atc': u'J07AL0',
		'live': False,
		# for generic vaccine do not differentiate between conjugated or not
		'ingredients': ['pneumococcus']
	},

	'tetanus': {
		'name': _(u'generic tetanus vaccine'),
		'atc': u'J07AM',
		'live': False,
		'ingredients': ['tetanus']
	},

	'Tbc': {
		'name': _(u'generic Tbc vaccine'),
		'atc': u'J07AN',
		'live': True,
		'ingredients': ['tbc-live']
	},

	'typhoid': {
		'name': _(u'generic typhoid vaccine'),
		'atc': u'J07AP02',
		'live': False,
		'ingredients': ['salmo-inact']
	},
	'typhoid, live': {
		'name': _(u'generic typhoid vaccine, live'),
		'atc': u'J07AP01',
		'live': True,
		'ingredients': ['salmo-live']
	},
	'typhoid, paratyphus': {
		'name': _(u'generic typhoid/paratyphus vaccine'),
		'atc': u'J07AP10',
		'live': False,
		'ingredients': ['salmo-typh+ent']
	},

	'typhus exanthematicus': {
		'name': _(u'generic typhus exanthematicus vaccine'),
		'atc': u'J07AR',
		'live': False,
		'ingredients': ['typh-exanth']
	},

	'q fever': {
		'name': _(u'generic Q fever vaccine'),
		'atc': u'J07AXQF',
		'live': False,
		'ingredients': ['qfever']
	},

	# J07B - antiviral vaccines

	'tick-borne encephalitis': {
		'name': _(u'generic tick-borne encephalitis vaccine'),
		'atc': u'J07BA',
		'live': False,
		'ingredients': ['fsme']
	},

	'japanese encephalitis': {
		'name': _(u'generic japanese encephalitis vaccine'),
		'atc': u'J07BA02',
		'live': False,
		'ingredients': ['japEnc']
	},
	'japanese encephalitis, live': {
		'name': _(u'generic japanese encephalitis vaccine, live'),
		'atc': u'J07BA03',
		'live': True,
		'ingredients': ['japEnc-live']
	},

	'influenza': {
		'name': _(u'generic influenza vaccine'),
		'atc': u'J07BB01',
		'live': False,
		'ingredients': ['influ-inact']
	},
	'influenza, live': {
		'name': _(u'generic influenza vaccine, live'),
		'atc': u'J07BB03',
		'live': True,
		'ingredients': ['influ-live']
	},

	'hepatitis A': {
		'name': _(u'generic hepatitis A vaccine'),
		'atc': u'J07BC02',
		'live': False,
		'ingredients': ['hepA-inact']
	},

	'hepatitis B': {
		'name': _(u'generic hepatitis B vaccine'),
		'atc': u'J07BC01',
		'live': False,
		'ingredients': ['hepB']
	},

	'measles-live': {
		'name': _(u'generic measles vaccine, live'),
		'atc': u'J07BD',
		'live': True,
		'ingredients': ['measles-live']
	},

	'mumps-live': {
		'name': _(u'generic mumps vaccine, live'),
		'atc': u'J07BE',
		'live': True,
		'ingredients': ['mumps-live']
	},

	'poliomyelitis': {
		'name': _(u'generic poliomyelitis vaccine'),
		'atc': u'J07BF03',
		'live': False,
		'ingredients': ['polio-inact']
	},

	'poliomyelitis, live': {
		'name': _(u'generic poliomyelitis vaccine, live'),
		'atc': u'J07BF01',
		'live': True,
		'ingredients': ['polio-live']
	},

	'rabies': {
		'name': _(u'generic rabies vaccine'),
		'atc': u'J07BG',
		'live': False,
		'ingredients': ['rabies']
	},

	'rotavirus, live': {
		'name': _(u'generic rotavirus vaccine, live'),
		'atc': u'J07BH01',
		'live': True,
		'ingredients': ['rota-live-atten']
	},

	'rubella': {
		'name': _(u'generic rubella vaccine, live'),
		'atc': u'J07BJ',
		'live': True,
		'ingredients': ['rubella-live']
	},

	'varicella': {
		'name': _(u'generic varicella vaccine, live'),
		'atc': u'J07BK01',
		'live': True,
		'ingredients': ['chickenpox-live']
	},
	'zoster': {
		'name': _(u'generic zoster vaccine, live'),
		'atc': u'J07BK02',
		'live': True,
		'ingredients': ['shingles-live']
	},

	'yellow fever': {
		'name': _(u'generic yellow fever vaccine'),
		'atc': u'J07BL',
		'live': True,
		'ingredients': ['yellow_fever-live']
	},

	'HPV': {
		'name': _(u'generic HPV vaccine'),
		'atc': u'J07BM',
		'live': False,
		'ingredients': ['pap-generic']
	},

	'variola': {
		'name': _(u'generic variola vaccine, live'),
		'atc': u'J07BX01',
		'live': True,
		'ingredients': ['smallpox']
	},

	# combinations

	'meningococcus AC': {
		'name': _(u'generic meningococcus AC vaccine'),
		'atc': u'J07AH03',
		'live': False,
		'ingredients': ['menA', 'menC']
	},
	'meningococcus ACYW135': {
		'name': _(u'generic meningococcus ACYW135 vaccine'),
		'atc': u'J07AH04', # 4/8
		'live': False,
		'ingredients': ['menA', 'menC', 'menY', 'menW']
	},

	'measles, mumps': {
		'name': _(u'generic measles-mumps vaccine, live'),
		'atc': u'J07BD51',
		'live': True,
		'ingredients': ['measles-live', 'mumps-live']
	},

	'measles, mumps, rubella': {
		'name': _(u'generic MMR vaccine, live'),
		'atc': u'J07BD52',
		'live': True,
		'ingredients': ['measles-live', 'mumps-live', 'rubella-live']
	},

	'measles, mumps, rubella, varicella': {
		'name': _(u'generic MMRV vaccine, live'),
		'atc': u'J07BD54',
		'live': True,
		'ingredients': ['measles-live', 'mumps-live', 'rubella-live', 'chickenpox-live']
	},

	'measles, rubella': {
		'name': _(u'generic measles-rubella vaccine, live'),
		'atc': u'J07BD53',
		'live': True,
		'ingredients': ['measles-live', 'rubella-live']
	},

	'mumps, rubella': {
		'name': _(u'generic mumps-rubella vaccine, live'),
		'atc': u'J07BJ51',
		'live': True,
		'ingredients': ['mumps-live', 'rubella-live']
	},

	'cholera, typhoid': {
		'name': _(u'generic cholera-typhoid vaccine'),
		'atc': u'J07AE51',
		'live': False,
		'ingredients': ['cholera', 'salmo-inact']
	},

	'typhoid, hepatitis A': {
		'name': _(u'generic typhoid-hepA vaccine'),
		'atc': u'J07CA10',
		'live': False,
		'ingredients': ['salmo-inact', 'hepA-inact']
	},

	'tetanus, diphtheria': {
		'name': _(u'generic Td vaccine'),
		'atc': u'J07AM51',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria']
	},
#	'Diphtheria, tetanus': {
#		'name': _(u'generic DT vaccine'),
#		'atc': u'J07AM51',
#		'live': False,
#		'ingredients': ['diphtheria', 'tetanus']
#	},
	#J07AM52,,"Tetanus-Toxoid, Kombinationen mit Tetanus-Immunglobulin",,,,,,

	'tetanus, diphtheria, poliomyelitis': {
		'name': _(u'generic TdPol vaccine'),
		'atc': u'J07CA01',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'polio-inact']
	},
	'tetanus, diphtheria, poliomyelitis': {
		'name': _(u'generic DTPol vaccine'),
		'atc': u'J07CA01',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'polio-inact']
	},

	'tetanus, diphtheria, HepB': {
		'name': _(u'generic Td-HepB vaccine'),
		'atc': u'J07CA07',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'hepB']
	},

	'tetanus, diphtheria, rubella': {
		'name': _(u'generic Td-rubella vaccine'),
		'atc': u'J07CA03',
		'live': True,
		'ingredients': ['tetanus', 'diphtheria', 'rubella-live']
	},

	'tetanus, diphtheria, pertussis, poliomyelitis': {
		'name': _(u'generic TdaPPol vaccine'),
		'atc': u'J07CA02',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'polio-inact']
	},

	'tetanus, diphtheria, pertussis, HepB': {
		'name': _(u'generic TdaP-HepB vaccine'),
		'atc': u'J07CA05',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'hepB']
	},

	'tetanus, diphtheria, pertussis': {
		'name': _(u'generic TdaP vaccine'),
		'atc': u'J07CA',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis']
	},

	'tetanus, diphtheria, pertussis, poliomyelitis, HiB': {
		'name': _(u'generic DTaPPol-Hib vaccine'),
		'atc': u'J07CA06',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'polio-inact', 'HiB']
	},

	'tetanus, diphtheria, pertussis, HiB, HepB': {
		'name': _(u'generic TdaP-Hib-HepB vaccine'),
		'atc': u'J07CA11',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'HiB', 'hepB']
	},

	'tetanus, diphtheria, pertussis, poliomyelitis, HepB': {
		'name': _(u'generic TdaPPol-HepB vaccine'),
		'atc': u'J07CA12',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'polio-inact', 'hepB']
	},

	'tetanus, diphtheria, pertussis, poliomyelitis, HiB, HepB': {
		'name': _(u'generic TdaPPol-HiB-HepB vaccine'),
		'atc': u'J07CA09',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'polio-inact', 'HiB', 'hepB']
	},

	'tetanus, diphtheria, pertussis, poliomyelitis, HiB, HepB, MenAC': {
		'name': _(u'generic TdaPPol-HiB-HepB-MenAC vaccine'),
		'atc': u'J07CA13',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'polio-inact', 'HiB', 'hepB', 'menA', 'menC']
	}

}

#------------------------------------------------------------
u"""
# single

J07AX  ,,Andere bakterielle Impfstoffe,,,,,,
J07AX01,,Lactobacillus acidophilus,,,,,,
J07AX52,,"Lactobacillus Stämme, Kombinationen",,Standarddosis: 1 Einzeldosis P ,,,,
J07AX53,,"Enterobacteriacae Stämme, Kombinationen",,Standarddosis: 1 Einzeldosis P ,,,,

J07BX  ,,Andere virale Impfstoffe,,,,,,
J07BX02,,Inaktiviertes Herpes-simplex-Virus,,Standarddosis: 1 Einzeldosis P ,,,,

J07X   ,,ANDERE IMPFSTOFFE,,,,,,

J07AH05,,"Andere Meningokokken polyvalent, gereinigtes Polysaccharid-Antigen",,,,,,

# combi

J07AG51,,"Haemophilus influenzae B, Kombinationen mit Toxoiden",,Standarddosis: 1 Einzeldosis P ,,,,
J07AG52,,"Haemophilus influenzae B, Kombinationen mit Pertussis und Toxoiden",,Standarddosis: 1 Einzeldosis P ,,,,
J07AG53,,"Haemophilus influenzae B, Kombinationen mit Meningokokken C, konjugiert",,,,,,

J07AJ51,,"Pertussis, inaktiviert, ganze Zelle, Kombinationen mit Toxoiden",,,,,,
J07AJ52,,"Pertussis, gereinigtes Antigen, Kombinationen mit Toxoiden",,Standarddosis: 1 Einzeldosis P ,,,,

J07AL52,,"Pneumokokken, gereinigtes Polysaccharid-Antigen und Haemophilus influenzae B, konjugiert",,Standarddosis: 1 Einzeldosis P ,,,,

Hep: J07BC20,,Kombinationen,,Standarddosis: 1 Einzeldosis P ,,,,

J07CA04,,Haemophilus influenzae B und Poliomyelitis,,,,,,

J07CA08,,Haemophilus influenzae B und Hepatitis B,,Standarddosis: 1 Einzeldosis P ,,,,

	'': {
		'name': _(u'generic NNN vaccine'),
		'atc': u'',
		'live': True/False,
		'ingredients': [u'']
	},
"""

#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()


	def print_substs():
		for moniker in _VACCINE_SUBSTANCES.keys():
			subst = _VACCINE_SUBSTANCES[moniker]
			print(moniker)
			print(' substance:', subst['name'])
			print(' target:', subst['target'])


	def print_vaccs():
		for key in _GENERIC_VACCINES:
			vacc = _GENERIC_VACCINES[key]
			print(u'vaccine "%s" (ATC %s)' % (vacc['name'], vacc['atc']))
			for key in vacc['ingredients']:
				subst = _VACCINE_SUBSTANCES[key]
				atc = subst['atc4target']
				print(' contains: %s (ATC %s)' % (subst['name'], atc))
				print('  protects against: "%s" [%s]' % (_(subst['target']).lstrip(u'%s-target::' % atc), subst['target']))


	print_vaccs()
