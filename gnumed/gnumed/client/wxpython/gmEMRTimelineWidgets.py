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
import lxml.etree as lxml_etree


# GNUmed libs
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmPerson

from Gnumed.wxpython import gmRegetMixin

from Gnumed.exporters import gmTimelineExporter


_log = logging.getLogger('gm.ui.tl')

#============================================================
#from Gnumed.timelinelib.canvas.data import TimePeriod

# activate experimental container features
from Gnumed.timelinelib.features.experimental import experimentalfeatures
experimentalfeatures.EXTENDED_CONTAINER_HEIGHT.set_active(True)
experimentalfeatures.EXTENDED_CONTAINER_STRATEGY.set_active(True)

from Gnumed.timelinelib.canvas.data.timeperiod import TimePeriod
from Gnumed.timelinelib.calendar.gregorian.gregorian import GregorianDateTime

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
		appearance.set_hide_events_done(False)
		appearance.set_colorize_weekends(True)
		appearance.set_display_checkmark_on_events_done(True)

		self.InitDragScroll(direction = wx.BOTH)
		self.InitZoomSelect()
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
		self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_dclick)
		self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
		self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
		self.Bind(wx.EVT_RIGHT_DOWN, self._on_right_down)
		self.Bind(wx.EVT_RIGHT_UP, self._on_right_up)

        #self.Bind(wx.EVT_MIDDLE_DOWN, self._on_middle_down)

	#--------------------------------------------------------
	def _on_mouse_motion(self, evt):
		# not scrolling or zooming:
		self.DisplayBalloons(evt)

		# in case we are drag-scrolling:
		self.DragScroll(evt)

		# in case we are drag-zooming:
		self.DragZoom(evt)

	#--------------------------------------------------------
	def _on_mousewheel_action(self, evt):
		self.SpecialScrollVerticallyOnMouseWheel(evt)

	#--------------------------------------------------------
	def _on_left_dclick(self, evt):
		self.CenterAtCursor(evt)

	#--------------------------------------------------------
	def _on_left_down(self, evt):
		self.StartDragScroll(evt)

	#--------------------------------------------------------
	def _on_left_up(self, evt):
		self.StopDragScroll()

	#--------------------------------------------------------
	def _on_right_down(self, evt):
		self.StartZoomSelect(evt)

	#--------------------------------------------------------
	def _on_right_up(self, evt):
		# right down-up sequence w/o mouse motion leads to
		# "cannot zoom in deeper than 1 minute"
		try:
			self.StopDragZoom()
		except ValueError:
			_log.exception('drag-zoom w/o mouse motion')

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def center_at_today(self):
		now = gmDateTime.pydt_now_here()
		g_now = GregorianDateTime(now.year, now.month, now.day, now.hour, now.minute, now.second).to_time()
		self.Navigate(lambda tp: tp.center(g_now))

	#--------------------------------------------------------
	def clear_timeline(self):
		self.SetTimeline(None)

	#--------------------------------------------------------
	def open_timeline(self, tl_filename):
		if not self._validate_timeline_file(tl_filename):
			gmDispatcher.send(signal = 'statustext', msg = 'Timeline file failed to validate.')
		from Gnumed.timelinelib.db import db_open
		db = db_open(tl_filename)
		db.display_in_canvas(self)
		self.fit_care_era()

	#--------------------------------------------------------
	def export_as_svg(self, filename=None):
		if filename is None:
			filename = gmTools.get_unique_filename(suffix = '.svg')
		self.SaveAsSvg(filename)
		return filename

	#--------------------------------------------------------
	def export_as_png(self, filename=None):
		if filename is None:
			filename = gmTools.get_unique_filename(suffix = '.png')
		self.SaveAsPng(filename)
		return filename

	#--------------------------------------------------------
	def fit_all_events(self):
		all_events = self._controller.get_timeline().get_all_events()
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
		return end_time(max(events, key = end_time))

	#--------------------------------------------------------
	def fit_care_era(self):
		all_eras = self._controller.get_timeline().get_all_eras()
		care_era = [ e for e in all_eras if e.name == gmTimelineExporter.ERA_NAME_CARE_PERIOD ][0]
		era_period = care_era.time_period
		if era_period.is_period():
			self.Navigate(lambda tp: tp.update(era_period.start_time, era_period.end_time))
		else:
			self.Navigate(lambda tp: tp.center(era_period.mean_time()))

	#--------------------------------------------------------
	def fit_last_year(self):
		end = gmDateTime.pydt_now_here()
		g_end = GregorianDateTime(end.year, end.month, end.day, end.hour, end.minute, end.second).to_time()
		g_start = GregorianDateTime(end.year - 1, end.month, end.day, end.hour, end.minute, end.second).to_time()
		last_year = TimePeriod(g_start, g_end)
		self.Navigate(lambda tp: tp.update(last_year.start_time, last_year.end_time))

	#--------------------------------------------------------
	def _validate_timeline_file(self, tl_filename):
		xsd_name = 'timeline.xsd'
		xsd_paths = [
			os.path.join(gmTools.gmPaths().system_app_data_dir, 'resources', 'timeline', xsd_name),
			# maybe in dev tree
			os.path.join(gmTools.gmPaths().local_base_dir, 'resources', 'timeline', xsd_name)
		]
		xml_schema = None
		for xsd_filename in xsd_paths:
			_log.debug('XSD: %s', xsd_filename)
			if not os.path.exists(xsd_filename):
				_log.warning('not found')
				continue
			try:
				xml_schema = lxml_etree.XMLSchema(file = xsd_filename)
				break
			except lxml_etree.XMLSchemaParseError:
				_log.exception('cannot parse')
		if xml_schema is None:
			_log.error('no XSD found')
			return False

		with open(tl_filename, encoding = 'utf-8') as tl_file:
			try:
				xml_doc = lxml_etree.parse(tl_file)
			except lxml_etree.XMLSyntaxError:
				_log.exception('[%s] does not parse as XML', tl_filename)
				return False

		if xml_schema.validate(xml_doc):
			_log.debug('[%s] seems valid', tl_filename)
			return True

		_log.warning('[%s] does not validate against [%s]', tl_filename, xsd_filename)
		for entry in xml_schema.error_log:
			_log.debug(entry)
		return False

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
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
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
			defaultDir = gmTools.gmPaths().user_work_dir,
			defaultFile = 'timeline.svg',
			wildcard = '%s (*.svg)|*.svg' % _('SVG files'),
			style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
		)
		choice = dlg.ShowModal()
		fname = dlg.GetPath()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return False

		self._PNL_timeline.export_as_svg(filename = fname)
		self._PNL_timeline.export_as_png(filename = gmTools.fname_stem_with_path(fname) + '.png')

	#--------------------------------------------------------
	def _on_print_button_pressed(self, event):
		if self.__tl_file is None:
			return
		tl_image_file = self._PNL_timeline.export_as_png()
		gmMimeLib.call_viewer_on_file(aFile = tl_image_file, block = None)

	#--------------------------------------------------------
	def _on_export_area_button_pressed(self, event):
		if self.__tl_file is None:
			return
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return
		pat.export_area.add_file(filename = self.__tl_file, hint = _('timeline data (xml)'))
		pat.export_area.add_file(filename = self._PNL_timeline.export_as_png(), hint = _('timeline image (png)'))
		pat.export_area.add_file(filename = self._PNL_timeline.export_as_svg(), hint = _('timeline image (svg)'))

	#--------------------------------------------------------
	def _on_zoom_in_button_pressed(self, event):
		self._PNL_timeline.zoom_in()

	#--------------------------------------------------------
	def _on_zoom_out_button_pressed(self, event):
		self._PNL_timeline.zoom_out()

	#--------------------------------------------------------
	def _on_go2day_button_pressed(self, event):
		self._PNL_timeline.center_at_today()

	#--------------------------------------------------------
	def _on_zoom_fit_all_button_pressed(self, event):
		self._PNL_timeline.fit_all_events()

	#--------------------------------------------------------
	def _on_zoom_fit_last_year_button_pressed(self, event):
		self._PNL_timeline.fit_last_year()

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
