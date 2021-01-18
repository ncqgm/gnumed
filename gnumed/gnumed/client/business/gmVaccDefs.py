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
from Gnumed.pycommon import gmI18N
if __name__ == '__main__':
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')


_log = logging.getLogger('gm.vacc')

#============================================================
_VACCINE_SUBSTANCES = {

	# bacterial

	'anthrax': {
		'name': 'bacillus anthracis antigen',
		'atc4target': 'J07AC01',
		'target': _('J07AC01-target::anthrax'),
		'v21_indications': ['bacillus anthracis (Anthrax)']
	},

	'brucellosis': {
		'name': 'brucella antigen',
		'atc4target': 'J07AD01',
		'target': _('J07AD01-target::brucellosis')
	},

	'cholera': {
		'name': 'cholera, inactivated',
		'atc4target': 'J07AE0',
		'target': _('J07AE0-target::cholera'),
		'v21_indications': ['cholera']
	},
	'cholera-live': {
		'name': 'cholera, live, attenuated',
		'atc4target': 'J07AE0',
		'target': _('J07AE0-target::cholera'),
		'v21_indications_live': ['cholera']
	},

	'diphtheria': {
		'name': 'diphtheria toxoid',
		'atc4target': 'J07AF01',
		'target': _('J07AF01-target::diphtheria'),
		'v21_indications': ['diphtheria']
	},

	'HiB': {
		'name': 'hemophilus influenzae B antigen',
		'atc4target': 'J07AG01',
		'target': _('J07AG01-target::HiB'),
		'v21_indications': ['haemophilus influenzae b']
	},

	'menA': {
		'name': 'meningococcus A antigen',
		'atc4target': 'J07AH01',
		'target': _('J07AH01-target::meningococcus A'),
		'v21_indications': ['meningococcus A']
	},
#	'menA-conj': {
#		'name': u'meningococcus A antigen, conjugated',
#		'atc4target': u'J07AH10',
#		'target': _(u'J07AH10-target::meningococcus A')
#	},
	'menBmem': {
		'name': 'meningococcus B membrane',
		'atc4target': 'J07AH06',
		'target': _('J07AH06-target::meningococcus B')
	},
#	'menBmulti': {
#		'name': u'meningococcus B multicomponent',
#		'atc4target': u'J07AH09',
#		'target': _(u'J07AH09-target::meningococcus B'),
#	},
	'menC': {
		'name': 'meningococcus C antigen',
		'atc4target': 'J07AH07',
		'target': _('J07AH07-target::meningococcus C'),
		'v21_indications': ['meningococcus C']
	},
	'menY': {		# fake
		'name': 'meningococcus Y antigen',
		'atc4target': 'J07AH0Y',
		'target': _('J07AH0Y-target::meningococcus Y'),
		'v21_indications': ['meningococcus Y']
	},
	'menW': {		# fake
		'name': 'meningococcus W-135 antigen',
		'atc4target': 'J07AH0W',
		'target': _('J07AH0W-target::meningococcus W'),
		'v21_indications': ['meningococcus W']
	},

	'pertussis': {		# fake
		'name': 'pertussis',
		'atc4target': 'J07AJ0',
		'target': _('J07AJ0-target::pertussis'),
		'v21_indications': ['pertussis']
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
		'name': 'yersinia pestis, inactivated',
		'atc4target': 'J07AK01',
		'target': _('J07AK01-target::plague'),
		'v21_indications': ['yersinia pestis']
	},

	'pneumococcus': {
		'name': 'pneumococcus antigen',
		'atc4target': 'J07AL0',
		'target': _('J07AL0-target::pneumococcus'),
		'v21_indications': ['pneumococcus']
	},
#	'pneumococcus-conjugated': {
#		'name': u'pneumococcus antigen, conjugated',
#		'atc4target': u'J07AL02',
#		'target': _(u'J07AL02-target::pneumococcus'),
#	},

	'tetanus': {
		'name': 'tetanus toxoid',
		'atc4target': 'J07AM01',
		'target': _('J07AM01-target::tetanus'),
		'v21_indications': ['tetanus']
	},

	'tbc-live': {
		'name': 'tuberculosis, live, attenuated',
		'atc4target': 'J07AN01',
		'target': _('J07AN01-target::tbc'),
		'v21_indications_live': ['tuberculosis']
	},

	'salmo-live': {
		'name': 'salmonella typhi, live, attenuated',
		'atc4target': 'J07AP0',
		'target': _('J07AP0-target::typhoid'),
		'v21_indications_live': ['salmonella typhi (typhoid)']
	},
	'salmo-inact': {
		'name': 'salmonella typhi, inactivated',
		'atc4target': 'J07AP0',
		'target': _('J07AP0-target::typhoid')
	},
#	'salmo-antigen': {
#		'name': u'salmonella typhi antigen',
#		'atc4target': u'J07AP03',
#		'target': _(u'J07AP03-target::typhoid')
#	},
	'salmo-typh+ent': {
		'name': 'salmonella typhi, enterica',
		'atc4target': 'J07AP1',
		'target': _('J07AP1-target::typhoid, paratyphus'),
		'v21_indications': ['salmonella typhi (typhoid)']
	},

	'typh-exanth': {
		'name': 'rickettsia prowazekii, inactivated',
		'atc4target': 'J07AR01',
		'target': _('J07AR01-target::typhus exanthematicus')
	},

	'qfever': {		# fake
		'name': 'coxiella burnetii',
		'atc4target': 'J07AXQF',
		'target': _('J07AXQF-target::Q fever'),
		'v21_indications': ['coxiella burnetii (Q fever)']
	},

	# viral
	'sars-cov-2-mrna': {
		'name': 'SARS-CoV-2 spike protein mRNA',
		'atc4target': 'J07BX03',
		'target': _('J07BX03-target::CoViD-2019')
	},

	'fsme': {
		'name': 'flavivirus, tick-borne',
		'atc4target': 'J07BA01',
		'target': _('J07BA01-target::tick-borne encephalitis'),
		'v21_indications': ['tick-borne meningoencephalitis']
	},

	'japEnc': {
		'name': 'flavivirus, japanese',
		'atc4target': 'J07BA0J',		# fake
		'target': _('J07BA0J-target::japanese encephalitis'),
		'v21_indications': ['japanese B encephalitis']
	},
	'japEnc-live': {
		'name': 'flavivirus, japanese, live, attenuated',
		'atc4target': 'J07BA0J',		# fake
		'target': _('J07BA0J-target::japanese encephalitis'),
		'v21_indications_live': ['japanese B encephalitis']
	},

	'influ-inact': {
		'name': 'influenza, inactivated',
		'atc4target': 'J07BB0',
		'target': _('J07BB0-target::influenza'),
		'v21_indications': ['influenza (seasonal)', 'influenza (H3N2)', 'influenza (H1N1)']
	},
#	'influ-inact-surf': {
#		'name': u'influenza, inactivated, surface',
#		'atc4target': u'J07BB0',
#		'target': _(u'J07BB0-target::influenza')
#	},
	'influ-live': {
		'name': 'influenza, live, attenuated',
		'atc4target': 'J07BB0',
		'target': _('J07BB0-target::influenza'),
		'v21_indications_live': ['influenza (seasonal)', 'influenza (H3N2)', 'influenza (H1N1)']
	},

	'hepB': {
		'name': 'hepatitis B antigen',
		'atc4target': 'J07BC01',
		'target': _('J07BC01-target::hepatitis B'),
		'v21_indications': ['hepatitis B']
	},

	'hepA-inact': {
		'name': 'hepatitis A, inactivated',
		'atc4target': 'J07BC0',	# 02
		'target': _('J07BC0-target::hepatitis A'),
		'v21_indications': ['hepatitis A']
	},
#	'hepA-antig': {
#		'name': u'hepatitis A antigen',
#		'atc4target': u'J07BC0', # 03
#		'target': _(u'J07BC0-target::hepatitis A')
#	},

	'measles-live': {
		'name': 'measles, live, attenuated',
		'atc4target': 'J07BD01',
		'target': _('J07BD01-target::measles'),
		'v21_indications_live': ['measles']
	},

	'mumps-live': {
		'name': 'mumps, live, attenuated',
		'atc4target': 'J07BE01',
		'target': _('J07BE01-target::mumps'),
		'v21_indications_live': ['mumps']
	},

	'polio-live': {
		'name': 'poliomyelitis, live, attenuated',
		'atc4target': 'J07BF0',	# 01
		'target': _('J07BF0-target::poliomyelitis'),
		'v21_indications_live': ['poliomyelitis']
	},
	'polio-inact': {
		'name': 'poliomyelitis, inactivated',
		'atc4target': 'J07BF0',
		'target': _('J07BF0-target::poliomyelitis'),
		'v21_indications': ['poliomyelitis']
	},

	'rabies': {
		'name': 'rabies, inactivated',
		'atc4target': 'J07BG01',
		'target': _('J07BG01-target::rabies'),
		'v21_indications': ['rabies']
	},

	'rota-live-atten': {
		'name': 'rotavirus, live, attenuated',
		'atc4target': 'J07BH0',		# 01
		'target': _('J07BH0-target::rotavirus diarrhea')
	},
#	'rota-live': {
#		'name': u'rotavirus, live',
#		'atc4target': u'J07BH0',		# 02
#		'target': _(u'J07BH0-target::rotavirus diarrhea'),
#		'v21_indications_live': [u'rotavirus']
#	},

	'rubella-live': {
		'name': 'rubella, live',
		'atc4target': 'J07BJ01',
		'target': _('J07BJ01-target::rubella'),
		'v21_indications_live': ['rubella']
	},

	'chickenpox-live': {
		'name': 'herpes virus (chickenpox), live',
		'atc4target': 'J07BK0',	# 01
		'target': _('J07BK0-target::varicella (chickenpox)'),
		'v21_indications_live': ['varicella (chickenpox, shingles)']
	},
	'shingles-live': {
		'name': 'herpes virus (shingles), live',
		'atc4target': 'J07BK0',	# 02
		'target': _('J07BK0-target::zoster (shingles)')
	},

	'yellow_fever-live': {
		'name': 'yellow fever virus, live',
		'atc4target': 'J07BL01',
		'target': _('J07BL01-target::yellow fever'),
		'v21_indications_live': ['yellow fever']
	},

	'pap-generic': {		# fake
		'name': 'papillomavirus',
		'atc4target': 'J07BM0',
		'target': _('J07BM0-target::HPV'),
		'v21_indications': ['human papillomavirus']
	},
	'pap6-11-16-18': {
		'name': 'papillomavirus 6,11,16,18',
		'atc4target': 'J07BM01',
		'target': _('J07BM01-target::HPV')
	},
	'pap16-18': {
		'name': 'papillomavirus 16,18',
		'atc4target': 'J07BM02',
		'target': _('J07BM02-target::HPV')
	},
	'pap6-11-16-18-31-33-45-52-58': {
		'name': 'papillomavirus 6,11,16,18,31,33,45,52,58',
		'atc4target': 'J07BM03',
		'target': _('J07BM03-target::HPV')
	},

	'smallpox': {
		'name': 'variola virus, live',
		'atc4target': 'J07BX01',
		'target': _('J07BX01-target::variola (smallpox)'),
		'v21_indications_live': ['variola virus (smallpox)']
	}

}

#------------------------------------------------------------
# J07 - vaccines
_GENERIC_VACCINES = {

	# J07A - antibacterial vaccines

	'anthrax': {
		'name': _('generic anthrax vaccine'),
		'atc': 'J07AC',
		'live': False,
		'ingredients': ['anthrax']
	},

	'brucellosis': {
		'name': _('generic brucellosis vaccine'),
		'atc': 'J07AD',
		'live': False,
		'ingredients': ['brucellosis']
	},

	'cholera': {
		'name': _('generic cholera vaccine'),
		'atc': 'J07AE01',
		'live': False,
		'ingredients': ['cholera']
	},
	'cholera, live': {
		'name': _('generic cholera vaccine, live'),
		'atc': 'J07AE02',
		'live': True,
		'ingredients': ['cholera-live']
	},

	'diphtheria': {
		'name': _('generic diphtheria vaccine'),
		'atc': 'J07AF',
		'live': False,
		'ingredients': ['diphtheria']
	},

	'HiB': {
		'name': _('generic HiB vaccine'),
		'atc': 'J07AG',
		'live': False,
		'ingredients': ['HiB']
	},

	'meningococcus A': {
		'name': _('generic meningococcus A vaccine'),
		'atc': 'J07AH01',
		'live': False,
		# for generic vaccine do not differentiate between conjugated or not
		'ingredients': ['menA']
	},
	'meningococcus B': {
		'name': _('generic meningococcus B vaccine'),
		'atc': 'J07AH06',
		'live': False,
		# do not differentiate membrane vs multicomponent in generic vaccine
		'ingredients': ['menBmem']
	},
	'meningococcus C': {
		'name': _('generic meningococcus C vaccine'),
		'atc': 'J07AH',
		'live': False,
		'ingredients': ['menC']
	},

	'pertussis': {
		'name': _('generic pertussis vaccine'),
		'atc': 'J07AJ01',
		'live': False,
		'ingredients': ['pertussis']
	},

	'plague': {
		'name': _('generic plague vaccine'),
		'atc': 'J07AK',
		'live': False,
		'ingredients': ['plague']
	},

	'pneumococcus': {
		'name': _('generic pneumococcus vaccine'),
		'atc': 'J07AL0',
		'live': False,
		# for generic vaccine do not differentiate between conjugated or not
		'ingredients': ['pneumococcus']
	},

	'tetanus': {
		'name': _('generic tetanus vaccine'),
		'atc': 'J07AM',
		'live': False,
		'ingredients': ['tetanus']
	},

	'Tbc': {
		'name': _('generic Tbc vaccine'),
		'atc': 'J07AN',
		'live': True,
		'ingredients': ['tbc-live']
	},

	'typhoid': {
		'name': _('generic typhoid vaccine'),
		'atc': 'J07AP02',
		'live': False,
		'ingredients': ['salmo-inact']
	},
	'typhoid, live': {
		'name': _('generic typhoid vaccine, live'),
		'atc': 'J07AP01',
		'live': True,
		'ingredients': ['salmo-live']
	},
	'typhoid, paratyphus': {
		'name': _('generic typhoid/paratyphus vaccine'),
		'atc': 'J07AP10',
		'live': False,
		'ingredients': ['salmo-typh+ent']
	},

	'typhus exanthematicus': {
		'name': _('generic typhus exanthematicus vaccine'),
		'atc': 'J07AR',
		'live': False,
		'ingredients': ['typh-exanth']
	},

	'q fever': {
		'name': _('generic Q fever vaccine'),
		'atc': 'J07AXQF',
		'live': False,
		'ingredients': ['qfever']
	},

	# J07B - antiviral vaccines

	'tick-borne encephalitis': {
		'name': _('generic tick-borne encephalitis vaccine'),
		'atc': 'J07BA',
		'live': False,
		'ingredients': ['fsme']
	},

	'CoViD-2019': {
		'name': _('generic CoViD-2019 vaccine'),
		'atc': 'J07BX03',
		'live': False,
		'ingredients': ['sars-cov-2-mrna']
	},

	'japanese encephalitis': {
		'name': _('generic japanese encephalitis vaccine'),
		'atc': 'J07BA02',
		'live': False,
		'ingredients': ['japEnc']
	},
	'japanese encephalitis, live': {
		'name': _('generic japanese encephalitis vaccine, live'),
		'atc': 'J07BA03',
		'live': True,
		'ingredients': ['japEnc-live']
	},

	'influenza': {
		'name': _('generic influenza vaccine'),
		'atc': 'J07BB01',
		'live': False,
		'ingredients': ['influ-inact']
	},
	'influenza, live': {
		'name': _('generic influenza vaccine, live'),
		'atc': 'J07BB03',
		'live': True,
		'ingredients': ['influ-live']
	},

	'hepatitis A': {
		'name': _('generic hepatitis A vaccine'),
		'atc': 'J07BC02',
		'live': False,
		'ingredients': ['hepA-inact']
	},

	'hepatitis B': {
		'name': _('generic hepatitis B vaccine'),
		'atc': 'J07BC01',
		'live': False,
		'ingredients': ['hepB']
	},

	'measles-live': {
		'name': _('generic measles vaccine, live'),
		'atc': 'J07BD',
		'live': True,
		'ingredients': ['measles-live']
	},

	'mumps-live': {
		'name': _('generic mumps vaccine, live'),
		'atc': 'J07BE',
		'live': True,
		'ingredients': ['mumps-live']
	},

	'poliomyelitis': {
		'name': _('generic poliomyelitis vaccine'),
		'atc': 'J07BF03',
		'live': False,
		'ingredients': ['polio-inact']
	},

	'poliomyelitis, live': {
		'name': _('generic poliomyelitis vaccine, live'),
		'atc': 'J07BF01',
		'live': True,
		'ingredients': ['polio-live']
	},

	'rabies': {
		'name': _('generic rabies vaccine'),
		'atc': 'J07BG',
		'live': False,
		'ingredients': ['rabies']
	},

	'rotavirus, live': {
		'name': _('generic rotavirus vaccine, live'),
		'atc': 'J07BH01',
		'live': True,
		'ingredients': ['rota-live-atten']
	},

	'rubella': {
		'name': _('generic rubella vaccine, live'),
		'atc': 'J07BJ',
		'live': True,
		'ingredients': ['rubella-live']
	},

	'varicella': {
		'name': _('generic varicella vaccine, live'),
		'atc': 'J07BK01',
		'live': True,
		'ingredients': ['chickenpox-live']
	},
	'zoster': {
		'name': _('generic zoster vaccine, live'),
		'atc': 'J07BK02',
		'live': True,
		'ingredients': ['shingles-live']
	},

	'yellow fever': {
		'name': _('generic yellow fever vaccine'),
		'atc': 'J07BL',
		'live': True,
		'ingredients': ['yellow_fever-live']
	},

	'HPV': {
		'name': _('generic HPV vaccine'),
		'atc': 'J07BM',
		'live': False,
		'ingredients': ['pap-generic']
	},

	'variola': {
		'name': _('generic variola vaccine, live'),
		'atc': 'J07BX01',
		'live': True,
		'ingredients': ['smallpox']
	},

	# combinations

	'meningococcus AC': {
		'name': _('generic meningococcus AC vaccine'),
		'atc': 'J07AH03',
		'live': False,
		'ingredients': ['menA', 'menC']
	},
	'meningococcus ACYW135': {
		'name': _('generic meningococcus ACYW135 vaccine'),
		'atc': 'J07AH04', # 4/8
		'live': False,
		'ingredients': ['menA', 'menC', 'menY', 'menW']
	},

	'measles, mumps': {
		'name': _('generic measles-mumps vaccine, live'),
		'atc': 'J07BD51',
		'live': True,
		'ingredients': ['measles-live', 'mumps-live']
	},

	'measles, mumps, rubella': {
		'name': _('generic MMR vaccine, live'),
		'atc': 'J07BD52',
		'live': True,
		'ingredients': ['measles-live', 'mumps-live', 'rubella-live']
	},

	'measles, mumps, rubella, varicella': {
		'name': _('generic MMRV vaccine, live'),
		'atc': 'J07BD54',
		'live': True,
		'ingredients': ['measles-live', 'mumps-live', 'rubella-live', 'chickenpox-live']
	},

	'measles, rubella': {
		'name': _('generic measles-rubella vaccine, live'),
		'atc': 'J07BD53',
		'live': True,
		'ingredients': ['measles-live', 'rubella-live']
	},

	'mumps, rubella': {
		'name': _('generic mumps-rubella vaccine, live'),
		'atc': 'J07BJ51',
		'live': True,
		'ingredients': ['mumps-live', 'rubella-live']
	},

	'cholera, typhoid': {
		'name': _('generic cholera-typhoid vaccine'),
		'atc': 'J07AE51',
		'live': False,
		'ingredients': ['cholera', 'salmo-inact']
	},

	'typhoid, hepatitis A': {
		'name': _('generic typhoid-hepA vaccine'),
		'atc': 'J07CA10',
		'live': False,
		'ingredients': ['salmo-inact', 'hepA-inact']
	},

	'tetanus, diphtheria': {
		'name': _('generic Td vaccine'),
		'atc': 'J07AM51',
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
		'name': _('generic TdPol vaccine'),
		'atc': 'J07CA01',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'polio-inact']
	},
	'tetanus, diphtheria, poliomyelitis': {
		'name': _('generic DTPol vaccine'),
		'atc': 'J07CA01',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'polio-inact']
	},

	'tetanus, diphtheria, HepB': {
		'name': _('generic Td-HepB vaccine'),
		'atc': 'J07CA07',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'hepB']
	},

	'tetanus, diphtheria, rubella': {
		'name': _('generic Td-rubella vaccine'),
		'atc': 'J07CA03',
		'live': True,
		'ingredients': ['tetanus', 'diphtheria', 'rubella-live']
	},

	'tetanus, diphtheria, pertussis, poliomyelitis': {
		'name': _('generic TdaPPol vaccine'),
		'atc': 'J07CA02',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'polio-inact']
	},

	'tetanus, diphtheria, pertussis, HepB': {
		'name': _('generic TdaP-HepB vaccine'),
		'atc': 'J07CA05',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'hepB']
	},

	'tetanus, diphtheria, pertussis': {
		'name': _('generic TdaP vaccine'),
		'atc': 'J07CA',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis']
	},

	'tetanus, diphtheria, pertussis, poliomyelitis, HiB': {
		'name': _('generic DTaPPol-Hib vaccine'),
		'atc': 'J07CA06',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'polio-inact', 'HiB']
	},

	'tetanus, diphtheria, pertussis, HiB, HepB': {
		'name': _('generic TdaP-Hib-HepB vaccine'),
		'atc': 'J07CA11',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'HiB', 'hepB']
	},

	'tetanus, diphtheria, pertussis, poliomyelitis, HepB': {
		'name': _('generic TdaPPol-HepB vaccine'),
		'atc': 'J07CA12',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'polio-inact', 'hepB']
	},

	'tetanus, diphtheria, pertussis, poliomyelitis, HiB, HepB': {
		'name': _('generic TdaPPol-HiB-HepB vaccine'),
		'atc': 'J07CA09',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'polio-inact', 'HiB', 'hepB']
	},

	'tetanus, diphtheria, pertussis, poliomyelitis, HiB, HepB, MenAC': {
		'name': _('generic TdaPPol-HiB-HepB-MenAC vaccine'),
		'atc': 'J07CA13',
		'live': False,
		'ingredients': ['tetanus', 'diphtheria', 'pertussis', 'polio-inact', 'HiB', 'hepB', 'menA', 'menC']
	}

}

#------------------------------------------------------------
"""
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

	if sys.argv[1] != 'test':
		sys.exit()


	def print_substs():
		for moniker in _VACCINE_SUBSTANCES:
			subst = _VACCINE_SUBSTANCES[moniker]
			print(moniker)
			print(' substance:', subst['name'])
			print(' target:', subst['target'])


	def print_vaccs():
		for key in _GENERIC_VACCINES:
			vacc = _GENERIC_VACCINES[key]
			print('vaccine "%s" (ATC %s)' % (vacc['name'], vacc['atc']))
			for key in vacc['ingredients']:
				subst = _VACCINE_SUBSTANCES[key]
				atc = subst['atc4target']
				print(' contains: %s (ATC %s)' % (subst['name'], atc))
				print('  protects against: "%s" [%s]' % (_(subst['target']).lstrip('%s-target::' % atc), subst['target']))


	print_vaccs()
