"""GnuMed vaccination related business objects.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmVaccination.py,v $
# $Id: gmVaccination.py,v 1.3 2004-04-24 12:59:17 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

from Gnumed.pycommon import gmLog, gmExceptions, gmI18N, gmPG
from Gnumed.business import gmClinItem

gmLog.gmDefLog.Log(gmLog.lInfo, __version__)
#============================================================
class cVaccination(gmClinItem.cClinItem):
	"""Represents one vaccination event.
	"""
	_cmd_fetch_payload = """
		select * from v_pat_vacc4ind
		where pk_vaccination=%s"""

	_cmds_store_payload = [
		"""select 1 from vaccination where id=%(pk_vaccination)s for update""",
		"""update vaccination set
				clin_when=%(date)s,
--				id_encounter
--				id_episode
				narrative=%(narrative)s,
--				fk_patient
				fk_provider=%(pk_provider)s,
				fk_vaccine=(select id from vaccine where trade_name=%(vaccine)s),
				site=%(site)s,
				batch_no=%(batch_no)s
			where id=%(pk_vaccination)s
			order by date desc"""
		]

	_updatable_fields = [
		'date',
		'narrative',
		'pk_provider',
		'vaccine',
		'site',
		'batch_no'
	]
#============================================================
# convenience functions
#------------------------------------------------------------
def create_vaccination(patient_id=None, episode_id=None, encounter_id=None, vaccine=None):
	# sanity check
	# any of the args being None should fail the SQL code
	# do episode/encounter belong to the patient ?
	cmd = "select exists(select 1 from v_patient_items where id_patient=%s and id_episode=%s and id_encounter=%s)"
	valid = gmPG.run_ro_query('historica', cmd, None, patient_id, episode_id, encounter_id)
	if valid is None:
		_log.Log(gmLog.lErr, 'error checking patient [%s] <-> episode [%s] <-> encounter [%s] consistency' % (patient_id, episode_id, encounter_id))
		return (None, _('internal error, check log'))
	if not valid[0]:
		_log(gmLog.lErr, 'episode [%s] and/or encounter [%s] apparently do not belong to patient [%s]' % (episode_id, encounter_id, patient_id))
		return (None, _('consistency error, check log'))
	# insert new vaccination
	queries = []
	if type(vaccine) == types.IntType:
		cmd = "insert into vaccination (id_encounter, id_episode, fk_patient, fk_provider, fk_vaccine) values (%s, %s, %s, %s, %s)"
	else:
		cmd = "insert into vaccination (id_encounter, id_episode, fk_patient, fk_provider, fk_vaccine) values (%s, %s, %s, %s, (select id from vaccine where trade_name=%s))"
		vaccine = str(vaccine)
	queries.append((cmd, [encounter_id, episode_id, patient_id, vaccine]))
	# get PK of inserted row
	cmd = "select currval('vaccination_id_seq')"
	queries.append((cmd, []))

	result, msg = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (None, msg)

	try:
		vacc = cVaccination(aPKey = result[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate vaccination' % (result[0][0]), sys.exc_info, verbose=0)
		return (None, _('internal error, check log'))

	return (True, vacc)

#		try:
#			vals1['date'] = aVacc['date given']
#			cols.append('clin_when')
#			val_snippets.append('%(date)s')
#		except KeyError:
#			_log.LogException('missing date_given', sys.exc_info(), verbose=0)
#			return (None, _('"date given" missing'))

#		try:
#			vals1['narrative'] = aVacc['progress note']
#			cols.append('narrative')
#			val_snippets.append('%(narrative)s')
#		except KeyError:
#			pass

#		try:
#			vals1['site'] = aVacc['site given']
#			cols.append('site')
#			val_snippets.append('%(site)s')
#		except KeyError:
#			pass

#		try:
#			vals1['batch'] = aVacc['batch no']
#			cols.append('batch_no')
#			val_snippets.append('%(batch)s')
#		except KeyError:
#			_log.LogException('missing batch #', sys.exc_info(), verbose=0)
#			return (None, _('"batch #" missing'))

#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':
	import sys
	_log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	gmPG.set_default_client_encoding('latin1')
	vacc = cVaccination(aPKey=1)
	print vacc
	fields = vacc.get_fields()
	for field in fields:
		print field, ':', vacc[field]
	print "updatable:", vacc.get_updatable_fields()
	print vacc['wrong attribute']
	try:
		vacc['wrong attribute'] = 'hallo'
	except:
		_log.LogException('programming error', sys.exc_info())
#============================================================
# $Log: gmVaccination.py,v $
# Revision 1.3  2004-04-24 12:59:17  ncq
# - all shiny and new, vastly improved vaccinations
#   handling via clinical item objects
# - mainly thanks to Carlos Moro
#
# Revision 1.2  2004/04/11 12:07:54  ncq
# - better unit testing
#
# Revision 1.1  2004/04/11 10:16:53  ncq
# - first version
#
