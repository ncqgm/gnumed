"""GNUmed printing."""
# =======================================================================
__version__ = "$Revision: 1.4 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (details at http://www.gnu.org)'

# =======================================================================
import logging, sys, os


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
	u'os_startfile',
	u'gm-print_doc'
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
		print "unknown print API <%s>" % print_api
		_log.warning('print API "%s" unknown, trying all', print_api)

	if print_api == u'os_startfile':
		return __print_file_by_os_startfile(filename = filename)

	if print_api == u'gm-print_doc':
		return __print_file_by_shellscript(filename = filename, jobtype = jobtype)

	if __print_file_by_os_startfile(filename = filename):
		return True

	if __print_file_by_shellscript(filename = filename, jobtype = jobtype):
		return True

	return False
#=======================================================================
# external print APIs
#-----------------------------------------------------------------------
def __print_file_by_os_startfile(filename=None):

	_log.debug('printing [%s]', filename)

	try:
		os.startfile(filename, 'print')
	except AttributeError:
		_log.exception('platform does not support "os.startfile()", cannot print')
		return False

	return True
#-----------------------------------------------------------------------
def __print_file_by_shellscript(filename=None, jobtype=None):

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
