"""A small convience function to enable strace () -like tracing
of gnumed excpetion

Usage: set_trace () starts the tracing and spits out one line
to stdout for every line of Python executed inside gnumed
Certain modules (such as pycommon) are not traced.
 @copyright: authors
 @dependencies: python >= 2.4
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/Attic/gmTrace.py,v $
# $Id: gmTrace.py,v 1.2 2006-10-31 16:03:25 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "I Haywood"
__license__ = 'GPL (details at http://www.gnu.org)'

import sys, inspect

oldvals = {}
watches = []
taboo = ['gmTrace.py', 'gmPG2.py', 'gmDispatcher.py', 'gmSignals.py', 'gmLog.py', '/site-packages/', '/usr/lib/', 'gmGuiMain.py', 'gmRegetMixin.py', 'gmGuiHelpers.py']


def get_code (frame):
    lineno = frame.f_lineno
    code = frame.f_code
    codestart = code.co_firstlineno
    text = inspect.getsource (code)
    lines = text.splitlines ()
    return lines[lineno-codestart]

def make_args (args):
    return ", ".join (["%s=%s"% (i, repr (args[i])) for i in args.keys ()])

def tracer (frame, event, arg):
    global oldvals
    global watches
    global taboo
    if event == 'line':
        code = frame.f_code
        print "%s: %s: %s" % (inspect.getsourcefile (code), frame.f_lineno, get_code (frame))
        return tracer
    if event == 'call':
        try:
            f = inspect.getsourcefile (frame.f_code)
            if f is None:
                f = "<None>"
            for t in taboo:
                if f.find (t) > -1:
                    return None
            print "%s: %s: CALL %s (%s)" % (f, frame.f_lineno, frame.f_code.co_name, make_args (frame.f_locals))
            return tracer
        except TypeError:
            return None
    if event == 'return':
        code = frame.f_code
        print "%s: %s: RETURN %s" % (inspect.getsourcefile (code), frame.f_lineno, repr (arg))
    if event == 'exception':
        exception, value, bt = arg
        print "%s: %s: EXCEPTION %s (%s)" % (inspect.getsourcefile (frame.f_code), frame.f_lineno, exception, repr (value))
        return None


def set_trace (w=[]):
    global watches
    watches = w
    sys.settrace (tracer)
