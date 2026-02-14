# -*- coding: utf-8 -*-
"""Some HL7 handling."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import os
import logging
import time
import shutil
import datetime as pyDT
import hl7 as pyhl7
from xml.etree import ElementTree as pyxml


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmI18N
if __name__ == '__main__':
	gmI18N.activate_locale()
	gmI18N.install_domain()
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmIncomingData
from Gnumed.business import gmPathLab
from Gnumed.business import gmPerson
from Gnumed.business import gmPraxis
from Gnumed.business import gmStaff


_log = logging.getLogger('gm.hl7')

# constants
HL7_EOL = '\r'
HL7_BRK = r'\.br\ '[:-1]

HL7_SEGMENTS = 'FHS BHS MSH PID PV1 OBX NTE ORC OBR'.split()

HL7_segment2field_count = {
	'FHS': 12,
	'BHS': 12,
	'MSH': 19,
	'PID': 30,
	'PV1': 52,
	'OBR': 43,
	'OBX': 17,
	'NTE': 3,
	'ORC': 19
}

MSH_field__sending_lab = 3

PID_field__name = 5
PID_field__dob = 7
PID_field__gender = 8
PID_component__lastname = 1
PID_component__firstname = 2
PID_component__middlename = 3

OBR_field__service_name = 4
OBR_field__ts_requested = 6
OBR_field__ts_started = 7
OBR_field__ts_ended = 8
OBR_field__ts_specimen_received = 14

OBX_field__set_id = 1
OBX_field__datatype = 2
OBX_field__type = 3
# components of 3rd field:
OBX_component__loinc = 1
OBX_component__name = 2
OBX_field__subid = 4
OBX_field__value = 5
OBX_field__unit = 6
OBX_field__range = 7
OBX_field__abnormal_flag = 8
OBX_field__status = 11
OBX_field__timestamp = 14

NET_field__set_id = 1
NET_field__src = 2
NET_field__note = 3

HL7_field_labels = {
	'MSH': {
		0: 'Segment Type',
		1: 'Field Separator',
		2: 'Encoding Characters',
		3: 'Sending Application',
		4: 'Sending Facility',
		5: 'Receiving Application',
		6: 'Receiving Facility',
		7: 'Date/Time of Message',
		8: 'Security',
		9: 'Message Type',
		10: 'ID: Message Control',
		11: 'ID: Processing',
		12: 'ID: Version',
		14: 'Continuation Pointer',
		15: 'Accept Acknowledgement Type',
		16: 'Application Acknowledgement Type'
	},
	'PID': {
		0: 'Segment Type',
		1: '<PID> Set ID',
		2: 'Patient ID (external)',
		3: 'Patient ID (internal)',
		4: 'Patient ID (alternate)',
		5: 'Patient Name',
		7: 'Date/Time of birth',
		8: 'Administrative Gender',
		11: 'Patient Address',
		13: 'Patient Phone Number - Home'
	},
	'OBR': {
		0: 'Segment Type',
		1: 'ID: Set',
		3: 'Filler Order Number (= ORC-3)',
		4: 'ID: Universal Service',
		5: 'Priority',
		6: 'Date/Time requested',
		7: 'Date/Time Observation started',
		14: 'Date/Time Specimen received',
		16: 'Ordering Provider',
		18: 'Placer Field 1',
		20: 'Filler Field 1',
		21: 'Filler Field 2',
		22: 'Date/Time Results reported/Status changed',
		24: 'ID: Diagnostic Service Section',
		25: 'Result Status',
		27: 'Quantity/Timing',
		28: 'Result Copies To'
	},
	'ORC': {
		0: 'Segment Type',
		1: 'Order Control',
		3: 'Filler Order Number',
		12: 'Ordering Provider'
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
	},
	'NTE': {
		0: 'Segment Type',
		3: 'Comment'
	}
}

HL7_GENDERS = {
	'F': 'f',
	'M': 'm',
	'O': None,
	'U': None,
	None: None
}

#============================================================
# public API
#============================================================
#------------------------------------------------------------
def format_hl7_message(message=None, skip_empty_fields=True, eol='\n ', source=None):
	# a segment is a line starting with a type
	msg = pyhl7.parse(message)

	output = []
	if source is not None:
		output.append([_('HL7 Source'), '%s' % source])
	output.append([_('HL7 data size'), _('%s bytes') % len(message)])
	output.append([_('HL7 Message'), _(' %s segments (lines)%s') % (len(msg), gmTools.bool2subst(skip_empty_fields, _(', skipping empty fields'), ''))])

	max_len = 0
	for seg_idx in range(len(msg)):
		seg = msg[seg_idx]
		seg_type = seg[0][0]

		output.append([_('Segment #%s <%s>') % (seg_idx, seg_type), _('%s fields') % len(seg)])

		for field_idx in range(len(seg)):
			field = seg[field_idx]
			try:
				label = HL7_field_labels[seg_type][field_idx]
			except KeyError:
				label = _('HL7 %s field') % seg_type

			max_len = max(max_len, len(label))

			if len(field) == 0:
				if not skip_empty_fields:
					output.append(['%2s - %s' % (field_idx, label), _('<EMTPY>')])
				continue
			if (len(field) == 1) and (('%s' % field[0]).strip() == ''):
				if not skip_empty_fields:
					output.append(['%2s - %s' % (field_idx, label), _('<EMTPY>')])
				continue

			content_lines = ('%s' % field).split(HL7_BRK)
			output.append(['%2s - %s' % (field_idx, label), content_lines[0]])
			for line in content_lines[1:]:
				output.append(['', line])
			#output.append([u'%2s - %s' % (field_idx, label), u'%s' % field])

	if eol is None:
		return output

	max_len += 7
	return eol.join([ '%s: %s' % ((o[0] + (' ' * max_len))[:max_len], o[1]) for o in output ])

#------------------------------------------------------------
def format_hl7_file(filename, skip_empty_fields=True, eol='\n ', return_filename=False, fix_hl7=True):
	if fix_hl7:
		fixed_name = __fix_malformed_hl7_file(filename)
		hl7_file = open(fixed_name, mode = 'rt', encoding = 'utf-8-sig', newline = '')	# read universal but pass on untranslated
		source = '%s (<- %s)' % (fixed_name, filename)
	else:
		hl7_file = open(filename, mode = 'rt', encoding = 'utf-8-sig', newline = '')	# read universal but pass on untranslated
		source = filename
	output = format_hl7_message (
		message = hl7_file.read(1024 * 1024 * 5),		# 5 MB max
		skip_empty_fields = skip_empty_fields,
		eol = eol,
		source = source
	)
	hl7_file.close()

	if not return_filename:
		return output

	max_len = 120
	if eol is None:
		output = '\n '.join([ '%s: %s' % ((o[0] + (' ' * max_len))[:max_len], o[1]) for o in output ])

	out_name = gmTools.get_unique_filename(prefix = 'gm-formatted_hl7-', suffix = '.hl7')
	out_file = open(out_name, mode = 'wt', encoding = 'utf8')
	out_file.write(output)
	out_file.close()

	return out_name

#============================================================
# internal helpers
#============================================================
def __fix_malformed_hl7_file(filename, encoding='utf8'):

	_log.debug('fixing HL7 file [%s]', filename)

	# first pass:
	# - remove empty lines
	# - normalize line endings
	# - unwrap wrapped segments (based on the assumption that segments are wrapped until a line starts with a known segment marker)
	out1_fname = gmTools.get_unique_filename (
		prefix = 'gm_fix1-%s-' % gmTools.fname_stem(filename),
		suffix = '.hl7'
	)
	hl7_in = open(filename, mode = 'rt', encoding = encoding)					# universal newlines: translate any type of EOL to \n
	hl7_out = open(out1_fname, mode = 'wt', encoding = 'utf8', newline = '')	# newline='' -> no translation of EOL at all
	is_first_line = True
	for line in hl7_in:
		# skip empty line
		if line.strip() == '':
			continue
		# starts with known segment ?
		segment = line[:3]
		if (segment in HL7_SEGMENTS) and (line[3] == '|'):
			if not is_first_line:
				hl7_out.write(HL7_EOL)
			else:
				is_first_line = False
		else:
			hl7_out.write(' ')
		hl7_out.write(line.rstrip())
	hl7_out.write(HL7_EOL)
	hl7_out.close()
	hl7_in.close()

	# second pass:
	# - normalize # of fields per line
	# - remove '\.br.\'-only fields ;-)
	out2_fname = gmTools.get_unique_filename (
		prefix = 'gm_fix2-%s-' % gmTools.fname_stem(filename),
		suffix = '.hl7'
	)
	# we can now _expect_ lines to end in HL7_EOL, anything else is an error
	hl7_in = open(out1_fname, mode = 'rt', encoding = 'utf-8-sig', newline = HL7_EOL)
	hl7_out = open(out2_fname, mode = 'wt', encoding = 'utf8', newline = '')
	for line in hl7_in:
		line = line.strip()
		seg_type = line[:3]						# assumption: field separator = '|'
		field_count = line.count('|') + 1		# assumption: no '|' in data ...
		try:
			required_fields = HL7_segment2field_count[seg_type]
		except KeyError:
			required_fields = field_count
		missing_fields_count = required_fields - field_count
		if missing_fields_count > 0:
			line += ('|' * missing_fields_count)
		cleaned_fields = []
		for field in line.split('|'):
			if field.replace(HL7_BRK, '').strip() == '':
				cleaned_fields.append('')
				continue
			cleaned = gmTools.strip_prefix(field, HL7_BRK, remove_repeats = True, remove_whitespace = True)
			cleaned = gmTools.strip_suffix(cleaned, HL7_BRK, remove_repeats = True, remove_whitespace = True)
			cleaned_fields.append(cleaned)
		hl7_out.write('|'.join(cleaned_fields) + HL7_EOL)
	hl7_out.close()
	hl7_in.close()

	# third pass:
	# - unsplit same-name, same-time, text-type OBX segments
	out3_fname = gmTools.get_unique_filename (
		prefix = 'gm_fix3-%s-' % gmTools.fname_stem(filename),
		suffix = '.hl7'
	)
	# we can now _expect_ lines to end in HL7_EOL, anything else is an error
	hl7_in = open(out2_fname, mode = 'rt', encoding = 'utf-8-sig', newline = HL7_EOL)
	hl7_out = open(out3_fname, mode = 'wt', encoding = 'utf8', newline = '')
	prev_identity = None
	prev_fields = None
	for line in hl7_in:
		line = line.strip()
		if not line.startswith('OBX|'):
			if prev_fields is not None:
				hl7_out.write('|'.join(prev_fields) + HL7_EOL)
			hl7_out.write(line + HL7_EOL)
			prev_identity = None
			prev_fields = None
			curr_fields = None
			continue
		# first OBX
		curr_fields = line.split('|')
		if curr_fields[OBX_field__datatype] != 'FT':
			hl7_out.write(line + HL7_EOL)
			prev_identity = None
			prev_fields = None
			curr_fields = None
			continue
		# first FT type OBX
		if prev_fields is None:
			prev_fields = line.split('|')
			prev_identity = line.split('|')
			prev_identity[OBX_field__set_id] = ''
			prev_identity[OBX_field__subid] = ''
			prev_identity[OBX_field__value] = ''
			prev_identity = '|'.join(prev_identity)
			continue
		# non-first FT type OBX
		curr_identity = line.split('|')
		curr_identity[OBX_field__set_id] = ''
		curr_identity[OBX_field__subid] = ''
		curr_identity[OBX_field__value] = ''
		curr_identity = '|'.join(curr_identity)
		if curr_identity != prev_identity:
			# write out previous line
			hl7_out.write('|'.join(prev_fields) + HL7_EOL)
			# keep current fields, since it may start a "repeat FT type OBX block"
			prev_fields = curr_fields
			prev_identity = curr_identity
			continue
		if prev_fields[OBX_field__value].endswith(HL7_BRK):
			prev_fields[OBX_field__value] += curr_fields[OBX_field__value]
		else:
			if curr_fields[OBX_field__value].startswith(HL7_BRK):
				prev_fields[OBX_field__value] += curr_fields[OBX_field__value]
			else:
				prev_fields[OBX_field__value] += HL7_BRK
				prev_fields[OBX_field__value] += curr_fields[OBX_field__value]
	if prev_fields is not None:
		hl7_out.write('|'.join(prev_fields) + HL7_EOL)
	hl7_out.close()
	hl7_in.close()

	return out3_fname

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmDateTime.init()
	gmTools.gmPaths()

	#-------------------------------------------------------
	def test_format_hl7_message():
		tests = [
			"OBR|1||03-1350023-LIP-0|LIP^Lipids||20031004073300|20031004073300|||||||20031004073300||22333^MEDIC^IAN^TEST||031350023||03-1350023|031350023|20031004131600||CHEM|F|||22333^MEDIC^IAN^TEST",
			"OBX|2|NM|22748-8^LDL Cholesterol||4.0|mmol/L|1.5 - 3.4|H|||F|||20031004073300"
		]
		for test in tests:
			print(format_hl7_message (
#				skip_empty_fields = True,
				message = test
			))
	#-------------------------------------------------------
	def test_format_hl7_file(filename):
		print(format_hl7_file (
			filename,
#			skip_empty_fields = True
			return_filename = True
		))

	#-------------------------------------------------------
	def test___fix_malformed_hl7():
		print("fixed HL7:", __fix_malformed_hl7_file(sys.argv[2]))

	#-------------------------------------------------------
	def test_parse_hl7():
		MSH_file = open(sys.argv[2], mode = 'rt', encoding = 'utf-8-sig', newline = '')
		raw_hl7 = MSH_file.read(1024 * 1024 * 5)	# 5 MB max
		MSH_file.close()
		print(format_hl7_message (
			message = raw_hl7,
			skip_empty_fields = True,
			eol = '\n'
		))
		HL7 = pyhl7.parse(raw_hl7)
		del raw_hl7
		for seg in HL7.segments('MSH'):
			print(seg)
		print("PID:")
		print(HL7.extract_field('PID'))
		print(HL7.extract_field('PID', segment_num = 1, field_num = PID_field__name, component_num = PID_component__lastname))
		print(HL7.extract_field('PID', segment_num = 1, field_num = PID_field__name, component_num = PID_component__lastname))

#			incoming['firstnames'] = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__name, component_num = PID_component__firstname)
#			val = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__name, component_num = PID_component__middlename)
#			if val is not None:
#				incoming['firstnames'] += u' '
#				incoming['firstnames'] += val
#			val = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__dob)
#			if val is not None:
#				tmp = time.strptime(val, '%Y%m%d')
#				incoming['dob'] = pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)
#			val = HL7.extract_field('PID', segment_num = 1, field_num = PID_field__gender)
#			if val is not None:
#				incoming['gender'] = val
#			incoming['external_data_id'] = filename

	#-------------------------------------------------------
	#test_format_hl7_message()
	#test_format_hl7_file(sys.argv[2])
	#test___fix_malformed_hl7()
	test_parse_hl7()
