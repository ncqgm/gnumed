"""GNUMed client log handling.

All error logging, user notification and otherwise unhandled 
exception handling should go through classes or functions of 
this module

Theory of operation:

A logger object is a unifying wrapper for an arbitrary number
of log targets. A log target may be a file, syslog, the console,
or an email address, or, in fact, any object derived from the
class cLogTarget. Log targets will only log messages with at least
their own message priority level (log level). Each log target
may have it's own log level.

There's also a dummy log target that just drops messages to the floor.

By importing gmLog into your code you'll immediately have
access to a default logger: gmDefLog. Initially, the logger has
a log file as it's default target. The name of the file is
automatically derived from the name of the main application.
The log file will be found in one of the following standard
locations:

1) given on the command line as "--log-file=LOGFILE"
2) /var/log/<base_name>/<base_name>.log
3) /var/log/<base_name>.log
4) ~/.<base_name>/<base_name>.log
5) /dir/of/binary/<base_name>.log	- mainly for DOS/Windows

where <base_name> is derived from the name
of the main application.

If you want to specify just a directory for the log file you
must end the LOGFILE definition with slash.

By importing gmLog and logging to the default log your modules
never need to worry about the real message destination or whether
at any given time there's a valid logger available. Your MAIN
module simply adds real log targets to the default logger and
all other modules will merrily and automagically start logging
there.

You can of course instantiate any number of additional loggers
that log to different targets alltogether if you want to keep
some messages separate from others.

Usage:
1.) if desired create an instance of cLogger
2.) create appropriate log targets and add them to the default logger or your own (from step 1)
3.) call the cLogger.LogXXX() functions

@license: GPL
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/Attic/gmLog.py,v $
__version__ = "$Revision: 1.17 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#-------------------------------------------
# don't use gmCLI in here since that would give a circular reference
import sys, time, traceback, os.path, os, string, stat

#, atexit

# safely import SYSLOG, currently POSIX only
try:
	import syslog
	_use_syslog = (1 == 1)
except ImportError:
	_use_syslog = (1 == 0)
	if os.name == 'posix':
		print "Although we are on a POSIX compliant platform the module SYSLOG cannot be imported !"
		print "You should download and install this module !"

#-------------------------------------------
# log levels:
# lPanic - try to log this before we die
# lErr   - some error occured, may be recoverable
# lWarn  - something should be done about this though it's not fatal
# lInfo  - user info such as program flow
# lData  - raw data processed by program

# injudicious use of lData may lead to copious amounts of log output
# and has inherent security risks (may dump raw data including passwords,
# sensitive records, etc)

lPanic, lErr, lWarn, lInfo, lData = range(5)

# process non-printable characters ?
lUncooked = 0
lCooked = 1

# table used for cooking non-printables
AsciiName = ['<#0-0x00-nul>',
			 '<#1-0x01-soh>',
			 '<#2-0x02-stx>',
			 '<#3-0x03-etx>',
			 '<#4-0x04-eot>',
			 '<#5-0x05-enq>',
			 '<#6-0x06-ack>',
			 '<#7-0x07-bel>',
			 '<#8-0x08-bs>',
			 '<#9-0x09-ht>',
			 '<#10-0x0A-lf>',
			 '<#11-0x0B-vt>',
			 '<#12-0x0C-ff>',
			 '<#13-0x0D-cr>',
			 '<#14-0x0E-so>',
			 '<#15-0x0F-si>',
			 '<#16-0x10-dle>',
			 '<#17-0x11-dc1/xon>',
			 '<#18-0x12-dc2>',
			 '<#19-0x13-dc3/xoff>',
			 '<#20-0x14-dc4>',
			 '<#21-0x15-nak>',
			 '<#22-0x16-syn>',
			 '<#23-0x17-etb>',
			 '<#24-0x18-can>',
			 '<#25-0x19-em>',
			 '<#26-0x1A-sub>',
			 '<#27-0x1B-esc>',
			 '<#28-0x1C-fs>',
			 '<#29-0x1D-gs>',
			 '<#30-0x1E-rs>',
			 '<#31-0x1F-us>'
			]

class cLogger:
	# file(s)/pipes, stdout/stderr = console, email, syslog, widget, you-name-it
	# can be any arbitrary object derived from cLogTarget (see below)
	__targets = {}
	#---------------------------
	def __init__(self, aTarget=None):
		"""Open an instance of cLogger and initialize a target.

		in case there's no target given open a dummy target
	"""
		if aTarget is None:
			aTarget = cLogTargetDummy()
		self.AddTarget (aTarget)
	#---------------------------
	def close(self):
		"""Close this logger and cleanly shutdown any open targets.
		"""
		for key in self.__targets.keys():
			self.__targets[key].flush()
			self.__targets[key].close()
	#---------------------------
	def AddTarget (self, aTarget):
		"""Add another log target.

		- targets must be objects derived from cLogTarget
		- ignores identical targets
		- the number of concurrent targets is potentially unlimited
		"""

		# log security warning
		# (additional log targets are potential sources of inadvertant disclosure)
		self.Log(lInfo, 'SECURITY: adding log target "' + str(aTarget.getID()) + '"')

		# FIXME - we need some assertions about the new target here !

		# no duplicate targets
		if not self.__targets.has_key(aTarget.getID()):
			self.__targets[aTarget.getID()] = aTarget
	#---------------------------
	def RemoveTarget (self, anID):
		"""Remove a log target by it's ID.

		- clients have to track target ID's themselves if they want to remove targets
		"""

		if self.__targets.has_key(anID):
			self.Log(lWarn, 'SECURITY: removing log target "' + str(anID) + '"')
			self.__targets[anID].close()
			del self.__targets[anID]
	#---------------------------
	def Info(self, aMsg, aRawnessFlag = lUncooked):
		"""Just a convenience wrapper for Log(gmLog.lInfo, ...)"""
		self.Log(lInfo, aMsg, aRawnessFlag)
	#---------------------------
	def Data(self, aMsg, aRawnessFlag = lCooked):
		"""Just a convenience wrapper for Log(gmLog.lData, ...)"""
		self.Log(lData, aMsg, aRawnessFlag)
	#---------------------------
	def Error(self, aMsg):
		self.Log(lErr, aMsg)
	#---------------------------
	def Log(self, aLogLevel, aMsg, aRawnessFlag = lUncooked):
		"""Log a message.

		- for a list of log levels see top of file
		- messages above the currently active level of logging/verbosity are dropped silently
		- if Rawness == lCooked non-printables < 32 (space) will be mapped to their name in ASCII
		- FIXME: this should be a Unicode mapping
		"""
		# are we in for work ?
		if self.__targets is not None:
			dummy = ""
			# handle types somewhat intelligently
			if type(aMsg) != type(dummy):
				tmp = str(aMsg)
			else:
				tmp = aMsg
			# cook it ?
			if aRawnessFlag == lCooked:
				msg = reduce(lambda x, y: x+y, (map(self.__char2AsciiName, list(tmp))), '')
			else:
				msg = tmp

			# now dump it
			for key in self.__targets.keys():
				self.__targets[key].writeMsg(aLogLevel, msg)
	#---------------------------
	def LogDelimiter (self):
		"""Write a horizontal delimiter to the log target.
		"""
		for key in self.__targets.keys():
			self.__targets[key].writeDelimiter()
	#---------------------------
	def LogException(self, aMsg, exception=None, verbose=1, **kwargs):
		"""Log an exception.

		'exception' is a tuple as returned by sys.exc_info()
		"""
		# avoid one level of indirection by not calling self.__Log such
		# that the chances of succeeding shall be increased
		if self.__targets is not None:
			if verbose:
				level1 = lPanic
				level2 = lPanic
			else:
				level1 = lWarn
				level2 = lData
			# split the tuple
			exc_type, exc_val, exc_traceback = sys.exc_info()
			# FIXME: I wonder if the following back-and-forth reversing is necessary
			# trace back to root caller
			tb = exc_traceback
			if not tb:
				return
			while 1:
				if  not tb.tb_next:
					break
				tb = tb.tb_next
			# and put the frames on a stack
			stack_of_frames = []
			frame = tb.tb_frame
			while frame:
				stack_of_frames.append(frame)
				frame = frame.f_back
			stack_of_frames.reverse()

			traceback_stack = traceback.format_exception(exc_type, exc_val, exc_traceback)
			for key in self.__targets.keys():
				self.__targets[key].writeMsg(level1, aMsg)
				self.__targets[key].writeMsg(level1, "exception type : %s" % exc_type)
				self.__targets[key].writeMsg(level1, "exception value: %s" % exc_val)
				for line in traceback_stack:
					self.__targets[key].writeMsg(level2, reduce(lambda x, y: x+y, (map(self.__char2AsciiName, list(line)))))
				if verbose:
					self.__targets[key].writeMsg(lData, "locals by frame, outmost frame first")
					for frame in stack_of_frames:
						self.__targets[key].writeMsg(lData, ">>> execution frame [%s] in [%s] at line %s <<<" % (
							frame.f_code.co_name,
							frame.f_code.co_filename,
							frame.f_lineno)
						)
						for varname, value in frame.f_locals.items():
							try:
								self.__targets[key].writeMsg(lData, "%20s = %s" % (varname, value))
							except:
								pass
	#---------------------------
	def SetInfoLevel(self):
		self.SetAllLogLevels(lInfo)
	#---------------------------
	def SetAllLogLevels (self, aLogLevel = None):
		"""Set a certain log level on all targets."""
		if aLogLevel is None:
			return
		for key in self.__targets.keys():
			self.__targets[key].SetLogLevel(aLogLevel)
	#---------------------------
	def flush(self):
		for key in self.__targets.keys():
			self.__targets[key].flush()
	#---------------------------
	# internal methods
	#---------------------------
	def __char2AsciiName(self, aChar):
		try:
			return AsciiName[ord(aChar)]
		except IndexError:
			return aChar
#---------------------------------------------------------------
class cLogTarget:
	"""Base class for actual log target implementations.

	- derive your targets from this class
	- offers lots of generic functionality
	"""

	# used to add/remove a target in logger
	ID = None

	# default log level
	__activeLogLevel = lErr

	# any security related items should be tagged with "SECURITY" by the programmer
	__LogLevelPrefix = {lPanic: '[PANIC] ', lErr: '[ERROR] ', lWarn: '[WARN]  ', lInfo: '[INFO]  ', lData: '[DATA]  '}
	#---------------------------
	def __init__(self, aLogLevel = lErr):
		self.__activeLogLevel = aLogLevel
		if aLogLevel == lInfo or aLogLevel == lData:
			self.writeDelimiter()
		self.writeMsg (lInfo, "SECURITY: initial log level is " + self.__LogLevelPrefix[self.__activeLogLevel])
		self.__has_ever_logged = 0 # true if ever logged anything interesting
	#---------------------------
	def close(self):
		self.writeMsg (lInfo, "SECURITY: closing log target (ID = %s)" % self.ID)
	#---------------------------
	def getID (self):
		return self.ID
	#---------------------------
	def SetLogLevel(self, aLogLevel):
		# are we sane ?
		if aLogLevel not in range(lData+1):
			self.writeMsg (lPanic, "SECURITY: trying to set invalid log level (" + str(aLogLevel) + ") - keeping current log level (" + str(self.__activeLogLevel) + ")")
			return None
		# log the change
		self.writeMsg (lInfo, "SECURITY: log level change from " + self.__LogLevelPrefix[self.__activeLogLevel] + " to " + self.__LogLevelPrefix[aLogLevel])
		self.__activeLogLevel = aLogLevel
		return self.__activeLogLevel
	#---------------------------
	def writeMsg (self, aLogLevel, aMsg):
		if aLogLevel <= self.__activeLogLevel:
			self.__has_ever_logged = 1
			timestamp = self.__timestamp()
			severity = self.__LogLevelPrefix[aLogLevel]
			self.__tracestack()
			caller = '(%s:%s@%s): ' % (self.__modulename, self.__functionname, str(self.__linenumber))
#			caller = "(" + self.__modulename + ":" + self.__functionname + "@" + str(self.__linenumber) + "): "
			if aLogLevel > lErr:
				self.dump2stdout (timestamp, severity, caller, aMsg + "\n")
			else:
				self.dump2stderr (timestamp, severity, caller, aMsg + "\n")
			# FIXME: lPanic immediately flush()es ?
			if aLogLevel == lPanic:
				#self.flush()
				pass
	#---------------------------
	def hasLogged (self):
		return self.__has_ever_logged
	#---------------------------
	def writeDelimiter (self):
		self.dump2stdout (self.__timestamp(), '', '', '------------------------------------------------------------\n')
	#---------------------------
	def flush (self):
		pass
	#---------------------------
	# Private methods - you never have to use those directly
	#---------------------------
	# stdout equivalent for lWarn and above
	def dump2stdout (self, aTimestamp, aSeverity, aCaller, aMsg):
		# for most log targets we make no distinction between stderr and stdout
		self.dump2stderr (aTimestamp, aSeverity, aCaller, aMsg)
	#---------------------------
	# stderr equivalent for lPanic, lErr
	def dump2stderr (self, aTimestamp, aSeverity, aCaller, aMsg):
		print "cLogTarget: You forgot to override dump2stderr() !\n"
	#---------------------------
	def __timestamp(self):
		"""return a nicely formatted time stamp

		FIXME: allow for non-hardwired format string
		"""
		return time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime(time.time()))
	#---------------------------
	def __tracestack(self):
		"""extract data from the current execution stack

		this is rather fragile, I guess
		"""
		stack = traceback.extract_stack()
		self.__modulename = stack[-4][0]
		self.__linenumber = stack[-4][1]
		self.__functionname = stack[-4][2]
		if (self.__functionname == "?"):
			self.__functionname = "Main"

#---------------------------------------------------------------
class cLogTargetFile(cLogTarget):
	# the actual file handle
	__handle = None
	#---------------------------
	def __init__ (self, aLogLevel = lErr, aFileName = "", aMode = "ab"):
		# do our extra work
		self.__handle = open (aFileName, aMode)
		if self.__handle is None:
			return None
		else:
			# call inherited
			cLogTarget.__init__(self, aLogLevel)
			self.ID = os.path.abspath (aFileName) # the file name canonicalized

		self.writeMsg (lInfo, "instantiated log file " + aFileName + " with ID " + str(self.ID))
	#---------------------------
	def dummy(self):
		for module in sys.modules.values():
			if hasattr(module, "__version__"):
				cLogTarget.writeMsg(gmLog.lData, "[%s]: %s" % (module, module.__version__))
		cLogTarget.close(self)
		self.__handle.close()
	#---------------------------
	def dump2stderr (self, aTimeStamp, aPrefix, aLocation, aMsg):
		try:
			self.__handle.write(aTimeStamp + aPrefix + aLocation + aMsg)
		except:
			print "*** cannot write to log file [%s] ***" % self.ID
#---------------------------------------------------------------
class cLogTargetConsole(cLogTarget):
	def __init__ (self, aLogLevel = lErr):
		# call inherited
		cLogTarget.__init__(self, aLogLevel)
		# do our extra work
		self.ID = "stdout/stderr"
		self.writeMsg (lData, "instantiated console logging with ID " + str(self.ID))
	#---------------------------
	def dump2stdout (self, aTimeStamp, aPrefix, aLocation, aMsg):
		try: 
			sys.stdout.write(aPrefix + aLocation + aMsg)
		except IOError:
			print aPrefix + aLocation + aMsg
	#---------------------------
	def dump2stderr (self, aTimeStamp, aPrefix, aLocation, aMsg):
		try:
			sys.stderr.write(aPrefix + aLocation + aMsg)
		except IOError:
			print aPrefix + aLocation + aMsg
#---------------------------------------------------------------
class cLogTargetSyslog(cLogTarget):
	def __init__ (self, aLogLevel = lErr):
		# is syslog available ?
		if _use_syslog:
			# call inherited
			cLogTarget.__init__(self, aLogLevel)
			# do our extra work
			syslog.openlog(os.path.basename(sys.argv[0]))
			syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))
			self.ID = "syslog"
			self.writeMsg (lData, "instantiated syslog logging with ID " + str(self.ID))
		else:
			raise NotImplementedError, "No SYSLOG module available on this platform (" + str(os.name) + ") !"
	#---------------------------
	def close(self):
		print "cLogTargetSyslog.close()"
#		cLogTarget.close(self)
#		syslog.closelog()
	#---------------------------
	def dump2stdout (self, aTimeStamp, aPrefix, aLocation, aMsg):
		syslog.syslog ((syslog.LOG_USER | syslog.LOG_INFO), aPrefix + aLocation + aMsg)
	#---------------------------
	def dump2stderr (self, aTimeStamp, aPrefix, aLocation, aMsg):
		syslog.syslog ((syslog.LOG_USER | syslog.LOG_ERR), aPrefix + aLocation + aMsg)
#---------------------------------------------------------------
class cLogTargetDummy(cLogTarget):
	def __init__ (self):
		# call inherited
		cLogTarget.__init__(self, lPanic)
		self.ID = "dummy"
	#---------------------------
	def dump2stderr (self, aTimestamp, aSeverity, aCaller, aMsg):
		pass
#---------------------------------------------------------------
class cLogTargetEMail(cLogTarget):
	"""Log into E-Mail.

	- sends log messages to the specified e-mail address upon flush() or close()
	- holds unsent log messages in a ring buffer
	"""
	def __init__ (self, aLogLevel = lErr, aFrom = None, aTo = None, anSMTPServer = None):
		"""Instantiate.

		- aTo must hold a sequence of addresses (usually a singleton)
		- anSMTPServer is the URL of a valid SMTP server, will use "localhost" if == None
		"""
		# sanity check
		if aTo == None:
			raise ValueError, "cLogTargetEMail.__init__(): aTo must contain values !"

		if aFrom == None:
			# FIXME
			raise ValueError, "cLogTargetEMail.__init__(): aFrom must contain a value !"

		self.__dump_sys_info = (1==1)
		self.__max_buf_len = 100
		self.__max_line_size = 150
		self.__msg_buffer = []

		# call inherited
		cLogTarget.__init__(self, aLogLevel)

		# do our extra work
		self.__from = str(aFrom)
		self.__to = string.join(aTo, ", ")
		self.__comment = ""

		if anSMTPServer == None:
			self.__smtp_server = 'localhost'
		else:
			self.__smtp_server = str(anSMTPServer)

		self.ID = "email: " + self.__to
		self.writeMsg (lInfo, "instantiated e-mail logging with ID " + str(self.ID))
	#---------------------------
	def close(self):
		print "cLogTargetEMail.close()"
#		cLogTarget.close(self)
	#---------------------------
	def setFrom (self, aFrom):
		self.__from = str(aFrom)
	#---------------------------
	def setTo (self, aTo):
		self.__to = string.join(aTo, ", ")
	#---------------------------
	def setComment (self, aComment):
		self.__comment = str(aComment)
	#---------------------------
	def setSysDump (self, aFlag):
		"""Whether to include various system info when flush()ing."""
		self.__dump_sys_info = aFlag
	#---------------------------
	def setMaxBufLen (self, aBufLen):
		"""Set maximum number of log messages in ring buffer."""
		if aBufLen < 5:
			return (1==1)
		if aBufLen > 250:
			return (1==1)
		self.__max_buf_len = aBufLen
	#---------------------------
	def setMaxLineSize (self, aLineSize):
		"""Set maximum line size in byte."""
		if aLineSize < 30:
			return (1==1)
		if aLineSize > 300:
			return (1==1)
		self.__max_line_size = aLineSize
	#---------------------------
	def dump2stderr (self, aTimeStamp, aPrefix, aLocation, aMsg):
		# any messages containing "CONFIDENTIAL" get dropped
		if string.find(aMsg, "CONFIDENTIAL") != -1:
			return (1==1)
		# any message larger than max_line_size is truncated
		if len(aMsg) > self.__max_line_size:
			tmp = aMsg[:self.__max_line_size]
			aMsg = tmp = " [...]\n"
		# drop oldest msg from buffer if buffer full
		if len(self.__msg_buffer) >= self.__max_buf_len:
			self.__msg_buffer.pop(0)
		# now finally store the current log message
		self.__msg_buffer.append(aTimeStamp + aPrefix + aLocation + aMsg)
	#---------------------------
	def flush(self):
		# - PYTHONPATH still missing

		# create mail headers
		msg = ''
		msg = msg + 'From: %s\n' % self.__from
		msg = msg + 'To: %s\n' % self.__to
		msg = msg + 'Date: %s\n' % time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(time.time()))
		msg = msg + 'Subject: gmLog error log\n'
		msg = msg + '\n'

		# create mail body
		# - dump comment
		msg = msg + self.__comment + "\n"
		msg = msg + '----------------------------------------------\n'

		# - dump system info
		if self.__dump_sys_info:
			msg = msg + 'sys.version : %s\n' % sys.version
			msg = msg + 'sys.platform: %s\n' % sys.platform
			msg = msg + '----------------------------------------------\n'
			msg = msg + 'sys.path    : %s\n' % sys.path
			msg = msg + '----------------------------------------------\n'
			for key in sys.modules.keys():
				module = sys.modules[key]
				msg = msg + '"%s": %s' % (key, module)
				if hasattr(module, "__version__"):
					msg = msg + ' (%s)' % module.__version__
				msg = msg + '\n'
			msg = msg + '----------------------------------------------\n'

		# - dump actual message buffer
		msg = msg + string.join(self.__msg_buffer, '')

		# dynamically import smtplib statically - God, I love Python
		import smtplib

		# connect to mail server
		smtpd = smtplib.SMTP(self.__smtp_server)
		# send mail
		smtpd.sendmail(self.__from, self.__to, msg)
		# tear down connection
		smtpd.quit()

		# reinitialize msg buffer
		del self.__msg_buffer
		self.__msg_buffer = []
#---------------------------------------------------------------
def __open_default_logfile():
	"""Try to open log file in a standard location.

	- we don't have a logger available yet
	"""
	loghandle = None

	# get base dir from name of script
	base_dir = os.path.splitext(os.path.basename(sys.argv[0]))[0]
	# get base name from name of script
	base_name = base_dir + ".log"

	# config file given on command line ?
	for option in sys.argv[1:]:
		if option.find('--log-file=') == 0:
			(tmp1,tmp2) = option.split('=')
			(ldir, lname) = os.path.split(tmp2)
			if ldir == '':
				ldir = '.'
			if lname == '':
				lname = base_name
			logName = os.path.abspath(os.path.expanduser(os.path.join(ldir, lname)))
			try:
				loghandle = cLogTargetFile (lInfo, logName, "ab")
				print """
#################################################################################
#
# log file is [%s]
#
# Please email this file to <gnumed-devel@gnu.org> if you encounter problems.
#
#################################################################################
""" % logName
				return loghandle
			except:
				print "command line log file [%s] cannot be opened" % logName
				exc_type, exc_val, exc_traceback = sys.exc_info()
				print exc_type
				print exc_val

	# else look in standard locations
	# /var/log/base_dir/base_name.log
	logName = os.path.join('/var/log', base_dir, base_name)
	try:
		loghandle = cLogTargetFile(lInfo, logName, "ab")
		print "log file is [%s]" % logName
		return loghandle
	except:
		pass

	# /var/log/base_name.log
	logName = os.path.join('/var/log', base_name)
	try:
		loghandle = cLogTargetFile (lInfo, logName, "ab")
		print "log file is [%s]" % logName
		return loghandle
	except:
		pass

	# ~/.base_dir/base_name.log
	# make sure path is there
	tmp = os.path.expanduser(os.path.join('~', '.' + base_dir))
	if not os.path.exists(tmp):
		try:
			os.mkdir(tmp)
		except:
			print "Cannot make directory [%s] for log file." % tmp
	if os.path.exists(tmp):
		logName = os.path.expanduser(os.path.join('~', '.' + base_dir, base_name))
		try:
			loghandle = cLogTargetFile (lInfo, logName, "wb")
			print "log file is [%s]" % logName
			return loghandle
		except:
			pass

	# ./base_name.log
	# last resort for inferior operating systems such as DOS/Windows
	logName = os.path.abspath(os.path.join(os.path.split(sys.argv[0])[0], base_name))
	try:
		loghandle = cLogTargetFile (lInfo, logName, "wb")
		print "log file is [%s]" % logName
		return loghandle
	except:
		pass

	print "Cannot open any log file."
	return None
#---------------------------------------------------------------
#def myExitFunc():
#	pass
	# FIXME - do something useful
	#gmDefLog.close()
	# should close other loggers, too, but I need to keep track of them first
#------- MAIN -------------------------------------------------------
if __name__ == "__main__":
	print "\nTesting module gmLog\n=========================="

	# create a file target
	loghandle = cLogTargetFile (lData, "test.log", "a")

	# procure the ID
	handleID = loghandle.getID()
	print (str(handleID))

	# and use that to populate the logger
	log = cLogger(loghandle)

	# set up an email target
	print "please type sender and receiver of log messages"
	aFrom = raw_input("From: ").strip()
	aTo = raw_input("To: ").strip().split()
	#aServer = raw_input("SMTP server: ").strip().split()
	#mailhandle = cLogTargetEMail(lData, aFrom, aTo, aServer[0])
	mailhandle = cLogTargetEMail(lData, aFrom, aTo)
	log.AddTarget(mailhandle)

	# should log a security warning
	loghandle.SetLogLevel (lWarn)

	# should log a security warning and fail
	loghandle.SetLogLevel (12)

	# we are sane again - play with this for different verbosity leveles
	loghandle.SetLogLevel (lData)

	# now do something
	log.Log (lInfo, "starting whatever we were about to do")

	print "Let's add a console logging handle."
	# let's add a console log target - it can have it's own log level
	consolehandle = cLogTargetConsole (lInfo)
	log.AddTarget (consolehandle)

	log.Log (lData, "this should only show up in the log file")
	log.Log (lInfo, "this should show up both on console and in the log file")

	# syslog is cool, too
	#if _use_syslog:
	print "adding syslog logging"
	sysloghandle = cLogTargetSyslog (lWarn)
	log.AddTarget (sysloghandle)

	log.Log (lData, "the logger object uncooked: " + str(log))
	log.Log (lInfo, "and now cooked with some non-printables appended:")
	log.Log (lData, str(log) + "\001\002\003\004\005\012\013\015", lCooked)
	log.Log (lErr, "an error occurred ...")

	print "Now, try an exception (divison by zero)"
	try:
		n = 1/0
	except:
		exc = sys.exc_info()
		log.LogException("Exception caught !", exc)

	log.Log (lInfo, "done with whatever we were about to do")
	log.close()

	print "======================================================================"
	print __doc__
	print "======================================================================"

	print "Done."
else:
	# register application specific default log file
	target = __open_default_logfile()
	if not target:
		gmDefLog = cLogger(aTarget = None)
		raise ImportError, "Cannot open any log target. Falling back to dummy log target."
	else:
		gmDefLog = cLogger(target)

	# this needs Python 2.x
	#atexit.register(myExitFunc)
#---------------------------------------------------------------
# sample code for inclusion in your project
#---------------------------------------------------------------
# by just importing this module you will usually get a default
# log file in a fairly standard location:
"""
import gmLog
"""

# it is rather convenient to define a shortcut:
"""
_log = gmLog.gmDefLog
"""

# if you want to add log targets do this:
"""
# make a _real_ log target
loghandle = gmLog.cLogTargetFile (gmLog.lData, 'your-log-file.log', "ab")
# and tell the default logger to also use that
_log.AddTarget(loghandle)
"""

# alternatively if you want to setup your own logger with targets:
"""
myLogger = gmLog.cLogger(aTarget = your-log-target)
"""
#---------------------------------------------------------------
# random ideas and TODO
#
# target wxPython
# target DB-API
#
# log areas ?
#
# promptfunc() ?
#
# __bases__
# callable()
# type()
# __del__
# __is_subclass__
#===============================================================
# $Log: gmLog.py,v $
# Revision 1.17  2006-06-20 14:28:23  ncq
# - give people an email address they can actually send the log to ;-)
#
# Revision 1.16  2005/11/27 12:45:47  ncq
# - improved log file display
#
# Revision 1.15  2005/10/28 07:38:59  shilbert
# - console message about log file location has been visually enhanced
#
# Revision 1.14  2005/10/10 18:18:14  ncq
# - some cleanup only, really
#
# Revision 1.13  2005/10/04 13:09:49  sjtan
# correct syntax errors; get soap entry working again.
#
# Revision 1.12  2005/10/03 13:49:21  sjtan
# using new wx. temporary debugging to stdout(easier to read). where is rfe ?
#
# Revision 1.11  2005/07/14 21:25:06  ncq
# - cleanup
#
# Revision 1.10  2004/10/20 12:18:11  ncq
# - fix sync errors
#
# Revision 1.9  2004/10/20 11:10:35  sjtan
# convenient name for logging errors. Consistent with Data Info.
#
# Revision 1.7  2004/08/18 08:20:06  ncq
# - remove SPACE from char2ascii map
#
# Revision 1.6  2004/08/16 19:24:21  ncq
# - try to speed up __char2AsciiName()
#
# Revision 1.5  2004/08/11 08:00:05  ncq
# - improve log prefix
# - cleanup SQL cfg/remove old use of _USER
#
# Revision 1.4  2004/06/26 23:06:00  ncq
# - cleanup
# - I checked it, no matter where we import (function-/class-/method-
#   local or globally) it will always only be done once so we can
#   get rid of the semaphore
#
# Revision 1.3  2004/06/09 14:52:56  ncq
# - implement flush() method at cLogger level
#
# Revision 1.2  2004/03/02 10:19:53  ihaywood
# problems with accessing sys.stderr
# use "print" as backup now
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.45  2003/11/19 18:09:33  ncq
# - make "locals by frame" message less confusing
#
# Revision 1.44  2003/11/19 14:41:14  ncq
# - somehow, the log keyword got dropped in the recent mess, re-add
#
#
# revision 1.43
# date: 2003/11/19 14:34:30;  author: ncq;  state: Exp;  lines: +4 -4
# - remerge patches that Syan dropped
#
# revision 1.42
# date: 2003/11/17 10:56:36;  author: sjtan;  state: Exp;  lines: +10 -5
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.41  2003/10/31 08:48:17  ncq
# - PSU: --log-file=test.log should of course use test.log in the current directory
#
# Revision 1.40  2003/09/30 19:02:28  ncq
# - added try: except: on write errors to log targets ...
#
# Revision 1.39  2003/09/22 23:19:58  ncq
# - raise level of self-name logging for file targets
#
# Revision 1.38  2003/07/21 20:54:36  ncq
# - verbose=1 in LogException: log locals in all execution frames
#
# Revision 1.37  2003/06/03 13:25:48  ncq
# - coding style fix for Data() wrapper
#
# Revision 1.36  2003/06/01 13:20:32  sjtan
#
# logging to data stream for debugging. Adding DEBUG tags when work out how to use vi
# with regular expression groups (maybe never).
#
# Revision 1.35  2003/05/27 13:52:54  ncq
# - made var names in LogException() more descriptive
# - changed fatal to verbose in LogException(), but kept backward compat with deprec warning
#
# Revision 1.34  2003/05/27 13:13:23  ncq
# - I must always nitpick on coding style :-)
#
# Revision 1.33  2003/05/27 13:00:41  sjtan
#
# removed redundant property support, read directly from __dict__
#
# Revision 1.32  2003/02/13 16:09:13  ncq
# - typo
#
# Revision 1.31  2003/02/12 01:03:44  ncq
# - when logging to console: don't display timestamp, it scrolls past too fast anyways
#
# Revision 1.30  2002/11/20 12:08:36  ncq
# - finally make --log-file=LOGFILE actually work
#
# Revision 1.29  2002/11/18 11:36:04  ncq
# - --log-file -> append not overwrite
#
# Revision 1.28  2002/11/18 09:41:25  ncq
# - removed magic #! interpreter incantation line to make Debian happy
#
# Revision 1.27  2002/11/18 02:23:01  ncq
# - make it work with /var/log/...
#
# Revision 1.26  2002/11/18 00:18:12  ncq
# - conform to Debian/FHS/LSB idea of where to place log files (/var/log/<base>/)
# - will slightly increase startup on Windows/DOS
# - admin must still create /var/log/base/ and assign appropriate rights to users
#
# Revision 1.25  2002/11/17 20:09:10  ncq
# - always display __doc__ when called standalone
#
# Revision 1.24  2002/11/08 16:32:24  ncq
# *** empty log message ***
#
# Revision 1.23  2002/11/03 14:11:19  ncq
# - autocreate log file on failing to find one
#
# Revision 1.22  2002/09/26 13:21:37  ncq
# - log version
#
# Revision 1.21  2002/09/14 09:10:52  ncq
# - gracefully handle the condition when we cannot open a default log file
#
# Revision 1.20  2002/09/12 23:20:10  ncq
# - whitespace fix
#
# Revision 1.19  2002/09/08 15:53:32  ncq
# - added changelog cvs keyword
#
