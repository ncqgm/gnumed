#!/usr/bin/python

"""This module encapsulates mime operations.

@copyright: GPL
"""

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/modules/Attic/docMime.py,v $
__version__ = "$Revision: 1.10 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

#=======================================================================================
import os, mailcap, string, sys
import gmLog

__log__ = gmLog.gmDefLog
#=======================================================================================
def guess_mimetype(aFileName = None):
	"""Guess mime type of arbitrary file."""
	# sanity check
	if not os.path.exists(aFileName):
		__log__.Log(gmLog.lErr, "Cannot guess mimetypes if I don't have any file to guess on.")
		return None

	desperate_guess = "application/octet-stream"
	mime_guesser_cmd = ("file -i -b %s" % aFileName)

	mime_type = desperate_guess
	# this only works on POSIX with 'file' installed (which is standard, however)
	# it might work of Cygwin installations
	# -i get mime type
	# -b don't display a header
	aPipe = os.popen(mime_guesser_cmd)
	tmp = aPipe.readline()
	ret_code = aPipe.close()
	if ret_code == None:
		mime_type = string.replace(tmp, "\n", "")
		__log__.Log(gmLog.lData, "%s -> %s" % (aFileName, mime_type))
	else:
		__log__.Log(gmLog.lErr, "Something went awry while calling `%s`." % mime_guesser_cmd)
		__log__.Log(gmLog.lErr, "%s (%s): [%s] %s" % (os.name, sys.platform, ret_code, tmp))

	# if we still have "application/octet-stream" we either
	# have an insufficient systemwide magic number file or we
	# suffer from a deficient operating system altogether,
	# it can't get much worse if we try ourselves
	if mime_type == desperate_guess:
		__log__.Log(gmLog.lInfo, "OS level mime detection failed, falling back to built-in.")
		# we must trade speed vs. RAM now by loading a data file
		try:
			import docMagic
		except ImportError:
			__log__.Log(gmLog.lErr, "Cannot import internal magic data file !")

		tmp = docMagic.file(aFileName)
		# save ressources
		del docMagic
		if not tmp == None:
			mime_type = tmp

	return mime_type
#-----------------------------------------------------------------------------------
def get_viewer_cmd(aMimeType = None, aFileName = None, aToken = None):
	"""Return command for viewer for this mime type complete with this file"""

	# sanity checks
	if aMimeType == None:
		__log__.Log(gmLog.lErr, "Cannot determine viewer if I don't have a mime type.")
		return None

	if aFileName == None:
		__log__.Log(gmLog.lErr, "You should specify a file name for the replacement of %s.")
		# last resort: if no file name given replace %s in original with literal '%s'
		# and hope for the best - we certainly don't want the module default "/dev/null"
		aFileName = """%s"""

	mailcaps = mailcap.getcaps()
	(cmd, junk) = mailcap.findmatch(mailcaps, aMimeType, key = 'view', filename = "\'%s\'" % aFileName)
	# FIXME: actually we should check for "x-token" flags such as x-docsys

	if (cmd == None) and ()
	return cmd
#-----------------------------------------------------------------------------------
def get_win_fname(aMimeType = None):
	"""Return file name suitable for a given file type in Windows and other inferior OS."""

	# sanity checks
	if aMimeType == None:
		__log__.Log(gmLog.lErr, "Cannot determine file name if I don't have a mime type.")
		return None

	import mimetypes
	f_ext = mimetypes.guess_extension(aMimeType)

	import tempfile
	tempfile.template = "obj-"
	return os.path.normpath(tempfile.mktemp(f_ext))
#-----------------------------------------------------------------------------------
if __name__ == "__main__":
	import sys
	filename = sys.argv[1]
	print str(guess_mimetype(filename))
	print str(get_viewer_cmd(guess_mimetype(filename), filename))
