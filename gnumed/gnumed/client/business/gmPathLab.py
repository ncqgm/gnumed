"""GNUmed measurements related business objects."""
#============================================================
__version__ = "$Revision: 1.81 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"


import types, sys, logging, codecs, decimal

if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmDateTime
if __name__ == '__main__':
	from Gnumed.pycommon import gmLog2
	from Gnumed.pycommon import gmI18N
	gmDateTime.init()
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmHooks
from Gnumed.business import gmOrganization


_log = logging.getLogger('gm.lab')
_log.info(__version__)

# FIXME: use UCUM from Regenstrief Institute

#============================================================
def _on_test_result_modified():
	"""Always relates to the active patient."""
	gmHooks.run_hook_script(hook = u'after_test_result_modified')

gmDispatcher.connect(_on_test_result_modified, u'test_result_mod_db')

#============================================================
class cTestOrg(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one test org/lab."""
	_cmd_fetch_payload = u"""SELECT * FROM clin.v_test_orgs WHERE pk_test_org = %s"""
	_cmds_store_payload = [
		u"""UPDATE clin.test_org SET
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
		u'pk_org_unit',
		u'test_org_contact',
		u'comment'
	]
#------------------------------------------------------------
def create_test_org(name=None, comment=None, pk_org_unit=None):

	if name is None:
		name = _('inhouse lab')
		comment = _('auto-generated')

	# get org unit
	if pk_org_unit is None:
		org = gmOrganization.org_exists(organization = name)
		if org is None:
			org = gmOrganization.create_org (
				organization = name,
				category = u'Laboratory'
			)
		org_unit = gmOrganization.create_org_unit (
			pk_organization = org['pk_org'],
			unit = name
		)
		pk_org_unit = org_unit['pk_org_unit']

	# test org exists ?
	args = {'pk_unit': pk_org_unit}
	cmd = u'SELECT pk_test_org FROM clin.v_test_orgs WHERE pk_org_unit = %(pk_unit)s'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	if len(rows) == 0:
		cmd = u'INSERT INTO clin.test_org (fk_org_unit) VALUES (%(pk_unit)s) RETURNING pk'
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True)

	test_org = cTestOrg(aPK_obj = rows[0][0])
	if comment is not None:
		comment = comment.strip()
	test_org['comment'] = comment
	test_org.save()

	return test_org
#------------------------------------------------------------
def delete_test_org(test_org=None):
	args = {'pk': test_org}
	cmd = u"""
		DELETE FROM clin.test_org
		WHERE
			pk = %(pk)s
				AND
			NOT EXISTS (SELECT 1 FROM clin.lab_request WHERE fk_test_org = %(pk)s LIMIT 1)
				AND
			NOT EXISTS (SELECT 1 FROM clin.test_type WHERE fk_test_org = %(pk)s LIMIT 1)
	"""
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
#------------------------------------------------------------
def get_test_orgs(order_by=u'unit'):
	cmd = u'SELECT * FROM clin.v_test_orgs ORDER BY %s' % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cTestOrg(row = {'pk_field': 'pk_test_org', 'data': r, 'idx': idx}) for r in rows ]
#============================================================
class cMetaTestType(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one meta test type under which actual test types can be aggregated."""

	_cmd_fetch_payload = u"""select * from clin.meta_test_type where pk = %s"""

	_cmds_store_payload = []

	_updatable_fields = []
#------------------------------------------------------------
def delete_meta_type(meta_type=None):
	cmd = u'delete from clin.meta_test_type where pk = %(pk)s'
	args = {'pk': meta_type}
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
#------------------------------------------------------------
def get_meta_test_types():
	cmd = u'select * from clin.meta_test_type'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cMetaTestType(row = {'pk_field': 'pk', 'data': r, 'idx': idx}) for r in rows ]
#============================================================
class cUnifiedTestType(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one unified test type."""

	# FIXME: if we ever want to write we need to include XMIN in the view
	_cmd_fetch_payload = u"""select * from clin.v_unified_test_types where pk_test_type = %s"""

	_cmds_store_payload = []

	_updatable_fields = []
	#--------------------------------------------------------
	def get_most_recent_results(self, patient=None, no_of_results=1):
		results = get_most_recent_results (
			test_type = self._payload[self._idx['pk_test_type']],
			loinc = None,
			no_of_results = no_of_results,
			patient = patient
		)
		if results is None:
			if self._payload[self._idx['loinc_tt']] is not None:
				results = get_most_recent_results (
					test_type = None,
					loinc = self._payload[self._idx['loinc_tt']],
					no_of_results = no_of_results,
					patient = patient
				)
		if results is None:
			if self._payload[self._idx['loinc_meta']] is not None:
				results = get_most_recent_results (
					test_type = None,
					loinc = self._payload[self._idx['loinc_meta']],
					no_of_results = no_of_results,
					patient = patient
				)
		return results
#============================================================
class cMeasurementType(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one test result type."""

	_cmd_fetch_payload = u"""select * from clin.v_test_types where pk_test_type = %s"""

	_cmds_store_payload = [
		u"""update clin.test_type set
				abbrev = %(abbrev)s,
				name = %(name)s,
				loinc = gm.nullify_empty_string(%(loinc)s),
				code = gm.nullify_empty_string(%(code)s),
				coding_system = gm.nullify_empty_string(%(coding_system)s),
				comment = gm.nullify_empty_string(%(comment_type)s),
				conversion_unit = gm.nullify_empty_string(%(conversion_unit)s),
				fk_test_org = %(pk_test_org)s
			where pk = %(pk_test_type)s""",
		u"""select xmin_test_type from clin.v_test_types where pk_test_type = %(pk_test_type)s"""
	]

	_updatable_fields = [
		'abbrev',
		'name',
		'loinc',
		'code',
		'coding_system',
		'comment_type',
		'conversion_unit',
		'pk_test_org'
	]
	#--------------------------------------------------------
#	def __setitem__(self, attribute, value):
#
#		# find fk_test_org from name
#		if (attribute == 'fk_test_org') and (value is not None):
#			try:
#				int(value)
#			except:
#				cmd = u"select pk from clin.test_org where internal _name = %(val)s"
#				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'val': value}}])
#				if len(rows) == 0:
#					raise ValueError('[%s]: no test org for [%s], cannot set <%s>' % (self.__class__.__name__, value, attribute))
#				value = rows[0][0]
#
#		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)
	#--------------------------------------------------------
	def _get_in_use(self):
		cmd = u'select exists(select 1 from clin.test_result where fk_type = %(pk_type)s)'
		args = {'pk_type': self._payload[self._idx['pk_test_type']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		return rows[0][0]

	in_use = property(_get_in_use, lambda x:x)
	#--------------------------------------------------------
	def get_most_recent_results(self, patient=None, no_of_results=1):
		results = get_most_recent_results (
			test_type = self._payload[self._idx['pk_test_type']],
			loinc = None,
			no_of_results = no_of_results,
			patient = patient
		)
		if results is None:
			if self._payload[self._idx['loinc']] is not None:
				results = get_most_recent_results (
					test_type = None,
					loinc = self._payload[self._idx['loinc']],
					no_of_results = no_of_results,
					patient = patient
				)
		return results
#------------------------------------------------------------
def get_measurement_types(order_by=None):
	cmd = u'select * from clin.v_test_types %s' % gmTools.coalesce(order_by, u'', u'order by %s')
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cMeasurementType(row = {'pk_field': 'pk_test_type', 'data': r, 'idx': idx}) for r in rows ]
#------------------------------------------------------------
def find_measurement_type(lab=None, abbrev=None, name=None):

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

		where_clause = u' and '.join(where_snippets)
		cmd = u"select * from clin.v_test_types where %s" % where_clause
		args = {'lab': lab, 'abbrev': abbrev, 'name': name}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		if len(rows) == 0:
			return None

		tt = cMeasurementType(row = {'pk_field': 'pk_test_type', 'data': rows[0], 'idx': idx})
		return tt
#------------------------------------------------------------
def delete_measurement_type(measurement_type=None):
	cmd = u'delete from clin.test_type where pk = %(pk)s'
	args = {'pk': measurement_type}
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
#------------------------------------------------------------
def create_measurement_type(lab=None, abbrev=None, unit=None, name=None):
	"""Create or get test type."""

	ttype = find_measurement_type(lab = lab, abbrev = abbrev, name = name)
	# found ?
	if ttype is not None:
		return ttype

	_log.debug('creating test type [%s:%s:%s:%s]', lab, abbrev, name, unit)

	# not found, so create it
	if unit is None:
		_log.error('need <unit> to create test type: %s:%s:%s:%s' % (lab, abbrev, name, unit))
		raise ValueError('need <unit> to create test type')

	# make query
	cols = []
	val_snippets = []
	vals = {}

	# lab
	if lab is None:
		lab = create_test_org()['pk_test_org']

	cols.append('fk_test_org')
	try:
		vals['lab'] = int(lab)
		val_snippets.append('%(lab)s')
	except:
		vals['lab'] = lab
		val_snippets.append('(SELECT pk_test_org FROM clin.v_test_orgs WHERE unit = %(lab)s)')

	# code
	cols.append('abbrev')
	val_snippets.append('%(abbrev)s')
	vals['abbrev'] = abbrev

	# unit
	cols.append('conversion_unit')
	val_snippets.append('%(unit)s')
	vals['unit'] = unit

	# name
	if name is not None:
		cols.append('name')
		val_snippets.append('%(name)s')
		vals['name'] = name

	col_clause = u', '.join(cols)
	val_clause = u', '.join(val_snippets)
	queries = [
		{'cmd': u'insert into clin.test_type (%s) values (%s)' % (col_clause, val_clause), 'args': vals},
		{'cmd': u"select * from clin.v_test_types where pk_test_type = currval(pg_get_serial_sequence('clin.test_type', 'pk'))"}
	]
	rows, idx = gmPG2.run_rw_queries(queries = queries, get_col_idx = True, return_data = True)
	ttype = cMeasurementType(row = {'pk_field': 'pk_test_type', 'data': rows[0], 'idx': idx})

	return ttype
#============================================================
class cTestResult(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one test result."""

	_cmd_fetch_payload = u"select * from clin.v_test_results where pk_test_result = %s"

	_cmds_store_payload = [
		u"""update clin.test_result set
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
				fk_intended_reviewer = %(pk_intended_reviewer)s,
				fk_encounter = %(pk_encounter)s,
				fk_episode = %(pk_episode)s,
				fk_type = %(pk_test_type)s,
				fk_request = %(pk_request)s
			where
				pk = %(pk_test_result)s and
				xmin = %(xmin_test_result)s""",
		u"""select xmin_test_result from clin.v_test_results where pk_test_result = %(pk_test_result)s"""
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
		'pk_intended_reviewer',
		'pk_encounter',
		'pk_episode',
		'pk_test_type',
		'pk_request'
	]
	#--------------------------------------------------------
	def format(self, with_review=True, with_comments=True, date_format='%Y-%m-%d %H:%M'):

		lines = []

		lines.append(u' %s %s (%s): %s %s%s' % (
			self._payload[self._idx['clin_when']].strftime(date_format),
			self._payload[self._idx['unified_abbrev']],
			self._payload[self._idx['unified_name']],
			self._payload[self._idx['unified_val']],
			self._payload[self._idx['val_unit']],
			gmTools.coalesce(self._payload[self._idx['abnormality_indicator']], u'', u' (%s)')
		))

		if with_comments:
			if gmTools.coalesce(self._payload[self._idx['comment']], u'').strip() != u'':
				lines.append(_('   Doc: %s') % self._payload[self._idx['comment']].strip())
			if gmTools.coalesce(self._payload[self._idx['note_test_org']], u'').strip() != u'':
				lines.append(_('   MTA: %s') % self._payload[self._idx['note_test_org']].strip())

		if with_review:
			if self._payload[self._idx['reviewed']]:
				if self._payload[self._idx['is_clinically_relevant']]:
					lines.append(u'   %s  %s: %s' % (
						self._payload[self._idx['last_reviewer']],
						self._payload[self._idx['last_reviewed']].strftime('%Y-%m-%d %H:%M'),
						gmTools.bool2subst (
							self._payload[self._idx['is_technically_abnormal']],
							_('abnormal and relevant'),
							_('normal but relevant')
						)
					))
			else:
				lines.append(_('   unreviewed'))

		return lines
	#--------------------------------------------------------
	def _get_reference_ranges(self):

		cmd = u"""
select
distinct on (norm_ref_group_str, val_unit, val_normal_min, val_normal_max, val_normal_range, val_target_min, val_target_max, val_target_range)
	pk_patient,
	val_unit,
	val_normal_min, val_normal_max, val_normal_range,
	val_target_min, val_target_max, val_target_range,
	norm_ref_group,
	coalesce(norm_ref_group, '') as norm_ref_group_str
from
	clin.v_test_results
where
	pk_test_type = %(pk_type)s
"""
		args = {'pk_type': self._payload[self._idx['pk_test_type']]}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
		return rows

	def _set_reference_ranges(self, val):
		raise AttributeError('[%s]: reference ranges not settable') % self.__class__.__name__

	reference_ranges = property(_get_reference_ranges, _set_reference_ranges)
	#--------------------------------------------------------
	def _get_test_type(self):
		return cMeasurementType(aPK_obj = self._payload[self._idx['pk_test_type']])

	test_type = property(_get_test_type, lambda x:x)
	#--------------------------------------------------------
	def set_review(self, technically_abnormal=None, clinically_relevant=None, comment=None, make_me_responsible=False):

		# FIXME: this is not concurrency safe
		if self._payload[self._idx['reviewed']]:
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
					comment = gmTools.none_if(comment, u'', strip_string = True)
					if comment is None:
						if make_me_responsible is False:
							return True
			self.__set_new_review (
				technically_abnormal = technically_abnormal,
				clinically_relevant = clinically_relevant,
				comment = comment
			)

		if make_me_responsible is True:
			cmd = u"SELECT pk FROM dem.staff WHERE db_user = current_user"
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
			self['pk_intended_reviewer'] = rows[0][0]
			self.save_payload()
			return

		self.refetch_payload()
	#--------------------------------------------------------
	def get_adjacent_results(self, desired_earlier_results=1, desired_later_results=1, max_offset=None):

		if desired_earlier_results < 1:
			raise ArgumentError('<desired_earlier_results> must be > 0')

		if desired_later_results < 1:
			raise ArgumentError('<desired_later_results> must be > 0')

		args = {
			'pat': self._payload[self._idx['pk_patient']],
			'ttyp': self._payload[self._idx['pk_test_type']],
			'tloinc': self._payload[self._idx['loinc_tt']],
			'mtyp': self._payload[self._idx['pk_meta_test_type']],
			'mloinc': self._payload[self._idx['loinc_meta']],
			'when': self._payload[self._idx['clin_when']],
			'offset': max_offset
		}
		WHERE = u'((pk_test_type = %(ttyp)s) OR (loinc_tt = %(tloinc)s))'
		WHERE_meta = u'((pk_meta_test_type = %(mtyp)s) OR (loinc_meta = %(mloinc)s))'
		if max_offset is not None:
			WHERE = WHERE + u' AND (clin_when BETWEEN (%(when)s - %(offset)s) AND (%(when)s + %(offset)s))'
			WHERE_meta = WHERE_meta + u' AND (clin_when BETWEEN (%(when)s - %(offset)s) AND (%(when)s + %(offset)s))'

		SQL = u"""
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
		cmd = SQL % (u'<', WHERE, desired_earlier_results)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		if len(rows) > 0:
			earlier_results.extend([ cTestResult(row = {'pk_field': 'pk_test_result', 'idx': idx, 'data': r}) for r in rows ])
		# by meta type ?
		missing_results = desired_earlier_results - len(earlier_results)
		if  missing_results > 0:
			cmd = SQL % (u'<', WHERE_meta, missing_results)
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
			if len(rows) > 0:
				earlier_results.extend([ cTestResult(row = {'pk_field': 'pk_test_result', 'idx': idx, 'data': r}) for r in rows ])

		# get later results
		later_results = []
		# by type
		cmd = SQL % (u'>', WHERE, desired_later_results)
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		if len(rows) > 0:
			later_results.extend([ cTestResult(row = {'pk_field': 'pk_test_result', 'idx': idx, 'data': r}) for r in rows ])
		# by meta type ?
		missing_results = desired_later_results - len(later_results)
		if  missing_results > 0:
			cmd = SQL % (u'>', WHERE_meta, missing_results)
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
			if len(rows) > 0:
				later_results.extend([ cTestResult(row = {'pk_field': 'pk_test_result', 'idx': idx, 'data': r}) for r in rows ])

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
			if self._payload[self._idx['abnormality_indicator']] is not None:
				if self._payload[self._idx['abnormality_indicator']].strip() != u'':
					technically_abnormal = True

		if clinically_relevant is None:
			clinically_relevant = technically_abnormal

		cmd = u"""
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
			'pk': self._payload[self._idx['pk_test_result']],
			'abnormal': technically_abnormal,
			'relevant': clinically_relevant,
			'cmt': comment
		}

		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#--------------------------------------------------------
	def __change_existing_review(self, technically_abnormal=None, clinically_relevant=None, comment=None):
		"""Change a review on a row.

			- if technically abnormal/clinically relevant are
			  None they are not set
		"""
		args = {
			'pk_row': self._payload[self._idx['pk_test_result']],
			'abnormal': technically_abnormal,
			'relevant': clinically_relevant,
			'cmt': comment
		}

		set_parts = [
			u'fk_reviewer = (SELECT pk FROM dem.staff WHERE db_user = current_user)',
			u'comment = gm.nullify_empty_string(%(cmt)s)'
		]

		if technically_abnormal is not None:
			set_parts.append(u'is_technically_abnormal = %(abnormal)s')

		if clinically_relevant is not None:
			set_parts.append(u'clinically_relevant = %(relevant)s')

		cmd = u"""
UPDATE clin.reviewed_test_results SET
	%s
WHERE
	fk_reviewed_row = %%(pk_row)s
""" % u',\n	'.join(set_parts)

		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])

#------------------------------------------------------------
def get_most_recent_results(test_type=None, loinc=None, no_of_results=1, patient=None):

	if None not in [test_type, loinc]:
		raise ArgumentError('either <test_type> or <loinc> must be None')

	if no_of_results < 1:
		raise ArgumentError('<no_of_results> must be > 0')

	args = {
		'pat': patient,
		'ttyp': test_type,
		'loinc': loinc
	}

	where_parts = [u'pk_patient = %(pat)s']
	if test_type is not None:
		where_parts.append(u'pk_test_type = %(ttyp)s')		# consider: pk_meta_test_type = %(pkmtt)s / self._payload[self._idx['pk_meta_test_type']]
	elif loinc is not None:
		where_parts.append(u'((loinc_tt = %(loinc)s) OR (loinc_meta = %(loinc)s))')

	cmd = u"""
		SELECT * FROM clin.v_test_results
		WHERE
			%s
		ORDER BY clin_when DESC
		LIMIT %s""" % (
			u' AND '.join(where_parts),
			no_of_results
		)
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
	if len(rows) == 0:
		return None

	if no_of_results == 1:
		return cTestResult(row = {'pk_field': 'pk_test_result', 'idx': idx, 'data': rows[0]})

	return [ cTestResult(row = {'pk_field': 'pk_test_result', 'idx': idx, 'data': r}) for r in rows ]
#------------------------------------------------------------
def delete_test_result(result=None):

	try:
		pk = int(result)
	except (TypeError, AttributeError):
		pk = result['pk_test_result']

	cmd = u'delete from clin.test_result where pk = %(pk)s'
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'pk': pk}}])
#------------------------------------------------------------
def create_test_result(encounter=None, episode=None, type=None, intended_reviewer=None, val_num=None, val_alpha=None, unit=None):

	cmd1 = u"""
insert into clin.test_result (
	fk_encounter,
	fk_episode,
	fk_type,
	fk_intended_reviewer,
	val_num,
	val_alpha,
	val_unit
) values (
	%(enc)s,
	%(epi)s,
	%(type)s,
	%(rev)s,
	%(v_num)s,
	%(v_alpha)s,
	%(unit)s
)"""

	cmd2 = u"""
select *
from
	clin.v_test_results
where
	pk_test_result = currval(pg_get_serial_sequence('clin.test_result', 'pk'))"""

	args = {
		u'enc': encounter,
		u'epi': episode,
		u'type': type,
		u'rev': intended_reviewer,
		u'v_num': val_num,
		u'v_alpha': val_alpha,
		u'unit': unit
	}

	rows, idx = gmPG2.run_rw_queries (
		queries = [
			{'cmd': cmd1, 'args': args},
			{'cmd': cmd2}
		],
		return_data = True,
		get_col_idx = True
	)

	tr = cTestResult(row = {
		'pk_field': 'pk_test_result',
		'idx': idx,
		'data': rows[0]
	})

	return tr
#------------------------------------------------------------
def format_test_results(results=None, output_format=u'latex'):

	_log.debug(u'formatting test results into [%s]', output_format)

	if output_format == u'latex':
		return __format_test_results_latex(results = results)

	msg = _('unknown test results output format [%s]') % output_format
	_log.error(msg)
	return msg
#------------------------------------------------------------
def __tests2latex_minipage(results=None, width=u'1.5cm', show_time=False, show_range=True):

	if len(results) == 0:
		return u'\\begin{minipage}{%s} \\end{minipage}' % width

	lines = []
	for t in results:

		tmp = u''

		if show_time:
			tmp += u'{\\tiny (%s)} ' % t['clin_when'].strftime('%H:%M')

		tmp += u'%.8s' % t['unified_val']

		lines.append(tmp)
		tmp = u''

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
					tmp += u'{\\tiny %s}' % t['unified_target_range']
				else:
					tmp += u'{\\tiny %s}' % (
						gmTools.coalesce(t['unified_target_min'], u'- ', u'%s - '),
						gmTools.coalesce(t['unified_target_max'], u'', u'%s')
					)
				lines.append(tmp)

	return u'\\begin{minipage}{%s} \\begin{flushright} %s \\end{flushright} \\end{minipage}' % (width, u' \\\\ '.join(lines))
#------------------------------------------------------------
def __tests2latex_cell(results=None, show_time=False, show_range=True):

	if len(results) == 0:
		return u''

	lines = []
	for t in results:

		tmp = u''

		if show_time:
			tmp += u'\\tiny %s ' % t['clin_when'].strftime('%H:%M')

		tmp += u'\\normalsize %.8s' % t['unified_val']

		lines.append(tmp)
		tmp = u'\\tiny %s' % gmTools.coalesce(t['val_unit'], u'', u'%s ')

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
			tmp += u'[%s]' % t['unified_target_range']
		else:
			tmp += u'[%s%s]' % (
				gmTools.coalesce(t['unified_target_min'], u'--', u'%s--'),
				gmTools.coalesce(t['unified_target_max'], u'', u'%s')
			)
		lines.append(tmp)

	return u' \\\\ '.join(lines)
#------------------------------------------------------------
def __format_test_results_latex(results=None):

	if len(results) == 0:
		return u'\\noindent %s' % _('No test results to format.')

	# discover the columns and rows
	dates = {}
	tests = {}
	grid = {}
	for result in results:
#		row_label = u'%s \\ \\tiny (%s)}' % (result['unified_abbrev'], result['unified_name'])
		row_label = result['unified_abbrev']
		tests[row_label] = None
		col_label = u'{\\scriptsize %s}' % result['clin_when'].strftime('%Y-%m-%d')
		dates[col_label] = None
		try:
			grid[row_label]
		except KeyError:
			grid[row_label] = {}
		try:
			grid[row_label][col_label].append(result)
		except KeyError:
			grid[row_label][col_label] = [result]

	col_labels = sorted(dates.keys(), reverse = True)
	del dates
	row_labels = sorted(tests.keys())
	del tests

	col_def = len(col_labels) * u'>{\\raggedleft}p{1.7cm}|'

	# format them
	tex = u"""\\noindent %s

\\noindent \\begin{tabular}{|l|%s}
\\hline
 & %s \\tabularnewline
\\hline

%%s \\tabularnewline

\\hline

\\end{tabular}""" % (
		_('Test results'),
		col_def,
		u' & '.join(col_labels)
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
				cells.append(u' ')
				continue

			cells.append (
				__tests2latex_cell (
					results = tests,
					show_time = (len(tests) > 1),
					show_range = True
				)
			)

		rows.append(u' & '.join(cells))

	return tex % u' \\tabularnewline\n \\hline\n'.join(rows)

#============================================================
def export_results_for_gnuplot(results=None, filename=None, show_year=True):

	if filename is None:
		filename = gmTools.get_unique_filename(prefix = u'gm2gpl-', suffix = '.dat')

	# sort results into series by test type
	series = {}
	for r in results:
		try:
			series[r['unified_name']].append(r)
		except KeyError:
			series[r['unified_name']] = [r]

	gp_data = codecs.open(filename, 'wb', 'utf8')

	gp_data.write(u'# %s\n' % _('GNUmed test results export for Gnuplot plotting'))
	gp_data.write(u'# -------------------------------------------------------------\n')
	gp_data.write(u'# first line of index: test type abbreviation & name\n')
	gp_data.write(u'#\n')
	gp_data.write(u'# clin_when at full precision\n')
	gp_data.write(u'# value\n')
	gp_data.write(u'# unit\n')
	gp_data.write(u'# unified (target or normal) range: lower bound\n')
	gp_data.write(u'# unified (target or normal) range: upper bound\n')
	gp_data.write(u'# normal range: lower bound\n')
	gp_data.write(u'# normal range: upper bound\n')
	gp_data.write(u'# target range: lower bound\n')
	gp_data.write(u'# target range: upper bound\n')
	gp_data.write(u'# clin_when formatted into string as x-axis tic label\n')
	gp_data.write(u'# -------------------------------------------------------------\n')

	for test_type in series.keys():
		if len(series[test_type]) == 0:
			continue

		r = series[test_type][0]
		title = u'%s (%s)' % (
			r['unified_abbrev'],
			r['unified_name']
		)
		gp_data.write(u'\n\n"%s" "%s"\n' % (title, title))

		prev_date = None
		prev_year = None
		for r in series[test_type]:
			curr_date = r['clin_when'].strftime('%Y-%m-%d')
			if curr_date == prev_date:
				gp_data.write(u'\n# %s\n' % _('blank line inserted to allow for discontinued line drawing for same-day values'))
			if show_year:
				if r['clin_when'].year == prev_year:
					when_template = '%b %d %H:%M'
				else:
					when_template = '%b %d %H:%M (%Y)'
				prev_year = r['clin_when'].year
			else:
				when_template = '%b %d'
			gp_data.write (u'%s %s "%s" %s %s %s %s %s %s "%s"\n' % (
				r['clin_when'].strftime('%Y-%m-%d_%H:%M'),
				r['unified_val'],
				gmTools.coalesce(r['val_unit'], u'"<?>"'),
				gmTools.coalesce(r['unified_target_min'], u'"<?>"'),
				gmTools.coalesce(r['unified_target_max'], u'"<?>"'),
				gmTools.coalesce(r['val_normal_min'], u'"<?>"'),
				gmTools.coalesce(r['val_normal_max'], u'"<?>"'),
				gmTools.coalesce(r['val_target_min'], u'"<?>"'),
				gmTools.coalesce(r['val_target_max'], u'"<?>"'),
				gmDateTime.pydt_strftime (
					r['clin_when'],
					format = when_template,
					accuracy = gmDateTime.acc_minutes
				)
			))
			prev_date = curr_date

	gp_data.close()

	return filename
#============================================================
class cLabResult(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one lab result."""

	_cmd_fetch_payload = """
		select *, xmin_test_result from v_results4lab_req
		where pk_result=%s"""
	_cmds_lock_rows_for_update = [
		"""select 1 from test_result where pk=%(pk_result)s and xmin=%(xmin_test_result)s for update"""
	]
	_cmds_store_payload = [
		"""update test_result set
				clin_when = %(val_when)s,
				narrative = %(progress_note_result)s,
				fk_type = %(pk_test_type)s,
				val_num = %(val_num)s::numeric,
				val_alpha = %(val_alpha)s,
				val_unit = %(val_unit)s,
				val_normal_min = %(val_normal_min)s,
				val_normal_max = %(val_normal_max)s,
				val_normal_range = %(val_normal_range)s,
				val_target_min = %(val_target_min)s,
				val_target_max = %(val_target_max)s,
				val_target_range = %(val_target_range)s,
				abnormality_indicator = %(abnormal)s,
				norm_ref_group = %(ref_group)s,
				note_provider = %(note_provider)s,
				material = %(material)s,
				material_detail = %(material_detail)s
			where pk = %(pk_result)s""",
		"""select xmin_test_result from v_results4lab_req where pk_result=%(pk_result)s"""
		]

	_updatable_fields = [
		'val_when',
		'progress_note_result',
		'val_num',
		'val_alpha',
		'val_unit',
		'val_normal_min',
		'val_normal_max',
		'val_normal_range',
		'val_target_min',
		'val_target_max',
		'val_target_range',
		'abnormal',
		'ref_group',
		'note_provider',
		'material',
		'material_detail'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, row=None):
		"""Instantiate.

		aPK_obj as dict:
			- patient_id
			- when_field (see view definition)
			- when
			- test_type
			- val_num
			- val_alpha
			- unit
		"""
		# instantiate from row data ?
		if aPK_obj is None:
			gmBusinessDBObject.cBusinessDBObject.__init__(self, row=row)
			return
		pk = aPK_obj
		# find PK from row data ?
		if type(aPK_obj) == types.DictType:
			# sanity checks
			if None in [aPK_obj['patient_id'], aPK_obj['when'], aPK_obj['when_field'], aPK_obj['test_type'], aPK_obj['unit']]:
				raise gmExceptions.ConstructorError, 'parameter error: %s' % aPK_obj
			if (aPK_obj['val_num'] is None) and (aPK_obj['val_alpha'] is None):
				raise gmExceptions.ConstructorError, 'parameter error: val_num and val_alpha cannot both be None'
			# get PK
			where_snippets = [
				'pk_patient=%(patient_id)s',
				'pk_test_type=%(test_type)s',
				'%s=%%(when)s' % aPK_obj['when_field'],
				'val_unit=%(unit)s'
			]
			if aPK_obj['val_num'] is not None:
				where_snippets.append('val_num=%(val_num)s::numeric')
			if aPK_obj['val_alpha'] is not None:
				where_snippets.append('val_alpha=%(val_alpha)s')

			where_clause = ' and '.join(where_snippets)
			cmd = "select pk_result from v_results4lab_req where %s" % where_clause
			data = gmPG.run_ro_query('historica', cmd, None, aPK_obj)
			if data is None:
				raise gmExceptions.ConstructorError, 'error getting lab result for: %s' % aPK_obj
			if len(data) == 0:
				raise gmExceptions.NoSuchClinItemError, 'no lab result for: %s' % aPK_obj
			pk = data[0][0]
		# instantiate class
		gmBusinessDBObject.cBusinessDBObject.__init__(self, aPK_obj=pk)
	#--------------------------------------------------------
	def get_patient(self):
		cmd = """
			select
				%s,
				vbp.title,
				vbp.firstnames,
				vbp.lastnames,
				vbp.dob
			from v_basic_person vbp
			where vbp.pk_identity=%%s""" % self._payload[self._idx['pk_patient']]
		pat = gmPG.run_ro_query('historica', cmd, None, self._payload[self._idx['pk_patient']])
		return pat[0]
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
		if type(aPK_obj) == types.DictType:
			# sanity check
			try:
				aPK_obj['req_id']
				aPK_obj['lab']
			except:
				_log.exception('[%s:??]: faulty <aPK_obj> structure: [%s]' % (self.__class__.__name__, aPK_obj), sys.exc_info())
				raise gmExceptions.ConstructorError, '[%s:??]: cannot derive PK from [%s]' % (self.__class__.__name__, aPK_obj)
			# generate query
			where_snippets = []
			vals = {}
			where_snippets.append('request_id=%(req_id)s')
			if type(aPK_obj['lab']) == types.IntType:
				where_snippets.append('pk_test_org=%(lab)s')
			else:
				where_snippets.append('lab_name=%(lab)s')
			where_clause = ' and '.join(where_snippets)
			cmd = "select pk_request from v_lab_requests where %s" % where_clause
			# get pk
			data = gmPG.run_ro_query('historica', cmd, None, aPK_obj)
			if data is None:
				raise gmExceptions.ConstructorError, '[%s:??]: error getting lab request for [%s]' % (self.__class__.__name__, aPK_obj)
			if len(data) == 0:
				raise gmExceptions.NoSuchClinItemError, '[%s:??]: no lab request for [%s]' % (self.__class__.__name__, aPK_obj)
			pk = data[0][0]
		# instantiate class
		gmBusinessDBObject.cBusinessDBObject.__init__(self, aPK_obj=pk)
	#--------------------------------------------------------
	def get_patient(self):
		cmd = """
			select vpi.pk_patient, vbp.title, vbp.firstnames, vbp.lastnames, vbp.dob
			from v_pat_items vpi, v_basic_person vbp
			where
				vpi.pk_item=%s
					and
				vbp.pk_identity=vpi.pk_patient"""
		pat = gmPG.run_ro_query('historica', cmd, None, self._payload[self._idx['pk_item']])
		if pat is None:
			_log.error('cannot get patient for lab request [%s]' % self._payload[self._idx['pk_item']])
			return None
		if len(pat) == 0:
			_log.error('no patient associated with lab request [%s]' % self._payload[self._idx['pk_item']])
			return None
		return pat[0]
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
	req = None
	aPK_obj = {
		'lab': lab,
		'req_id': req_id
	}
	try:
		req = cLabRequest (aPK_obj)
	except gmExceptions.NoSuchClinItemError, msg:
		_log.info('%s: will try to create lab request' % str(msg))
	except gmExceptions.ConstructorError, msg:
		_log.exception(str(msg), sys.exc_info(), verbose=0)
		return (False, msg)
	# found
	if req is not None:
		db_pat = req.get_patient()
		if db_pat is None:
			_log.error('cannot cross-check patient on lab request')
			return (None, '')
		# yes but ambigous
		if pat_id != db_pat[0]:
			_log.error('lab request found for [%s:%s] but patient mismatch: expected [%s], in DB [%s]' % (lab, req_id, pat_id, db_pat))
			me = '$RCSfile: gmPathLab.py,v $ $Revision: 1.81 $'
			to = 'user'
			prob = _('The lab request already exists but belongs to a different patient.')
			sol = _('Verify which patient this lab request really belongs to.')
			ctxt = _('lab [%s], request ID [%s], expected link with patient [%s], currently linked to patient [%s]') % (lab, req_id, pat_id, db_pat)
			cat = 'lab'
			status, data = gmPG.add_housekeeping_todo(me, to, prob, sol, ctxt, cat)
			return (None, data)
		return (True, req)
	# not found
	queries = []
	if type(lab) is types.IntType:
		cmd = "insert into lab_request (fk_encounter, fk_episode, fk_test_org, request_id) values (%s, %s, %s, %s)"
	else:
		cmd = "insert into lab_request (fk_encounter, fk_episode, fk_test_org, request_id) values (%s, %s, (select pk from test_org where internal_OBSOLETE_name=%s), %s)"
	queries.append((cmd, [encounter_id, episode_id, str(lab), req_id]))
	cmd = "select currval('lab_request_pk_seq')"
	queries.append((cmd, []))
	# insert new
	result, err = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, err)
	try:
		req = cLabRequest(aPK_obj=result[0][0])
	except gmExceptions.ConstructorError, msg:
		_log.exception(str(msg), sys.exc_info(), verbose=0)
		return (False, msg)
	return (True, req)
#------------------------------------------------------------
def create_lab_result(patient_id=None, when_field=None, when=None, test_type=None, val_num=None, val_alpha=None, unit=None, encounter_id=None, request=None):
	tres = None
	data = {
		'patient_id': patient_id,
		'when_field': when_field,
		'when': when,
		'test_type': test_type,
		'val_num': val_num,
		'val_alpha': val_alpha,
		'unit': unit
	}
	try:
		tres = cLabResult(aPK_obj=data)
		# exists already, so fail
		_log.error('will not overwrite existing test result')
		_log.debug(str(tres))
		return (None, tres)
	except gmExceptions.NoSuchClinItemError:
		_log.debug('test result not found - as expected, will create it')
	except gmExceptions.ConstructorError, msg:
		_log.exception(str(msg), sys.exc_info(), verbose=0)
		return (False, msg)
	if request is None:
		return (False, _('need lab request when inserting lab result'))
	# not found
	if encounter_id is None:
		encounter_id = request['pk_encounter']
	queries = []
	cmd = "insert into test_result (fk_encounter, fk_episode, fk_type, val_num, val_alpha, val_unit) values (%s, %s, %s, %s, %s, %s)"
	queries.append((cmd, [encounter_id, request['pk_episode'], test_type, val_num, val_alpha, unit]))
	cmd = "insert into lnk_result2lab_req (fk_result, fk_request) values ((select currval('test_result_pk_seq')), %s)"
	queries.append((cmd, [request['pk_request']]))
	cmd = "select currval('test_result_pk_seq')"
	queries.append((cmd, []))
	# insert new
	result, err = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, err)
	try:
		tres = cLabResult(aPK_obj=result[0][0])
	except gmExceptions.ConstructorError, msg:
		_log.exception(str(msg), sys.exc_info(), verbose=0)
		return (False, msg)
	return (True, tres)
#------------------------------------------------------------
def get_unreviewed_results(limit=50):
	# sanity check
	if limit < 1:
		limit = 1
	# retrieve one more row than needed so we know there's more available ;-)
	lim = limit + 1
	cmd = """
		select pk_result
		from v_results4lab_req
		where reviewed is false
		order by pk_patient
		limit %s""" % lim
	rows = gmPG.run_ro_query('historica', cmd)
	if rows is None:
		_log.error('error retrieving unreviewed lab results')
		return (None, _('error retrieving unreviewed lab results'))
	if len(rows) == 0:
		return (False, [])
	# more than LIMIT rows ?
	if len(rows) == lim:
		more_avail = True
		# but deliver only LIMIT rows so that our assumption holds true...
		del rows[limit]
	else:
		more_avail = False
	results = []
	for row in rows:
		try:
			results.append(cLabResult(aPK_obj=row[0]))
		except gmExceptions.ConstructorError:
			_log.exception('skipping unreviewed lab result [%s]' % row[0], sys.exc_info(), verbose=0)
	return (more_avail, results)
#------------------------------------------------------------
def get_pending_requests(limit=250):
	lim = limit + 1
	cmd = "select pk from lab_request where is_pending is true limit %s" % lim
	rows = gmPG.run_ro_query('historica', cmd)
	if rows is None:
		_log.error('error retrieving pending lab requests')
		return (None, None)
	if len(rows) == 0:
		return (False, [])
	results = []
	# more than LIMIT rows ?
	if len(rows) == lim:
		too_many = True
		# but deliver only LIMIT rows so that our assumption holds true...
		del rows[limit]
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
	if type(lab) == types.IntType:
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
	rows = gmPG.run_ro_query('historica', cmd, None, lab)
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
		return False, u'mass: cannot convert <%s> to Decimal' % mass

	converted, height = gmTools.input2decimal(height)
	if not converted:
		return False, u'height: cannot convert <%s> to Decimal' % height

	approx_surface = (height / decimal.Decimal(100))**2
	bmi = mass / approx_surface

	print mass, height, '->', approx_surface, '->', bmi

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

	gmI18N.activate_locale()
	gmI18N.install_domain()

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
		print tr
		return tr
	#------------------------------------------
	def test_delete_test_result():
		tr = test_create_test_result()
		delete_test_result(tr)
	#------------------------------------------
	def test_result():
		r = cTestResult(aPK_obj=1)
		print r
		print r.reference_ranges
	#------------------------------------------
	def test_lab_result():
		print "test_result()"
#		lab_result = cLabResult(aPK_obj=4)
		data = {
			'patient_id': 12,
			'when_field': 'val_when',
			'when': '2000-09-17 18:23:00+02',
			'test_type': 9,
			'val_num': 17.3,
			'val_alpha': None,
			'unit': 'mg/l'
		}
		lab_result = cLabResult(aPK_obj=data)
		print lab_result
		fields = lab_result.get_fields()
		for field in fields:
			print field, ':', lab_result[field]
		print "updatable:", lab_result.get_updatable_fields()
		print time.time()
		print lab_result.get_patient()
		print time.time()
	#------------------------------------------
	def test_request():
		print "test_request()"
		try:
#			lab_req = cLabRequest(aPK_obj=1)
#			lab_req = cLabRequest(req_id='EML#SC937-0176-CEC#11', lab=2)
			data = {
				'req_id': 'EML#SC937-0176-CEC#11',
				'lab': 'Enterprise Main Lab'
			}
			lab_req = cLabRequest(aPK_obj=data)
		except gmExceptions.ConstructorError, msg:
			print "no such lab request:", msg
			return
		print lab_req
		fields = lab_req.get_fields()
		for field in fields:
			print field, ':', lab_req[field]
		print "updatable:", lab_req.get_updatable_fields()
		print time.time()
		print lab_req.get_patient()
		print time.time()
	#--------------------------------------------------------
	def test_unreviewed():
		data = get_unreviewed_results()
		for result in data:
			print result
	#--------------------------------------------------------
	def test_pending():
		data = get_pending_requests()
		for result in data:
			print result
	#--------------------------------------------------------
	def test_create_measurement_type():
		print create_measurement_type (
			lab = None,
			abbrev = u'tBZ2',
			unit = u'mg%',
			name = 'BZ (test 2)'
		)
	#--------------------------------------------------------
	def test_meta_test_type():
		mtt = cMetaTestType(aPK_obj = 1)
		print mtt
		print get_meta_test_types()
	#--------------------------------------------------------
	def test_test_type():
		tt = cMeasurementType(aPK_obj = 1)
		print tt
		print get_measurement_types()
	#--------------------------------------------------------
	def test_format_test_results():
		results = [
			cTestResult(aPK_obj=1),
			cTestResult(aPK_obj=2),
			cTestResult(aPK_obj=3)
#			cTestResult(aPK_obj=4)
		]
		print format_test_results(results = results)
	#--------------------------------------------------------
	def test_calculate_bmi():
		done, data = calculate_bmi(mass = sys.argv[2], height = sys.argv[3])
		bmi, low, high = data

		print "BMI:", bmi
		print "low:", low, "kg"
		print "hi :", high, "kg"

	#--------------------------------------------------------

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
	#test_format_test_results()
	test_calculate_bmi()

#============================================================

