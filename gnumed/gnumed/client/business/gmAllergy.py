"""GnuMed allergy related business object.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmAllergy.py,v $
# $Id: gmAllergy.py,v 1.6 2004-05-12 14:28:52 ncq Exp $
__version__ = "$Revision: 1.6 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"

from Gnumed.pycommon import gmLog
from Gnumed.business import gmClinItem

gmLog.gmDefLog.Log(gmLog.lInfo, __version__)
#============================================================
class cAllergy(gmClinItem.cClinItem):
	"""Represents one allergy event.
	"""
	_cmd_fetch_payload = """
		select * from v_pat_allergies
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
				narrative=%(reaction)s
			where id=%(id)s"""
		]
#--              id_item,
#--              id_episode,
#--              id_patient,
#--              id_encounter,
#--              id_health_issue

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
	allg = cAllergy(aPK_obj=1)
	print allg
#	fields = allg.get_fields()
#	for field in fields:
#		print field, ':', allg[field]
	print "updatable:", allg.get_updatable_fields()
#	allg['reaction'] = 'hehehe'
#	print allg
#	allg.save_payload()
#============================================================
# $Log: gmAllergy.py,v $
# Revision 1.6  2004-05-12 14:28:52  ncq
# - allow dict style pk definition in __init__ for multicolum primary keys (think views)
# - self.pk -> self.pk_obj
# - __init__(aPKey) -> __init__(aPK_obj)
#
# Revision 1.5  2004/04/20 13:32:33  ncq
# - improved __str__ output
#
# Revision 1.4  2004/04/20 00:17:55  ncq
# - allergies API revamped, kudos to Carlos
#
# Revision 1.3  2004/04/16 16:17:33  ncq
# - test save_payload
#
# Revision 1.2  2004/04/16 00:00:59  ncq
# - Carlos fixes
# - save_payload should now work
#
# Revision 1.1  2004/04/12 22:58:55  ncq
# - Carlos sent me this
#
