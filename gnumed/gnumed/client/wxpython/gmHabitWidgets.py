"""GNUmed habits widgets."""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import sys
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmDateTime

from Gnumed.wxpython import gmEditArea


_log = logging.getLogger('gm.habits')

#================================================================
def edit_smoking_status(parent=None, emr=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	ea = cSmokingEAPnl(parent = parent, id = -1, emr = emr)
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = True)
	dlg.SetTitle(_('Editing smoking status'))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
	return False

#----------------------------------------------------------------
def manage_smoking_status(parent=None, patient=None):
	return edit_smoking_status(parent = parent, emr = patient.emr)

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgSmokingEAPnl

class cSmokingEAPnl(wxgSmokingEAPnl.wxgSmokingEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		data = kwargs['emr']
		del kwargs['emr']

		wxgSmokingEAPnl.wxgSmokingEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.data = data
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

		if not self._DPRW_last_confirmed.is_valid_timestamp(allow_empty = False):
			validity = False
			self._DPRW_last_confirmed.SetFocus()

		if not self._DPRW_quit_when.is_valid_timestamp(allow_empty = True):
			validity = False
			self._DPRW_quit_when.SetFocus()

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):

		if self._RBTN_unknown_smoking_status.GetValue() is True:
			ever = None
		elif self._RBTN_never_smoked.GetValue() is True:
			ever = False
		else:
			ever = True

		details = {
			'comment': self._TCTRL_comment.GetValue(),
			'quit_when': self._DPRW_quit_when.date,
			'last_confirmed': self._DPRW_last_confirmed.date
		}

		self.data.smoking_status = (ever, details)

		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		return self._save_as_new()
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._RBTN_unknown_smoking_status.SetValue(True)
		self._TCTRL_comment.SetValue(u'')
		self._DPRW_quit_when.SetText(u'', None)
		self._DPRW_last_confirmed.SetText(data = gmDateTime.pydt_now_here())
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_from_existing()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		smoker, details = self.data.smoking_status
		if smoker is None:
			self._RBTN_unknown_smoking_status.SetValue(True)
		elif smoker is False:
			self._RBTN_never_smoked.SetValue(True)
		else:
			self._RBTN_smokes.SetValue(True)

		if details is not None:
			self._TCTRL_comment.SetValue(gmTools.coalesce(details['comment'], u''))
			self._DPRW_quit_when.SetText(data = details['quit_when'])
			self._DPRW_last_confirmed.SetText(data = details['last_confirmed'])

		self._TCTRL_comment.SetFocus()
	#----------------------------------------------------------------

#================================================================
# main
#================================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

#	def test_message_inbox():
#		app = wx.PyWidgetTester(size = (800, 600))
#		app.SetWidget(cProviderInboxPnl, -1)
#		app.MainLoop()

#	def test_msg_ea():
#		app = wx.PyWidgetTester(size = (800, 600))
#		app.SetWidget(cInboxMessageEAPnl, -1)
#		app.MainLoop()


	#test_message_inbox()
	#test_msg_ea()
