"""GNUmed family history handling middleware"""
#============================================================
__license__ = "GPL"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


# stdlib
import sys, logging


# GNUmed modules
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmTools

from Gnumed.business import gmCoding


_log = logging.getLogger('gm.fhx')

#============================================================
# relationship type handling
#------------------------------------------------------------
def create_relationship_type(relationship=None, genetic=None):

	args = {'rel': relationship, 'gen': genetic}

	# already exists ?
	cmd = """
		SELECT *, _(description) as l10n_description
		FROM clin.fhx_relation_type
		WHERE
			description = %(rel)s
				OR
			_(description) = %(rel)s
	"""
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(rows) > 0:
		return rows[0]

	# create it
	cmd = """
		INSERT INTO clin.fhx_relation_type (
			description,
			is_genetic
		) VALUES (
			i18n.i18n(gm.nullify_empty_string(%(rel)s)),
			%(gen)s
		)
		RETURNING *
	"""
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)
	return rows[0]

#============================================================
# Family History item handling
#------------------------------------------------------------
_SQL_get_family_history = "SELECT * from clin.v_family_history WHERE %s"

class cFamilyHistory(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a Family History item."""

	_cmd_fetch_payload = _SQL_get_family_history % "pk_family_history = %s"
	_cmds_store_payload = [
		"""
			UPDATE clin.family_history SET
				narrative = gm.nullify_empty_string(%(condition)s),
				age_noted = gm.nullify_empty_string(%(age_noted)s),
				age_of_death = %(age_of_death)s,
				contributed_to_death = %(contributed_to_death)s,
				clin_when = %(when_known_to_patient)s,
				name_relative = gm.nullify_empty_string(%(name_relative)s),
				dob_relative = %(dob_relative)s,
				comment = gm.nullify_empty_string(%(comment)s),
				fk_episode = %(pk_episode)s,
				fk_relation_type = %(pk_fhx_relation_type)s
			WHERE
				pk = %(pk_family_history)s
					AND
				xmin = %(xmin_family_history)s
			RETURNING
				pk as pk_family_history,
				xmin as xmin_family_history
		"""
	]
	# view columns that can be updated:
	_updatable_fields = [
		'condition',
		'age_noted',
		'age_of_death',
		'contributed_to_death',
		'when_known_to_patient',
		'name_relative',
		'dob_relative',
		'pk_encounter',
		'pk_episode',
		'pk_fhx_relation_type',
		'comment'
	]

	#--------------------------------------------------------
	def add_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""

		if pk_code in self._payload['pk_generic_codes']:
			return

		cmd = """
			INSERT INTO clin.lnk_code2fhx
				(fk_item, fk_generic_code)
			SELECT
				%(item)s,
				%(code)s
			WHERE NOT EXISTS (
				SELECT 1 FROM clin.lnk_code2fhx
				WHERE
					fk_item = %(item)s
						AND
					fk_generic_code = %(code)s
			)"""
		args = {
			'item': self._payload['pk_family_history'],
			'code': pk_code
		}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		return

	#--------------------------------------------------------
	def remove_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "DELETE FROM clin.lnk_code2fhx WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		args = {
			'item': self._payload['pk_family_history'],
			'code': pk_code
		}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	def format_maximum_information(self, patient=None):

		# include more fields from clin.v_family_history

		return self.format (
			include_episode = True,
			include_comment = True,
			include_codes = True
		).split('\n')

	#--------------------------------------------------------
	def format(self, left_margin=0, include_episode=False, include_comment=False, include_codes=False):

		line = '%s%s' % (
			(' ' * left_margin),
			self._payload['l10n_relation']
		)
		if self._payload['age_of_death'] is not None:
			line += ' (%s %s)' % (
				gmTools.u_latin_cross,
				gmDateTime.format_interval_medically(self._payload['age_of_death'])
			)
		line += ': %s' % self._payload['condition']
		if self._payload['age_noted'] is not None:
			line += gmTools.coalesce(self._payload['age_noted'], '', ' (@ %s)')
		if self._payload['contributed_to_death']:
			line += ' %s %s' % (
				gmTools.u_arrow2right,
				gmTools.u_skull_and_crossbones
			)

		if include_episode:
			line += '\n%s  %s: %s' % (
				(' ' * left_margin),
				_('Episode'),
				self._payload['episode']
			)

		if include_comment:
			if self._payload['comment'] is not None:
				line += '\n%s  %s' % (
					(' ' * left_margin),
					self._payload['comment']
				)

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
	# properties
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
				'sql': 'DELETE FROM clin.lnk_code2fhx WHERE fk_item = %(fhx)s AND fk_generic_code = ANY(%(codes)s)',
				'args': {
					'fhx': self._payload['pk_family_history'],
					'codes': self._payload['pk_generic_codes']
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'sql': 'INSERT INTO clin.lnk_code2fhx (fk_item, fk_generic_code) VALUES (%(fhx)s, %(pk_code)s)',
				'args': {
					'fhx': self._payload['pk_family_history'],
					'pk_code': pk_code
				}
			})
		if len(queries) == 0:
			return
		# run it all in one transaction
		gmPG2.run_rw_queries(queries = queries)
		return

	generic_codes = property(_get_generic_codes, _set_generic_codes)
#------------------------------------------------------------
def get_family_history(order_by=None, patient=None):

	args = {}
	where_parts = []

	if patient is not None:
		where_parts.append('pk_patient = %(pat)s')
		args['pat'] = patient

	if order_by is None:
		if len(where_parts) == 0:
			order_by = 'true'
		else:
			order_by = ''
	else:
		if len(where_parts) == 0:
			order_by = 'true ORDER BY %s' % order_by
		else:
			order_by = 'ORDER BY %s' % order_by

	cmd = _SQL_get_family_history % ' AND '.join(where_parts) + ' ' + order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return [ cFamilyHistory(row = {'data': r, 'pk_field': 'pk_family_history'}) for r in rows ]

#------------------------------------------------------------
def create_family_history(encounter=None, episode=None, condition=None, relation=None):

	args = {
		'enc': encounter,
		'epi': episode,
		'cond': condition,
		'rel': relation
	}
	cmd = """
		INSERT INTO clin.family_history (
			soap_cat,
			fk_encounter,
			fk_episode,
			narrative,
			fk_relation_type
		) VALUES (
			's'::text,
			%(enc)s,
			%(epi)s,
			gm.nullify_empty_string(%(cond)s),
			%(rel)s
		)
		RETURNING pk
	"""
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)

	return cFamilyHistory(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
def delete_family_history(pk_family_history=None):
	args = {'pk': pk_family_history}
	cmd = "DELETE FROM clin.family_history WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	return True
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#----------------------------------------------------
	def test_get_fhx():
		print("family history:")
		for fhx in get_family_history():
			print(fhx)
	#----------------------------------------------------
	test_get_fhx()

#============================================================
