#!/usr/bin/python

"""This module encapsulates mime operations.

@copyright: GPL
"""
#=======================================================================================
import gmLog

__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__version__ = "$Revision: 1.1 $"

__log__ = gmLog.gmDefLog
#=======================================================================================
def guess_mimetype(aFileName = None):
    """Guess mime type of arbitrary file.

    Perhaps this should be moved elsewhere (another module).
    """
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
