"""GnuMed allergy related business object.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmAllergy.py,v $
# $Id: gmAllergy.py,v 1.2 2004-04-16 00:00:59 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"

from Gnumed.pycommon import gmLog
from Gnumed.business import gmClinItem

gmLog.gmDefLog.Log(gmLog.lInfo, __version__)
#============================================================
class cAllergy(gmClinItem.cClinItem):
	"""Represents one allergy event.
	"""
	_cmd_fetch_payload = """
		select * from v_i18n_patient_allergies
		where id=%s"""

	_cmds_store_payload = [
		"""select 1 from allergy where id=%(id)s for update""",
		"""update allergy set
				substance=%(substance)s,
				substance_code=%(substance_code)s,
				generics=%(generics)s,
				allergene=%(allergene)s,
				atc_code=%(atc_code)s,
				id_type=%(id_type)s,
				generic_specific=%(generic_specific)s,
				definite=%(definite)s,
				narrative=%(reaction)s,
--              id_item,
--              id_episode,
--              id_patient,
--              id_encounter,
--              id_health_issue
			where id=%(id)s"""
		]

	_updatable_fields = [
		'substance',
		'substance_code',	
		'generics',
		'allergene',
		'atc_code',
		'id_type',
		'generic_specific',
		'definite',
		'reaction'
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
	allg = cAllergy(aPKey=1)
	print allg
	fields = allg.get_fields()
	for field in fields:
		print field, ':', allg[field]
	print "updatable:", allg.get_updatable_fields()
	print allg['wrong attribute']
	try:
		allg['wrong attribute'] = 'hallo'
	except:
		_log.LogException('programming error', sys.exc_info())
#============================================================
# $Log: gmAllergy.py,v $
# Revision 1.2  2004-04-16 00:00:59  ncq
# - Carlos fixes
# - save_payload should now work
#
# Revision 1.1  2004/04/12 22:58:55  ncq
# - Carlos sent me this
#
