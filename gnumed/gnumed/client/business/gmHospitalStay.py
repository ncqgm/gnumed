# -*- coding: utf-8 -*-
"""GNUmed hospital stay business object.

license: GPL v2 or later
"""
#============================================================
__author__ = "<karsten.hilbert@gmx.net>"

import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmBusinessDBObject

from Gnumed.business import gmDocuments


_log = logging.getLogger('gm.emr')

#============================================================
_SQL_get_hospital_stays = "select * from clin.v_hospital_stays where %s"

class cHospitalStay(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_hospital_stays % "pk_hospital_stay = %s"
	_cmds_store_payload = [
		"""UPDATE clin.hospital_stay SET
				clin_when = %(admission)s,
				discharge = %(discharge)s,
				fk_org_unit = %(pk_org_unit)s,
				narrative = gm.nullify_empty_string(%(comment)s),
				fk_episode = %(pk_episode)s,
				fk_encounter = %(pk_encounter)s
			WHERE
				pk = %(pk_hospital_stay)s
					AND
				xmin = %(xmin_hospital_stay)s
			RETURNING
				xmin AS xmin_hospital_stay
			"""
	]
	_updatable_fields = [
		'admission',
		'discharge',
		'pk_org_unit',
		'pk_episode',
		'pk_encounter',
		'comment'
	]

	#--------------------------------------------------------
	def format_maximum_information(self, patient=None):
		return self.format (
			include_procedures = True,
			include_docs = True
		).split('\n')

	#-------------------------------------------------------
	def format(self, left_margin=0, include_procedures=False, include_docs=False, include_episode=True):

		if self._payload['discharge']:
			discharge = ' - %s' % self._payload['discharge'].strftime('%Y %b %d')
		else:
			discharge = ''

		episode = ''
		if include_episode:
			episode = ': %s%s%s' % (
				gmTools.u_left_double_angle_quote,
				self._payload['episode'],
				gmTools.u_right_double_angle_quote
			)

		lines = ['%s%s%s (%s@%s)%s' % (
			' ' * left_margin,
			self._payload['admission'].strftime('%Y %b %d'),
			discharge,
			self._payload['ward'],
			self._payload['hospital'],
			episode
		)]

		if include_docs:
			for doc in self.documents:
				lines.append('%s%s: %s\n' % (
					' ' * left_margin,
					_('Document'),
					doc.format(single_line = True)
				))

		return '\n'.join(lines)

	#--------------------------------------------------------
	def _get_documents(self):
		return [ gmDocuments.cDocument(aPK_obj = pk_doc) for pk_doc in  self._payload['pk_documents'] ]

	documents = property(_get_documents)

#-----------------------------------------------------------
def get_latest_patient_hospital_stay(patient:int=None) -> cHospitalStay | None:
	"""Actually, the stay with the most recent admission."""
	SQL = _SQL_get_hospital_stays % "pk_patient = %(pat)s ORDER BY admission DESC LIMIT 1"
	queries = [{'sql': SQL, 'args': {'pat': patient}}]
	rows = gmPG2.run_ro_queries(queries = queries)
	if not rows:
		return None

	return cHospitalStay(row = {'data': rows[0], 'pk_field': 'pk_hospital_stay'})

#-----------------------------------------------------------
def get_patient_hospital_stays(patient:int=None, ongoing_only:bool=False, return_pks:bool=False) -> list[cHospitalStay]:
	args = {'pat': patient}
	if ongoing_only:
		SQL = _SQL_get_hospital_stays % "pk_patient = %(pat)s AND discharge is NULL ORDER BY admission"
	else:
		SQL = _SQL_get_hospital_stays % "pk_patient = %(pat)s ORDER BY admission"
	queries = [{'sql': SQL, 'args': args}]
	rows = gmPG2.run_ro_queries(queries = queries)
	if return_pks:
		return [ r['pk_hospital_stay'] for r in rows ]

	return [ cHospitalStay(row = {'data': r, 'pk_field': 'pk_hospital_stay'})  for r in rows ]

#-----------------------------------------------------------
def create_hospital_stay(encounter:int=None, episode:int=None, fk_org_unit:int=None) -> cHospitalStay:
	SQL = 'INSERT INTO clin.hospital_stay (fk_encounter, fk_episode, fk_org_unit) VALUES (%(enc)s, %(epi)s, %(fk_org_unit)s) RETURNING pk'
	args = {'enc': encounter, 'epi': episode, 'fk_org_unit': fk_org_unit}
	queries = [{'sql': SQL, 'args': args}]
	rows = gmPG2.run_rw_queries(queries = queries, return_data = True)
	return cHospitalStay(aPK_obj = rows[0][0])

#-----------------------------------------------------------
def delete_hospital_stay(stay:int=None):
	cmd = 'DELETE FROM clin.hospital_stay WHERE pk = %(pk)s'
	args = {'pk': stay}
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	return True

#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	#--------------------------------------------------------
	# define tests
	#--------------------------------------------------------
	def test_hospital_stay():
		stay = create_hospital_stay(encounter = 1, episode = 2, fk_org_unit = 1)
#		stay['hospital'] = u'Starfleet Galaxy General Hospital'
#		stay.save_payload()
		print(stay)
		for s in get_patient_hospital_stays(12):
			print(s)
			print(s.format())
		delete_hospital_stay(stay['pk_hospital_stay'])
		print('should fail:')
		stay = create_hospital_stay(encounter = 1, episode = 4, fk_org_unit = 1)

	#--------------------------------------------------------
	gmPG2.request_login_params(setup_pool = True)

	test_hospital_stay()
