"""GNUmed hospital stay widgets"""
#================================================================
__author__ = "cfmoro1976@yahoo.es, karsten.hilbert@gmx.net"
__license__ = "GPL v2 or later"

# stdlib
import sys
import logging
import datetime as pydt


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmDateTime
if __name__ == '__main__':
	gmDateTime.init()

from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMatchProvider

from Gnumed.business import gmHospitalStay
from Gnumed.business import gmPerson

from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEditArea


_log = logging.getLogger('gm.ui')

#================================================================
# hospitalizations related widgets/functions
#----------------------------------------------------------------
def manage_hospital_stays(parent=None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.emr

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#-----------------------------------------
	def get_tooltip(stay=None):
		if stay is None:
			return None
		return stay.format (
			include_procedures = True,
			include_docs = True
		)

	#-----------------------------------------
	def edit(stay=None):
		return edit_hospital_stay(parent = parent, hospital_stay = stay)

	#-----------------------------------------
	def delete(stay=None):
		if gmHospitalStay.delete_hospital_stay(stay = stay['pk_hospital_stay']):
			return True

		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Cannot delete hospitalization.'),
			beep = True
		)
		return False

	#-----------------------------------------
	def refresh(lctrl):
		stays = emr.get_hospital_stays()
		items = [
			[
				s['admission'].strftime('%Y-%m-%d'),
				gmTools.coalesce(s['discharge'], '', function4value = ('strftime', '%Y-%m-%d')),
				s['episode'],
				'%s @ %s' % (s['ward'], s['hospital'])
			] for s in stays
		]
		lctrl.set_string_items(items = items)
		lctrl.set_data(data = stays)
	#-----------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _("The patient's hospitalizations:\n"),
		caption = _('Editing hospitalizations ...'),
		columns = [_('Admission'), _('Discharge'), _('Reason'), _('Hospital')],
		single_selection = True,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh,
		list_tooltip_callback = get_tooltip
	)

#----------------------------------------------------------------
def edit_hospital_stay(parent=None, hospital_stay=None, single_entry=True):
	ea = cHospitalStayEditAreaPnl(parent, -1)
	ea.data = hospital_stay
	ea.mode = gmTools.coalesce(hospital_stay, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(hospital_stay, _('Adding a hospitalization'), _('Editing a hospitalization')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#----------------------------------------------------------------
class cHospitalWardPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Phrasewheel to allow selection of a hospitalization."""
	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__ (self, *args, **kwargs)

		query = """
		SELECT data, list_label, field_label FROM (
			SELECT DISTINCT ON (data) * FROM ((

				-- already-used org_units
				SELECT
					pk_org_unit
						AS data,
					ward || ' @ ' || hospital
						AS list_label,
					ward || ' @ ' || hospital
						AS field_label,
					1
						AS rank
				FROM
					clin.v_hospital_stays
				WHERE
					ward %(fragment_condition)s
						OR
					hospital %(fragment_condition)s

				) UNION ALL (
				-- wards
				SELECT
					pk_org_unit
						AS data,
					unit || ' (' || l10n_unit_category || ') @ ' || organization
						AS list_label,
					unit || ' @ ' || organization
						AS field_label,
					2
						AS rank
				FROM
					dem.v_org_units
				WHERE
					unit_category = 'Ward'
						AND
					unit %(fragment_condition)s
						AND
					NOT EXISTS (
						SELECT 1 FROM clin.v_hospital_stays WHERE clin.v_hospital_stays.pk_org_unit = dem.v_org_units.pk_org_unit
					)

				) UNION ALL (
				-- hospital units
				SELECT
					pk_org_unit
						AS data,
					unit || coalesce(' (' || l10n_unit_category || ')', '') || ' @ ' || organization || ' (' || l10n_organization_category || ')'
						AS list_label,
					unit || ' @ ' || organization
						AS field_label,
					3
						AS rank
				FROM
					dem.v_org_units
				WHERE
					unit_category <> 'Ward'
						AND
					organization_category = 'Hospital'
						AND
					unit %(fragment_condition)s
						AND
					NOT EXISTS (
						SELECT 1 FROM clin.v_hospital_stays WHERE clin.v_hospital_stays.pk_org_unit = dem.v_org_units.pk_org_unit
					)

				) UNION ALL (
				-- any other units
				SELECT
					pk_org_unit
						AS data,
					unit || coalesce(' (' || l10n_unit_category || ')', '') || ' @ ' || organization || ' (' || l10n_organization_category || ')'
						AS list_label,
					unit || ' @ ' || organization
						AS field_label,
					3
						AS rank
				FROM
					dem.v_org_units
				WHERE
					unit_category <> 'Ward'
						AND
					organization_category <> 'Hospital'
						AND
					unit %(fragment_condition)s
						AND
					NOT EXISTS (
						SELECT 1 FROM clin.v_hospital_stays WHERE clin.v_hospital_stays.pk_org_unit = dem.v_org_units.pk_org_unit
					)
			)) AS all_matches
			ORDER BY data, rank
		) AS distinct_matches
		ORDER BY rank, list_label
		LIMIT 50
		"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = [query])
		mp.setThresholds(2, 4, 6)
		self.matcher = mp
		self.selection_only = True

#----------------------------------------------------------------
__SQL_hospital_stay_match_provider = """-- PRW: retrieve matching hospital stays
	SELECT
		pk_hospital_stay,
		descr
	FROM (
		SELECT DISTINCT ON (pk_hospital_stay)
			pk_hospital_stay,
			descr
		FROM
			(SELECT
				pk_hospital_stay,
				(
					to_char(admission, 'YYYY-Mon-DD')
					|| ' (' || ward || ' @ ' || hospital || '):'
					|| episode
					|| coalesce((' (' || health_issue || ')'), '')
				) AS descr
			 FROM
			 	clin.v_hospital_stays
			 WHERE
				%(ctxt_pat)s (
					hospital %(fragment_condition)s
						OR
					ward %(fragment_condition)s
						OR
					episode %(fragment_condition)s
						OR
					health_issue %(fragment_condition)s
				)
			) AS the_stays
	) AS distinct_stays
	ORDER BY descr
	LIMIT 25
"""

class cHospitalStayPhraseWheel(gmPhraseWheel.cPhraseWheel):
	"""Phrasewheel to allow selection of a hospital-type org_unit."""
	def __init__(self, *args, **kwargs):
		gmPhraseWheel.cPhraseWheel.__init__ (self, *args, **kwargs)
		ctxt = {'ctxt_pat': {'where_part': '(pk_patient = %(pat)s) AND', 'placeholder': 'pat'}}
		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [__SQL_hospital_stay_match_provider],
			context = ctxt
		)
		mp.setThresholds(3, 4, 6)
		mp.set_context('pat', gmPerson.gmCurrentPatient().ID)
		self.matcher = mp
		self.selection_only = True

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgHospitalStayEditAreaPnl

class cHospitalStayEditAreaPnl(wxgHospitalStayEditAreaPnl.wxgHospitalStayEditAreaPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):
		wxgHospitalStayEditAreaPnl.wxgHospitalStayEditAreaPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		valid = True

		if self._PRW_episode.GetValue().strip() == '':
			valid = False
			self._PRW_episode.display_as_valid(False)
			self.StatusText = _('Must select an episode or enter a name for a new one. Cannot save hospitalization.')
			self._PRW_episode.SetFocus()

		if not self._PRW_admission.is_valid_timestamp(empty_is_valid = False):
			valid = False
			self.StatusText = _('Missing admission data. Cannot save hospitalization.')
			self._PRW_admission.SetFocus()

		if self._PRW_discharge.is_valid_timestamp(empty_is_valid = True):
			if self._PRW_discharge.date is not None:
				adm = self._PRW_admission.date
				discharge = self._PRW_discharge.date
				# normalize for comparison
				discharge = discharge.replace (
					hour = adm.hour,
					minute = adm.minute,
					second = adm.second,
					microsecond = adm.microsecond
				)
				if adm is not None:
					if discharge == adm:
						self._PRW_discharge.SetData(discharge + pydt.timedelta(seconds = 1))
					elif not self._PRW_discharge.date > self._PRW_admission.date:
						valid = False
						self._PRW_discharge.display_as_valid(False)
						self.StatusText = _('Discharge date must be empty or later than admission. Cannot save hospitalization.')
						self._PRW_discharge.SetFocus()

		if self._PRW_hospital.GetData() is None:
			valid = False
			self._PRW_hospital.display_as_valid(False)
			self.StatusText = _('Must select a hospital. Cannot save hospitalization.')
			self._PRW_hospital.SetFocus()
		else:
			self._PRW_hospital.display_as_valid(True)

		return (valid is True)
	#----------------------------------------------------------------
	def _save_as_new(self):

		pat = gmPerson.gmCurrentPatient()
		emr = pat.emr
		stay = emr.add_hospital_stay(episode = self._PRW_episode.GetData(can_create = True), fk_org_unit = self._PRW_hospital.GetData())
		stay['comment'] = self._TCTRL_comment.GetValue().strip()
		stay['admission'] = self._PRW_admission.GetData()
		stay['discharge'] = self._PRW_discharge.GetData()
		stay['comment'] = self._TCTRL_comment.GetValue()
		stay.save_payload()

		self.data = stay
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		self.data['pk_episode'] = self._PRW_episode.GetData(can_create = True)
		self.data['pk_org_unit'] = self._PRW_hospital.GetData()
		self.data['admission'] = self._PRW_admission.GetData()
		self.data['discharge'] = self._PRW_discharge.GetData()
		self.data['comment'] = self._TCTRL_comment.GetValue()
		self.data.save_payload()

		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_hospital.SetText(value = '', data = None)
		self._PRW_episode.SetText(value = '')
		self._PRW_admission.SetText(data = gmDateTime.pydt_now_here())
		self._PRW_discharge.SetText()
		self._TCTRL_comment.SetValue('')
		self._PRW_hospital.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_hospital.SetText(value = '%s @ %s' % (self.data['ward'], self.data['hospital']), data = self.data['pk_org_unit'])

		if self.data['pk_episode'] is not None:
			self._PRW_episode.SetText(value = self.data['episode'], data = self.data['pk_episode'])

		self._PRW_admission.SetText(data = self.data['admission'])
		self._PRW_discharge.SetText(data = self.data['discharge'])
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))

		self._PRW_hospital.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		print("this was not expected to be used in this edit area")

#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.business import gmPersonSearch
	from Gnumed.wxpython import gmPatSearchWidgets

	#================================================================
	# obtain patient
	pat = gmPersonSearch.ask_for_patient()
	if pat is None:
		print("No patient. Exiting gracefully...")
		sys.exit(0)
	gmPatSearchWidgets.set_active_patient(patient=pat)

	#----------------------------------------------------------------
#	def test_hospital_stay_prw():
#		app = wx.PyWidgetTester(size = (400, 40))
#		app.SetWidget(cHospitalStayPhraseWheel, id=-1, size=(180,20), pos=(10,20))
#		app.MainLoop()

#	test_hospital_stay_prw()
