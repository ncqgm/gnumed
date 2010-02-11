"""
This is a no-frills document display handler for the
GNUmed medical document database.

It knows nothing about the documents itself. All it does
is to let the user select a page to display and tries to
hand it over to an appropriate viewer.

For that it relies on proper mime type handling at the OS level.
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmShowMedDocs.py,v $
__version__ = "$Revision: 1.78 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import os.path, sys, logging


import wx


from Gnumed.wxpython import gmDocumentWidgets, gmPlugin, images_Archive_plugin


_log = logging.getLogger('gm.ui')
_log.info(__version__)
#================================================================
class gmShowMedDocs(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate document tree."""

	tab_name = _("Documents")

	def name(self):
		return gmShowMedDocs.tab_name
	#--------------------------------------------------------
	def GetWidget(self, parent):
		self._widget = gmDocumentWidgets.cSelectablySortedDocTreePnl(parent, -1)
		return self._widget
	#--------------------------------------------------------
	def MenuInfo(self):
		return ('emr', _('&Documents review'))
	#--------------------------------------------------------
	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
	#--------------------------------------------------------
	def _on_raise_by_signal(self, **kwds):
		if not gmPlugin.cNotebookPlugin._on_raise_by_signal(self, **kwds):
			return False

		try:
			if kwds['sort_mode'] == 'review':
				self._widget._on_sort_by_review_selected(None)
		except KeyError:
			pass

		return True
	#--------------------------------------------------------
#	def populate_toolbar (self, tb, widget):
#		wxID_TB_BTN_show_page = wx.NewId()
#		tool1 = tb.AddTool(
#			wxID_TB_BTN_show_page,
#			images_Archive_plugin.getreportsBitmap(),
#			shortHelpString=_("show document"),
#			isToggle=False
#		)
#		wx.EVT_TOOL(tb, wxID_TB_BTN_show_page, self._widget._doc_tree.display_selected_part)
#		tb.AddControl(wx.StaticBitmap(
#			tb,
#			-1,
#			images_Archive_plugin.getvertical_separator_thinBitmap(),
#			wx.DefaultPosition,
#			wx.DefaultSize
#		))
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	pass
#================================================================
