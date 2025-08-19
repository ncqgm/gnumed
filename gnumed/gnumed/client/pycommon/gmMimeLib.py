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
import mimetypes
import subprocess
import shutil
import logging
from typing import Callable
try:
	import mailcap as _mailcap
except (ImportError, ModuleNotFoundError):		# Python 3.11 deprecated mailcap, in 3.13 it is gone ...
	import _mailcap__copy as _mailcap			# type: ignore


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmWorkerThread


_log = logging.getLogger('gm.mime')

WORST_CASE_MIMETYPE = 'application/octet-stream'

#=======================================================================================
# mime type handling
#---------------------------------------------------------------------------------------
def is_probably_textfile(filename:str=None) -> bool:
	"""Check whether a file might be a text file by mime type."""
	if guess_mimetype(filename).startswith('text/'):
		return True

	return False

#---------------------------------------------------------------------------------------
def is_probably_image(filename:str=None) -> bool:
	"""Check whether a file might be an image file by mime type."""
	if guess_mimetype(filename).startswith('image/'):
		return True

	return False

#---------------------------------------------------------------------------------------
def is_probably_pdf(filename:str=None) -> bool:
	"""Check whether a file might be a PDF file by mime type."""
	if guess_mimetype(filename) == 'application/pdf':
		return True

	return False

#---------------------------------------------------------------------------------------
def split_multipage_image(filename:str=None) -> list[str]:
	sandbox = gmTools.mk_sandbox_dir()
	cmd_line = [
		'convert',
		'-verbose',
		filename,
		os.path.join(sandbox, '%s.%%d' % gmTools.fname_from_path(filename))
	]
	success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = True)
	if not success:
		return []

	fname_stem = gmTools.fname_stem(filename)
	items = os.listdir(sandbox)
	image_pages = []
	for item in items:
		if not item.startswith(fname_stem):
			continue
		image_pages.append(os.path.join(sandbox, item))
	return sorted(image_pages)

#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
def __guess_mimetype__pylibextractor(filename:str=None) -> str:
	# Python libextractor
	try:
		import extractor
	except ImportError:
		_log.debug('module <extractor> (python wrapper for libextractor) not installed')
		return None

	except OSError as exc:
		# winerror 126, errno 22
		if exc.errno != 22:
			raise
		_log.exception('module <extractor> (python wrapper for libextractor) not installed')
		return None

	xtractor = extractor.Extractor()
	props = xtractor.extract(filename = filename)
	for prop, val in props:
		if prop != 'mimetype':
			continue
		_log.debug('[import extractor]: <%s>' % val)
		if val != WORST_CASE_MIMETYPE:
			return val

	return None

#---------------------------------------------------------------------------------------
def __guess_mimetype__file(filename:str=None) -> str:
	# this only works on POSIX with 'file' installed (which is standard, however)
	# it might work on Cygwin installations
	mime_guesser_cmd = 'file --mime-type --brief "%s"' % filename
	pipe = os.popen(mime_guesser_cmd, 'r')
	if pipe is None:
		_log.debug("cannot open pipe to [%s]" % mime_guesser_cmd)
		return None

	pipe_output = pipe.readline().replace('\n', '').strip()
	ret_code = pipe.close()
	if ret_code is not None:
		_log.error('[%s] on %s (%s): failed with exit(%s)' % (mime_guesser_cmd, os.name, sys.platform, ret_code))
		return None

	_log.debug('[%s]: <%s>' % (mime_guesser_cmd, pipe_output))
	if pipe_output in ['', WORST_CASE_MIMETYPE]:
		return None

	return pipe_output

#---------------------------------------------------------------------------------------
def __guess_mimetype__extract(filename:str=None) -> str:
	mime_guesser_cmd = 'extract -p mimetype "%s"' % filename
	pipe = os.popen(mime_guesser_cmd, 'r')
	if pipe is None:
		_log.debug("cannot open pipe to [%s]" % mime_guesser_cmd)
		return None

	pipe_output = pipe.readline()[11:].replace('\n', '').strip()
	ret_code = pipe.close()
	if ret_code is not None:
		_log.error('[%s] on %s (%s): failed with exit(%s)' % (mime_guesser_cmd, os.name, sys.platform, ret_code))
		return None

	_log.debug('[%s]: <%s>' % (mime_guesser_cmd, pipe_output))
	if pipe_output in ['', WORST_CASE_MIMETYPE]:
		return None

	return pipe_output

#---------------------------------------------------------------------------------------
def guess_mimetype(filename:str=None) -> str:
	"""Guess mime type of arbitrary file.

	Returns:
		Detected mimetype or 'application/octet-stream'.
	"""
	_log.debug('guessing mime type of [%s]', filename)
	mimetype, encoding = mimetypes.guess_type(filename)
	if mimetype not in [WORST_CASE_MIMETYPE, None]:
		_log.debug('"%s" -> <%s> (%s)', filename, mimetype, encoding)
		return mimetype

	mimetype = __guess_mimetype__pylibextractor(filename = filename)
	if mimetype:
		return mimetype

	mimetype = __guess_mimetype__file(filename = filename)
	if mimetype:
		return mimetype

	# 3) use "extract" shell level libextractor wrapper
	mimetype = __guess_mimetype__extract(filename = filename)
	if mimetype:
		return mimetype

	# If we and up here we either have an insufficient systemwide
	# magic number file or we suffer from a deficient operating system
	# alltogether. It can't get much worse if we try ourselves.
	_log.info("OS level mime detection failed, falling back to built-in magic")
	from Gnumed.pycommon import gmMimeMagic
	mimetype = gmTools.coalesce(gmMimeMagic.filedesc(filename), WORST_CASE_MIMETYPE)
	del gmMimeMagic
	_log.debug('"%s" -> <%s>' % (filename, mimetype))
	return mimetype

#-----------------------------------------------------------------------------------
def get_viewer_cmd(aMimeType = None, aFileName = None, aToken = None):
	"""Return command for viewer for this mime type complete with this file"""

	if aFileName is None:
		_log.error("You should specify a file name for the replacement of %s.")
		# last resort: if no file name given replace %s in original with literal '%s'
		# and hope for the best - we certainly don't want the module default "/dev/null"
		aFileName = """%s"""

	mailcaps = _mailcap.getcaps()
	(viewer, junk) = _mailcap.findmatch(mailcaps, aMimeType, key = 'view', filename = '%s' % aFileName)
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

	mailcaps = _mailcap.getcaps()
	(editor, junk) = _mailcap.findmatch(mailcaps, mimetype, key = 'edit', filename = '%s' % filename)

	# FIXME: we should check for "x-token" flags

	_log.debug("<%s> editor: [%s]" % (mimetype, editor))

	return editor

#-----------------------------------------------------------------------------------
def guess_ext_by_mimetype(mimetype=''):
	"""Return file extension based on what the OS thinks a file of this mimetype should end in."""

	# ask system first
	ext = mimetypes.guess_extension(mimetype)
	if ext is not None:
		_log.debug('<%s>: %s', mimetype, ext)
		return ext

	_log.error("<%s>: no suitable file extension known to the OS" % mimetype)
	# try to help the OS a bit
	cfg = gmCfgINI.gmCfgData()
	ext = cfg.get (
		group = 'extensions',
		option = mimetype,
		source_order = [('user-mime', 'return'), ('system-mime', 'return')]
	)
	if ext and ext.startswith('.'):
		ext = ext[1:]
	if ext:
		_log.debug('<%s>: %s', mimetype, ext)
		return ext

	_log.error("<%s>: no suitable file extension found in config files", mimetype)
	return ext

#-----------------------------------------------------------------------------------
def guess_ext_for_file(aFile:str=None) -> str:
	"""Guesses an approprate file name extension based on mimetype.

	Args:
		aFile: the name of an existing file
	"""
	if aFile is None:
		return None

	(path_name, f_ext) = os.path.splitext(aFile)
	if f_ext:
		return f_ext

	mime_type = guess_mimetype(aFile)
	f_ext = guess_ext_by_mimetype(mime_type)
	if f_ext is None:
		_log.error('unable to guess file name extension for mime type [%s]' % mime_type)
		return None

	return f_ext

#-----------------------------------------------------------------------------------
def adjust_extension_by_mimetype(filename:str) -> str:
	"""Rename file to have proper extension as per its mimetype.

	Returns:
		Original filename if no suffix found or empty suffix found or existing suffix already correct (case insensitive).

		New filename if renamed. New filename will have any old suffix removed and the new suffix appende.
	"""
	mimetype = guess_mimetype(filename)
	mime_suffix = guess_ext_by_mimetype(mimetype)
	_log.debug('%s -> %s', mimetype, mime_suffix)
	if mime_suffix is None:
		return filename

	if mime_suffix.strip() == '':
		return filename

	mime_suffix = mime_suffix.lstrip('.')
	base_name_with_path, old_ext = os.path.splitext(filename)
	old_ext = old_ext.lstrip('.')
	if old_ext.casefold() == mime_suffix.casefold():
		return filename

	new_filename = '%s.%s' % (base_name_with_path, mime_suffix)
	_log.debug('[%s] -> [%s]', filename, new_filename)
	renamed = gmTools.rename_file (
		filename = filename,
		new_filename = new_filename,
		overwrite = True,
		allow_symlink = True
	)
	if renamed:
		return new_filename

	return None

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

def _get_system_startfile_cmd(filename:str):

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
def join_files_as_pdf(files:list[str]=None, pdf_name:str=None) -> str:
	"""Convert files to PDF and joins them into one final PDF.

	Returns:
		Name of final PDF or None
	"""
	assert (files is not None), '<files> must not be None'

	if len(files) == 0:
		return None

	sandbox = gmTools.mk_sandbox_dir()
	pdf_pages = []
	page_idx = 1
	for fname in files:
		pdf = convert_file (
			filename = fname,
			target_mime = 'application/pdf',
			target_filename = gmTools.get_unique_filename(prefix = '%s-' % page_idx, suffix = '.pdf', tmp_dir = sandbox),
			target_extension = '.pdf',
			verbose = True
		)
		if pdf is None:
			return None

		pdf_pages.append(pdf)
		page_idx += 1

	if pdf_name is None:
		pdf_name = gmTools.get_unique_filename(suffix = '.pdf')
	cmd_line = ['pdfunite']
	cmd_line.extend(pdf_pages)
	cmd_line.append(pdf_name)
	success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = True)
	if not success:
		_log.debug('cannot join files into one PDF')
		return None

	return pdf_name

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
# mimetype conversion helpers
#-----------------------------------------------------------------------------------
__LaTeX_version_checked = False
__pdflatex_executable = None

def convert_latex_to_pdf(filename:str=None, verbose:bool=False, is_sandboxed:bool=False, max_pages:int=25) -> str:
	"""Compile LaTeX code to PDF using pdflatex.

	Args:
		is_sandboxed: whether or not to create a sandbox for compiling

	Returns:
		Name of resulting PDF, or None on failure.
	"""
	global __LaTeX_version_checked
	global __pdflatex_executable
	if not __LaTeX_version_checked:
		__LaTeX_version_checked = True
		found, __pdflatex_executable = gmShellAPI.detect_external_binary(binary = 'pdflatex')
		if not found:
			_log.error('pdflatex not found')
			return None

		cmd_line = [__pdflatex_executable, '-version']
		success, ret_code, stdout = gmShellAPI.run_process(cmd_line = cmd_line, encoding = 'utf8', verbose = True)
		if not success:
			_log.error('[%s] failed, LaTeX not usable', cmd_line)
			return None

	if is_sandboxed:
		sandbox_dir = os.path.split(filename)[0]
	else:
		sandbox_dir = gmTools.mk_sandbox_dir(prefix = gmTools.fname_stem(filename) + '_')
		shutil.copy(filename, sandbox_dir)
		filename = os.path.join(sandbox_dir, os.path.split(filename)[1])
	_log.debug('LaTeX sandbox directory: [%s]', sandbox_dir)
	cmd_final = [
		__pdflatex_executable,
		'-recorder',
		'-interaction=nonstopmode',
		"-output-directory=%s" % sandbox_dir
	]
	cmd_draft = cmd_final + ['-draftmode']
	# LaTeX can need up to three runs to get cross references et al right
	for cmd2run in [cmd_draft, cmd_draft, cmd_final]:
		success, ret_code, stdout = gmShellAPI.run_process (
			cmd_line = cmd2run + [filename],
			acceptable_return_codes = [0],
			encoding = 'utf8',
			verbose = True	#_cfg.get(option = 'debug')
		)
		if not success:
			_log.error('problem running pdflatex, cannot generate form output, trying diagnostics')
			found, binary = gmShellAPI.find_first_binary(binaries = ['lacheck', 'miktex-lacheck.exe'])
			if not found:
				_log.debug('lacheck not found')
			else:
				cmd_line = [binary, filename]
				success, ret_code, stdout = gmShellAPI.run_process(cmd_line = cmd_line, encoding = 'utf8', verbose = True)
			found, binary = gmShellAPI.find_first_binary(binaries = ['chktex', 'ChkTeX.exe'])
			if not found:
				_log.debug('chcktex not found')
			else:
				cmd_line = [binary, '--verbosity=2', '--headererr', filename]
				success, ret_code, stdout = gmShellAPI.run_process(cmd_line = cmd_line, encoding = 'utf8', verbose = True)
			return None

	return '%s.pdf' % os.path.splitext(filename)[0]

#-----------------------------------------------------------------------------------
def __convert_odt_to_pdf(filename:str=None, verbose:bool=False, max_pages:int=25):
	cmd_line = [
		'lowriter',
		'--convert-to', 'pdf',
		'--outdir', os.path.split(filename)[0],
		filename
	]
	success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = True)
	if not success:
		return None

	return gmTools.fname_stem_with_path(filename) + '.pdf'

#-----------------------------------------------------------------------------------
def __convert_pdf_to_image(filename:str=None, verbose:bool=False, max_pages:int=25) -> str:
	cmd_line = ['convert']
	if verbose:
		cmd_line.append('-verbose')
	cmd_line.append('-density')
	cmd_line.append('150x150')
	cmd_line.append('%s[0-%s]' % (filename, max_pages-1))
	sandbox = gmTools.mk_sandbox_dir()
	cmd_line.append(os.path.join(sandbox, '%s.%%d.tiff' % gmTools.fname_from_path(filename)))
	success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = True)
	if not success:
		return None

	pdf_stem = gmTools.fname_stem(filename)
	items = os.listdir(sandbox)
	image_pages = []
	for item in items:
		if not item.endswith('.tiff'):
			continue
		if not item.startswith(pdf_stem):
			continue
		image_pages.append(os.path.join(sandbox, item))
	cmd_line = ['convert']
	if verbose:
		cmd_line.append('-verbose')
	cmd_line.extend(sorted(image_pages))
	cmd_line.append('-adjoin')
	tiff_name = os.path.join(sandbox, '%s.tiff' % filename)
	cmd_line.append(tiff_name)
	success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = True)
	if not success:
		return None

	return tiff_name

#-----------------------------------------------------------------------------------
def __convert_pdf_to_text(filename:str=None, verbose:bool=False, max_pages:int=25) -> str:
	txt_fname = '%s.txt' % filename
	cmd_line = [
		'pdftotext',
		'-f', '1',
		'-l', '1',
		'-layout',
		filename,
		txt_fname
	]
	success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = True)
	if not success:
		return None

	return txt_fname

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
__CONVERSION_DELEGATES:dict[str, dict[str, Callable]] = {
	'application/vnd.oasis.opendocument.text': {
		'application/pdf': __convert_odt_to_pdf
	},
	'text/latex': {
		'application/pdf': convert_latex_to_pdf
	},
	'application/pdf': {
		'image/any': __convert_pdf_to_image,
		'image/*': __convert_pdf_to_image,
		'image/': __convert_pdf_to_image,
		'image': __convert_pdf_to_image,
		'text/plain': __convert_pdf_to_text,
		'text/any': __convert_pdf_to_text,
		'text/*': __convert_pdf_to_text,
		'text/': __convert_pdf_to_text,
		'text': __convert_pdf_to_text
	}
}

__CONVERSION_DELEGATES['text/tex'] = __CONVERSION_DELEGATES['text/latex']
__CONVERSION_DELEGATES['text/x-tex'] = __CONVERSION_DELEGATES['text/latex']
__CONVERSION_DELEGATES['application/x-latex'] = __CONVERSION_DELEGATES['text/latex']
__CONVERSION_DELEGATES['application/x-tex'] = __CONVERSION_DELEGATES['text/latex']

#-----------------------------------------------------------------------------------
def convert_file_to_image(filename:str=None, verbose:bool=False, max_pages:int=10) -> list[str]:
	return convert_file(filename = filename, target_mime = 'image/*', verbose = verbose, max_pages = max_pages)

#-----------------------------------------------------------------------------------
def convert_file_to_text(filename:str=None, verbose:bool=False) -> str:
	return convert_file(filename = filename, target_mime = 'text/*', verbose = verbose)

#-----------------------------------------------------------------------------------
def convert_file(filename=None, target_mime=None, target_filename=None, target_extension=None, verbose=False, max_pages:int=25):
	"""Convert file from one format into another.

	Args:
		target_mime: mime type to convert file into
	"""
	assert (target_mime is not None), '<target_mime> must not be None'
	assert (filename is not None), '<filename> must not be None'
	assert (filename != target_filename), '<target_filename> must be different from <filename>'

	source_mime = guess_mimetype(filename = filename)
	target_mime_parts = target_mime.rsplit('/', 1)
	if (len(target_mime_parts) == 1) or (target_mime_parts[1].strip().casefold() in ['', '*', 'any']):
		_log.debug('generic target mime type')
		target_mime = target_mime_parts[0] + '/'

	if source_mime.casefold().startswith(target_mime.casefold()):
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

	# try user-local conversion script
	script_name = 'gm-convert_file'
	binary = os.path.join(gmTools.gmPaths().home_dir, 'bin', script_name)
	_log.debug('trying user-local script: %s', binary)
	_log.debug('<%s> API: SOURCEFILE TARGET_MIMETYPE TARGET_EXTENSION TARGET_FILENAME', script_name)
	found, binary = gmShellAPI.detect_external_binary(binary = binary)
	if found:
		cmd_line = [
			binary,
			filename,
			target_mime,
			converted_ext,
			converted_fname
		]
		success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = True)
		if success:
			if target_filename is None:
				return converted_fname

			shutil.copyfile(converted_fname, target_filename)
			return target_filename

	# try built-in conversions
	_log.debug('trying built-in conversion functions')
	try:
		conversion_func = __CONVERSION_DELEGATES[source_mime][target_mime]
	except KeyError:
		conversion_func = None
	if conversion_func is not None:
		converted_fname = conversion_func(filename = filename, verbose = verbose, max_pages = max_pages)
		if converted_fname is not None:
			if target_filename is None:
				return converted_fname

			shutil.copyfile(converted_fname, target_filename)
			return target_filename

	# try system-wide conversion script
	paths = gmTools.gmPaths()
	local_script = os.path.join(paths.local_base_dir, '..', 'external-tools', script_name)
	candidates = [ script_name, local_script ]		#, script_name + u'.bat'
	_log.debug('trying system-wide scripts: %s', candidates)
	found, binary = gmShellAPI.find_first_binary(binaries = candidates)
	if not found:	# try anyway
		_log.debug('trying anyway as last-ditch resort')
		binary = script_name# + r'.bat'
	cmd_line = [
		binary,
		filename,
		target_mime,
		converted_ext,
		converted_fname
	]
	success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = True)
	if success:
		if target_filename is None:
			return converted_fname

		shutil.copyfile(converted_fname, target_filename)
		return target_filename

	# seems to have failed but check for target file anyway
	_log.error('conversion script returned error exit code, checking target file anyway')
	if not os.path.exists(converted_fname):
		return None

	_log.info('conversion target file found')
	stats = os.stat(converted_fname)
	if stats.st_size == 0:
		return None

	_log.info('conversion target file size > 0')
	achieved_mime = guess_mimetype(filename = converted_fname)
	if not achieved_mime.casefold().startswith(target_mime.casefold()):
		_log.error('target: [%s], achieved: [%s]', target_mime, achieved_mime)
		return None

	# we may actually have something despite a non-0 exit code
	_log.info('conversion target file mime type [%s], as expected, might be usable', achieved_mime)
	if target_filename is None:
		return converted_fname

	shutil.copyfile(converted_fname, target_filename)
	return target_filename

#-----------------------------------------------------------------------------------
def __run_file_describer(filename=None, cookie=None):
	base_name = 'gm-describe_file'
	paths = gmTools.gmPaths()
	local_script = os.path.join(paths.local_base_dir, '..', 'external-tools', base_name)
	candidates = [base_name, local_script]		#, base_name + '.bat'
	found, binary = gmShellAPI.find_first_binary(binaries = candidates)
	if not found:
		_log.error('cannot find <%s(.bat)>', base_name)
		return (False, _('<%s(.bat)> not found') % base_name, cookie)

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
		return (False, _('problem with <%s>') % binary, cookie)

	_log.info('exit code [%s]', proc_result.returncode)
	if proc_result.returncode != 0:
		_log.error('[%s] failed', binary)
		_log.error('STDERR:\n%s', proc_result.stderr)
		_log.error('STDOUT:\n%s', proc_result.stdout)
		return (False, _('problem with <%s>') % binary, cookie)

	return (True, proc_result.stdout, cookie)

#-----------------------------------------------------------------------------------
def describe_file(filename, callback=None, cookie=None):
	if callback is None:
		return __run_file_describer(filename)

	payload_kwargs = {'filename': filename, 'cookie': cookie}
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
			filename = sys.argv[2],
			target_mime = sys.argv[3]
		))

	#--------------------------------------------------------
	def test_join_files_as_pdf():
		print(join_files_as_pdf(files = gmTools.dir_list_files(sys.argv[2])))

	#--------------------------------------------------------
	def test_check_is_textfile():
		for fname in gmTools.dir_list_files(sys.argv[2]):
			print(fname)
			print(' =>', is_probably_textfile(filename = fname))

	#--------------------------------------------------------
	def test__convert_pdf_to_img():
		img_name = __convert_pdf_to_image(sys.argv[2], verbose = True, max_pages = 3)
		print(img_name)
		#print(split_multipage_image(img_name))

	#--------------------------------------------------------
	def test__split_multipage():
		print(split_multipage_image(sys.argv[2]))

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
	#print(get_editor_cmd('text/x-tex', filename))
	#print(guess_ext_by_mimetype(mimetype=filename))
	#call_viewer_on_file(aFile = filename, block = True)
	#call_editor_on_file(filename)
	#test_describer()
	#print(test_edit())
	#test_convert_file()
	test__convert_pdf_to_img()
	#test_join_files_as_pdf()
	#test_check_is_textfile()
	#test__split_multipage()
