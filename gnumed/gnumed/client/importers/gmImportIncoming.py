#!/usr/bin/python3
# -*- coding: utf-8 -*-



__doc__ = """Incoming data importer."""
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"
#============================================================

# stdlib
import sys
import os


# do not run as root
if os.name in ['posix'] and os.geteuid() == 0:
	print("""
%s should not be run as root.

Running as <root> can potentially put all your
medical data at risk. It is strongly advised
against. Please run as a non-root user.
""" % sys.argv[0])
	sys.exit(1)


# when attempting to run from a tarball:
if '--local-import' in sys.argv:
	sys.path.insert(0, '../../')


# stdlib
import logging

# GNUmed
from Gnumed.pycommon import gmCfg2
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools

from Gnumed.business import gmIncomingData


_log = logging.getLogger('importer')

# update man page and help text when changing options
_known_short_options = 'h?'
_known_long_options = [
	'help',
	'local-import',
	'data-type=',
	'file2import=',
	'user=',
	'host=',
	'port='
]

# update man page when changing options
_help_text = """
--------------------------------------------------------------------------------------
Command line:
 %s

Usage synopsis:
 %s --local-import --file2import=DATA --data-type=TYPE --user=USER --host=HOST --port=PORT

  --local-import: use when running from a tarball

  DATA: full path of data file to import
  TYPE: short description of file to be shown in GNUmed (say, "fax")
  USER: PostgreSQL user in database [%s]
  HOST: host name of machine running PostgreSQL, if needed
  PORT: port at which PostgreSQL listens on HOST, if needed, typically 5432

See the man page for more details.

Log file:
 %s
--------------------------------------------------------------------------------------"""

#============================================================
def import_file(data_type, filename):

	_log.info('[%s]: %s', data_type, filename)

	inc = gmIncomingData.create_incoming_data(data_type, filename)
	if inc is None:
		_log.error('import failed')
	else:
		_log.info('success')
		target_filename = filename + '.imported'
		_log.debug('[%s] -> [%s]', filename, target_filename)
		try:
			os.rename(filename, target_filename)
		except OSError:
			_log.exception('cannot rename [%s] to [%s]', filename, target_filename)
	return inc

#	u'request_id',						# request ID as found in <data>
#	u'firstnames',
#	u'lastnames',
#	u'dob',
#	u'postcode',
##	u'other_info',						# other identifying info in .data
#	u'gender',
#	u'requestor',						# Requestor of data (e.g. who ordered test results) if available in source data.
#	u'external_data_id',				# ID of content of .data in external system (e.g. importer) where appropriate
#	u'comment',							# a free text comment on this row, eg. why is it here, error logs etc

#============================================================
def process_options():

	if _cfg.get(option = '-h', source_order = [('cli', 'return')]):
		show_usage()
		sys.exit(0)

	if _cfg.get(option = '-?', source_order = [('cli', 'return')]):
		show_usage()
		sys.exit(0)

	if _cfg.get(option = '--help', source_order = [('cli', 'return')]):
		show_usage()
		sys.exit(0)

	file2import = _cfg.get(option = '--file2import', source_order = [('cli', 'return')])
	if file2import is None:
		exit_with_message('ERROR: option --file2import missing')
	if file2import is True:
		exit_with_message('ERROR: data file missing in option --file2import=')
	try:
		open(file2import).close()
	except IOError:
		_log.exception('cannot open data file')
		exit_with_message('ERROR: cannot open data file in option --file2import=%s' % file2import)

	datatype = _cfg.get(option = '--data-type', source_order = [('cli', 'return')])
	if datatype is None:
		exit_with_message('ERROR: option --data-type missing')
	if datatype is True:
		exit_with_message('ERROR: data type missing in option --data-type=')
	if datatype.strip() == '':
		exit_with_message('ERROR: invalid data type in option --data-type=>>>%s<<<' % datatype)

	db_user = _cfg.get(option = '--user', source_order = [('cli', 'return')])
	if db_user is None:
		exit_with_message('ERROR: option --user missing')
	if db_user is True:
		exit_with_message('ERROR: user name missing in option --user=')
	if db_user.strip() == '':
		exit_with_message('ERROR: invalid user name in option --user=>>>%s<<<' % db_user)

	db_host = _cfg.get(option = '--host', source_order = [('cli', 'return')])
	if db_host is None:
		_log.debug('option --host not set, using <UNIX domain socket> on <localhost>')
	elif db_host is True:
		exit_with_message('ERROR: host name missing in option --host=')
	elif db_host.strip() == '':
		_log.debug('option --host set to "", using <UNIX domain socket> on <localhost>')
		db_host = None

	db_port = _cfg.get(option = '--port', source_order = [('cli', 'return')])
	if db_port is None:
		_log.debug('option --port not set, using <UNIX domain socket> on <localhost>')
	elif db_port is True:
		exit_with_message('ERROR: port value missing in option --port=')
	elif db_port.strip() == '':
		_log.debug('option --port set to "", using <UNIX domain socket> on <localhost>')
		db_port = None
	else:
		converted, db_port = gmTools.input2int(initial = db_port, minval = 1024, maxval = 65535)
		if not converted:
			exit_with_message('ERROR: invalid port in option --port=%s (must be 1024...65535)' % db_port)

	return datatype, file2import

#	val = _cfg.get(option = '--debug', source_order = [('cli', 'return')])
#	_cfg.set_option (
#		option = u'debug',
#		value = val
#	)

#============================================================
def exit_with_message(message=None):
	if message is not None:
		_log.error(message)
		print('')
		print(message)
	show_usage()
	sys.exit(1)

#============================================================
def show_usage():
	from Gnumed.pycommon import gmLog2
	print(_help_text % (
		' '.join(sys.argv),
		sys.argv[0],
		gmPG2.default_database,
		gmLog2._logfile_name
	))

#============================================================
if __name__ == '__main__':

	_cfg = gmCfg2.gmCfgData()
	_cfg.add_cli (
		short_options = _known_short_options,
		long_options = _known_long_options
	)
	datatype, file2import = process_options()
	inc = import_file(datatype, file2import)
	sys.exit(0)

#	print('Log file:')
#	from Gnumed.pycommon import gmLog2
#	print(' %s' % gmLog2._logfile_name)
