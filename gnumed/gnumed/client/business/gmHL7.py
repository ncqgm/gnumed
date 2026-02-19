# -*- coding: utf-8 -*-
"""Some HL7 handling."""
#============================================================
# SPDX-License-Identifier: GPL-2.0-or-later
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import logging


import hl7 as pyhl7


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try: _
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmHL7Defs


_log = logging.getLogger('gm.hl7')

#============================================================
# public API
#============================================================
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
				label = gmHL7Defs.HL7_field_labels[seg_type][field_idx]
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

			content_lines = ('%s' % field).split(gmHL7Defs.HL7_BRK)
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
		if (segment in gmHL7Defs.HL7_SEGMENTS) and (line[3] == '|'):
			if not is_first_line:
				hl7_out.write(gmHL7Defs.HL7_EOL)
			else:
				is_first_line = False
		else:
			hl7_out.write(' ')
		hl7_out.write(line.rstrip())
	hl7_out.write(gmHL7Defs.HL7_EOL)
	hl7_out.close()
	hl7_in.close()

	# second pass:
	# - normalize # of fields per line
	# - remove '\.br.\'-only fields ;-)
	out2_fname = gmTools.get_unique_filename (
		prefix = 'gm_fix2-%s-' % gmTools.fname_stem(filename),
		suffix = '.hl7'
	)
	# we can now _expect_ lines to end in gmHL7Defs.HL7_EOL, anything else is an error
	hl7_in = open(out1_fname, mode = 'rt', encoding = 'utf-8-sig', newline = gmHL7Defs.HL7_EOL)
	hl7_out = open(out2_fname, mode = 'wt', encoding = 'utf8', newline = '')
	for line in hl7_in:
		line = line.strip()
		seg_type = line[:3]						# assumption: field separator = '|'
		field_count = line.count('|') + 1		# assumption: no '|' in data ...
		try:
			required_fields = gmHL7Defs.HL7_segment2field_count[seg_type]
		except KeyError:
			required_fields = field_count
		missing_fields_count = required_fields - field_count
		if missing_fields_count > 0:
			line += ('|' * missing_fields_count)
		cleaned_fields = []
		for field in line.split('|'):
			if field.replace(gmHL7Defs.HL7_BRK, '').strip() == '':
				cleaned_fields.append('')
				continue
			cleaned = gmTools.strip_prefix(field, gmHL7Defs.HL7_BRK, remove_repeats = True, remove_whitespace = True)
			cleaned = gmTools.strip_suffix(cleaned, gmHL7Defs.HL7_BRK, remove_repeats = True, remove_whitespace = True)
			cleaned_fields.append(cleaned)
		hl7_out.write('|'.join(cleaned_fields) + gmHL7Defs.HL7_EOL)
	hl7_out.close()
	hl7_in.close()

	# third pass:
	# - unsplit same-name, same-time, text-type OBX segments
	out3_fname = gmTools.get_unique_filename (
		prefix = 'gm_fix3-%s-' % gmTools.fname_stem(filename),
		suffix = '.hl7'
	)
	# we can now _expect_ lines to end in gmHL7Defs.HL7_EOL, anything else is an error
	hl7_in = open(out2_fname, mode = 'rt', encoding = 'utf-8-sig', newline = gmHL7Defs.HL7_EOL)
	hl7_out = open(out3_fname, mode = 'wt', encoding = 'utf8', newline = '')
	prev_identity = None
	prev_fields = None
	for line in hl7_in:
		line = line.strip()
		if not line.startswith('OBX|'):
			if prev_fields is not None:
				hl7_out.write('|'.join(prev_fields) + gmHL7Defs.HL7_EOL)
			hl7_out.write(line + gmHL7Defs.HL7_EOL)
			prev_identity = None
			prev_fields = None
			curr_fields = None
			continue
		# first OBX
		curr_fields = line.split('|')
		if curr_fields[gmHL7Defs.OBX_field__datatype] != 'FT':
			hl7_out.write(line + gmHL7Defs.HL7_EOL)
			prev_identity = None
			prev_fields = None
			curr_fields = None
			continue
		# first FT type OBX
		if prev_fields is None:
			prev_fields = line.split('|')
			prev_identity = line.split('|')
			prev_identity[gmHL7Defs.OBX_field__set_id] = ''
			prev_identity[gmHL7Defs.OBX_field__subid] = ''
			prev_identity[gmHL7Defs.OBX_field__value] = ''
			prev_identity = '|'.join(prev_identity)
			continue
		# non-first FT type OBX
		curr_identity = line.split('|')
		curr_identity[gmHL7Defs.OBX_field__set_id] = ''
		curr_identity[gmHL7Defs.OBX_field__subid] = ''
		curr_identity[gmHL7Defs.OBX_field__value] = ''
		curr_identity = '|'.join(curr_identity)
		if curr_identity != prev_identity:
			# write out previous line
			hl7_out.write('|'.join(prev_fields) + gmHL7Defs.HL7_EOL)
			# keep current fields, since it may start a "repeat FT type OBX block"
			prev_fields = curr_fields
			prev_identity = curr_identity
			continue
		if prev_fields[gmHL7Defs.OBX_field__value].endswith(gmHL7Defs.HL7_BRK):
			prev_fields[gmHL7Defs.OBX_field__value] += curr_fields[gmHL7Defs.OBX_field__value]
		else:
			if curr_fields[gmHL7Defs.OBX_field__value].startswith(gmHL7Defs.HL7_BRK):
				prev_fields[gmHL7Defs.OBX_field__value] += curr_fields[gmHL7Defs.OBX_field__value]
			else:
				prev_fields[gmHL7Defs.OBX_field__value] += gmHL7Defs.HL7_BRK
				prev_fields[gmHL7Defs.OBX_field__value] += curr_fields[gmHL7Defs.OBX_field__value]
	if prev_fields is not None:
		hl7_out.write('|'.join(prev_fields) + gmHL7Defs.HL7_EOL)
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

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')
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
		print(HL7.extract_field('PID', segment_num = 1, field_num = gmHL7Defs.PID_field__name, component_num = gmHL7Defs.PID_component__lastname))
		print(HL7.extract_field('PID', segment_num = 1, field_num = gmHL7Defs.PID_field__name, component_num = gmHL7Defs.PID_component__lastname))

#			incoming['firstnames'] = HL7.extract_field('PID', segment_num = 1, field_num = gmHL7Defs.PID_field__name, component_num = gmHL7Defs.PID_component__firstname)
#			val = HL7.extract_field('PID', segment_num = 1, field_num = gmHL7Defs.PID_field__name, component_num = gmHL7Defs.PID_component__middlename)
#			if val is not None:
#				incoming['firstnames'] += u' '
#				incoming['firstnames'] += val
#			val = HL7.extract_field('PID', segment_num = 1, field_num = gmHL7Defs.PID_field__dob)
#			if val is not None:
#				tmp = time.strptime(val, '%Y%m%d')
#				incoming['dob'] = pyDT.datetime(tmp.tm_year, tmp.tm_mon, tmp.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)
#			val = HL7.extract_field('PID', segment_num = 1, field_num = gmHL7Defs.PID_field__gender)
#			if val is not None:
#				incoming['gender'] = val
#			incoming['external_data_id'] = filename

	#-------------------------------------------------------
	#test_format_hl7_message()
	#test_format_hl7_file(sys.argv[2])
	#test___fix_malformed_hl7()
	test_parse_hl7()
