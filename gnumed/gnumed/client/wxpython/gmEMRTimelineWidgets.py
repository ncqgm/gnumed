"""GNUmed patient EMR timeline browser.

Uses the excellent TheTimlineProject.
"""
#================================================================
__author__ = "Karsten.Hilbert@gmx.net"
__license__ = "GPL v2 or later"

# std lib
import sys
import logging
import os.path


# 3rd party
import wx


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMimeLib
from Gnumed.business import gmPerson
from Gnumed.wxpython import gmRegetMixin
from Gnumed.exporters import timeline


_log = logging.getLogger('gm.ui.tl')

#============================================================
from Gnumed.timelinelib.canvas import TimelineCanvas	# works because of __init__.py

class cEMRTimelinePnl(TimelineCanvas):

	def __init__(self, *args, **kwargs):
		TimelineCanvas.__init__(self, args[0])
		self.Bind(wx.EVT_MOUSEWHEEL, self._on_mousewheel_action)

	#--------------------------------------------------------
	def _on_mousewheel_action(self, event):
		self.Scroll(event.GetWheelRotation() / 1200.0)

	#--------------------------------------------------------
	def clear_timeline(self):
		self.set_timeline(None)

	#--------------------------------------------------------
	def open_timeline(self, tl_file):
		from Gnumed.timelinelib.db import db_open
		db = db_open(tl_file)
		db.display_in_canvas(self)

	#--------------------------------------------------------
	def export_as_svg(self, filename=None):
		if filename is None:
			filename = gmTools.get_unique_filename(suffix = u'.svg')
		self.SaveAsSvg(self, filename)
		return filename

#============================================================
from Gnumed.wxGladeWidgets import wxgEMRTimelinePluginPnl

class cEMRTimelinePluginPnl(wxgEMRTimelinePluginPnl.wxgEMRTimelinePluginPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""Panel holding a number of widgets. Used as notebook page."""
	def __init__(self, *args, **kwargs):
		self.__tl_file = None
		wxgEMRTimelinePluginPnl.wxgEMRTimelinePluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
#		self.__init_ui()
		self.__register_interests()
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = u'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
#		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._schedule_data_reget)

	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		self._PNL_timeline.clear_timeline()

	#--------------------------------------------------------
	def _on_refresh_button_pressed(self, event):
		self._populate_with_data()

	#--------------------------------------------------------
	def _on_save_button_pressed(self, event):
		if self.__tl_file is None:
			return
		dlg = wx.FileDialog (
			parent = self,
			message = _("Save timeline as SVG image under..."),
			defaultDir = os.path.expanduser(os.path.join('~', 'gnumed')),
			defaultFile = u'timeline.svg',
			wildcard = u'%s (*.svg)|*.svg' % _('SVG files'),
			style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
		)
		choice = dlg.ShowModal()
		fname = dlg.GetPath()
		dlg.Destroy()
		if choice != wx.ID_OK:
			return False
		self._PNL_timeline.export_as_svg(filename = fname)

	#--------------------------------------------------------
	def _on_print_button_pressed(self, event):
		if self.__tl_file is None:
			return
		svg_file = self._PNL_timeline.export_as_svg()
		gmMimeLib.call_viewer_on_file(aFile = svg_file, block = None)

	#--------------------------------------------------------
	def _on_export_area_button_pressed(self, event):
		if self.__tl_file is None:
			return
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return
		pat.export_area.add_file(filename = self._PNL_timeline.export_as_svg(), hint = _(u'timeline image'))
		pat.export_area.add_file(filename = self.__tl_file, hint = _('timeline data'))

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
			self.__tl_file = timeline.create_timeline_file(patient = pat)
			self._PNL_timeline.open_timeline(self.__tl_file)
		except Exception:		# more specifically: TimelineIOError
			_log.exception('cannot load EMR from timeline XML')
			self._PNL_timeline.clear_timeline()
			self.__tl_file = timeline.create_fake_timeline_file(patient = pat)
			self._PNL_timeline.open_timeline(self.__tl_file)
			return True

		return True

#============================================================
