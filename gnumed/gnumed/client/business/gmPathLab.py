"""GnuMed vaccination related business objects.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmPathLab.py,v $
# $Id: gmPathLab.py,v 1.2 2004-04-11 12:07:54 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

from Gnumed.pycommon import gmLog
from Gnumed.business import gmClinItem

gmLog.gmDefLog.Log(gmLog.lInfo, __version__)
#============================================================
class cLabResult(gmClinItem.cClinItem):
	"""Represents one vaccination event.
	"""
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
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':
	import sys
	_log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	gmPG.set_default_client_encoding('latin1')
	lab_result = cLabResult(aPKey=1)
	print lab_result
	fields = lab_result.get_fields()
	for field in fields:
		print field, ':', lab_result[field]
	print "updatable:", lab_result.get_updatable_fields()
	print lab_result['wrong attribute']
	try:
		lab_result['wrong attribute'] = 'hallo'
	except:
		_log.LogException('programming error', sys.exc_info())
#============================================================
# $Log: gmPathLab.py,v $
# Revision 1.2  2004-04-11 12:07:54  ncq
# - better unit testing
#
# Revision 1.1  2004/04/11 12:04:55  ncq
# - first version
#
