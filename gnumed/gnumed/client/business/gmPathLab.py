"""GNUmed measurements related business objects."""

# FIXME: use UCUM from Regenstrief Institute
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"


import sys
import logging
import decimal
import re as regex
import os.path


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
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmHooks
from Gnumed.pycommon import gmCfgINI

from Gnumed.business import gmOrganization
from Gnumed.business import gmCoding

_log = logging.getLogger('gm.lab')
_cfg = gmCfgINI.gmCfgData()

#============================================================
HL7_RESULT_STATI = {
	None: _('unknown'),
	'': _('empty status'),
	'C': _('C (HL7: Correction, replaces previous final)'),
	'D': _('D (HL7: Deletion)'),
	'F': _('F (HL7: Final)'),
	'I': _('I (HL7: pending, specimen In lab)'),
	'P': _('P (HL7: Preliminary)'),
	'R': _('R (HL7: result entered, not yet verified)'),
	'S': _('S (HL7: partial)'),
	'X': _('X (HL7: cannot obtain results for this observation)'),
	'U': _('U (HL7: mark as final (I/P/R/S -> F, value Unchanged)'),
	'W': _('W (HL7: original Wrong (say, wrong patient))')
}

URL_test_result_information = 'http://www.laborlexikon.de'
URL_test_result_information_search = "https://www.google.de/search?as_oq=%(search_term)s&num=10&as_sitesearch=laborlexikon.de"

#============================================================
def _on_test_result_modified():
	"""Always relates to the active patient."""
	gmHooks.run_hook_script(hook = 'after_test_result_modified')

gmDispatcher.connect(_on_test_result_modified, 'clin.test_result_mod_db')

#============================================================
_SQL_get_test_orgs = "SELECT * FROM clin.v_test_orgs WHERE %s"

class cTestOrg(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one test org/lab."""
	_cmd_fetch_payload = _SQL_get_test_orgs % 'pk_test_org = %s'
	_cmds_store_payload = [
		"""UPDATE clin.test_org SET
				fk_org_unit = %(pk_org_unit)s,
				contact = gm.nullify_empty_string(%(test_org_contact)s),
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				pk = %(pk_test_org)s
					AND
				xmin = %(xmin_test_org)s
			RETURNING
				xmin AS xmin_test_org
		"""
	]
	_updatable_fields = [
		'pk_org_unit',
		'test_org_contact',
		'comment'
	]
#------------------------------------------------------------
def create_test_org(name=None, comment=None, pk_org_unit=None, link_obj=None):

	_log.debug('creating test org [%s:%s:%s]', name, comment, pk_org_unit)

	if name is None:
		name = 'unassigned lab'

	# get org unit
	if pk_org_unit is None:
		org = gmOrganization.create_org (
			link_obj = link_obj,
			organization = name,
			category = 'Laboratory'
		)
		org_unit = gmOrganization.create_org_unit (
			link_obj = link_obj,
			pk_organization = org['pk_org'],
			unit = name
		)
		pk_org_unit = org_unit['pk_org_unit']

	# test org exists ?
	args = {'pk_unit': pk_org_unit}
	cmd = 'SELECT pk_test_org FROM clin.v_test_orgs WHERE pk_org_unit = %(pk_unit)s'
	rows = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}])

	if len(rows) == 0:
		cmd = 'INSERT INTO clin.test_org (fk_org_unit) VALUES (%(pk_unit)s) RETURNING pk'
		rows = gmPG2.run_rw_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}], return_data = True)

	test_org = cTestOrg(link_obj = link_obj, aPK_obj = rows[0][0])
	if comment is not None:
		comment = comment.strip()
	test_org['comment'] = comment
	test_org.save(conn = link_obj)

	return test_org
#------------------------------------------------------------
def delete_test_org(test_org=None):
	args = {'pk': test_org}
	cmd = """
		DELETE FROM clin.test_org
		WHERE
			pk = %(pk)s
				AND
			NOT EXISTS (SELECT 1 FROM clin.lab_request WHERE fk_test_org = %(pk)s LIMIT 1)
				AND
			NOT EXISTS (SELECT 1 FROM clin.test_type WHERE fk_test_org = %(pk)s LIMIT 1)
	"""
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
#------------------------------------------------------------
def get_test_orgs(order_by='unit', return_pks=False):
	cmd = 'SELECT * FROM clin.v_test_orgs ORDER BY %s' % order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	if return_pks:
		return [ r['pk_test_org'] for r in rows ]
	return [ cTestOrg(row = {'pk_field': 'pk_test_org', 'data': r}) for r in rows ]

#============================================================
# test panels / profiles
#------------------------------------------------------------
_SQL_get_test_panels = "SELECT * FROM clin.v_test_panels WHERE %s"

class cTestPanel(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a grouping/listing of tests into a panel."""

	_cmd_fetch_payload = _SQL_get_test_panels % "pk_test_panel = %s"
	_cmds_store_payload = [
		"""
			UPDATE clin.test_panel SET
				description = gm.nullify_empty_string(%(description)s),
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				pk = %(pk_test_panel)s
					AND
				xmin = %(xmin_test_panel)s
			RETURNING
				xmin AS xmin_test_panel
		"""
	]
	_updatable_fields = [
		'description',
		'comment'
	]
	#--------------------------------------------------------
	def format(self):
		txt = _('Test panel "%s"          [#%s]\n') % (
			self._payload['description'],
			self._payload['pk_test_panel']
		)

		if self._payload['comment'] is not None:
			txt += '\n'
			txt += gmTools.wrap (
				text = self._payload['comment'],
				width = 50,
				initial_indent = ' ',
				subsequent_indent = ' '
			)
			txt += '\n'

		txt += '\n'
		txt += _('Includes:\n')
		if len(self.included_loincs) == 0:
			txt += _('no tests')
		else:
			tts_by_loinc = {}
			for loinc in self._payload['loincs']:
				tts_by_loinc[loinc] = []
			for ttype in self.test_types:
				tts_by_loinc[ttype['loinc']].append(ttype)
			for loinc, ttypes in tts_by_loinc.items():
				# maybe resolve LOINC, too
				txt += _(' %s: %s\n') % (
					loinc,
					'; '.join([ '%(abbrev)s@%(name_org)s [#%(pk_test_type)s]' % tt for tt in ttypes ])
				)

		codes = self.generic_codes
		if len(codes) > 0:
			txt += '\n'
			for c in codes:
				txt += '    %s: %s (%s - %s)\n' % (
					c['code'],
					c['term'],
					c['name_short'],
					c['version']
				)

		return txt

	#--------------------------------------------------------
	def add_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "INSERT INTO clin.lnk_code2tst_pnl (fk_item, fk_generic_code) values (%(tp)s, %(code)s)"
		args = {
			'tp': self._payload['pk_test_panel'],
			'code': pk_code
		}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	def remove_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "DELETE FROM clin.lnk_code2tst_pnl WHERE fk_item = %(tp)s AND fk_generic_code = %(code)s"
		args = {
			'tp': self._payload['pk_test_panel'],
			'code': pk_code
		}
		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	def get_test_types_for_results(self, pk_patient, order_by=None, unique_meta_types=False):
		"""Retrieve data about test types on this panel (for which this patient has results)."""

		if order_by is None:
			order_by = ''
		else:
			order_by = 'ORDER BY %s' % order_by

		if unique_meta_types:
			cmd = """
				SELECT * FROM clin.v_test_types c_vtt
				WHERE c_vtt.pk_test_type IN (
						SELECT DISTINCT ON (c_vtr1.pk_meta_test_type) c_vtr1.pk_test_type
						FROM clin.v_test_results c_vtr1
						WHERE
							c_vtr1.pk_test_type IN %%(pks)s
								AND
							c_vtr1.pk_patient = %%(pat)s
								AND
							c_vtr1.pk_meta_test_type IS NOT NULL
					UNION ALL
						SELECT DISTINCT ON (c_vtr2.pk_test_type) c_vtr2.pk_test_type
						FROM clin.v_test_results c_vtr2
						WHERE
							c_vtr2.pk_test_type IN %%(pks)s
								AND
							c_vtr2.pk_patient = %%(pat)s
								AND
							c_vtr2.pk_meta_test_type IS NULL
				)
				%s""" % order_by
		else:
			cmd = """
				SELECT * FROM clin.v_test_types c_vtt
				WHERE c_vtt.pk_test_type IN (
					SELECT DISTINCT ON (c_vtr.pk_test_type) c_vtr.pk_test_type
					FROM clin.v_test_results c_vtr
					WHERE
						c_vtr.pk_test_type = ANY(%%(pks)s)
								AND
						c_vtr.pk_patient = %%(pat)s
				)
				%s""" % order_by

		args = {
			'pat': pk_patient,
			'pks': [ tt['pk_test_type'] for tt in self._payload['test_types'] ]
		}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return [ cMeasurementType(row = {'pk_field': 'pk_test_type', 'data': r}) for r in rows ]

	#--------------------------------------------------------
	def add_loinc(self, loinc):
		if self._payload['loincs'] is not None:
			if loinc in self._payload['loincs']:
				return
		gmPG2.run_rw_queries(queries = [{
			'sql': 'INSERT INTO clin.lnk_loinc2test_panel (fk_test_panel, loinc) VALUES (%(pk_pnl)s, %(loinc)s)',
			'args': {'loinc': loinc, 'pk_pnl': self._payload['pk_test_panel']}
		}])
		return

	#--------------------------------------------------------
	def remove_loinc(self, loinc):
		if self._payload['loincs'] is None:
			return
		if loinc not in self._payload['loincs']:
			return
		gmPG2.run_rw_queries(queries = [{
			'sql': 'DELETE FROM clin.lnk_loinc2test_panel WHERE fk_test_panel = %(pk_pnl)s AND loinc = %(loinc)s',
			'args': {'loinc': loinc, 'pk_pnl': self._payload['pk_test_panel']}
		}])
		return

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_included_loincs(self):
		return self._payload['loincs']

	def _set_included_loincs(self, loincs):
		queries = []
		# remove those which don't belong
		if len(loincs) == 0:
			cmd = 'DELETE FROM clin.lnk_loinc2test_panel WHERE fk_test_panel = %(pk_pnl)s'
		else:
			cmd = 'DELETE FROM clin.lnk_loinc2test_panel WHERE fk_test_panel = %(pk_pnl)s AND loinc <> ALL(%(loincs)s)'
		queries.append({'sql': cmd, 'args': {'loincs': loincs, 'pk_pnl': self._payload['pk_test_panel']}})
		# add those not there yet
		if len(loincs) > 0:
			for loinc in loincs:
				cmd = """INSERT INTO clin.lnk_loinc2test_panel (fk_test_panel, loinc)
				SELECT %(pk_pnl)s, %(loinc)s WHERE NOT EXISTS (
					SELECT 1 FROM clin.lnk_loinc2test_panel WHERE
						fk_test_panel = %(pk_pnl)s
							AND
						loinc = %(loinc)s
				)"""
				queries.append({'sql': cmd, 'args': {'loinc': loinc, 'pk_pnl': self._payload['pk_test_panel']}})
		return gmPG2.run_rw_queries(queries = queries)

	included_loincs = property(_get_included_loincs, _set_included_loincs)

	#--------------------------------------------------------
	def _get_test_types(self):
		if len(self._payload['test_types']) == 0:
			return []

		rows = gmPG2.run_ro_queries (
			queries = [{
				'sql': _SQL_get_test_types % 'pk_test_type = ANY(%(pks)s) ORDER BY unified_abbrev',
				'args': {'pks': [ tt['pk_test_type'] for tt in self._payload['test_types'] ]}
			}]
		)
		return [ cMeasurementType(row = {'data': r, 'pk_field': 'pk_test_type'}) for r in rows ]

	test_types = property(_get_test_types)

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
				'sql': 'DELETE FROM clin.lnk_code2tst_pnl WHERE fk_item = %(tp)s AND fk_generic_code = ANY(%(codes)s)',
				'args': {
					'tp': self._payload['pk_test_panel'],
					'codes': self._payload['pk_generic_codes']
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'sql': 'INSERT INTO clin.lnk_code2test_panel (fk_item, fk_generic_code) VALUES (%(tp)s, %(pk_code)s)',
				'args': {
					'tp': self._payload['pk_test_panel'],
					'pk_code': pk_code
				}
			})
		if len(queries) == 0:
			return
		# run it all in one transaction
		gmPG2.run_rw_queries(queries = queries)
		return

	generic_codes = property(_get_generic_codes, _set_generic_codes)

	#--------------------------------------------------------
	def get_most_recent_results(self, pk_patient=None, order_by=None, group_by_meta_type=False, include_missing=False):

		if len(self._payload['test_types']) == 0:
			return []

		pnl_results = get_most_recent_results_for_panel (
			pk_patient = pk_patient,
			pk_panel = self._payload['pk_test_panel'],
			order_by = order_by,
			group_by_meta_type = group_by_meta_type
		)
		if not include_missing:
			return pnl_results

		loincs_found = [ r['loinc_tt'] for r in pnl_results ]
		loincs_found.extend([ r['loinc_meta'] for r in pnl_results if r['loinc_meta'] not in loincs_found ])
		loincs2consider = set([ tt['loinc'] for tt in self._payload['test_types'] ])
		loincs_missing = loincs2consider - set(loincs_found)
		pnl_results.extend(loincs_missing)
		return pnl_results

#------------------------------------------------------------
def get_test_panels(order_by=None, loincs=None, return_pks=False):
	where_args = {}
	if loincs is None:
		where_parts = ['true']
	else:
		where_parts = ['loincs @> %(loincs)s']
		where_args['loincs'] = list(loincs)

	if order_by is None:
		order_by = u''
	else:
		order_by = ' ORDER BY %s' % order_by

	cmd = (_SQL_get_test_panels % ' AND '.join(where_parts)) + order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': where_args}])
	if return_pks:
		return [ r['pk_test_panel'] for r in rows ]
	return [ cTestPanel(row = {'data': r, 'pk_field': 'pk_test_panel'}) for r in rows ]

#------------------------------------------------------------
def create_test_panel(description=None):

	args = {'desc': description.strip()}
	cmd = """
		INSERT INTO clin.test_panel (description)
		VALUES (gm.nullify_empty_string(%(desc)s))
		RETURNING pk
	"""
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)

	return cTestPanel(aPK_obj = rows[0]['pk'])

#------------------------------------------------------------
def delete_test_panel(pk=None):
	args = {'pk': pk}
	cmd = "DELETE FROM clin.test_panel WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])
	return True

#============================================================
class cMetaTestType(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one meta test type under which actual test types can be aggregated."""

	_cmd_fetch_payload = "SELECT *, xmin FROM clin.meta_test_type WHERE pk = %s"
	_cmds_store_payload = ["""
		UPDATE clin.meta_test_type SET
			abbrev = %(abbrev)s,
			name = %(name)s,
			loinc = gm.nullify_empty_string(%(loinc)s),
			comment = gm.nullify_empty_string(%(comment)s)
		WHERE
			pk = %(pk)s
				AND
			xmin = %(xmin)s
		RETURNING
			xmin
	"""]
	_updatable_fields = [
		'abbrev',
		'name',
		'loinc',
		'comment'
	]
	#--------------------------------------------------------
	def format(self, with_tests=False, patient=None):
		txt = _('Meta (%s=aggregate) test type              [#%s]\n\n') % (gmTools.u_sum, self._payload['pk'])
		txt += _(' Name: %s (%s)\n') % (
			self._payload['abbrev'],
			self._payload['name']
		)
		if self._payload['loinc'] is not None:
			txt += ' LOINC: %s\n' % self._payload['loinc']
		if self._payload['comment'] is not None:
			txt += _(' Comment: %s\n') % self._payload['comment']
		if with_tests:
			ttypes = self.included_test_types
			if len(ttypes) > 0:
				txt += _(' Aggregates the following test types:\n')
			for ttype in ttypes:
				txt += '  - %s (%s)%s%s%s      [#%s]\n' % (
					ttype['name'],
					ttype['abbrev'],
					gmTools.coalesce(ttype['reference_unit'], '', ', %s'),
					gmTools.coalesce(ttype['name_org'], '', ' (%s)'),
					gmTools.coalesce(ttype['loinc'], '', ', LOINC: %s'),
					ttype['pk_test_type']
				)
		if patient is not None:
			txt += '\n'
			most_recent = self.get_most_recent_result(patient = patient)
			if most_recent is not None:
				txt += _(' Most recent (%s): %s%s%s') % (
					most_recent['clin_when'].strftime('%Y %b %d'),
					most_recent['unified_val'],
					gmTools.coalesce(most_recent['val_unit'], '', ' %s'),
					gmTools.coalesce(most_recent['abnormality_indicator'], '', ' (%s)')
				)
			oldest = self.get_oldest_result(patient = patient)
			if oldest is not None:
				txt += '\n'
				txt += _(' Oldest (%s): %s%s%s') % (
					oldest['clin_when'].strftime('%Y %b %d'),
					oldest['unified_val'],
					gmTools.coalesce(oldest['val_unit'], '', ' %s'),
					gmTools.coalesce(oldest['abnormality_indicator'], '', ' (%s)')
				)
		return txt

	#--------------------------------------------------------
	def get_most_recent_result(self, patient=None):
		args = {
			'pat': patient,
			'mttyp': self._payload['pk']
		}
		cmd = """
			SELECT * FROM clin.v_test_results
			WHERE
				pk_patient = %(pat)s
					AND
				pk_meta_test_type = %(mttyp)s
			ORDER BY clin_when DESC
			LIMIT 1"""
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) == 0:
			return None

		return cTestResult(row = {'pk_field': 'pk_test_result', 'data': rows[0]})

	#--------------------------------------------------------
	def get_oldest_result(self, patient=None):
		args = {
			'pat': patient,
			'mttyp': self._payload['pk']
		}
		cmd = """
			SELECT * FROM clin.v_test_results
			WHERE
				pk_patient = %(pat)s
					AND
				pk_meta_test_type = %(mttyp)s
			ORDER BY clin_when
			LIMIT 1"""
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) == 0:
			return None

		return cTestResult(row = {'pk_field': 'pk_test_result', 'data': rows[0]})

	#--------------------------------------------------------
	def get_temporally_closest_result(self, date, pk_patient):

		args = {
			'pat': pk_patient,
			'mtyp': self._payload['pk'],
			'mloinc': self._payload['loinc'],
			'when': date
		}
		SQL = """
			SELECT * FROM clin.v_test_results
			WHERE
				pk_patient = %%(pat)s
					AND
				clin_when %s %%(when)s
					AND
				((pk_meta_test_type = %%(mtyp)s) OR (loinc_meta = %%(mloinc)s))
			ORDER BY clin_when
			LIMIT 1"""

		# get earlier results by meta type
		earlier_result = None
		cmd = SQL % '<'
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) > 0:
			earlier_result = cTestResult(row = {'pk_field': 'pk_test_result', 'data': rows[0]})

		# get later results by meta type ?
		later_result = None
		cmd = SQL % '>'
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) > 0:
			later_result = cTestResult(row = {'pk_field': 'pk_test_result', 'data': rows[0]})

		if earlier_result is None:
			return later_result
		if later_result is None:
			return earlier_result

		earlier_ago = date - earlier_result['clin_when']
		later_ago = later_result['clin_when'] - date
		if earlier_ago < later_ago:
			return earlier_result
		return later_result

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_included_test_types(self):
		cmd = _SQL_get_test_types % 'pk_meta_test_type = %(pk_meta)s'
		args = {'pk_meta': self._payload['pk']}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return [ cMeasurementType(row = {'pk_field': 'pk_test_type', 'data': r}) for r in rows ]

	included_test_types = property(_get_included_test_types)

#------------------------------------------------------------
def create_meta_type(name=None, abbreviation=None, return_existing=False):
	cmd = """
		INSERT INTO clin.meta_test_type (name, abbrev)
		SELECT
			%(name)s,
			%(abbr)s
		WHERE NOT EXISTS (
			SELECT 1 FROM clin.meta_test_type
			WHERE
				name = %(name)s
					AND
				abbrev = %(abbr)s
		)
		 RETURNING *, xmin
	"""
	args = {
		'name': name.strip(),
		'abbr': abbreviation.strip()
	}
	rows = gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}], return_data = True)
	if len(rows) == 0:
		if not return_existing:
			return None
		cmd = "SELECT *, xmin FROM clin.meta_test_type WHERE name = %(name)s and %(abbr)s"
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])

	return cMetaTestType(row = {'pk_field': 'pk', 'data': rows[0]})

#------------------------------------------------------------
def delete_meta_type(meta_type=None):
	cmd = """
		DELETE FROM clin.meta_test_type
		WHERE
			pk = %(pk)s
				AND
			NOT EXISTS (
				SELECT 1 FROM clin.test_type
				WHERE fk_meta_test_type = %(pk)s
			)"""
	args = {'pk': meta_type}
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

#------------------------------------------------------------
def get_meta_test_types(return_pks=False):
	cmd = 'SELECT *, xmin FROM clin.meta_test_type'
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
	if return_pks:
		return [ r['pk'] for r in rows ]
	return [ cMetaTestType(row = {'pk_field': 'pk', 'data': r}) for r in rows ]

#============================================================
_SQL_get_test_types = "SELECT * FROM clin.v_test_types WHERE %s"

class cMeasurementType(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one test result type."""

	_cmd_fetch_payload = _SQL_get_test_types % "pk_test_type = %s"

	_cmds_store_payload = [
		"""UPDATE clin.test_type SET
				abbrev = gm.nullify_empty_string(%(abbrev)s),
				name = gm.nullify_empty_string(%(name)s),
				loinc = gm.nullify_empty_string(%(loinc)s),
				comment = gm.nullify_empty_string(%(comment_type)s),
				reference_unit = gm.nullify_empty_string(%(reference_unit)s),
				fk_test_org = %(pk_test_org)s,
				fk_meta_test_type = %(pk_meta_test_type)s
			WHERE
				pk = %(pk_test_type)s
					AND
				xmin = %(xmin_test_type)s
			RETURNING
				xmin AS xmin_test_type"""
	]

	_updatable_fields = [
		'abbrev',
		'name',
		'loinc',
		'comment_type',
		'reference_unit',
		'pk_test_org',
		'pk_meta_test_type'
	]
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_in_use(self):
		cmd = 'SELECT EXISTS(SELECT 1 FROM clin.test_result WHERE fk_type = %(pk_type)s)'
		args = {'pk_type': self._payload['pk_test_type']}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		return rows[0][0]

	in_use = property(_get_in_use)

	#--------------------------------------------------------
	def get_most_recent_results(self, patient=None, max_no_of_results=1):
		results = get_most_recent_results_for_test_type (
			test_type = self._payload['pk_test_type'],
			max_no_of_results = max_no_of_results,
			patient = patient
		)
		if len(results) > 0:
			return results

		if self._payload['loinc'] is None:
			return []

		return get_most_recent_results_in_loinc_group (
			loincs = list(self._payload['loinc']),
			max_no_of_results = max_no_of_results,
			patient = patient
			# ?
		)

	#--------------------------------------------------------
	def get_oldest_result(self, patient=None):
		result = get_oldest_result (
			test_type = self._payload['pk_test_type'],
			loinc = None,
			patient = patient
		)
		if result is None:
			if self._payload['loinc'] is not None:
				result = get_oldest_result (
					test_type = None,
					loinc = self._payload['loinc'],
					patient = patient
				)
		return result

	#--------------------------------------------------------
	def _get_test_panels(self):
		if self._payload['pk_test_panels'] is None:
			return None

		return [ cTestPanel(aPK_obj = pk) for pk in self._payload['pk_test_panels'] ]

	test_panels = property(_get_test_panels)

	#--------------------------------------------------------
	def get_meta_test_type(self, real_one_only=True):
		if real_one_only is False:
			return cMetaTestType(aPK_obj = self._payload['pk_meta_test_type'])
		if self._payload['is_fake_meta_type']:
			return None
		return cMetaTestType(aPK_obj = self._payload['pk_meta_test_type'])

	meta_test_type = property(get_meta_test_type)

	#--------------------------------------------------------
	def get_temporally_closest_normal_range(self, unit, timestamp=None):
		"""Returns the closest test result which does have normal range information.

		- needs <unit>
		- if <timestamp> is None it will assume now() and thus return the most recent
		"""
		if timestamp is None:
			timestamp = gmDateTime.pydt_now_here()
		cmd = """
SELECT * FROM clin.v_test_results
WHERE
	pk_test_type = %(pk_type)s
		AND
	val_unit = %(unit)s
		AND
	(
		(val_normal_min IS NOT NULL)
			OR
		(val_normal_max IS NOT NULL)
			OR
		(val_normal_range IS NOT NULL)
	)
ORDER BY
	CASE
		WHEN clin_when > %(clin_when)s THEN clin_when - %(clin_when)s
		ELSE %(clin_when)s - clin_when
	END
LIMIT 1"""
		args = {
			'pk_type': self._payload['pk_test_type'],
			'unit': unit,
			'clin_when': timestamp
		}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) == 0:
			return None
		r = rows[0]
		return cTestResult(row = {'pk_field': 'pk_test_result', 'data': r})

	#--------------------------------------------------------
	def get_temporally_closest_target_range(self, unit, patient, timestamp=None):
		"""Returns the closest test result which does have target range information.

		- needs <unit>
		- needs <patient> (as target will be per-patient)
		- if <timestamp> is None it will assume now() and thus return the most recent
		"""
		if timestamp is None:
			timestamp = gmDateTime.pydt_now_here()
		cmd = """
SELECT * FROM clin.v_test_results
WHERE
	pk_test_type = %(pk_type)s
		AND
	val_unit = %(unit)s
		AND
	pk_patient = %(pat)s
		AND
	(
		(val_target_min IS NOT NULL)
			OR
		(val_target_max IS NOT NULL)
			OR
		(val_target_range IS NOT NULL)
	)
ORDER BY
	CASE
		WHEN clin_when > %(clin_when)s THEN clin_when - %(clin_when)s
		ELSE %(clin_when)s - clin_when
	END
LIMIT 1"""
		args = {
			'pk_type': self._payload['pk_test_type'],
			'unit': unit,
			'pat': patient,
			'clin_when': timestamp
		}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) == 0:
			return None
		r = rows[0]
		return cTestResult(row = {'pk_field': 'pk_test_result', 'data': r})

	#--------------------------------------------------------
	def get_temporally_closest_unit(self, timestamp=None):
		"""Returns the unit of the closest test result.

		- if <timestamp> is None it will assume now() and thus return the most recent
		"""
		if timestamp is None:
			timestamp = gmDateTime.pydt_now_here()
		cmd = """
SELECT val_unit FROM clin.v_test_results
WHERE
	pk_test_type = %(pk_type)s
		AND
	val_unit IS NOT NULL
ORDER BY
	CASE
		WHEN clin_when > %(clin_when)s THEN clin_when - %(clin_when)s
		ELSE %(clin_when)s - clin_when
	END
LIMIT 1"""
		args = {
			'pk_type': self._payload['pk_test_type'],
			'clin_when': timestamp
		}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) == 0:
			return None
		return rows[0]['val_unit']

	temporally_closest_unit = property(get_temporally_closest_unit)

	#--------------------------------------------------------
	def format(self, patient=None):
		tt = ''
		tt += _('Test type "%s" (%s)          [#%s]\n') % (
			self._payload['name'],
			self._payload['abbrev'],
			self._payload['pk_test_type']
		)
		tt += '\n'
		tt += gmTools.coalesce(self._payload['loinc'], '', ' LOINC: %s\n')
		tt += gmTools.coalesce(self._payload['reference_unit'], '', _(' Reference unit: %s\n'))
		tt += gmTools.coalesce(self._payload['comment_type'], '', _(' Comment: %s\n'))

		tt += '\n'
		tt += _('Lab details:\n')
		tt += _(' Name: %s\n') % gmTools.coalesce(self._payload['name_org'], '')
		tt += gmTools.coalesce(self._payload['contact_org'], '', _(' Contact: %s\n'))
		tt += gmTools.coalesce(self._payload['comment_org'], '', _(' Comment: %s\n'))

		if self._payload['is_fake_meta_type'] is False:
			tt += '\n'
			tt += _('Aggregated under meta type:\n')
			tt += _(' Name: %s - %s             [#%s]\n') % (
				self._payload['abbrev_meta'],
				self._payload['name_meta'],
				self._payload['pk_meta_test_type']
			)
			tt += gmTools.coalesce(self._payload['loinc_meta'], '', ' LOINC: %s\n')
			tt += gmTools.coalesce(self._payload['comment_meta'], '', _(' Comment: %s\n'))

		panels = self.test_panels
		if panels is not None:
			tt += '\n'
			tt += _('Listed in test panels:\n')
			for panel in panels:
				tt += _(' Panel "%s"             [#%s]\n') % (
					panel['description'],
					panel['pk_test_panel']
				)

		if patient is not None:
			tt += '\n'
			results = self.get_most_recent_results(patient = patient, max_no_of_results = 1)
			if len(results) > 0:
				result = results[0]
				tt += _(' Most recent (%s): %s%s%s') % (
					result['clin_when'].strftime('%Y %b %d'),
					result['unified_val'],
					gmTools.coalesce(result['val_unit'], '', ' %s'),
					gmTools.coalesce(result['abnormality_indicator'], '', ' (%s)')
				)
			result = self.get_oldest_result(patient = patient)
			if result is not None:
				tt += '\n'
				tt += _(' Oldest (%s): %s%s%s') % (
					result['clin_when'].strftime('%Y %b %d'),
					result['unified_val'],
					gmTools.coalesce(result['val_unit'], '', ' %s'),
					gmTools.coalesce(result['abnormality_indicator'], '', ' (%s)')
				)

		return tt

#------------------------------------------------------------
def get_measurement_types(order_by=None, loincs=None, return_pks=False):
	args = {}
	where_parts = []
	if loincs is not None:
		if len(loincs) > 0:
			where_parts.append('loinc = ANY(%(loincs)s)')
			args['loincs'] = loincs
	if len(where_parts) == 0:
		where_parts.append('TRUE')
	WHERE_clause = ' AND '.join(where_parts)
	cmd = (_SQL_get_test_types % WHERE_clause) + gmTools.coalesce(order_by, '', ' ORDER BY %s')
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if return_pks:
		return [ r['pk_test_type'] for r in rows ]
	return [ cMeasurementType(row = {'pk_field': 'pk_test_type', 'data': r}) for r in rows ]

#------------------------------------------------------------
def find_measurement_type(lab=None, abbrev=None, name=None, link_obj=None):

		if (abbrev is None) and (name is None):
			raise ValueError('must have <abbrev> and/or <name> set')

		where_snippets = []

		if lab is None:
			where_snippets.append('pk_test_org IS NULL')
		else:
			try:
				int(lab)
				where_snippets.append('pk_test_org = %(lab)s')
			except (TypeError, ValueError):
				where_snippets.append('pk_test_org = (SELECT pk_test_org FROM clin.v_test_orgs WHERE unit = %(lab)s)')

		if abbrev is not None:
			where_snippets.append('abbrev = %(abbrev)s')

		if name is not None:
			where_snippets.append('name = %(name)s')

		where_clause = ' and '.join(where_snippets)
		cmd = "select * from clin.v_test_types where %s" % where_clause
		args = {'lab': lab, 'abbrev': abbrev, 'name': name}

		rows = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'sql': cmd, 'args': args}])

		if len(rows) == 0:
			return None

		tt = cMeasurementType(row = {'pk_field': 'pk_test_type', 'data': rows[0]})
		return tt

#------------------------------------------------------------
def delete_measurement_type(measurement_type=None):
	cmd = 'delete from clin.test_type where pk = %(pk)s'
	args = {'pk': measurement_type}
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

#------------------------------------------------------------
def create_measurement_type(lab=None, abbrev=None, unit=None, name=None, link_obj=None):
	"""Create or get test type."""

	ttype = find_measurement_type(lab = lab, abbrev = abbrev, name = name, link_obj = link_obj)
	# found ?
	if ttype is not None:
		return ttype

	_log.debug('creating test type [%s:%s:%s:%s]', lab, abbrev, name, unit)

	# not found, so create it
#	if unit is None:
#		_log.error('need <unit> to create test type: %s:%s:%s:%s' % (lab, abbrev, name, unit))
#		raise ValueError('need <unit> to create test type')

	# make query
	cols = []
	val_snippets = []
	vals = {}

	# lab
	if lab is None:
		lab = create_test_org(link_obj = link_obj)['pk_test_org']

	cols.append('fk_test_org')
	try:
		vals['lab'] = int(lab)
		val_snippets.append('%(lab)s')
	except Exception:
		vals['lab'] = lab
		val_snippets.append('(SELECT pk_test_org FROM clin.v_test_orgs WHERE unit = %(lab)s)')

	# code
	cols.append('abbrev')
	val_snippets.append('%(abbrev)s')
	vals['abbrev'] = abbrev

	# unit
	if unit is not None:
		cols.append('reference_unit')
		val_snippets.append('%(unit)s')
		vals['unit'] = unit

	# name
	if name is not None:
		cols.append('name')
		val_snippets.append('%(name)s')
		vals['name'] = name

	col_clause = ', '.join(cols)
	val_clause = ', '.join(val_snippets)
	queries = [
		{'sql': 'insert into clin.test_type (%s) values (%s)' % (col_clause, val_clause), 'args': vals},
		{'sql': "select * from clin.v_test_types where pk_test_type = currval(pg_get_serial_sequence('clin.test_type', 'pk'))"}
	]
	rows = gmPG2.run_rw_queries(link_obj = link_obj, queries = queries, return_data = True)
	ttype = cMeasurementType(row = {'pk_field': 'pk_test_type', 'data': rows[0]})

	return ttype

#============================================================
class cTestResult(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one test result."""

	_cmd_fetch_payload = "select * from clin.v_test_results where pk_test_result = %s"

	_cmds_store_payload = [
		"""UPDATE clin.test_result SET
				clin_when = %(clin_when)s,
				narrative = nullif(trim(%(comment)s), ''),
				val_num = %(val_num)s,
				val_alpha = nullif(trim(%(val_alpha)s), ''),
				val_unit = nullif(trim(%(val_unit)s), ''),
				val_normal_min = %(val_normal_min)s,
				val_normal_max = %(val_normal_max)s,
				val_normal_range = nullif(trim(%(val_normal_range)s), ''),
				val_target_min = %(val_target_min)s,
				val_target_max = %(val_target_max)s,
				val_target_range = nullif(trim(%(val_target_range)s), ''),
				abnormality_indicator = nullif(trim(%(abnormality_indicator)s), ''),
				norm_ref_group = nullif(trim(%(norm_ref_group)s), ''),
				note_test_org = nullif(trim(%(note_test_org)s), ''),
				material = nullif(trim(%(material)s), ''),
				material_detail = nullif(trim(%(material_detail)s), ''),
				status = gm.nullify_empty_string(%(status)s),
				val_grouping = gm.nullify_empty_string(%(val_grouping)s),
				source_data = gm.nullify_empty_string(%(source_data)s),
				fk_intended_reviewer = %(pk_intended_reviewer)s,
				fk_encounter = %(pk_encounter)s,
				fk_episode = %(pk_episode)s,
				fk_type = %(pk_test_type)s,
				fk_request = %(pk_request)s
			WHERE
				pk = %(pk_test_result)s AND
				xmin = %(xmin_test_result)s
			RETURNING
				xmin AS xmin_test_result
		"""
#		, u"""select xmin_test_result from clin.v_test_results where pk_test_result = %(pk_test_result)s"""
	]

	_updatable_fields = [
		'clin_when',
		'comment',
		'val_num',
		'val_alpha',
		'val_unit',
		'val_normal_min',
		'val_normal_max',
		'val_normal_range',
		'val_target_min',
		'val_target_max',
		'val_target_range',
		'abnormality_indicator',
		'norm_ref_group',
		'note_test_org',
		'material',
		'material_detail',
		'status',
		'val_grouping',
		'source_data',
		'pk_intended_reviewer',
		'pk_encounter',
		'pk_episode',
		'pk_test_type',
		'pk_request'
	]

	#--------------------------------------------------------
	def format_concisely(self, date_format='%Y %b %d', with_notes=True):
		range_info = gmTools.coalesce (
			self.formatted_clinical_range,
			self.formatted_normal_range
		)
		review = gmTools.bool2subst (
			self._payload['reviewed'],
			'',
			' ' + gmTools.u_writing_hand,
			' ' + gmTools.u_writing_hand
		)
		txt = '%s %s: %s%s%s%s%s%s' % (
			self._payload['clin_when'].strftime(date_format),
			self._payload['name_tt'],
			self._payload['unified_val'],
			gmTools.coalesce(self._payload['val_unit'], '', ' %s'),
			gmTools.coalesce(self._payload['abnormality_indicator'], '', ' %s'),
			gmTools.coalesce(range_info, '', ' (%s)'),
			gmTools.coalesce(self._payload['status'], '', ' [%s]')[:2],
			review
		)
		if with_notes:
			txt += '\n'
			if self._payload['note_test_org'] is not None:
				txt += ' ' + _('Lab comment: %s\n') % _('\n Lab comment: ').join(self._payload['note_test_org'].split('\n'))
			if self._payload['comment'] is not None:
				txt += ' ' + _('Praxis comment: %s\n') % _('\n Praxis comment: ').join(self._payload['comment'].split('\n'))

		return txt.strip('\n')

	#--------------------------------------------------------
	def __format_evaluation(self) -> str:
		if self._payload['val_num'] is None:
			return ''

		tt = ''
		norm_eval = None
		# 1) normal range
		# lowered ?
		if (self._payload['val_normal_min'] is not None) and (self._payload['val_num'] < self._payload['val_normal_min']):
			try:
				percent = (self._payload['val_num'] * 100) / self._payload['val_normal_min']
			except ZeroDivisionError:
				percent = None
			if percent is not None:
				if percent < 6:
					norm_eval = _('%.1f %% of the normal lower limit') % percent
				else:
					norm_eval = _('%.0f %% of the normal lower limit') % percent
		# raised ?
		if (self._payload['val_normal_max'] is not None) and (self._payload['val_num'] > self._payload['val_normal_max']):
			try:
				x_times = self._payload['val_num'] / self._payload['val_normal_max']
			except ZeroDivisionError:
				x_times = None
			if x_times is not None:
				if x_times < 10:
					norm_eval = _('%.1f times the normal upper limit') % x_times
				else:
					norm_eval = _('%.0f times the normal upper limit') % x_times
		if norm_eval:
			tt += '  = %s\n' % norm_eval
#		#-------------------------------------
#		# this idea was shot down on the list
#		#-------------------------------------
#		# bandwidth of deviation
#		if None not in [self._payload['val_normal_min'], self._payload['val_normal_max']]:
#			normal_width = self._payload['val_normal_max'] - self._payload['val_normal_min']
#			deviation_from_normal_range = None
#			# below ?
#			if self._payload['val_num'] < self._payload['val_normal_min']:
#				deviation_from_normal_range = self._payload['val_normal_min'] - self._payload['val_num']
#			# above ?
#			elif self._payload['val_num'] > self._payload['val_normal_max']:
#				deviation_from_normal_range = self._payload['val_num'] - self._payload['val_normal_max']
#			if deviation_from_normal_range is None:
#				try:
#					times_deviation = deviation_from_normal_range / normal_width
#				except ZeroDivisionError:
#					times_deviation = None
#				if times_deviation is not None:
#					if times_deviation < 10:
#						tt += u'  (%s)\n' % _(u'deviates by %.1f times of the normal range') % times_deviation
#					else:
#						tt += u'  (%s)\n' % _(u'deviates by %.0f times of the normal range') % times_deviation
#		#-------------------------------------
		# 2) clinical target range
		norm_eval = None
		# lowered ?
		if (self._payload['val_target_min'] is not None) and (self._payload['val_num'] < self._payload['val_target_min']):
			try:
				percent = (self._payload['val_num'] * 100) / self._payload['val_target_min']
			except ZeroDivisionError:
				percent = None
			if percent is not None:
				if percent < 6:
					norm_eval = _('%.1f %% of the target lower limit') % percent
				else:
					norm_eval = _('%.0f %% of the target lower limit') % percent
		# raised ?
		if (self._payload['val_target_max'] is not None) and (self._payload['val_num'] > self._payload['val_target_max']):
			try:
				x_times = self._payload['val_num'] / self._payload['val_target_max']
			except ZeroDivisionError:
				x_times = None
			if x_times is not None:
				if x_times < 10:
					norm_eval = _('%.1f times the target upper limit') % x_times
				else:
					norm_eval = _('%.0f times the target upper limit') % x_times
		if norm_eval:
			tt += ' = %s\n' % norm_eval
#		#-------------------------------------
#		# this idea was shot down on the list
#		#-------------------------------------
#		# bandwidth of deviation
#		if None not in [self._payload['val_target_min'], self._payload['val_target_max']]:
#			normal_width = self._payload['val_target_max'] - self._payload['val_target_min']
#			deviation_from_target_range = None
#			# below ?
#			if self._payload['val_num'] < self._payload['val_target_min']:
#				deviation_from_target_range = self._payload['val_target_min'] - self._payload['val_num']
#			# above ?
#			elif self._payload['val_num'] > self._payload['val_target_max']:
#				deviation_from_target_range = self._payload['val_num'] - self._payload['val_target_max']
#			if deviation_from_target_range is None:
#				try:
#					times_deviation = deviation_from_target_range / normal_width
#				except ZeroDivisionError:
#					times_deviation = None
#			if times_deviation is not None:
#				if times_deviation < 10:
#					tt += u'  (%s)\n' % _(u'deviates by %.1f times of the target range') % times_deviation
#				else:
#					tt += u'  (%s)\n' % _(u'deviates by %.0f times of the target range') % times_deviation
		return tt

	#--------------------------------------------------------
	def __format_review(self, date_format:str='%Y %b %d %H:%M') -> str:
		if self._payload['reviewed']:
			review = self._payload['last_reviewed'].strftime(date_format)
		else:
			review = _('not yet')
		tt = _('Signed (%(sig_hand)s): %(reviewed)s\n') % ({
			'sig_hand': gmTools.u_writing_hand,
			'reviewed': review
		})
		tt += ' ' + _('Responsible clinician: %s\n') % gmTools.bool2subst (
			self._payload['you_are_responsible'],
			_('you'),
			self._payload['responsible_reviewer']
		)
		if self._payload['reviewed']:
			tt += ' ' + _('Last reviewer: %(reviewer)s\n') % ({
				'reviewer': gmTools.bool2subst (
					self._payload['review_by_you'],
					_('you'),
					gmTools.coalesce(self._payload['last_reviewer'], '?')
				)
			})
			tt += ' ' + _(' Technically abnormal: %(abnormal)s\n') % ({
				'abnormal': gmTools.bool2subst (
					self._payload['is_technically_abnormal'],
					_('yes'),
					_('no'),
					'?'
				)
			})
			tt += ' ' + _(' Clinically relevant: %(relevant)s\n') % ({
				'relevant': gmTools.bool2subst (
					self._payload['is_clinically_relevant'],
					_('yes'),
					_('no'),
					'?'
				)
			})
		if self._payload['review_comment']:
			tt += ' ' + _(' Comment: %s\n') % self._payload['review_comment'].strip()
		tt += '\n'
		return tt

	#--------------------------------------------------------
	def format(self, with_review=True, with_evaluation=True, with_ranges=True, with_episode=True, with_type_details=True, with_source_data=False, date_format='%Y %b %d %H:%M'):

		# FIXME: add battery, request details

		# header
		tt = _('Result from %s             \n') % self._payload['clin_when'].strftime(date_format)
		# basics
		tt += ' ' + _('Type: "%(name)s" (%(abbr)s)  [#%(pk_type)s]\n') % ({
			'name': self._payload['name_tt'],
			'abbr': self._payload['abbrev_tt'],
			'pk_type': self._payload['pk_test_type']
		})
		if self.is_long_text:
			sso = gmTools.u_superscript_one
		else:
			sso = ''
		tt += ' ' + _('%(sso)sResult: %(val)s%(unit)s%(ind)s  [#%(pk_result)s]\n') % ({
			'sso': sso,
			'val': self._payload['unified_val'],
			'unit': gmTools.coalesce(self._payload['val_unit'], '', ' %s'),
			'ind': gmTools.coalesce(self._payload['abnormality_indicator'], '', ' (%s)'),
			'pk_result': self._payload['pk_test_result']
		})

		if self._payload['status']:
			try:
				stat = HL7_RESULT_STATI[self._payload['status']]
			except KeyError:
				stat = self._payload['status']
			tt += ' ' + _('Status: %s\n') % stat
		if self._payload['val_grouping']:
			tt += ' ' + _('Grouping: %s\n') % self._payload['val_grouping']

		if with_evaluation:
			tt += self.__format_evaluation()

		tmp = ('%s%s' % (
			gmTools.coalesce(self._payload['name_test_org'], ''),
			gmTools.coalesce(self._payload['contact_test_org'], '', ' (%s)'),
		)).strip()
		if tmp != '':
			tt += ' ' + _('Source: %s\n') % tmp
		tt += '\n'
		if self._payload['note_test_org'] is not None:
			tt += ' ' + gmTools.u_superscript_one + _('Lab comment: %s\n') % _('\n Lab comment: ').join(self._payload['note_test_org'].split('\n'))
		if self._payload['comment'] is not None:
			tt += ' ' + gmTools.u_superscript_one + _('Praxis comment: %s\n') % _('\n Praxis comment: ').join(self._payload['comment'].split('\n'))

		if with_ranges:
			tt += gmTools.coalesce(self.formatted_normal_range, '', ' ' + _('Standard normal range: %s\n'))
			tt += gmTools.coalesce(self.formatted_clinical_range, '', ' ' + _('Clinical target range: %s\n'))
			tt += gmTools.coalesce(self._payload['norm_ref_group'], '', ' ' + _('Reference group: %s\n'))

		# metadata
		if with_episode:
			tt += ' ' + _('Episode: %s\n') % self._payload['episode']
			if self._payload['health_issue'] is not None:
				tt += ' ' + _('Issue: %s\n') % self._payload['health_issue']
		if self._payload['material'] is not None:
			tt += ' ' + _('Material: %s\n') % self._payload['material']
		if self._payload['material_detail'] is not None:
			tt += ' ' + _('Details: %s\n') % self._payload['material_detail']
		tt += '\n'

		if with_review:
			tt += self.__format_review(date_format = date_format)

		# type
		if with_type_details:
			has_details = None not in [self._payload['comment_tt'], self._payload['pk_meta_test_type'], self._payload['comment_meta']]
			if has_details:
				tt += _('Test type details:\n')
			if self._payload['comment_tt'] is not None:
				tt += ' ' + _('Type comment: %s\n') % _('\n Type comment:').join(self._payload['comment_tt'].split('\n'))
			if self._payload['pk_meta_test_type'] is not None:
				tt += ' ' + _('Aggregated (%s) under: %s (%s)  [#%s]\n') % (
					gmTools.u_sum,
					self._payload['name_meta'],
					self._payload['abbrev_meta'],
					self._payload['pk_meta_test_type']
				)
			if self._payload['comment_meta'] is not None:
				tt += ' ' + _('Group comment: %s\n') % _('\n Group comment: ').join(self._payload['comment_meta'].split('\n'))
			if has_details:
				tt += '\n'

		if with_source_data:
			if self._payload['source_data'] is not None:
				tt += _('Source data:\n')
				tt += ' ' + self._payload['source_data']
				tt += '\n\n'

		if with_review:
			tt += _('Revisions: %(row_ver)s, last %(mod_when)s by %(mod_by)s.') % ({
				'row_ver': self._payload['row_version'],
				'mod_when': self._payload['modified_when'].strftime(date_format),
				'mod_by': self._payload['modified_by']
			})
		return tt

	#--------------------------------------------------------
	def _get_has_normal_min_or_max(self):
		return (
			self._payload['val_normal_min'] is not None
		) or (
			self._payload['val_normal_max'] is not None
		)

	has_normal_min_or_max = property(_get_has_normal_min_or_max)

	#--------------------------------------------------------
	def _get_normal_min_max(self):
		has_range_info = (
			self._payload['val_normal_min'] is not None
		) or (
			self._payload['val_normal_max'] is not None
		)
		if has_range_info is False:
			return None

		return '%s - %s' % (
			gmTools.coalesce(self._payload['val_normal_min'], '?'),
			gmTools.coalesce(self._payload['val_normal_max'], '?')
		)

	normal_min_max = property(_get_normal_min_max)

	#--------------------------------------------------------
	def _get_formatted_normal_range(self):
		has_numerical_range = (
			self._payload['val_normal_min'] is not None
		) or (
			self._payload['val_normal_max'] is not None
		)
		if has_numerical_range:
			numerical_range = '%s - %s' % (
				gmTools.coalesce(self._payload['val_normal_min'], '?'),
				gmTools.coalesce(self._payload['val_normal_max'], '?')
			)
		else:
			numerical_range = ''
		textual_range = gmTools.coalesce (
			self._payload['val_normal_range'],
			'',
			gmTools.bool2subst (
				has_numerical_range,
				' / %s',
				'%s'
			)
		)
		range_info = '%s%s' % (numerical_range, textual_range)
		if range_info == '':
			return None
		return range_info

	formatted_normal_range = property(_get_formatted_normal_range)

	#--------------------------------------------------------
	def _get_has_clinical_min_or_max(self):
		return (
			self._payload['val_target_min'] is not None
		) or (
			self._payload['val_target_max'] is not None
		)

	has_clinical_min_or_max = property(_get_has_clinical_min_or_max)

	#--------------------------------------------------------
	def _get_clinical_min_max(self):
		has_range_info = (
			self._payload['val_target_min'] is not None
		) or (
			self._payload['val_target_max'] is not None
		)
		if has_range_info is False:
			return None

		return '%s - %s' % (
			gmTools.coalesce(self._payload['val_target_min'], '?'),
			gmTools.coalesce(self._payload['val_target_max'], '?')
		)

	clinical_min_max = property(_get_clinical_min_max)

	#--------------------------------------------------------
	def _get_formatted_clinical_range(self):
		has_numerical_range = (
			self._payload['val_target_min'] is not None
		) or (
			self._payload['val_target_max'] is not None
		)
		if has_numerical_range:
			numerical_range = '%s - %s' % (
				gmTools.coalesce(self._payload['val_target_min'], '?'),
				gmTools.coalesce(self._payload['val_target_max'], '?')
			)
		else:
			numerical_range = ''
		textual_range = gmTools.coalesce (
			self._payload['val_target_range'],
			'',
			gmTools.bool2subst (
				has_numerical_range,
				' / %s',
				'%s'
			)
		)
		range_info = '%s%s' % (numerical_range, textual_range)
		if range_info == '':
			return None
		return range_info

	formatted_clinical_range = property(_get_formatted_clinical_range)

	#--------------------------------------------------------
	def _get_temporally_closest_normal_range(self):
		"""Returns the closest test result which does have normal range information."""
		if self._payload['val_normal_min'] is not None:
			return self
		if self._payload['val_normal_max'] is not None:
			return self
		if self._payload['val_normal_range'] is not None:
			return self
		cmd = """
			SELECT * from clin.v_test_results
			WHERE
				pk_type = %(pk_type)s
					AND
				val_unit = %(unit)s
					AND
				(
					(val_normal_min IS NOT NULL)
						OR
					(val_normal_max IS NOT NULL)
						OR
					(val_normal_range IS NOT NULL)
				)
			ORDER BY
				CASE
					WHEN clin_when > %(clin_when)s THEN clin_when - %(clin_when)s
					ELSE %(clin_when)s - clin_when
				END
			LIMIT 1"""
		args = {
			'pk_type': self._payload['pk_test_type'],
			'unit': self._payload['val_unit'],
			'clin_when': self._payload['clin_when']
		}
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) == 0:
			return None
		return cTestResult(row = {'pk_field': 'pk_test_result', 'data': rows[0]})

	temporally_closest_normal_range = property(_get_temporally_closest_normal_range)

	#--------------------------------------------------------
	def _get_formatted_range(self):

		has_normal_min_or_max = (
			self._payload['val_normal_min'] is not None
		) or (
			self._payload['val_normal_max'] is not None
		)
		if has_normal_min_or_max:
			normal_min_max = '%s - %s' % (
				gmTools.coalesce(self._payload['val_normal_min'], '?'),
				gmTools.coalesce(self._payload['val_normal_max'], '?')
			)

		has_clinical_min_or_max = (
			self._payload['val_target_min'] is not None
		) or (
			self._payload['val_target_max'] is not None
		)
		if has_clinical_min_or_max:
			clinical_min_max = '%s - %s' % (
				gmTools.coalesce(self._payload['val_target_min'], '?'),
				gmTools.coalesce(self._payload['val_target_max'], '?')
			)

		if has_clinical_min_or_max:
			return _('Target: %(clin_min_max)s%(clin_range)s') % ({
				'clin_min_max': clinical_min_max,
				'clin_range': gmTools.coalesce (
					self._payload['val_target_range'],
					'',
					gmTools.bool2subst (
						has_clinical_min_or_max,
						' / %s',
						'%s'
					)
				)
			})

		if has_normal_min_or_max:
			return _('Norm: %(norm_min_max)s%(norm_range)s') % ({
				'norm_min_max': normal_min_max,
				'norm_range': gmTools.coalesce (
					self._payload['val_normal_range'],
					'',
					gmTools.bool2subst (
						has_normal_min_or_max,
						' / %s',
						'%s'
					)
				)
			})

		if self._payload['val_target_range'] is not None:
			return _('Target: %s') % self._payload['val_target_range'],

		if self._payload['val_normal_range'] is not None:
			return _('Norm: %s') % self._payload['val_normal_range']

		return None

	formatted_range = property(_get_formatted_range)

	#--------------------------------------------------------
	def _get_test_type(self):
		return cMeasurementType(aPK_obj = self._payload['pk_test_type'])

	test_type = property(_get_test_type)

	#--------------------------------------------------------
	def _get_is_considered_elevated(self):
		# 1) the user is right (review)
		if self._payload['is_technically_abnormal'] is False:
			return False
		# 2) the lab is right (result.abnormality_indicator)
		indicator = self._payload['abnormality_indicator']
		if indicator is not None:
			indicator = indicator.strip()
			if indicator != '':
				if indicator.strip('+') == '':
					return True
				if indicator.strip('-') == '':
					return False
		# 3) non-numerical value ?
		if self._payload['val_num'] is None:
			return None
		# 4) the target range is right
		target_max = self._payload['val_target_max']
		if target_max is not None:
			if target_max < self._payload['val_num']:
				return True
		# 4) the normal range is right
		normal_max = self._payload['val_normal_max']
		if normal_max is not None:
			if normal_max < self._payload['val_num']:
				return True
		return None

	is_considered_elevated = property(_get_is_considered_elevated)

	#--------------------------------------------------------
	def _get_is_considered_lowered(self):
		# 1) the user is right (review)
		if self._payload['is_technically_abnormal'] is False:
			return False
		# 2) the lab is right (result.abnormality_indicator)
		indicator = self._payload['abnormality_indicator']
		if indicator is not None:
			indicator = indicator.strip()
			if indicator != '':
				if indicator.strip('+') == '':
					return False
				if indicator.strip('-') == '':
					return True
		# 3) non-numerical value ?
		if self._payload['val_num'] is None:
			return None
		# 4) the target range is right
		target_min = self._payload['val_target_min']
		if target_min is not None:
			if target_min > self._payload['val_num']:
				return True
		# 4) the normal range is right
		normal_min = self._payload['val_normal_min']
		if normal_min is not None:
			if normal_min > self._payload['val_num']:
				return True
		return None

	is_considered_lowered = property(_get_is_considered_lowered)

	#--------------------------------------------------------
	def _get_is_considered_abnormal(self):
		if self.is_considered_lowered is True:
			return True
		if self.is_considered_elevated is True:
			return True
		if (self.is_considered_lowered is False) and (self.is_considered_elevated is False):
			return False
		return self._payload['is_technically_abnormal']

	is_considered_abnormal = property(_get_is_considered_abnormal)

	#--------------------------------------------------------
	def _set_reference_range(self, ref_range):
		"""Parse reference range from string.

			Note: does NOT save the result.
		"""
		ref_range = ref_range.strip().replace(' ', '')

		is_range = regex.match(r'-{0,1}\d+[.,]{0,1}\d*--{0,1}\d+[.,]{0,1}\d*$', ref_range, regex.UNICODE)
		if is_range is not None:
			min_val = regex.match(r'-{0,1}\d+[.,]{0,1}\d*-', ref_range, regex.UNICODE).group(0).rstrip('-')
			success, min_val = gmTools.input2decimal(min_val)
			max_val = (regex.search(r'--{0,1}\d+[.,]{0,1}\d*$', ref_range, regex.UNICODE).group(0))[1:]
			success, max_val = gmTools.input2decimal(max_val)
			self['val_normal_min'] = min_val
			self['val_normal_max'] = max_val
			return

		if ref_range.startswith('<'):
			is_range = regex.match(r'<\d+[.,]{0,1}\d*$', ref_range, regex.UNICODE)
			if is_range is not None:
				max_val = ref_range[1:]
				success, max_val = gmTools.input2decimal(max_val)
				self['val_normal_min'] = 0
				self['val_normal_max'] = max_val
				return

		if ref_range.startswith('<-'):
			is_range = regex.match(r'<-\d+[.,]{0,1}\d*$', ref_range, regex.UNICODE)
			if is_range is not None:
				max_val = ref_range[1:]
				success, max_val = gmTools.input2decimal(max_val)
				self['val_normal_min'] = None
				self['val_normal_max'] = max_val
				return

		if ref_range.startswith('>'):
			is_range = regex.match(r'>\d+[.,]{0,1}\d*$', ref_range, regex.UNICODE)
			if is_range is not None:
				min_val = ref_range[1:]
				success, min_val = gmTools.input2decimal(min_val)
				self['val_normal_min'] = min_val
				self['val_normal_max'] = None
				return

		if ref_range.startswith('>-'):
			is_range = regex.match(r'>-\d+[.,]{0,1}\d*$', ref_range, regex.UNICODE)
			if is_range is not None:
				min_val = ref_range[1:]
				success, min_val = gmTools.input2decimal(min_val)
				self['val_normal_min'] = min_val
				self['val_normal_max'] = 0
				return

		self['val_normal_range'] = ref_range
		return

	reference_range = property(lambda x:x, _set_reference_range)

	#--------------------------------------------------------
	def _get_formatted_abnormality_indicator(self):
		# 1) the user is right
		if self._payload['is_technically_abnormal'] is False:
			return ''
		# 2) the lab is right (result.abnormality_indicator)
		indicator = self._payload['abnormality_indicator']
		if indicator is not None:
			indicator = indicator.strip()
			if indicator != '':
				return indicator
		# 3) non-numerical value ? then we can't know more
		if self._payload['val_num'] is None:
			return None
		# 4) the target range is right
		target_min = self._payload['val_target_min']
		if target_min is not None:
			if target_min > self._payload['val_num']:
				return '-'
		target_max = self._payload['val_target_max']
		if target_max is not None:
			if target_max < self._payload['val_num']:
				return '+'
		# 4) the normal range is right
		normal_min = self._payload['val_normal_min']
		if normal_min is not None:
			if normal_min > self._payload['val_num']:
				return '-'
		normal_max = self._payload['val_normal_max']
		if normal_max is not None:
			if normal_max < self._payload['val_num']:
				return '+'
		# reviewed, abnormal, but no indicator available
		if self._payload['is_technically_abnormal'] is True:
			return gmTools.u_plus_minus

		return None

	formatted_abnormality_indicator = property(_get_formatted_abnormality_indicator)

	#--------------------------------------------------------
	def _get_is_long_text(self):
		if self._payload['val_alpha'] is None:
			return False
		lines = gmTools.strip_empty_lines(text = self._payload['val_alpha'], eol = '\n', return_list = True)
		if len(lines) > 4:
			return True
		return False

	is_long_text = property(_get_is_long_text)

	#--------------------------------------------------------
	def _get_estimate_numeric_value_from_alpha(self):
		if self._payload['val_alpha'] is None:
			return None
		val = self._payload['val_alpha'].lstrip()
		if val[0] == '<':
			factor = decimal.Decimal(0.5)
			val = val[1:]
		elif val[0] == '>':
			factor = 2
			val = val[1:]
		else:
			return None
		success, val = gmTools.input2decimal(initial = val)
		if not success:
			return None
		return val * factor

	estimate_numeric_value_from_alpha = property(_get_estimate_numeric_value_from_alpha)

	#--------------------------------------------------------
	def set_review(self, technically_abnormal=None, clinically_relevant=None, comment=None, make_me_responsible=False):

		# FIXME: this is not concurrency safe
		if self._payload['reviewed']:
			self.__change_existing_review (
				technically_abnormal = technically_abnormal,
				clinically_relevant = clinically_relevant,
				comment = comment
			)
		else:
			# do not sign off unreviewed results if
			# NOTHING AT ALL is known about them
			if technically_abnormal is None:
				if clinically_relevant is None:
					comment = gmTools.none_if(comment, '', strip_string = True)
					if comment is None:
						if make_me_responsible is False:
							return True
			self.__set_new_review (
				technically_abnormal = technically_abnormal,
				clinically_relevant = clinically_relevant,
				comment = comment
			)

		if make_me_responsible is True:
			cmd = "SELECT pk FROM dem.staff WHERE db_user = current_user"
			rows = gmPG2.run_ro_queries(queries = [{'sql': cmd}])
			self['pk_intended_reviewer'] = rows[0][0]
			self.save_payload()
			return

		self.refetch_payload()

	#--------------------------------------------------------
	def get_adjacent_results(self, desired_earlier_results=1, desired_later_results=1, max_offset=None):

		if desired_earlier_results < 1:
			raise ValueError('<desired_earlier_results> must be > 0')

		if desired_later_results < 1:
			raise ValueError('<desired_later_results> must be > 0')

		args = {
			'pat': self._payload['pk_patient'],
			'ttyp': self._payload['pk_test_type'],
			'tloinc': self._payload['loinc_tt'],
			'mtyp': self._payload['pk_meta_test_type'],
			'mloinc': self._payload['loinc_meta'],
			'when': self._payload['clin_when'],
			'offset': max_offset
		}
		WHERE = '((pk_test_type = %(ttyp)s) OR (loinc_tt = %(tloinc)s))'
		WHERE_meta = '((pk_meta_test_type = %(mtyp)s) OR (loinc_meta = %(mloinc)s))'
		if max_offset is not None:
			WHERE = WHERE + ' AND (clin_when BETWEEN (%(when)s - %(offset)s) AND (%(when)s + %(offset)s))'
			WHERE_meta = WHERE_meta + ' AND (clin_when BETWEEN (%(when)s - %(offset)s) AND (%(when)s + %(offset)s))'

		SQL = """
			SELECT * FROM clin.v_test_results
			WHERE
				pk_patient = %%(pat)s
					AND
				clin_when %s %%(when)s
					AND
				%s
			ORDER BY clin_when
			LIMIT %s"""

		# get earlier results
		earlier_results = []
		# by type
		cmd = SQL % ('<', WHERE, desired_earlier_results)
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) > 0:
			earlier_results.extend([ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ])
		# by meta type ?
		missing_results = desired_earlier_results - len(earlier_results)
		if  missing_results > 0:
			cmd = SQL % ('<', WHERE_meta, missing_results)
			rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
			if len(rows) > 0:
				earlier_results.extend([ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ])

		# get later results
		later_results = []
		# by type
		cmd = SQL % ('>', WHERE, desired_later_results)
		rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
		if len(rows) > 0:
			later_results.extend([ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ])
		# by meta type ?
		missing_results = desired_later_results - len(later_results)
		if  missing_results > 0:
			cmd = SQL % ('>', WHERE_meta, missing_results)
			rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
			if len(rows) > 0:
				later_results.extend([ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ])

		return earlier_results, later_results

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __set_new_review(self, technically_abnormal=None, clinically_relevant=None, comment=None):
		"""Add a review to a row.

			- if technically abnormal is not provided/None it will be set
			  to True if the lab's indicator has a meaningful value
			- if clinically relevant is not provided/None it is set to
			  whatever technically abnormal is
		"""
		if technically_abnormal is None:
			technically_abnormal = False
			if self._payload['abnormality_indicator'] is not None:
				if self._payload['abnormality_indicator'].strip() != '':
					technically_abnormal = True

		if clinically_relevant is None:
			clinically_relevant = technically_abnormal

		cmd = """
INSERT INTO clin.reviewed_test_results (
	fk_reviewed_row,
	is_technically_abnormal,
	clinically_relevant,
	comment
) VALUES (
	%(pk)s,
	%(abnormal)s,
	%(relevant)s,
	gm.nullify_empty_string(%(cmt)s)
)"""
		args = {
			'pk': self._payload['pk_test_result'],
			'abnormal': technically_abnormal,
			'relevant': clinically_relevant,
			'cmt': comment
		}

		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

	#--------------------------------------------------------
	def __change_existing_review(self, technically_abnormal=None, clinically_relevant=None, comment=None):
		"""Change a review on a row.

			- if technically abnormal/clinically relevant are
			  None they are not set
		"""
		args = {
			'pk_result': self._payload['pk_test_result'],
			'abnormal': technically_abnormal,
			'relevant': clinically_relevant,
			'cmt': comment
		}

		set_parts = [
			'fk_reviewer = (SELECT pk FROM dem.staff WHERE db_user = current_user)',
			'comment = gm.nullify_empty_string(%(cmt)s)'
		]

		if technically_abnormal is not None:
			set_parts.append('is_technically_abnormal = %(abnormal)s')

		if clinically_relevant is not None:
			set_parts.append('clinically_relevant = %(relevant)s')

		cmd = """
UPDATE clin.reviewed_test_results SET
	%s
WHERE
	fk_reviewed_row = %%(pk_result)s
""" % ',\n	'.join(set_parts)

		gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': args}])

#------------------------------------------------------------
def get_test_results(pk_patient=None, encounters=None, episodes=None, order_by=None, return_pks=False):

	where_parts = []

	if pk_patient is not None:
		where_parts.append('pk_patient = %(pat)s')
		args = {'pat': pk_patient}
#	if tests is not None:
#		where_parts.append(u'pk_test_type = ANY(%(tests)s)')
#		args['tests'] = tests
	if encounters is not None:
		where_parts.append('pk_encounter = ANY(%(encs)s)')
		args['encs'] = encounters
	if episodes is not None:
		where_parts.append('pk_episode = ANY(%(epis)s)')
		args['epis'] = episodes
	if order_by is None:
		order_by = ''
	else:
		order_by = 'ORDER BY %s' % order_by

	cmd = """
		SELECT * FROM clin.v_test_results
		WHERE %s
		%s
	""" % (
		' AND '.join(where_parts),
		order_by
	)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if return_pks:
		return [ r['pk_test_result'] for r in rows ]
	tests = [ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ]
	return tests

#------------------------------------------------------------
def get_most_recent_results_for_panel(pk_patient=None, pk_panel=None, order_by=None, group_by_meta_type=False):

	if order_by is None:
		order_by = ''
	else:
		order_by = 'ORDER BY %s' % order_by

	args = {
		'pat': pk_patient,
		'pk_pnl': pk_panel
	}

	if group_by_meta_type:
		# return most recent results in panel grouped by
		# meta test type if any, non-grouped results are
		# returned ungrouped :-)
		cmd = """
			SELECT c_vtr.*
			FROM (
				-- max(clin_when) per test_type-in-panel for patient
				SELECT
					pk_meta_test_type,
					MAX(clin_when) AS max_clin_when
				FROM clin.v_test_results
				WHERE
					pk_patient = %(pat)s
						AND
					pk_meta_test_type IS DISTINCT FROM NULL
						AND
					pk_test_type IN (
						(SELECT c_vtt4tp.pk_test_type FROM clin.v_test_types4test_panel c_vtt4tp WHERE c_vtt4tp.pk_test_panel = %(pk_pnl)s)
					)
				GROUP BY pk_meta_test_type
			) AS latest_results
				INNER JOIN clin.v_test_results c_vtr ON
					c_vtr.pk_meta_test_type = latest_results.pk_meta_test_type
						AND
					c_vtr.clin_when = latest_results.max_clin_when

		UNION ALL

		SELECT c_vtr.*
		FROM (
			-- max(clin_when) per test_type-in-panel for patient
			SELECT
				pk_test_type,
				MAX(clin_when) AS max_clin_when
			FROM clin.v_test_results
			WHERE
				pk_patient = %(pat)s
					AND
				pk_meta_test_type IS NULL
					AND
				pk_test_type IN (
					(SELECT c_vtt4tp.pk_test_type FROM clin.v_test_types4test_panel c_vtt4tp WHERE c_vtt4tp.pk_test_panel = %(pk_pnl)s)
				)
			GROUP BY pk_test_type
		) AS latest_results
			INNER JOIN clin.v_test_results c_vtr ON
				c_vtr.pk_test_type = latest_results.pk_test_type
					AND
				c_vtr.clin_when = latest_results.max_clin_when
		"""
	else:
		# return most recent results in panel regardless of whether
		# distinct test types in this panel are grouped under the
		# same meta test type
		cmd = """
			SELECT c_vtr.*
			FROM (
				-- max(clin_when) per test_type-in-panel for patient
				SELECT
					pk_test_type,
					MAX(clin_when) AS max_clin_when
				FROM clin.v_test_results
				WHERE
					pk_patient = %(pat)s
						AND
					pk_test_type IN (
						(SELECT c_vtt4tp.pk_test_type FROM clin.v_test_types4test_panel c_vtt4tp WHERE c_vtt4tp.pk_test_panel = %(pk_pnl)s)
					)
				GROUP BY pk_test_type
			) AS latest_results
				-- this INNER join makes certain we do not expand
				-- the row selection beyond the patient's rows
				-- which we constrained to inside the SELECT
				-- producing "latest_results"
				INNER JOIN clin.v_test_results c_vtr ON
					c_vtr.pk_test_type = latest_results.pk_test_type
						AND
					c_vtr.clin_when = latest_results.max_clin_when
			"""
	cmd += order_by
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return [ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ]

#------------------------------------------------------------
def get_result_at_timestamp(timestamp=None, test_type=None, loinc=None, tolerance_interval=None, patient=None):

	if None not in [test_type, loinc]:
		raise ValueError('either <test_type> or <loinc> must be None')

	args = {
		'pat': patient,
		'ttyp': test_type,
		'loinc': loinc,
		'ts': timestamp,
		'intv': tolerance_interval
	}

	where_parts = ['pk_patient = %(pat)s']
	if test_type is not None:
		where_parts.append('pk_test_type = %(ttyp)s')		# consider: pk_meta_test_type = %(pkmtt)s / self._payload['pk_meta_test_type']
	elif loinc is not None:
		where_parts.append('((loinc_tt = ANY(%(loinc)s)) OR (loinc_meta = ANY(%(loinc)s)))')
		args['loinc'] = loinc

	if tolerance_interval is None:
		where_parts.append('clin_when = %(ts)s')
	else:
		where_parts.append('clin_when between (%(ts)s - %(intv)s::interval) AND (%(ts)s + %(intv)s::interval)')

	cmd = """
		SELECT * FROM clin.v_test_results
		WHERE
			%s
		ORDER BY
			abs(extract(epoch from age(clin_when, %%(ts)s)))
		LIMIT 1""" % ' AND '.join(where_parts)

	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(rows) == 0:
		return None

	return cTestResult(row = {'pk_field': 'pk_test_result', 'data': rows[0]})

#------------------------------------------------------------
def get_results_for_day(timestamp=None, patient=None, order_by=None):

	args = {
		'pat': patient,
		'ts': timestamp
	}

	where_parts = [
		'pk_patient = %(pat)s',
		"date_trunc('day'::text, clin_when) = date_trunc('day'::text, %(ts)s)"
	]

	cmd = """
		SELECT * FROM clin.v_test_results
		WHERE
			%s
		ORDER BY
			val_grouping,
			abbrev_tt,
			clin_when DESC
	""" % ' AND '.join(where_parts)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return [ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ]

#------------------------------------------------------------
def get_results_for_issue(pk_health_issue=None, order_by=None):
	args = {'pk_issue': pk_health_issue}
	where_parts = ['pk_health_issue = %(pk_issue)s']
	cmd = """
		SELECT * FROM clin.v_test_results
		WHERE %s
		ORDER BY
			val_grouping,
			abbrev_tt,
			clin_when DESC
	""" % ' AND '.join(where_parts)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return [ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ]

#------------------------------------------------------------
def get_results_for_episode(pk_episode=None):
	args = {'pk_epi': pk_episode}
	where_parts = ['pk_episode = %(pk_epi)s']
	cmd = """
		SELECT * FROM clin.v_test_results
		WHERE %s
		ORDER BY
			val_grouping,
			abbrev_tt,
			clin_when DESC
	""" % ' AND '.join(where_parts)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return [ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ]

#------------------------------------------------------------
def get_most_recent_results_in_loinc_group(loincs=None, max_no_of_results=1, patient=None, max_age=None, consider_indirect_matches=False):
	"""Get N most recent results *among* a list of tests selected by LOINC.

		1) get test types with LOINC (or meta type LOINC) in the group of <loincs>
		2) from these get the test results for <patient> within the given <max_age>
		3) from these return "the N=<max_no_of_results> most recent ones" or "None"

		<loinc> must be a list or tuple or set, NOT a single string
		<max_age> must be a string holding a PG interval or else a pydt interval
	"""
	assert (max_no_of_results > 0), '<max_no_of_results> must be >0'

	args = {'pat': patient, 'loincs': loincs}
	if max_age is None:
		max_age_cond = ''
	else:
		max_age_cond = 'AND clin_when > (now() - %(max_age)s::interval)'
		args['max_age'] = max_age
	cmd = """
		SELECT * FROM (
			SELECT DISTINCT ON (pk_test_result) *
			FROM clin.v_test_results
			WHERE
				pk_patient = %%(pat)s
					AND
				unified_loinc = ANY(%%(loincs)s)
				%s
		) AS distinct_results
		ORDER BY
			clin_when DESC
		LIMIT %s""" % (
		max_age_cond,
		max_no_of_results
	)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(rows) > 0:
		return [ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ]

	if not consider_indirect_matches:
		return []

	cmd = """
	-- get the test results
	SELECT * FROM clin.v_test_results c_vtr
	WHERE
		-- for this <patient>
		pk_patient = %%(pat)s
			AND
		-- not having *any* LOINC (if the result did have a LOINC and had not been caught by the by-LOINC search it does not apply)
		unified_loinc IS NULL
			AND
		-- with these meta test types (= results for the explicit equivalance group)
		c_vtr.pk_meta_test_type IN (
			-- get the meta test types for those types
			SELECT pk_meta_test_type
			FROM clin.v_test_types
			WHERE
				pk_meta_test_type IS NOT NULL
					AND
				(-- retrieve test types which have .LOINC in <loincs>
					(loinc IN %%(loincs)s)
						OR
					(loinc_meta IN  %%(loincs)s)
				)
					AND
				-- but no result for <patient>
				pk_test_type NOT IN (
					select pk_test_type from clin.v_test_results WHERE pk_patient = %%(pat)s
				) %s
		)
	-- return the N most resent result
	ORDER BY clin_when DESC
	LIMIT %s
	""" % (
		max_age_cond,
		max_no_of_results
	)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return [ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ]

#------------------------------------------------------------
def get_most_recent_results_for_test_type(test_type=None, max_no_of_results=1, patient=None):
	"""Get N most recent results for *one* defined test type."""

	assert (test_type is not None), '<test_type> must not be None'
	assert (max_no_of_results > 0), '<max_no_of_results> must be > 0'

	args = {'pat': patient, 'ttyp': test_type}
	where_parts = ['pk_patient = %(pat)s']
	where_parts.append('pk_test_type = %(ttyp)s')		# ?consider: pk_meta_test_type = %(pkmtt)s / self._payload['pk_meta_test_type']
	cmd = """
		SELECT * FROM clin.v_test_results
		WHERE
			%s
		ORDER BY clin_when DESC
		LIMIT %s""" % (
			' AND '.join(where_parts),
			max_no_of_results
		)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return [ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ]

#------------------------------------------------------------
_SQL_most_recent_result_for_test_types = """
-- return the one most recent result for each of a list of test types
-- without regard to whether they belong to a meta test type
SELECT * FROM (
	SELECT
		*,
		MAX(clin_when) OVER relevant_tests AS max_clin_when
	FROM
		clin.v_test_results
	WHERE
		%s
	WINDOW relevant_tests AS (PARTITION BY pk_patient, pk_test_type)
) AS windowed_tests
WHERE
	clin_when = max_clin_when
%s
"""

_SQL_most_recent_result_for_test_types_without_meta_type = """
-- return the one most recent result for each of a list of test types
-- none of which may belong to a meta test type
SELECT * FROM (
	SELECT
		*,
		MAX(clin_when) OVER relevant_tests AS max_clin_when
	FROM
		clin.v_test_results
	WHERE
		pk_meta_test_type IS NULL
			AND
		%s
	WINDOW relevant_tests AS (PARTITION BY pk_patient, pk_test_type)
) AS windowed_tests
WHERE
	clin_when = max_clin_when
"""

_SQL_most_recent_result_for_test_types_by_meta_type = """
-- return the one most recent result for each of a list of meta test types
-- derived from a list of test types
SELECT * FROM (
	SELECT
		*,
		MAX(clin_when) OVER relevant_tests AS max_clin_when
	FROM
		clin.v_test_results
	WHERE
		pk_meta_test_type IS NOT NULL
			AND
		%s
	WINDOW relevant_tests AS (PARTITION BY pk_patient, pk_meta_test_type)
) AS windowed_tests
WHERE
	clin_when = max_clin_when
"""

def get_most_recent_result_for_test_types(pk_test_types=None, pk_patient=None, return_pks=False, consider_meta_type=False, order_by=None):
	"""Return the one most recent result for *each* of a list of test types.

		If <pk_test_types> is not given, most recent results for *each*
		test type the patient has any results for is returned.
	"""
	where_parts = ['pk_patient = %(pat)s']
	args = {'pat': pk_patient}

	if pk_test_types is not None:
		where_parts.append('pk_test_type = ANY(%(ttyps)s)')
		args['ttyps'] = pk_test_types

	order_by = 'ORDER BY clin_when DESC' if order_by is None else 'ORDER BY %s' % order_by

	if consider_meta_type:
		cmd = 'SELECT * FROM ((%s) UNION ALL (%s)) AS result_union %s' % (
			_SQL_most_recent_result_for_test_types_without_meta_type % ' AND '.join(where_parts),
			_SQL_most_recent_result_for_test_types_by_meta_type % ' AND '.join(where_parts),
			order_by
		)
	else:
		cmd = _SQL_most_recent_result_for_test_types % (
			' AND '.join(where_parts),
			order_by
		)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if return_pks:
		return [ r['pk_test_result'] for r in rows ]

	return [ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ]

#------------------------------------------------------------
def get_most_recent_results_for_patient(no_of_results=1, patient=None):
	"""Get N most recent results for a given patient."""

	if no_of_results < 1:
		raise ValueError('<no_of_results> must be > 0')

	args = {'pat': patient}
	cmd = """
		SELECT * FROM clin.v_test_results
		WHERE
			pk_patient = %%(pat)s
		ORDER BY clin_when DESC
		LIMIT %s""" % no_of_results
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	return [ cTestResult(row = {'pk_field': 'pk_test_result', 'data': r}) for r in rows ]

#------------------------------------------------------------
def get_oldest_result(test_type=None, loinc=None, patient=None):

	if None not in [test_type, loinc]:
		raise ValueError('either <test_type> or <loinc> must be None')

	args = {
		'pat': patient,
		'ttyp': test_type,
		'loinc': loinc
	}

	where_parts = ['pk_patient = %(pat)s']
	if test_type is not None:
		where_parts.append('pk_test_type = %(ttyp)s')		# consider: pk_meta_test_type = %(pkmtt)s / self._payload['pk_meta_test_type']
	elif loinc is not None:
		where_parts.append('((loinc_tt = ANY(%(loinc)s)) OR (loinc_meta = ANY(%(loinc)s)))')
		args['loinc'] = loinc

	cmd = """
		SELECT * FROM clin.v_test_results
		WHERE
			%s
		ORDER BY clin_when
		LIMIT 1""" % ' AND '.join(where_parts)
	rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': args}])
	if len(rows) == 0:
		return None

	return cTestResult(row = {'pk_field': 'pk_test_result', 'data': rows[0]})

#------------------------------------------------------------
def delete_test_result(result=None):
	try:
		pk = int(result)
	except (TypeError, AttributeError):
		pk = result['pk_test_result']

	cmd = 'DELETE FROM clin.test_result WHERE pk = %(pk)s'
	gmPG2.run_rw_queries(queries = [{'sql': cmd, 'args': {'pk': pk}}])

#------------------------------------------------------------
def create_test_result(encounter=None, episode=None, type=None, intended_reviewer=None, val_num=None, val_alpha=None, unit=None, link_obj=None):

	cmd1 = """
		INSERT INTO clin.test_result (
			fk_encounter,
			fk_episode,
			fk_type,
			fk_intended_reviewer,
			val_num,
			val_alpha,
			val_unit
		) VALUES (
			%(enc)s,
			%(epi)s,
			%(type)s,
			%(rev)s,
			%(v_num)s,
			%(v_alpha)s,
			%(unit)s
		)
	"""
	cmd2 = "SELECT * from clin.v_test_results WHERE pk_test_result = currval(pg_get_serial_sequence('clin.test_result', 'pk'))"
	args = {
		'enc': encounter,
		'epi': episode,
		'type': type,
		'rev': intended_reviewer,
		'v_num': val_num,
		'v_alpha': val_alpha,
		'unit': unit
	}
	rows = gmPG2.run_rw_queries (
		link_obj = link_obj,
		queries = [
			{'sql': cmd1, 'args': args},
			{'sql': cmd2}
		],
		return_data = True
	)
	tr = cTestResult(row = {
		'pk_field': 'pk_test_result',
		'data': rows[0]
	})
	return tr

#------------------------------------------------------------
def generate_failsafe_test_results_entries(pk_patient:int=None, test_results:list[cTestResult]=None, max_width:int=80) -> list[str]:
	if not test_results:
		if pk_patient:
			test_results = get_test_results(pk_patient = 12, order_by = 'unified_abbrev, clin_when DESC')
	if not test_results:
		return []

	prev_abbrev = None
	lines = []
	for tr in test_results:
		abbrev = tr['unified_abbrev']
		if abbrev != prev_abbrev:
			lines.append('')
			lines.append('%s - %s' % (abbrev, tr['unified_name']))
			prev_abbrev = abbrev
		line = '  %s: %s %s%s%s' % (
			tr['clin_when'].strftime('%Y %b %d %H:%m'),
			tr['unified_val'],
			tr['val_unit'],
			gmTools.bool2subst(tr.is_considered_abnormal, ' !', '', ''),
			gmTools.coalesce(tr.formatted_range, '', ' (%s)')
		)
		lines.append(gmTools.shorten_text(line, max_width))
		if tr['note_test_org']:
			cmt = _('  Lab: %s') % tr['note_test_org'].replace('\n', ' // ')
			lines.append(gmTools.shorten_text(cmt, max_width))
		if tr['comment']:
			cmt = _('  Praxis: %s') % tr['comment'].replace('\n', ' // ')
			lines.append(gmTools.shorten_text(cmt, max_width))
	return lines

#------------------------------------------------------------
def format_test_results(results=None, output_format='latex'):

	_log.debug('formatting test results into [%s]', output_format)

	if output_format == 'latex':
		return __format_test_results_latex(results = results)

	msg = _('unknown test results output format [%s]') % output_format
	_log.error(msg)
	return msg

#------------------------------------------------------------
def __tests2latex_minipage(results=None, width='1.5cm', show_time=False, show_range=True):

	if len(results) == 0:
		return '\\begin{minipage}{%s} \\end{minipage}' % width

	lines = []
	for t in results:

		tmp = ''

		if show_time:
			tmp += '{\\tiny (%s)} ' % t['clin_when'].strftime('%H:%M')

		tmp += '%.8s' % t['unified_val']

		lines.append(tmp)
		tmp = ''

		if show_range:
			has_range = (
				t['unified_target_range'] is not None
					or
				t['unified_target_min'] is not None
					or
				t['unified_target_max'] is not None
			)
			if has_range:
				if t['unified_target_range'] is not None:
					tmp += '{\\tiny %s}' % t['unified_target_range']
				else:
					tmp += '{\\tiny %s%s}' % (
						gmTools.coalesce(t['unified_target_min'], '- ', '%s - '),
						gmTools.coalesce(t['unified_target_max'], '', '%s')
					)
				lines.append(tmp)

	return '\\begin{minipage}{%s} \\begin{flushright} %s \\end{flushright} \\end{minipage}' % (width, ' \\\\ '.join(lines))

#------------------------------------------------------------
def __tests2latex_cell(results=None, show_time=False, show_range=True):

	if len(results) == 0:
		return ''

	lines = []
	for t in results:

		tmp = ''

		if show_time:
			tmp += '\\tiny %s ' % t['clin_when'].strftime('%H:%M')

		tmp += '\\normalsize %.8s' % t['unified_val']

		lines.append(tmp)
		tmp = '\\tiny %s' % gmTools.coalesce(t['val_unit'], '', '%s ')

		if not show_range:
			lines.append(tmp)
			continue

		has_range = (
			t['unified_target_range'] is not None
				or
			t['unified_target_min'] is not None
				or
			t['unified_target_max'] is not None
		)

		if not has_range:
			lines.append(tmp)
			continue

		if t['unified_target_range'] is not None:
			tmp += '[%s]' % t['unified_target_range']
		else:
			tmp += '[%s%s]' % (
				gmTools.coalesce(t['unified_target_min'], '--', '%s--'),
				gmTools.coalesce(t['unified_target_max'], '', '%s')
			)
		lines.append(tmp)

	return ' \\\\ '.join(lines)

#------------------------------------------------------------
def __format_test_results_latex(results=None):

	if len(results) == 0:
		return '\\noindent %s' % _('No test results to format.')

	# discover the columns and rows
	dates = {}
	tests = {}
	grid = {}
	for result in results:
#		row_label = u'%s \\ \\tiny (%s)}' % (result['unified_abbrev'], result['unified_name'])
		row_label = result['unified_abbrev']
		tests[row_label] = None
		col_label = '{\\scriptsize %s}' % result['clin_when'].strftime('%Y-%m-%d')
		dates[col_label] = None
		try:
			grid[row_label]
		except KeyError:
			grid[row_label] = {}
		try:
			grid[row_label][col_label].append(result)
		except KeyError:
			grid[row_label][col_label] = [result]

	col_labels = sorted(dates, reverse = True)
	del dates
	row_labels = sorted(tests)
	del tests

	col_def = len(col_labels) * '>{\\raggedleft}p{1.7cm}|'

	# format them
	tex = """\\noindent %s

\\noindent \\begin{tabular}{|l|%s}
\\hline
 & %s \\tabularnewline
\\hline

%%s \\tabularnewline

\\hline

\\end{tabular}""" % (
		_('Test results'),
		col_def,
		' & '.join(col_labels)
	)

	rows = []

	# loop over rows
	for rl in row_labels:
		cells = [rl]
		# loop over cols per row
		for cl in col_labels:
			try:
				# get tests for this (row/col) position
				tests = grid[rl][cl]
			except KeyError:
				# none there, so insert empty cell
				cells.append(' ')
				continue

			cells.append (
				__tests2latex_cell (
					results = tests,
					show_time = (len(tests) > 1),
					show_range = True
				)
			)

		rows.append(' & '.join(cells))

	return tex % ' \\tabularnewline\n \\hline\n'.join(rows)

#============================================================
GPLOT_DATAFILE_HEADER = """#
# -------------------------------------------------------------
# GNUmed test results export for Gnuplot plotting
# -------------------------------------------------------------
#
# There is one (gnuplot) index per test type. Two blank
# lines will separate indices.
#
# The first line of each index contains test type abbreviation
# and test type name which can be used as title for plots:
#  set key ... autotitle columnheader)
#
# Each index contains one test result per line.
#
# Columns in each line:
#   1 - clin_when at full precision:
#        set timefmt "%%Y-%%m-%%d_%%H:%%M"
#        timecolumn(1, "%%Y-%%m-%%d_%%H:%%M")
#   2 - value
#   3 - unit
#   4 - unified (target or normal) range: lower bound
#   5 - unified (target or normal) range: upper bound
#   6 - normal range: lower bound
#   7 - normal range: upper bound
#   8 - target range: lower bound
#   9 - target range: upper bound
#  10 - clin_when formatted into string (say, as x-axis tic label)
#
# If the timestamp of consecutive test results is on one and the
# same day one blank line is inserted such that a discontinuous
# line can be plotted if desired.
#
# -------------------------------------------------------------
#
# the file
#
#  <%s.conf>
#
# will contain various gnuplot settings specific to this plot,
# such as <ylabel>, <y2label>, <title>,
# there will also be settings suitable for stacked multiplots
# -------------------------------------------------------------
"""

def export_results_for_gnuplot(results=None, filename=None, show_year=True, patient=None):

	sandbox_dir = os.path.join(gmTools.gmPaths().tmp_dir, 'gplot')
	if not gmTools.mkdir(sandbox_dir):
		sandbox_dir = gmTools.mk_sandbox_dir(prefix = 'gm2gpl-')
	_log.debug('sandbox directory: [%s]', sandbox_dir)
	if filename is None:
		filename = gmTools.get_unique_filename(prefix = 'gm2gpl-', suffix = '.dat', tmp_dir = sandbox_dir)

	# sort results into groups by test type
	results_grouped_by_test_type = {}
	for r in results:
		try:
			results_grouped_by_test_type[r['unified_name']].append(r)
		except KeyError:
			results_grouped_by_test_type[r['unified_name']] = [r]

	conf_name = '%s.conf' % filename
	gplot_conf = open(conf_name, mode = 'wt', encoding = 'utf8')
	gplot_conf.write('# settings for stacked multiplot layouts:\n')
	sub_title = _('plotted %s (GNUmed v%s)') % (
		gmDateTime.pydt_now_here().strftime('%Y %b %d %H:%M'),
		_cfg.get(option = 'client_version')
	)
	if patient is None:
		plot_title = sub_title
	else:
		plot_title = '%s - %s\\n{/*0.8 %s}' % (
			patient.get_description_gender(with_nickname = False).strip(),
			patient.get_formatted_dob(format = '%Y %b %d', none_string = _('unknown DOB'), honor_estimation = True),
			sub_title
		)
	gplot_conf.write('multiplot_title = "%s"\n' % plot_title)
	gplot_conf.write('multiplot_no_of_tests = %s	# number of index blocks (resp. test types)\n' % len(results_grouped_by_test_type))
	gplot_conf.write('array multiplot_y_labels[multiplot_no_of_tests]	# list for ylabels suitable for stacked multiplots\n')
	gplot_conf.write('\n')
	gplot_conf.write('# settings for individual plots, stacked or not:\n')

	gplot_data = open(filename, mode = 'wt', encoding = 'utf8')
	gplot_data.write(GPLOT_DATAFILE_HEADER % filename)

	test_type_groups = list(results_grouped_by_test_type)
	for test_type_idx in range(len(test_type_groups)):
		test_type = test_type_groups[test_type_idx]
		if len(results_grouped_by_test_type[test_type]) == 0:
			continue
		first_result = results_grouped_by_test_type[test_type][0]
		if test_type_idx == 0:
			gplot_conf.write('set title "%s" enhanced\n' % plot_title)
			gplot_conf.write('\n')
			gplot_conf.write('set ylabel "%s"\n' % first_result['unified_name'])
		elif test_type_idx == 1:
			gplot_conf.write('set y2label "%s"\n' % first_result['unified_name'])
		gplot_conf.write('multiplot_y_labels[%s] = "%s (%s)"\n' % (test_type_idx + 1, first_result['unified_name'], first_result['unified_abbrev']))
		title = '%s (%s)' % (
			first_result['unified_abbrev'],
			first_result['unified_name']
		)
		gplot_data.write('\n\n"%s" "%s"\n' % (title, title))
		prev_date = None
		prev_year = None
		for result in sorted(results_grouped_by_test_type[test_type], key=lambda result:result['clin_when']):
			curr_date = result['clin_when'].strftime('%Y-%m-%d')
			if curr_date == prev_date:
				gplot_data.write('# %s\n\n' % _('blank line inserted to allow for discontinued-line style drawing of same-day values:'))
			if show_year:
				if result['clin_when'].year == prev_year:
					when_template = '%b %d %H:%M'
				else:
					when_template = '%b %d %H:%M (%Y)'
				prev_year = result['clin_when'].year
			else:
				when_template = '%b %d'
			val = result['val_num']
			if val is None:
				val = result.estimate_numeric_value_from_alpha
			if val is None:
				continue		# skip distinctly non-numericable values
			gplot_data.write ('%s %s "%s" %s %s %s %s %s %s "%s"\n' % (
				result['clin_when'].strftime('%Y-%m-%d_%H:%M'),
				val,
				gmTools.coalesce(result['val_unit'], '"<?>"'),
				gmTools.coalesce(result['unified_target_min'], '"<?>"'),
				gmTools.coalesce(result['unified_target_max'], '"<?>"'),
				gmTools.coalesce(result['val_normal_min'], '"<?>"'),
				gmTools.coalesce(result['val_normal_max'], '"<?>"'),
				gmTools.coalesce(result['val_target_min'], '"<?>"'),
				gmTools.coalesce(result['val_target_max'], '"<?>"'),
				result['clin_when'].strftime(when_template)
			))
			prev_date = curr_date
	gplot_data.close()
	gplot_conf.close()

	return filename

#============================================================
class cLabRequest(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one lab request."""

	_cmd_fetch_payload = """
		select *, xmin_lab_request from v_lab_requests
		where pk_request=%s"""
	_cmds_lock_rows_for_update = [
		"""select 1 from lab_request where pk=%(pk_request)s and xmin=%(xmin_lab_request)s for update"""
	]
	_cmds_store_payload = [
		"""update lab_request set
				request_id=%(request_id)s,
				lab_request_id=%(lab_request_id)s,
				clin_when=%(sampled_when)s,
				lab_rxd_when=%(lab_rxd_when)s,
				results_reported_when=%(results_reported_when)s,
				request_status=%(request_status)s,
				is_pending=%(is_pending)s::bool,
				narrative=%(progress_note)s
			where pk=%(pk_request)s""",
		"""select xmin_lab_request from v_lab_requests where pk_request=%(pk_request)s"""
	]
	_updatable_fields = [
		'request_id',
		'lab_request_id',
		'sampled_when',
		'lab_rxd_when',
		'results_reported_when',
		'request_status',
		'is_pending',
		'progress_note'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, row=None):
		"""Instantiate lab request.

		The aPK_obj can be either a dict with the keys "req_id"
		and "lab" or a simple primary key.
		"""
		# instantiate from row data ?
		if aPK_obj is None:
			gmBusinessDBObject.cBusinessDBObject.__init__(self, row=row)
			return
		pk = aPK_obj
		# instantiate from "req_id" and "lab" ?
		if type(aPK_obj) == dict:
			# sanity check
			try:
				aPK_obj['req_id']
				aPK_obj['lab']
			except Exception:
				_log.exception('[%s:??]: faulty <aPK_obj> structure: [%s]' % (self.__class__.__name__, aPK_obj), sys.exc_info())
				raise gmExceptions.ConstructorError('[%s:??]: cannot derive PK from [%s]' % (self.__class__.__name__, aPK_obj))
			# generate query
			where_snippets = []
			where_snippets.append('request_id=%(req_id)s')
			if type(aPK_obj['lab']) == int:
				where_snippets.append('pk_test_org=%(lab)s')
			else:
				where_snippets.append('lab_name=%(lab)s')
#			where_clause = ' and '.join(where_snippets)
#			cmd = "select pk_request from v_lab_requests where %s" % where_clause
#			# get pk
#			data = gmPG2.run_ro_query('historica', cmd, None, aPK_obj)
#			if data is None:
#				raise gmExceptions.ConstructorError('[%s:??]: error getting lab request for [%s]' % (self.__class__.__name__, aPK_obj))
#			if len(data) == 0:
#				raise gmExceptions.NoSuchClinItemError('[%s:??]: no lab request for [%s]' % (self.__class__.__name__, aPK_obj))
#			pk = data[0][0]
		# instantiate class
		gmBusinessDBObject.cBusinessDBObject.__init__(self, aPK_obj=pk)
#	#--------------------------------------------------------
#	def get_patient(self):
#		cmd = """
#			select vpi.pk_patient, vbp.title, vbp.firstnames, vbp.lastnames, vbp.dob
#			from v_pat_items vpi, v_active_persons vbp
#			where
#				vpi.pk_item=%s
#					and
#				vbp.pk_identity=vpi.pk_patient"""
#		pat = gmPG2.run_ro_query('historica', cmd, None, self._payload['pk_item'])
#		if pat is None:
#			_log.error('cannot get patient for lab request [%s]' % self._payload['pk_item'])
#			return None
#		if len(pat) == 0:
#			_log.error('no patient associated with lab request [%s]' % self._payload['pk_item'])
#			return None
#		return pat[0]

#============================================================
# convenience functions
#------------------------------------------------------------
def create_lab_request(lab=None, req_id=None, pat_id=None, encounter_id=None, episode_id=None):
	"""Create or get lab request.

		returns tuple (status, value):
			(True, lab request instance)
			(False, error message)
			(None, housekeeping_todo primary key)
	"""
	pass
#	req = None
#	aPK_obj = {
#		'lab': lab,
#		'req_id': req_id
#	}
#	try:
#		req = cLabRequest (aPK_obj)
#	except gmExceptions.NoSuchClinItemError as msg:
#		_log.info('%s: will try to create lab request' % str(msg))
#	except gmExceptions.ConstructorError as msg:
#		_log.exception(str(msg), sys.exc_info(), verbose=0)
#		return (False, msg)
	# found
#	if req is not None:
#		db_pat = req.get_patient()
#		db_pat = None
#		if db_pat is None:
#			_log.error('cannot cross-check patient on lab request')
#			return (None, '')
#		# yes but ambiguous
#		if pat_id != db_pat[0]:
#			_log.error('lab request found for [%s:%s] but patient mismatch: expected [%s], in DB [%s]' % (lab, req_id, pat_id, db_pat))
#			me = '$RCSfile: gmPathLab.py,v $ $Revision: 1.81 $'
#			to = 'user'
#			prob = _('The lab request already exists but belongs to a different patient.')
#			sol = _('Verify which patient this lab request really belongs to.')
#			ctxt = _('lab [%s], request ID [%s], expected link with patient [%s], currently linked to patient [%s]') % (lab, req_id, pat_id, db_pat)
#			cat = 'lab'
#			status, data = gmPG2.add_housekeeping_todo(me, to, prob, sol, ctxt, cat)
#			return (None, None)
#		return (True, req)
#	# not found
#	queries = []
#	if type(lab) is int:
#		cmd = "insert into lab_request (fk_encounter, fk_episode, fk_test_org, request_id) values (%s, %s, %s, %s)"
#	else:
#		cmd = "insert into lab_request (fk_encounter, fk_episode, fk_test_org, request_id) values (%s, %s, (select pk from test_org where internal_OBSOLETE_name=%s), %s)"
#	queries.append((cmd, [encounter_id, episode_id, str(lab), req_id]))
#	cmd = "select currval('lab_request_pk_seq')"
#	queries.append((cmd, []))
#	# insert new
#	result, err = (None, 'error')
#	#result, err = gmPG2.run_commit('historica', queries, True)
#	if result is None:
#		return (False, err)
#	try:
#		req = cLabRequest(aPK_obj=result[0][0])
#	except gmExceptions.ConstructorError as msg:
#		_log.exception(str(msg), sys.exc_info(), verbose=0)
#		return (False, msg)
#	return (True, req)
#------------------------------------------------------------
def get_pending_requests(limit=250):
	lim = limit + 1
	cmd = "select pk from lab_request where is_pending is true limit %s" % lim
	rows = gmPG2.run_ro_queries(queries = cmd)
	if rows is None:
		_log.error('error retrieving pending lab requests')
		return (None, None)
	if len(rows) == 0:
		return (False, [])
	# more than LIMIT rows ?
	if len(rows) == lim:
		too_many = True
		# but deliver only LIMIT rows so that our assumption holds true...
		rows = rows[:limit]
	else:
		too_many = False
	requests = []
	for row in rows:
		try:
			requests.append(cLabRequest(aPK_obj=row[0]))
		except gmExceptions.ConstructorError:
			_log.exception('skipping pending lab request [%s]' % row[0], sys.exc_info(), verbose=0)
	return (too_many, requests)

#------------------------------------------------------------
def get_next_request_ID(lab=None, incrementor_func=None):
	"""Get logically next request ID for given lab.

	- incrementor_func:
	  - if not supplied the next ID is guessed
	  - if supplied it is applied to the most recently used ID
	"""
	if type(lab) == int:
		lab_snippet = 'vlr.fk_test_org=%s'
	else:
		lab_snippet = 'vlr.lab_name=%s'
		lab = str(lab)
	cmd =  """
		select request_id
		from lab_request lr0
		where lr0.clin_when = (
			select max(vlr.sampled_when)
			from v_lab_requests vlr
			where %s
		)""" % lab_snippet
	rows = gmPG2.run_ro_queries(cmd, None, lab)
	if rows is None:
		_log.warning('error getting most recently used request ID for lab [%s]' % lab)
		return ''
	if len(rows) == 0:
		return ''
	most_recent = rows[0][0]
	# apply supplied incrementor
	if incrementor_func is not None:
		try:
			next = incrementor_func(most_recent)
		except TypeError:
			_log.error('cannot call incrementor function [%s]' % str(incrementor_func))
			return most_recent
		return next
	# try to be smart ourselves
	for pos in range(len(most_recent)):
		header = most_recent[:pos]
		trailer = most_recent[pos:]
		try:
			return '%s%s' % (header, str(int(trailer) + 1))
		except ValueError:
			header = most_recent[:-1]
			trailer = most_recent[-1:]
			return '%s%s' % (header, chr(ord(trailer) + 1))

#============================================================
def calculate_bmi(mass=None, height=None, age=None):
	"""Calculate BMI.

	mass: kg
	height: cm
	age: not yet used

	returns:
		(True/False, data)
		True: data = (bmi, lower_normal, upper_normal)
		False: data = error message
	"""
	converted, mass = gmTools.input2decimal(mass)
	if not converted:
		return False, 'mass: cannot convert <%s> to Decimal' % mass

	converted, height = gmTools.input2decimal(height)
	if not converted:
		return False, 'height: cannot convert <%s> to Decimal' % height

	approx_surface = (height / decimal.Decimal(100))**2
	bmi = mass / approx_surface

	print(mass, height, '->', approx_surface, '->', bmi)

	lower_normal_mass = 20.0 * approx_surface
	upper_normal_mass = 25.0 * approx_surface

	return True, (bmi, lower_normal_mass, upper_normal_mass)

#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	import time

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	#------------------------------------------
	def test_create_test_result():
		tr = create_test_result (
			encounter = 1,
			episode = 1,
			type = 1,
			intended_reviewer = 1,
			val_num = '12',
			val_alpha=None,
			unit = 'mg/dl'
		)
		print(tr)
		return tr
	#------------------------------------------
	def test_delete_test_result():
		tr = test_create_test_result()
		delete_test_result(tr)
	#------------------------------------------
	def test_result():
		r = cTestResult(aPK_obj=6)
		#print r
		#print r.reference_ranges
		#print r.formatted_range
		#print r.temporally_closest_normal_range
		print(r.estimate_numeric_value_from_alpha)
	#------------------------------------------
	def test_request():
		print("test_request()")
		try:
#			lab_req = cLabRequest(aPK_obj=1)
#			lab_req = cLabRequest(req_id='EML#SC937-0176-CEC#11', lab=2)
			data = {
				'req_id': 'EML#SC937-0176-CEC#11',
				'lab': 'Enterprise Main Lab'
			}
			lab_req = cLabRequest(aPK_obj=data)
		except gmExceptions.ConstructorError as msg:
			print("no such lab request:", msg)
			return
		print(lab_req)
		fields = lab_req.get_fields()
		for field in fields:
			print(field, ':', lab_req[field])
		print("updatable:", lab_req.get_updatable_fields())
		print(time.time())
		print(lab_req.get_patient())
		print(time.time())
	#--------------------------------------------------------
	def test_unreviewed():
		#data = get_unreviewed_results()
		data = []
		for result in data:
			print(result)
	#--------------------------------------------------------
	def test_pending():
		data = get_pending_requests()
		for result in data:
			print(result)
	#--------------------------------------------------------
	def test_create_measurement_type():
		print(create_measurement_type (
			lab = None,
			abbrev = 'tBZ2',
			unit = 'mg%',
			name = 'BZ (test 2)'
		))
	#--------------------------------------------------------
	def test_meta_test_type():
		mtt = cMetaTestType(aPK_obj = 1)
		print(mtt)
		print(get_meta_test_types())
	#--------------------------------------------------------
	def test_test_type():
		tt = cMeasurementType(aPK_obj = 1)
		print(tt)
		print(get_measurement_types())
	#--------------------------------------------------------
	def test_format_test_results():
		results = [
			cTestResult(aPK_obj=1),
			cTestResult(aPK_obj=2),
			cTestResult(aPK_obj=3)
#			cTestResult(aPK_obj=4)
		]
		print(format_test_results(results = results))
		for r in results:
			print(r.format())
	#--------------------------------------------------------
	def test_calculate_bmi():
		done, data = calculate_bmi(mass = sys.argv[2], height = sys.argv[3])
		bmi, low, high = data
		print("BMI:", bmi)
		print("low:", low, "kg")
		print("hi :", high, "kg")

	#--------------------------------------------------------
	def test_test_panel():
		tp = cTestPanel(aPK_obj = 2)
		print(tp)
		print(tp.test_types)
		print(tp.format())

	#--------------------------------------------------------
	def test_get_most_recent_results_for_panel():
		tp = cTestPanel(aPK_obj = 1)
		#print tp.included_loincs
		#tp = cTestPanel(aPK_obj = 3)
		print(tp.format())
		#most_recent = tp.get_most_recent_results(pk_patient = 12, group_by_meta_type = False)
		#most_recent = tp.get_most_recent_results(pk_patient = 138, group_by_meta_type = False)
		#print len(most_recent)
		most_recent = tp.get_most_recent_results(pk_patient = 12, group_by_meta_type = True, include_missing = True)
		#most_recent = tp.get_most_recent_results(pk_patient = 138, group_by_meta_type = True)
		print('found:', len(most_recent))

		for t in most_recent:
			print('--------------')
			if t['pk_meta_test_type'] is None:
				print("standalone")
			else:
				print("meta")
			print(t.format())

	#--------------------------------------------------------
	def test_get_most_recent_results_in_loinc_group():
		most_recent = get_most_recent_results_in_loinc_group (
			#loincs = [u'pseudo LOINC [C-reactive protein (EML)::9] (v21->v22 test panel conversion)'],
			#loincs = ['8867-4'],
			loincs = ['2160-0', '14682-9', '40264-4', '40248-7'],
			max_no_of_results = 6,
			patient = 201,
			consider_indirect_matches = False
		)
		for t in most_recent:
			print(t['loinc_tt'], t['loinc_meta'], t['unified_loinc'])
			if t['pk_meta_test_type'] is None:
				print("---- standalone ----")
			else:
				print("---- meta ----")
			print(t.format())
			input('next')

		return

		most_recent = get_most_recent_results_in_loinc_group (
			#loincs = [u'pseudo LOINC [C-reactive protein (EML)::9] (v21->v22 test panel conversion)'],
			#loincs = ['8867-4'],
			loincs = ['2160-0', '14682-9', '40264-4', '40248-7'],
			max_no_of_results = 2,
			patient = 201,
			consider_indirect_matches = False
			#consider_indirect_matches = True
		)
		for t in most_recent:
			if t['pk_meta_test_type'] is None:
				print("---- standalone ----")
			else:
				print("---- meta ----")
			print(t.format())

	#--------------------------------------------------------
	def test_export_result_for_gnuplot():

		results = get_test_results(pk_patient = 12)
		print(results)
		export_results_for_gnuplot(results=results, filename='test.gpl', show_year=True, patient=None)

	#--------------------------------------------------------
	def test_get_test_results():
		results = get_test_results(pk_patient = 12, order_by = 'unified_abbrev, clin_when DESC')
		print(results)

	#--------------------------------------------------------
	def test_format_test_results_failsafe():
		results = get_test_results(pk_patient = 12, order_by = 'unified_abbrev, clin_when DESC')
		lines = generate_failsafe_test_results_entries(results)
		for line in lines:
			print(line)

	#--------------------------------------------------------

	#print(GPLOT_DATAFILE_HEADER % 'test')

	gmPG2.request_login_params(setup_pool = True)

	#test_result()
	#test_create_test_result()
	#test_delete_test_result()
	#test_create_measurement_type()
	#test_lab_result()
	#test_request()
	#test_create_result()
	#test_unreviewed()
	#test_pending()
	#test_meta_test_type()
	#test_test_type()
	test_format_test_results()
	#test_calculate_bmi()
	#test_test_panel()
	#test_get_test_results()
	#test_get_most_recent_results_for_panel()
	#test_get_most_recent_results_in_loinc_group()
	#test_export_result_for_gnuplot()
	#test_format_test_results_failsafe()

#============================================================
