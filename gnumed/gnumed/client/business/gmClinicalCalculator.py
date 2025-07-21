# -*- coding: utf-8 -*-
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
import datetime as pydt


if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmI18N
if __name__ == '__main__':
	_ = lambda x:x
	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()
from Gnumed.pycommon import gmTools
from Gnumed.business import gmLOINC
from Gnumed.business.gmGender import map_gender2mf

_log = logging.getLogger('gm.calc')

#============================================================
class cClinicalResult(object):

	def __init__(self, message=None):
		self.message = message
		self.numeric_value = None
		self.unit = None
		self.date_valid = None
		self.formula_name = None
		self.formula_source = None
		self.variables = {}
		self.sub_results = []
		self.warnings = [_('THIS IS NOT A VERIFIED MEASUREMENT. DO NOT USE FOR ACTUAL CARE.')]
		self.hints = []

	#--------------------------------------------------------
	def __str__(self):
		txt = '[cClinicalResult]: %s %s (%s)\n\n%s' % (
			self.numeric_value,
			self.unit,
			self.date_valid,
			self.format (
				left_margin = 0,
				width = 80,
				eol = '\n',
				with_formula = True,
				with_warnings = True,
				with_variables = True,
				with_sub_results = True,
				return_list = False
			)
		)
		return txt

	#--------------------------------------------------------
	def format(self, left_margin=0, eol='\n', width=None, with_formula=False, with_warnings=True, with_variables=False, with_sub_results=False, with_hints=True, return_list=False):
		lines = []
		lines.append(self.message)

		if with_formula:
			txt = gmTools.wrap (
				text = '%s %s' % (
					_('Algorithm:'),
					self.formula_name
				),
				width = width,
				initial_indent = ' ',
				subsequent_indent = ' ' * 2,
				eol = eol
			)
			lines.append(txt)
			txt = gmTools.wrap (
				text = '%s %s' % (
					_('Source:'),
					self.formula_source
				),
				width = width,
				initial_indent = ' ',
				subsequent_indent = ' ' * 2,
				eol = eol
			)
			lines.append(txt)

		if with_warnings:
			if len(self.warnings) > 0:
				lines.append(' Caveat:')
			for w in self.warnings:
				txt = gmTools.wrap(text = w, width = width, initial_indent = '  %s ' % gmTools.u_arrow2right, subsequent_indent = '    ', eol = eol)
				lines.append(txt)

		if with_hints:
			if len(self.hints) > 0:
				lines.append(' Hints:')
			for h in self.hints:
				txt = gmTools.wrap(text = h, width = width, initial_indent = '  %s ' % gmTools.u_arrow2right, subsequent_indent = '    ', eol = eol)
				lines.append(txt)

		if with_variables:
			if len(self.variables) > 0:
				lines.append(' %s' % _('Variables:'))
			for key in self.variables:
				txt = '  %s %s: %s' % (
					gmTools.u_arrow2right,
					key,
					self.variables[key]
				)
				lines.append(txt)

		if with_sub_results:
			if len(self.sub_results) > 0:
				lines.append(' %s' % _('Intermediate results:'))
			for r in self.sub_results:
				lines.extend(r.format (
					left_margin = left_margin + 1,
					width = width,
					eol = eol,
					with_formula = with_formula,
					with_warnings = with_warnings,
					with_variables = with_variables,
					with_sub_results = False,			# break cycles
					return_list = True
				))

		lines = gmTools.strip_trailing_empty_lines(lines = lines, eol = eol)
		if return_list:
			return lines

		left_margin = ' ' * left_margin
		return left_margin + (eol + left_margin).join(lines) + eol

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
	def get_EDC(self, lmp=None, nullipara=True):

		result = cClinicalResult(_('unknown EDC'))
		result.formula_name = 'EDC (Mittendorf 1990)'
		result.formula_source = 'Mittendorf, R. et al., "The length of uncomplicated human gestation," OB/GYN, Vol. 75, No., 6 June, 1990, pp. 907-932.'

		if lmp is None:
			result.message = _('EDC: unknown LMP')
			return result

		result.variables['LMP'] = lmp
		result.variables['nullipara'] = nullipara
		if nullipara:
			result.variables['parity_offset'] = 15		# days
		else:
			result.variables['parity_offset'] = 10		# days

		now = gmDateTime.pydt_now_here()
		if lmp > now:
			result.warnings.append(_('LMP in the future'))

		if self.__patient is None:
			result.warnings.append(_('cannot run sanity checks, no patient'))
		else:
			if self.__patient['dob'] is None:
				result.warnings.append(_('cannot run sanity checks, no DOB'))
			else:
				years, months, days, hours, minutes, seconds = gmDateTime.calculate_apparent_age(start = self.__patient['dob'])
				# 5 years -- Myth ?
				# http://www.mirror.co.uk/news/uk-news/top-10-crazy-amazing-and-world-789842
				if years < 10:
					result.warnings.append(_('patient less than 10 years old'))
			if self.__patient['gender'] in [None, 'm']:
				result.warnings.append(_('atypical gender for pregnancy: %s') % self.__patient.gender_string)
			if self.__patient['deceased'] is not None:
				result.warnings.append(_('patient already passed away'))

		if lmp.month > 3:
			edc_month = lmp.month - 3
			edc_year = lmp.year + 1
		else:
			edc_month = lmp.month + 9
			edc_year = lmp.year

		result.numeric_value = gmDateTime.pydt_replace(dt = lmp, year = edc_year, month = edc_month, strict = False) + pydt.timedelta(days = result.variables['parity_offset'])
		result.message = _('EDC: %s') % result.numeric_value.strftime('%Y %b %d')
		result.date_valid = now
		_log.debug('%s' % result)

		return result

	#--------------------------------------------------------
	def _get_egfrs(self):
		egfrs = [
			self.eGFR_MDRD_short,
			self.eGFR_Cockcroft_Gault,
			self.eGFR_CKD_EPI,
			self.eGFR_Schwartz
		]
		return egfrs

	eGFRs = property(_get_egfrs)

	#--------------------------------------------------------
	def _get_egfr(self):

		# < 18 ?
		Schwartz = self.eGFR_Schwartz
		if Schwartz.numeric_value is not None:
			return Schwartz

		# this logic is based on "KVH aktuell 2/2014 Seite 10-15"
		# expect normal GFR
		CKD = self.eGFR_CKD_EPI
		if CKD.numeric_value is not None:
			if CKD.numeric_value > self.d(60):
				return CKD

		# CKD at or below 60
		if self.__patient['dob'] is None:
			return CKD			# no method will work, so return CKD anyway

		CG = self.eGFR_Cockcroft_Gault
		MDRD = self.eGFR_MDRD_short
		age = None
		if age is None:
			try:
				age = CKD.variables['age@crea']
			except KeyError:
				_log.warning('CKD-EPI: no age@crea')
		if age is None:
			try:
				age = CG.variables['age@crea']
			except KeyError:
				_log.warning('CG: no age@crea')
		if age is None:
			try:
				age = MDRD.variables['age@crea']
			except KeyError:
				_log.warning('MDRD: no age@crea')
		if age is None:
			age = gmDateTime.calculate_apparent_age(start = self.__patient['dob'])[0]

		# geriatric ?
		if age > self.d(65):
			if CG.numeric_value is not None:
				return CG

		# non-geriatric or CG not computable
		if MDRD.numeric_value is None:
			if (CKD.numeric_value is not None) or (CG.numeric_value is None):
				return CKD
			return CG

		if MDRD.numeric_value > self.d(60):
			if CKD.numeric_value is not None:
				# probably normal after all (>60) -> use CKD-EPI
				return CKD

		return MDRD

	eGFR = property(_get_egfr)

	#--------------------------------------------------------
	def _get_gfr_mdrd_short(self):

		try:
			return self.__cache['MDRD_short']
		except KeyError:
			pass

		result = cClinicalResult(_('unknown MDRD (4 vars/IDMS)'))
		result.formula_name = 'eGFR from 4-variables IDMS-MDRD'
		result.formula_source = '1/2013: http://en.wikipedia.org/Renal_function / http://www.ganfyd.org/index.php?title=Estimated_glomerular_filtration_rate (NHS)'
		result.hints.append(_('best @ 30 < GFR < 60 ml/min'))

		if self.__patient is None:
			result.message = _('MDRD (4 vars/IDMS): no patient')
			return result

		if self.__patient['dob'] is None:
			result.message = _('MDRD (4 vars/IDMS): no DOB (no age)')
			return result

		# 1) gender
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
		creas = self.__patient.emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_creatinine_quantity, max_no_of_results = 1)
		result.variables['serum_crea'] = creas[0] if len(creas) > 0 else None
		if result.variables['serum_crea'] is None:
			result.message = _('MDRD (4 vars/IDMS): serum creatinine value not found (LOINC: %s)') % gmLOINC.LOINC_creatinine_quantity
			return result
		if result.variables['serum_crea']['val_num'] is None:
			result.message = _('MDRD (4 vars/IDMS): creatinine value not numeric')
			return result
		result.variables['serum_crea_val'] = self.d(result.variables['serum_crea']['val_num'])
		if result.variables['serum_crea']['val_unit'] in ['mg/dl', 'mg/dL']:
			result.variables['unit_multiplier'] = self.d(175)						# older: 186
		elif result.variables['serum_crea']['val_unit'] in ['µmol/L', 'µmol/l']:
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
		result.unit = 'ml/min/1.73m²'

		BSA = self.body_surface_area
		result.sub_results.append(BSA)
		if BSA.numeric_value is None:
			result.warnings.append(_('NOT corrected for non-average body surface (average = 1.73m²)'))
		else:
			result.variables['BSA'] = BSA.numeric_value
			result.numeric_value = result.numeric_value / BSA.numeric_value

		result.message = _('eGFR(MDRD): %.1f %s (%s) [4-vars, IDMS]') % (
			result.numeric_value,
			result.unit,
			result.variables['serum_crea']['clin_when'].strftime('%Y %b %d')
		)
		result.date_valid = result.variables['serum_crea']['clin_when']

		self.__cache['MDRD_short'] = result
		_log.debug('%s' % result)

		return result

	eGFR_MDRD_short = property(_get_gfr_mdrd_short)

	#--------------------------------------------------------
	def _get_gfr_ckd_epi(self):

		try:
			return self.__cache['CKD-EPI']
		except KeyError:
			pass

		result = cClinicalResult(_('unknown CKD-EPI'))
		result.formula_name = 'eGFR from CKD-EPI'
		result.formula_source = '8/2014: http://en.wikipedia.org/Renal_function'
		result.hints.append(_('best @ GFR > 60 ml/min'))

		if self.__patient is None:
			result.message = _('CKD-EPI: no patient')
			return result

		if self.__patient['dob'] is None:
			result.message = _('CKD-EPI: no DOB (no age)')
			return result

		# 1) gender
		result.variables['gender'] = self.__patient['gender']
		result.variables['gender_mf'] = map_gender2mf[self.__patient['gender']]
		if result.variables['gender_mf'] == 'm':
			result.variables['gender_multiplier'] = self.d(1)
			result.variables['k:gender_divisor'] = self.d('0.9')
			result.variables['a:gender_power'] = self.d('-0.411')
		elif result.variables['gender_mf'] == 'f':
			result.variables['gender_multiplier'] = self.d('1.018')
			result.variables['k:gender_divisor'] = self.d('0.7')
			result.variables['a:gender_power'] = self.d('-0.329')
		else:
			result.message = _('CKD-EPI: neither male nor female')
			return result

		# 2) creatinine
		creas = self.__patient.emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_creatinine_quantity, max_no_of_results = 1)
		result.variables['serum_crea'] = creas[0] if len(creas) > 0 else None
		if result.variables['serum_crea'] is None:
			result.message = _('CKD-EPI: serum creatinine value not found (LOINC: %s)') % gmLOINC.LOINC_creatinine_quantity
			return result
		if result.variables['serum_crea']['val_num'] is None:
			result.message = _('CKD-EPI: creatinine value not numeric')
			return result
		result.variables['serum_crea_val'] = self.d(result.variables['serum_crea']['val_num'])
		if result.variables['serum_crea']['val_unit'] in ['mg/dl', 'mg/dL']:
			result.variables['serum_crea_val'] = self.d(result.variables['serum_crea']['val_num'])
		elif result.variables['serum_crea']['val_unit'] in ['µmol/L', 'µmol/l']:
			result.variables['serum_crea_val'] = self.d(result.variables['serum_crea']['val_num']) / self.d('88.4')
		else:
			result.message = _('CKD-EPI: unknown serum creatinine unit (%s)') % result.variables['serum_crea']['val_unit']
			return result

		# 3) age (at creatinine evaluation)
		result.variables['dob'] = self.__patient['dob']
		result.variables['age@crea'] = self.d (
			gmDateTime.calculate_apparent_age (
				start = result.variables['dob'],
				end = result.variables['serum_crea']['clin_when']
			)[0]
		)
#		if (result.variables['age@crea'] > 84) or (result.variables['age@crea'] < 18):
#			result.message = _('CKD-EPI: formula does not apply at age [%s] (17 < age < 85)') % result.variables['age@crea']
#			return result

		# 4) ethnicity
		result.variables['ethnicity_multiplier'] = self.d(1)			# non-black
		result.warnings.append(_('ethnicity: GNUmed does not know patient ethnicity, ignoring correction factor of 1.519 for "black"'))

		# calculate
		result.numeric_value = (
			self.d(141) * \
			pow(min((result.variables['serum_crea_val'] / result.variables['k:gender_divisor']), self.d(1)), result.variables['a:gender_power']) * \
			pow(max((result.variables['serum_crea_val'] / result.variables['k:gender_divisor']), self.d(1)), self.d('-1.209')) * \
			pow(self.d('0.993'), result.variables['age@crea']) * \
			result.variables['gender_multiplier'] * \
			result.variables['ethnicity_multiplier']
		)
		result.unit = 'ml/min/1.73m²'

		result.message = _('eGFR(CKD-EPI): %.1f %s (%s)') % (
			result.numeric_value,
			result.unit,
			result.variables['serum_crea']['clin_when'].strftime('%Y %b %d')
		)
		result.date_valid = result.variables['serum_crea']['clin_when']

		self.__cache['CKD-EPI'] = result
		_log.debug('%s' % result)

		return result

	eGFR_CKD_EPI = property(_get_gfr_ckd_epi)

	#--------------------------------------------------------
	def _get_gfr_cockcroft_gault(self):

		try:
			return self.__cache['cockcroft_gault']
		except KeyError:
			pass

		result = cClinicalResult(_('unknown Cockcroft-Gault'))
		result.formula_name = 'eGFR from Cockcroft-Gault'
		result.formula_source = '8/2014: http://en.wikipedia.org/Renal_function'
		result.hints.append(_('best @ age >65'))

		if self.__patient is None:
			result.message = _('Cockcroft-Gault: no patient')
			return result

		if self.__patient['dob'] is None:
			result.message = _('Cockcroft-Gault: no DOB (no age)')
			return result

		# 1) gender
		result.variables['gender'] = self.__patient['gender']
		result.variables['gender_mf'] = map_gender2mf[self.__patient['gender']]
		if result.variables['gender_mf'] not in ['m', 'f']:
			result.message = _('Cockcroft-Gault: neither male nor female')
			return result

		# 2) creatinine
		creas = self.__patient.emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_creatinine_quantity, max_no_of_results = 1)
		result.variables['serum_crea'] = creas[0] if len(creas) > 0 else None
		if result.variables['serum_crea'] is None:
			result.message = _('Cockcroft-Gault: serum creatinine value not found (LOINC: %s)') % gmLOINC.LOINC_creatinine_quantity
			return result
		if result.variables['serum_crea']['val_num'] is None:
			result.message = _('Cockcroft-Gault: creatinine value not numeric')
			return result
		result.variables['serum_crea_val'] = self.d(result.variables['serum_crea']['val_num'])
		if result.variables['serum_crea']['val_unit'] in ['mg/dl', 'mg/dL']:
			result.variables['unit_multiplier'] = self.d(72)
			if result.variables['gender_mf'] == 'm':
				result.variables['gender_multiplier'] = self.d('1')
			else: #result.variables['gender_mf'] == 'f'
				result.variables['gender_multiplier'] = self.d('0.85')
		elif result.variables['serum_crea']['val_unit'] in ['µmol/L', 'µmol/l']:
			result.variables['unit_multiplier'] = self.d(1)
			if result.variables['gender_mf'] == 'm':
				result.variables['gender_multiplier'] = self.d('1.23')
			else: #result.variables['gender_mf'] == 'f'
				result.variables['gender_multiplier'] = self.d('1.04')
		else:
			result.message = _('Cockcroft-Gault: unknown serum creatinine unit (%s)') % result.variables['serum_crea']['val_unit']
			return result

		# 3) age (at creatinine evaluation)
		result.variables['dob'] = self.__patient['dob']
		result.variables['age@crea'] = self.d (
			gmDateTime.calculate_apparent_age (
				start = result.variables['dob'],
				end = result.variables['serum_crea']['clin_when']
			)[0]
		)
		if (result.variables['age@crea'] < 18):
			result.message = _('Cockcroft-Gault: formula does not apply at age [%s] (17 < age)') % result.variables['age@crea']
			return result

		weights = self.__patient.emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_weight, max_no_of_results = 1)
		result.variables['weight'] = weights[0] if len(weights) > 0 else None
		if result.variables['weight'] is None:
			result.message = _('Cockcroft-Gault: weight not found')
			return result
		if result.variables['weight']['val_num'] is None:
			result.message = _('Cockcroft-Gault: weight not numeric')
			return result
		if result.variables['weight']['val_unit'] == 'kg':
			result.variables['weight_kg'] = self.d(result.variables['weight']['val_num'])
		elif result.variables['weight']['val_unit'] == 'g':
			result.variables['weight_kg'] = self.d(result.variables['weight']['val_num'] / self.d(1000))
		else:
			result.message = _('Cockcroft-Gault: weight not in kg or g')
			return result

		# calculate
		result.numeric_value = ((
			(140 - result.variables['age@crea']) * result.variables['weight_kg'] * result.variables['gender_multiplier']) \
					/								\
			(result.variables['unit_multiplier'] * result.variables['serum_crea_val'])
		)
		result.unit = 'ml/min'		#/1.73m²

		result.message = _('eGFR(CG): %.1f %s (%s)') % (
			result.numeric_value,
			result.unit,
			result.variables['serum_crea']['clin_when'].strftime('%Y %b %d')
		)
		result.date_valid = result.variables['serum_crea']['clin_when']

		self.__cache['cockroft_gault'] = result
		_log.debug('%s' % result)

		return result

	eGFR_Cockcroft_Gault = property(_get_gfr_cockcroft_gault)

	#--------------------------------------------------------
	def _get_gfr_schwartz(self):

		try:
			return self.__cache['gfr_schwartz']
		except KeyError:
			pass

		result = cClinicalResult(_('unknown eGFR (Schwartz)'))
		result.formula_name = 'eGFR from updated Schwartz "bedside" formula (age < 19yrs)'
		result.formula_source = '1/2013: http://en.wikipedia.org/Renal_function / http://www.ganfyd.org/index.php?title=Estimated_glomerular_filtration_rate (NHS) / doi 10.1681/ASN.2008030287 / doi: 10.2215/CJN.01640309'
		result.hints.append(_('only applies @ age <18'))

		if self.__patient is None:
			result.message = _('eGFR (Schwartz): no patient')
			return result

		if self.__patient['dob'] is None:
			result.message = _('eGFR (Schwartz): DOB needed for age')
			return result

		result.variables['dob'] = self.__patient['dob']

		# creatinine
		creas = self.__patient.emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_creatinine_quantity, max_no_of_results = 1)
		result.variables['serum_crea'] = creas[0] if len(creas) > 0 else None
		if result.variables['serum_crea'] is None:
			result.message = _('eGFR (Schwartz): serum creatinine value not found (LOINC: %s') % gmLOINC.LOINC_creatinine_quantity
			return result
		if result.variables['serum_crea']['val_num'] is None:
			result.message = _('eGFR (Schwartz): creatinine value not numeric')
			return result
		result.variables['serum_crea_val'] = self.d(result.variables['serum_crea']['val_num'])
		if result.variables['serum_crea']['val_unit'] in ['mg/dl', 'mg/dL']:
			result.variables['unit_multiplier'] = self.d(1)
		elif result.variables['serum_crea']['val_unit'] in ['µmol/L', 'µmol/l']:
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
		if result.variables['height']['val_unit'] == 'cm':
			result.variables['height_cm'] = self.d(result.variables['height']['val_num'])
		elif result.variables['height']['val_unit'] == 'mm':
			result.variables['height_cm'] = self.d(result.variables['height']['val_num'] / self.d(10))
		elif result.variables['height']['val_unit'] == 'm':
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
		result.unit = 'ml/min/1.73m²'

		result.message = _('eGFR (Schwartz): %.1f %s (%s)') % (
			result.numeric_value,
			result.unit,
			result.variables['serum_crea']['clin_when'].strftime('%Y %b %d')
		)
		result.date_valid = result.variables['serum_crea']['clin_when']

		self.__cache['gfr_schwartz'] = result
		_log.debug('%s' % result)

		return result

	eGFR_Schwartz = property(_get_gfr_schwartz)

	#--------------------------------------------------------
	def _get_body_surface_area(self):

		try:
			return self.__cache['body_surface_area']
		except KeyError:
			pass

		result = cClinicalResult(_('unknown body surface area'))
		result.formula_name = 'Du Bois Body Surface Area'
		result.formula_source = '12/2012: http://en.wikipedia.org/wiki/Body_surface_area'

		if self.__patient is None:
			result.message = _('Body Surface Area: no patient')
			return result

		heights = self.__patient.emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_height, max_no_of_results = 1)
		result.variables['height'] = heights[0] if len(heights) > 0 else None
		if result.variables['height'] is None:
			result.message = _('Body Surface Area: height not found')
			return result

		if result.variables['height']['val_num'] is None:
			result.message = _('Body Surface Area: height not numeric')
			return result

		if result.variables['height']['val_unit'] == 'cm':
			result.variables['height_cm'] = self.d(result.variables['height']['val_num'])
		elif result.variables['height']['val_unit'] == 'mm':
			result.variables['height_cm'] = self.d(result.variables['height']['val_num'] / self.d(10))
		elif result.variables['height']['val_unit'] == 'm':
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

		if result.variables['weight']['val_unit'] == 'kg':
			result.variables['weight_kg'] = self.d(result.variables['weight']['val_num'])
		elif result.variables['weight']['val_unit'] == 'g':
			result.variables['weight_kg'] = self.d(result.variables['weight']['val_num'] / self.d(1000))
		else:
			result.message = _('Body Surface Area: weight not in kg or g')
			return result

		result.numeric_value = self.d('0.007184') * \
			pow(result.variables['weight_kg'], self.d('0.425')) * \
			pow(result.variables['height_cm'], self.d('0.725'))
		result.unit = 'm²'
		result.message = _('BSA (DuBois): %.2f %s') % (
			result.numeric_value,
			result.unit
		)
		result.date_valid = gmDateTime.pydt_now_here()
		self.__cache['body_surface_area'] = result
		_log.debug('%s' % result)
		return result

	body_surface_area = property(_get_body_surface_area)

	#--------------------------------------------------------
	def _get_body_mass_index(self):

		try:
			return self.__cache['body_mass_index']
		except KeyError:
			pass

		result = cClinicalResult(_('unknown BMI'))
		result.formula_name = 'BMI/Quetelet Index'
		result.formula_source = '08/2014: https://en.wikipedia.org/wiki/Body_mass_index'

		if self.__patient is None:
			result.message = _('BMI: no patient')
			return result

		heights = self.__patient.emr.get_most_recent_results_in_loinc_group(loincs = gmLOINC.LOINC_height, max_no_of_results = 1)
		result.variables['height'] = heights[0] if len(heights) > 0 else None
		if result.variables['height'] is None:
			result.message = _('BMI: height not found')
			return result

		if result.variables['height']['val_num'] is None:
			result.message = _('BMI: height not numeric')
			return result

		if result.variables['height']['val_unit'] == 'cm':
			result.variables['height_m'] = self.d(result.variables['height']['val_num'] / self.d(100))
		elif result.variables['height']['val_unit'] == 'mm':
			result.variables['height_m'] = self.d(result.variables['height']['val_num'] / self.d(1000))
		elif result.variables['height']['val_unit'] == 'm':
			result.variables['height_m'] = self.d(result.variables['height']['val_num'])
		else:
			result.message = _('BMI: height not in m, cm, or mm')
			return result

		result.variables['weight'] = self.__patient.emr.get_result_at_timestamp (
			timestamp = result.variables['height']['clin_when'],
			loinc = gmLOINC.LOINC_weight,
			tolerance_interval = '10 days'
		)
		if result.variables['weight'] is None:
			result.message = _('BMI: weight not found')
			return result

		if result.variables['weight']['val_num'] is None:
			result.message = _('BMI: weight not numeric')
			return result

		if result.variables['weight']['val_unit'] == 'kg':
			result.variables['weight_kg'] = self.d(result.variables['weight']['val_num'])
		elif result.variables['weight']['val_unit'] == 'g':
			result.variables['weight_kg'] = self.d(result.variables['weight']['val_num'] / self.d(1000))
		else:
			result.message = _('BMI: weight not in kg or g')
			return result

		result.variables['dob'] = self.__patient['dob']
		start = result.variables['dob']
		end = result.variables['height']['clin_when']
		multiplier = 1
		if end < start:
			start = result.variables['height']['clin_when']
			end = result.variables['dob']
			multiplier = -1
		result.variables['age@height'] = multiplier * self.d(gmDateTime.calculate_apparent_age(start, end)[0])
		if (result.variables['age@height'] < 18):
			result.message = _('BMI (Quetelet): formula does not apply at age [%s] (0 < age < 18)') % result.variables['age@height']
			return result

		# bmi = mass kg / height m2
		result.numeric_value = result.variables['weight_kg'] / (result.variables['height_m'] * result.variables['height_m'])
		result.unit = 'kg/m²'

		result.message = _('BMI (Quetelet): %.2f %s') % (
			result.numeric_value,
			result.unit
		)
		result.date_valid = max(result.variables['height']['clin_when'], result.variables['weight']['clin_when'])

		self.__cache['body_mass_index'] = result
		_log.debug('%s' % result)
		return result

	body_mass_index = property(_get_body_mass_index)
	bmi = property(_get_body_mass_index)

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
		if isinstance(val, str):
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

	#-----------------------------------------
	def test_clin_calc():
		from Gnumed.business import gmPraxis
		branches = gmPraxis.get_praxis_branches()
		gmPraxis.gmCurrentPraxisBranch(branches[0])

		from Gnumed.business.gmPerson import cPatient
		pat = cPatient(aPK_obj = 201)

		calc = cClinicalCalculator(patient = pat)
		#result = calc.eGFR_MDRD_short
		#result = calc.eGFR_Schwartz
		result = calc.eGFR
		#result = calc.body_surface_area
		#result = calc.get_EDC(lmp = gmDateTime.pydt_now_here())
		#result = calc.body_mass_index
		#result = calc.eGFRs
		print('%s' % result.format(with_formula = True, with_warnings = True, with_variables = True, with_sub_results = True))

	#-----------------------------------------
	test_clin_calc()
