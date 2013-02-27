# -*- coding: utf8 -*-
"""Some HL7 handling."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import codecs
import logging
import hl7 as pyhl7


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools

from Gnumed.business import gmPathLab


_log = logging.getLogger('gm.hl7')

# constants
MSH_sending_lab = 3

PID_name = 5
PID_lastname = 0
PID_firstname = 1
PID_middlename = 2

OBX_type = 3
OBX_LOINC = 0
OBX_name = 1
OBX_value = 5
OBX_unit = 6

#============================================================
def split_hl7_by_MSH(filename, encoding='utf8'):

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
			out_fname = gmTools.get_unique_filename(prefix = u'%s.MSH_%s.' % (filename, idx))
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

		IOW, what's created by split_hl7_into_MSH()
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
			out_fname = gmTools.get_unique_filename(prefix = u'%s.PID_%s.' % (filename, idx))
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
def split_hl7_by_PID(filename, encoding='utf8'):

	PID_fnames = []
	for MSH_fname in split_hl7_by_MSH(filename, encoding):
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
		raise ValueError('LOINC code mismatch between GM (%s) and HL7 (%s) for result type [%s]', tt['loinc'], loinc, name)

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
		__find_or_create_test_type(tt[OBX_LOINC], tt[OBX_name], gm_lab['pk_test_org'], OBX[OBX_unit][0])

	# verify patient is in database
	name = HL7.segment('PID')[PID_name]
	pat_lname = name[PID_lastname]
	pat_fname = name[PID_firstname]
	pat_mname = None
	if len(name) > 2:
		pat_mname = name[PID_middlename]
	print " Patient: %s (%s) %s" % (pat_fname, pat_mname, pat_lname)

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2

	#-------------------------------------------------------
	def test_import_hl7():
		PID_names = split_hl7_by_PID(sys.argv[2], encoding='utf8')
		for name in PID_names:
			print name
			import_MSH(name)

	#-------------------------------------------------------
	test_import_hl7()
