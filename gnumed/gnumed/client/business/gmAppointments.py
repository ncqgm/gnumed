# -*- coding: utf-8 -*-
"""Handling appointments."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"


import csv
import os
import sys
import logging
import datetime as pydt


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmShellAPI


_log = logging.getLogger('gm.appointment')

_KONSOLEKALENDAR_IS_BUGGY = None
_KONSOLEKALENDAR_BINARY_NAME = 'konsolekalendar'
_KONSOLEKALENDER_CALENDARS_LOGGED = False

#============================================================
def __konsolekalendar_is_buggy() -> bool:
	"""Detect whether konsolekalender seems buggy.

		Determine whether the date-range bug in konsolekalendar
		is present or not. (Should be fixed by version 6.7.2 of
		konsolekalendar.)
			Does that by comparing output results for:
				--view (could be buggy)
				--next (known to work)

	Logic contributed by Maria.
	"""
	global _KONSOLEKALENDAR_IS_BUGGY
	if _KONSOLEKALENDAR_IS_BUGGY is not None:
		return _KONSOLEKALENDAR_IS_BUGGY

	# just for kicks, log available calendars ;-)
	global _KONSOLEKALENDER_CALENDARS_LOGGED
	if not _KONSOLEKALENDER_CALENDARS_LOGGED:
		cmd_line = [_KONSOLEKALENDAR_BINARY_NAME, '--verbose', '--list-calendars']
		success, exitcode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, timeout = 1, verbose = True)
		if success:
			_log.debug(stdout)
		else:
			_log.error('problem listing KOrganizer calendars')
			# ignore in the hope it was a fluke

	# what works for sure: output with --next (just one event)
	cmd_line = [_KONSOLEKALENDAR_BINARY_NAME, '--verbose', '--next', '--export-type', 'csv']
	success, exitcode, output_from_next = gmShellAPI.run_process(cmd_line = cmd_line, timeout = 2, verbose = True)
	if not success:
		_log.error('problem retrieving appointments from KOrganizer')
		return None

	if not output_from_next:
		# if there's no output from --next we cannot detect the bug
		# because there are no appointments to retrieve and compare
		# potential --view output to
		_log.debug('no --next appointment found in KOrganizer, cannot check for bug')
		return None

	date_by_next = output_from_next[:10]
	_log.debug('--next appointment found in KOrganizer: %s', date_by_next)
	# attempt --view retrieval
	cmd_line = [
		_KONSOLEKALENDAR_BINARY_NAME,
		'--verbose',
		'--view',
		'--date', date_by_next,
		'--time', '00:00:00',
		'--end-time', '23:59:59'
		#,'--export-type', 'csv'		# should not matter ?
	]
	success, exitcode, output_from_view = gmShellAPI.run_process(cmd_line = cmd_line, timeout = 2, verbose = True)
	if not success:
		_log.error('problem retrieving appointments from KOrganizer, should not happen because it worked just moments ago')
		return None

	if output_from_view:
		_KONSOLEKALENDAR_IS_BUGGY = False
		return False

	_log.error('KOrganizer via konsolekalendar: "--next" tells us there *are* events for [%s] but "--view" does not return them (known bug)', date_by_next)
	_KONSOLEKALENDAR_IS_BUGGY = True
	return True

#------------------------------------------------------------
def __csv_from_all_appointments(target_date:str=None, verbose:bool=False) -> str:
	"""Only called if konsolekalendar date-range bug is still
	present. (As long as --view does not generate event
	output, even if there are events for the day.)

	Gets ALL the calendar's entries, filters only today's,
	and re-saves self.fname so that it only includes those.

	Could be slow, since it will have to get all of the
	calendar entries.

	target_date: YYYY-MM-DD

	Added: 2026 05 26, logic by Maria
	"""
	# gets ALL calendar items in a csv -- the only functional output due to the bug
	csv_fname_all = gmTools.get_unique_filename(prefix = 'konsolekalendar2gnumed-', suffix = '.--all.csv')
	cmd_line = [
		_KONSOLEKALENDAR_BINARY_NAME,
		'--view',
		'--all',
		'--export-type', 'csv',
		'--export-file', '"%s"' % csv_fname_all
	]
	success, exitcode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, timeout = 4, verbose = verbose)
	if not success:
		_log.error('problem running konsolekalendar')
		return None

	try:
		csv_file_all = open(csv_fname_all, mode = 'rt', encoding = 'utf-8-sig', errors = 'replace')
	except IOError:
		_log.error('cannot open transfer file [%s]', csv_fname_all)
		return None

	csv_name_target_date = gmTools.get_unique_filename(prefix = 'konsolekalendar2gnumed-', suffix = '.csv')
	try:
		csv_file_target_date = open(csv_name_target_date, mode = 'wt', encoding = 'utf-8', errors = 'replace')
	except IOError:
		_log.error('cannot open transfer file [%s]', csv_fname_target_date)
		csv_file_all.close()
		return None

	csv_lines_all = gmTools.unicode_csv_reader(csv_file_all, delimiter = ',')
	csv_writer_target_date = csv.writer(csv_file_target_date, delimiter = ',', lineterminator = '\n')
	if not target_date:
		target_date = pydt.date.today().isoformat()[:10]
	for line in csv_lines_all:
		if len(line) < 8:			# <10 ?   (YYYY-MM-DD)
			continue
		if line[0] != target_date:
			continue
		csv_writer_target_date.writerow(line)
	csv_file_target_date.close()
	csv_file_all.close()
	return csv_name_target_date

#------------------------------------------------------------
def get_appointments_for_today_from_korganizer(verbose:bool=False) -> str:
	"""Generates the KOrganizer transfer file, a .csv file with today's events."""
	today = pydt.date.today().isoformat()[:10]
	if not __konsolekalendar_is_buggy():
		csv_name = gmTools.get_unique_filename(prefix = 'konsolekalendar2gnumed-', suffix = '.csv')
		cmd_line = [
			_KONSOLEKALENDAR_BINARY_NAME,
			'--view',
			'--date', today,
			'--time', '00:00:00',
			'--end-time', '23:59:59',
			'--export-type', 'csv',
			'--export-file', '"%s"' % csv_name
		]
		success, exitcode, stdout = gmShellAPI.run_process(cmd_line = cmd_line, timeout = 2, verbose = verbose)
		if success:
			return csv_name

		_log.error('problem running konsolekalendar')
		return None

	return __csv_from_all_appointments(taget_date = today, verbose = verbose)

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmTools.gmPaths()
	#-------------------------------------------------------
	def test():
		print(get_appointments_for_today_from_korganizer(verbose = True))
	#-------------------------------------------------------
	test()
