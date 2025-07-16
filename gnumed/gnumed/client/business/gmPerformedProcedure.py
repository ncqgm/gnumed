# -*- coding: utf-8 -*-
"""GNUmed performed-procedure business object.

license: GPL v2 or later
"""
#============================================================
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, <karsten.hilbert@gmx.net>"

import sys
import logging


# setup translation
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try:
		_
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()

from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmBusinessDBObject

from Gnumed.business import gmHospitalStay
from Gnumed.business import gmCoding
from Gnumed.business import gmOrganization
from Gnumed.business import gmDocuments


_log = logging.getLogger('gm.emr')

#============================================================
_SQL_get_procedures = "select * from clin.v_procedures where %s"

class cPerformedProcedure(gmBusinessDBObject.cBusinessDBObject):

	_cmd_fetch_payload = _SQL_get_procedures % "pk_procedure = %s"
	_cmds_store_payload = [
		"""UPDATE clin.procedure SET
				soap_cat = 'p',
				clin_when = %(clin_when)s,
				clin_end = %(clin_end)s,
				is_ongoing = %(is_ongoing)s,
				narrative = gm.nullify_empty_string(%(performed_procedure)s),
				fk_hospital_stay = %(pk_hospital_stay)s,
				fk_org_unit = (CASE
					WHEN %(pk_hospital_stay)s IS NULL THEN %(pk_org_unit)s
					ELSE NULL
				END)::integer,
				fk_episode = %(pk_episode)s,
				fk_encounter = %(pk_encounter)s,
				fk_doc = %(pk_doc)s,
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				pk = %(pk_procedure)s AND
				xmin = %(xmin_procedure)s
			RETURNING xmin as xmin_procedure"""
	]
	_updatable_fields = [
		'clin_when',
		'clin_end',
		'is_ongoing',
		'performed_procedure',
		'pk_hospital_stay',
		'pk_org_unit',
		'pk_episode',
		'pk_encounter',
		'pk_doc',
		'comment'
	]
	#-------------------------------------------------------
	def __setitem__(self, attribute, value):

		if (attribute == 'pk_hospital_stay') and (value is not None):
			gmBusinessDBObject.cBusinessDBObject.__setitem__(self, 'pk_org_unit', None)

		if (attribute == 'pk_org_unit') and (value is not None):
			gmBusinessDBObject.cBusinessDBObject.__setitem__(self, 'pk_hospital_stay', None)

		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)

	#--------------------------------------------------------
	def format_maximum_information(self, left_margin=0, patient=None):
		return self.format (
			left_margin = left_margin,
			include_episode = True,
			include_codes = True,
			include_address = True,
			include_comm = True,
			include_doc = True
		).split('\n')

	#-------------------------------------------------------
	def format(self, left_margin=0, include_episode=True, include_codes=False, include_address=False, include_comm=False, include_doc=False):

		if self._payload['is_ongoing']:
			end = _(' (ongoing)')
		else:
			end = self._payload['clin_end']
			if end is None:
				end = ''
			else:
				end = ' - %s' % end.strftime('%Y %b %d')

		line = '%s%s%s: %s%s [%s @ %s]' % (
			(' ' * left_margin),
			self._payload['clin_when'].strftime('%Y %b %d'),
			end,
			self._payload['performed_procedure'],
			gmTools.bool2str(include_episode, ' (%s)' % self._payload['episode'], ''),
			self._payload['unit'],
			self._payload['organization']
		)

		line += gmTools.coalesce(self._payload['comment'], '', '\n' + (' ' * left_margin) + _('Comment: ') + '%s')

		if include_comm:
			for channel in self.org_unit.comm_channels:
				line += ('\n%(comm_type)s: %(url)s' % channel)

		if include_address:
			adr = self.org_unit.address
			if adr is not None:
				line += '\n'
				line += '\n'.join(adr.format(single_line = False, show_type = False))
				line += '\n'

		if include_doc:
			doc = self.doc
			if doc is not None:
				line += '\n'
				line += _('Document') + ': ' + doc.format(single_line = True)
				line += '\n'

		if include_codes:
			codes = self.generic_codes
			if len(codes) > 0:
				line += '\n'
			for c in codes:
				line += '%s  %s: %s (%s - %s)\n' % (
					(' ' * left_margin),
					c['code'],
					c['term'],
					c['name_short'],
					c['version']
				)
			del codes

		return line

	#--------------------------------------------------------
	def add_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "INSERT INTO clin.lnk_code2procedure (fk_item, fk_generic_code) values (%(issue)s, %(code)s)"
		args = {
			'issue': self._payload['pk_procedure'],
			'code': pk_code
		}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	def remove_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "DELETE FROM clin.lnk_code2procedure WHERE fk_item = %(issue)s AND fk_generic_code = %(code)s"
		args = {
			'issue': self._payload['pk_procedure'],
			'code': pk_code
		}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_stay(self):
		if self._payload['pk_hospital_stay'] is None:
			return None

		return gmHospitalStay.cHospitalStay(aPK_obj = self._payload['pk_hospital_stay'])

	hospital_stay = property(_get_stay)

	#--------------------------------------------------------
	def _get_org_unit(self):
		return gmOrganization.cOrgUnit(self._payload['pk_org_unit'])

	org_unit = property(_get_org_unit)

	#--------------------------------------------------------
	def _get_doc(self):
		if self._payload['pk_doc'] is None:
			return None
		return gmDocuments.cDocument(aPK_obj = self._payload['pk_doc'])

	doc = property(_get_doc)

	#--------------------------------------------------------
	def _get_generic_codes(self):
		if len(self._payload['pk_generic_codes']) == 0:
			return []

		cmd = gmCoding._SQL_get_generic_linked_codes % 'pk_generic_code = ANY(%(pks)s)'
		args = {'pks': self._payload['pk_generic_codes']}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload['pk_generic_codes']) > 0:
			queries.append ({
				'sql': 'DELETE FROM clin.lnk_code2procedure WHERE fk_item = %(proc)s AND fk_generic_code = ANY(%(codes)s)',
				'args': {
					'proc': self._payload['pk_procedure'],
					'codes': self._payload['pk_generic_codes']
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'sql': 'INSERT INTO clin.lnk_code2procedure (fk_item, fk_generic_code) VALUES (%(proc)s, %(pk_code)s)',
				'args': {
					'proc': self._payload['pk_procedure'],
					'pk_code': pk_code
				}
			})
		if len(queries) == 0:
			return
		# run it all in one transaction
		gmPG2.run_rw_queries(queries = queries)
		return

	generic_codes = property(_get_generic_codes, _set_generic_codes)

#-----------------------------------------------------------
def get_performed_procedures(patient=None, return_pks=False):
	queries = [{
		'sql': 'SELECT * FROM clin.v_procedures WHERE pk_patient = %(pat)s ORDER BY clin_when',
		'args': {'pat': patient}
	}]
	rows = gmPG2.run_ro_queries(queries = queries)
	if return_pks:
		return [ r['pk_procedure'] for r in rows ]
	return [ cPerformedProcedure(row = {'data': r, 'pk_field': 'pk_procedure'})  for r in rows ]

#-----------------------------------------------------------
def get_procedures4document(pk_document=None, return_pks=False):
	args = {'pk_doc': pk_document}
	cmd = _SQL_get_procedures % 'pk_doc = %(pk_doc)s'
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if return_pks:
		return [ r['pk_procedure'] for r in rows ]
	return [ cPerformedProcedure(row = {'data': r, 'pk_field': 'pk_procedure'})  for r in rows ]

#-----------------------------------------------------------
def get_latest_performed_procedure(patient=None):
	queries = [{
		'sql': 'select * FROM clin.v_procedures WHERE pk_patient = %(pat)s ORDER BY clin_when DESC LIMIT 1',
		'args': {'pat': patient}
	}]
	rows = gmPG2.run_ro_queries(queries = queries)
	if len(rows) == 0:
		return None

	return cPerformedProcedure(row = {'data': rows[0], 'pk_field': 'pk_procedure'})

#-----------------------------------------------------------
def create_performed_procedure(encounter=None, episode=None, location=None, hospital_stay=None, procedure=None):

	queries = [{
		'sql': """
			INSERT INTO clin.procedure (
				fk_encounter,
				fk_episode,
				soap_cat,
				fk_org_unit,
				fk_hospital_stay,
				narrative
			) VALUES (
				%(enc)s,
				%(epi)s,
				'p',
				%(loc)s,
				%(stay)s,
				gm.nullify_empty_string(%(proc)s)
			)
			RETURNING pk""",
		'args': {'enc': encounter, 'epi': episode, 'loc': location, 'stay': hospital_stay, 'proc': procedure}
	}]

	rows = gmPG2.run_rw_queries(queries = queries, return_data = True)

	return cPerformedProcedure(aPK_obj = rows[0][0])

#-----------------------------------------------------------
def delete_performed_procedure(procedure=None):
	cmd = 'delete from clin.procedure where pk = %(pk)s'
	args = {'pk': procedure}
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

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	#--------------------------------------------------------
	# define tests
	#--------------------------------------------------------
	def test_performed_procedure():
		procs = get_performed_procedures(patient = 12)
		for proc in procs:
			print(proc.format(left_margin = 2))

	#--------------------------------------------------------
	gmPG2.request_login_params(setup_pool = True)

	test_performed_procedure()
