# -*- coding: utf-8 -*-
"""HL7 data mapping definitions."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try: _
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()

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

HL7_EOL = '\r'
HL7_BRK = r'\.br\ '.rstrip()

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
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	# setup a real translation
	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	g = globals().copy()
	for key in g:
		if key.startswith('HL7_'):
			print(key, ':\n', g[key])
