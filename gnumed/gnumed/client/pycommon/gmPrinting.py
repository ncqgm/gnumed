"""GNUmed printing."""
# =======================================================================
__version__ = "$Revision: 1.4 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

# =======================================================================
import logging
import sys
import os
import subprocess
import codecs
import time


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmTools


_log = logging.getLogger('gm.printing')
_log.info(__version__)


known_printjob_types = [
	u'medication_list',
	u'generic_document'
]

external_print_APIs = [
	u'gm-print_doc',
	u'os_startfile',		# win, mostly
	u'gsprint',				# win
	u'acrobat_reader',		# win
	u'gktlp',				# Linux
	u'Internet_Explorer',	# win
	u'Mac_Preview'			# MacOSX
]

#=======================================================================
# internal print API
#-----------------------------------------------------------------------
def print_file(filename=None, jobtype=None, print_api=None):

	_log.debug('printing "%s": [%s]', jobtype, filename)

	if jobtype not in known_printjob_types:
		print "unregistered print job type <%s>" % jobtype
		_log.warning('print job type "%s" not registered', jobtype)

	if print_api not in external_print_APIs:
		_log.warning('print API "%s" unknown, trying all', print_api)

	if print_api == u'os_startfile':
		return _print_file_by_os_startfile(filename = filename)
	elif print_api == u'gm-print_doc':
		return _print_file_by_shellscript(filename = filename, jobtype = jobtype)
	elif print_api == u'gsprint':
		return _print_file_by_gsprint_exe(filename = filename)
	elif print_api == u'acrobat_reader':
		return _print_file_by_acroread_exe(filename = filename)
	elif print_api == u'gtklp':
		return _print_file_by_gtklp(filename = filename)
	elif print_api == u'Internet_Explorer':
		return _print_file_by_IE(filename = filename)
	elif print_api == u'Mac_Preview':
		return _print_file_by_mac_preview(filename = filename)

	# else try all
	if (sys.platform == 'darwin') or (os.name == 'mac'):
		if _print_file_by_mac_preview(filename = filename):
			return True
	elif os.name == 'posix':
		if _print_file_by_gtklp(filename = filename):
			return True
	elif os.name == 'nt':
		if _print_file_by_gsprint_exe(filename = filename):
			return True
		if _print_file_by_acroread_exe(filename = filename):
			return True
		if _print_file_by_os_startfile(filename = filename):
			return True
		if _print_file_by_IE(filename = filename):
			return True

	if _print_file_by_shellscript(filename = filename, jobtype = jobtype):
		return True

	return False
#=======================================================================
# external print APIs
#-----------------------------------------------------------------------
def _print_file_by_mac_preview(filename=None):

	if sys.platform != 'darwin':
#	if os.name != 'mac':
		_log.debug('MacOSX <open> only available under MacOSX/Darwin')
		return False

	cmd_line = [
		r'open',				# "open" must be in the PATH
		r'-a Preview',			# action = Preview
		filename
	]
	_log.debug('printing with %s' % cmd_line)
	try:
		mac_preview = subprocess.Popen(cmd_line, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	except OSError:
		_log.debug('cannot run <open -a Preview>')
		return False
	#except ValueError:		# invalid arguments == programming error
	stdout, stderr = mac_preview.communicate()
	if mac_preview.returncode != 0:
		_log.error('<open -a Preview> returned [%s], failed to print', mac_preview.returncode)
		return False

	return True
#-----------------------------------------------------------------------
def _print_file_by_IE(filename=None):

	if os.name != 'nt':
		_log.debug('Internet Explorer only available under Windows')
		return False

	try:
		from win32com import client as dde_client
	except ImportError:
		_log.exception('<win32com> Python module not available for use in printing')
		return False

	i_explorer = dde_client.Dispatch("InternetExplorer.Application")
	i_explorer.Navigate(os.path.normpath(filename))
	if i_explorer.Busy:
		time.sleep(1)
	i_explorer.Document.printAll()
	i_explorer.Quit()

	return True
#-----------------------------------------------------------------------
def _print_file_by_gtklp(filename=None):

	if sys.platform != 'linux2':
#	if os.name != 'posix':
		_log.debug('<gtklp> only available under Linux')
		return False

	cmd_line = [
		r'gtklp',				# "gtklp" must be in the PATH
		r'-i',					# ignore STDIN garbage
		r'-# 1',				# 1 copy
		filename
	]
	_log.debug('printing with %s' % cmd_line)
	try:
		gtklp = subprocess.Popen(cmd_line, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	except OSError:
		_log.debug('cannot run <gtklp>')
		return False
	#except ValueError:		# invalid arguments == programming error
	stdout, stderr = gtklp.communicate()
	if gtklp.returncode != 0:
		_log.error('<gtklp> returned [%s], failed to print', gtklp.returncode)
		return False

	return True
#-----------------------------------------------------------------------
def _print_file_by_gsprint_exe(filename=None):
	"""Use gsprint.exe from Ghostscript tools. Windows only.

	- docs: http://pages.cs.wisc.edu/~ghost/gsview/gsprint.htm
	- download: http://www.cs.wisc.edu/~ghost/
	"""
	if os.name != 'nt':
		_log.debug('<gsprint.exe> only available under Windows')
		return False

	conf_filename = gmTools.get_unique_filename(prefix = 'gm2gsprint-', suffix = '.cfg')
	conf_file = codecs.open(conf_filename, 'wb', 'utf8')
	conf_file.write('-color\n')
	conf_file.write('-query\n')				# printer setup dialog
	conf_file.write('-all\n')				# all pages
	conf_file.write('-copies 1\n')
	conf_file.write('%s\n' % os.path.normpath(filename))
	conf_file.close()

	# "gsprint.exe" must be in the PATH
	cmd_line = [ r'gsprint.exe', r'-config "%s"' % conf_filename ]
	_log.debug('printing with %s' % cmd_line)
	try:
		gsprint = subprocess.Popen(cmd_line, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	except OSError:
		_log.debug('cannot run <gsprint.exe>')
		return False
	#except ValueError:		# invalid arguments == programming error
	stdout, stderr = gsprint.communicate()
	if gsprint.returncode != 0:
		_log.error('<gsprint.exe> returned [%s], failed to print', gsprint.returncode)
		return False

	return True
#-----------------------------------------------------------------------
def _print_file_by_acroread_exe(filename):
	"""Use Adobe Acrobat Reader. Windows only.

	- docs: http://www.robvanderwoude.com/printfiles.php#PrintPDF
	"""
	if os.name != 'nt':
		_log.debug('Acrobat Reader only used under Windows')
		return False

	cmd_line = [
		r'AcroRd32.exe',			# "AcroRd32.exe" must be in the PATH
		r'/s',						# no splash
		r'/o',						# no open-file dialog
		r'/h',						# minimized
		r'/p',						# go straight to printing dialog
		os.path.normpath(filename)
	]
	_log.debug('printing with %s' % cmd_line)
	try:
		acroread = subprocess.Popen(cmd_line, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	except OSError:
		_log.debug('cannot run <AcroRd32.exe>')
		cmd_line[0] = r'acroread.exe'
		_log.debug('printing with %s' % cmd_line)
		try:
			acroread = subprocess.Popen(cmd_line, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		except OSError:
			_log.debug('cannot run <acroread.exe>')
			return False

	stdout, stderr = acroread.communicate()
	if acroread.returncode != 0:
		_log.error('Acrobat Reader returned [%s], failed to print', acroread.returncode)
		return False

	return True
#-----------------------------------------------------------------------
def _print_file_by_os_startfile(filename=None):

	_log.debug('printing [%s]', filename)

	try:
		os.startfile(filename, 'print')
	except AttributeError:
		_log.exception('platform does not support "os.startfile()", cannot print')
		return False

	return True
#-----------------------------------------------------------------------
def _print_file_by_shellscript(filename=None, jobtype=None):

	paths = gmTools.gmPaths()
	local_script = os.path.join(paths.local_base_dir, '..', 'external-tools', 'gm-print_doc')

	candidates = [u'gm-print_doc', u'gm-print_doc.bat', local_script, u'gm-print_doc.bat']
	args = u' %s %s' % (jobtype, filename)

	success = gmShellAPI.run_first_available_in_shell (
		binaries = candidates,
		args = args,
		blocking = True,
		run_last_one_anyway = True
	)

	if success:
		return True

	_log.error('print command failed')
	return False
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


	def test_print_file():
		return print_file(filename = sys.argv[2], jobtype = sys.argv[3])
	#--------------------------------------------------------------------

	print test_print_file()

# =======================================================================
