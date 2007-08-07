# -*- coding: latin-1 -*-

"""This module encapsulates mime operations.
"""
#=======================================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmMimeLib.py,v $
# $Id: gmMimeLib.py,v 1.11 2007-08-07 21:40:36 ncq Exp $
__version__ = "$Revision: 1.11 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

import os, mailcap, sys, mimetypes, shutil


if __name__ == '__main__':
	sys.path.insert(0, '../../')
import gmLog, gmShellAPI, gmTools, gmCfg


_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#=======================================================================================
def guess_mimetype(aFileName = None):
	"""Guess mime type of arbitrary file.

	filenames are supposed to be in Unicode
	"""
	worst_case = "application/octet-stream"

	# 1) use Python libextractor
	# - but we don't have docs for that

	ret_code = -1

	# 2) use "file" system command
	#    -i get mime type
	#    -b don't display a header
	mime_guesser_cmd = u'file -i -b "%s"' % aFileName
	# this only works on POSIX with 'file' installed (which is standard, however)
	# it might work on Cygwin installations
	aPipe = os.popen(mime_guesser_cmd.encode(sys.getfilesystemencoding()), 'r')
	if aPipe is None:
		_log.Log(gmLog.lData, "cannot open pipe to [%s]" % mime_guesser_cmd)
	else:
		pipe_output = aPipe.readline().replace('\n', '').strip()
		ret_code = aPipe.close()
		if ret_code is None:
			_log.Log(gmLog.lData, '[%s]: <%s>' % (mime_guesser_cmd, pipe_output))
			if pipe_output not in [u'', worst_case]:
				return pipe_output
		else:
			_log.Log(gmLog.lErr, '[%s] on %s (%s): failed with exit(%s)' % (mime_guesser_cmd, os.name, sys.platform, ret_code))

	# 3) use "extract" shell level libextractor wrapper
	mime_guesser_cmd = 'extract -p mimetype "%s"' % aFileName
	aPipe = os.popen(mime_guesser_cmd.encode(sys.getfilesystemencoding()), 'r')
	if aPipe is None:
		_log.Log(gmLog.lData, "cannot open pipe to [%s]" % mime_guesser_cmd)
	else:
		pipe_output = aPipe.readline()[11:].replace('\n', '').strip()
		ret_code = aPipe.close()
		if ret_code is None:
			_log.Log(gmLog.lData, '[%s]: <%s>' % (mime_guesser_cmd, pipe_output))
			if pipe_output not in [u'', worst_case]:
				return pipe_output
		else:
			_log.Log(gmLog.lErr, '[%s] on %s (%s): failed with exit(%s)' % (mime_guesser_cmd, os.name, sys.platform, ret_code))

	# if we and up here we either have an insufficient systemwide
	# magic number file or we suffer from a deficient operating system
	# altogether, it can't get much worse if we try ourselves

	_log.Log(gmLog.lInfo, "OS level mime detection failed, falling back to built-in magic")

	import gmMimeMagic
	mime_type = gmTools.coalesce(gmMimeMagic.file(aFileName), worst_case)
	del gmMimeMagic

	_log.Log(gmLog.lData, '"%s" -> <%s>' % (aFileName, mime_type))
	return mime_type
#-----------------------------------------------------------------------------------
def get_viewer_cmd(aMimeType = None, aFileName = None, aToken = None):
	"""Return command for viewer for this mime type complete with this file"""

	if aFileName is None:
		_log.Log(gmLog.lErr, "You should specify a file name for the replacement of %s.")
		# last resort: if no file name given replace %s in original with literal '%s'
		# and hope for the best - we certainly don't want the module default "/dev/null"
		aFileName = """%s"""

	mailcaps = mailcap.getcaps()
	(viewer, junk) = mailcap.findmatch(mailcaps, aMimeType, key = 'view', filename = '%s' % aFileName)
	# FIXME: we should check for "x-token" flags

	_log.Log(gmLog.lData, "<%s> viewer: [%s]" % (aMimeType, viewer))

	return viewer
#-----------------------------------------------------------------------------------
def guess_ext_by_mimetype(mimetype=''):
	"""Return file extension based on what the OS thinks a file of this mimetype should end in."""

	# FIXME: does this screw up with scope of binding vs. scope of import ?
	ext = mimetypes.guess_extension(mimetype)
	if ext is not None:
		_log.Log(gmLog.lData, '<%s>: *.%s' % (mimetype, ext))
		return ext

	_log.Log(gmLog.lErr, "<%s>: no suitable file extension known to the OS" % mimetype)

	# try to help the OS a bit
	fname = u'mime_type2file_extension.conf'
	paths = gmTools.gmPaths()
	candidates = [
		os.path.join(paths.user_config_dir, fname),
		os.path.join(paths.system_config_dir, fname)
	]

	for candidate in candidates:
		try:
			cfg = gmCfg.cCfgFile(aFile = candidate)
		except IOError:
			continue
		ext = cfg.get('extensions', mimetype)
		if ext is not None:
			_log.Log(gmLog.lData, '<%s>: *.%s (%s)' % (mimetype, ext, candidate))
			return ext

	_log.Log(gmLog.lErr, "<%s>: no suitable file extension found in [%s]" % (mimetype, ', '.join(candidates)))

	return ext
#-----------------------------------------------------------------------------------
def guess_ext_for_file(aFile=None):
	if aFile is None:
		return None

	(path_name, f_ext) = os.path.splitext(aFile)
	if f_ext != '':
		return f_ext

	# try to guess one
	mime_type = guess_mimetype(aFile)
	f_ext = guess_ext_by_mimetype(mime_type)
	if f_ext is None:
		_log.Log(gmLog.lErr, 'unable to guess file extension for mime type [%s]' % mime_type)
		return None

	return f_ext
#-----------------------------------------------------------------------------------
def call_viewer_on_file(aFile = None, block=None):
	"""Try to find an appropriate viewer with all tricks and call it.

	block: try to detach from viewer or not, None means to use mailcap default
	"""

	# does this file exist, actually ?
	if not (os.path.isfile(aFile) and os.access(aFile, os.R_OK)):
		msg = '[%s] is not a readable file' % aFile
		_log.Log(gmLog.lErr, msg)
		raise IOError(msg)

	# sigh ! let's be off to work
	mime_type = guess_mimetype(aFile)
	viewer_cmd = get_viewer_cmd(mime_type, aFile)

	if viewer_cmd is not None:
		if gmShellAPI.run_command_in_shell(command=viewer_cmd, blocking=block):
			return True, ''

	_log.Log(gmLog.lWarn, "no viewer found via standard mailcap system")
	if os.name == "posix":
		_log.Log(gmLog.lWarn, "You should add a viewer for this mime type to your mailcap file.")
		msg = _("Unable to display the file:\n\n"
				" [%s]\n\n"
				"Your system does not seem to have a (working)\n"
				"viewer registered for the file type\n"
				" [%s]"
		) % (aFile, mime_type)
		return False, msg

	_log.Log(gmLog.lInfo, "let's see what the OS can do about that")
	# does the file already have an extension ?
	(path_name, f_ext) = os.path.splitext(aFile)
	# no
	if f_ext == '':
		# try to guess one
		f_ext = guess_ext_by_mimetype(mime_type)
		if f_ext is None:
			_log.Log(gmLog.lWarn, "no suitable file extension found, trying sheer luck")
			file_to_display = aFile
			f_ext = '?unknown?'
		else:
			file_to_display = aFile + f_ext
			shutil.copyfile(aFile, file_to_display)
	# yes
	else:
		file_to_display = aFile

	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
	# FIXME: this needs more experimentation on Windows
	file_to_display = os.path.normpath(file_to_display)
	#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

	_log.Log(gmLog.lData, "file %s <type %s> (ext %s) -> file %s" % (aFile, mime_type, f_ext, file_to_display))
	try:
		os.startfile(file_to_display)
	except:
		_log.LogException('os.startfile(%s) failed' % file_to_display)
		return False, _("Unable to start viewer on file [%s].") % file_to_display

	# don't kill the file from under the (possibly async) viewer
#	if file_to_display != aFile:
#		os.remove(file_to_display)

	return True, ''
#=======================================================================================
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
	filename = sys.argv[1]

	print guess_mimetype(filename)
	print get_viewer_cmd(guess_mimetype(filename), filename)
#	print guess_ext_by_mimetype(mimetype=filename)

#=======================================================================================
# $Log: gmMimeLib.py,v $
# Revision 1.11  2007-08-07 21:40:36  ncq
# - streamline code
# - teach guess_ext_by_mimetype() about mime_type2file_name.conf
#
# Revision 1.10  2007/07/09 12:39:36  ncq
# - cleanup, improved logging
#
# Revision 1.9  2007/03/31 21:20:14  ncq
# - os.popen() needs encoded command strings
# - fix test suite
#
# Revision 1.8  2006/12/23 15:24:28  ncq
# - use gmShellAPI
#
# Revision 1.7  2006/10/31 17:19:26  ncq
# - some ERRORs are really WARNings
#
# Revision 1.6  2006/09/12 17:23:30  ncq
# - add block argument to call_viewer_on_file()
# - improve file access checks and raise exception on failure
# - improve some error messages
#
# Revision 1.5  2006/06/17 13:15:10  shilbert
# - shutil import was added to make it work on Windows
#
# Revision 1.4  2006/05/16 15:50:51  ncq
# - properly escape filename
#
# Revision 1.3  2006/05/01 18:47:16  ncq
# - add use of "extract" command in mimetype guessing
#
# Revision 1.2  2004/10/11 19:08:08  ncq
# - guess_ext_for_file()
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.5  2003/11/17 10:56:36  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.4  2003/06/26 21:34:43  ncq
# - fatal->verbose
#
# Revision 1.3  2003/04/20 15:33:03  ncq
# - call_viewer_on_file() belongs here, I guess
#
# Revision 1.2  2003/02/17 16:17:20  ncq
# - fix typo
#
# Revision 1.1  2003/02/14 00:22:17  ncq
# - mime ops for general use
#
