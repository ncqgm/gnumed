# -*- coding: utf-8 -*-

"""This module encapsulates mime operations.

	http://www.dwheeler.com/essays/open-files-urls.html
"""
#=======================================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# stdlib
import sys
import os
import mailcap
import mimetypes
import subprocess
import shutil
import logging
import io


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
import gmShellAPI
import gmTools
import gmCfg2
import gmWorkerThread


_log = logging.getLogger('gm.docs')

#=======================================================================================
def guess_mimetype(filename=None):
	"""Guess mime type of arbitrary file.

	filenames are supposed to be in Unicode
	"""
	worst_case = "application/octet-stream"

	# 1) use Python libextractor
	try:
		import extractor
		xtract = extractor.Extractor()
		props = xtract.extract(filename = filename)
		for prop, val in props:
			if (prop == 'mimetype') and (val != worst_case):
				return val
	except ImportError:
		_log.debug('module <extractor> (python wrapper for libextractor) not installed')

	ret_code = -1

	# 2) use "file" system command
	#    -i get mime type
	#    -b don't display a header
	mime_guesser_cmd = u'file -i -b "%s"' % filename
	# this only works on POSIX with 'file' installed (which is standard, however)
	# it might work on Cygwin installations
	aPipe = os.popen(mime_guesser_cmd.encode(sys.getfilesystemencoding()), 'r')
	if aPipe is None:
		_log.debug("cannot open pipe to [%s]" % mime_guesser_cmd)
	else:
		pipe_output = aPipe.readline().replace('\n', '').strip()
		ret_code = aPipe.close()
		if ret_code is None:
			_log.debug('[%s]: <%s>' % (mime_guesser_cmd, pipe_output))
			if pipe_output not in [u'', worst_case]:
				return pipe_output.split(u';')[0].strip()
		else:
			_log.error('[%s] on %s (%s): failed with exit(%s)' % (mime_guesser_cmd, os.name, sys.platform, ret_code))

	# 3) use "extract" shell level libextractor wrapper
	mime_guesser_cmd = 'extract -p mimetype "%s"' % filename
	aPipe = os.popen(mime_guesser_cmd.encode(sys.getfilesystemencoding()), 'r')
	if aPipe is None:
		_log.debug("cannot open pipe to [%s]" % mime_guesser_cmd)
	else:
		pipe_output = aPipe.readline()[11:].replace('\n', '').strip()
		ret_code = aPipe.close()
		if ret_code is None:
			_log.debug('[%s]: <%s>' % (mime_guesser_cmd, pipe_output))
			if pipe_output not in [u'', worst_case]:
				return pipe_output
		else:
			_log.error('[%s] on %s (%s): failed with exit(%s)' % (mime_guesser_cmd, os.name, sys.platform, ret_code))

	# If we and up here we either have an insufficient systemwide
	# magic number file or we suffer from a deficient operating system
	# alltogether. It can't get much worse if we try ourselves.

	_log.info("OS level mime detection failed, falling back to built-in magic")

	import gmMimeMagic
	mime_type = gmTools.coalesce(gmMimeMagic.file(filename), worst_case)
	del gmMimeMagic

	_log.debug('"%s" -> <%s>' % (filename, mime_type))
	return mime_type

#-----------------------------------------------------------------------------------
def get_viewer_cmd(aMimeType = None, aFileName = None, aToken = None):
	"""Return command for viewer for this mime type complete with this file"""

	if aFileName is None:
		_log.error("You should specify a file name for the replacement of %s.")
		# last resort: if no file name given replace %s in original with literal '%s'
		# and hope for the best - we certainly don't want the module default "/dev/null"
		aFileName = """%s"""

	mailcaps = mailcap.getcaps()
	(viewer, junk) = mailcap.findmatch(mailcaps, aMimeType, key = 'view', filename = '%s' % aFileName)
	# FIXME: we should check for "x-token" flags

	_log.debug("<%s> viewer: [%s]" % (aMimeType, viewer))

	return viewer

#-----------------------------------------------------------------------------------
def get_editor_cmd(mimetype=None, filename=None):

	if filename is None:
		_log.error("You should specify a file name for the replacement of %s.")
		# last resort: if no file name given replace %s in original with literal '%s'
		# and hope for the best - we certainly don't want the module default "/dev/null"
		filename = """%s"""

	mailcaps = mailcap.getcaps()
	(editor, junk) = mailcap.findmatch(mailcaps, mimetype, key = 'edit', filename = '%s' % filename)

	# FIXME: we should check for "x-token" flags

	_log.debug("<%s> editor: [%s]" % (mimetype, editor))

	return editor

#-----------------------------------------------------------------------------------
def guess_ext_by_mimetype(mimetype=''):
	"""Return file extension based on what the OS thinks a file of this mimetype should end in."""

	# ask system first
	ext = mimetypes.guess_extension(mimetype)
	if ext is not None:
		_log.debug('<%s>: *.%s' % (mimetype, ext))
		return ext

	_log.error("<%s>: no suitable file extension known to the OS" % mimetype)

	# try to help the OS a bit
	cfg = gmCfg2.gmCfgData()
	ext = cfg.get (
		group = u'extensions',
		option = mimetype,
		source_order = [('user-mime', 'return'), ('system-mime', 'return')]
	)

	if ext is not None:
		_log.debug('<%s>: *.%s (%s)' % (mimetype, ext, candidate))
		return ext

	_log.error("<%s>: no suitable file extension found in config files" % mimetype)

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
		_log.error('unable to guess file extension for mime type [%s]' % mime_type)
		return None

	return f_ext

#-----------------------------------------------------------------------------------
_system_startfile_cmd = None

open_cmds = {
	'xdg-open': 'xdg-open "%s"',			# nascent standard on Linux
	'kfmclient': 'kfmclient exec "%s"',		# KDE
	'gnome-open': 'gnome-open "%s"',		# GNOME
	'exo-open': 'exo-open "%s"',
	'op': 'op "%s"',
	'open': 'open "%s"',					# MacOSX: "open -a AppName file" (-a allows to override the default app for the file type)
	'cmd.exe': 'cmd.exe /c "%s"'			# Windows
	#'run-mailcap'
	#'explorer'
}

def _get_system_startfile_cmd(filename):

	global _system_startfile_cmd

	if _system_startfile_cmd == u'':
		return False, None

	if _system_startfile_cmd is not None:
		return True, _system_startfile_cmd % filename

	open_cmd_candidates = open_cmds.keys()

	for candidate in open_cmd_candidates:
		found, binary = gmShellAPI.detect_external_binary(binary = candidate)
		if not found:
			continue
		_system_startfile_cmd = open_cmds[candidate]
		_log.info('detected local startfile cmd: [%s]', _system_startfile_cmd)
		return True, _system_startfile_cmd % filename

	_system_startfile_cmd = u''
	return False, None

#-----------------------------------------------------------------------------------
def convert_file(filename=None, target_mime=None, target_filename=None, target_extension=None):
	"""Convert file from one format into another.

		target_mime: a mime type
	"""
	if target_extension is None:
		tmp, target_extension = os.path.splitext(target_filename)

	base_name = u'gm-convert_file'

	paths = gmTools.gmPaths()
	local_script = os.path.join(paths.local_base_dir, '..', 'external-tools', base_name)

	candidates = [ base_name, local_script ]		#, base_name + u'.bat'
	found, binary = gmShellAPI.find_first_binary(binaries = candidates)
	if not found:
		binary = base_name# + r'.bat'

	cmd_line = [
		binary,
		filename,
		target_mime,
		target_extension.strip('.'),
		target_filename
	]
	_log.debug('converting: %s', cmd_line)
	try:
		gm_convert = subprocess.Popen(cmd_line)
	except OSError:
		_log.debug('cannot run <%s(.bat)>', base_name)
		return False
	gm_convert.communicate()
	if gm_convert.returncode != 0:
		_log.error('<%s(.bat)> returned [%s], failed to convert', base_name, gm_convert.returncode)
		return False

	return True

#-----------------------------------------------------------------------------------
def __run_file_describer(filename=None):

	base_name = u'gm-describe_file'

	paths = gmTools.gmPaths()
	local_script = os.path.join(paths.local_base_dir, '..', 'external-tools', base_name)

	candidates = [ base_name, local_script ]		#, base_name + u'.bat'
	found, binary = gmShellAPI.find_first_binary(binaries = candidates)
	if not found:
		#binary = base_name# + r'.bat'
		_log.debug(u'cannot find <%s(.bat)>', base_name)
		return (False, _(u'<%s(.bat)> not found') % base_name)

	desc_fname = gmTools.get_unique_filename()

	cmd_line = [
		binary,
		filename,
		desc_fname
	]
	_log.debug('describing: %s', cmd_line)
	try:
		gm_describe = subprocess.Popen(cmd_line)
	except OSError:
		_log.debug('cannot run <%s>', binary)
		return (False, _(u'problem with <%s>') % binary)

	gm_describe.communicate()
	if gm_describe.returncode != 0:
		_log.error('<%s> returned [%s], failed to convert', binary, gm_describe.returncode)
		return (False, _(u'problem with <%s>') % binary)

	try:
		desc_file = io.open(desc_fname, mode = 'rt', encoding = 'utf8', errors = 'replace')
	except IOError:
		_log.exception('cannot open [%s]', desc_fname)
		return (False, _(u'problem with <%s>') % binary)

	desc = u''.join(desc_file.readlines())
	desc_file.close()
	return (True, desc)

#-----------------------------------------------------------------------------------
def describe_file(filename, callback=None):
	if callback is None:
		return __run_file_describer(filename)

	payload_kwargs = {'filename': filename}
	gmWorkerThread.execute_in_worker_thread (
		payload_function = __run_file_describer,
		payload_kwargs = payload_kwargs,
		completion_callback = callback
	)

#-----------------------------------------------------------------------------------
def call_viewer_on_file(aFile = None, block=None):
	"""Try to find an appropriate viewer with all tricks and call it.

	block: try to detach from viewer or not, None means to use mailcap default
	"""
	if not os.path.isdir(aFile):
		# is the file accessible at all ?
		try:
			open(aFile).close()
		except:
			_log.exception('cannot read [%s]', aFile)
			msg = _('[%s] is not a readable file') % aFile
			return False, msg

	# try to detect any of the UNIX openers
	found, startfile_cmd = _get_system_startfile_cmd(aFile)
	if found:
		if gmShellAPI.run_command_in_shell(command = startfile_cmd, blocking = block):
			return True, ''

	mime_type = guess_mimetype(aFile)
	viewer_cmd = get_viewer_cmd(mime_type, aFile)

	if viewer_cmd is not None:
		if gmShellAPI.run_command_in_shell(command = viewer_cmd, blocking = block):
			return True, ''

	_log.warning("no viewer found via standard mailcap system")
	if os.name == "posix":
		_log.warning("you should add a viewer for this mime type to your mailcap file")

	_log.info("let's see what the OS can do about that")

	# does the file already have an extension ?
	(path_name, f_ext) = os.path.splitext(aFile)
	# no
	if f_ext in ['', '.tmp']:
		# try to guess one
		f_ext = guess_ext_by_mimetype(mime_type)
		if f_ext is None:
			_log.warning("no suitable file extension found, trying anyway")
			file_to_display = aFile
			f_ext = '?unknown?'
		else:
			file_to_display = aFile + f_ext
			shutil.copyfile(aFile, file_to_display)
	# yes
	else:
		file_to_display = aFile

	file_to_display = os.path.normpath(file_to_display)
	_log.debug("file %s <type %s> (ext %s) -> file %s" % (aFile, mime_type, f_ext, file_to_display))

	try:
		os.startfile(file_to_display)
		return True, ''
	except AttributeError:
		_log.exception('os.startfile() does not exist on this platform')
	except:
		_log.exception('os.startfile(%s) failed', file_to_display)

	msg = _("Unable to display the file:\n\n"
			" [%s]\n\n"
			"Your system does not seem to have a (working)\n"
			"viewer registered for the file type\n"
			" [%s]"
	) % (file_to_display, mime_type)
	return False, msg

#=======================================================================================
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	# for testing:
	logging.basicConfig(level = logging.DEBUG)

	filename = sys.argv[2]

	#_get_system_startfile_cmd(filename)
	#print(_system_startfile_cmd)
	#print(guess_mimetype(filename))
	#print(get_viewer_cmd(guess_mimetype(filename), filename))
	#print(guess_ext_by_mimetype(mimetype=filename))
	#call_viewer_on_file(aFile = filename, block=None)
	status, desc = describe_file(filename)
	print status
	print desc
