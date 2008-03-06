#======================================================================
# GnuMed allergies notebook plugin
# --------------------------------
#
# @copyright: author
#======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmAllergiesPlugin.py,v $
# $Id: gmAllergiesPlugin.py,v 1.8 2008-03-06 18:32:30 ncq Exp $
__version__ = "$Revision: 1.8 $"
__author__ = "R.Terry, S.J.Tan, K.Hilbert"
__license__ = "GPL (details at http://www.gnu.org)"

import logging


import wx


from Gnumed.wxpython import gmPlugin, gmAllergyWidgets

_log = logging.getLogger('gm.ui')
_log.info(__version__)

#======================================================================
class gmAllergiesPlugin(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate the allergies window."""

	__icons = {
"""icon_letter_A""": 'x\xda\xd3\xc8)0\xe4\nV74S\x00"\x13\x05Cu\xae\xc4`\xf5|\x85d\x05e\x17W\x10\
\x04\xf3\xf5@|77\x03 \x00\xf3\x15\x80|\xbf\xfc\xbcT0\'\x02$i\xee\x06\x82PIT@\
HPO\x0f\xab`\x04\x86\xa0\x9e\x1e\\)\xaa`\x04\x9a P$\x02\xa6\x14Y0\x1f\xa6\
\x14&\xa8\x07\x05h\x82\x11\x11 \xfd\x11H\x82 1\x84[\x11\x82Hn\x85i\x8f\x80\
\xba&"\x82\x08\xbf\x13\x16\xd4\x03\x00\xe4\xa2I\x9c'
}

	tab_name = _('Allergies')

	def name (self):
		return gmAllergiesPlugin.tab_name

	def GetWidget (self, parent):
#		self._widget = gmAllergyWidgets.cAllergyPanel(parent, -1)
#		return self._widget
		pass

	def MenuInfo (self):
		return ('view', '&Allergies')

	def can_receive_focus(self):
		# need patient
		if not self._verify_patient_avail():
			return None
		return 1
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	#app.SetWidget(gmAllergyWidgets.cAllergyPanel, -1)
	app.MainLoop()
#======================================================================
# $Log: gmAllergiesPlugin.py,v $
# Revision 1.8  2008-03-06 18:32:30  ncq
# - standard lib logging only
#
# Revision 1.7  2007/10/12 07:28:24  ncq
# - lots of import related cleanup
#
# Revision 1.6  2007/05/21 14:50:05  ncq
# - cleanup
#
# Revision 1.5  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.4  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.3  2004/10/11 20:12:09  ncq
# - turn into new-style notebook plugin
#
# Revision 1.2  2004/08/04 17:16:02  ncq
# - wx.NotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.1  2004/07/17 21:16:39  ncq
# - cleanup/refactor allergy widgets:
#   - Horst space plugin added
#   - Richard space plugin separated out
#   - plugin independant GUI code aggregated
#   - allergies edit area factor out from generic edit area file
#
