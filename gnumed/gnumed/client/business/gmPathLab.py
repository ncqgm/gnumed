"""GnuMed vaccination related business objects.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmPathLab.py,v $
# $Id: gmPathLab.py,v 1.3 2004-04-12 22:59:38 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import types

from Gnumed.pycommon import gmLog, gmPG
from Gnumed.business import gmClinItem
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cLabResult(gmClinItem.cClinItem):
	"""Represents one lab result."""

	_cmd_fetch_payload = """
		select * from v_results4lab_req
		where pk_result=%s"""

	_cmds_store_payload = [
		"""select 1"""
#		"""select 1 from vaccination where id=%(pk_vaccination)s for update""",
#		"""update vaccination set
#				clin_when=%(date)s,
#--				id_encounter
#--				id_episode
#				narrative=%(narrative)s,
#--				fk_patient
#				fk_provider=%(pk_provider)s,
#				fk_vaccine=(select id from vaccine where trade_name=%(vaccine)s),
#				site=%(site)s,
#				batch_no=%(batch_no)s
#			where id=%(pk_vaccination)s"""
		]

	_updatable_fields = [
#		'date',
#		'narrative',
#		'pk_provider',
#		'vaccine',
#		'site',
#		'batch_no'
	]
#============================================================
class cLabRequest(gmClinItem.cClinItem):
	"""Represents one lab request."""

	_cmd_fetch_payload = """
		select * from lab_request
		where pk=%s"""

	_cmds_store_payload = [
		"""select 1 from lab_request where id=%(pk)s for update""",
		"""update lab_request set
				clin_when=%(clin_when)s,
--				id_encounter
--				id_episode
				narrative=%(narrative)s,
				request_id=%(request_id)s,
				lab_request_id=%(lab_request_id)s,
				lab_rxd_when=%(lab_rxd_when)s,
				results_reported_when=%(results_reported_when)s
				request_status=%(request_status)s,
				is_pending=%(is_pending)s
			where pk=%(pk)s"""
		]

	_updatable_fields = [
		'clin_when',
		'narrative',
		'request_id',
		'lab_request_id',
		'lab_rxd_when',
		'results_reported_when',
		'request_status',
		'is_pending'
	]
	#--------------------------------------------------------
	def _pre_init(self, **kwargs):
		if self.pk is not None:
			return True
		# sanity check
		if None in [kwargs['req_id'], kwargs['lab']]:
			_log.Log(gmLog.lErr, 'req_id and lab must be defined')
			return False
		# generate query
		where_snippets = []
		vals = {}
		where_snippets.append('request_id=%(req_id)s')
		vals['req_id'] = kwargs['req_id']
		if type(kwargs['lab']) == types.IntType:
			where_snippets.append('fk_test_org=%(lab)s')
			vals['lab'] = kwargs['lab']
		else:
			where_snippets.append('fk_test_org=(select pk from test_org where internal_name=%(lab)s)')
			vals['lab'] = str(kwargs['lab'])
		where_clause = ' and '.join(where_snippets)
		cmd = "select pk from lab_request where %s" % where_clause
		data = gmPG.run_ro_query('historica', cmd, None, vals)
		# error
		if data is None:
			_log.Log(gmLog.lErr, 'error getting lab request for %s' % kwargs)
			return False
		# no such request
		if len(data) == 0:
			_log.Log(gmLog.lErr, 'no lab request for %s' % kwargs)
			return False
		self.pk = data[0][0]
		return True
#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':
	import sys
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	gmPG.set_default_client_encoding('latin1')

	lab_result = cLabResult(aPKey=1)
	print lab_result
	fields = lab_result.get_fields()
	for field in fields:
		print field, ':', lab_result[field]
	print "updatable:", lab_result.get_updatable_fields()

	lab_req = cLabRequest(aPKey=1)
	print lab_req
	fields = lab_req.get_fields()
	for field in fields:
		print field, ':', lab_req[field]
	print "updatable:", lab_req.get_updatable_fields()

#============================================================
# $Log: gmPathLab.py,v $
# Revision 1.3  2004-04-12 22:59:38  ncq
# - add lab request
#
# Revision 1.2  2004/04/11 12:07:54  ncq
# - better unit testing
#
# Revision 1.1  2004/04/11 12:04:55  ncq
# - first version
#
