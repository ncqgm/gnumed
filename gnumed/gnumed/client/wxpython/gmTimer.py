"""GNUmed wx.Timer proxy object.

@copyright: author(s)
"""
#===========================================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL v2 or later (details at https://www.gnu.org)"

# stdlib
import logging

# 3rd party
import wx


_log = logging.getLogger('gm.timers')
_timers:list['cTimer'] = []

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
		print("timer <%s> fired" % cookie)
	#-----------------------------------------------------------------------
	class cApp(wx.App):
		def OnInit(self):
			print("setting up timer")
			timer = cTimer(callback = cb_timer)
			print("starting timer")
			timer.Start()
			return True
	#-----------------------------------------------------------------------
	app = cApp(0)
	# and enter the main event loop
	app.MainLoop()
	print("waiting 10 seconds for timer to trigger")
	time.sleep(10)
#===========================================================================
