"""GnuMed scrolled window text dump of EMR content.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEMRTextDump.py,v $
# $Id: gmEMRTextDump.py,v 1.20 2008-01-30 14:03:41 ncq Exp $
__version__ = "$Revision: 1.20 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, string


import wx


from Gnumed.pycommon import gmLog, gmDispatcher, gmExceptions
from Gnumed.business import gmPerson


_log = gmLog.gmDefLog
#============================================================
class gmEMRDumpPanel(wx.Panel):
	def __init__(self, *args, **kwargs):
		wx.Panel.__init__(self, *args, **kwargs)
		self.__do_layout()

		if not self.__register_events():
			raise gmExceptions.ConstructorError, 'cannot register interests'
	#--------------------------------------------------------
	def __do_layout(self):
		self.txt = wx.TextCtrl(
			self,
			-1,
			_('No EMR data loaded.'),
			style = wx.TE_MULTILINE | wx.TE_READONLY 
		)
		# arrange widgets
		szr_outer = wx.StaticBoxSizer(wx.StaticBox(self, -1, _("EMR text dump")), wx.VERTICAL)
		szr_outer.Add(self.txt, 1, wx.EXPAND, 0)
		# and do layout
		self.SetAutoLayout(1)
		self.SetSizer(szr_outer)
		szr_outer.Fit(self)
		szr_outer.SetSizeHints(self)
		self.Layout()
	#--------------------------------------------------------
	def __register_events(self):
		# client internal signals
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._on_post_patient_selection)
		return 1
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		pass
		# FIXME: if has_focus ...
	#--------------------------------------------------------
	def populate(self):
		pat = gmPerson.gmCurrentPatient()
		# this should not really happen
		if not pat.is_connected():
			_log.Log(gmLog.lErr, 'no active patient, cannot get EMR text dump')
			self.txt.SetValue(_('Currently there is no active patient. Cannot retrieve EMR text.'))
			return None
		emr = pat.get_emr()
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
		return True
#============================================================
class gmScrolledEMRTextDump(wx.ScrolledWindow):
	def __init__(self, parent):
		wx.ScrolledWindow.__init__(
			self,
			parent,
			-1
		)
		self.txt = wx.TextCtrl(
			self,
			-1,
			_('No EMR data loaded.'),
			style = wx.TE_MULTILINE | wx.TE_READONLY 
		)
		szr_vbox_main = wx.BoxSizer(wx.VERTICAL)
		szr_vbox_main.Add(self.txt, 0, wxEXPAND | wx.CENTER | wx.ALL, 5)

		self.SetAutoLayout(1)
		self.SetSizer(szr_vbox_main)
		szr_vbox_main.Fit(self)
		szr_vbox_main.SetSizeHints(self)
		szr_vbox_main.SetVirtualSizeHints(self)
		self.Layout()

		# scroll back to top after initial events
		self.EnableScrolling(0, 1)
		self.SetScrollRate(0, 20)
		wx.CallAfter(self.Scroll, 0, 0)


#============================================================
# $Log: gmEMRTextDump.py,v $
# Revision 1.20  2008-01-30 14:03:41  ncq
# - use signal names directly
# - switch to std lib logging
#
# Revision 1.19  2008/01/22 12:21:49  ncq
# - cleanup
#
# Revision 1.18  2006/07/19 20:29:50  ncq
# - import cleanup
#
# Revision 1.17  2006/05/15 13:35:59  ncq
# - signal cleanup:
#   - activating_patient -> pre_patient_selection
#   - patient_selected -> post_patient_selection
#
# Revision 1.16  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.15  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.14  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.13  2005/09/26 18:01:50  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.12  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.11  2004/06/13 22:31:48  ncq
# - gb['main.toolbar'] -> gb['main.top_panel']
# - self.internal_name() -> self.__class__.__name__
# - remove set_widget_reference()
# - cleanup
# - fix lazy load in _on_patient_selected()
# - fix lazy load in ReceiveFocus()
# - use self._widget in self.GetWidget()
# - override populate_with_data()
# - use gb['main.notebook.raised_plugin']
#
# Revision 1.10  2004/03/09 10:51:50  ncq
# - cleanup
#
# Revision 1.9  2004/03/09 10:12:41  shilbert
# - adapt to new API from Gnumed.foo import bar
#
# Revision 1.8  2004/02/25 09:46:22  ncq
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
