"""GnuMed vaccination related business objects.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmVaccination.py,v $
# $Id: gmVaccination.py,v 1.4 2004-05-12 14:30:30 ncq Exp $
__version__ = "$Revision: 1.4 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

from Gnumed.pycommon import gmLog, gmExceptions, gmI18N, gmPG
from Gnumed.business import gmClinItem
from Gnumed.pycommon.gmPyCompat import *

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
				narrative=%(narrative)s,
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
class cMissingVaccination(gmClinItem.cClinItem):
	"""Represents one missing vaccination.

	- can be due or overdue
	"""
	_cmd_fetch_payload = """
			(select *, False as overdue
			from v_pat_missing_vaccs vpmv
			where
				pk_patient=%(pat_id)s
					and
				age((select dob from identity where id=%(pat_id)s)) between age_due_min and coalesce(age_due_max, '115 years'::interval)
					and
				indication=%(indication)s
					and
				seq_no=%(seq_no)s
			order by time_left)
				UNION
			(select *, True as overdue
			from v_pat_missing_vaccs vpmv
			where
				pk_patient=%(pat_id)s
					and
				now() - ((select dob from identity where id=%(pat_id)s)) >  coalesce(age_due_max, '115 years'::interval)
					and
				indication=%(indication)s
					and
				seq_no=%(seq_no)s		
			order by amount_overdue)"""

	_cmds_store_payload = []

	_updatable_fields = []
	#--------------------------------------------------------
	def is_overdue(self):
		return self['overdue']
	#--------------------------------------------------------
	def create_vaccination(self):
		# FIXME: create vaccination from myself,
		# either pass in episode/encounter/vaccine id or use default for
		# episode/encounter or use curr_pat.* if pk_patient=curr_pat,
		# should we auto-destroy after create_vaccination() ?
		return (False, 'not implemented')
#============================================================
class cMissingBooster(gmClinItem.cClinItem):
	"""Represents one due booster.
	"""
	_cmd_fetch_payload = """
		select
			indication,
			regime,
			reg_comment,
			vacc_comment,
			age_due_min,
			age_due_max,				
			min_interval,
			amount_overdue,
			now() - amount_overdue as latest_due,
			pk_indication,
			pk_recommended_by
		from v_pat_missing_boosters vpmb
		where
			pk_patient=%(pat_id)s
				and
			indication=%(indication)s"""
	_cmds_store_payload = []

	_updatable_fields = []
	#--------------------------------------------------------
#	def refetch_payload(self):
#		"""
#		Fetches due booster fields from backend
#		"""
#		self._payload = None
#		args = { 'pat_id' : self.pat_id, 'indication' : self.indication, 'seq_no': self.seq_no }
#		data, self._idx = gmPG.run_ro_query(
#			'historica',
#			self.__class__._cmd_fetch_payload,
#			True,
#			args)
#		if data is None:
#			_log.Log(gmLog.lErr, '[%s:%s]: error retrieving instance' % (self.__class__.__name__, self.pk))
#			return False
#		if len(data) == 0:
#			_log.Log(gmLog.lErr, '[%s:%s]: no such instance' % (self.__class__.__name__, self.pk))
#			return None
#		self._payload = data[0]
#		return True
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
		vacc = cVaccination(aPK_obj = result[0][0])
	except gmExceptions.ConstructorError:
		_log.LogException('cannot instantiate vaccination' % (result[0][0]), sys.exc_info, verbose=0)
		return (None, _('internal error, check log'))

	return (True, vacc)
#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':
	import sys
	_log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	#--------------------------------------------------------
	def test_vacc():
		vacc = cVaccination(aPK_obj=1)
		print vacc
		fields = vacc.get_fields()
		for field in fields:
			print field, ':', vacc[field]
		print "updatable:", vacc.get_updatable_fields()
		print vacc['wrong attribute']
		try:
			vacc['wrong attribute'] = 'hallo'
		except:
			_log.LogException('programming error', sys.exc_info(), verbose=0)
	#--------------------------------------------------------
	def test_due_vacc():
		# Test for a due vaccination
		pk_args = {
			'pat_id': 12,
			'indication': 'meningococcus C',
			'seq_no': 1
		}
		missing_vacc = cMissingVaccination(aPK_obj=pk_args)
		fields = missing_vacc.get_fields()
		print "\nDue vaccination:"
		print missing_vacc
		for field in fields:
			print field, ':', missing_vacc[field]
		# Test for an overdue vaccination
		pk_args = {
			'pat_id': 12,
			'indication': 'diphtheria',
			'seq_no': 6
		}
		missing_vacc = cMissingVaccination(aPK_obj=pk_args)
		fields = missing_vacc.get_fields()
		print "\nOverdue vaccination (?):"
		print missing_vacc
		for field in fields:
			print field, ':', missing_vacc[field]
	#--------------------------------------------------------
	def test_due_booster():
		pk_args = {
			'pat_id': 12,
			'indication': 'influenza'
		}
		missing_booster = cMissingBooster(aPK_obj=pk_args)
		fields = missing_booster.get_fields()
		print "\nDue booster:"
		print missing_booster
		for field in fields:
			print field, ':', missing_booster[field]
	#--------------------------------------------------------
	gmPG.set_default_client_encoding('latin1')
	test_vacc()
	test_due_vacc()
	test_due_booster()
#============================================================
# $Log: gmVaccination.py,v $
# Revision 1.4  2004-05-12 14:30:30  ncq
# - cMissingVaccination()
# - cMissingBooster()
#
# Revision 1.3  2004/04/24 12:59:17  ncq
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
