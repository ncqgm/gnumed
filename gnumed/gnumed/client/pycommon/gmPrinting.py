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

# =======================================================================
def print_file_by_shellscript(filename=None, jobtype=None):

	_log.debug('printing "%s": [%s]', jobtype, filename)

	if jobtype not in known_printjob_types:
		print "unregistered print job type <%s>" % jobtype
		_log.warning('print job type "%s" not registered')

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
# =======================================================================
# main
#------------------------------------------------------------------------
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
		return print_file_by_shellscript (filename = sys.argv[2], jobtype = sys.argv[3])
	#--------------------------------------------------------------------

	print test_print_file()

# =======================================================================
