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
# $Id: gmLDTimporter.py,v 1.3 2004-04-20 00:16:27 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL, details at http://www.gnu.org"

# stdlib
import glob, os.path, sys, tempfile, fileinput

from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

from Gnumed.pycommon import gmCfg, gmPG, gmLoginInfo, gmExceptions
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.business import gmPathLab
from Gnumed.business.gmXdtMappings import map_Befundstatus_xdt2gm, xdt_Befundstatus_map

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
		if not self.__verify_file_header(self.ldt_filename):
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
		file_list = self.__split_file(self.ldt_filename)
		if file_list is None:
			_log.Log(gmLog.lErr, 'cannot split LDT file [%s]' % self.ldt_filename)
			return False

		print "initial request files:", file_list

		# import request results
		for request_file in file_list['data']:
			if self.__import_request_result(request_file):
				# remove from file_list
				file_list['data'].remove(request_file)
			else:
				_log.Log(gmLog.lErr, 'cannot import LDT request result from [%s]' % request_file)

		print "left over request files:", file_list

		# reassemble file if anything left
		if len(file_list['data']) > 0:
			pass

		# clean up

		return True
	#-----------------------------------------------------------
	# internal helpers
	#-----------------------------------------------------------
	def __import_request_result(self, filename):
		request = self.__import_request_header(filename)
		if request is False:
			return False
		data = {}
		for line in fileinput.input(filename):
			line_type = line[3:7]
			line_data = line[7:-2]
			# start of new record
			if line_type == '8401':
				# first record
				if data == {}:
					data['code'] = line_data
					continue
				# save old record
				# - verify/create test type
				try:
					ttype = gmPathLab.cTestType(lab=self.__lab_name, code=data['code'], name=data['name'])
				except ConstructorError, err:
					_log.LogException(err, sys.exc_info(), verbose=0)
					
				# handle test result
				# and start new one
				data = {}
				data['code'] = line_data
				continue
		return True
	#-----------------------------------------------------------
	def __import_request_header(self, filename):
		header = {}
		request = None
		for line in fileinput.input(filename):
			line_type = line[3:7]
			line_data = line[7:-2]
			# found header
			if line_type == '8000':
				if line_data not in ['8202']:
					_log.Log(gmLog.lErr, "don't know how to handle [%s] results" % line_data)
					fileinput.close()
					return False
				self.__result_type = line_data
				continue
			# or start of following record
			elif line_type in ['8410']:
				if request is None:
					_log.Log(gmLog.lErr, 'no request header found !')
					fileinput.close()
					return False
				# sanity check
				if (request['is_pending'] == False) and (header['request_status'] != 'final'):
					_log.Log(gmLog.lWarn, 'kein Befund für [%s:%s] mehr erwartet, aber Befund mit Status [%s] in [%s] enthalten (Feld 8401, Regel 135)' % (self.__lab_name, request['request_id'], request['request_status'], self.ldt_filename))
					problem = 'kein Befund für [%s:%s] mehr erwartet, aber Befund mit Status [%s] in [%s] enthalten)' % (self.__lab_name, request['request_id'], request['request_status'], self.ldt_filename)
					solution = 'Befund wird trotzdem importiert. Bitte Befunde für Anforderung [%s] an Labor [%s] auf Duplikate überprüfen.' % (request['request_id'], self.__lab_name)
					insert_housekeeping_todo(problem, solution, 'user')
					# don't set is_pending to True if previously False and erroneous record received
					header['request_status'] = 'final'
				# update request record from header dict
				for field in header.keys():
					request[field] = header[field]
				request.save_payload()
				fileinput.close()
				return request
			# or request ID
			elif line_type == '8310':
				# if it's an LG-Bericht we know we have a request id
				if self.__result_type == '8202':
					try:
						request = gmPathLab.cLabRequest(req_id=line_data, lab=self.__lab_name)
					except gmExceptions.ConstructorError:
						_log.LogException('cannot get lab request', sys.exc_info(), verbose=0)
						fileinput.close()
						return False
				else:
					_log.Log(gmLog.lErr, "don't know how to handle [%s] results" % self.__result_type)
					fileinput.close()
					return False
				continue
			# or request status
			elif line_type == '8401':
				try:
					header['request_status'] = map_Befundstatus_xdt2gm[line_data]
				except KeyError:
					_log.LogException('unbekannter Befundstatus [%s] (Feld 8401, Regel 135)' % line_data, sys.exc_info(), verbose=0)
					fileinput.close()
					return False
				# deduce pending status
				if header['request_status'] == 'final':
					header['is_pending'] = False
				else:
					header['is_pending'] = True
				continue
			# or gender
			elif line_type == '8407':
				# FIXME: map and validate
				self.__gender = line_data
			# or other data
			elif line_type == '8311':
				header['lab_request_id'] = line_data
				continue
			elif line_type == '8301':
				header['lab_rxd_when'] = line_data
				continue
			elif line_type == '8302':
				header['results_reported_when'] = line_data
				continue
			elif line_type == '8405':
				header['narrative'] = line_data
				continue
			elif line_type == '8100':
				continue
			else:
				_log.Log(gmLog.lErr, "don't know how to import [%s] line" % line_type)
				fileinput.close()
				return False
	#-----------------------------------------------------------
	def __verify_file_header(self, filename):
		"""Verify that header is suitable for import.

		This does not verify whether the header is conforming
		to the LDT specs but rather that it is fit for import.
		"""
		verified_lines = 0
		for line in fileinput.input(filename):
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
					_log.Log(gmLog.lErr, 'cannot handle LDT file [%s]' % filename)
					fileinput.close()
					return False

		_log.Log(gmLog.lErr, 'LDT file [%s] contains nothing but a header' % filename)
		fileinput.close()
		return False
	#-----------------------------------------------------------
	def __split_file(self, filename):
		tempfile.tempdir = self.work_dir
		file_list = {}
		file_list['data'] = []
		for line in fileinput.input(filename):
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
			problem = 'Labor [%s] unbekannt. Import von [%s] abgebrochen.' % (field_data, self.ldt_filename)
			solution = 'Labor ergänzen oder vorhandenes Labor anpassen (test_org.internal_name).'
			insert_housekeeping_todo(problem, solution, 'user')
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
def insert_housekeeping_todo(problem=None, solution='', recipient='DEFAULT'):
	reporter = '$RCSfile: gmLDTimporter.py,v $ $Revision: 1.3 $'
	if problem is None:
		problem = 'lazy programmer'
	cmd = "insert into housekeeping_todo (reported_by, reported_to, problem, solution) values (%s, %s, %s, %s)"
	status, err = gmPG.run_commit('historica', [(cmd, [reporter, recipient, problem, solution])], True)
	if status is None:
		_log.Log(gmLog.lErr, err)
	return status
#---------------------------------------------------------------
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
# Revision 1.3  2004-04-20 00:16:27  ncq
# - try harder to become useful
#
# Revision 1.2  2004/04/16 00:34:53  ncq
# - now tries to import requests
#
# Revision 1.1  2004/04/13 14:24:07  ncq
# - first version here
#
