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
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmCfg2
from Gnumed.pycommon import gmWorkerThread


_log = logging.getLogger('gm.mime')

#=======================================================================================
def guess_mimetype(filename=None):
	"""Guess mime type of arbitrary file.

	filenames are supposed to be in Unicode
	"""
	worst_case = "application/octet-stream"
	_log.debug('guessing mime type of [%s]', filename)
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
	except OSError as exc:
		# winerror 126, errno 22
		if exc.errno != 22:
			raise
		_log.exception('module <extractor> (python wrapper for libextractor) not installed')

	ret_code = -1
	# 2) use "file" system command
	#    -i get mime type
	#    -b don't display a header
	mime_guesser_cmd = 'file -i -b "%s"' % filename
	# this only works on POSIX with 'file' installed (which is standard, however)
	# it might work on Cygwin installations
	aPipe = os.popen(mime_guesser_cmd, 'r')
	if aPipe is None:
		_log.debug("cannot open pipe to [%s]" % mime_guesser_cmd)
	else:
		pipe_output = aPipe.readline().replace('\n', '').strip()
		ret_code = aPipe.close()
		if ret_code is None:
			_log.debug('[%s]: <%s>' % (mime_guesser_cmd, pipe_output))
			if pipe_output not in ['', worst_case]:
				return pipe_output.split(';')[0].strip()
		else:
			_log.error('[%s] on %s (%s): failed with exit(%s)' % (mime_guesser_cmd, os.name, sys.platform, ret_code))

	# 3) use "extract" shell level libextractor wrapper
	mime_guesser_cmd = 'extract -p mimetype "%s"' % filename
	aPipe = os.popen(mime_guesser_cmd, 'r')
	if aPipe is None:
		_log.debug("cannot open pipe to [%s]" % mime_guesser_cmd)
	else:
		pipe_output = aPipe.readline()[11:].replace('\n', '').strip()
		ret_code = aPipe.close()
		if ret_code is None:
			_log.debug('[%s]: <%s>' % (mime_guesser_cmd, pipe_output))
			if pipe_output not in ['', worst_case]:
				return pipe_output
		else:
			_log.error('[%s] on %s (%s): failed with exit(%s)' % (mime_guesser_cmd, os.name, sys.platform, ret_code))

	# If we and up here we either have an insufficient systemwide
	# magic number file or we suffer from a deficient operating system
	# alltogether. It can't get much worse if we try ourselves.

	_log.info("OS level mime detection failed, falling back to built-in magic")

	import gmMimeMagic
	mime_type = gmTools.coalesce(gmMimeMagic.filedesc(filename), worst_case)
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
		_log.debug('<%s>: %s' % (mimetype, ext))
		return ext

	_log.error("<%s>: no suitable file extension known to the OS" % mimetype)

	# try to help the OS a bit
	cfg = gmCfg2.gmCfgData()
	ext = cfg.get (
		group = 'extensions',
		option = mimetype,
		source_order = [('user-mime', 'return'), ('system-mime', 'return')]
	)

	if ext is not None:
		_log.debug('<%s>: %s' % (mimetype, ext))
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
def adjust_extension_by_mimetype(filename):
	mimetype = guess_mimetype(filename)
	mime_suffix = guess_ext_by_mimetype(mimetype)
	if mime_suffix is None:
		return filename

	old_name, old_ext = os.path.splitext(filename)
	if old_ext == '':
		new_filename = filename + mime_suffix
	elif old_ext.lower() == mime_suffix.lower():
		return filename

	new_filename = old_name + mime_suffix
	_log.debug('[%s] -> [%s]', filename, new_filename)
	try:
		os.rename(filename, new_filename)
		return new_filename

	except OSError:
		_log.exception('cannot rename, returning original filename')
	return filename

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

	if _system_startfile_cmd == '':
		return False, None

	if _system_startfile_cmd is not None:
		return True, _system_startfile_cmd % filename

	open_cmd_candidates = list(open_cmds)

	for candidate in open_cmd_candidates:
		found, binary = gmShellAPI.detect_external_binary(binary = candidate)
		if not found:
			continue
		_system_startfile_cmd = open_cmds[candidate]
		_log.info('detected local startfile cmd: [%s]', _system_startfile_cmd)
		return True, _system_startfile_cmd % filename

	_system_startfile_cmd = ''
	return False, None

#-----------------------------------------------------------------------------------
def convert_file(filename=None, target_mime=None, target_filename=None, target_extension=None, verbose=False):
	"""Convert file from one format into another.

		target_mime: a mime type
	"""
	assert (target_mime is not None), '<target_mime> must not be None'
	assert (filename is not None), '<filename> must not be None'
	assert (filename != target_filename), '<target_filename> must be different from <filename>'

	source_mime = guess_mimetype(filename = filename)
	if source_mime.lower() == target_mime.lower():
		_log.debug('source file [%s] already target mime type [%s]', filename, target_mime)
		if target_filename is None:
			return filename

		shutil.copyfile(filename, target_filename)
		return target_filename

	converted_ext = guess_ext_by_mimetype(target_mime)
	if converted_ext is None:
		if target_filename is not None:
			tmp, converted_ext = os.path.splitext(target_filename)
	if converted_ext is None:
		converted_ext = target_extension		# can still stay None
	converted_ext = gmTools.coalesce(converted_ext, '').strip().lstrip('.')
	converted_fname = gmTools.get_unique_filename(suffix = converted_ext)
	_log.debug('attempting conversion: [%s] -> [<%s>:%s]', filename, target_mime, gmTools.coalesce(target_filename, converted_fname))
	script_name = 'gm-convert_file'
	paths = gmTools.gmPaths()
	local_script = os.path.join(paths.local_base_dir, '..', 'external-tools', script_name)
	candidates = [ script_name, local_script ]		#, script_name + u'.bat'
	found, binary = gmShellAPI.find_first_binary(binaries = candidates)
	if not found:
		# try anyway
		binary = script_name# + r'.bat'
	_log.debug('<%s> API: SOURCEFILE TARGET_MIMETYPE TARGET_EXTENSION TARGET_FILENAME' % binary)
	cmd_line = [
		binary,
		filename,
		target_mime,
		converted_ext,
		converted_fname
	]
	success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = True)
	if not success:
		_log.error('conversion returned error exit code')
		if not os.path.exists(converted_fname):
			return None
		_log.info('conversion target file found')
		stats = os.stat(converted_fname)
		if stats.st_size == 0:
			return None
		_log.info('conversion target file size > 0')
		achieved_mime = guess_mimetype(filename = converted_fname)
		if achieved_mime != target_mime:
			_log.error('target: [%s], achieved: [%s]', target_mime, achieved_mime)
			return None
		_log.info('conversion target file mime type [%s], as expected, might be usable', achieved_mime)
		# we may actually have something despite a non-0 exit code

	if target_filename is None:
		return converted_fname

	shutil.copyfile(converted_fname, target_filename)
	return target_filename

#-----------------------------------------------------------------------------------
def __run_file_describer(filename=None):
	base_name = 'gm-describe_file'
	paths = gmTools.gmPaths()
	local_script = os.path.join(paths.local_base_dir, '..', 'external-tools', base_name)
	candidates = [base_name, local_script]		#, base_name + '.bat'
	found, binary = gmShellAPI.find_first_binary(binaries = candidates)
	if not found:
		_log.error('cannot find <%s(.bat)>', base_name)
		return (False, _('<%s(.bat)> not found') % base_name)

	cmd_line = [binary, filename]
	_log.debug('describing: %s', cmd_line)
	try:
		proc_result = subprocess.run (
			args = cmd_line,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			#timeout = timeout,
			encoding = 'utf8',
			errors = 'backslashreplace'
		)
	except (subprocess.TimeoutExpired, FileNotFoundError):
		_log.exception('there was a problem running external process')
		return (False, _('problem with <%s>') % binary)

	_log.info('exit code [%s]', proc_result.returncode)
	if proc_result.returncode != 0:
		_log.error('[%s] failed', binary)
		_log.error('STDERR:\n%s', proc_result.stderr)
		_log.error('STDOUT:\n%s', proc_result.stdout)
		return (False, _('problem with <%s>') % binary)
	return (True, proc_result.stdout)

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
		except Exception:
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
	except Exception:
		_log.exception('os.startfile(%s) failed', file_to_display)

	msg = _("Unable to display the file:\n\n"
			" [%s]\n\n"
			"Your system does not seem to have a (working)\n"
			"viewer registered for the file type\n"
			" [%s]"
	) % (file_to_display, mime_type)
	return False, msg

#-----------------------------------------------------------------------------------
def call_editor_on_file(filename=None, block=True):
	"""Try to find an appropriate editor with all tricks and call it.

	block: try to detach from editor or not, None means to use mailcap default.
	"""
	if not os.path.isdir(filename):
		# is the file accessible at all ?
		try:
			open(filename).close()
		except Exception:
			_log.exception('cannot read [%s]', filename)
			msg = _('[%s] is not a readable file') % filename
			return False, msg

	mime_type = guess_mimetype(filename)

	editor_cmd = get_editor_cmd(mime_type, filename)
	if editor_cmd is not None:
		if gmShellAPI.run_command_in_shell(command = editor_cmd, blocking = block):
			return True, ''
	viewer_cmd = get_viewer_cmd(mime_type, filename)
	if viewer_cmd is not None:
		if gmShellAPI.run_command_in_shell(command = viewer_cmd, blocking = block):
			return True, ''
	_log.warning("no editor or viewer found via standard mailcap system")

	if os.name == "posix":
		_log.warning("you should add an editor and/or viewer for this mime type to your mailcap file")

	_log.info("let's see what the OS can do about that")
	# does the file already have a useful extension ?
	(path_name, f_ext) = os.path.splitext(filename)
	if f_ext in ['', '.tmp']:
		# try to guess one
		f_ext = guess_ext_by_mimetype(mime_type)
		if f_ext is None:
			_log.warning("no suitable file extension found, trying anyway")
			file_to_display = filename
			f_ext = '?unknown?'
		else:
			file_to_display = filename + f_ext
			shutil.copyfile(filename, file_to_display)
	else:
		file_to_display = filename

	file_to_display = os.path.normpath(file_to_display)
	_log.debug("file %s <type %s> (ext %s) -> file %s" % (filename, mime_type, f_ext, file_to_display))

	# try to detect any of the UNIX openers (will only find viewers)
	found, startfile_cmd = _get_system_startfile_cmd(filename)
	if found:
		if gmShellAPI.run_command_in_shell(command = startfile_cmd, blocking = block):
			return True, ''

	# last resort: hand over to Python itself
	try:
		os.startfile(file_to_display)
		return True, ''
	except AttributeError:
		_log.exception('os.startfile() does not exist on this platform')
	except Exception:
		_log.exception('os.startfile(%s) failed', file_to_display)

	msg = _("Unable to edit/view the file:\n\n"
			" [%s]\n\n"
			"Your system does not seem to have a (working)\n"
			"editor or viewer registered for the file type\n"
			" [%s]"
	) % (file_to_display, mime_type)
	return False, msg

#=======================================================================================
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N

	# for testing:
	logging.basicConfig(level = logging.DEBUG)

	filename = sys.argv[2]
	_get_system_startfile_cmd(filename)

	#--------------------------------------------------------
	def test_edit():

		mimetypes = [
			'application/x-latex',
			'application/x-tex',
			'text/latex',
			'text/tex',
			'text/plain'
		]

		for mimetype in mimetypes:
			editor_cmd = get_editor_cmd(mimetype, filename)
			if editor_cmd is not None:
				break

		if editor_cmd is None:
			# LaTeX code is text: also consider text *viewers*
			# since pretty much any of them will be an editor as well
			for mimetype in mimetypes:
				editor_cmd = get_viewer_cmd(mimetype, filename)
				if editor_cmd is not None:
					break

		if editor_cmd is None:
			return False

		result = gmShellAPI.run_command_in_shell(command = editor_cmd, blocking = True)

		return result

	#--------------------------------------------------------
	def test_describer():
		status, desc = describe_file(filename)
		print(status)
		print(desc)

	#--------------------------------------------------------
	def test_convert_file():
		print(convert_file (
			filename = filename,
			target_mime = sys.argv[3]
		))

	#--------------------------------------------------------
#	print(_system_startfile_cmd)
#	print(guess_mimetype(filename))
#	print(get_viewer_cmd(guess_mimetype(filename), filename))
#	print(get_editor_cmd(guess_mimetype(filename), filename))
#	print(get_editor_cmd('application/x-latex', filename))
#	print(get_editor_cmd('application/x-tex', filename))
#	print(get_editor_cmd('text/latex', filename))
#	print(get_editor_cmd('text/tex', filename))
#	print(get_editor_cmd('text/plain', filename))
	#print(guess_ext_by_mimetype(mimetype=filename))
#	call_viewer_on_file(aFile = filename, block = True)
	#call_editor_on_file(filename)
	#test_describer()
	#print(test_edit())
	test_convert_file()
