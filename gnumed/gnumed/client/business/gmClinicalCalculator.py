# -*- coding: utf8 -*-
"""GNUmed clinical calculator(s)

THIS IS NOT A VERIFIED CALCULATOR. DO NOT USE FOR ACTUAL CARE.
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

# standard libs
import sys
import logging
import decimal


if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmLog2

if __name__ == '__main__':
	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

from Gnumed.pycommon import gmTools
from Gnumed.business import gmLOINC


_log = logging.getLogger('gm.calc')

#============================================================
class cClinicalResult(object):

	def __init__(self, message=None):
		self.message = message
		self.numeric_value = None
		self.unit = None
		self.date_valid = None
		self.variables = {}
		self.formula_name = None
		self.formula_source = None
		self.sub_results = []
		self.warnings = [_('THIS IS NOT A VERIFIED MEASUREMENT. DO NOT USE FOR ACTUAL CARE.')]

	def __unicode__(self):
		return u'[cClinicalResult]: name: %s\nsource: %s\nvalue: %s unit: %s, date: %s\nmsg: %s\nvars: %s\nwarnings: %s\nsub-results: %s' % (
			self.formula_name,
			self.formula_source,
			self.numeric_value,
			self.unit,
			self.date_valid,
			self.message,
			self.variables,
			self.warnings,
			self.sub_results
		)

#============================================================
class cClinicalCalculator(object):

	def __init__(self, patient=None):
		self.__cache = {}
		self.__patient = patient
	#--------------------------------------------------------
	def _get_patient(self):
		return self.__patient

	def _set_patient(self, patient):
		if patient == self.__patient:
			return
		self.__patient = patient
		self.remove_from_cache()			# uncache all values

	patient = property(lambda x:x, _set_patient)
	#--------------------------------------------------------
#	def suggest_algorithm(self, pk_test_type):
#		return None
	#--------------------------------------------------------
	def remove_from_cache(self, key=None):
		if key is None:
			self.__cache = {}
			return True
		try:
			del self.__cache[key]
			return True
		except KeyError:
			_log.error('key [%s] does not exist in cache', key)
			return False
	#--------------------------------------------------------
	# formulae
	#--------------------------------------------------------
	def _get_egfr(self):
		eGFR = self.eGFR_Schwartz
		if eGFR.numeric_value is None:
			eGFR = self.eGFR_MDRD_short
		return eGFR

	eGFR = property(_get_egfr, lambda x:x)
	#--------------------------------------------------------
	def _get_mdrd_short(self):

		try:
			return self.__cache['MDRD_short']
		except KeyError:
			pass

		result = cClinicalResult(_('unknown MDRD (4 vars/IDMS)'))
		result.formula_name = u'eGFR from 4-variables IDMS-MDRD'
		result.formula_source = u'1/2013: http://en.wikipedia.org/Renal_function / http://www.ganfyd.org/index.php?title=Estimated_glomerular_filtration_rate (NHS)'

		if self.__patient is None:
			result.message = _('MDRD (4 vars/IDMS): no patient')
			return result

		if self.__patient['dob'] is None:
			result.message = _('MDRD (4 vars/IDMS): no DOB (no age)')
			return result

		# 1) gender
		from Gnumed.business.gmPerson import map_gender2mf
		result.variables['gender'] = self.__patient['gender']
		result.variables['gender_mf'] = map_gender2mf[self.__patient['gender']]
		if result.variables['gender_mf'] == 'm':
			result.variables['gender_multiplier'] = self.d(1)
		elif result.variables['gender_mf'] == 'f':
			result.variables['gender_multiplier'] = self.d('0.742')
		else:
			result.message = _('MDRD (4 vars/IDMS): neither male nor female')
			return result

		# 2) creatinine
		result.variables['serum_crea'] = self.__patient.emr.get_most_recent_results(loinc = ['2160-0', '14682-9', '40264-4'], no_of_results = 1)
		if result.variables['serum_crea'] is None:
			result.message = _('MDRD (4 vars/IDMS): serum creatinine value not found (LOINC: 2160-0, 14682-9)')
			return result
		if result.variables['serum_crea']['val_num'] is None:
			result.message = _('MDRD (4 vars/IDMS): creatinine value not numeric')
			return result
		result.variables['serum_crea_val'] = self.d(result.variables['serum_crea']['val_num'])
		if result.variables['serum_crea']['val_unit'] in [u'mg/dl', u'mg/dL']:
			result.variables['unit_multiplier'] = self.d(175)						# older: 186
		elif result.variables['serum_crea']['val_unit'] in [u'µmol/L', u'µmol/l']:
			result.variables['unit_multiplier'] = self.d(30849)					# older: 32788
		else:
			result.message = _('MDRD (4 vars/IDMS): unknown serum creatinine unit (%s)') % result.variables['serum_crea']['val_unit']
			return result

		# 3) age (at creatinine evaluation)
		result.variables['dob'] = self.__patient['dob']
		result.variables['age@crea'] = self.d (
			gmDateTime.calculate_apparent_age (
				start = result.variables['dob'],
				end = result.variables['serum_crea']['clin_when']
			)[0]
		)
		if (result.variables['age@crea'] > 84) or (result.variables['age@crea'] < 18):
			result.message = _('MDRD (4 vars/IDMS): formula does not apply at age [%s] (17 < age < 85)') % result.variables['age@crea']
			return result

		# 4) ethnicity
		result.variables['ethnicity_multiplier'] = self.d(1)			# non-black
		result.warnings.append(_('ethnicity: GNUmed does not know patient ethnicity, ignoring correction factor'))

		# calculate
		result.numeric_value =  result.variables['unit_multiplier'] * \
			pow(result.variables['serum_crea_val'], self.d('-1.154')) * \
			pow(result.variables['age@crea'], self.d('-0.203')) * \
			result.variables['ethnicity_multiplier'] * \
			result.variables['gender_multiplier']
		result.unit = u'ml/min/1.73m²'

		BSA = self.body_surface_area
		result.sub_results.append(BSA)
		if BSA.numeric_value is None:
			result.warnings.append(_(u'NOT corrected for non-average body surface (average = 1.73m²)'))
		else:
			result.variables['BSA'] = BSA.numeric_value
			result_numeric_value = result.numeric_value / BSA.numeric_value

		result.message = _('eGFR(MDRD): %.2f %s (%s) [4-vars, IDMS]') % (
			result.numeric_value,
			result.unit,
			gmDateTime.pydt_strftime (
				result.variables['serum_crea']['clin_when'],
				format = '%Y %b %d'
			)
		)
		result.date_valid = result.variables['serum_crea']['clin_when']

		self.__cache['MDRD_short'] = result
		_log.debug(u'%s' % result)

		return result

	eGFR_MDRD_short = property(_get_mdrd_short, lambda x:x)
	#--------------------------------------------------------
	def _get_gfr_schwartz(self):

		try:
			return self.__cache['gfr_schwartz']
		except KeyError:
			pass

		result = cClinicalResult(_('unknown eGFR (Schwartz)'))
		result.formula_name = u'eGFR from updated Schwartz "bedside" formula (age < 19yrs)'
		result.formula_source = u'1/2013: http://en.wikipedia.org/Renal_function / http://www.ganfyd.org/index.php?title=Estimated_glomerular_filtration_rate (NHS) / doi 10.1681/ASN.2008030287 / doi: 10.2215/CJN.01640309'

		if self.__patient is None:
			result.message = _('eGFR (Schwartz): no patient')
			return result

		if self.__patient['dob'] is None:
			result.message = _('eGFR (Schwartz): DOB needed for age')
			return result

		result.variables['dob'] = self.__patient['dob']

		# creatinine
		result.variables['serum_crea'] = self.__patient.emr.get_most_recent_results(loinc = ['2160-0', '14682-9', '40264-4'], no_of_results = 1)
		if result.variables['serum_crea'] is None:
			result.message = _('eGFR (Schwartz): serum creatinine value not found (LOINC: 2160-0, 14682-9)')
			return result
		if result.variables['serum_crea']['val_num'] is None:
			result.message = _('eGFR (Schwartz): creatinine value not numeric')
			return result
		result.variables['serum_crea_val'] = self.d(result.variables['serum_crea']['val_num'])
		if result.variables['serum_crea']['val_unit'] in [u'mg/dl', u'mg/dL']:
			result.variables['unit_multiplier'] = self.d(1)
		elif result.variables['serum_crea']['val_unit'] in [u'µmol/L', u'µmol/l']:
			result.variables['unit_multiplier'] = self.d('0.00113')
		else:
			result.message = _('eGFR (Schwartz): unknown serum creatinine unit (%s)') % result.variables['serum_crea']['val_unit']
			return result

		# age
		result.variables['age@crea'] = self.d (
			gmDateTime.calculate_apparent_age (
				start = result.variables['dob'],
				end = result.variables['serum_crea']['clin_when']
			)[0]
		)
		if result.variables['age@crea'] > 17:
			result.message = _('eGFR (Schwartz): formula does not apply at age [%s] (age must be <18)') % result.variables['age@crea']
			return result

		# age-dependant constant
		if result.variables['age@crea'] < 1:
			# first year pre-term: k = 0.33
			# first year full-term: k = (0.45)		0.41 (updated)
			result.variables['constant_for_age'] = self.d('0.41')
			result.warnings.append(_('eGFR (Schwartz): not known whether pre-term birth, applying full-term formula'))
		else:
			result.variables['constant_for_age'] = self.d('0.41')

		# height
		result.variables['height'] = self.__patient.emr.get_result_at_timestamp (
			timestamp = result.variables['serum_crea']['clin_when'],
			loinc = gmLOINC.LOINC_height,
			tolerance_interval = '7 days'
		)
		if result.variables['height'] is None:
			result.message = _('eGFR (Schwartz): height not found')
			return result
		if result.variables['height']['val_num'] is None:
			result.message = _('eGFR (Schwartz): height not numeric')
			return result
		if result.variables['height']['val_unit'] == u'cm':
			result.variables['height_cm'] = self.d(result.variables['height']['val_num'])
		elif result.variables['height']['val_unit'] == u'mm':
			result.variables['height_cm'] = self.d(result.variables['height']['val_num'] / self.d(10))
		elif result.variables['height']['val_unit'] == u'm':
			result.variables['height_cm'] = self.d(result.variables['height']['val_num'] * 100)
		else:
			result.message = _('eGFR (Schwartz): height not in m, cm, or mm')
			return result

		# calculate
		result.numeric_value = (
			result.variables['constant_for_age'] * result.variables['height_cm']
		) / (
			result.variables['unit_multiplier'] * result.variables['serum_crea_val']
		)
		result.unit = u'ml/min/1.73m²'

		result.message = _('eGFR (Schwartz): %.2f %s (%s)') % (
			result.numeric_value,
			result.unit,
			gmDateTime.pydt_strftime (
				result.variables['serum_crea']['clin_when'],
				format = '%Y %b %d'
			)
		)
		result.date_valid = result.variables['serum_crea']['clin_when']

		self.__cache['gfr_schwartz'] = result
		_log.debug(u'%s' % result)

		return result

	eGFR_Schwartz = property(_get_gfr_schwartz, lambda x:x)
	#--------------------------------------------------------
	def _get_body_surface_area(self):

		try:
			return self.__cache['body_surface_area']
		except KeyError:
			pass

		result = cClinicalResult(_('unknown body surface area'))
		result.formula_name = u'Du Bois Body Surface Area'
		result.formula_source = u'12/2012: http://en.wikipedia.org/wiki/Body_surface_area'

		if self.__patient is None:
			result.message = _('Body Surface Area: no patient')
			return result

		result.variables['height'] = self.__patient.emr.get_most_recent_results(loinc = gmLOINC.LOINC_height, no_of_results = 1)
		if result.variables['height'] is None:
			result.message = _('Body Surface Area: height not found')
			return result
		if result.variables['height']['val_num'] is None:
			result.message = _('Body Surface Area: height not numeric')
			return result
		if result.variables['height']['val_unit'] == u'cm':
			result.variables['height_cm'] = self.d(result.variables['height']['val_num'])
		elif result.variables['height']['val_unit'] == u'mm':
			result.variables['height_cm'] = self.d(result.variables['height']['val_num'] / self.d(10))
		elif result.variables['height']['val_unit'] == u'm':
			result.variables['height_cm'] = self.d(result.variables['height']['val_num'] * 100)
		else:
			result.message = _('Body Surface Area: height not in m, cm, or mm')
			return result

		result.variables['weight'] = self.__patient.emr.get_result_at_timestamp (
			timestamp = result.variables['height']['clin_when'],
			loinc = gmLOINC.LOINC_weight,
			tolerance_interval = '10 days'
		)
		if result.variables['weight'] is None:
			result.message = _('Body Surface Area: weight not found')
			return result
		if result.variables['weight']['val_num'] is None:
			result.message = _('Body Surface Area: weight not numeric')
			return result
		if result.variables['weight']['val_unit'] == u'kg':
			result.variables['weight_kg'] = self.d(result.variables['weight']['val_num'])
		elif result.variables['weight']['val_unit'] == u'g':
			result.variables['weight_kg'] = self.d(result.variables['weight']['val_num'] / self.d(1000))
		else:
			result.message = _('Body Surface Area: weight not in kg or g')
			return result

		result.numeric_value = self.d('0.007184') * \
			pow(result.variables['weight_kg'], self.d('0.425')) * \
			pow(result.variables['height_cm'], self.d('0.725'))
		result.unit = u'm²'

		result.message = _('BSA (DuBois): %.2f %s') % (
			result.numeric_value,
			result.unit
		)
		result.date_valid = gmDateTime.pydt_now_here()

		self.__cache['body_surface_area'] = result
		_log.debug(u'%s' % result)

		return result

	body_surface_area = property(_get_body_surface_area, lambda x:x)
	#--------------------------------------------------------
	# helper functions
	#--------------------------------------------------------
	def d(self, initial):
		if isinstance(initial, decimal.Decimal):
			return initial

		val = initial

		# float ? -> to string first
		if type(val) == type(float(1.4)):
			val = str(val)

		# string ? -> "," to "."
		if isinstance(val, basestring):
			val = val.replace(',', '.', 1)
			val = val.strip()

		try:
			d = decimal.Decimal(val)
			return d
		except (TypeError, decimal.InvalidOperation):
			return None

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) == 1:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2
	#-----------------------------------------
	def test_clin_calc():
		from Gnumed.business.gmPerson import cPatient
		pat = cPatient(aPK_obj = 12)
		calc = cClinicalCalculator(patient = pat)
		#result = calc.eGFR_MDRD_short
		#result = calc.eGFR_Schwartz
		#result = calc.eGFR
		result = calc.body_surface_area

		print result.message
		print result.numeric_value, result.unit, result.date_valid
		print result.formula_name
		print result.formula_source
		print ""
		print result.variables
		print ""
		print result.warnings
		print ""
		print result.sub_results
	#-----------------------------------------
	test_clin_calc()
