#! /usr/bin/python
"""GNUMed client log handling

All error logging, user notification and otherwise unhandled 
exception handling should go through classes or functions of 
this module

Usage:
1.) create an instance of Logger
2.) if neccessary, redirect your output to your output device/widget
3.) call the Logger.Log() function

@author: Dr. Horst Herb
@version: 0.1
@copyright: GPL
"""

import sys, time, traceback, os.path, syslog
#---------------------------

# log levels:
# lPanic - try to log this before we die
# lErr   - some error occured, may be recoverable
# lWarn  - something should be done about this though it's not fatal
# lInfo  - user info like program flow
# lData  - raw data processed by program

lPanic, lErr, lWarn, lInfo, lData = range(5)

lUncooked = 0
lCooked = 1

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

class Logger:
    # file(s), stdout/stderr, pipes, email, syslog, widget, you-name-it
    # can be any arbitrary object derived from LogTarget
    __targets = {}

    def __init__(self, aTarget):
	"""Standard screen output will be redirected to 'stdout' if not None
	Standard error output will be redirected to 'stderr' if not None
	These arguments can be any class instance having a method 'write(string)'"""
	self.AddTarget (aTarget)
	
    def close(self):
	for key in self.__targets.keys():
	    self.__targets[key].close()

    def AddTarget (self, aTarget):
	# log warning if any targets defined yet
	if self.__targets is not None:
	    self.Log(lInfo, 'SECURITY: adding log target "' + str(aTarget.getID()) + '"')
	# no duplicate targets
	if not self.__targets.has_key(aTarget.getID()):
	    self.__targets[aTarget.getID()] = aTarget

    def RemoveTarget (self, anID):
	"""
	remove a log target by it's ID,
	clients have to track target ID's themselves if they want to remove targets
	"""
	if self.__targets.has_key(anID):
	    self.Log(lWarn, 'SECURITY: removing log target "' + str(anID) + '"')
	    self.__targets[anID].close()
	    del self.__targets[anID]

    def Log(self, aLogLevel, aMsg, aRawnessFlag = lUncooked):
	# are we in for work ?
	if self.__targets is not None:
	    # shall we cook it ?
	    if aRawnessFlag == lCooked:
		msg = reduce(lambda x, y: x+y, (map(self.__char2AsciiName, list(aMsg))))
	    else:
		msg = aMsg

	    # now dump it
	    for key in self.__targets.keys():
		self.__targets[key].write(aLogLevel, msg)

    def LogDelimiter (self):
	for key in self.__targets.keys():
	    self.__targets[key].writeDelimiter()

    def LogException(self, aMsg, exception):
    	"""logs the exception with a timestamp.
	'exception' is a tuple as returned by sys.exc_info()
	If 'promptfunc' is not None, the result of promptfunc is returned
	else Error() returns None.
	prototype: promptfunc(message, timestamp)"""

	for key in self.__targets.keys():
	    self.__targets[key].write(lPanic, aMsg)

	t, v, tb = exception
	tbs = traceback.format_exception(t, v, tb)

	for line in tbs:
	    for key in self.__targets.keys():
		self.__targets[key].write(lPanic, reduce(lambda x, y: x+y, (map(self.__char2AsciiName, list(line)))))

	return None

    def __char2AsciiName(self, aChar):
	if ord(aChar) in range(0,32):
	    return AsciiName[ord(aChar)]
	else:
	    return aChar
#---------------------------------------------------------------
class LogTarget:
    # used to add/remove target in logger
    ID = None
    # default
    __activeLogLevel = lErr
    # any security related items should be tagged with "SECURITY" by the programmer
    __LogLevelPrefix = {lPanic: '[PANIC] ', lErr: '[ERROR] ', lWarn: '[WARN]  ', lInfo: '[INFO]  ', lData: '[DATA]  '}

    def __init__(self, aLogLevel = lErr):
	self.__activeLogLevel = aLogLevel
	self.writeDelimiter()
	self.write (lPanic, "SECURITY: log level on __init__() is " + self.__LogLevelPrefix[self.__activeLogLevel])

    def close(self):
	self.write (lPanic, "SECURITY: closing log target (ID = " + str(self.ID) + ")")

    def getID (self):
	return self.ID

    def SetLogLevel(self, aLogLevel):
	# are we sane ?
	if aLogLevel not in range(lData+1):
	    self.write (lPanic, "SECURITY: trying to set invalid log level (" + str(aLogLevel) + ") - keeping current log level (" + str(self.__activeLogLevel) + ")")
	    return None
	# log the change
	self.write (lPanic, "SECURITY: log level change from " + self.__LogLevelPrefix[self.__activeLogLevel] + " to " + self.__LogLevelPrefix[aLogLevel])
	self.__activeLogLevel = aLogLevel
	return self.__activeLogLevel

    def write (self, aLogLevel, aMsg):
	if aLogLevel <= self.__activeLogLevel:
	    timestamp = self.__timestamp()
	    severity = self.__LogLevelPrefix[aLogLevel]
	    self.__tracestack()
	    caller = "(" + self.__modulename + "::" + self.__functionname + ":" + str(self.__linenumber) + "): "
	    if aLogLevel > lErr:
		self.dump2stdout (timestamp, severity, caller, aMsg + "\n")
	    else:
		self.dump2stderr (timestamp, severity, caller, aMsg + "\n")

    def writeDelimiter (self):
	self.dump2stdout (self.__timestamp(), '', '', '------------------------------------------------------------\n')

    def flush (self):
	pass

    # Private methods - you never have to use those directly

    # stdout equivalent for lWarn and above
    def dump2stdout (self, aTimestamp, aSeverity, aCaller, aMsg):
	# for most log targest we make no distinction between stderr and stdout
	self.dump2stderr (aTimestamp, aSeverity, aCaller, aMsg)

    # stderr equivalent for lPanic, lErr
    def dump2stderr (self, aTimestamp, aSeverity, aCaller, aMsg):
	print "LogTarget: You forgot to override dump2stderr() !\n"

    def __timestamp(self):
	return time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime(time.time()))

    def __tracestack(self):
        stack = traceback.extract_stack()
	self.__modulename = stack[-4][0]
        self.__linenumber = stack[-4][1]
        self.__functionname = stack[-4][2]
        if (self.__functionname == "?"):
            self.__functionname = "Main"

#---------------------------------------------------------------
class LogTargetFile(LogTarget):
    # the actual file handle
    __handle = None

    def __init__ (self, aFileName, aMode, aLogLevel):
	# do our extra work
	self.__handle = open (aFileName, aMode)
	if self.__handle is None:
	    return None
	else:
	    # call inherited
	    LogTarget.__init__(self, aLogLevel)
	    self.ID = os.path.abspath (aFileName) # the file name canonicalized

	self.write (lData, "instantiated log file " + aFileName + " with ID " + str(self.ID))

    def close(self):
	LogTarget.close(self)
	self.__handle.close()

    def dump2stderr (self, aTimeStamp, aPrefix, aLocation, aMsg):
	self.__handle.write(aTimeStamp + aPrefix + aLocation + aMsg)

#---------------------------------------------------------------
class LogTargetConsole(LogTarget):
    def __init__ (self, aLogLevel = lErr):
	# call inherited
	LogTarget.__init__(self, aLogLevel)
	# do our extra work
	self.ID = "stdout/stderr"
	self.write (lData, "instantiated console logging with ID " + str(self.ID))

    def dump2stdout (self, aTimeStamp, aPrefix, aLocation, aMsg):
	sys.stdout.write(aTimeStamp + aPrefix + aLocation + aMsg)

    def dump2stderr (self, aTimeStamp, aPrefix, aLocation, aMsg):
	sys.stderr.write(aTimeStamp + aPrefix + aLocation + aMsg)

#---------------------------------------------------------------
class LogTargetSyslog(LogTarget):
    def __init__ (self, aLogLevel = lErr):
	# call inherited
	LogTarget.__init__(self, aLogLevel)
	# do our extra work
	syslog.openlog(os.path.basename(sys.argv[0]))
	syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))
	self.ID = "syslog"
	self.write (lData, "instantiated syslog logging with ID " + str(self.ID))

    def close(self):
	LogTarget.close(self)
	syslog.closelog()

    def dump2stdout (self, aTimeStamp, aPrefix, aLocation, aMsg):
	syslog.syslog ((syslog.LOG_USER | syslog.LOG_INFO), aPrefix + aLocation + aMsg)

    def dump2stderr (self, aTimeStamp, aPrefix, aLocation, aMsg):
	syslog.syslog ((syslog.LOG_USER | syslog.LOG_ERR), aPrefix + aLocation + aMsg)

#------- MAIN -------------------------------------------------------
if __name__ == "__main__":
    print "\nTesting module gmLog\n=========================="

    # create a file target
    loghandle = LogTargetFile ("test.log", "a", lData)

    # procure the ID
    handleID = loghandle.getID()
    print (str(handleID))

    # and use that to populate the logger
    log = Logger(loghandle)

    # should log a security warning
    loghandle.SetLogLevel (lWarn)

    # should log a security warning and fail
    loghandle.SetLogLevel (12)

    # we are sane again - play with this for different verbosity leveles
    loghandle.SetLogLevel (lData)

    # now do something
    log.Log (lInfo, "starting whatever we were about to do")

    print "Hello world !"

    print "Let's add a console logging handle."
    # let's add a console log target - it can have it's own log level
    consolehandle = LogTargetConsole (lInfo)
    log.AddTarget (consolehandle)

    log.Log (lData, "this should only show up in the log file")
    log.Log (lInfo, "this should show up both on console and in the log file")

    # syslog is cool, too
    print "adding syslog logging"
    sysloghandle = LogTargetSyslog (lWarn)
    log.AddTarget (sysloghandle)

    log.Log (lData, "the logger object uncooked: " + str(log))
    log.Log (lInfo, "and now cooked with some non-printables appended:")
    log.Log (lData, str(log) + "\001\002\003\004\005\012\013\015", lCooked)
    log.Log (lErr, "an error occurred ...")

    print "Now, try an exception (divison / zero)"
    try:
	n = 1/0
    except:
	e = sys.exc_info()
	log.LogException("Exception caught !", e)

    log.Log (lInfo, "done with whatever we were about to do")
    log.close()

    print "Done."
