"""This module encapsulates mime operations.
"""
#=======================================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmMimeLib.py,v $
# $Id: gmMimeLib.py,v 1.3 2003-04-20 15:33:03 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import os, mailcap, string, sys

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)
#=======================================================================================
def guess_mimetype(aFileName = None):
	"""Guess mime type of arbitrary file."""
	# sanity check
	if not os.path.exists(aFileName):
		_log.Log(gmLog.lErr, "Cannot guess mimetypes if I don't have any file to guess on.")
		return None

	desperate_guess = "application/octet-stream"
	mime_guesser_cmd = ("file -i -b %s" % aFileName)

	mime_type = desperate_guess
	ret_code = -1
	# this only works on POSIX with 'file' installed (which is standard, however)
	# it might work on Cygwin installations
	# -i get mime type
	# -b don't display a header
	aPipe = os.popen(mime_guesser_cmd, "r")
	if aPipe is None:
		_log.Log(gmLog.lData, "Cannot open pipe to [%s]." % mime_guesser_cmd)
	else:
		tmp = aPipe.readline()
		ret_code = aPipe.close()

	if ret_code is None and tmp != "":
		mime_type = string.replace(tmp, "\n", "")
	else:
		_log.Log(gmLog.lErr, "Something went awry while calling `%s`." % mime_guesser_cmd)
		_log.Log(gmLog.lErr, '%s (%s): exit(%s) -> <%s>' % (os.name, sys.platform, ret_code, tmp))

	# if we still have "application/octet-stream" we either
	# have an insufficient systemwide magic number file or we
	# suffer from a deficient operating system altogether,
	# it can't get much worse if we try ourselves
	if mime_type == desperate_guess:
		_log.Log(gmLog.lInfo, "OS level mime detection failed, falling back to built-in.")

		# we must trade speed vs. RAM now by loading a data file
		try:
			import gmMimeMagic
		except ImportError:
			exc = sys.exc_info()
			_log.LogException("Cannot import internal magic data file.", exc, fatal=0)
			return None
		tmp = gmMimeMagic.file(aFileName)
		# save resources
		del gmMimeMagic

		if not tmp is None:
			mime_type = tmp

	_log.Log(gmLog.lData, '"%s" -> <%s>' % (aFileName, mime_type))
	return mime_type
#-----------------------------------------------------------------------------------
def get_viewer_cmd(aMimeType = None, aFileName = None, aToken = None):
	"""Return command for viewer for this mime type complete with this file"""

	# sanity checks
	if aMimeType is None:
		_log.Log(gmLog.lErr, "Cannot determine viewer if I don't have a mime type.")
		return None

	if aFileName is None:
		_log.Log(gmLog.lErr, "You should specify a file name for the replacement of %s.")
		# last resort: if no file name given replace %s in original with literal '%s'
		# and hope for the best - we certainly don't want the module default "/dev/null"
		aFileName = """%s"""

	mailcaps = mailcap.getcaps()
	(cmd, junk) = mailcap.findmatch(mailcaps, aMimeType, key = 'view', filename = "\'%s\'" % aFileName)
	# FIXME: actually we should check for "x-token" flags such as x-docsys

	#if (cmd is None) and ()
	return cmd
#-----------------------------------------------------------------------------------
def guess_ext_by_mimetype(aMimeType = None):
	"""Return file extension based on what the OS thinks a file of this mimetype should end in."""
	# sanity checks
	if aMimeType is None:
		_log.Log(gmLog.lErr, "Cannot determine file name if I don't have a mime type.")
		return None

	# FIXME: does this screw up with scope of binding vs. scope of import ?
	import mimetypes
	f_ext = mimetypes.guess_extension(aMimeType)
	if f_ext is None:
		_log.Log(gmLog.lErr, "The system does not know the file extension for the mimetype <%s>." % aMimeType)

	return f_ext
#-----------------------------------------------------------------------------------
def call_viewer_on_file(aFile = None):
	"""Try to find an appropriate viewer with all tricks and call it."""

	if aFile is None:
		msg = "No need to call viewer without file name."
		_log.Log(gmLog.lErr, msg)
		return None, msg

	# does this file exist, actually ?
	if not os.path.exists(aFile):
		msg = _('File [%s] does not exist !') % aFile
		_log.Log(gmLog.lErr, msg)
		return None, msg

	# sigh ! let's be off to work
	mime_type = guess_mimetype(aFile)
	_log.Log(gmLog.lData, "mime type : %s" % mime_type)
	viewer_cmd = get_viewer_cmd(mime_type, aFile)
	_log.Log(gmLog.lData, "viewer cmd: '%s'" % viewer_cmd)

	if viewer_cmd != None:
		os.system(viewer_cmd)
		return 1, ""

	_log.Log(gmLog.lErr, "Cannot determine viewer via standard mailcap mechanism.")
	if os.name == "posix":
		_log.Log(gmLog.lErr, "You should add a viewer for this mime type to your mailcap file.")
		msg = _("Unable to start viewer on file\n[%s]\nYou need to update your mailcap file.") % aFile
		return None, msg
	else:
		_log.Log(gmLog.lInfo, "Let's see what the OS can do about that.")
		# does the file already have an extension ?
		(path_name, f_ext) = os.path.splitext(aFile)
		# no
		if f_ext == "":
			# try to guess one
			f_ext = guess_ext_by_mimetype(mime_type)
			if f_ext is None:
				_log.Log(gmLog.lErr, "Unable to guess file extension from mime type. Trying sheer luck.")
				file_to_display = aFile
				f_ext = ""
			else:
				file_to_display = aFile + f_ext
				shutil.copyfile(aFile, file_to_display)
		# yes
		else:
			file_to_display = aFile

		_log.Log(gmLog.lData, "file %s <type %s> (ext %s) -> file %s" % (aFile, mime_type, f_ext, file_to_display))
		try:
			os.startfile(file_to_display)
		except:
			msg = _("Unable to start viewer on file [%s].") % file_to_display		
			_log.LogException(msg, sys.exc_info(), fatal=0)
			return None, msg

	# clean up if necessary
	# don't kill the file from under the (async) viewer
#	if file_to_display != aFile:
#		os.remove(file_to_display)

	return 1, ""
#=======================================================================================
if __name__ == "__main__":
	filename = sys.argv[1]
	print str(guess_mimetype(filename))
	print str(get_viewer_cmd(guess_mimetype(filename), filename))
#=======================================================================================
# $Log: gmMimeLib.py,v $
# Revision 1.3  2003-04-20 15:33:03  ncq
# - call_viewer_on_file() belongs here, I guess
#
# Revision 1.2  2003/02/17 16:17:20  ncq
# - fix typo
#
# Revision 1.1  2003/02/14 00:22:17  ncq
# - mime ops for general use
#
