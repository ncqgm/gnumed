# -*- coding: latin-1 -*-
"""GnuMed LDT importer.

This script automatically imports German pathology result
files in LDT format.

It relies on patient-to-request-ID mappings to be present
in the GnuMed database. It will only import those request
that have a mapping.

The general theory of operation of automatic import at
Hilbert office is as follows:

- automatically retrieve LDT files from labs
- archive them
- make them available in a GnuMed private directory
- run importer every hour
- import those records that have a mapping
- make those records available to TurboMed
- retain unmapped records until next time around

copyright: authors
"""
#===============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/importers/gmLDTimporter.py,v $
# $Id: gmLDTimporter.py,v 1.1 2004-04-13 14:24:07 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL, details at http://www.gnu.org"

from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

from Gnumed.pycommon import gmCfg, gmPG, gmLoginInfo, gmExceptions
from Gnumed.pycommon.gmPyCompat import *

import glob, os.path, sys, tempfile, fileinput

_cfg = gmCfg.gmDefCfgFile

lines_8220 = [
	'8000',
	'8100',
	'9211',
	'9221',
	'0201',
	'0203',
	'0204',
	'0205',
	'0206',
	'8300',
	'0101',
	'9106',
	'8312',
	'9103',
	'9300',
	'9301']

lines_8202 = [
	'8000',
	'8100',
	'8310',
	'8311',
	'8301',
	'8302',
	'3103',
	'8401',
	'8405',
	'8407',
	'8410',
	'8411',
	'8412',
	'8418',
	'8428',
	'8429',
	'8430',
	'8431',
	'8420',
	'8421',
	'8480',
	'8470',
	'8460',
	'8422',
	'8490']

#===============================================================
class cLDTImporter:

	def __init__(self, cfg=None):
		self._cfg = cfg
		# verify db connectivity
		pool = gmPG.ConnectionPool()
		conn = pool.GetConnection('historica')
		if conn is None:
			_log.Log(gmLog.lErr, 'cannot connect to database')
			raise gmExceptions.ConstructorError, 'cannot connect to database'
		else:
			pool.ReleaseConnection('historica')
			return
	#-----------------------------------------------------------
	def import_file(self, filename=None):
		# verify ldt file
		if not os.access(filename, os.R_OK):
			_log.Log(gmLog.lErr, 'cannot access LDT file [%s] for reads' % filename)
			return False
		self.ldt_filename = filename

		# verify header of LDT file
		if not self.__verify_file_header():
			return False

		# verify base working directory
		self.work_base = self._cfg.get('import', 'work dir base')
		if self.work_base is None:
			self.work_base = os.path.dirname(self.ldt_filename)
		self.work_base = os.path.expanduser(os.path.abspath(self.work_base))
		if not os.access(self.work_base, os.W_OK):
			_log.Log(gmLog.lErr, 'cannot write to work directory [%s]' % self.work_base)
			return False

		# create scratch directory
		tempfile.tempdir = self.work_base
		self.work_dir = tempfile.mktemp()
		os.mkdir(self.work_dir, 0700)

		# split into parts
		part_list = self.__split_file()
		if part_list is None:
			_log.Log(gmLog.lErr, 'cannot split LDT file [%s]' % self.ldt_filename)
			return False

		print part_list

		for part in part_list:
			if self.import_request_results(part):
				# delete part file
				# remove from part_list
				pass
			else:
				_log.Log(gmLog.lErr, 'cannot import LDT request results from [%s]' % part)

		# reassemble file if anything left
		if len(part_list) > 0:
			pass

#		self.bak_filename = tempfile.mktemp()
#		self.bak_file = open(self.bak_filename, 'wb')

		# clean up

		return True
	#-----------------------------------------------------------
	# internal helpers
	#-----------------------------------------------------------
	def __verify_file_header(self):
		"""Verify that header is suitable for import.

		This does not verify whether the header is conforming
		to the LDT specs but rather that it is fit for import.
		"""
		verified_lines = 0
		for line in fileinput.input(self.ldt_filename):
			line_type = line[3:7]
			line_data = line[7:-2]
			# found start of record following header
			if line_type == '8000':
				if line_data != '8220':
					fileinput.close()
					return (verified_lines == len(cLDTImporter._map_field2verifier))
			else:
				try:
					verify_line = cLDTImporter._map_field2verifier[line_type]
				except KeyError:
					continue
				if verify_line(self, line, line_data):
					verified_lines += 1
				else:
					_log.Log(gmLog.lErr, 'cannot handle LDT file [%s]' % self.ldt_filename)
					fileinput.close()
					return False

		_log.Log(gmLog.lErr, 'LDT file [%s] contains nothing but a header' % self.ldt_filename)
		fileinput.close()
		return False
	#-----------------------------------------------------------
	def __split_file(self):
		tempfile.tempdir = self.work_dir
		file_list = {}
		file_list['data'] = []
		for line in fileinput.input(self.ldt_filename):
			line_type = line[3:7]
			line_data = line[7:-2]
			if line_type == '8000':
				# start of header == start of file
				if line_data == '8220':
					outname = os.path.join(self.work_dir, 'header.txt')
					file_list['header'] = outname
					outfile = open(outname, 'w+b')
				# start of trailer
				elif line_data == '8221':
					outfile.close()
					outname = os.path.join(self.work_dir, 'trailer.txt')
					file_list['trailer'] = outname
					outfile = open(outname, 'w+b')
				# start of LG-Bericht
				elif line_data == '8202':
					outfile.close()
					outname = os.path.join(self.work_dir, tempfile.mktemp(suffix='.txt'))
					file_list['data'].append(outname)
					outfile = open(outname, 'w+b')
			# keep line
			outfile.write(line)

		# end of file
		outfile.close()
		fileinput.close()
		return file_list
	#-----------------------------------------------------------
	def _verify_8300(self, a_line, field_data):
		cmd = "select exists(select pk from test_org where internal_name=%s)"
		status = gmPG.run_ro_query('historica', cmd, None, field_data)
		if status is None:
			_log.Log(gmLog.lErr, 'cannot check for lab existance on [%s]' % field_data)
			return False
		if not status[0][0]:
			_log.Log(gmLog.lErr, 'Unbekanntes Labor [%s]' % field_data)
			reporter = '$RCSfile: gmLDTimporter.py,v $ $Revision: 1.1 $'
			problem = 'Labor [%s] unbekannt. Import von [%s] abgebrochen.' % (field_data, self.ldt_filename)
			solution = 'Labor ergänzen oder vorhandenes Labor anpassen (test_org.internal_name).'
			cmd = "insert into housekeeping_todo (reported_by, problem, solution) values (%s, %s, %s)"
			gmPG.run_commit('historica', [(cmd, [reporter, problem, solution])])
			return False
		self.__lab_name = field_data
		return True
	#-----------------------------------------------------------
	def _verify_9211(self, a_line, field_data):
		if field_data not in ['09/95']:
			_log.Log(gmLog.lWarn, 'not sure whether I can handle LDT version [%s]' % field_data)
		return True
	#-----------------------------------------------------------
	_map_field2verifier = {
		'8300': _verify_8300,
		'9211': _verify_9211
		}
#===============================================================
def verify_next_in_chain():
	tmp = _cfg.get('target', 'repository')
	if tmp is None:
		return False
	target_dir = os.path.expanduser(os.path.abspath(tmp))
	if not os.access(target_dir, os.W_OK):
		_log.Log(gmLog.lErr, 'cannot write to target repository [%s]' % target_dir)
		return False
	return True
#---------------------------------------------------------------
# LDT functions
#---------------------------------------------------------------
#def _verify_9221(a_line, field_data):
	# FIXME: check minor version, too
#	return True
#---------------------------------------------------------------
#def _verify_0203(a_line, field_data):
	# FIXME: validate against database
#	return True
#---------------------------------------------------------------
def run_import():
	# make sure files can be made available to TurboMed
	if not verify_next_in_chain():
		return False
	# get import files
	import_dir = _cfg.get('import', 'repository')
	if import_dir is None:
		return False
	import_dir = os.path.expanduser(os.path.abspath(import_dir))
	filename_pattern = _cfg.get('import', 'file pattern')
	if filename_pattern is None:
		return False
	import_file_pattern = os.path.join(import_dir, filename_pattern)
	files2import = glob.glob(import_file_pattern)
	_log.Log(gmLog.lData, 'importing files: %s' % files2import)
	# loop over files
	for ldt_file in files2import:
		importer = cLDTImporter(cfg=_cfg)
		if not importer.import_file(ldt_file):
			_log.Log(gmLog.lErr, 'cannot import LDT file [%s]' % ldt_file)
	return True
#===============================================================
# main
#---------------------------------------------------------------
if __name__ == '__main__':
	if _cfg is None:
		_log.Log(gmLog.lErr, 'need config file to run')
		sys.exit(1)
	# set encoding
	gmPG.set_default_client_encoding('latin1')
	# setup login defs
	auth_data = gmLoginInfo.LoginInfo(
		user = _cfg.get('database', 'user'),
		passwd = _cfg.get('database', 'password'),
		host = _cfg.get('database', 'host'),
		port = _cfg.get('database', 'port'),
		database = _cfg.get('database', 'database')
	)
	backend = gmPG.ConnectionPool(login = auth_data)
	# actually run the import
	run_import()

#===============================================================
# $Log: gmLDTimporter.py,v $
# Revision 1.1  2004-04-13 14:24:07  ncq
# - first version here
#
