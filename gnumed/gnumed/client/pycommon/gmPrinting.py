__doc__ = """GNUmed printing."""

__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'
# =======================================================================
import logging
import sys
import os
import io
import time


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmLog2


_log = logging.getLogger('gm.printing')


known_printjob_types = [
	'medication_list',
	'generic_document'
]

external_print_APIs = [
	'gm-print_doc',
	'os_startfile',			# win, mostly
	'gsprint',				# win
	'acrobat_reader',		# win
	'gtklp',				# Linux
	'Internet_Explorer',	# win
	'Mac_Preview'			# MacOSX
]

#=======================================================================
# internal print API
#-----------------------------------------------------------------------
def print_files(filenames=None, jobtype=None, print_api=None, verbose=False):

	_log.debug('printing "%s": %s', jobtype, filenames)

	for fname in filenames:
		try:
			open(fname, 'r').close()
		except Exception:
			_log.exception('cannot open [%s], aborting', fname)
			return False

	if jobtype not in known_printjob_types:
		print("unregistered print job type <%s>" % jobtype)
		_log.warning('print job type "%s" not registered', jobtype)

	if print_api not in external_print_APIs:
		_log.warning('print API "%s" unknown, trying all', print_api)

	if print_api == 'os_startfile':
		return _print_files_by_os_startfile(filenames = filenames)
	if print_api == 'gm-print_doc':
		return _print_files_by_shellscript(filenames = filenames, jobtype = jobtype, verbose = verbose)
	if print_api == 'gsprint':
		return _print_files_by_gsprint_exe(filenames = filenames, verbose = verbose)
	if print_api == 'acrobat_reader':
		return _print_files_by_acroread_exe(filenames = filenames, verbose = verbose)
	if print_api == 'gtklp':
		return _print_files_by_gtklp(filenames = filenames, verbose = verbose)
	if print_api == 'Internet_Explorer':
		return _print_files_by_IE(filenames = filenames)
	if print_api == 'Mac_Preview':
		return _print_files_by_mac_preview(filenames = filenames, verbose = verbose)

	# else try all
	if (sys.platform == 'darwin') or (os.name == 'mac'):
		if _print_files_by_mac_preview(filenames = filenames, verbose = verbose):
			return True
	elif os.name == 'posix':
		if _print_files_by_gtklp(filenames = filenames, verbose = verbose):
			return True
	elif os.name == 'nt':
		if _print_files_by_shellscript(filenames = filenames, jobtype = jobtype, verbose = verbose):
			return True
		if _print_files_by_gsprint_exe(filenames = filenames, verbose = verbose):
			return True
		if _print_files_by_acroread_exe(filenames = filenames, verbose = verbose):
			return True
		if _print_files_by_os_startfile(filenames = filenames):
			return True
		if _print_files_by_IE(filenames = filenames):
			return True
		return False

	if _print_files_by_shellscript(filenames = filenames, jobtype = jobtype, verbose = verbose):
		return True

	return False

#=======================================================================
# external print APIs
#-----------------------------------------------------------------------
def _print_files_by_mac_preview(filenames=None, verbose=False):

#	if os.name != 'mac':				# does not work
	if sys.platform != 'darwin':
		_log.debug('MacOSX <open> only available under MacOSX/Darwin')
		return False
	for filename in filenames:
		cmd_line = [
			'open',				# "open" must be in the PATH
			'-a Preview',		# action = Preview
			filename
		]
		success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = verbose)
		if not success:
			return False
	return True

#-----------------------------------------------------------------------
def _print_files_by_IE(filenames=None):

	if os.name != 'nt':
		_log.debug('Internet Explorer only available under Windows')
		return False
	try:
		from win32com import client as dde_client
	except ImportError:
		_log.exception('<win32com> Python module not available for use in printing')
		return False
	try:
		i_explorer = dde_client.Dispatch("InternetExplorer.Application")
		for filename in filenames:
			if i_explorer.Busy:
				time.sleep(1)
			i_explorer.Navigate(os.path.normpath(filename))
			if i_explorer.Busy:
				time.sleep(1)
			i_explorer.Document.printAll()
		i_explorer.Quit()
	except Exception:
		_log.exception('error calling IE via DDE')
		return False

	return True

#-----------------------------------------------------------------------
def _print_files_by_gtklp(filenames=None, verbose=False):

#	if os.name != 'posix':
	if sys.platform != 'linux':
		_log.debug('<gtklp> only available under Linux')
		return False
	cmd_line = ['gtklp', '-i', '-# 1']
	cmd_line.extend(filenames)
	success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = verbose)
	if not success:
		return False
	return True

#-----------------------------------------------------------------------
def _print_files_by_gsprint_exe(filenames=None, verbose=False):
	"""Use gsprint.exe from Ghostscript tools. Windows only.

	- docs: http://pages.cs.wisc.edu/~ghost/gsview/gsprint.htm
	- download: http://www.cs.wisc.edu/~ghost/
	"""
	if os.name != 'nt':
		_log.debug('<gsprint.exe> only available under Windows')
		return False
	conf_filename = gmTools.get_unique_filename (
		prefix = 'gm2gsprint-',
		suffix = '.cfg'
	).encode(sys.getfilesystemencoding())
	for filename in filenames:
		conf_file = io.open(conf_filename, mode = 'wt', encoding = 'utf8')
		conf_file.write('-color\n')
		conf_file.write('-query\n')			# printer setup dialog
		conf_file.write('-all\n')			# all pages
		conf_file.write('-copies 1\n')
		conf_file.write('%s\n' % os.path.normpath(filename))
		conf_file.close()
		cmd_line = ['gsprint.exe', '-config', conf_filename]		# "gsprint.exe" must be in the PATH
		success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = verbose)
		if not success:
			return False
	return True

#-----------------------------------------------------------------------
def _print_files_by_acroread_exe(filenames, verbose=False):
	"""Use Adobe Acrobat Reader. Windows only.

	- docs: http://www.robvanderwoude.com/printfiles.php#PrintPDF
	"""
	if os.name != 'nt':
		_log.debug('Acrobat Reader only used under Windows')
		return False
	for filename in filenames:
		cmd_line = [
			'AcroRd32.exe',					# "AcroRd32.exe" must be in the PATH
			'/s',							# no splash
			'/o',							# no open-file dialog
			'/h',							# minimized
			'/p',							# go straight to printing dialog
			os.path.normpath(filename)
		]
		success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = verbose)
		if not success:
			# retry with "acroread.exe"
			cmd_line[0] = r'acroread.exe'	# "acroread.exe" must be in the PATH
			success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = verbose)
			if not success:
				return False
	return True

#-----------------------------------------------------------------------
def _print_files_by_os_startfile(filenames=None):
	try:
		os.startfile
	except AttributeError:
		_log.error('platform does not support "os.startfile()"')
		return False
	for filename in filenames:
		fname = os.path.normcase(os.path.normpath(filename))
		_log.debug('%s -> %s', filename, fname)
		try:
			try:
				os.startfile(fname, 'print')
			except WindowsError as e:
				_log.exception('no <print> action defined for this type of file')
				if e.winerror == 1155:	# try (default) <view> action
					os.startfile(fname)
		except Exception:
			_log.exception('os.startfile() failed')
			gmLog2.log_stack_trace()
			return False
	return True

#-----------------------------------------------------------------------
def _print_files_by_shellscript(filenames=None, jobtype=None, verbose=False):

	paths = gmTools.gmPaths()
	local_script = os.path.join(paths.local_base_dir, '..', 'external-tools', 'gm-print_doc')
	candidates = ['gm-print_doc', local_script, 'gm-print_doc.bat']
	found, binary = gmShellAPI.find_first_binary(binaries = candidates)
	if not found:
		binary = r'gm-print_doc.bat'
	cmd_line = [binary,	jobtype]
	cmd_line.extend(filenames)
	success, returncode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, verbose = verbose)
	if not success:
		return False
	return True

#=======================================================================
# main
#-----------------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	#--------------------------------------------------------------------
	def test_print_files():
		return print_files(filenames = [sys.argv[2]], jobtype = sys.argv[3])
	#--------------------------------------------------------------------
	def test_print_files_by_shellscript():
		print_files(filenames = [sys.argv[2], sys.argv[2]], jobtype = 'generic_document', print_api = 'gm-print_doc')
	#--------------------------------------------------------------------
	def test_print_files_by_gtklp():
		print_files(filenames = [sys.argv[2], sys.argv[2]], jobtype = 'generic_document', print_api = 'gtklp')
	#--------------------------------------------------------------------
	def test_print_files_by_mac_preview():
		print("testing printing via Mac Preview")
		_print_files_by_mac_preview(filenames = [sys.argv[0]])
	#--------------------------------------------------------------------
	print(test_print_files())
	#test_print_files_by_gtklp()
	#test_print_files_by_mac_preview()
