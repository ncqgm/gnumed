"""GNUmed generic contact related widgets."""
#================================================================
__author__ = 'karsten.hilbert@gmx.net'
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

# stdlib
import logging, sys


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider

from Gnumed.business import gmDemographicRecord

from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmGuiHelpers


_log = logging.getLogger('gm.ui')
#============================================================
# communication channels related widgets
#============================================================
def manage_comm_channel_types(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def delete(channel=None):
		return gmDemographicRecord.delete_comm_channel_type(pk_channel_type = channel['pk'])
	#------------------------------------------------------------
	def refresh(lctrl):
		wx.BeginBusyCursor()
		channel_types = gmDemographicRecord.get_comm_channel_types()
		lctrl.set_string_items([ (ct['l10n_description'], ct['description'], ct['pk']) for ct in channel_types ])
		lctrl.set_data(channel_types)
		wx.EndBusyCursor()
	#------------------------------------------------------------
	msg = _('\nThis lists the communication channel types known to GNUmed.\n')

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Managing communication types ...'),
		columns = [_('Channel'), _('System type'), '#'],
		single_selection = True,
		#new_callback = edit,
		#edit_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh
	)

#------------------------------------------------------------
class cCommChannelTypePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
SELECT
	data,
	field_label,
	list_label
FROM (
	SELECT DISTINCT ON (field_label)
		pk
			AS data,
		_(description)
			AS field_label,
		(_(description) || ' (' || description || ')')
			AS list_label
	FROM dem.enum_comm_types
	WHERE
		_(description) %(fragment_condition)s
			OR
		description %(fragment_condition)s
) AS ur
ORDER BY
	ur.list_label
"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 4)
		mp.word_separators = '[ \t]+'
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.matcher = mp
		self.SetToolTip(_('Select the type of communications channel.'))
		self.selection_only = True

#================================================================
def edit_comm_channel(parent=None, comm_channel=None, channel_owner=None):
	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	ea = cCommChannelEditAreaPnl(parent, -1, comm_channel = comm_channel)
	ea.channel_owner = channel_owner
	dlg = gmEditArea.cGenericEditAreaDlg2(-1, edit_area = ea, single_entry = True)
	dlg.SetTitle(_('Editing communications channel'))
	if dlg.ShowModal() == wx.ID_OK:
		return True
	return False
#------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgCommChannelEditAreaPnl

class cCommChannelEditAreaPnl(wxgCommChannelEditAreaPnl.wxgCommChannelEditAreaPnl, gmEditArea.cGenericEditAreaMixin):
	"""An edit area for editing/creating a comms channel.

	Does NOT act on/listen to the current patient.
	"""
	def __init__(self, *args, **kwargs):
		try:
			data = kwargs['comm_channel']
			del kwargs['comm_channel']
		except KeyError:
			data = None

		self.channel_owner = None

		wxgCommChannelEditAreaPnl.wxgCommChannelEditAreaPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		#self.__init_ui()
	#----------------------------------------------------------------
	#def __init_ui(self):
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		validity = True

		if self._TCTRL_url.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_url, valid = False)
			self._TCTRL_url.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_url, valid = True)

		# do not check GetData() because comm
		# types are created as needed
		#if self._PRW_type.GetData() is None:
		if self._PRW_type.GetValue().strip() == '':
			validity = False
			self._PRW_type.display_as_valid(False)
			self._PRW_type.SetFocus()
		else:
			self._PRW_type.display_as_valid(True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):
		try:
			data = self.channel_owner.link_comm_channel (
				comm_medium = self._PRW_type.GetValue().strip(),
				pk_channel_type = self._PRW_type.GetData(),
				url = self._TCTRL_url.GetValue().strip(),
				is_confidential = self._CHBOX_confidential.GetValue(),
			)
		except gmPG2.dbapi.IntegrityError:
			_log.exception('error saving comm channel')
			self.StatusText = _('Cannot save (duplicate ?) communications channel.')
			return False

		data['comment'] = self._TCTRL_comment.GetValue().strip()
		data.save()

		self.data = data
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		comm_type = self._PRW_type.GetValue().strip()
		if comm_type != '':
			self.data['comm_type'] = comm_type
		url = self._TCTRL_url.GetValue().strip()
		if url != '':
			self.data['url'] = url
		self.data['is_confidential'] = self._CHBOX_confidential.GetValue()
		self.data['comment'] = self._TCTRL_comment.GetValue().strip()

		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_type.SetText('')
		self._TCTRL_url.SetValue('')
		self._CHBOX_confidential.SetValue(False)
		self._TCTRL_comment.SetValue('')

		self._PRW_type.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_type.SetText(self.data['l10n_comm_type'])
		self._TCTRL_url.SetValue(self.data['url'])
		self._CHBOX_confidential.SetValue(self.data['is_confidential'])
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))

		self._TCTRL_url.SetFocus()
#------------------------------------------------------------
class cCommChannelsManagerPnl(gmListWidgets.cGenericListManagerPnl):
	"""A list for managing a person's comm channels."""
	def __init__(self, *args, **kwargs):

		try:
			self.__channel_owner = kwargs['identity']
			del kwargs['identity']
		except KeyError:
			self.__channel_owner = None

		gmListWidgets.cGenericListManagerPnl.__init__(self, *args, **kwargs)

		self.refresh_callback = self.refresh
		self.new_callback = self._add_comm
		self.edit_callback = self._edit_comm
		self.delete_callback = self._del_comm

		self.__init_ui()
		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def refresh(self, *args, **kwargs):
		if self.__channel_owner is None:
			self._LCTRL_items.set_string_items()
			return

		comms = self.__channel_owner.get_comm_channels()
		self._LCTRL_items.set_string_items (
			items = [ [
				gmTools.bool2str(c['is_confidential'], 'X', ''),
				c['l10n_comm_type'],
				c['url'],
				gmTools.coalesce(c['comment'], '')
			] for c in comms ]
		)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = comms)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_items.SetToolTip(_('List of known communication channels.'))
		self._LCTRL_items.set_columns(columns = [
			_('confidential'),
			_('Type'),
			_('Value'),
			_('Comment')
		])
	#--------------------------------------------------------
	def _add_comm(self):
		ea = cCommChannelEditAreaPnl(self, -1)
		ea.channel_owner = self.__channel_owner
		dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea)
		dlg.SetTitle(_('Adding new communications channel'))
		if dlg.ShowModal() == wx.ID_OK:
			return True
		return False
	#--------------------------------------------------------
	def _edit_comm(self, comm_channel):
		ea = cCommChannelEditAreaPnl(self, -1, comm_channel = comm_channel)
		ea.channel_owner = self.__channel_owner
		dlg = gmEditArea.cGenericEditAreaDlg2(self, -1, edit_area = ea, single_entry = True)
		dlg.SetTitle(_('Editing communications channel'))
		if dlg.ShowModal() == wx.ID_OK:
			return True
		return False
	#--------------------------------------------------------
	def _del_comm(self, comm):
		go_ahead = gmGuiHelpers.gm_show_question (
			_(	'Are you sure this communication channel\n'
				'can no longer be used ?'
			),
			_('Removing communication channel')
		)
		if not go_ahead:
			return False
		self.__channel_owner.unlink_comm_channel(comm_channel = comm)
		return True
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def __get_channel_owner(self):
		return self.__channel_owner

	def __set_channel_owner(self, channel_owner):
		self.__channel_owner = channel_owner
		self.refresh()

	channel_owner = property(__get_channel_owner, __set_channel_owner)

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
#	from Gnumed.business import gmPersonSearch

	#--------------------------------------------------------
#	def test_person_comms_pnl():
#		pat = gmPersonSearch.ask_for_patient()
#		app = wx.PyWidgetTester(size = (600, 400))
#		widget = cCommChannelsManagerPnl(app.frame, -1)
#		widget.identity = pat
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
#	test_person_comms_pnl()

#================================================================
