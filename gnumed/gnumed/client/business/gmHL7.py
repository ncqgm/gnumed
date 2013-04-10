# -*- coding: utf8 -*-
"""Some HL7 handling."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import os
import codecs
import logging
import time
import datetime as pyDT
import hl7 as pyhl7
from xml.etree import ElementTree as pyxml


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDateTime
from Gnumed.business import gmPathLab


_log = logging.getLogger('gm.hl7')

# constants
HL7_EOL = u'\r'

HL7_SEGMENTS = u'FHS BHS MSH PID PV1 OBX NTE ORC OBR'.split()

MSH_sending_lab = 3

PID_name = 5
PID_lastname = 0
PID_firstname = 1
PID_middlename = 2
PID_dob = 7
PID_gender = 8

OBX_type = 3
OBX_LOINC = 0
OBX_name = 1
OBX_value = 5
OBX_unit = 6

HL7_field_labels = {
	'PID': {
		0: 'Segment Type',
		1: '<PID> Set ID',
		2: 'Patient ID',
		5: 'Patient name',
		7: 'Date/Time of birth',
		8: 'Administrative gender'
	},
	'OBR': {
		0: 'Segment Type'
	},
	'OBX': {
		0: 'Segment Type',
		1: 'Set ID',
		2: 'Value Type',
		3: 'Identifier (LOINC)',
		4: 'Observation Sub-ID',
		5: 'Value',
		6: 'Units',
		7: 'References Range (Low - High)',
		8: 'Abnormal Flags',
		11: 'Result Status',
		14: 'Date/Time of Observation'
	}
}

#============================================================
# class to handle unmatched incoming clinical data
#------------------------------------------------------------
_SQL_get_incoming_data = u"""SELECT * FROM clin.v_incoming_data_unmatched WHERE %s"""

class cIncomingData(gmBusinessDBObject.cBusinessDBObject):
	"""Represents items of incoming data, say, HL7 snippets."""

	_cmd_fetch_payload = _SQL_get_incoming_data % u"pk_incoming_data_unmatched = %s"
	_cmds_store_payload = [
		u"""UPDATE clin.incoming_data_unmatched SET
				fk_patient_candidates = %(pk_patient_candidates)s,
				fk_identity_disambiguated = %(pk_identity_disambiguated)s,
				fk_provider_disambiguated = %(pk_provider_disambiguated)s,
				request_id = gm.nullify_empty_string(%(request_id)s),
				firstnames = gm.nullify_empty_string(%(firstnames)s),
				lastnames = gm.nullify_empty_string(%(lastnames)s),
				dob = %(dob)s,
				postcode = gm.nullify_empty_string(%(postcode)s),
				other_info = gm.nullify_empty_string(%(other_info)s),
				type = gm.nullify_empty_string(%(data_type)s),
				gender = gm.nullify_empty_string(%(gender)s),
				requestor = gm.nullify_empty_string(%(requestor)s),
				external_data_id = gm.nullify_empty_string(%(external_data_id)s),
				comment = gm.nullify_empty_string(%(comment)s)
			WHERE
				pk = %(pk_incoming_data_unmatched)s
					AND
				xmin = %(xmin_incoming_data_unmatched)s
			RETURNING
				xmin as xmin_incoming_data_unmatched,
				octet_length(data) as data_size
		"""
	]
	# view columns that can be updated:
	_updatable_fields = [
		u'pk_patient_candidates',
		u'request_id',						# request ID as found in <data>
		u'firstnames',
		u'lastnames',
		u'dob',
		u'postcode',
		u'other_info',						# other identifying info in .data
		u'data_type',
		u'gender',
		u'requestor',						# Requestor of data (e.g. who ordered test results) if available in source data.
		u'external_data_id',				# ID of content of .data in external system (e.g. importer) where appropriate
		u'comment',							# a free text comment on this row, eg. why is it here, error logs etc
		u'pk_identity_disambiguated',
		u'pk_provider_disambiguated'		# The provider the data is relevant to.
	]
	#--------------------------------------------------------
	def format(self):
		return u'%s' % self
	#--------------------------------------------------------
	def update_data_from_file(self, fname=None):
		# sanity check
		if not (os.access(fname, os.R_OK) and os.path.isfile(fname)):
			_log.error('[%s] is not a readable file' % fname)
			return False

		gmPG2.file2bytea (
			query = u"UPDATE clin.incoming_data_unmatched SET data = %(data)s::bytea WHERE pk = %(pk)s",
			filename = fname,
			args = {'pk': self.pk_obj}
		)

		# must update XMIN now ...
		self.refetch_payload()
		return True
	#--------------------------------------------------------
	def export_to_file(self, aChunkSize=0, filename=None):

		if self._payload[self._idx['data_size']] == 0:
			return None

		if self._payload[self._idx['data_size']] is None:
			return None

		if filename is None:
			filename = gmTools.get_unique_filename(prefix = 'gm-incoming_data_unmatched-')

		success = gmPG2.bytea2file (
			data_query = {
				'cmd': u'SELECT substring(data from %(start)s for %(size)s) FROM clin.incoming_data_unmatched WHERE pk = %(pk)s',
				'args': {'pk': self.pk_obj}
			},
			filename = filename,
			chunk_size = aChunkSize,
			data_size = self._payload[self._idx['data_size']]
		)

		if not success:
			return None

		return filename

#------------------------------------------------------------
def get_incoming_data(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = u'true ORDER BY %s' % order_by
	cmd = _SQL_get_incoming_data % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cIncomingData(row = {'data': r, 'idx': idx, 'pk_field': 'pk_incoming_data_unmatched'}) for r in rows ]

#------------------------------------------------------------
def create_incoming_data(data_type, filename):
	args = {'typ': data_type}
	cmd = u"""
		INSERT INTO clin.incoming_data_unmatched (type, data)
		VALUES (%(typ)s, 'new data'::bytea)
		RETURNING pk"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)
	pk = rows[0]['pk']
	incoming = cIncomingData(aPK_obj = pk)
	if not incoming.update_data_from_file(fname = filename):
		delete_incoming_data(incoming_data = pk)
		return None
	return incoming

#------------------------------------------------------------
def delete_incoming_data(pk_incoming_data=None):
	args = {'pk': pk_incoming_data}
	cmd = u"DELETE FROM clin.incoming_data_unmatched WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True

#------------------------------------------------------------

#============================================================
def fix_HL7_stupidities(filename, encoding='utf8'):

	out_fname = gmTools.get_unique_filename (
		prefix = u'%s-fixed-' % gmTools.fname_stem(filename),
		suffix = '.hl7'
	)
	_log.debug('fixing HL7 [%s] -> [%s]', filename, out_fname)
	hl7_in = codecs.open(filename, 'rb', encoding)
	hl7_out = codecs.open(out_fname, 'wb', 'utf8')

	line_idx = 0
	prev_line = None
	for line in hl7_in:
		line_idx += 1
		# suspicious for non-terminating line ?
		if line.endswith(u' \n'):
			_log.debug('#%s: suspicious non-terminating line ("...<SPACE>\\n"): [%s...%s]', line_idx, line[:4], line[-7:])
			if prev_line is None:
				prev_line = line[:-1]
			else:
				prev_line = prev_line + line[:-1]
			continue

		line = line.strip('\r').strip('\n').strip('\r').strip('\n')

		# final continuation line ?
		if line[3] != u'|':
			if prev_line is None:
				raise ValueError('line #%s does not start with "<SEGMENT>|" but previous line did not end with BLANK either: [%s]' % (line_idx, line))
			hl7_out.write(prev_line)
			prev_line = None
			hl7_out.write(line + HL7_EOL)
			continue

		# start of a known segment ?
		if line[:3] in HL7_SEGMENTS:
			if prev_line is not None:
				hl7_out.write(prev_line + HL7_EOL)
				prev_line = None
			hl7_out.write(line + HL7_EOL)
			continue

	hl7_out.close()
	hl7_in.close()

	return out_fname
#============================================================
def extract_HL7_from_CDATA(filename, xml_path):

	_log.debug('extracting HL7 from CDATA of <%s> nodes in XML file [%s]', xml_path, filename)

	hl7_xml = pyxml.ElementTree()
	try:
		hl7_xml.parse(filename)
	except pyxml.ParseError:
		_log.exception('cannot parse [%s]' % filename)
		return None
	nodes = hl7_xml.findall(xml_path)
	if len(nodes) == 0:
		_log.debug('no data found')
		return None

	out_fname = gmTools.get_unique_filename(prefix = u'%s-' % gmTools.fname_stem(filename), suffix = '.hl7')
	_log.debug('writing HL7 to [%s]', out_fname)
	hl7_file = codecs.open(out_fname, 'wb', 'utf8')
	for node in nodes:
		hl7_file.write(node.text)

	return out_fname
#============================================================
def split_HL7_by_MSH(filename, encoding='utf8'):

	_log.debug('splitting [%s]', filename)

	hl7_in = codecs.open(filename, 'rb', encoding)

	idx = 0
	first_line = True
	MSH_file = None
	MSH_fnames = []
	for line in hl7_in:
		# first line must be MSH
		if first_line:
			# ignore empty / FHS / BHS lines
			if line.strip() == u'':
				continue
			if line.startswith(u'FHS|'):
				_log.debug('ignoring FHS')
				continue
			if line.startswith(u'BHS|'):
				_log.debug('ignoring BHS')
				continue
			if not line.startswith(u'MSH|'):
				raise ValueError('HL7 file <%s> does not start with "MSH" line' % filename)
			first_line = False
		# start new file
		if line.startswith(u'MSH|'):
			if MSH_file is not None:
				MSH_file.close()
			idx += 1
			out_fname = gmTools.get_unique_filename(prefix = u'%s-MSH_%s-' % (gmTools.fname_stem(filename), idx), suffix = 'hl7')
			_log.debug('writing message %s to [%s]', idx, out_fname)
			MSH_fnames.append(out_fname)
			MSH_file = codecs.open(out_fname, 'wb', 'utf8')
		# ignore BTS / FTS lines
		if line.startswith(u'BTS|'):
			_log.debug('ignoring BTS')
			continue
		if line.startswith(u'FTS|'):
			_log.debug('ignoring FTS')
			continue
		# else write line to new file
		MSH_file.write(line.strip('\n').strip('\r').strip('\n').strip('\r') + u'\r')

	if MSH_file is not None:
		MSH_file.close()
	hl7_in.close()

	return MSH_fnames

#============================================================
def flatten_MSH_by_PID(filename):
	"""Assumes:
		- ONE MSH per file
		- utf8 encoding
		- first non-empty line must be MSH line

		- anything between MSH and PID is lost

		IOW, what's created by split_HL7_into_MSH()
	"""
	_log.debug('splitting [%s]', filename)

	MSH_in = codecs.open(filename, 'rb', 'utf8')

	looking_for_MSH = True
	MSH_line = None
	looking_for_first_PID = True
	PID_file = None
	PID_fnames = []
	idx = 0
	for line in MSH_in:
		# ignore empty
		if line.strip() == u'':
			continue

		# first non-empty line must be MSH
		if looking_for_MSH:
			if line.startswith(u'MSH|'):
				looking_for_MSH = False
				MSH_line = line.strip('\n').strip('\r').strip('\n').strip('\r') + u'\r'
				continue
			raise ValueError('HL7 MSH file <%s> does not start with "MSH" line' % filename)

		# first non-empty line after MSH must be PID
		if looking_for_first_PID:
			if not line.startswith(u'PID|'):
				raise ValueError('HL7 MSH file <%s> does not have "PID" line follow "MSH" line' % filename)
			looking_for_first_PID = False

		# start new file if line is PID
		if line.startswith(u'PID|'):
			if PID_file is not None:
				PID_file.close()
			idx += 1
			out_fname = gmTools.get_unique_filename(prefix = u'%s-PID_%s-' % (gmTools.fname_stem(filename), idx), suffix = 'hl7')
			_log.debug('writing message for PID %s to [%s]', idx, out_fname)
			PID_fnames.append(out_fname)
			PID_file = codecs.open(out_fname, 'wb', 'utf8')
			PID_file.write(MSH_line)
		# else write line to new file
		PID_file.write(line.strip('\n').strip('\r').strip('\n').strip('\r') + u'\r')

	if PID_file is not None:
		PID_file.close()
	MSH_in.close()

	return PID_fnames

#============================================================
def split_HL7_by_PID(filename, encoding='utf8'):

	PID_fnames = []
	for MSH_fname in split_HL7_by_MSH(filename, encoding):
		PID_fnames.extend(flatten_MSH_by_PID(MSH_fname))

	return PID_fnames

#============================================================
def __find_or_create_lab(hl7_lab):
	comment_tag = u'[HL7 name::%s]' % hl7_lab
	for gm_lab in gmPathLab.get_test_orgs():
		if comment_tag in gmTools.coalesce(gm_lab['comment'], u''):
			return gm_lab
	_log.debug('lab not found: %s', hl7_lab)
	gm_lab = gmPathLab.create_test_org(name = hl7_lab, comment = comment_tag)
	if gm_lab is None:
		raise ValueError('cannot create lab [%s] in GNUmed' % hl7_lab)
	_log.debug('created lab: %s', gm_lab)
	return gm_lab

#------------------------------------------------------------
def __find_or_create_test_type(loinc, name, pk_lab, unit):

	tt = gmPathLab.find_measurement_type(lab = pk_lab, name = name)
	if tt is None:
		_log.debug('test type [%s %s (%s)] not found for lab #%s, creating', name, unit, loinc, pk_lab)
		tt = gmPathLab.create_measurement_type(lab = pk_lab, abbrev = name, unit = unit, name = name)

	if loinc is None:
		return tt
	if loinc.strip() == u'':
		return tt
	if tt['loinc'] is None:
		tt['loinc'] = loinc
		tt.save()
		return tt
	if tt['loinc'] != loinc:
#		raise ValueError('LOINC code mismatch between GM (%s) and HL7 (%s) for result type [%s]' % (tt['loinc'], loinc, name))
		_log.error('LOINC code mismatch between GM (%s) and HL7 (%s) for result type [%s]', tt['loinc'], loinc, name)

	return tt

#------------------------------------------------------------
def import_MSH(filename):
	"""Assumes what's produced by flatten_MSH_by_PID()."""

	_log.debug('importing HL7 from [%s]', filename)

	# read the file
	MSH_file = codecs.open(filename, 'rb', 'utf8')
	HL7 = pyhl7.parse(MSH_file.read(1024 * 1024 * 5))	# 5 MB max
	MSH_file.close()

	# verify lab is in database
	gm_lab = __find_or_create_lab(HL7.segment('MSH')[MSH_sending_lab][0])

	# verify test types are in database
	for OBX in HL7.segments('OBX'):
		tt = OBX[OBX_type]
		unit = OBX[OBX_unit][0]
		__find_or_create_test_type(tt[OBX_LOINC], tt[OBX_name], gm_lab['pk_test_org'], unit)

	# find patient
	name = HL7.segment('PID')[PID_name]
	pat_lname = name[PID_lastname]
	pat_fname = name[PID_firstname]
	pat_mname = None
	if len(name) > 2:
		pat_mname = name[PID_middlename]
	print " Patient: %s (%s) %s" % (pat_fname, pat_mname, pat_lname)

#------------------------------------------------------------
def stage_MSH_as_incoming_data(filename, source=None):
	"""Assumes what's produced by flatten_MSH_by_PID()."""

	_log.debug('staging HL7%s from [%s]', gmTools.coalesce(source, u'', u' (%s)'), filename)

	# parse HL7
	MSH_file = codecs.open(filename, 'rb', 'utf8')
	HL7 = pyhl7.parse(MSH_file.read(1024 * 1024 * 5))	# 5 MB max
	MSH_file.close()

	# import file
	inc = create_incoming_data(u'HL7%s' % gmTools.coalesce(source, u'', u' (%s)'), filename)
	if inc is None:
		return None

	try:
		# set fields if known
		PID = HL7.segment('PID')
		name = PID[PID_name]
		inc['lastnames'] = gmTools.coalesce(name[PID_lastname], u'')
		inc['firstnames'] = gmTools.coalesce(name[PID_firstname], u'')
		if len(name) > 2:
			inc['firstnames'] += u' '
			inc['firstnames'] += name[PID_middlename]
		if PID[PID_dob] is not None:
			tmp = time.strptime(PID[PID_dob][0], '%Y%m%d')
			inc['dob'] = pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)
		if PID[PID_gender] is not None:
			inc['gender'] = PID[PID_gender][0]
		inc['external_data_id'] = filename
		#u'fk_patient_candidates',
		#	u'request_id',						# request ID as found in <data>
		#	u'postcode',
		#	u'other_info',						# other identifying info in .data
		#	u'requestor',						# Requestor of data (e.g. who ordered test results) if available in source data.
		#	u'fk_identity_disambiguated',
		#	u'comment',							# a free text comment on this row, eg. why is it here, error logs etc
		#	u'fk_provider_disambiguated'		# The provider the data is relevant to.
		inc.save()
	except:
		delete_incoming_data(pk_incoming_data = inc['pk_incoming_data_unmatched'])
		raise

	return inc

#------------------------------------------------------------
def format_hl7_message(message=None, skip_empty_fields=True, eol=u'\n '):
	# a segment is a line starting with a type

	msg = pyhl7.parse(message)

	output = [[_('HL7 Message'), _(' %s segments (lines)%s') % (len(msg), gmTools.bool2subst(skip_empty_fields, _(', skipping empty fields'), u''))]]

	max_len = 0
	for s_idx in range(len(msg)):
		seg = msg[s_idx]
		seg_type = seg[0][0]

		output.append([_('Segment #%s <%s>') % (s_idx, seg_type), _('%s fields') % len(seg)])

		for f_idx in range(len(seg)):
			field = seg[f_idx]
			try:
				label = HL7_field_labels[seg_type][f_idx]
			except KeyError:
				label = _('HL7 %s field') % seg_type

			max_len = max(max_len, len(label))

			if len(field) == 0:
				if not skip_empty_fields:
					output.append([u'%2s - %s' % (f_idx, label), _('<EMTPY>')])
				continue
			if (len(field) == 1) and (field[0].strip() == u''):
				if not skip_empty_fields:
					output.append([u'%2s - %s' % (f_idx, label), _('<EMTPY>')])
				continue

			output.append([u'%2s - %s' % (f_idx, label), u'%s' % field])

	if eol is None:
		return output

	max_len += 7
	return eol.join([ u'%s: %s' % ((o[0] + (u' ' * max_len))[:max_len], o[1]) for o in output ])

#------------------------------------------------------------
def format_hl7_file(filename, skip_empty_fields=True, eol=u'\n ', return_filename=False):
	hl7_file = codecs.open(filename, 'rb', 'utf8')
	output = format_hl7_message (
		message = hl7_file.read(1024 * 1024 * 5),		# 5 MB max
		skip_empty_fields = skip_empty_fields,
		eol = eol
	)
	hl7_file.close()

	if not return_filename:
		return output

	if eol is None:
		output = u'\n '.join([ u'%s: %s' % ((o[0] + (u' ' * max_len))[:max_len], o[1]) for o in output ])

	out_name = gmTools.get_unique_filename(prefix = 'gm-formatted_hl7-', suffix = u'.hl7')
	out_file = codecs.open(out_name, 'wb', 'utf8')
	out_file.write(output)
	out_file.close()

	return out_name
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2
	from Gnumed.pycommon import gmI18N

	gmDateTime.init()
	gmI18N.activate_locale()
	gmI18N.install_domain()

	#-------------------------------------------------------
	def test_import_HL7():
		PID_names = split_HL7_by_PID(sys.argv[2], encoding='utf8')
		for name in PID_names:
			print name
			import_MSH(name)
	#-------------------------------------------------------
	def test_xml_extract():
		hl7 = extract_HL7_from_CDATA(sys.argv[2], u'.//Message')
		print "HL7:", hl7
		fixed = fix_HL7_stupidities(hl7)
		print "fixed HL7:", fixed
		PID_names = split_HL7_by_PID(fixed, encoding='utf8')
		print "per-PID MSH files:"
		for name in PID_names:
			print " ", name
	#-------------------------------------------------------
	def test_incoming_data():
		for d in get_incoming_data():
			print d
	#-------------------------------------------------------
	def test_stage_hl7_from_xml():
		hl7 = extract_HL7_from_CDATA(sys.argv[2], u'.//Message')
		print "HL7:", hl7
		fixed = fix_HL7_stupidities(hl7)
		print "fixed HL7:", fixed
		PID_names = split_HL7_by_PID(fixed, encoding='utf8')
		print "staging per-PID HL7 files:"
		for name in PID_names:
			print " file:", name
			print "", stage_MSH_as_incoming_data(name, source = u'Excelleris')
	#-------------------------------------------------------
	def test_stage_hl7():
		fixed = fix_HL7_stupidities(sys.argv[2])
		print "fixed HL7:", fixed
		PID_names = split_HL7_by_PID(fixed, encoding='utf8')
		print "staging per-PID HL7 files:"
		for name in PID_names:
			print " file:", name
			print "", stage_MSH_as_incoming_data(name, source = u'?')
	#-------------------------------------------------------
	def test_format_hl7_message():
		tests = [
			"OBR|1||03-1350023-LIP-0|LIP^Lipids||20031004073300|20031004073300|||||||20031004073300||22333^MEDIC^IAN^TEST||031350023||03-1350023|031350023|20031004131600||CHEM|F|||22333^MEDIC^IAN^TEST",
			"OBX|2|NM|22748-8^LDL Cholesterol||4.0|mmol/L|1.5 - 3.4|H|||F|||20031004073300"
		]
		for test in tests:
			print format_hl7_message (
#				skip_empty_fields = True,
				message = test
			)
	#-------------------------------------------------------
	def test_format_hl7_file():
		print format_hl7_file (
			sys.argv[2]
#			skip_empty_fields = True
		)
	#-------------------------------------------------------
	#test_import_HL7()
	#test_xml_extract()
	#test_incoming_data()
	#test_stage_hl7_from_xml()
	#test_stage_hl7()
	#test_format_hl7_message()
	test_format_hl7_file()
