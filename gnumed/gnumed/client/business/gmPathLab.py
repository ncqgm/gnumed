"""GnuMed vaccination related business objects.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmPathLab.py,v $
# $Id: gmPathLab.py,v 1.27 2004-05-26 15:45:25 ncq Exp $
__version__ = "$Revision: 1.27 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import types, sys

from Gnumed.pycommon import gmLog, gmPG, gmExceptions
from Gnumed.business import gmClinItem
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
# FIXME: TODO
class cTestResult(gmClinItem.cClinItem):
	def link_to_lab_request(self):
		pass
#============================================================
class cLabResult(gmClinItem.cClinItem):
	"""Represents one lab result."""

	_cmd_fetch_payload = """
		select * from v_results4lab_req
		where pk_result=%s"""

	_cmds_store_payload = [
		"""select 1 from test_result where id=%(pk_result)s for update""",
		"""update test_result set
				clin_when=%(val_when)s,
				narrative=%(progress_note_result)s,
				fk_type=%(pk_test_type)s,
				val_num=%(val_num)s,
				val_alpha=%(val_alpha)s,
				val_unit=%(val_unit)s,
				val_normal_min=%(val_normal_min)s,
				val_normal_max=%(val_normal_max)s,
				val_normal_range=%(val_normal_range)s,
				technically_abnormal=%(abnormal)s,
				norm_ref_group=%(ref_group)s,
				note_provider=%(note_provider)s,
				material=%(material)s,
				material_detail=%(material_detail)s,
				reviewed_by_clinician=%(reviewed)s::bool,
				fk_reviewer=%(pk_reviewer)s,
				clinically_relevant=%(relevant)s::bool
			where id=%(pk_result)s"""
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
		'abnormal',
		'ref_group',
		'note_provider',
		'material',
		'material_detail',
		'reviewed',
		'pk_reviewer',
		'relevant'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, patient_id=None, when_field=None, when=None, test_type=None, val_num=None, val_alpha=None, unit=None):
		pk = aPK_obj
		if pk is None:
			# sanity checks
			if None in [patient_id, when, when_field, test_type, unit]:
				raise gmExceptions.ConstructorError, 'parameter error: pat=%s %s=%s test_type=%s val_num=%s val_alpha=%s unit=%s' % (patient_id, when_field, when, test_type, val_num, val_alpha, unit)
			if (val_num is None) and (val_alpha is None):
				raise gmExceptions.ConstructorError, 'parameter error: val_num and val_alpha cannot both be None'
			# get PK
			params = {
				'pat_id': patient_id,
				'type': test_type,
				'valn': val_num,
				'vala': val_alpha,
				'when': when,
				'unit': unit
			}
			where_snippets = [
				'pk_patient=%(pat_id)s',
				'pk_test_type=%(type)s',
				'val_num=%(valn)s::float',
				'val_alpha=%(vala)s',
				'%s=%%(when)s' % when_field,
				'val_unit=%(unit)s'
			]
			where_clause = ' and '.join(where_snippets)
			cmd = "select pk_result from v_results4lab_req where %s" % where_clause
			data = gmPG.run_ro_query('historica', cmd, None, params)
			if data is None:
				raise gmExceptions.ConstructorError, 'error getting lab result for: pat=%s %s=%s test_type=%s val_num=%s val_alpha=%s unit=%s' % (patient_id, when_field, when, test_type, val_num, val_alpha, unit)
			if len(data) == 0:
				raise gmExceptions.NoSuchClinItemError, 'no lab result for: pat=%s %s=%s test_type=%s val_num=%s val_alpha=%s unit=%s' % (patient_id, when_field, when, test_type, val_num, val_alpha, unit)
			pk = data[0][0]
		# instantiate class
		gmClinItem.cClinItem.__init__(self, aPK_obj=pk)
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
			where vbp.i_id=%%s""" % self._payload[self._idx['pk_patient']]
		pat = gmPG.run_ro_query('historica', cmd, None, self._payload[self._idx['pk_patient']])
		return pat[0]
#============================================================
class cLabRequest(gmClinItem.cClinItem):
	"""Represents one lab request."""

	_cmd_fetch_payload = """
		select * from lab_request
		where pk=%s"""

	_cmds_store_payload = [
		"""select 1 from lab_request where pk=%(pk)s for update""",
		"""update lab_request set
				clin_when=%(clin_when)s,
				narrative=%(narrative)s,
				request_id=%(request_id)s,
				lab_request_id=%(lab_request_id)s,
				lab_rxd_when=%(lab_rxd_when)s,
				results_reported_when=%(results_reported_when)s,
				request_status=%(request_status)s,
				is_pending=%(is_pending)s::bool
			where pk=%(pk)s"""
		]

	_updatable_fields = [
		'clin_when',
		'narrative',
		'request_id',
		'lab_request_id',
		'lab_rxd_when',
		'results_reported_when',
		'request_status',
		'is_pending'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, req_id=None, lab=None):
		pk = aPK_obj
		# no PK given, so find it from req_id and lab
		if pk is None:
			if None in [req_id, lab]:
				raise gmExceptions.ConstructorError, 'req_id and lab must be defined (%s:%s)' % (lab, req_id)
			# generate query
			where_snippets = []
			vals = {}
			where_snippets.append('request_id=%(req_id)s')
			vals['req_id'] = req_id
			if type(lab) == types.IntType:
				where_snippets.append('fk_test_org=%(lab)s')
				vals['lab'] = lab
			else:
				where_snippets.append('fk_test_org=(select pk from test_org where internal_name=%(lab)s)')
				vals['lab'] = str(lab)
			where_clause = ' and '.join(where_snippets)
			cmd = "select pk from lab_request where %s" % where_clause
			data = gmPG.run_ro_query('historica', cmd, None, vals)
			# error
			if data is None:
				raise gmExceptions.ConstructorError, 'error getting lab request for [%s:%s]' % (lab, req_id)
			# no such request
			if len(data) == 0:
				raise gmExceptions.NoSuchClinItemError, 'no lab request for [%s:%s]' % (lab, req_id)
			pk = data[0][0]
		# instantiate class
		gmClinItem.cClinItem.__init__(self, aPK_obj=pk)
	#--------------------------------------------------------
	def get_patient(self):
		cmd = """
			select vpi.id_patient, vbp.title, vbp.firstnames, vbp.lastnames, vbp.dob
			from v_patient_items vpi, v_basic_person vbp
			where
				vpi.id_item=%s
					and
				vbp.i_id=vpi.id_patient"""
		pat = gmPG.run_ro_query('historica', cmd, None, self._payload[self._idx['pk_item']])
		return pat[0]
#============================================================
class cTestType(gmClinItem.cClinItem):
	"""Represents one test result type."""

	_cmd_fetch_payload = """select * from test_type where id=%s"""

	_cmds_store_payload = [
		"""select 1 from test_type where id=%(id)s for update""",
		"""update test_type set
				fk_test_org=%(fk_test_org)s,
				code=%(code)s,
				coding_system=%(coding_system)s,
				name=%(name)s,
				comment=%(comment)s,
				basic_unit=%(basic_unit)s
			where id=%(id)s"""
	]

	_updatable_fields = [
		'fk_test_org',
		'code',
		'coding_system',
		'name',
		'comment',
		'basic_unit'
	]
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, lab=None, code=None, name=None):
		pk = aPK_obj
		# no PK given, so find it from lab/code/name
		if pk is None:
			if lab is None:
				raise gmExceptions.ConstructorError, 'need lab to find test type'
			if (code is None) and (name is None):
				raise gmExceptions.ConstructorError, 'need code and/or name to find test type'
			where_snippets = []
			vals = {}
			if type(lab) == types.IntType:
				where_snippets.append('fk_test_org=%(lab)s')
				vals['lab'] = lab
			else:
				where_snippets.append('fk_test_org=(select pk from test_org where internal_name=%(lab)s)')
				vals['lab'] = str(lab)
			if code is not None:
				where_snippets.append('code=%(code)s')
				vals['code'] = code
			if name is not None:
				where_snippets.append('name=%(name)s')
				vals['name'] = name
			where_clause = ' and '.join(where_snippets)
			cmd = "select id from test_type where %s" % where_clause
			data = gmPG.run_ro_query('historica', cmd, None, vals)
			# error
			if data is None:
				raise gmExceptions.ConstructorError, 'error getting test type for [%s:%s:%s]' % (lab, code, name)
			# no such request
			if len(data) == 0:
				raise gmExceptions.NoSuchClinItemError, 'no test type for [%s:%s:%s]' % (lab, code, name)
			pk = data[0][0]
		# instantiate class
		gmClinItem.cClinItem.__init__(self, aPK_obj=pk)
	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		# find fk_test_org from name
		if attribute == 'fk_test_org':
			if type(value) != types.IntType:
				cmd = "select pk from test_org where internal_name=%s"
				data = gmPG.run_ro_query('historica', cmd, None, str(value))
				# error
				if data is None:
					raise ValueError, '[%s]: error finding test org for [%s], cannot set <%s>' % (self.__class__.__name__, value, attribute)
				if len(data) == 0:
					raise ValueError, '[%s]: no test org for [%s], cannot set <%s>' % (self.__class__.__name__, value, attribute)
				value = data[0][0]
		gmClinItem.cClinItem.__setitem__(self, attribute, value)
#============================================================
# convenience functions
#------------------------------------------------------------
def create_test_type(lab=None, code=None, unit=None, name=None):
	"""Create or get test type.

		returns tuple (status, value):
			(True, test type instance)
			(False, error message)
			(None, housekeeping_todo primary key)
	"""
	ttype = None
	try:
		ttype = cTestType(lab=lab, code=code)
	except gmExceptions.NoSuchClinItemError:
		_log.Log(gmLog.lInfo, 'will try to create test type')
	except gmExceptions.ConstructorError, msg:
		_log.LogException(str(msg), sys.exc_info(), verbose=0)
		return (False, msg)
	# found ?
	if ttype is not None:
		if name is None:
			return (True, ttype)
		db_lname = ttype['name']
		# yes but ambigous
		if name != db_lname:
			_log.Log(gmLog.lErr, 'test type found for [%s:%s] but long name mismatch: expected [%s], in DB [%s]' % (lab, code, name, db_lname))
			me = '$RCSfile: gmPathLab.py,v $ $Revision: 1.27 $'
			to = 'user'
			prob = _('The test type already exists but the long name is different. '
					'The test facility may have changed the descriptive name of this test.')
			sol = _('Verify with facility and change the old descriptive name to the new one.')
			ctxt = _('lab [%s], code [%s], expected long name [%s], existing long name [%s], unit [%s]') % (lab, code, name, db_lname, unit)
			cat = 'lab'
			status, data = gmPG.add_housekeeping_todo(me, to, prob, sol, ctxt, cat)
			return (None, data)
		return (True, ttype)
	# not found, so create it
	if unit is None:
		_log.Log(gmLog.lErr, 'need <unit> to create test type: %s:%s:%s:%s' % (lab, code, name, unit))
		return (False, 'argument error: %s:%s:%s%s' % (lab, code, name, unit))
	# make query
	cols = []
	val_snippets = []
	vals = {}
	# lab
	cols.append('fk_test_org')
	if type(lab) is types.IntType:
		val_snippets.append('%(lab)s')
		vals['lab'] = lab
	else:
		val_snippets.append('(select pk from test_org where internal_name=%(lab)s)')
		vals['lab'] = str(lab)
	# code
	cols.append('code')
	val_snippets.append('%(code)s')
	vals['code'] = code
	# unit
	cols.append('basic_unit')
	val_snippets.append('%(unit)s')
	vals['unit'] = unit
	# name
	if name is not None:
		cols.append('name')
		val_snippets.append('%(name)s')
		vals['name'] = name
	# join query parts
	col_clause = ','.join(cols)
	val_clause = ','.join(val_snippets)
	queries = []
	cmd = "insert into test_type(%s) values (%s)" % (col_clause, val_clause)
	queries.append((cmd, [vals]))
	cmd = "select currval('test_type_id_seq')"
	queries.append((cmd, []))
	# insert new
	result, err = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, err)
	try:
		ttype = cTestType(aPK_obj=result[0][0])
	except gmExceptions.ConstructorError, msg:
		_log.LogException(str(msg), sys.exc_info(), verbose=0)
		return (False, msg)
	return (True, ttype)
#------------------------------------------------------------
def create_lab_request(lab=None, req_id=None, pat_id=None, encounter_id=None, episode_id=None):
	"""Create or get lab request.

		returns tuple (status, value):
			(True, lab request instance)
			(False, error message)
			(None, housekeeping_todo primary key)
	"""
	req = None
	try:
		req = cLabRequest(lab=lab, req_id=req_id)
	except gmExceptions.NoSuchClinItemError, msg:
		_log.Log(gmLog.lInfo, '%s: will try to create lab request' % str(msg))
	except gmExceptions.ConstructorError, msg:
		_log.LogException(str(msg), sys.exc_info(), verbose=0)
		return (False, msg)
	# found
	if req is not None:
		db_pat = req.get_patient()
		# yes but ambigous
		if pat_id != db_pat[0]:
			_log.Log(gmLog.lErr, 'lab request found for [%s:%s] but patient mismatch: expected [%s], in DB [%s]' % (lab, req_id, pat_id, db_pat))
			me = '$RCSfile: gmPathLab.py,v $ $Revision: 1.27 $'
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
		cmd = "insert into lab_request (id_encounter, id_episode, fk_test_org, request_id) values (%s, %s, %s, %s)"
	else:
		cmd = "insert into lab_request (id_encounter, id_episode, fk_test_org, request_id) values (%s, %s, (select pk from test_org where internal_name=%s), %s)"
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
		_log.LogException(str(msg), sys.exc_info(), verbose=0)
		return (False, msg)
	return (True, req)
#------------------------------------------------------------
def create_lab_result(patient_id=None, when_field=None, when=None, test_type=None, val_num=None, val_alpha=None, unit=None, encounter_id=None, episode_id=None, request_id=None):
	tres = None
	try:
		tres = cLabResult(
			patient_id = patient_id,
			when_field=when_field,
			when=when,
			test_type=test_type,
			val_num=val_num,
			val_alpha=val_alpha,
			unit=unit
		)
		# exists already, so fail
		_log.Log(gmLog.lErr, 'cannot create test result, it exists already: %s' % str(tres))
		return (None, tres)
	except gmExceptions.NoSuchClinItemError:
		_log.Log(gmLog.lData, 'test result not found - as expected, will create it')
	except gmExceptions.ConstructorError, msg:
		_log.LogException(str(msg), sys.exc_info(), verbose=0)
		return (False, msg)
	# not found
	queries = []
	cmd = "insert into test_result (id_encounter, id_episode, fk_type, val_num, val_alpha, val_unit) values (%s, %s, %s, %s, %s, %s)"
	queries.append((cmd, [encounter_id, episode_id, test_type, val_num, val_alpha, unit]))
	cmd = "insert into lnk_result2lab_req (fk_result, fk_request) values ((select currval('test_result_id_seq')), %s)"
	queries.append((cmd, [request_id]))
	cmd = "select currval('test_result_id_seq')"
	queries.append((cmd, []))
	# insert new
	result, err = gmPG.run_commit('historica', queries, True)
	if result is None:
		return (False, err)
	try:
		tres = cLabResult(aPK_obj=result[0][0])
	except gmExceptions.ConstructorError, msg:
		_log.LogException(str(msg), sys.exc_info(), verbose=0)
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
		_log.Log(gmLog.lErr, 'error retrieving unreviewed lab results')
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
			_log.LogException('skipping unreviewed lab result [%s]' % row[0], sys.exc_info(), verbose=0)
	return (more_avail, results)
#------------------------------------------------------------
def get_pending_requests(limit=250):
	lim = limit + 1
	cmd = "select pk from lab_request where is_pending is true limit %s" % lim
	rows = gmPG.run_ro_query('historica', cmd)
	if rows is None:
		_log.Log(gmLog.lErr, 'error retrieving pending lab requests')
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
			_log.LogException('skipping pending lab request [%s]' % row[0], sys.exc_info(), verbose=0)
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
		lab_snippet = '%s'
	else:
		lab_snippet = '(select pk from test_org where internal_name=%s)'
		lab = str(lab)
	cmd =  """
		select request_id
		from lab_request lr0
		where lr0.clin_when = (
			select max(lr1.clin_when)
			from lab_request lr1
			where lr1.fk_test_org=%s
		)""" % lab_snippet
	rows = gmPG.run_ro_query('historica', cmd, None, lab)
	if rows is None:
		_log.Log(gmLog.lWarn, 'error getting most recently used request ID for lab [%s]' % lab)
		return ''
	if len(rows) == 0:
		return ''
	most_recent = rows[0][0]
	# apply supplied incrementor
	if incrementor_func is not None:
		try:
			next = incrementor_func(most_recent)
		except TypeError:
			_log.Log(gmLog.lErr, 'cannot call incrementor function [%s]' % str(incrementor_func))
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

	def test_result():
		lab_result = cLabResult(aPK_obj=29)
		print lab_result
		fields = lab_result.get_fields()
		for field in fields:
			print field, ':', lab_result[field]
		print "updatable:", lab_result.get_updatable_fields()
		print time.time()
		print lab_result.get_patient()
		print time.time()
	#--------------------------------------------------------
	def test_request():
		try:
#			lab_req = cLabRequest(aPK_obj=1)
#			lab_req = cLabRequest(req_id='EML#SC937-0176-CEC#11', lab=2)
			lab_req = cLabRequest(req_id='EML#SC937-0176-CEC#11', lab='Enterprise Main Lab')
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
	def test_create_result():
#		data = create_test_result(patient_id=12, when_field='lab_rxd_when', when='2000-09-17 15:40', test_type=6, val_num=9.5, unit='Gpt/l')
		print data[0]
		print data[1]
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
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmPG
	gmPG.set_default_client_encoding('latin1')

	test_result()
	test_request()
#	test_create_result()
#	test_unreviewed()
#	test_pending()

	gmPG.ConnectionPool().StopListeners()
#============================================================
# $Log: gmPathLab.py,v $
# Revision 1.27  2004-05-26 15:45:25  ncq
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
