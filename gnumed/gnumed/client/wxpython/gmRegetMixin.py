"""gmRegetMixin - GNUmed data change callback mixin.

Widget code can mix in this class as a base class and
thus gain the infrastructure to update it's display
when data changes. If the widget is not visible it will
only schedule refetching data from the business layer.
If it *is* visible it will immediately fetch and redisplay.

You must call cRegetOnPaintMixin.__init__() in your own
__init__() after calling __init__() on the appropriate
wx.Widgets class your widget inherits from.

You must then make sure to call _schedule_data_reget()
whenever you learn of backend data changes. This will
in most cases happen after you receive a gmDispatcher
signal indicating a change in the backend.

The _populate_with_data(self) method must be overridden in the
including class and must return True if the UI was successfully
repopulated with content.

@copyright: authors

Template for users:

	#-----------------------------------------------------
	# reget-on-paint mixin API
	#
	# remember to call
	#	self._schedule_data_reget()
	# whenever you learn of data changes from database
	# listener threads, dispatcher signals etc.
	#-----------------------------------------------------
	def _populate_with_data(self):
		# fill the UI with data
		print("need to implement _populate_with_data")
		return False
		return True
	#-----------------------------------------------------
"""
#===========================================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

import wx

#===========================================================================
class cRegetOnPaintMixin:
	"""Mixin to add redisplay_data-on-wx.EVT_PAINT aspect.

	Any code mixing in this class will gain the mechanism
	to reget data on wxPaint events. The code must be an
	instance of a wx.Window and must implement a
	_populate_with_data() method. It must also call
	_schedule_data_reget() at appropriate times.
	"""
	def __init__(self):
		self._data_stale = True
		try:
			self.Bind(wx.EVT_PAINT, self.__on_paint_event)
		except Exception:
			print('you likely need to call "cRegetOnPaintMixin.__init__(self)" later in %s__init__()' % self.__class__.__name__)
			raise

	#-----------------------------------------------------
	def __on_paint_event(self, event):
		"""Called just before the widget is repainted.

		Checks whether data needs to be refetched.
		"""
		self.__repopulate_ui()
		event.Skip()
	#-----------------------------------------------------
	def __repopulate_ui(self):
		"""Checks whether data must be refetched and does so 

		Called on different occasions such as "notebook page
		raised" or "paint event received".
		"""
		if not self._data_stale:
			return True
		repopulated = self._populate_with_data()
		self._data_stale = (repopulated is False)
		return repopulated
	#-----------------------------------------------------
	# API for child classes
	#-----------------------------------------------------
	def _populate_with_data(self):
		"""Actually fills the UI with data.

		This must be overridden in child classes !

		Must return True/False.
		"""
		raise NotImplementedError("[%s] _populate_with_data() not implemented" % self.__class__.__name__)
	#-----------------------------------------------------
	def _schedule_data_reget(self):
		"""Flag data as stale and schedule refetch/redisplay.

		- if not visible schedules refetch only
		- if visible redisplays immediately (virtue of Refresh()
		  calling __on_paint_event() if visible) thereby invoking
		  the actual data refetch

		Called by the child class whenever it learns of data changes
		such as from database listener threads, dispatcher signals etc.
		"""
		self._data_stale = True

		# Master Robin Dunn sayeth this is The Way(tm) but
		# neither this:
		#wx.GetApp().GetTopWindow().Refresh()
		# nor this:
		#top_parent = wx.GetTopLevelParent(self)
		#top_parent.Refresh()
		# appear to work as expected :-(
		# The issues I have with them are:
		# 1) It appears to cause refreshes "too often", eg whenever
		#    *any*  child of self calls this method - but this may
		#    not matter much as only those that have self._data_stale
		#    set to True will trigger backend refetches.
		# 2) Even this does not in all cases cause a proper redraw
		#    of the visible widgets - likely because nothing has
		#    really changed in them, visually.

		# further testing by Hilmar revealed that the
		# following appears to work:
		self.Refresh()
		# the logic should go like this:
		# database insert -> after-insert trigger
		# -> notify
		# -> middleware listener
		# -> flush optional middleware cache
		# -> dispatcher signal to frontend listener*s*
		# -> frontend listeners schedule a data reget and a Refresh()
		# problem: those that are not visible are refreshed, too
		# FIXME: is this last assumption true ?
		return True
	#-----------------------------------------------------
	# notebook plugin API if needed
	#-----------------------------------------------------
	def repopulate_ui(self):
		"""Just a glue method to make this compatible with notebook plugins."""
		self.__repopulate_ui()

#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':
	print("no unit test available")
