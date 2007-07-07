"""GNUmed list controls and widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmListWidgets.py,v $
# $Id: gmListWidgets.py,v 1.8 2007-07-07 12:42:00 ncq Exp $
__version__ = "$Revision: 1.8 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"


import sys


import wx
import wx.lib.mixins.listctrl as listmixins


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.business import gmPerson
from Gnumed.pycommon import gmTools, gmDispatcher
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxGladeWidgets import wxgGenericListSelectorDlg

#================================================================
def get_choice_from_list(parent=None, msg=None, caption=None, choices=None):

	if msg is None:
		msg = _('programmer forgot to specify info message')

	if caption is None:
		caption = _('generic single choice dialog')

	dlg = wx.SingleChoiceDialog (
		parent = None,
		message = msg,
		caption = caption,
		choices = choices,
		style = wx.OK | wx.CANCEL | wx.CENTRE
	)
	btn_pressed = dlg.ShowModal()
	sel = dlg.GetSelection()
	dlg.Destroy()

	if btn_pressed == wx.ID_OK:
		return sel

	return False
#================================================================
def get_choices_from_list(parent=None, msg=None, caption=None, choices=None, selections=None, columns=None, data=None):

	if msg is None:
		msg = _('programmer forgot to specify info message')

	if caption is None:
		caption = _('generic multi choice dialog')

	dlg = cGenericListSelectorDlg(parent, -1, caption)
	dlg.set_columns(columns = columns)
	dlg.set_string_items(items = choices)
	if selections is not None:
		dlg.set_selections(selections = selections)
	if data is not None:
		dlg.set_data(data=data)

	btn_pressed = dlg.ShowModal()
	sels = dlg.get_selected_item_data()
	dlg.Destroy()

	if btn_pressed == wx.ID_OK:
		return sels

	return None
#----------------------------------------------------------------
class cGenericListSelectorDlg(wxgGenericListSelectorDlg.wxgGenericListSelectorDlg):

	def __init__(self, *args, **kwargs):

#		try: msg = kwargs['msg']
#		except KeyError: msg = None

		wxgGenericListSelectorDlg.wxgGenericListSelectorDlg.__init__(self, *args, **kwargs)
	#------------------------------------------------------------
	def set_columns(self, columns=None):
		self._LCTRL_items.set_columns(columns = columns)
	#------------------------------------------------------------
	def set_string_items(self, items = None):
		self._LCTRL_items.set_string_items(items = items)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.Select(0)
	#------------------------------------------------------------
	def set_selections(self, selections = None):
		self._LCTRL_items.set_selections(selections = selections)
	#------------------------------------------------------------
	def set_data(self, data = None):
		self._LCTRL_items.set_data(data = data)
	#------------------------------------------------------------
	def get_selected_item_data(self, only_one=False):
		return self._LCTRL_items.get_selected_item_data(only_one=only_one)
	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_list_item_selected(self, event):
		self._BTN_ok.Enable(True)
		self._BTN_ok.SetDefault()
	#------------------------------------------------------------
	def _on_list_item_deselected(self, event):
		if self._LCTRL_items.get_selected_items(only_one=True) == -1:
			self._BTN_ok.Enable(False)
			self._BTN_cancel.SetDefault()
#================================================================
class cReportListCtrl(wx.ListCtrl, listmixins.ListCtrlAutoWidthMixin):

	def __init__(self, *args, **kwargs):

		try:
			kwargs['style'] = kwargs['style'] | wx.LC_REPORT
		except KeyError:
			kwargs['style'] = wx.LC_REPORT

		self.__is_single_selection = ((kwargs['style'] & wx.LC_SINGLE_SEL) != 0)

		wx.ListCtrl.__init__(self, *args, **kwargs)
		listmixins.ListCtrlAutoWidthMixin.__init__(self)
	#------------------------------------------------------------
	# setters
	#------------------------------------------------------------
	def set_columns(self, columns=None):
		"""(Re)define the columns.

		Note that this will (have to) delete the items.
		"""
		self.ClearAll()
		if columns is None:
			return
		for idx in range(len(columns)):
			self.InsertColumn(idx, columns[idx])
	#------------------------------------------------------------
	def set_column_widths(self, widths=None):
		if widths is None:
			for idx in range(self.GetColumnCount()):
				self.SetColumnWidth(col = idx, width = wx.LIST_AUTOSIZE)
			return

		for idx in range(len(widths)):
			self.SetColumnWidth(col = idx, width = widths[idx])
	#------------------------------------------------------------
	def set_string_items(self, items = None):
		"""All item members must be unicode()able or None."""

		self.DeleteAllItems()

		if items is None:
			return

		for item in items:
			col_val = unicode(gmTools.coalesce(item[0], u''))
			row_num = self.InsertStringItem(index = sys.maxint, label = col_val)
			for col_idx in range(1, len(item)):
				col_val = unicode(gmTools.coalesce(item[col_idx], u''))
				self.SetStringItem(index = row_num, col = col_idx, label = col_val)

		self.__data = items
	#------------------------------------------------------------
	def set_data(self, data = None):
		"""<data must be a list corresponding to the item indices>"""
		self.__data = data
	#------------------------------------------------------------
	def set_selections(self, selections=None):
		for idx in selections:
			self.Select(idx = idx, on = 1)
	#------------------------------------------------------------
	# getters
	#------------------------------------------------------------
	def get_item_data(self, item_idx = None):
		return self.__data[item_idx]
	#------------------------------------------------------------
	def get_selected_items(self, only_one=False):

		if self.__is_single_selection or only_one:
			return self.GetFirstSelected()

		items = []
		idx = self.GetFirstSelected()
		while idx != -1:
			items.append(idx)
			idx = self.GetNextSelected(idx)

		return items
	#------------------------------------------------------------
	def get_selected_item_data(self, only_one=False):

		if self.__is_single_selection or only_one:
			return self.__data[self.GetFirstSelected()]

		data = []
		idx = self.GetFirstSelected()
		while idx != -1:
			data.append(self.__data[idx])
			idx = self.GetNextSelected(idx)

		return data
	#------------------------------------------------------------
	def deselect_selected_item(self):
		self.Select(idx = self.GetFirstSelected(), on = 0)
#================================================================
class cPatientListingCtrl(cReportListCtrl):

	def __init__(self, *args, **kwargs):
		"""<patient_key> must index or name a column in self.__data"""
		try:
			self.patient_key = kwargs['patient_key']
			del kwargs['patient_key']
		except KeyError:
			self.patient_key = None

		cReportListCtrl.__init__(self, *args, **kwargs)

		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_item_activated, self)
	#------------------------------------------------------------
	# event handling
	#------------------------------------------------------------
	def _on_list_item_activated(self, evt):
		if self.patient_key is None:
			gmDispatcher.send(signal = 'statustext', msg = _('List not known to be patient-related.'))
			return
		data = self.get_selected_item_data(only_one=True)
		try:
			pat_data = data[self.patient_key]
		except (KeyError, IndexError, TypeError):
			gmGuiHelpers.gm_show_info (
				_(
				'Cannot activate patient.\n\n'
				'The row does not contain a column\n'
				'named or indexed "%s".\n\n'
				) % self.patient_key,
				_('activating patient from list')
			)
			return
		try:
			pat_pk = int(pat_data)
			pat = gmPerson.cIdentity(aPK_obj = pat_pk)
		except (ValueError, TypeError):
			searcher = gmPerson.cPatientSearcher_SQL()
			idents = searcher.get_identities(pat_data)
			if len(idents) == 0:
				gmDispatcher.send(signal = 'statustext', msg = _('No matching patient found.'))
				return
			if len(idents) == 1:
				pat = idents[0]
			else:
				dlg = cSelectPersonFromListDlg(parent=wx.GetTopLevelParent(self), id=-1)
				dlg.set_persons(persons=idents)
				result = dlg.ShowModal()
				if result == wx.ID_CANCEL:
					dlg.Destroy()
					return
				ident = dlg.get_selected_person()
				dlg.Destroy()

		gmPerson.set_active_patient(patient = pat)
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	#------------------------------------------------------------
	def test_wxMultiChoiceDialog():
		app = wx.PyWidgetTester(size = (400, 500))
		dlg = wx.MultiChoiceDialog (
			parent = None,
			message = 'test message',
			caption = 'test caption',
			choices = ['a', 'b', 'c', 'd', 'e']
		)
		dlg.ShowModal()
		sels = dlg.GetSelections()
		print "selected:"
		for sel in sels:
			print sel
	#------------------------------------------------------------
	def test_get_choices_from_list():
		app = wx.PyWidgetTester(size = (200, 50))
		chosen = get_choices_from_list (
			caption = 'select health issues',
			choices = [['D.M.II', '4'], ['MS', '3'], ['Fraktur', '2']],
			columns = ['issue', 'no of episodes']
		)
		print "chosen:"
		print chosen
	#------------------------------------------------------------
	def test_pat_list_ctrl():
		app = wx.PyWidgetTester(size = (400, 500))
		lst = cPatientListingCtrl(app.frame, patient_key = 0)
		lst.set_columns(['name', 'comment'])
		lst.set_string_items([
			['Kirk', 'Kirk by name'],
			['#12', 'Kirk by ID'],
			['unknown', 'unknown patient']
		])
#		app.SetWidget(cPatientListingCtrl, patient_key = 0)
		app.frame.Show()
		app.MainLoop()
	#------------------------------------------------------------

#	test_get_choices_from_list()
#	test_wxMultiChoiceDialog()
	test_pat_list_ctrl()

#================================================================
# $Log: gmListWidgets.py,v $
# Revision 1.8  2007-07-07 12:42:00  ncq
# - set_string_items now applies unicode() to all item members
# - cPatientListingCtrl and test suite
#
# Revision 1.7  2007/06/28 12:38:15  ncq
# - fix logic reversal in get_selected_*()
#
# Revision 1.6  2007/06/18 20:33:56  ncq
# - add get_choice(s)_from_list()
# - add cGenericListSelectorDlg
# - add set_string_items()/set_selections()/get_selected_items()
# - improve test suite
#
# Revision 1.5  2007/06/12 16:03:02  ncq
# - properly get rid of all columns in set_columns()
#
# Revision 1.4  2007/04/09 18:51:47  ncq
# - add support for multiple selections and auto-setting the widths
#
# Revision 1.3  2007/03/18 14:09:31  ncq
# - add set_columns() and set_column_widths()
#
# Revision 1.2  2006/12/11 20:50:45  ncq
# - get_selected_item_data()
# - deselect_selected_item()
#
# Revision 1.1  2006/07/23 20:34:50  ncq
# - list controls and widgets
#
#