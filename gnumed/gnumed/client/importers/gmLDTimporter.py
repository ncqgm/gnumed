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

FIXME: check status on save_payload()s
"""
#===============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/importers/gmLDTimporter.py,v $
# $Id: gmLDTimporter.py,v 1.28 2006-10-25 07:46:44 ncq Exp $
__version__ = "$Revision: 1.28 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL, details at http://www.gnu.org"

# stdlib
import glob, os.path, sys, tempfile, fileinput, time, copy, random, shutil

from Gnumed.pycommon import gmLog, gmCLI
if __name__ == '__main__':
	if gmCLI.has_arg('--debug'):
		gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)
	else:
		gmLog.gmDefLog.SetAllLogLevels(gmLog.lInfo)

from Gnumed.pycommon import gmCfg, gmLoginInfo, gmExceptions, gmI18N
from Gnumed.business import gmPathLab, gmXdtMappings, gmPerson

import mx.DateTime as mxDT

_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile
#===============================================================
class cLDTImporter:

	_chunk_starters = ['8000', '8410']
	_map_820xline2req_field = {
		'8311': 'lab_request_id',
		'8301': 'lab_rxd_when',
		'8401': 'request_status',
		'8405': 'progress_note'
	}

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
	#-----------------------------------------------------------
	def import_file(self, filename=None):
		# verify ldt file
		if not os.access(filename, os.R_OK):
			_log.Log(gmLog.lErr, 'cannot access LDT file [%s] for reads' % filename)
			return False
		self.ldt_filename = filename

		# verify header of LDT file
		if not self.__verify_file_header(self.ldt_filename):
			_log.Log(gmLog.lInfo, 'cannot verify file header on [%s]' % self.ldt_filename)
			return False

		# verify base working directory
		self.work_base = self._cfg.get('import', 'work dir base')
		if self.work_base is None:
			self.work_base = os.path.dirname(self.ldt_filename)
		self.work_base = os.path.abspath(os.path.expanduser(self.work_base))
		if not os.access(self.work_base, os.W_OK):
			_log.Log(gmLog.lErr, 'cannot write to work directory [%s]' % self.work_base)
			return False

		# create scratch directory
		tempfile.tempdir = self.work_base
		self.work_dir = tempfile.mktemp()
		os.mkdir(self.work_dir, 0700)

		# split into parts
		source_files = self.__split_file(self.ldt_filename)
		if source_files is None:
			_log.Log(gmLog.lErr, 'cannot split LDT file [%s]' % self.ldt_filename)
			return False

		# import requested results
		if len(source_files['data']) > 0:
			tmp_src_files = copy.copy(source_files['data'])
			for request_file in tmp_src_files:
				_log.Log(gmLog.lInfo, 'importing request file [%s]' % request_file)
				if self.__import_request_file(request_file):
					source_files['data'].remove(request_file)
					_log.Log(gmLog.lErr, 'success importing request file\n')
				else:
					_log.Log(gmLog.lErr, 'cannot import request file [%s]\n' % request_file)
		else:
			_log.Log(gmLog.lData, 'skipping empty LDT file [%s]' % self.ldt_filename)

		# cleanup work area
		try:
			shutil.rmtree(path=self.work_dir, ignore_errors=True)
		except:
			_log.LogException('cannot cleanup work dir [%s]' % self.work_dir, sys.exc_info(), verbose=0)

		# anything left ?
		if len(source_files['data']) > 0:
			# keep source file for next time
			return False
		return True
	#-----------------------------------------------------------
	# internal helpers
	#-----------------------------------------------------------
	def _verify_8300(self, a_line, field_data):
		cmd = "select exists(select pk from test_org where internal_name=%s)"
		status = gmPG.run_ro_query('historica', cmd, None, field_data)
		if status is None:
			_log.Log(gmLog.lErr, 'cannot check for lab existance on [%s]' % field_data)
			return False
		if not status[0][0]:
			_log.Log(gmLog.lErr, 'Unbekanntes Labor [%s]' % field_data)
			prob = 'Labor unbekannt. Import abgebrochen.' % field_data
			sol = 'Labor ergänzen oder vorhandenes Labor anpassen (test_org.internal_name).'
			ctxt = 'LDT-Datei [%s], Labor [%s]' % (self.ldt_filename, field_data)
			add_todo(problem=prob, solution=sol, context=txt)
			return False
		self.__lab_name = field_data
		return True
	#-----------------------------------------------------------
#	def _verify_9211(self, a_line, field_data):
#		_log.Log(gmLog.lInfo, 'LDT version [%s]' % field_data)
#		return True
	#-----------------------------------------------------------
	_map_field2verifier = {
		'8300': _verify_8300
#		'9211': _verify_9211
		}
	#-----------------------------------------------------------
	def __verify_file_header(self, filename):
		"""Verify that header is suitable for import.

		This does not verify whether the header is conforming
		to the LDT specs but rather that it is fit for import.
		"""
		verified_lines = 0
		in_header = False
		for line in fileinput.input(filename):
			tmp = line.replace('\r','')
			tmp = tmp.replace('\n','')
			line_type = tmp[3:7]
			line_data = tmp[7:]
			# found start of record
			if line_type == '8000':
				# header found ?
				if line_data == '8220':
					in_header = True
					continue
				# skip prepended junk
				if not in_header:
					continue
				# found record following header
				if line_data != '8220':
					fileinput.close()
					if verified_lines == len(cLDTImporter._map_field2verifier):
						return True
					_log.Log(gmLog.lErr, 'zuwenige verifizierbare Zeilen im LDT-Datei-Header')
					return False
			if not in_header:
				continue
			try:
				verify_line = cLDTImporter._map_field2verifier[line_type]
			except KeyError:
				_log.Log(gmLog.lData, 'kein Handler für Zeilentyp [%s] in LDT-Datei-Header' % line_type)
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
		"""Split LDT file.

		Splits LDT files into header (record type 8220), data
		records (8202, etc) and trailer (8221).
		"""
		tempfile.tempdir = self.work_dir
		source_files = {}
		source_files['data'] = []
		outname = None
		in_header = False
		in_trailer = False
		for line in fileinput.input(filename):
			tmp = line.replace('\r','')
			tmp = tmp.replace('\n','')
			line_type = tmp[3:7]
			line_data = tmp[7:]
			if line_type == '8000':
				# start headers == start of file
				if line_data in ['0020', '8220']:
					if not in_header:
						header = os.path.join(self.work_dir, 'header.txt')
						source_files['header'] = header
						outfile = open(header, 'w+b')
						in_header = True
				# start of trailer
				elif line_data in ['8221', '0021']:
					in_header = False
					# did we have any data records ?
					if outname is not None:
						# yes, so append them
						source_files['data'].append(outname)
					if not in_trailer:
						outfile.close()
						trailer = os.path.join(self.work_dir, 'trailer.txt')
						source_files['trailer'] = trailer
						outfile = open(trailer, 'w+b')
						in_trailer = True
				# start of data record
				else:
					in_header = False
					in_trailer = False
					outfile.close()
					# first record ?
					if outname is not None:
						# no, so append record name
						source_files['data'].append(outname)
					outname = os.path.join(self.work_dir, tempfile.mktemp(suffix='.txt'))
					outfile = open(outname, 'w+b')
					if line_data not in ['8202', '8201']:
						_log.Log(gmLog.lWarn, 'unbekannter Satztyp [%s]' % line_data)
			# keep line
			outfile.write(line)

		# end of file
		outfile.close()
		fileinput.close()
		return source_files
	#-----------------------------------------------------------
	#-----------------------------------------------------------
	def __xform_8311(self, request_data):
		return request_data['8311'][0].strip()
	#-----------------------------------------------------------
	def __xform_8301(self, request_data):
		return gmXdtMappings.xdt_8date2iso(request_data['8301'][0].strip())
	#-----------------------------------------------------------
	def __xform_8302(self, request_data):
		"""8302: Berichtsdatum"""
		if self.__request['results_reported_when'] is None:
			self.__request['results_reported_when'] = mxDT.now()
		self.__request['results_reported_when'] = mxDT.strptime(
			request_data['8302'][0].strip(),
			'%d%m%Y',
			self.__request['results_reported_when']
		)
		return None
	#-----------------------------------------------------------
	def __xform_8303(self, request_data):
		"""8303: Berichtszeit"""
		if self.__request['results_reported_when'] is None:
			self.__request['results_reported_when'] = mxDT.now()
		self.__request['results_reported_when'] = mxDT.strptime(
			request_data['8303'][0].strip(),
			'%H%M',
			self.__request['results_reported_when']
		)
		return None
	#-----------------------------------------------------------
	def __xform_3103(self, request_data):
		tmp = gmXdtMappings.xdt_8date2iso(request_data['3103'][0])
		# keep for result records to store
		self.__ref_group_str = ' / '.join([self.__ref_group_str, ("geb: %s" % tmp)])
		# - sanity check patient dob
		cmd = """
			select exists(
				select 1
				from clin.v_pat_items vpi, clin.lab_request lr, dem.identity i
				where
					vpi.pk_patient=i.pk
						and
					vpi.pk_item=%s
						and
					date_trunc('day', i.dob)=%s::timestamp
			)"""
		data = gmPG.run_ro_query('personalia', cmd, None, self.__request['pk_item'], tmp)
		if data is None:
			_log.Log(gmLog.lErr, 'cannot sanity check patient dob [%s]' % tmp)
		if not data[0]:
			_log.Log(gmLog.lErr, 'lab used [%s] as reference dob while patient has different dob !' % tmp)
			self.__ref_group_str = "!!!*** Im Labor wurde vermutlich ein falsches Referenzalter verwendet. ***!!!\n%s" % self.__ref_group_str
		return None
	#-----------------------------------------------------------
	def __xform_8401(self, request_data):
		try:
			req_stat = gmXdtMappings.map_Befundstatus_xdt2gm[request_data['8401'][0].strip()]
		except KeyError:
			_log.Log(gmLog.lErr, 'unbekannter Befundstatus [%s] (Feld 8401, Regel 135)' % request_data['8401'][0])
			req_stat = 'preliminary'
		# sanity check
		if (not self.__request['is_pending']) and (req_stat != 'final'):
			prob = 'kein Befund für [%s] mehr erwartet, aber Befund mit Status [%s] erhalten)' % (self.__request['request_id'], req_stat)
			sol = 'Befund wird trotzdem importiert. Bitte Befunde auf Duplikate überprüfen.'
			ctxt = 'Patient: %s, Labor [%s], LDT-Datei [%s], Probe [%s], (Feld 8401, Regel 135)' % (self.__request.get_patient(), self.__lab_name, self.ldt_filename, self.__request['request_id'])
			add_todo(problem=prob, solution=sol, context=ctxt)
			_log.Log(gmLog.lWarn, prob)
			_log.Log(gmLog.lWarn, ctxt)
			# don't force is_pending back to true just because
			# a wrong status was received from the lab
			req_stat = 'final'
		if req_stat == 'final':
			self.__request['is_pending'] = 'false'
		else:
			self.__request['is_pending'] = 'true'
		return req_stat
	#-----------------------------------------------------------
	def __xform_8405(self, request_data):
		new_comment = '\n'.join(request_data['8405'])
		old_narrative = self.__request['progress_note']
		if old_narrative is None:
			return new_comment
		if old_narrative.find(new_comment) == -1:
			old_narrative = old_narrative + '\n' + new_comment
		return old_narrative
	#-----------------------------------------------------------
	def __xform_8407(self, request_data):
		tmp = request_data['8407'][0]
		# keep this so test results can store it
		self.__ref_group_str = ' / '.join([gmXdtMappings.map_8407_2str[tmp], self.__ref_group_str])
		# - sanity check patient gender/age
		# I discussed the age cutoff with a pediatrician and
		# we came to the conclusion that a useful value for
		# child/adult age separation in terms of lab results
		# would be 12 years.
		# - get patient gender/age
		cmd = """
				select
					i.gender,
					case when i.dob < (now() - '12 years'::interval)
						then false
						else true
					end as is_child
				from v_pat_items vpi, lab_request lr, identity i
				where
					vpi.id_patient=i.pk
						and
					vpi.pk_item=%s"""
		data = gmPG.run_ro_query('personalia', cmd, None, self.__request['pk_item'])
		if data is None:
			_log.Log(gmLog.lErr, 'cannot sanity check patient ref group [%s]' % gmXdtMappings.map_8407_2str[tmp])
		elif len(data) == 0:
			_log.Log(gmLog.lErr, 'cannot sanity check patient ref group [%s]' % gmXdtMappings.map_8407_2str[tmp])
		else:
			gender = data[0]
			is_child = data[1]
			if tmp in [0,6]:
				self.__ref_group_str = "%s\n* Kann Referenzgruppe nicht mit Patient abgleichen. *" % self.__ref_group_str
			else:
					# Kind
				if (((tmp in [3,4,5]) and (not is_child)) or
					# männlich
					((tmp in [1,4]) and (gender != 'm')) or
					# weiblich
					((tmp in [2,5]) and (gender != 'f'))):
					_log.Log(gmLog.lErr, 'lab thinks patient is [%s] but patient is [%s:child->%s]' % (gmXdtMappings.map_8407_2str[tmp], gender, is_child))
					self.__ref_group_str = "!!!*** Im Labor wurde vermutlich eine falsche Referenzgruppe verwendet (Alter/Geschlecht). ***!!!\n%s" % self.__ref_group_str
		return None
	#-----------------------------------------------------------
	__820xline_handler = {
		'0020': None,
		'9105': None,
		'8000': None,
		'8100': None,
		'8310': None,
		'8311': __xform_8311,
		'8301': __xform_8301,
		'8302': __xform_8302,
		'8303': __xform_8303,
		'3100': None,
		'3101': None,
		'3102': None,
		'3103': __xform_3103,
		'3104': None,
		'8401': __xform_8401,
		'8403': None,			# Gebührenordnung
		'8405': __xform_8405,
		'8407': __xform_8407,
		'8609': None			# Gebührenordnung
	}
	#-----------------------------------------------------------
	def __handle_8202(self, request_data):
		# essential fields
		try:
			reqid = request_data['8310'][0]
		except KeyError, IndexError:
			# FIXME: todo item
			_log.Log(gmLog.lErr, 'Satz vom Typ [8000:%s] enthält keine Probennummer' % request_data['8000'][0])
			return False
		# get lab request
		try:
			self.__request = gmPathLab.cLabRequest(req_id=reqid, lab=self.__lab_name)
		except gmExceptions.ConstructorError:
			prob = 'Kann keine Patientenzuordnung der Probe finden.'
			sol = 'Zuordnung der Probe zu einem Patienten prüfen. Falls doch vorhanden, Systembetreuer verständigen.'
			ctxt = 'Labor [%s], Probe [%s], LDT-Datei [%s]' % (self.__lab_name, reqid, self.ldt_filename)
			add_todo(problem=prob, solution=sol, context=ctxt)
			_log.LogException('cannot get lab request', sys.exc_info(), verbose=0)
			return False
		# update fields in request from request_data
		for line_type in request_data.keys():
			# get handler
			try:
				handle_line = cLDTImporter.__820xline_handler[line_type]
			except KeyError:
				_log.LogException('no handler for line [%s:%s] in [8000:8201] record' % (line_type, request_data[line_type]), sys.exc_info(), verbose=0)
				continue
			# ignore line
			if handle_line is None:
				try:
					name = gmXdtMappings.xdt_id_map[line_type]
				except KeyError:
					name = '?'
				_log.Log(gmLog.lData, 'skipping [%s] (%s)' % (line_type, name))
				continue
			# handle line
			line_data = handle_line(self, request_data)
			if line_data is False:
				# FIXME: todo item
				_log.Log(gmLog.lErr, 'handling line [%s] failed' %  line_type)
				return False
			try:
				self.__request[cLDTImporter._map_820xline2req_field[line_type]] = line_data
			except KeyError:
				pass
		self.__request.save_payload()
		return True
	#-----------------------------------------------------------
	#-----------------------------------------------------------
	def __get_request_from_8201(self, request_data):
		request = None
		try:
			pat_ldt = {
				'lastnames': request_data['3101'][0],
				'firstnames': request_data['3102'][0],
				'dob': gmXdtMappings.xdt_8date2iso(request_data['3103'][0])
			}
		except KeyError, IndexError:
			pat_ldt = None
		# either get lab request from request id
		if request_data.has_key('8310'):
			reqid = request_data['8310'][0]
			try:
				request = gmPathLab.cLabRequest(req_id=reqid, lab=self.__lab_name)
			except gmExceptions.ConstructorError:
				_log.LogException('cannot get lab request', sys.exc_info(), verbose=0)
			# try to verify patient
			if request is not None:
				if pat_ldt is not None:
					pat_db = request.get_patient()
					if ((pat_ldt['lastnames'] != pat_db[3]) or
					    (pat_ldt['firstnames'] != pat_db[2]) or
					    (pat_ldt['dob'] != pat_db[4].strftime('%Y-%m-%d'))):
						_log.Log(gmLog.lErr, 'patient mismatch LDT-Datei <-> Datenbank')
						_log.Log(gmLog.lData, 'Datei: %s' % pat_ldt)
						_log.Log(gmLog.lData, 'DB: %s' % pat_db)
						return None

		# or create one from name/dob
		# FIXME: we may have to use field 3100, too
		if request is None:
			# check essential fields
			if pat_ldt is None:
				_log.Log(gmLog.lErr, 'Satz vom Typ [8000:%s] enthält nicht alle Felder [3101, 3102, 3103]' % request_data['8000'][0])
				_log.Log(gmLog.lErr, 'Kann lab_request nicht automatisch erzeugen.')
				return None
			# find patient
			searcher = gmPerson.cPatientSearcher_SQL()
			pat_ids = searcher.get_patient_ids(search_dict=pat_ldt)
			if len(pat_ids) == 0:
				_log.Log(gmLog.lErr, 'Kann in der Datenbank keinen Patienten für %s finden.' % str(pat_ldt))
				return None
			if len(pat_ids) > 1:
				_log.Log(gmLog.lErr, 'Mehrere Patienten für %s gefunden: %s' % (str(pat_ldt), str(pat_ids)))
				return None
			# create lab request
			try:
				pat = gmPerson.gmPerson(aPKey=pat_ids[0])
			except gmExceptions.ConstructorError:
				_log.LogException('patient error', sys.exc_info())
				return None
			emr = pat.get_emr()
			if request_data.has_key('8310'):
				reqid = request_data['8310'][0]
			elif request_data.has_key('8311'):
				reqid = request_data['8311'][0]
			else:
				reqid = str(random.randrange(sys.maxint))
			request = emr.add_lab_request(lab=self.__lab_name, req_id=reqid)
			pat.cleanup()
			if request is None:
				_log.Log(gmLog.lErr, 'cannot auto-create lab request with [%s:%s]' % (self.__lab_name, reqid))
				return None
		# eventually we got one
		return request
	#-----------------------------------------------------------
	def __handle_8201(self, request_data):
		self.__request = self.__get_request_from_8201(request_data)
		if self.__request is None:
			prob = 'Kann Labordaten keiner Anforderung zuordnen.'
			sol = 'Zuordnungen überprüfen. Systembetreuer verständigen. Details im Log.'
			ctxt = 'Labor [%s], LDT-Datei [%s]' % (self.__lab_name, self.ldt_filename)
			add_todo(problem=prob, solution=sol, context=ctxt)
			_log.Log(gmLog.lErr, 'cannot find lab request matching data derived from 8201 record')
			return False

		# update fields in request from request_data
		for line_type in request_data.keys():
			# get handler
			try:
				handle_line = cLDTImporter.__820xline_handler[line_type]
			except KeyError:
				_log.LogException('no handler for line [%s:%s] in [8000:8201] record' % (line_type, request_data[line_type]), sys.exc_info(), verbose=0)
				continue
			# ignore line
			if handle_line is None:
				try:
					name = gmXdtMappings.xdt_id_map[line_type]
				except KeyError:
					name = '?'
				_log.Log(gmLog.lData, 'skipping [%s] (%s)' % (line_type, name))
				continue
			# handle line
			line_data = handle_line(self, request_data)
			if line_data is False:
				# FIXME: todo item
				_log.Log(gmLog.lErr, 'failed to handle [%s] line' % line_type)
				return False
			try:
				self.__request[cLDTImporter._map_820xline2req_field[line_type]] = line_data
			except KeyError:
				pass
		self.__request.save_payload()
		return True
	#-----------------------------------------------------------
	#-----------------------------------------------------------
	__chunk8000_handler = {
		# skip file header chunk
		'8220': None,
		'8201': __handle_8201,
		'8202': __handle_8202
	}
	#-----------------------------------------------------------
	def __handle_8000(self, chunk):
		try:
			handler = cLDTImporter.__chunk8000_handler[chunk['8000'][0]]
		except KeyError:
			_log.Log(gmLog.lErr, 'kein Handler für Satztyp [8000:%s]' % chunk['8000'][0])
			return False
		if handler is None:
			return True
		if not handler(self, chunk):
			_log.Log(gmLog.lErr, 'kann Satz vom Typ [8000:%s] nicht importieren' % chunk['8000'][0])
			return False
		return True
	#-----------------------------------------------------------
	#-----------------------------------------------------------
	def __xform_8418(self, result_data):
		try:
			tmp = gmXdtMappings.xdt_Teststatus_map[result_data['8418'][0].strip()]
		except KeyError:
			tmp = _('unknown test status [%s]') % result_data['8418'][0].strip()
		if self.__lab_result['note_provider'] is None:
			self.__lab_result['note_provider'] = tmp
		else:
			self.__lab_result['note_provider'] = "%s\n* %s *" % (self.__lab_result['note_provider'], tmp)
		return True
	#-----------------------------------------------------------
	def __xform_8428(self, result_data):
		tmp = "[ID:%s]" % result_data['8428'][0].strip()
		if self.__lab_result['material_detail'] is None:
			self.__lab_result['material_detail'] = tmp
		else:
			self.__lab_result['material_detail'] = "%s %s" % (self.__lab_result['material_detail'], tmp)
		return True
	#-----------------------------------------------------------
	def __xform_8429(self, result_data):
		tmp = "[IDX:%s]" % result_data['8429'][0].strip()
		if self.__lab_result['material_detail'] is None:
			self.__lab_result['material_detail'] = tmp
		else:
			self.__lab_result['material_detail'] = "%s %s" % (self.__lab_result['material_detail'], tmp)
		return True
	#-----------------------------------------------------------
	def __xform_8430(self, result_data):
		self.__lab_result['material'] = result_data['8430'][0].strip()
		return True
	#-----------------------------------------------------------
	def __xform_8431(self, result_data):
		tmp = '\n'.join(result_data['8431'])
		if self.__lab_result['material_detail'] is None:
			self.__lab_result['material_detail'] = tmp
		else:
			self.__lab_result['material_detail'] = "%s\n%s" % (self.__lab_result['material_detail'], tmp)
		return True
	#-----------------------------------------------------------
	def __xform_8432(self, result_data):
		self.__request['sampled_when'] = mxDT.strptime(
			result_data['8432'][0],
			'%d%m%Y',
			self.__request['sampled_when']
			)
		self.__request.save_payload()
	#-----------------------------------------------------------
	def __xform_8433(self, result_data):
		self.__request['sampled_when'] = mxDT.strptime(
			result_data['8433'][0],
			'%H%M',
			self.__request['sampled_when']
			)
		self.__request.save_payload()
	#-----------------------------------------------------------
	def __xform_8420(self, result_data):
		tmp = result_data['8420'][0].strip()
		try:
			self.__lab_result['val_num'] = float(tmp)
		except ValueError:
			_log.Log(gmLog.lErr, 'angeblich numerisches Ergebnis [%s] ist nicht-numerisch, speichere als alphanumerisch' % str(result_data['8420']))
			if self.__lab_result['val_alpha'] is None:
				self.__lab_result['val_alpha'] = tmp
			else:
				self.__lab_result['val_alpha'] = "%s\n* %s *" % (self.__lab_result['val_alpha'], tmp)
		return True
	#-----------------------------------------------------------
	def __xform_8421(self, result_data):
		self.__lab_result['val_unit'] = result_data['8421'][0].strip()
		return True
	#-----------------------------------------------------------
	def __xform_8480(self, result_data):
		tmp = '\n'.join(result_data['8480'])
		if self.__lab_result['val_alpha'] is None:
			self.__lab_result['val_alpha'] = tmp
		else:
			self.__lab_result['val_alpha'] = "%s\n%s" % (tmp, self.__lab_result['val_alpha'])
		return True
	#-----------------------------------------------------------
	def __xform_8470(self, result_data):
		tmp = '\n'.join(result_data['8470'])
		if self.__lab_result['note_provider'] is None:
			self.__lab_result['note_provider'] = tmp
		else:
			self.__lab_result['note_provider'] = "%s\n%s" % (tmp, self.__lab_result['note_provider'])
		return True
	#-----------------------------------------------------------
	def __xform_8460(self, result_data):
		self.__lab_result['val_normal_range'] = '\n'.join(result_data['8460'])
		return True
	#-----------------------------------------------------------
	def __xform_8461(self, result_data):
		self.__lab_result['val_normal_min'] = result_data['8461'][0]
		return True
	#-----------------------------------------------------------
	def __xform_8462(self, result_data):
		self.__lab_result['val_normal_max'] = result_data['8462'][0]
		return True
	#-----------------------------------------------------------
	def __xform_8422(self, result_data):
		self.__lab_result['abnormal'] = result_data['8422'][0].strip()
		return True
	#-----------------------------------------------------------
	def __xform_8490(self, result_data):
		new_comment = '\n'.join(result_data['8490'])
		old_narrative = self.__request['progress_note']
		if old_narrative is None:
			self.__request['progress_note'] = new_comment
			self.__request.save_payload()
			return True
		if old_narrative.find(new_comment) == -1:
			self.__request['progress_note'] = old_narrative + '\n' + new_comment
			self.__request.save_payload()
		return True
	#-----------------------------------------------------------
	__8410line_handler = {
		'5001': None,
		'8404': None,
		'8406': None,				# Kosten Cent
		'8410': None,				# don't update code
		'8411': None,				# don't update name
		'8412': None,				# Abrechnungskennung
		'8418': __xform_8418,
		'8428': __xform_8428,
		'8429': __xform_8429,
		'8430': __xform_8430,
		'8431': __xform_8431,
		'8432': __xform_8432,
		'8433': __xform_8433,
		'8420': __xform_8420,
		'8421': __xform_8421,
		'8480': __xform_8480,
		'8470': __xform_8470,
		'8460': __xform_8460,
		'8461': __xform_8461,
		'8462': __xform_8462,
		'8422': __xform_8422,
		'8490': __xform_8490
	}
	#-----------------------------------------------------------
	def __handle_8410(self, result_data):
		if self.__request is None:
			_log.Log(gmLog.lErr, 'Kann Labordaten nicht ohne Zuordnung importieren.')
			return False
		# skip pseudo results
		if len(result_data) == 3:
			if (result_data.has_key('8410') and			# code
				result_data.has_key('8411') and			# name
				result_data.has_key('8412')):			# Abrechnungskennung
				_log.Log(gmLog.lInfo, 'skipping billing-only record')
				return True
		# verify essential fields
		# - numeric result
		try:
			vnum = '\n'.join(result_data['8420'])
		except KeyError:
			vnum = None
		# - alphanumeric result
		try:
			valpha = '\n'.join(result_data['8480'])
		except KeyError:
			valpha = None
		if (valpha is None) and (vnum is None):
			valpha = ''
		# - code
		try:
			vcode = result_data['8410'][0]
		except KeyError:
			_log.Log(gmLog.lWarn, 'adding default test type code')
		# - name
		try:
			vname = result_data['8411'][0]
		except KeyError:
			_log.Log(gmLog.lWarn, 'adding default test type name')
		# - unit
		try:
			vunit = result_data['8421'][0]
		except KeyError:
			vunit = ''
		# verify/create test type
		status, ttype = gmPathLab.create_test_type(
			lab=self.__lab_name,
			code=vcode,
			name=vname,
			unit=vunit
		)
		if status in [False, None]:
			_log.Log(gmLog.lErr, 'cannot create/retrieve test type')
			return False
		if ttype['comment'] in [None, '']:
			ttype['comment'] = 'created [%s] by [$RCSfile: gmLDTimporter.py,v $ $Revision: 1.28 $] from [%s]' % (time.strftime('%Y-%m-%d %H:%M'), self.ldt_filename)
			ttype.save_payload()
		# try to create test result row
		whenfield = 'lab_rxd_when'		# FIXME: make this configurable
		status, self.__lab_result = gmPathLab.create_lab_result(
			patient_id = self.__request.get_patient()[0],
			when_field = whenfield,
			when = self.__request[whenfield],
			test_type = ttype['pk'],
			val_num = vnum,
			val_alpha = valpha,
			unit = vunit,
			request = self.__request
		)
		if status is False:
			_log.Log(gmLog.lErr, 'cannot create result record')
			_log.Log(gmLog.lInfo, str(result_data)[:500])
			return False
		# FIXME: make this configurable (whether skipping or duplicating)
		if status is None:
			_log.Log(gmLog.lData, 'skipping duplicate lab result on import')
			_log.Log(gmLog.lData, 'in file: %s' % str(result_data))
			return True
		# update result record from dict
		# - force these to None so we can add in the proper values
		self.__lab_result['val_num'] = None
		self.__lab_result['val_alpha'] = None
		# - preset some fields
		self.__lab_result['reviewed'] = 'false'
		if self.__ref_group_str != '':
			self.__lab_result['ref_group'] = self.__ref_group_str
		# - process lines
		for line_type in result_data.keys():
			# get handler
			try:
				handle_line = cLDTImporter.__8410line_handler[line_type]
			except KeyError:
				_log.LogException('no handler for line [%s] in [8410] record' % line_type, sys.exc_info(), verbose=0)
				return False
			# ignore line
			if handle_line is None:
				continue
			if handle_line(self, result_data) is False:
				# FIXME: todo item
				_log.Log(gmLog.lErr, 'cannot handle [%s] line' % line_type)
				return False
		if (self.__lab_result['val_alpha'] is None) and (self.__lab_result['val_num'] is None):
			_log.Log(gmLog.lWarn, 'both result fields empty, setting alphanumeric default')
			self.__lab_result['val_alpha'] = ''
		saved, msg = self.__lab_result.save_payload()
		del self.__lab_result
		if not saved:
			_log.Log(gmLog.lErr, 'kann Laborwert (8410) nicht importieren')
			return False
		_log.Log(gmLog.lInfo, 'Laborwert (8410) erfolgreich importiert')
		return True
	#-----------------------------------------------------------
	#-----------------------------------------------------------
	__chunk_handler = {
		'8000': __handle_8000,
		'8410': __handle_8410
	}
	#-----------------------------------------------------------
	def __import_request_file(self, filename):
		random.jumpahead(int(time.strftime('%S%M%H')))
		self.__ref_group_str = ''
		self.__request = None
		chunk = {}
		for line in fileinput.input(filename):
			tmp = line.replace('\r','')
			tmp = tmp.replace('\n','')
			line_type = tmp[3:7]
			line_data = tmp[7:]
			if line_type in cLDTImporter._chunk_starters:
				# process any previous data
				if len(chunk) != 0:
					# get handler
					try:
						handle_chunk = cLDTImporter.__chunk_handler[chunk_type]
					except KeyError:
						fileinput.close()
						if self.__request is not None:
							self.__request['request_status'] = 'partial'
							self.__request['is_pending'] = 'true'
							self.__request.save_payload()
						_log.Log(gmLog.lErr, 'kein Handler für Satztyp [%s] verfügbar' % chunk_type)
						return False
					# handle chunk
					if not handle_chunk(self, chunk):
						if self.__request is not None:
							self.__request['request_status'] = 'partial'
							self.__request['is_pending'] = 'true'
							self.__request.save_payload()
						fileinput.close()
						_log.Log(gmLog.lErr, 'cannot handle [%s] chunk' % chunk_type)
						return False
				# start new chunk
				chunk = {}
				chunk_type = line_type
			# FIXME: max line count
			if not chunk.has_key(line_type):
				chunk[line_type] = []
			chunk[line_type].append(line_data)
		fileinput.close()
		return True
#===============================================================
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
	# make sure files can moved to the target repository
	target_dir = _cfg.get('target', 'repository')
	if target_dir is None:
		return False
	target_dir = os.path.abspath(os.path.expanduser(target_dir))
	if not (os.access(target_dir, os.W_OK) and os.path.isdir(target_dir)):
		_log.Log(gmLog.lErr, 'cannot write to target repository [%s]\n' % target_dir)
		return False
	# get import files
	import_dir = _cfg.get('import', 'repository')
	if import_dir is None:
		_log.Log(gmLog.lErr, 'no import dir found\n')
		return False
	import_dir = os.path.abspath(os.path.expanduser(import_dir))
	filename_pattern = _cfg.get('import', 'file pattern')
	if filename_pattern is None:
		_log.Log(gmLog.lErr, 'no import file name pattern found\n')
		return False
	import_file_pattern = os.path.join(import_dir, filename_pattern)
	files2import = glob.glob(import_file_pattern)
	# now import
	importer = cLDTImporter(cfg=_cfg)
	for ldt_file in files2import:
		_log.Log(gmLog.lInfo, 'importing LDT file [%s]' % ldt_file)
		if not importer.import_file(ldt_file):
			_log.Log(gmLog.lErr, 'cannot import LDT file\n')
		else:
			_log.Log(gmLog.lInfo, 'success importing LDT file\n')
			try:
				shutil.copy(ldt_file, target_dir)
				os.remove(ldt_file)
			except:
				_log.LogException('cannot move [%s] to [%s]\n' % (ldt_file, target_dir))
	return True
#---------------------------------------------------------------
def add_todo(problem, solution, context):
	cat = 'lab'
	by = '$RCSfile: gmLDTimporter.py,v $ $Revision: 1.28 $'
	rcvr = 'user'
	gmPG.add_housekeeping_todo(reporter=by, receiver=rcvr, problem=problem, solution=solution, context=context, category=cat)
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
	try:
		import profile
		profile.run('run_import()', './profile.log')
	except:
		_log.LogException('unhandled exception caught', sys.exc_info(), verbose=1)
		backend.StopListeners()
		sys.exit('aborting')
	backend.StopListeners()
	sys.exit(0)

#===============================================================
# $Log: gmLDTimporter.py,v $
# Revision 1.28  2006-10-25 07:46:44  ncq
# - Format() -> strftime() since datetime.datetime does not have .Format()
#
# Revision 1.27  2006/10/25 07:18:12  ncq
# - no more gmPG
#
# Revision 1.26  2006/07/19 20:25:48  ncq
# - gmPyCompat.py is history
#
# Revision 1.25  2006/05/06 18:53:56  ncq
# - select age(...) <> ...; -> select ... <> now() - ...; as per Syan
#
# Revision 1.24  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.23  2006/01/09 10:45:38  ncq
# - keep up to snuff re schema qualification
#
# Revision 1.22  2005/04/30 13:30:38  sjtan
#
# v_pat_items.id_patient -> v_pat_items.pk_patient
#
# Revision 1.21  2005/03/23 18:48:10  ncq
# - v_patient_items -> v_pat_items
#
# Revision 1.20  2005/02/15 18:31:35  ncq
# - identity.id -> identity.pk
#
# Revision 1.19  2005/01/31 09:53:25  ncq
# - gmPatient -> gmPerson
#
# Revision 1.18  2004/10/01 11:48:53  ncq
# - id -> pk
#
# Revision 1.17  2004/09/25 13:09:58  ncq
# - fix logged string
#
# Revision 1.16  2004/07/05 22:28:40  ncq
# - lab_request -> v_lab_request, therefore:
#   - clin_when -> sampled_when
#   - narrative -> progress_note
# - v_pat_items.id_item -> pk_item
#
# Revision 1.15  2004/06/25 12:27:58  ncq
# - correctly cross-check db<->ldt patient
# - 8461/8462
#
# Revision 1.14  2004/06/20 17:26:13  ncq
# - don't overwrite previous narrative but don't create duplicates either
# - correctly handle val_num/val_alpha both being NULL
#
# Revision 1.13  2004/06/18 13:39:00  ncq
# - semantically seems to import everything correctly
# - now handles input files on failure/success correctly,
#   eg moves to target repository
# - change of concept: don't assemble parts that have been
#   imported into new files, rather all or nothing: either
#   file imported successfully or file stays in queue, this
#   is safe as we now safely detect duplicates (which would,
#   in the worst case, duplicate data for what it's worth)
# - adjust logging to saner levels
#
# Revision 1.12  2004/06/13 22:09:12  ncq
# - don't verify LDT version, try to import regardless
# - 8303/8302/8403/8407/8609
#
# Revision 1.11  2004/05/25 00:22:26  ncq
# - imports nearly everything thrown at it now
#
# Revision 1.10  2004/05/17 23:53:10  ncq
# - while commiting I screwed up, praise be to MC's extf2s
#   undelete function for rescuing things from the ashes
# - the comment for 1.9 got lost in the process, so here it is again:
# - rewrite for generic chunk handling and map based line processing
#
# Revision 1.8  2004/05/14 13:20:13  ncq
# - cleanup
# - reverse expanduser(abspath()) use
# - skip empty LDT files
# - collect target snippet files
# - handle 8470
#
# Revision 1.7  2004/05/11 01:32:04  ncq
# - eventually actually imports test types and results
# - doesn't handle left over data though
#
# Revision 1.6  2004/05/08 22:15:10  ncq
# - almost there, all the code is there but it needs fixing and fine-tuning
#
# Revision 1.5  2004/04/26 21:58:22  ncq
# - now auto-creates test types during import
# - works around non-numerical val_num lines
# - uses gmPG.add_housekeeping_todo()
#
# Revision 1.4  2004/04/21 15:33:05  ncq
# - start on __import_result()
# - parse result lines in __import_request_results
#
# Revision 1.3  2004/04/20 00:16:27  ncq
# - try harder to become useful
#
# Revision 1.2  2004/04/16 00:34:53  ncq
# - now tries to import requests
#
# Revision 1.1  2004/04/13 14:24:07  ncq
# - first version here
#
