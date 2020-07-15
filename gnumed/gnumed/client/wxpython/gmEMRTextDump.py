"""GNUmed scrolled window text dump of EMR content.
"""
#============================================================
__version__ = "$Revision: 1.22 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, string


import wx


from Gnumed.pycommon import gmDispatcher, gmExceptions
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
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)
		return 1
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		pass
		# FIXME: if has_focus ...
	#--------------------------------------------------------
	def populate(self):
		pat = gmPerson.gmCurrentPatient()
		# this should not really happen
		if not pat.connected:
			_log.Log(gmLog.lErr, 'no active patient, cannot get EMR text dump')
			self.txt.SetValue(_('Currently there is no active patient. Cannot retrieve EMR text.'))
			return None
		emr = pat.emr
		if emr is None:
			_log.Log(gmLog.lErr, 'cannot get EMR text dump')
			self.txt.SetValue(_(
				'An error occurred while retrieving a text\n'
				'dump of the EMR for the active patient.\n\n'
				'Please check the log file for details.'
			))
			return None
		dump__grouped_by_age = emr.get_text_dump()
		if dump__grouped_by_age is None:
			_log.Log(gmLog.lErr, 'cannot get EMR text dump')
			self.txt.SetValue(_(
				'An error occurred while retrieving a text\n'
				'dump of the EMR for the active patient.\n\n'
				'Please check the log file for details.'
			))
			return None

		txt = ''
		for age in sorted(dump__grouped_by_age):
			for line in dump__grouped_by_age[age]:
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
