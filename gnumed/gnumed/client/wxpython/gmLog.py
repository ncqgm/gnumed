#! /usr/bin/python
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
access to a default logger: gmDefLog. Initially, the only log
target is a dummy which is formally fully functional but does
nothing. To turn on real logging you need to instantiate another
log target such as a file and add that target to gmDefLog.

By importing gmLog and logging to the default log your modules
never need to worry about the real message destination or whether
at any given instant there's a valid logger available. Your MAIN
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

@copyright: GPL
"""

__version__ = "$Revision: 1.15 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys, time, traceback, os.path, atexit, os, string

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
# lInfo  - user info like program flow
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
	     '<#31-0x1F-us>',
	     '<#32-0x20-space>'
	    ]

class cLogger:
    # file(s)/pipes, stdout/stderr = console, email, syslog, widget, you-name-it
    # can be any arbitrary object derived from cLogTarget (see below)
    __targets = {}

    def __init__(self, aTarget=None):
	"""Open an instance of cLogger and initialize a target.

	in case there's no target given open a dummy target
	"""
	if aTarget == None:
	    aTarget = cLogTargetDummy()
	self.AddTarget (aTarget)

    def close(self):
	"""Close this logger and cleanly shutdown any open targets.
	"""
	for key in self.__targets.keys():
	    self.__targets[key].flush()
	    self.__targets[key].close()

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

    def RemoveTarget (self, anID):
	"""Remove a log target by it's ID.

	- clients have to track target ID's themselves if they want to remove targets
	"""

	if self.__targets.has_key(anID):
	    self.Log(lWarn, 'SECURITY: removing log target "' + str(anID) + '"')
	    self.__targets[anID].close()
	    del self.__targets[anID]

    def Log(self, aLogLevel, aMsg, aRawnessFlag = lUncooked):
	"""Log a message.

	- for a list of log levels see top of file
	- messages above the currently active level of logging/verbosity are dropped silently
	- if Rawness == lCooked non-printables < 32 (space) will be mapped to their name in ASCII
	- FIXME: this should be a Unicode mapping
	"""

	# are we in for work ?
	if self.__targets is not None:
	    # cook it ?
	    if aRawnessFlag == lCooked:
		msg = reduce(lambda x, y: x+y, (map(self.__char2AsciiName, list(aMsg))))
	    else:
		msg = aMsg

	    # now dump it
	    for key in self.__targets.keys():
		self.__targets[key].writeMsg(aLogLevel, msg)

    def LogDelimiter (self):
	"""Write a horizontal delimiter to the log target.
	"""

	for key in self.__targets.keys():
	    self.__targets[key].writeDelimiter()

    def LogException(self, aMsg, exception):
    	"""Log an exception.

	'exception' is a tuple as returned by sys.exc_info()
	"""

	# avoid one level of indirection by not calling self.__Log such
	# that the chances of succeeding shall be increased
	if self.__targets is not None:
	    t, v, tb = exception
	    tbs = traceback.format_exception(t, v, tb)
	    for key in self.__targets.keys():
		self.__targets[key].writeMsg(lPanic, aMsg)
		for line in tbs:
		    self.__targets[key].writeMsg(lPanic, reduce(lambda x, y: x+y, (map(self.__char2AsciiName, list(line)))))

    def __char2AsciiName(self, aChar):
	if ord(aChar) in range(0,32):
	    return AsciiName[ord(aChar)]
	else:
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
	self.writeDelimiter()
	self.writeMsg (lPanic, "SECURITY: initial log level is " + self.__LogLevelPrefix[self.__activeLogLevel])
    #---------------------------
    def close(self):
	self.writeMsg (lPanic, "SECURITY: closing log target (ID = " + str(self.ID) + ")")
	#self.flush()
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
	self.writeMsg (lPanic, "SECURITY: log level change from " + self.__LogLevelPrefix[self.__activeLogLevel] + " to " + self.__LogLevelPrefix[aLogLevel])
	self.__activeLogLevel = aLogLevel
	return self.__activeLogLevel
    #---------------------------
    def writeMsg (self, aLogLevel, aMsg):
	if aLogLevel <= self.__activeLogLevel:
	    timestamp = self.__timestamp()
	    severity = self.__LogLevelPrefix[aLogLevel]
	    self.__tracestack()
	    caller = "(" + self.__modulename + "::" + self.__functionname + ":" + str(self.__linenumber) + "): "
	    if aLogLevel > lErr:
		self.dump2stdout (timestamp, severity, caller, aMsg + "\n")
	    else:
		self.dump2stderr (timestamp, severity, caller, aMsg + "\n")
	    # FIXME: lPanic immediately flush()es ?
	    if aLogLevel == lPanic:
		#self.flush()
		pass
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
	# for most log targest we make no distinction between stderr and stdout
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

	self.writeMsg (lData, "instantiated log file " + aFileName + " with ID " + str(self.ID))
    #---------------------------
    def close(self):
	cLogTarget.close(self)
	self.__handle.close()
    #---------------------------
    def dump2stderr (self, aTimeStamp, aPrefix, aLocation, aMsg):
	self.__handle.write(aTimeStamp + aPrefix + aLocation + aMsg)
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
	sys.stdout.write(aTimeStamp + aPrefix + aLocation + aMsg)
    #---------------------------
    def dump2stderr (self, aTimeStamp, aPrefix, aLocation, aMsg):
	sys.stderr.write(aTimeStamp + aPrefix + aLocation + aMsg)

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
	cLogTarget.close(self)
	syslog.closelog()
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
	print self.__to

	import smtplib
	if anSMTPServer == None:
	    self.__smtpd = smtplib.SMTP("localhost")
	else:
	    self.__smtpd = smtplib.SMTP(anSMTPServer)

	self.ID = "email: " + self.__to
	self.writeMsg (lInfo, "instantiated e-mail logging with ID " + str(self.ID))
    #---------------------------
    def close(self):
	cLogTarget.close(self)
	self.__smtpd.close()
    #---------------------------
    def setSysDump (self, aFlag):
	"""Whether to include various system info when flush()ing.

	   - PYTHONPATH"""
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
	    aMsg[self.__max_line_size:] = " [...]\n"
	# drop oldest msg from buffer if buffer full
	if len(self.__msg_buffer) >= self.__max_buf_len:
	    self.__msg_buffer.pop(0)
	# now finally store the current log message
	self.__msg_buffer.append(aTimeStamp + aPrefix + aLocation + aMsg)
    #---------------------------
    def flush(self):
	# create mail header
	msg = ''
	msg = msg + 'From: %s\n' % self.__from
	msg = msg + 'To: %s\n' % self.__to
	msg = msg + 'Date: %s\n' % time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(time.time()))
	msg = msg + 'Subject: GNUmed error log demon\n'
	msg = msg + '\n'
	# create mail body
	# - dump system info
	if self.__dump_sys_info:
	    msg = msg + 'sys.version : %s\n' % sys.version
	    msg = msg + 'sys.platform: %s\n' % sys.platform
	    msg = msg + 'sys.path    : %s\n' % sys.path
	    msg = msg + 'sys.modules : %s\n' % sys.modules

	# - dump actual message buffer
	msg = msg + string.join(self.__msg_buffer, '')

	# send mail
	self.__smtpd.sendmail(self.__from, self.__to, msg)

	# reinitialize msg buffer
	del self.__msg_buffer
	self.__msg_buffer = []
#---------------------------------------------------------------
def myExitFunc():
    pass
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

    print "Done."
else:
    gmDefLog = cLogger()
    # this needs Python 2.x
    atexit.register(myExitFunc)

#---------------------------------------------------------------
# random ideas and TODO
#
# target email
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
