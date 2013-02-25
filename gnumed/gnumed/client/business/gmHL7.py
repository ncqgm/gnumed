# -*- coding: utf8 -*-
"""Some HL7 handling."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import sys
import codecs
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools


_log = logging.getLogger('gm.hl7')
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
		MSH_file.write(line)

	if MSH_file is not None:
		MSH_file.close()
	hl7_in.close()

	return MSH_fnames

#============================================================
def split_MSH_by_PID(filename):
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
				MSH_line = line
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
		PID_file.write(line)

	if PID_file is not None:
		PID_file.close()
	MSH_in.close()

	return PID_fnames

#============================================================
def split_hl7_by_PID(filename, encoding='utf8'):

	PID_fnames = []
	for MSH_fname in split_hl7_by_MSH(filename, encoding):
		PID_fnames.extend(split_MSH_by_PID(MSH_fname))

	return PID_fnames
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2
#	from Gnumed.pycommon import gmI18N

#	gmI18N.activate_locale()
#	gmDateTime.init()

	#-------------------------------------------------------
	def test_split_by_patient():
		for name in split_hl7_by_PID(sys.argv[2], encoding='utf8'):
			print name

	#-------------------------------------------------------
	test_split_by_patient()
