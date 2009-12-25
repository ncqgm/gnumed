"""GNUmed printing."""
# =======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmPrinting.py,v $
# $Id: gmPrinting.py,v 1.1 2009-12-25 19:04:50 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (details at http://www.gnu.org)'

# =======================================================================
import logging, sys


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmLog2
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()


from Gnumed.pycommon import gmShellAPI


_log = logging.getLogger('gm.printing')
_log.info(__version__)
# =======================================================================
def print_file_by_shellscript(filename=None, jobtype=None):

	# 1) find gm_print_doc.sh
	found, external_cmd = gmShellAPI.detect_external_binary(u'gm_print_doc.sh')
	if not found:
		found, external_cmd = gmShellAPI.detect_external_binary(u'gm_print_doc.bat')
	if not found:
		_log.error('neither of gm_print_doc.sh or gm_print_doc.bat found')
		return False

	# 2) call it
	cmd = u'%s %s %s' % (external_cmd, filename, jobtype)
	success = gmShellAPI.run_command_in_shell (
		command = cmd,
		blocking = True
	)

	if success:
		return True

	_log.error('print command failed: [%s]', cmd)
	return False
# =======================================================================
# main
#------------------------------------------------------------------------
if __name__ == '__main__':

	def test_print_file():
		return print_file_by_shellscript (filename = sys.argv[2], jobtype = sys.argv[3])
	#--------------------------------------------------------------------
	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		print test_print_file()

# =======================================================================
# $Log: gmPrinting.py,v $
# Revision 1.1  2009-12-25 19:04:50  ncq
# - new code
#
#