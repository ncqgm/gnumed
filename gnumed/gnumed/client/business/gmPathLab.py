"""GNUmed vaccination related business objects.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmPathLab.py,v $
# $Id: gmPathLab.py,v 1.66 2009-01-02 11:34:50 ncq Exp $
__version__ = "$Revision: 1.66 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import types, sys, logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmLog2, gmDateTime, gmI18N
	gmDateTime.init()
	gmI18N.activate_locale()
from Gnumed.pycommon import gmExceptions, gmBusinessDBObject, gmPG2, gmTools


_log = logging.getLogger('gm.lab')
_log.info(__version__)

# FIXME: use psyopg2 dbapi extension of named cursors - they are *server* side !

#============================================================
class cTestType(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one test result type."""

	_cmd_fetch_payload = u"""select *, xmin from clin.test_type where pk = %s"""

	_cmds_store_payload = [
		u"""update clin.test_type set
				fk_test_org = %(fk_test_org)s,
				code = %(code)s,
				coding_system = %(coding_system)s,
				name = %(name)s,
				comment = %(comment)s,
				conversion_unit = %(conversion_unit)s
			where pk = %(pk)s""",
		u"""select xmin from clin.test_type where pk = %(pk)"""
	]

	_updatable_fields = [
		'fk_test_org',
		'code',
		'coding_system',
		'name',
		'comment',
		'conversion_unit'
	]
	#--------------------------------------------------------
	def __setitem__(self, attribute, value):

		# find fk_test_org from name
		if (attribute == 'fk_test_org') and (value is not None):
			try:
				int(value)
			except:
				cmd = u"select pk from clin.test_org where internal_name = %(val)s"
				rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'val': value}}])
				if len(rows) == 0:
					raise ValueError('[%s]: no test org for [%s], cannot set <%s>' % (self.__class__.__name__, value, attribute))
				value = rows[0][0]

		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)
#------------------------------------------------------------
def find_test_type(lab=None, code=None, name=None):

		where_snippets = []

		if lab is None:
			where_snippets.append('fk_test_org is null')
		else:
			try:
				int(lab)
				where_snippets.append('fk_test_org = %(lab)s')
			except (TypeError, ValueError):
				where_snippets.append('fk_test_org = (select pk from clin.test_org where internal_name=%(lab)s)')

		if (code is None) and (name is None):
			raise ArgumentError('must have <code> and/or <name> set')

		if code is not None:
			where_snippets.append('code = %(code)s')

		if name is not None:
			where_snippets.append('name = %(name)s')

		where_clause = u' and '.join(where_snippets)
		cmd = u"select *, xmin from clin.test_type where %s" % where_clause
		args = {'lab': lab, 'code': code, 'name': name}

		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

		if len(rows) == 0:
			return None

		tt = cTestType(row = {'pk_field': 'pk', 'data': rows[0], 'idx': idx})
		return tt
#------------------------------------------------------------
def create_test_type(lab=None, code=None, unit=None, name=None):
	"""Create or get test type."""

	ttype = find_test_type(lab = lab, code = code, name = name)
	# found ?
	if ttype is not None:
		return ttype
#		if name is None:
#			return ttype
#		db_lname = ttype['name']
#		# yes but ambigous
#		if name != db_lname:
#			_log.error('test type found for [%s:%s] but long name mismatch: expected [%s], in DB [%s]' % (lab, code, name, db_lname))
#			me = '$RCSfile: gmPathLab.py,v $ $Revision: 1.66 $'
#			to = 'user'
#			prob = _('The test type already exists but the long name is different. '
#					'The test facility may have changed the descriptive name of this test.')
#			sol = _('Verify with facility and change the old descriptive name to the new one.')
#			ctxt = _('lab [%s], code [%s], expected long name [%s], existing long name [%s], unit [%s]') % (lab, code, name, db_lname, unit)
#			cat = 'lab'
#			status, data = gmPG.add_housekeeping_todo(me, to, prob, sol, ctxt, cat)
#			return None
#		return ttype

	_log.debug('creating test type [%s:%s:%s:%s]', lab, code, name, unit)

	# not found, so create it
	if unit is None:
		_log.error('need <unit> to create test type: %s:%s:%s:%s' % (lab, code, name, unit))
		raise ValueError('need <unit> to create test type')

	# make query
	cols = []
	val_snippets = []
	vals = {}

	# lab
	if lab is not None:
		cols.append('fk_test_org')
		try:
			vals['lab'] = int(lab)
			val_snippets.append('%(lab)s')
		except:
			vals['lab'] = lab
			val_snippets.append('(select pk from clin.test_org where internal_name = %(lab)s)')

	# code
	cols.append('code')
	val_snippets.append('%(code)s')
	vals['code'] = code

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
		{'cmd': u"select *, xmin from clin.test_type where pk = currval(pg_get_serial_sequence('clin.test_type', 'pk'))"}
	]
	rows, idx = gmPG2.run_rw_queries(queries = queries, get_col_idx = True, return_data = True)
	ttype = cTestType(row = {'pk_field': 'pk', 'data': rows[0], 'idx': idx})

	return ttype
#============================================================
class cTestResult(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one test result."""

	_cmd_fetch_payload = u"select * from clin.v_test_results where pk_test_result = %s"

	_cmds_store_payload = [
		u"""update clin.test_result set
				clin_when = %(clin_when)s,
				narrative = %(comment)s,
				val_num = %(val_num)s,
				val_alpha = %(val_alpha)s,
				val_unit = %(val_unit)s,
				val_normal_min = %(val_normal_min)s,
				val_normal_max = %(val_normal_max)s,
				val_normal_range = %(val_normal_range)s,
				val_target_min = %(val_target_min)s,
				val_target_max = %(val_target_max)s,
				val_target_range = %(val_target_range)s,
				abnormality_indicator = %(abnormality_indicator)s,
				norm_ref_group = %(norm_ref_group)s,
				note_test_org = %(note_test_org)s,
				material = %(material)s,
				material_detail = %(material_detail)s,
				fk_intended_reviewer = %(pk_intended_reviewer)s,
				fk_encounter = %(pk_encounter)s,
				fk_episode = %(pk_episode)s,
				fk_type = %(pk_test_type)s
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
		'pk_test_type'
	]
	#--------------------------------------------------------
	def format(self):

		lines = []

		lines.append(u' %s %s (%s): %s %s (%s)' % (
			self._payload[self._idx['clin_when']].strftime('%d.%m. %H:%M'),
			self._payload[self._idx['unified_code']],
			self._payload[self._idx['unified_name']],
			self._payload[self._idx['unified_val']],
			self._payload[self._idx['val_unit']],
			self._payload[self._idx['abnormality_indicator']]
		))
		if gmTools.coalesce(self._payload[self._idx['comment']], u'').strip() != u'':
			lines.append(_('   Doc: %s') % self._payload[self._idx['comment']].strip())
		if gmTools.coalesce(self._payload[self._idx['comment']], u'').strip() != u'':
			lines.append(_('   MTA: %s') % self._payload[self._idx['note_test_org']].strip())
		if self._payload[self._idx['reviewed']]:
			lines.append(u'   %s @ %s: %s, %s' % (
				self._payload[self._idx['last_reviewer']],
				self._payload[self._idx['last_reviewed']].strftime('%x %H:%M'),
				gmTools.bool2subst(self._payload[self._idx['is_technically_abnormal']], _('abnormal'), _('normal')),
				gmTools.bool2subst(self._payload[self._idx['is_clinically_relevant']], _('relevant'), _('not relevant'))
			))

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
	def set_review(self, technically_abnormal=None, clinically_relevant=None, comment=None, make_me_responsible=False):

		if comment is not None:
			comment = comment.strip()

		if ((technically_abnormal is None) and
			(clinically_relevant is None) and
			(comment is None) and
			(make_me_responsible is False)):
				return True

		# FIXME: this is not concurrency safe
		if self._payload[self._idx['reviewed']]:
			self.__change_existing_review (
				technically_abnormal = technically_abnormal,
				clinically_relevant = clinically_relevant,
				comment = comment
			)
		else:
			self.__set_new_review (
				technically_abnormal = technically_abnormal,
				clinically_relevant = clinically_relevant,
				comment = comment
			)

		if make_me_responsible is True:
			cmd = u"select pk from dem.staff where db_user = current_user"
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
			self['pk_intended_reviewer'] = rows[0][0]
			self.save_payload()
		else:
			self.refetch_payload()
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
insert into clin.reviewed_test_results (
	fk_reviewed_row,
	is_technically_abnormal,
	clinically_relevant,
	comment
) values (
	%(pk)s,
	%(abnormal)s,
	%(relevant)s,
	%(cmt)s
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

			- if technically abnormal/clinically relevant/comment are
			  None (or empty) they are not set
		"""
		args = {
			'pk_row': self._payload[self._idx['pk_test_result']],
			'abnormal': technically_abnormal,
			'relevant': clinically_relevant
		}

		set_parts = []

		if technically_abnormal is not None:
			set_parts.append(u'is_technically_abnormal = %(abnormal)s')

		if clinically_relevant is not None:
			set_parts.append(u'clinically_relevant= %(relevant)s')

		if comment is not None:
			set_parts.append('comment = %(cmt)s')
			args['cmt'] = comment

		cmd = u"""
update clin.reviewed_test_results set
	fk_reviewer = (select pk from dem.staff where db_user = current_user),
	%s
where
	fk_reviewed_row = %%(pk_row)s
""" % u',\n	'.join(set_parts)

		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
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
				clin_when=%(val_when)s,
				narrative=%(progress_note_result)s,
				fk_type=%(pk_test_type)s,
				val_num=%(val_num)s::numeric,
				val_alpha=%(val_alpha)s,
				val_unit=%(val_unit)s,
				val_normal_min=%(val_normal_min)s,
				val_normal_max=%(val_normal_max)s,
				val_normal_range=%(val_normal_range)s,
				val_target_min=%(val_target_min)s,
				val_target_max=%(val_target_max)s,
				val_target_range=%(val_target_range)s,
				abnormality_indicator=%(abnormal)s,
				norm_ref_group=%(ref_group)s,
				note_provider=%(note_provider)s,
				material=%(material)s,
				material_detail=%(material_detail)s
			where pk=%(pk_result)s""",
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
			me = '$RCSfile: gmPathLab.py,v $ $Revision: 1.66 $'
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
		cmd = "insert into lab_request (fk_encounter, fk_episode, fk_test_org, request_id) values (%s, %s, (select pk from test_org where internal_name=%s), %s)"
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

	- lab either test_org PK or test_org.internal_name
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
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':
	import time

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
	def test_create_test_type():
		print create_test_type (
			lab = None,
			code = u'tBZ2',
			unit = u'mg%',
			name = 'BZ (test 2)'
		)
	#--------------------------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):

		#test_result()
		#test_create_test_result()
		test_delete_test_result()
		#test_create_test_type()
		#test_lab_result()
		#test_request()
		#test_create_result()
		#test_unreviewed()
		#test_pending()

#============================================================
# $Log: gmPathLab.py,v $
# Revision 1.66  2009-01-02 11:34:50  ncq
# - cleanup
#
# Revision 1.65  2008/10/22 12:04:55  ncq
# - use %x in strftime
#
# Revision 1.64  2008/07/14 13:45:08  ncq
# - add .format to test results
#
# Revision 1.63  2008/06/24 13:54:47  ncq
# - delete_test_result and test
#
# Revision 1.62  2008/06/23 21:49:19  ncq
# - pimp cTestType, find/create_test_type
# - some tests
#
# Revision 1.61  2008/06/19 15:24:47  ncq
# - fix updating cTestResult
#
# Revision 1.60  2008/06/16 15:01:53  ncq
# - create_test_result
# - test suite cleanup
# - reference_ranges property on cTestResult
#
# Revision 1.59  2008/04/22 21:15:16  ncq
# - cTestResult
#
# Revision 1.58  2008/02/25 17:31:41  ncq
# - logging cleanup
#
# Revision 1.57  2008/01/30 13:34:50  ncq
# - switch to std lib logging
#
# Revision 1.56  2007/07/17 11:13:25  ncq
# - no more gmClinItem
#
# Revision 1.55  2007/03/08 11:31:08  ncq
# - just cleanup
#
# Revision 1.54  2007/01/09 12:56:18  ncq
# - comment
#
# Revision 1.53  2006/10/25 07:17:40  ncq
# - no more gmPG
# - no more cClinItem
#
# Revision 1.52  2006/07/19 20:25:00  ncq
# - gmPyCompat.py is history
#
# Revision 1.51  2005/10/26 21:16:26  ncq
# - adjust to changes in reviewed status handling
#
# Revision 1.50  2005/04/27 12:37:32  sjtan
#
# id_patient -> pk_patient
#
# Revision 1.49  2005/03/23 18:31:19  ncq
# - v_patient_items -> v_pat_items
#
# Revision 1.48  2005/02/15 18:29:03  ncq
# - test_result.id -> pk
#
# Revision 1.47  2005/02/13 15:45:31  ncq
# - v_basic_person.i_pk -> pk_identity
#
# Revision 1.46  2005/01/02 19:55:30  ncq
# - don't need _xmins_refetch_col_pos anymore
#
# Revision 1.45  2004/12/27 16:48:11  ncq
# - fix create_lab_request() to use proper aPK_obj syntax
#
# Revision 1.44  2004/12/20 16:45:49  ncq
# - gmBusinessDBObject now requires refetching of XMIN after save_payload
#
# Revision 1.43  2004/12/14 03:27:56  ihaywood
# xmin_rest_result -> xmin_test_result
#
# Carlos used a very old version of the SOAP2.py for no good reason, fixed.
#
# Revision 1.42  2004/11/03 22:32:34  ncq
# - support _cmds_lock_rows_for_update in business object base class
#
# Revision 1.41  2004/10/18 09:48:20  ncq
# - must have been asleep at the keyboard
#
# Revision 1.40  2004/10/18 09:46:02  ncq
# - fix create_lab_result()
#
# Revision 1.39  2004/10/15 09:05:08  ncq
# - converted cLabResult to allow use of row __init__()
#
# Revision 1.38  2004/10/12 18:32:52  ncq
# - allow cLabRequest and cTestType to be filled from bulk fetch row data
# - cLabResult not adapted yet
#
# Revision 1.37  2004/09/29 10:25:04  ncq
# - basic_unit->conversion_unit
#
# Revision 1.36  2004/09/18 13:51:56  ncq
# - support val_target_*
#
# Revision 1.35  2004/07/02 00:20:54  ncq
# - v_patient_items.id_item -> pk_item
#
# Revision 1.34  2004/06/28 15:14:50  ncq
# - use v_lab_requests
#
# Revision 1.33  2004/06/28 12:18:52  ncq
# - more id_* -> fk_*
#
# Revision 1.32  2004/06/26 07:33:55  ncq
# - id_episode -> fk/pk_episode
#
# Revision 1.31  2004/06/18 13:33:58  ncq
# - saner logging
#
# Revision 1.30  2004/06/16 17:16:56  ncq
# - correctly handle val_num/val_alpha in create_lab_result so
#   we can safely detect duplicates
#
# Revision 1.29  2004/06/01 23:56:39  ncq
# - improved error handling in several places
#
# Revision 1.28  2004/05/30 20:12:33  ncq
# - make create_lab_result() handle request objects, not request_id
#
# Revision 1.27  2004/05/26 15:45:25  ncq
# - get_next_request_ID()
#
# Revision 1.26  2004/05/25 13:29:20  ncq
# - order unreviewed results by pk_patient
#
# Revision 1.25  2004/05/25 00:20:47  ncq
# - fix reversal of is_pending in get_pending_requests()
#
# Revision 1.24  2004/05/25 00:07:31  ncq
# - speed up get_patient in test_result
#
# Revision 1.23  2004/05/24 23:34:53  ncq
# - optimize get_patient in cLabRequest()
#
# Revision 1.22  2004/05/24 14:59:45  ncq
# - get_pending_requests()
#
# Revision 1.21  2004/05/24 14:35:00  ncq
# - get_unreviewed_results() now returns status of more_available
#
# Revision 1.20  2004/05/24 14:15:54  ncq
# - get_unreviewed_results()
#
# Revision 1.19  2004/05/14 13:17:27  ncq
# - less useless verbosity
# - cleanup
#
# Revision 1.18  2004/05/13 00:03:17  ncq
# - aPKey -> aPK_obj
#
# Revision 1.17  2004/05/11 01:37:21  ncq
# - create_test_result -> create_lab_result
# - need to insert into lnk_result2lab_req, too, in create_lab_result
#
# Revision 1.16  2004/05/08 22:13:11  ncq
# - cleanup
#
# Revision 1.15  2004/05/08 17:29:18  ncq
# - us NoSuchClinItemError
#
# Revision 1.14  2004/05/06 23:37:19  ncq
# - lab result _update_payload update
# - lab result.__init__ now supports values other than the PK
# - add create_test_result()
#
# Revision 1.13  2004/05/04 07:55:00  ncq
# - correctly detect "no such lab request" condition in create_lab_request()
# - fail gracefully in test_request()
#
# Revision 1.12  2004/05/03 22:25:10  shilbert
# - some typos fixed
#
# Revision 1.11  2004/05/03 15:30:58  ncq
# - add create_lab_request()
# - add cLabResult.get_patient()
#
# Revision 1.10  2004/05/03 12:50:34  ncq
# - relative imports
# - str()ify some things
#
# Revision 1.9  2004/05/02 22:56:36  ncq
# - add create_lab_request()
#
# Revision 1.8  2004/04/26 21:56:19  ncq
# - add cLabRequest.get_patient()
# - add create_test_type()
#
# Revision 1.7  2004/04/21 15:27:38  ncq
# - map 8407 to string for ldt import
#
# Revision 1.6  2004/04/20 00:14:30  ncq
# - cTestType invented
#
# Revision 1.5  2004/04/19 12:42:41  ncq
# - fix cLabRequest._cms_store_payload
# - modularize testing
#
# Revision 1.4  2004/04/18 18:50:36  ncq
# - override __init__() thusly removing the unholy _pre/post_init() business
#
# Revision 1.3  2004/04/12 22:59:38  ncq
# - add lab request
#
# Revision 1.2  2004/04/11 12:07:54  ncq
# - better unit testing
#
# Revision 1.1  2004/04/11 12:04:55  ncq
# - first version
#
