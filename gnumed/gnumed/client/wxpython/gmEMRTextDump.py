"""GnuMed scrolled window text dump of EMR content.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEMRTextDump.py,v $
# $Id: gmEMRTextDump.py,v 1.8 2004-02-25 09:46:22 ncq Exp $
__version__ = "$Revision: 1.8 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, string
import gmLog
_log = gmLog.gmDefLog

if __name__ == "__main__":
	sys.path.append ("../pycommon/")
	import gmI18N

import gmDispatcher, gmPatient, gmSignals

from gmExceptions import ConstructorError
from wxPython.wx import *
#============================================================
class gmEMRDumpPanel(wxPanel):
	def __init__(self, *args, **kwargs):
		wxPanel.__init__(self, *args, **kwargs)
		self.__do_layout()

		if not self.__register_events():
			raise ConstructorError, 'cannot register interests'
	#--------------------------------------------------------
	def __do_layout(self):
		self.txt = wxTextCtrl(
			self,
			-1,
			_('No EMR data loaded.'),
			style = wxTE_MULTILINE | wxTE_READONLY 
		)
		# arrange widgets
		szr_outer = wxStaticBoxSizer(wxStaticBox(self, -1, _("EMR text dump")), wxVERTICAL)
		szr_outer.Add(self.txt, 1, wxEXPAND, 0)
		# and do layout
		self.SetAutoLayout(1)
		self.SetSizer(szr_outer)
		szr_outer.Fit(self)
		szr_outer.SetSizeHints(self)
		self.Layout()
	#--------------------------------------------------------
	def __register_events(self):
		# client internal signals
		gmDispatcher.connect(signal = gmSignals.patient_selected(), receiver = self._retrieve_EMR_text)
		return 1
	#--------------------------------------------------------
	def _retrieve_EMR_text(self):
		wxCallAfter(self.__retrieve_EMR_text)
	#--------------------------------------------------------
	def __retrieve_EMR_text(self):
		pat = gmPatient.gmCurrentPatient()
		# this should not really happen
		if not pat.is_connected():
			_log.Log(gmLog.lErr, 'no active patient, cannot get EMR text dump')
			self.txt.SetValue(_('Currently there is no active patient. Cannot retrieve EMR text.'))
			return None
		emr = pat['clinical record']
		if emr is None:
			_log.Log(gmLog.lErr, 'cannot get EMR text dump')
			self.txt.SetValue(_(
				'An error occurred while retrieving a text\n'
				'dump of the EMR for the active patient.\n\n'
				'Please check the log file for details.'
			))
			return None
		dump = emr.get_text_dump()
		if dump is None:
			_log.Log(gmLog.lErr, 'cannot get EMR text dump')
			self.txt.SetValue(_(
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
		self.txt.SetValue(txt)
		return 1
#============================================================
class gmScrolledEMRTextDump(wxScrolledWindow):
	def __init__(self, parent):
		wxScrolledWindow.__init__(
			self,
			parent,
			-1
		)

#		self.txt = wxStaticText(
#			self,
#			-1,
#			_('No EMR data loaded.'),
#			style = wxST_NO_AUTORESIZE
#			style = wxALIGN_LEFT
#		)
		self.txt = wxTextCtrl(
			self,
			-1,
			_('No EMR data loaded.'),
			style = wxTE_MULTILINE | wxTE_READONLY 
		)
		szr_vbox_main = wxBoxSizer(wxVERTICAL)
		szr_vbox_main.Add(self.txt, 0, wxEXPAND | wxCENTER | wxALL, 5)

		self.SetAutoLayout(1)
		self.SetSizer(szr_vbox_main)
		szr_vbox_main.Fit(self)
		szr_vbox_main.SetSizeHints(self)
		szr_vbox_main.SetVirtualSizeHints(self)
		self.Layout()

		# scroll back to top after initial events
		self.EnableScrolling(0, 1)
		self.SetScrollRate(0, 20)
		wxCallAfter(self.Scroll, 0, 0)


#============================================================
# $Log: gmEMRTextDump.py,v $
# Revision 1.8  2004-02-25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.7  2004/02/05 23:49:52  ncq
# - use wxCallAfter()
#
# Revision 1.6  2003/11/17 10:56:37  sjtan
#
# synced and commiting.
#
# Revision 1.5  2003/11/11 18:21:30  ncq
# - cleanup
#
# Revision 1.4  2003/11/09 14:27:46  ncq
# - clinical record has new API style
#
# Revision 1.3  2003/10/26 01:36:13  ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.2  2003/07/19 20:20:59  ncq
# - use panel instead of scrolled window so it actually works nicely
# - maybe later put panel inside scrolled window...
# - code cleanup
#
# Revision 1.1  2003/07/03 15:27:08  ncq
# - first chekin
