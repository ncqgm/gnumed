"""GnuMed wx.Timer proxy object.

@copyright: author(s)
"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmTimer.py,v $
# $Id: gmTimer.py,v 1.9 2005-09-28 19:47:01 ncq Exp $
__version__ = "$Revision: 1.9 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL (details at http://www.gnu.org)"

# 3rd party
try:
	import wxversion
	import wx
except ImportError:
	from wxPython.wx import wxTimer

# GnuMed
from Gnumed.pycommon import gmLog

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#===========================================================================
class cTimer(wx.Timer):
	"""wx.Timer proxy.

	It would be quite useful to tune the delay
	according to current network speed either at
	application startup or even during runtime.
	"""
	def __init__(self, callback = None, delay = 300, cookie = None):
		"""Set up our timer with reasonable defaults.

		- delay default is 300ms as per Richard Terry's experience
		- delay should be tailored to network speed/user speed
		- <cookie> is passed to <callback> when <delay> is up
		"""
		# sanity check
		if callback is None:
			_log.Log(gmLog.lErr, "no use setting up a timer without a callback function")
			raise ValueError, "No use setting up a timer without a callback function."

		if cookie is None:
			self.__cookie = id(self)
		else:
			self.__cookie = cookie
		self.__callback = callback
		self.__delay = delay

		wx.Timer.__init__(self)
	#-----------------------------------------------------------------------
	def Start(self, milliseconds=-1, oneShot=False):
		if milliseconds == -1:
			milliseconds = self.__delay
		wx.Timer.Start(self, milliseconds=milliseconds, oneShot=oneShot)
	#-----------------------------------------------------------------------
	def Notify(self):
		self.__callback(self.__cookie)
	#-----------------------------------------------------------------------
	def set_cookie(self, cookie=None):
		if cookie is None:
			self.__cookie = id(self)
		else:
			self.__cookie = cookie
#===========================================================================
if __name__ == '__main__':
	import time

	try:
		import wxversion
		import wx
	except ImportError:
		from wxPython.wx import wxApp

	#-----------------------------------------------------------------------
	def cb_timer(cookie):
		print "timer <%s> fired" % cookie
		return 1
	#-----------------------------------------------------------------------
	class cApp(wx.App):
		def OnInit(self):
			print "setting up timer"
			timer = cTimer(callback = cb_timer)
			print "starting timer"
			timer.Start(oneShot=True)
			print "waiting for timer to trigger"
			time.sleep(2)
			return True
	#-----------------------------------------------------------------------
	app = cApp(0)
	# and enter the main event loop
	app.MainLoop()
#===========================================================================
# $Log: gmTimer.py,v $
# Revision 1.9  2005-09-28 19:47:01  ncq
# - runs until login dialog
#
# Revision 1.8  2005/09/28 15:57:48  ncq
# - a whole bunch of wxFoo -> wx.Foo
#
# Revision 1.7  2005/09/27 20:44:59  ncq
# - wx.wx* -> wx.*
#
# Revision 1.6  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.5  2005/07/24 09:21:09  ncq
# - use proxy Start() to work around Windows timer Start() glitches
#
# Revision 1.4  2005/07/23 21:12:19  ncq
# - no keywords for Windows in Start()
#
# Revision 1.3  2005/07/23 21:08:28  ncq
# - explicitely use milliseconds=-1 as Windows seems to require it
#
# Revision 1.2  2005/07/23 20:47:02  ncq
# - start wxApp instance when testing - needed in windows
#
# Revision 1.1  2004/12/23 15:07:36  ncq
# - provide a convenient wxTimer proxy object
#
#
