"""GnuMed health related business object.

license: GPL
"""
#============================================================
__version__ = "$Revision: 1.2 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"

from Gnumed.pycommon import gmLog
from Gnumed.business import gmClinItem

gmLog.gmDefLog.Log(gmLog.lInfo, __version__)
#============================================================
class cHealthIssue(gmClinItem.cClinItem):
	"""Represents one health issue.
	"""
	_cmd_fetch_payload = """select * from clin_health_issue where id=%s"""

	_cmds_store_payload = [
		"""select 1 from clin_health_issue where id=%(id)s for update""",
		"""update clin_health_issue set
				description=%(description)s
			where id=%(id)s"""
		]

	_updatable_fields = [
		'description'
	]
#============================================================
class cEpisode(gmClinItem.cClinItem):
	"""Represents one clinical episode.
	"""
	_cmd_fetch_payload = """
		select * from v_pat_episodes
		where id_episode=%s
		"""
	_cmds_store_payload = [
		"""select 1 from clin_episode where id=%(id)s for update""",
		"""update clin_episode set
				description=%(description)s,
				id_health_issue=%(id_health_issue)s
			where id=%(id)s"""
		]

	_updatable_fields = [
		'description',
		'id_health_issue'
	]
#============================================================
class cEncounter(gmClinItem.cClinItem):
	"""Represents one encounter.
	"""
	_cmd_fetch_payload = """
		select * from v_pat_encounters
		where pk_encounter=%s
		"""
	_cmds_store_payload = [
		"""select 1 from clin_encounter where id=%(pk_encounter)s for update""",
		"""update clin_encounter set
				description=%(description)s,
				started=%(started)s,
				last_affirmed=%(last_affirmed)s,
				fk_location=%(pk_location)s,
				fk_provider=%(pk_provider)s,
				fk_type=%(pk_type)s
			where id=%(pk_encounter)s"""
		]

	_updatable_fields = [
		'description',
		'started',
		'last_affirmed',
		'pk_location',
		'pk_provider',
		'pk_type'
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

	print "health issue test"
	print "-----------------"
	h_issue = cHealthIssue(aPK_obj=1)
	print h_issue
	fields = h_issue.get_fields()
	for field in fields:
		print field, ':', h_issue[field]
	print "updatable:", h_issue.get_updatable_fields()

	print "episode test"
	print "------------"
	episode = cEpisode(aPK_obj=1)
	print episode
	fields = episode.get_fields()
	for field in fields:
		print field, ':', episode[field]
	print "updatable:", episode.get_updatable_fields()

	print "encounter test"
	print "--------------"
	encounter = cEncounter(aPK_obj=1)
	print encounter
	fields = encounter.get_fields()
	for field in fields:
		print field, ':', encounter[field]
	print "updatable:", encounter.get_updatable_fields()
#============================================================
# $Log: gmEMRStructItems.py,v $
# Revision 1.2  2004-05-12 14:28:53  ncq
# - allow dict style pk definition in __init__ for multicolum primary keys (think views)
# - self.pk -> self.pk_obj
# - __init__(aPKey) -> __init__(aPK_obj)
#
# Revision 1.1  2004/04/17 12:18:50  ncq
# - health issue, episode, encounter classes
#
