"""GNUmed medication handling phrasewheels."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys


# setup translation
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	# we are the main script, setup a fake _() for now,
	# such that it can be used in module level definitions
	_ = lambda x:x
else:
	# we are being imported from elsewhere, say, mypy or some such
	try:
		# do we already have _() ?
		_
	except NameError:
		# no, setup i18n handling
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
from Gnumed.pycommon import gmMatchProvider

from Gnumed.business import gmMedication

from Gnumed.wxpython import gmPhraseWheel


_log = logging.getLogger('gm.ui')

#============================================================
# perhaps leave this here:
#============================================================
class cSubstancePreparationPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
SELECT DISTINCT ON (list_label)
	preparation AS data,
	preparation AS list_label,
	preparation AS field_label
FROM ref.drug_product
WHERE preparation %(fragment_condition)s
ORDER BY list_label
LIMIT 30"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_('The preparation (form) of the substance or product.'))
		self.matcher = mp
		self.selection_only = False

#============================================================
class cSubstancePRW(gmPhraseWheel.cPhraseWheel):
	"""Matches a substance by name."""
	def __init__(self, *args, **kwargs):
		SQL = """-- substance match provider
			SELECT DISTINCT ON (substance)
				r_vs.substance AS field_label,
				r_vs.substance AS list_label,
				r_vs.pk_substance AS data
			FROM ref.v_substances r_vs
			WHERE r_vs.substance %(fragment_condition)s
			ORDER BY r_vs.substance
			LIMIT 30
		"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries = SQL)
		mp.setThresholds(1, 2, 4)
		mp.word_separators = '[ \t=+&:@]+'
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_('The substance the patient is taking.'))
		self.matcher = mp
		#self.matcher.print_queries = True
		self.selection_only = False
		self.phrase_separators = None

	#--------------------------------------------------------
	def _data2instance(self, link_obj=None):
		pk = self.GetData(as_instance = False, can_create = False, link_obj = link_obj)
		if pk is None:
			return None

		return gmMedication.cSubstance(aPK_obj = pk, link_obj = link_obj)

	#--------------------------------------------------------
	def _create_data(self, link_obj=None):
		val = self.Value.strip()
		if not val:
			return

		subst = gmMedication.create_substance (
			substance = val,
			link_obj = link_obj
		)
		if not subst:
			self.data = {}
			return

		self.SetText(value = subst['substance'], data = subst['pk_substance'])

#============================================================
class cSubstanceOrDosePhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Matches a substance, by name, possibly with strength (then a dose).
	"""
	def __init__(self, *args, **kwargs):
		mp = gmMedication.cSubstanceDoseMatchProvider()
		mp.setThresholds(2, 3, 5)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_('The substance the patient is taking.\n\nYou can enter/select a substance with or without a strength.'))
		self.matcher = mp
		self.selection_only = False
		self.phrase_separators = None

	#--------------------------------------------------------
	def _data2instance(self, link_obj=None):
		if not self._data:
			return None

		pk_subst, pk_dose = self.GetData(as_instance = False, can_create = False, link_obj = link_obj)
		if not pk_subst:
			return None, None

		subst = gmMedication.cSubstance(aPK_obj = pk_subst)
		if pk_dose:
			dose = gmMedication.cSubstanceDose(aPK_obj = pk_dose)
		else:
			dose = None
		return subst, dose

	#--------------------------------------------------------
	def _create_data(self, link_obj=None):
		val = self.Value.strip()
		if not val:
			return

		subst = gmMedication.create_substance(substance = val, link_obj = link_obj)
		if not subst:
			self.data = {}
			return

		self.SetText(value = subst['substance'], data = [subst['pk_substance'], None])

	#--------------------------------------------------------
	def _get_as_dose(self):
		if not self._data:
			return None

		pk_dose = self.data[1]
		if not pk_dose:
			return None

		return gmMedication.cSubstanceDose(aPK_obj = pk_dose)

	as_dose = property(_get_as_dose)

#============================================================
# current substance intake widgets
#------------------------------------------------------------
class cSubstanceIntakeObjectPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		mp = gmMedication.cSubstanceIntakeObjectMatchProvider()
		mp.setThresholds(1, 2, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_('A drug product.'))
		self.matcher = mp
		self.selection_only = True
		self.phrase_separators = None

	#--------------------------------------------------------
	def _data2instance(self, link_obj=None):
		pk = self.GetData(as_instance = False, can_create = False)
		if pk is None:
			return None
		return gmMedication.cDrugProduct(aPK_obj = pk)

#------------------------------------------------------------
class cProductOrSubstancePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		mp = gmMedication.cProductOrSubstanceMatchProvider()
		mp.setThresholds(1, 2, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_('A substance with optional strength or a drug product.'))
		self.matcher = mp
		self.selection_only = False
		self.phrase_separators = None
		self.IS_PRODUCT = 1
		self.IS_SUBSTANCE = 2
		self.IS_COMPONENT = 3

	#--------------------------------------------------------
	def _data2instance(self, link_obj=None):
		entry_type, pk = self.GetData(as_instance = False, can_create = False)
		if entry_type == 1:
			return gmMedication.cDrugProduct(aPK_obj = pk)
		if entry_type == 2:
			return gmMedication.cSubstance(aPK_obj = pk)
		if entry_type == 3:
			return gmMedication.cDrugComponent(aPK_obj = pk)
		raise ValueError('entry type must be 1=drug product or 2=substance or 3=component')

#============================================================
class cSubstanceSchedulePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		SQL = """
			SELECT DISTINCT ON (narrative)
				narrative AS field_label,
				narrative AS list_label,
				narrative AS data
			FROM clin.intake_regimen
			WHERE narrative %(fragment_condition)s
			ORDER BY narrative
			LIMIT 50"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries = SQL)
		mp.setThresholds(1, 2, 4)
		mp.word_separators = '[ \t=+&:@]+'
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_('The schedule for taking this substance.'))
		self.matcher = mp
		self.selection_only = False

#============================================================
class cSubstancePatientNotesPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		SQL = """-- cSubstancePatientNotesPhraseWheel
			SELECT DISTINCT ON (field_label)
				data, list_label, field_label
			FROM ((
					SELECT
						notes4patient
							AS data,
						notes4patient || ' (' || substance || ' ' || amount || ' ' || unit || ')'
							AS list_label,
						notes4patient
							AS field_label
					FROM clin.v_intakes
					WHERE
						notes4patient %(fragment_condition)s
						%(ctxt_substance)s
				) UNION (
					SELECT
						notes4patient
							AS data,
						notes4patient || ' (' || substance || ' ' || amount || ' ' || unit || ')'
							AS list_label,
						notes4patient
							AS field_label
					FROM clin.v_intakes
					WHERE
						notes4patient %(fragment_condition)s
				)) AS notes
			ORDER BY field_label
			LIMIT 30"""
		context = {'ctxt_substance': {
			'where_part': 'AND substance = %(substance)s',
			'placeholder': 'substance'
		}}

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = SQL, context = context)
		mp.setThresholds(1, 2, 4)
		#mp.word_separators = '[ \t=+&:@]+'
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_('Notes for the patient on this substance intake.'))
		self.matcher = mp
		self.selection_only = False

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	from Gnumed.wxpython import gmGuiTest
	#----------------------------------------
	gmGuiTest.test_widget(widget_class = cSubstanceOrDosePhraseWheel, patient = 12, size = (600,200))
