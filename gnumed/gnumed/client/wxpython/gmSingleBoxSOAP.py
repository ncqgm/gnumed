"""GnuMed single box clinical notes input widget

This widget was suggested by David Guest on the mailing list.

All it does is to provide a single multi-line textbox for
typing clear-text clinical notes which are stored in clin_note.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmSingleBoxSOAP.py,v $
# $Id: gmSingleBoxSOAP.py,v 1.8 2003-11-09 14:29:11 ncq Exp $
__version__ = "$Revision: 1.8 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, string

if __name__ == "__main__":
	sys.path.append ("../python-common/")
	import gmI18N

import gmDispatcher, gmPatient, gmSignals

from gmExceptions import ConstructorError
from wxPython.wx import *

wxID_BTN_save = wxNewId()
wxID_BTN_discard = wxNewId()
#============================================================
class gmSingleBoxSOAP(wxTextCtrl):
	"""if we separate it out like this it can transparently gain features"""
	def __init__(self, *args, **kwargs):
		wxTextCtrl.__init__(self, *args, **kwargs)
#============================================================
class gmSingleBoxSOAPPanel(wxPanel):
	def __init__(self, *args, **kwargs):
		#kwargs["style"] = wxDEFAULT_FRAME_STYLE
		wxPanel.__init__(self, *args, **kwargs)
		self.__do_layout()

		if not self.__register_events():
			raise ConstructorError, 'cannot register interests'

		self.__pat = gmPatient.gmCurrentPatient()
	#--------------------------------------------------------
	def __do_layout(self):
		# large box for free-text clinical notes
		self.soap_box = gmSingleBoxSOAP(
			self,
			-1,
			'',
			style = wxTE_MULTILINE
		)
		# buttons below that
		self.BTN_save = wxButton(self, wxID_BTN_save, _("save"))
		self.BTN_save.SetToolTipString(_('save clinical note in EMR'))
		self.BTN_discard = wxButton(self, wxID_BTN_discard, _("discard"))
		self.BTN_discard.SetToolTipString(_('discard clinical note'))
		szr_btns = wxBoxSizer(wxHORIZONTAL)
		szr_btns.Add(self.BTN_save, 1, wxALIGN_CENTER_HORIZONTAL, 0)
		szr_btns.Add(self.BTN_discard, 1, wxALIGN_CENTER_HORIZONTAL, 0)
		# arrange widgets
		szr_outer = wxStaticBoxSizer(wxStaticBox(self, -1, _("SOAP clinical notes")), wxVERTICAL)
		szr_outer.Add(self.soap_box, 1, wxEXPAND, 0)
		szr_outer.Add(szr_btns, 0, wxEXPAND, 0)
		# and do layout
		self.SetAutoLayout(1)
		self.SetSizer(szr_outer)
		szr_outer.Fit(self)
		szr_outer.SetSizeHints(self)
		self.Layout()
	#--------------------------------------------------------
	def __register_events(self):
		# wxPython events
		EVT_BUTTON(self.BTN_save, wxID_BTN_save, self._on_save_note)
		EVT_BUTTON(self.BTN_discard, wxID_BTN_discard, self._on_discard_note)

		# client internal signals
		gmDispatcher.connect(signal = gmSignals.activating_patient(), receiver = self._save_note)
		gmDispatcher.connect(signal = gmSignals.application_closing(), receiver = self._save_note)

		return 1
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_note(self, event):
		self._save_note()
		event.Skip()
	#--------------------------------------------------------
	def _on_discard_note(self, event):
		# FIXME: maybe ask for confirmation ?
		self.soap_box.SetValue('')
		event.Skip()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _save_note(self):
		# sanity checks
		if self.__pat is None:
			return 1
		if not self.soap_box.IsModified():
			return 1
		note = self.soap_box.GetValue()
		if string.strip(note) == '':
			return 1
		# now save note
		emr = self.__pat['clinical record']
		if emr is None:
			_log.Log(gmLog.lErr, 'cannot access clinical record of patient')
			return None
		if not emr.add_clinical_note(note):
			_log.Log(gmLog.lErr, 'error saving clinical note')
			return None
		else:
			self.soap_box.SetValue('')
			return 1
		return 1
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(gmSingleBoxSOAPPanel, -1)
	app.MainLoop()

#============================================================
# $Log: gmSingleBoxSOAP.py,v $
# Revision 1.8  2003-11-09 14:29:11  ncq
# - new API style in clinical record
#
# Revision 1.7  2003/10/26 01:36:13  ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.6  2003/07/05 12:57:23  ncq
# - catch one more error on saving note
#
# Revision 1.5  2003/06/26 22:26:04  ncq
# - streamlined _save_note()
#
# Revision 1.4  2003/06/25 22:51:24  ncq
# - now also handle signale application_closing()
#
# Revision 1.3  2003/06/24 12:57:05  ncq
# - actually connect to backend
# - save note on patient change and on explicit save request
#
# Revision 1.2  2003/06/22 16:20:33  ncq
# - start backend connection
#
# Revision 1.1  2003/06/19 16:50:32  ncq
# - let's make something simple but functional first
#
#
