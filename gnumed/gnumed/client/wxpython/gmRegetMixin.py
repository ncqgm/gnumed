"""gmRegetMixin - GnuMed data change callback mixin.

Widget code can mix in this class as a base class and
thus gain the infrastructure to update it's display
when data changes. If the widget is not visible it will
only schedule refetching data from the business layer.
If it *is* visible it will immediately fetch and redisplay.

You must call cRegetOnPaintMixin.__init__() in your own
__init__() after calling __init__() on the appropriate
wxWidgets class your widget inherits from.

You must then make sure to call _schedule_data_reget()
whenever you learn of backend data changes. This will
in most cases happen after you receive a gmDispatcher
signal indicating a change in the backend.

The _populate_with_data(self) method must be overriden in the
including class and must return True if the contents was
redrawn successfully.

@copyright: authors
"""
#===========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmRegetMixin.py,v $
# $Id: gmRegetMixin.py,v 1.11 2005-05-06 15:31:03 ncq Exp $
__version__ = "$Revision: 1.11 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (details at http://www.gnu.org)'


from wxPython import wx

#===========================================================================
class cRegetOnPaintMixin:
	"""Mixin to add redisplay_data-on-EVT_PAINT aspect.

	Any code mixing in this class will gain the mechanism
	to reget data on wxPaint events. The code must be an
	instance of a wxWindow and must implement a
	_populate_with_data() method. It must also call
	_schedule_data_reget() at appropriate times.
	"""
	def __init__(self):
		self._data_stale = True
		try:
			wx.EVT_PAINT(self, self._on_paint_event)
		except:
			_log.Log(gmLog.lErr, 'you likely need to call "cRegetOnPaintMixin.__init__()" later in your __init__()')
			raise
		wx.EVT_SET_FOCUS(self, self._on_focus_event)
	#-----------------------------------------------------
	def _on_paint_event(self, event):
		"""Repopulate UI if data is stale."""
		if self._data_stale:
			self.__populate_with_data()
		event.Skip()
	#-----------------------------------------------------
	def _on_focus_event(self, event):
		"""Doubtful whether that's the proper way to do it but seems OK."""
		self.Refresh()
	#-----------------------------------------------------
	def __populate_with_data(self):
		if self._populate_with_data():
			self._data_stale = False
		else:
			self._data_stale = True
	#-----------------------------------------------------
	def _populate_with_data(self):
		"""Override in includers !

		- must fill widget controls with data
		"""
		print "%s._populate_with_data() not implemented" % self.__class__.__name__
		_log.Log(gmLog.lErr, 'not implemented for %s' % self.__class__.__name__)
		return False
	#-----------------------------------------------------
	def _schedule_data_reget(self):
		"""Flag data as stale and redisplay if needed.

		- if not visible schedule reget only
		- if visible redisplay immediately
		"""
		dc = wx.wxPaintDC(self)
		print "%s._schedule_data_reget(): %s" % (self.__class__.__name__, str(dc.GetClippingBox()))
		#if self.GetUpdateRegion().IsEmpty() == 1 and not self.IsShown():
		if self.GetUpdateRegion().IsEmpty() == 1:
			self._data_stale = True
			return True
		else:
			if self.__populate_with_data():
				self.Refresh()
				return True
			else:
				return False

#===========================================================================
# main
#---------------------------------------------------------------------------
if __name__ == '__main__':
	print "no unit test available"

#===========================================================================
# $Log: gmRegetMixin.py,v $
# Revision 1.11  2005-05-06 15:31:03  ncq
# - slightly improved docs
#
# Revision 1.10  2005/05/05 06:35:02  ncq
# - add some device context measurements in _schedule_data_reget
#   so we can maybe find a way to detect whether we are indeed
#   visible or obscured
#
# Revision 1.9  2005/04/30 13:32:14  sjtan
#
# if current wxWindow that inherits gmRegetMixin IsShown() is true, then it requires
# refresh, so Reget is not scheduled , but immediate.
#
# Revision 1.8  2005/03/20 17:51:41  ncq
# - although not sure whether conceptually it's the right thing to do it
#   sure seems appropriated to Refresh() on focus events
#
# Revision 1.7  2005/01/13 14:27:33  ncq
# - grammar fix
#
# Revision 1.6  2004/10/17 15:52:21  ncq
# - cleanup
#
# Revision 1.5  2004/10/17 00:05:36  sjtan
#
# fixup for paint event re-entry when notification dialog occurs over medDocTree graphics
# area, and triggers another paint event, and another notification dialog , in a loop.
# Fixup is set flag to stop _repopulate_tree, and to only unset this flag when
# patient activating signal gmMedShowDocs to schedule_reget, which is overridden
# to include resetting of flag, before calling mixin schedule_reget.
#
# Revision 1.4  2004/09/05 14:55:19  ncq
# - improve comments, some cleanup
#
# Revision 1.3  2004/08/04 17:12:06  ncq
# - fix comment
#
# Revision 1.2  2004/08/02 17:52:54  hinnef
# Added hint to _repopulate_with_data return value
#
# Revision 1.1  2004/07/28 15:27:31  ncq
# - first checkin, used in gmVaccWidget
#
#
