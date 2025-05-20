# =======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/testing/test-psycopg2_datetime-as_gnumed.py,v $
__version__ = "$Revision: 1.3 $"
__author__  = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'
# =======================================================================
import sys, logging
sys.path.insert(0, '../../')

from Gnumed.pycommon import gmLog2, gmI18N
gmI18N.activate_locale()
_log = logging.getLogger('gm.test')

from Gnumed.pycommon import gmPG2

print "testing psycopg2 date/time parsing via GNUmed code"

class login:
	pass

l = login()
l.database = 'gnumed_v9'
l.host = 'publicdb.gnumed.de'
l.port = '5432'
l.user = 'any-doc'
l.password = 'any-doc'

#gmPG2.set_default_client_timezone(timezone = 'Asia/Colombo')
#gmPG2.set_default_client_timezone(timezone = 'Asia/Calcutta')

conn = gmPG2.get_connection()

cmd = """select * from dem.v_staff where db_user = CURRENT_USER"""

try:
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}], verbose = True)
	for row in rows:
		_log.info(row)
	print rows
	print "==> success"
except Exception:
	_log.exception('query failed')
	gmLog2.log_stack_trace('query failed')
	print "==> failure"

# =======================================================================
# $Log: test-psycopg2_datetime-as_gnumed.py,v $
# Revision 1.3  2009-02-18 13:46:02  ncq
# - add example for succeeding time zone
#
# Revision 1.2  2009/02/17 17:47:07  ncq
# - adjust path
#
# Revision 1.1  2009/02/10 18:47:25  ncq
# - more TZ trouble test cases
#
#