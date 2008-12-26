"""GNUmed wx.Timer proxy object.

@copyright: author(s)
"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmTimer.py,v $
# $Id: gmTimer.py,v 1.13 2008-12-26 16:04:12 ncq Exp $
__version__ = "$Revision: 1.13 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL (details at http://www.gnu.org)"

# stdlib
import logging

# 3rd party
import wx


_log = logging.getLogger('gm.timers')
_timers = []
#===========================================================================
def shutdown():
	global _timers
	_log.info('shutting down %s pending timers', len(_timers))
	for timer in _timers:
		_log.debug('timer [%s]', timer.cookie)
		timer.Stop()
	_timers = []
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
		if not callable(callback):
			raise ValueError("[%s]: <callback> %s is not a callable()" % (self.__class__.__name__, callback))

		if cookie is None:
			self.cookie = id(self)
		else:
			self.cookie = cookie
		self.__callback = callback
		self.__delay = delay

		wx.Timer.__init__(self)

		_log.debug('setting up timer: cookie [%s], delay %sms', self.cookie, self.__delay)

		global _timers
		_timers.append(self)
	#-----------------------------------------------------------------------
	def Start(self, milliseconds=-1, oneShot=False):
		if milliseconds == -1:
			milliseconds = self.__delay
		wx.Timer.Start(self, milliseconds=milliseconds, oneShot=oneShot)
	#-----------------------------------------------------------------------
	def Notify(self):
		self.__callback(self.cookie)
	#-----------------------------------------------------------------------
	def set_cookie(self, cookie=None):
		if cookie is None:
			self.cookie = id(self)
		else:
			self.cookie = cookie
#===========================================================================
if __name__ == '__main__':
	import time

	#-----------------------------------------------------------------------
	def cb_timer(cookie):
		print "timer <%s> fired" % cookie
	#-----------------------------------------------------------------------
	class cApp(wx.App):
		def OnInit(self):
			print "setting up timer"
			timer = cTimer(callback = cb_timer)
			print "starting timer"
			timer.Start()
			return True
	#-----------------------------------------------------------------------
	app = cApp(0)
	# and enter the main event loop
	app.MainLoop()
	print "waiting 10 seconds for timer to trigger"
	time.sleep(10)
#===========================================================================
# $Log: gmTimer.py,v $
# Revision 1.13  2008-12-26 16:04:12  ncq
# - properly shutdown timers
#
# Revision 1.12  2008/07/13 16:23:27  ncq
# - add some debugging
#
# Revision 1.11  2007/02/05 12:11:58  ncq
# - imports cleanup
# - remove gmLog
#
# Revision 1.10  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.9  2005/09/28 19:47:01  ncq
# - runs until login dialog
#
# Revision 1.8  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
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
