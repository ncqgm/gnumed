"""GNUmed family history related widgets."""
#================================================================
__author__ = 'karsten.hilbert@gmx.net'
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

# stdlib
import logging, sys


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmMatchProvider

from Gnumed.business import gmPerson
from Gnumed.business import gmFamilyHistory

from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmPhraseWheel


_log = logging.getLogger('gm.ui')

#================================================================
def manage_family_history(parent=None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.emr

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#-----------------------------------------
	def edit(family_history=None):
		return edit_family_history(parent = parent, family_history = family_history)
	#-----------------------------------------
	def delete(family_history=None):
		if gmFamilyHistory.delete_family_history(pk_family_history = family_history['pk_family_history']):
			return True

		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Cannot delete family history item.'),
			beep = True
		)
		return False
	#------------------------------------------------------------
	def refresh(lctrl):
		fhx = emr.get_family_history()
		items = [ [
			f['l10n_relation'],
			f['condition'],
			gmTools.bool2subst(f['contributed_to_death'], _('yes'), _('no'), '?'),
			gmTools.coalesce(f['age_noted'], ''),
			gmDateTime.format_interval (
				interval = f['age_of_death'],
				accuracy_wanted = gmDateTime.acc_years,
				none_string = ''
			),
			gmTools.coalesce(f['name_relative'], ''),
			gmTools.coalesce(f['dob_relative'], '', function4value = ('strftime', '%Y-%m-%d'))
		] for f in fhx ]
		lctrl.set_string_items(items)
		lctrl.set_data(fhx)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('Family history of this patient.'),
		caption = _('Showing family history.'),
		columns = [ _('Relationship'), _('Condition'), _('Fatal'), _('Noted'), _('Died'), _('Name'), _('Born') ],
		single_selection = True,
		can_return_empty = True,
		ignore_OK_button = True,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete
#		left_extra_button=None,
#		middle_extra_button=None,
#		right_extra_button=None
	)

#----------------------------------------------------------------
def edit_family_history(parent=None, family_history=None, single_entry=True):
	ea = cFamilyHistoryEAPnl(parent, -1)
	ea.data = family_history
	ea.mode = gmTools.coalesce(family_history, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(family_history, _('Adding family history'), _('Editing family history')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#====================================================================
from Gnumed.wxGladeWidgets import wxgFamilyHistoryEAPnl

class cFamilyHistoryEAPnl(wxgFamilyHistoryEAPnl.wxgFamilyHistoryEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['family_history']
			del kwargs['family_history']
		except KeyError:
			data = None

		wxgFamilyHistoryEAPnl.wxgFamilyHistoryEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		#self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
#		# adjust phrasewheels etc
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		if self._PRW_condition.GetValue().strip() == '':
			validity = False
			self._PRW_condition.display_as_valid(False)
		else:
			self._PRW_condition.display_as_valid(True)

		# make sure there's a relationship string
		if self._PRW_relationship.GetValue().strip() == '':
			validity = False
			self._PRW_relationship.display_as_valid(False)
		else:
			self._PRW_relationship.display_as_valid(True)

		# make sure there's an episode name
		if self._PRW_episode.GetValue().strip() == '':
			self._PRW_episode.SetText(_('Family History'), None)
			self._PRW_episode.display_as_valid(True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):

		pat = gmPerson.gmCurrentPatient()
		emr = pat.emr

		data = emr.add_family_history (
			episode = self._PRW_episode.GetData(can_create = True),
			condition = self._PRW_condition.GetValue().strip(),
			relation = self._PRW_relationship.GetData(can_create = True)
		)

		data['age_noted'] = self._TCTRL_age_of_onset.GetValue().strip()
		data['age_of_death'] = self._PRW_age_of_death.GetData()
		data['contributed_to_death'] = self._PRW_died_of_this.GetData()
		data['name_relative'] = self._TCTRL_name.GetValue().strip()
		data['dob_relative'] = self._PRW_dob.GetData()
		data['comment'] = self._TCTRL_comment.GetValue().strip()
		data.save()

		data.generic_codes = [ c['data'] for c in self._PRW_codes.GetData() ]

		self.data = data
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		self.data['pk_episode'] = self._PRW_episode.GetData(can_create = True)
		self.data['condition'] = self._PRW_condition.GetValue().strip()
		self.data['pk_fhx_relation_type'] = self._PRW_relationship.GetData(can_create = True)

		self.data['age_noted'] = self._TCTRL_age_of_onset.GetValue().strip()
		self.data['age_of_death'] = self._PRW_age_of_death.GetData()
		self.data['contributed_to_death'] = self._PRW_died_of_this.GetData()
		self.data['name_relative'] = self._TCTRL_name.GetValue().strip()
		self.data['dob_relative'] = self._PRW_dob.GetData()
		self.data['comment'] = self._TCTRL_comment.GetValue().strip()

		self.data.save()
		self.data.generic_codes = [ c['data'] for c in self._PRW_codes.GetData() ]

		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_relationship.SetText('', None)
		self._PRW_condition.SetText('', None)
		self._PRW_codes.SetText()
		self._TCTRL_age_of_onset.SetValue('')
		self._PRW_age_of_death.SetText('', None)
		self._PRW_died_of_this.SetData(None)
		self._PRW_episode.SetText('', None)
		self._TCTRL_name.SetValue('')
		self._PRW_dob.SetText('', None)
		self._TCTRL_comment.SetValue('')

		self._PRW_relationship.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_relationship.SetText (
			self.data['l10n_relation'],
			self.data['pk_fhx_relation_type']
		)
		self._PRW_condition.SetText(self.data['condition'], None)
		val, data = self._PRW_codes.generic_linked_codes2item_dict(self.data.generic_codes)
		self._PRW_codes.SetText(val, data)
		self._TCTRL_age_of_onset.SetValue(gmTools.coalesce(self.data['age_noted'], ''))
		self._PRW_age_of_death.SetData(self.data['age_of_death'])
		self._PRW_died_of_this.SetData(self.data['contributed_to_death'])
		self._PRW_episode.SetText(self.data['episode'], self.data['pk_episode'])
		self._TCTRL_name.SetValue(gmTools.coalesce(self.data['name_relative'], ''))
		self._PRW_dob.SetData(self.data['dob_relative'])
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))

		self._PRW_relationship.SetFocus()
#================================================================
class cRelationshipTypePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		super(cRelationshipTypePhraseWheel, self).__init__(*args, **kwargs)

		query = """
			SELECT DISTINCT ON (list_label)
				pk as data,
				_(description) as field_label,
				_(description) as list_label
			FROM
				clin.fhx_relation_type
			WHERE
				description %(fragment_condition)s
					OR
				_(description) %(fragment_condition)s
			ORDER BY list_label
			LIMIT 30"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 3)
		self.matcher = mp
	#----------------------------------------------------------------
	def _create_data(self):
		if self.GetData() is not None:
			return

		val = self.GetValue().strip()
		if val == '':
			return

		self.SetText (
			value = val,
			data = gmFamilyHistory.create_relationship_type(relationship = val)
		)
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	#--------------------------------------------------------
#	def test_generic_codes_prw():
#		gmPG2.get_connection()
#		app = wx.PyWidgetTester(size = (500, 40))
#		pw = cGenericCodesPhraseWheel(app.frame, -1)
##		#pw.set_context(context = u'zip', val = u'04318')
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
#	test_generic_codes_prw()

#================================================================
