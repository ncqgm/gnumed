#!/usr/bin/python

"""This module encapsulates mime operations.

@copyright: GPL
"""
#=======================================================================================
import os, mailcap, string
import gmLog

__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__version__ = "$Revision: 1.3 $"

__log__ = gmLog.gmDefLog
#=======================================================================================
def guess_mimetype(aFileName = None):
    """Guess mime type of arbitrary file."""
    # sanity check
    if aFileName == None:
	__log__.Log(gmLog.lErr, "Cannot guess mimetypes if I don't have any file to guess on.")
	return None

    # this only works on POSIX with 'file' installed (which is standard, however)
    if os.name == 'posix':
	aPipe = os.popen("file -i -b %s" % aFileName)
	mime_type = string.replace(aPipe.readline(), "\n", "")
	aPipe.close()
    # sorry, no mime types on lesser operating systems ...
    # please send me your improvements
    else:
	__log__.Log(gmLog.lWarn, "No mime type detection available on this system. Please send your suggestions.")
	mime_type = 'application/octet-stream'

    return mime_type
#-----------------------------------------------------------------------------------
def get_viewer_cmd(aMimeType = None, aFileName = None, aToken = None):
    """Return command for viewer for this mime type."""

    # sanity checks
    if aMimeType == None:
	__log__.Log(gmLog.lErr, "Cannot determine viewer if I don't have a mime type.")
	return None

    if aFileName == None:
	__log__.Log(gmLog.lErr, "You should specify a file name for the replacement of %s.")
	aFileName = """%s"""

    mailcaps = mailcap.getcaps()
    (cmd, junk) = mailcap.findmatch(mailcaps, aMimeType, key = 'view', filename = aFileName)
    # FIXME: actually we should check for "x-token" flags such as x-docsys
    return cmd
#-----------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    print str(guess_mimetype(filename))
    print str(get_viewer_cmd(guess_mimetype(filename), filename))
