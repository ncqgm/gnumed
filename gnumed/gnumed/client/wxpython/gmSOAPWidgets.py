"""GnuMed SOAP related widgets.

The code in here is independant of gmPG.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmSOAPWidgets.py,v $
# $Id: gmSOAPWidgets.py,v 1.1 2005-01-10 16:14:35 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import sys, string

from Gnumed.pycommon import gmDispatcher, gmSignals, gmI18N
from Gnumed.business import gmPatient
from Gnumed.pycommon.gmExceptions import ConstructorError

from wxPython import wx
#============================================================



#============================================================
class gmSingleBoxSOAP(wx.wxTextCtrl):
	"""if we separate it out like this it can transparently gain features"""
	def __init__(self, *args, **kwargs):
		wx.wxTextCtrl.__init__(self, *args, **kwargs)
#============================================================
class gmSingleBoxSOAPPanel(wx.wxPanel):
	"""Single Box free text SOAP input.

	This widget was suggested by David Guest on the mailing
	list. All it does is provide a single multi-line textbox
	for typing free-text clinical notes which are stored as
	Subjective.
	"""
	def __init__(self, *args, **kwargs):
		wx.wxPanel.__init__(self, *args, **kwargs)
		self.__do_layout()
		self.__pat = gmPatient.gmCurrentPatient()
		if not self.__register_events():
			raise ConstructorError, 'cannot register interests'
	#--------------------------------------------------------
	def __do_layout(self):
		# large box for free-text clinical notes
		self.__soap_box = gmSingleBoxSOAP (
			self,
			-1,
			'',
			style = wx.wxTE_MULTILINE
		)
		# buttons below that
		self.__BTN_save = wx.wxButton(self, wx.wxNewId(), _("save"))
		self.__BTN_save.SetToolTipString(_('save clinical note in EMR'))
		self.__BTN_discard = wx.wxButton(self, wx.wxNewId(), _("discard"))
		self.__BTN_discard.SetToolTipString(_('discard clinical note'))
		szr_btns = wx.wxBoxSizer(wx.wxHORIZONTAL)
		szr_btns.Add(self.__BTN_save, 1, wx.wxALIGN_CENTER_HORIZONTAL, 0)
		szr_btns.Add(self.__BTN_discard, 1, wx.wxALIGN_CENTER_HORIZONTAL, 0)
		# arrange widgets
		szr_outer = wx.wxStaticBoxSizer(wx.wxStaticBox(self, -1, _("SOAP clinical notes")), wx.wxVERTICAL)
		szr_outer.Add(self.__soap_box, 1, wx.wxEXPAND, 0)
		szr_outer.Add(szr_btns, 0, wx.wxEXPAND, 0)
		# and do layout
		self.SetAutoLayout(1)
		self.SetSizer(szr_outer)
		szr_outer.Fit(self)
		szr_outer.SetSizeHints(self)
		self.Layout()
	#--------------------------------------------------------
	def __register_events(self):
		# wxPython events
		wx.EVT_BUTTON(self.__BTN_save, self.__BTN_save.GetId(), self._on_save_note)
		wx.EVT_BUTTON(self.__BTN_discard, self.__BTN_discard.GetId(), self._on_discard_note)

		# client internal signals
		gmDispatcher.connect(signal = gmSignals.activating_patient(), receiver = self._save_note)
		gmDispatcher.connect(signal = gmSignals.application_closing(), receiver = self._save_note)

		return True
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_note(self, event):
		self.__save_note()
		#event.Skip()
	#--------------------------------------------------------
	def _on_discard_note(self, event):
		# FIXME: maybe ask for confirmation ?
		self.__soap_box.SetValue('')
		#event.Skip()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _save_note(self):
		wx.wxCallAfter(self.__save_note)
	#--------------------------------------------------------
	def __save_note(self):
		# sanity checks
		if self.__pat is None:
			return True
		if not self.__pat.is_connected():
			return True
		if not self.__soap_box.IsModified():
			return True
		note = self.__soap_box.GetValue()
		if string.strip(note) == '':
			return True
		# now save note
		emr = self.__pat.get_clinical_record()
		if emr is None:
			_log.Log(gmLog.lErr, 'cannot access clinical record of patient')
			return False
		if not emr.add_clin_narrative(note, soap_cat='s'):
			_log.Log(gmLog.lErr, 'error saving clinical note')
			return False
		self.__soap_box.SetValue('')
		return True
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":
	app = wx.wxPyWidgetTester(size = (600, 600))
	app.SetWidget(gmSingleBoxSOAPPanel, -1)
	app.MainLoop()

#============================================================
# $Log: gmSOAPWidgets.py,v $
# Revision 1.1  2005-01-10 16:14:35  ncq
# - soap widgets independant of the backend (gmPG) live in here
#
# Revision 1.13	 2004/06/30 20:33:41  ncq
# - add_clinical_note() -> add_clin_narrative()
#
# Revision 1.12	 2004/03/09 07:54:32  ncq
# - can call __save_note() from button press handler directly
#
# Revision 1.11	 2004/03/08 23:35:10  shilbert
# - adapt to new API from Gnumed.foo import bar
#
# Revision 1.10	 2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.9	2004/02/05 23:49:52	 ncq
# - use wxCallAfter()
#
# Revision 1.8	2003/11/09 14:29:11	 ncq
# - new API style in clinical record
#
# Revision 1.7	2003/10/26 01:36:13	 ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.6	2003/07/05 12:57:23	 ncq
# - catch one more error on saving note
#
# Revision 1.5	2003/06/26 22:26:04	 ncq
# - streamlined _save_note()
#
# Revision 1.4	2003/06/25 22:51:24	 ncq
# - now also handle signale application_closing()
#
# Revision 1.3	2003/06/24 12:57:05	 ncq
# - actually connect to backend
# - save note on patient change and on explicit save request
#
# Revision 1.2	2003/06/22 16:20:33	 ncq
# - start backend connection
#
# Revision 1.1	2003/06/19 16:50:32	 ncq
# - let's make something simple but functional first
#
#
