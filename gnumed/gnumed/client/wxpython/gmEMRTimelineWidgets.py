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
#class cTLCursorDummy:
#	def __init__(self, x, y):
#		self.x = x
#		self.y = y

#------------------------------------------------------------
from Gnumed.timelinelib.canvas import TimelineCanvas	# works because of __init__.py
#from timelinelib.wxgui.components.maincanvas.noop import NoOpInputHandler

class cEMRTimelinePnl(TimelineCanvas):

	def __init__(self, *args, **kwargs):
		TimelineCanvas.__init__(self, args[0])	# args[0] should be "parent"

		self.__init_ui()
		self.__register_interests()
		"""
        self.balloon_show_timer = wx.Timer(self, -1)
        self.balloon_hide_timer = wx.Timer(self, -1)
        self.dragscroll_timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_dclick)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_TIMER, self._on_balloon_show_timer, self.balloon_show_timer)
        self.Bind(wx.EVT_TIMER, self._on_balloon_hide_timer, self.balloon_hide_timer)
        self.Bind(wx.EVT_TIMER, self._on_dragscroll, self.dragscroll_timer)
        self.Bind(wx.EVT_MIDDLE_DOWN, self._on_middle_down)
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_mousewheel)
		"""

	#--------------------------------------------------------
	def __init_ui(self):
		appearance = self.GetAppearance()
		appearance.set_balloons_visible(True)
		appearance.set_hide_events_done(True)
		"""
            appearance.set_legend_visible(self.config.show_legend)
            appearance.set_minor_strip_divider_line_colour(self.config.minor_strip_divider_line_colour)
            appearance.set_major_strip_divider_line_colour(self.config.major_strip_divider_line_colour)
            appearance.set_now_line_colour(self.config.now_line_colour)
            appearance.set_weekend_colour(self.config.weekend_colour)
            appearance.set_bg_colour(self.config.bg_colour)
            appearance.set_colorize_weekends(self.config.colorize_weekends)
            appearance.set_draw_period_events_to_right(self.config.draw_point_events_to_right)
            appearance.set_text_below_icon(self.config.text_below_icon)
            appearance.set_minor_strip_font(self.config.minor_strip_font)
            appearance.set_major_strip_font(self.config.major_strip_font)
            appearance.set_balloon_font(self.config.balloon_font)
            appearance.set_legend_font(self.config.legend_font)
            appearance.set_center_event_texts(self.config.center_event_texts)
            appearance.set_never_show_period_events_as_point_events(self.config.never_show_period_events_as_point_events)
            appearance.set_week_start(self.config.get_week_start())
            appearance.set_use_inertial_scrolling(self.config.use_inertial_scrolling)
            appearance.set_fuzzy_icon(self.config.fuzzy_icon)
            appearance.set_locked_icon(self.config.locked_icon)
            appearance.set_hyperlink_icon(self.config.hyperlink_icon)
            appearance.set_vertical_space_between_events(self.config.vertical_space_between_events)
            appearance.set_skip_s_in_decade_text(self.config.skip_s_in_decade_text)
            appearance.set_display_checkmark_on_events_done(self.config.display_checkmark_on_events_done)
            appearance.set_never_use_time(self.config.never_use_time)
            appearance.set_legend_pos(self.config.legend_pos)
		"""
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		#self._input_handler = NoOpInputHandler(self)

		self.Bind(wx.EVT_MOUSEWHEEL, self._on_mousewheel_action)
		self.Bind(wx.EVT_MOTION, self._on_mouse_motion)
		#self.Bind(wx.EVT_TIMER, self._on_balloon_show_timer, self.balloon_show_timer_fired)
		#self.Bind(wx.EVT_TIMER, self._on_balloon_hide_timer, self.balloon_hide_timer_fired)

	#--------------------------------------------------------
	def _on_mouse_motion(self, event):
		#cursor = cTLCursorDummy(event.GetX(), event.GetY())
		#self.SetHoveredEvent(self.GetEventAt(cursor))
		self.SetHoveredEvent(self.GetEventAt(event.GetX(), event.GetY()))

	#--------------------------------------------------------
	def _on_mousewheel_action(self, event):
		self.Scroll(event.GetWheelRotation() / 1200.0)

#	#--------------------------------------------------------
#	def _on_balloon_show_timer_fired(self, event):
#		self._input_handler.balloon_show_timer_fired()

#	#--------------------------------------------------------
#	def _on_balloon_hide_timer_fired(self, event):
#		self._input_handler.balloon_hide_timer_fired()

	#--------------------------------------------------------
	# internal API
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
		self.SaveAsSvg(filename)
		return filename

	#--------------------------------------------------------
	def export_as_png(self, filename=None):
		if filename is None:
			filename = gmTools.get_unique_filename(suffix = u'.png')
		self.SaveAsPng(filename)
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
		pat.export_area.add_file(filename = self._PNL_timeline.export_as_png(), hint = _(u'timeline image'))
		pat.export_area.add_file(filename = self._PNL_timeline.export_as_svg(), hint = _(u'timeline image (scalable)'))
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
