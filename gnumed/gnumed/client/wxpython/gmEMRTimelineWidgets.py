"""GNUmed patient EMR timeline browser.

Uses the excellent TheTimlineProject.
"""
#================================================================
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"

# std lib
import sys
import logging
#os.path, codecs


# 3rd party
import wx


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from timelinelib.wxgui.component import TimelineComponent
from timelinelib.db.exceptions import TimelineIOError

from Gnumed.pycommon import gmDispatcher
from Gnumed.business import gmPerson
from Gnumed.wxpython import gmRegetMixin
from Gnumed.exporters import timeline


_log = logging.getLogger('gm.ui')

#============================================================
class cEMRTimelinePnl(TimelineComponent):

	def __init__(self, *args, **kwargs):
#		TimelineComponent.__init__(self, *args, **kwargs)
#	def __init__(self, parent):
		TimelineComponent.__init__(self, args[0])

#============================================================
from Gnumed.wxGladeWidgets import wxgEMRTimelinePluginPnl

class cEMRTimelinePluginPnl(wxgEMRTimelinePluginPnl.wxgEMRTimelinePluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""Panel holding a number of widgets. Used as notebook page."""
	def __init__(self, *args, **kwargs):
		wxgEMRTimelinePluginPnl.wxgEMRTimelinePluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
#		self.__init_ui()
		self.__register_interests()
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
#		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._schedule_data_reget)
	#--------------------------------------------------------
	def _on_pre_patient_selection(self):
		wx.CallAfter(self.__on_pre_patient_selection)
	#--------------------------------------------------------
	def __on_pre_patient_selection(self):
		self._PNL_timeline.clear_timeline()
	#--------------------------------------------------------
	def _on_refresh_button_pressed(self, event):
		self._populate_with_data()
	#--------------------------------------------------------
	def repopulate_ui(self):
		self._populate_with_data()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
#	def __init_ui(self):
#		pass
	#--------------------------------------------------------
	# reget mixin API
	#
	# remember to call
	#	self._schedule_data_reget()
	# whenever you learn of data changes from database
	# listener threads, dispatcher signals etc.
	#--------------------------------------------------------
	def _populate_with_data(self):
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return True
		try:
			self._PNL_timeline.open_timeline(timeline.create_timeline_file(patient = pat))
		except TimelineIOError:
			self._PNL_timeline.clear_timeline()
			_log.exception('cannot load EMR from timeline XML')
			return False

		return True
#============================================================
