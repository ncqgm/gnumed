#!/usr/bin/python
#############################################################################
#
# gmLogFrame - A top level frame for universal log output in GNUMed
# ---------------------------------------------------------------------------
#    log output in a separate window that survives the client
#    when it goes down for postmortem analysis
#    To use it,
#    - create an instance of this widget
#    - redirect wxLog to the text control widget of that instance
#    - or write directly to the text control widget
#
#    EXAMPLE:
#        log = LogFrame(None, -1, _('GNUMed Debug Log'), size=(600,480))
#        wxLog_SetActiveTarget(wxLogTextCtrl(log.GetLogWidget()))
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	10.07.2001 hherb initial implementation, mostly untested
#
# @TODO:
############################################################################

from wxPython.wx import *

class LogFrame(wxFrame):
	"""The GNUMed log output goes here
	EXAMPLE:
	log = LogFrame(None, -1, _('GNUMed Debug Log'), size=(600,480))
	wxLog_SetActiveTarget(wxLogTextCtrl(log.GetLogWidget()))
	"""

	def __init__(self, parent, id, title, size=wxPyDefaultSize):

		wxFrame.__init__(self, parent, -1, title, size, \
				style = wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE)

		vb = wxBoxSizer(wxVERTICAL)
		self.txt= wxTextCtrl(self, -1, style=wxTE_MULTILINE)
		vb.Add(self.txt, 1, wxEXPAND|wxALL)
		self.Show(true)


	def GetLogWidget(self):
		return self.txt
