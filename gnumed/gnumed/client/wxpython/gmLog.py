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

import sys, time, traceback

class Logger:
    __stdout = sys.stdout
    __stderr = sys.stderr
    
    def __init__(self, stdout=None, stderr=None):
	"""Standard screen output will be redirected to 'stdout' if not None
	Standard error output will be redirected to 'stderr' if not None
	These arguments can be any class instance having a method 'write(string)'"""
	
	self.__saved_stdout = Logger.__stdout
	self.__saved_stderr = Logger.__stderr
	if stdout: 
	    self.SetStdout(stdout)
	if stderr:
	    self.SetStderr(stderr)

	    
    def SetStdout(self, stdout):
	"Redirect standard screen output to 'stdout'"
        Logger.__stdout=stdout

    
    def GetStdout(self):
	"returns the current default output object"
	return Logger.__stdout
	

    def SetStderr(self, stderr):
    	"Redirect standard error output to 'stderr'"
	Logger.__stderr=stderr


    def GetStderr(self):
    	"returns the current default error output object"
	return Logger.__stderr
	


    def Restore(self):
	"Restore output redirection to what it originally was"
	try:
    	    self.SetStdout(self.__saved_stdout)
	except:
	    sys.stderr.write("Could not restore stdout redirection in module gmLog")
	try:
	    self.SetStderr(self.__saved_stderr)
	except:
	    sys.stderr.write("Could not restore stderr redirection in module gmLog")

	

    def Log(self, message, timestamped=1):
	"""Log a message. 
	'message' can be any string.
	'timestamped': if zero, timestamp will be omitted"""
	
        output = Logger.__stdout
	output.write('\n')
	if timestamped: 
    	    output.write(time.strftime("%H:%M:%S %Y-%m-%d")+":") ,
	output.write(message+'\n')
	



    def Error(self, message, promptfunc=None):
	"""logs the error with a timestamp.
	If 'promptfunc' is not None, the result of promptfunc is returned
	else Error() returns None.
	prototype: promptfunc(message, timestamp)""" 
	
	output=Logger.__stderr
	timestamp = time.strftime("%H:%M:%S %Y-%m-%d")
	if promptfunc is not None:
	    assert(callable(promptfunc))
	    return promptfunc(message, timestamp)
	else:
	    output.write(timestamp + ':' + message + '\n')
	    return None

    
	    
    def Exception(self, message, exception, promptfunc=None):
    	"""logs the exception with a timestamp.
	'exception' is a tuple as returned by sys.exc_info()
	If 'promptfunc' is not None, the result of promptfunc is returned
	else Error() returns None.
	prototype: promptfunc(message, timestamp)""" 
	
	output = Logger.__stderr
	timestamp = time.strftime("%H:%M:%S %Y-%m-%d")
	if promptfunc is not None:
	    assert(callable(promptfunc))
	    return promptfunc(message, timestamp, exception)
	else:
	    output.write(timestamp + ': ' + message+'\n')	
	    tbs = traceback.format_exception(*exception)
            for s in tbs:
	        output.write(s)
	    return None
	    

	
	

if __name__ == "__main__":
    #(for module testing purposes only)
    
    print "\nTesting module gmLog\n==========================\n"

    #example for output redirection
    #any class will do where a method "write(string)"
    class debugoutput:
	def write(self, msg):
	    print "Debug:", msg
	    


    #Example for a prompting callback function
    def prompt(message, timestamp, exception=None):
	#show the exception traceback if neccessary
	if exception is not None:
	    tbs = traceback.format_exception(*exception)
	    for s in tbs:
		print s	
	print timestamp, '\n'
	print "\nThis is the callback function: (a)bort or (c)ontinue ? ",
	answer = raw_input()
	if answer in ['a', 'A']:
	    return 0
	elif answer in ['c', 'C']:
	    return 1
	else:
	    print "you entered bullshit - continuing anyway"
	    return 1


	
    l = Logger()
    
    print "-> Redirecting error output to file 'error.log'"
    f = open('error.log', 'a')
    l.SetStderr(f)
    d = debugoutput()
    
    print "-> Redirecting standard output to debug 'widget'"
    l.SetStdout(d)
    l.Log("This is logged via debug widget")

    print "-> error message redirected to file error.log"
    l.Error("this is an error\n")
    
    print "-> try a callback function:"
    if not l.Error("TRYING CALLBACK:", promptfunc=prompt):
	print "-> program aborted"
	sys.exit(1)
    else:
	print "-> program continued"
	
	
    l2=Logger()
    #this should be redirected to the same debug "widget" as in "l"
    l2.Log("Now, where is this going to?")

    #let us restore standard IO behaviour
    l.Restore()
    
    l.Log("This should not go to debug anymore")
    l2.Error("this error message should appear on the screen\n")

    print "->Now, try an exception (divison / zero):"
    try:
	n = 1/0
    except:
	l.Exception("Exception caught", exception = sys.exc_info(), promptfunc=prompt)
	
    f.close()    
    
    print "\n->That's all, folks!\n"
    