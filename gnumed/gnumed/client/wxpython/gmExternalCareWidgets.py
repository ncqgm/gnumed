"""GNUmed external patient care widgets."""
#================================================================
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"

# std lib
import sys
import logging
#import os.path


# 3rd party
import wx


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
#from Gnumed.pycommon import gmMimeLib
#from Gnumed.pycommon import gmDateTime
#from Gnumed.pycommon import gmPrinting
#from Gnumed.pycommon import gmShellAPI

from Gnumed.business import gmExternalCare
from Gnumed.business import gmPerson

from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmEditArea
#from Gnumed.wxpython import gmRegetMixin
#from Gnumed.wxpython import gmGuiHelpers


_log = logging.getLogger('gm.ui')

#============================================================
def manage_external_care(parent=None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.get_emr()

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#-----------------------------------------
	def edit(external_care_item=None):
		return edit_external_care_item(parent = parent, external_care_item = external_care_item)
	#-----------------------------------------
	def delete(external_care_item=None):
		if gmExternalCare.delete_external_care(pk_external_care = external_care_item['pk_external_care']):
			return True

		gmDispatcher.send (
			signal = u'statustext',
			msg = _('Cannot delete external care item.'),
			beep = True
		)
		return False
	#------------------------------------------------------------
	def get_tooltip(data):
		if data is None:
			return None
		return u'\n'.join(data.format(with_health_issue = True))
	#------------------------------------------------------------
	def refresh(lctrl):
		care = emr.get_external_care_items(order_by = u'issue, provider, unit, org')
		items = [ [
			c['issue'],
			gmTools.coalesce(c['provider'], u''),
			u'%s @ %s' % (
				c['unit'],
				c['organization']
			),
			gmTools.coalesce(c['comment'], u'')
		] for c in care ]
		lctrl.set_string_items(items)
		lctrl.set_data(care)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('External care of this patient.'),
		caption = _('Showing external care network.'),
		columns = [ _('Care target'), _('Provider'), _('Location'), _('Comment') ],
		single_selection = True,
		can_return_empty = True,
		ignore_OK_button = True,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		list_tooltip_callback = get_tooltip
#		left_extra_button=None,
#		middle_extra_button=None,
#		right_extra_button=None
	)

#----------------------------------------------------------------
def edit_external_care(parent=None, external_care_item=None):
	ea = cExternalCareEAPnl(parent = parent, id = -1)
	ea.data = external_care_item
	ea.mode = gmTools.coalesce(external_care_item, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea, single_entry = True)
	dlg.SetTitle(gmTools.coalesce(external_care_item, _('Adding external care'), _('Editing external care')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.Destroy()
		return True
	dlg.Destroy()
	return False
