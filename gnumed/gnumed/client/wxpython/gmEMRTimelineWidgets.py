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
from Gnumed.exporters import gmTimelineExporter


_log = logging.getLogger('gm.ui.tl')

#============================================================
#class cTLCursorDummy:
#	def __init__(self, x, y):
#		self.x = x
#		self.y = y

#------------------------------------------------------------
from Gnumed.timelinelib.canvas.data import TimePeriod

# activate experimental container features
from Gnumed.timelinelib.features.experimental import experimentalfeatures
experimentalfeatures.EXTENDED_CONTAINER_HEIGHT.set_active(True)
experimentalfeatures.EXTENDED_CONTAINER_STRATEGY.set_active(True)

#------------------------------------------------------------
from Gnumed.timelinelib.canvas import TimelineCanvas	# works because of __init__.py

class cEMRTimelinePnl(TimelineCanvas):

	def __init__(self, *args, **kwargs):
		TimelineCanvas.__init__(self, args[0])	# args[0] should be "parent"

		self.__init_ui()
		self.__register_interests()

	#--------------------------------------------------------
	def __init_ui(self):
		appearance = self.GetAppearance()
		appearance.set_balloons_visible(True)
		appearance.set_hide_events_done(True)
		appearance.set_colorize_weekends(True)
		appearance.set_display_checkmark_on_events_done(True)
		return
		"""
            appearance.set_legend_visible(self.config.show_legend)
            appearance.set_minor_strip_divider_line_colour(self.config.minor_strip_divider_line_colour)
            appearance.set_major_strip_divider_line_colour(self.config.major_strip_divider_line_colour)
            appearance.set_now_line_colour(self.config.now_line_colour)
            appearance.set_weekend_colour(self.config.weekend_colour)
            appearance.set_bg_colour(self.config.bg_colour)
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
            appearance.set_never_use_time(self.config.never_use_time)
            appearance.set_legend_pos(self.config.legend_pos)
		"""
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		self.Bind(wx.EVT_MOUSEWHEEL, self._on_mousewheel_action)
		self.Bind(wx.EVT_MOTION, self._on_mouse_motion)

        #self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        #self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_dclick)
        #self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        #self.Bind(wx.EVT_MIDDLE_DOWN, self._on_middle_down)
        #self.Bind(wx.EVT_MOUSEWHEEL, self._on_mousewheel)

	#--------------------------------------------------------
	def _on_mouse_motion(self, event):
		#cursor = cTLCursorDummy(event.GetX(), event.GetY())
		#self.SetHoveredEvent(self.GetEventAt(cursor))
		self.SetHoveredEvent(self.GetEventAt(event.GetX(), event.GetY()))

	#--------------------------------------------------------
	def _on_mousewheel_action(self, event):
		self.Scroll(event.GetWheelRotation() / 1200.0)

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

	#--------------------------------------------------------
	def fit_all_events(self):
		all_events = self.get_timeline().get_all_events()
		if len(all_events) == 0:
			period4all_events = None
		start = self._first_time(all_events)
		end = self._last_time(all_events)
		period4all_events = TimePeriod(start, end).zoom(-1)

		if period4all_events is None:
			return
		if period4all_events.is_period():
			self.Navigate(lambda tp: tp.update(period4all_events.start_time, period4all_events.end_time))
		else:
			self.Navigate(lambda tp: tp.center(period4all_events.mean_time()))

	#--------------------------------------------------------
	def _first_time(self, events):
		start_time = lambda event: event.get_start_time()
		return start_time(min(events, key=start_time))

	#--------------------------------------------------------
	def _last_time(self, events):
		end_time = lambda event: event.get_end_time()
		return end_time(max(events, key=end_time))

	#--------------------------------------------------------
	def fit_care_era(self):
		all_eras = self.get_timeline().get_all_eras()
		care_era = [ e for e in all_eras if e.name == gmTimelineExporter.ERA_NAME_CARE_PERIOD ][0]
		era_period = care_era.time_period
		if era_period.is_period():
			self.Navigate(lambda tp: tp.update(era_period.start_time, era_period.end_time))
		else:
			self.Navigate(lambda tp: tp.center(era_period.mean_time()))

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
			message = _("Save timeline as images (SVG, PNG) under..."),
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
		self._PNL_timeline.export_as_png(filename = gmTools.fname_stem_with_path(fname) + u'.png')

	#--------------------------------------------------------
	def _on_print_button_pressed(self, event):
		if self.__tl_file is None:
			return
		#tl_image_file = self._PNL_timeline.export_as_svg()
		tl_image_file = self._PNL_timeline.export_as_png()
		gmMimeLib.call_viewer_on_file(aFile = tl_image_file, block = None)

	#--------------------------------------------------------
	def _on_export_area_button_pressed(self, event):
		if self.__tl_file is None:
			return
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return
		pat.export_area.add_file(filename = self._PNL_timeline.export_as_png(), hint = _(u'timeline image (png)'))
		pat.export_area.add_file(filename = self._PNL_timeline.export_as_svg(), hint = _(u'timeline image (svg)'))
		pat.export_area.add_file(filename = self.__tl_file, hint = _('timeline data (xml)'))

	#--------------------------------------------------------
	def _on_zoom_in_button_pressed(self, event):
		self._PNL_timeline.zoom_in()

	#--------------------------------------------------------
	def _on_zoom_out_button_pressed(self, event):
		self._PNL_timeline.zoom_out()

	#--------------------------------------------------------
	def _on_zoom_fit_all_button_pressed(self, event):
		self._PNL_timeline.fit_all_events()

	#--------------------------------------------------------
	def _on_zoom_fit_care_period_button_pressed(self, event):
		self._PNL_timeline.fit_care_era()

	#--------------------------------------------------------
	# notebook plugin glue
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

		wx.BeginBusyCursor()
		try:
			self.__tl_file = gmTimelineExporter.create_timeline_file(patient = pat)
			self._PNL_timeline.open_timeline(self.__tl_file)
		except Exception:		# more specifically: TimelineIOError
			_log.exception('cannot load EMR from timeline XML')
			self._PNL_timeline.clear_timeline()
			self.__tl_file = gmTimelineExporter.create_fake_timeline_file(patient = pat)
			self._PNL_timeline.open_timeline(self.__tl_file)
			return True
		finally:
			wx.EndBusyCursor()

		return True

#============================================================
