"""GnuMed scrolled window text dump of EMR content.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEMRTextDump.py,v $
# $Id: gmEMRTextDump.py,v 1.1 2003-07-03 15:27:08 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, string

if __name__ == "__main__":
	sys.path.append ("../python-common/")
	import gmI18N

import gmDispatcher, gmTmpPatient, gmSignals

from gmExceptions import ConstructorError
from wxPython.wx import *

#============================================================
class gmScrolledEMRTextDump(wxScrolledWindow):
	def __init__(self, parent):
		wxScrolledWindow.__init__(
			self,
			parent,
			-1
		)

		self.txt = wxStaticText(
			self,
			-1,
			_('No EMR data loaded.'),
#			style = wxALIGN_LEFT
		)
#		 | wxST_NO_AUTORESIZE
		szr_vbox_main = wxBoxSizer(wxVERTICAL)
		szr_vbox_main.Add(self.txt, 0, wxCENTER | wxALL, 5)

		# The following is all that is needed to integrate the sizer and the
		# scrolled window.  In this case we will only support vertical scrolling.
		self.SetSizer(szr_vbox_main)
		self.EnableScrolling(0, 1)
		self.SetScrollRate(0, 20)
		szr_vbox_main.SetVirtualSizeHints(self)

		if not self.__register_events():
			raise ConstructorError, 'cannot register signal interests'
		# scroll back to top after initial events
		wxCallAfter(self.Scroll, 0, 0)
	#--------------------------------------------------------
	def __register_events(self):
		# wxPython events
#		EVT_BUTTON(self.BTN_save, wxID_BTN_save, self._on_save_note)
#		EVT_BUTTON(self.BTN_discard, wxID_BTN_discard, self._on_discard_note)

		# client internal signals
		gmDispatcher.connect(signal = gmSignals.patient_selected(), receiver = self._retrieve_EMR_text)

		return 1		
	#--------------------------------------------------------
	def _retrieve_EMR_text(self):
		pat = gmTmpPatient.gmCurrentPatient()
		# this should not really happen
		if not pat.is_connected():
			_log.Log(gmLog.lErr, 'no active patient, cannot get EMR text dump')
			self.txt.SetLabel(_('Currently there is no active patient. Cannot retrieve EMR text.'))
			return None
		emr = pat['clinical record']
		if emr is None:
			_log.Log(gmLog.lErr, 'cannot get EMR text dump')
			self.txt.SetLabel(_(
				'An error occurred while retrieving a text\n'
				'dump of the EMR for the active patient.\n\n'
				'Please check the log file for details.'
			))
			return None
		dump = emr['text dump']
		if dump is None:
			_log.Log(gmLog.lErr, 'cannot get EMR text dump')
			self.txt.SetLabel(_(
				'An error occurred while retrieving a text\n'
				'dump of the EMR for the active patient.\n\n'
				'Please check the log file for details.'
			))
			return None
		keys = dump.keys()
		keys.sort()
		txt = ''
		for age in keys:
			for line in dump[age]:
				txt = txt + "%s\n" % line
		self.txt.SetLabel(txt)
		return 1
#============================================================
# $Log: gmEMRTextDump.py,v $
# Revision 1.1  2003-07-03 15:27:08  ncq
# - first chekin
#
