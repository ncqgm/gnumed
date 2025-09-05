# -*- coding: utf-8 -*-

"""GNUmed DICOM handling middleware"""
#============================================================
__license__ = "GPL v2 or later"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


# stdlib
import os
import sys
import re as regex
import logging
import http.client		# exception names used by httplib2
import socket
import httplib2
import json
import shutil
import time
import datetime as pydt
from urllib.parse import urlencode


_log = logging.getLogger('gm.dicom')


# 3rd party
try:
	from packaging import version as py_version
except (ImportError, ModuleNotFoundError):
	_log.error('please install the <packaging> python module which used to be in the stdlib')
	py_version = None


# GNUmed modules
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmDateTime


_map_gender_gm2dcm = {
	'm': 'M',
	'f': 'F',
	'tm': 'M',
	'tf': 'F',
	'h': 'O'
}

#============================================================
class cOrthancServer:
	"""Interface for the REST API of an Orthanc DICOM server.
	"""
	# REST API access to Orthanc DICOM servers

	def __init__(self):
		self.__server_identification = None
		self.__user = None
		self.__password = None
		self.__conn = None
		self.__server_url = None
		self.using_ssl = None

	#--------------------------------------------------------
	def __get_server_url(self):
		return self.__server_url

	server_url = property(__get_server_url)

	#--------------------------------------------------------
	def __setup_cache_dir(self):
		cache_dir = os.path.join(gmTools.gmPaths().user_tmp_dir, '.orthanc2gm-cache')
		gmTools.mkdir(cache_dir, 0o700)
		gmTools.create_directory_description_file(directory = cache_dir, readme = 'this directory caches Orthanc REST data, mainly DICOM files')
		_log.debug('using cache directory: %s', cache_dir)
		return cache_dir

	#--------------------------------------------------------
	def __try_httpS(self, host, port):
		try:
			import ssl
			_log.debug('ssl: %s', ssl.OPENSSL_VERSION)
		except ModuleNotFoundError:
			_log.exception('no SSL support compiled into this Python')
			return False

		try:
			self.__server_url = str('https://%s:%s' % (host, port))
		except Exception:
			_log.exception('cannot create server url from: host [%s] and port [%s]', host, port)
			self.__server_url = None
			return False

		_log.info('trying connection as [%s] to Orthanc server at [%s]', self.__user, self.__server_url)
		ident = self.server_identification
		if not ident:
			_log.error('HTTPS failure ?')
			self.__server_url = None
			return False

		_log.debug('connected to server: %s', ident)
		return True

	#--------------------------------------------------------
	def __try_http(self, host, port):
		try:
			self.__server_url = str('http://%s:%s' % (host, port))
		except Exception:
			_log.exception('cannot create server url from: host [%s] and port [%s]', host, port)
			self.__server_url = None
			return False

		_log.info('trying connection as [%s] to Orthanc server at [%s]', self.__user, self.__server_url)
		ident = self.server_identification
		if not ident:
			_log.error('HTTP connect failure ?')
			self.__server_url = None
			return False

		_log.debug('connected to server: %s', ident)
		return True

	#--------------------------------------------------------
	def connect(self, host, port, user, password, expected_minimal_version=None, expected_name=None, expected_aet=None) -> bool:
		try:
			int(port)
		except Exception:
			_log.error('invalid port [%s]', port)
			return False

		if (host is None) or (host.strip() == ''):
			host = 'localhost'
		cache_dir = self.__setup_cache_dir()
		self.__user = user
		self.__password = password
		self.__conn = httplib2.Http(cache = cache_dir)
		self.__conn.add_credentials(self.__user, self.__password)
		self.__server_url = None
		self.using_ssl = self.__try_httpS(host, port)
		if not self.using_ssl:
			if not self.__try_http(host, port):
				_log.error('unable to connect')
				self.connect_error = 'retrieving server identification failed'
				return False

		if (expected_minimal_version is not None) and (py_version is not None):
			if py_version.parse(self.server_identification['Version']) < py_version.parse(expected_minimal_version):
				_log.error('server too old, needed [%s]', expected_minimal_version)
				self.connect_error = 'server too old, needed version [%s]' % expected_minimal_version
				return False

		if expected_name is not None:
			if self.server_identification['Name'] != expected_name:
				_log.error('wrong server name, expected [%s]', expected_name)
				self.connect_error = 'wrong server name, expected [%s]' % expected_name
				return False

		if expected_aet is not None:
			if self.server_identification['DicomAet'] != expected_name:
				_log.error('wrong server AET, expected [%s]', expected_aet)
				self.connect_error = 'wrong server AET, expected [%s]' % expected_aet
				return False

		self.connect_error = ''
		return True

	#--------------------------------------------------------
	def _get_server_identification(self):
		if self.__server_identification:
			return self.__server_identification

		system_data = self.__run_GET(url = '%s/system' % self.__server_url)
		if system_data is False:
			_log.error('unable to get server identification')
			return False

		_log.debug('server: %s', system_data)
		self.__server_identification = system_data
		self.__initial_orthanc_encoding = self.__run_GET(url = '%s/tools/default-encoding' % self.__server_url)
		_log.debug('initial Orthanc encoding: %s', self.__initial_orthanc_encoding)
		# check time skew
		tolerance = 60 # seconds
		client_now_as_utc = pydt.datetime.utcnow()
		start = time.time()
		orthanc_now_str = self.__run_GET(url = '%s/tools/now' % self.__server_url)		# 20180208T165832
		end = time.time()
		query_duration = end - start
		orthanc_now_unknown_tz = pydt.datetime.strptime(orthanc_now_str, '%Y%m%dT%H%M%S')
		_log.debug('GNUmed "now" (UTC): %s', client_now_as_utc)
		_log.debug('Orthanc "now" (UTC): %s', orthanc_now_unknown_tz)
		_log.debug('wire roundtrip (seconds): %s', query_duration)
		_log.debug('maximum skew tolerance (seconds): %s', tolerance)
		if query_duration > tolerance:
			_log.info('useless to check GNUmed/Orthanc time skew, wire roundtrip (%s) > tolerance (%s)', query_duration, tolerance)
		else:
			if orthanc_now_unknown_tz > client_now_as_utc:
				real_skew = orthanc_now_unknown_tz - client_now_as_utc
			else:
				real_skew = client_now_as_utc - orthanc_now_unknown_tz
			_log.info('GNUmed/Orthanc time skew: %s', real_skew)
			if real_skew > pydt.timedelta(seconds = tolerance):
				_log.error('GNUmed/Orthanc time skew > tolerance (may be due to timezone differences on Orthanc < v1.3.2)')
		return self.__server_identification

	server_identification = property(_get_server_identification)

	#--------------------------------------------------------
	def _get_as_external_id_issuer(self):
		# fixed type :: user level instance name :: DICOM AET
		return 'Orthanc::%(Name)s::%(DicomAet)s' % self.__server_identification

	as_external_id_issuer = property(_get_as_external_id_issuer)

	#--------------------------------------------------------
	def _get_url_browse_patients(self):
		if self.__user is None:
			return self.__server_url
		return self.__server_url.replace('http://', 'http://%s@' % self.__user)

	url_browse_patients = property(_get_url_browse_patients)

	#--------------------------------------------------------
	def get_url_browse_patient(self, patient_id):
		# http://localhost:8042/#patient?uuid=0da01e38-cf792452-65c1e6af-b77faf5a-b637a05b
		return '%s/#patient?uuid=%s' % (self.url_browse_patients, patient_id)

	#--------------------------------------------------------
	def get_url_browse_study(self, study_id):
		# http://localhost:8042/#study?uuid=0da01e38-cf792452-65c1e6af-b77faf5a-b637a05b
		return '%s/#study?uuid=%s' % (self.url_browse_patients, study_id)

	#--------------------------------------------------------
	# download API
	#--------------------------------------------------------
	def get_matching_patients(self, person) -> list[str]:
		"""Fetch matching patients from an Orthanc DICOM server.

		Matches are searched for via stored "external ID" and
		via generically generated ID. The external IDs are
		fetched from the patient store, must be of type
		"PACS" and must be marked as issued by the PACS
		represented by this instance (self).

		Args:
			person: a gmPerson.cPerson instance

		Returns:
			A list of Orthanc patient UIDs.
		"""
		_log.info('searching for Orthanc patients matching %s', person)
		pacs_ids = person.get_external_ids(id_type = 'PACS', issuer = self.as_external_id_issuer)
		if len(pacs_ids) > 1:
			_log.error('GNUmed patient has more than one ID for this PACS: %s', pacs_ids)
			_log.error('the stored-in-GNUmed PACS ID is expected to be unique _per PACS_')
			return []

		pacs_ids2search_by = []
		pacs_ids2search_by.extend([ pacs_id['value'] for pacs_id in pacs_ids ])
		pacs_ids2search_by.extend(person.suggest_external_ids(target = 'PACS'))
		matching_pats = []
		for pacs_id in pacs_ids2search_by:
			_log.debug('using PACS ID [%s]', pacs_id)
			pats = self.get_patients_by_external_id(external_id = pacs_id, fuzzy = False)
			if len(pats) > 1:
				_log.warning('more than one Orthanc patient matches PACS ID: %s', pacs_id)
			matching_pats.extend(pats)
		if not matching_pats:
			_log.debug('no matching patient found in PACS')
		return matching_pats

	#--------------------------------------------------------
	def get_patients_by_external_id(self, external_id=None, fuzzy=False):
		"""Search for instances by patient ID."""
		_log.info('external ID >>>%s<<< fuzzy [%s]', external_id, fuzzy)
		search_term = external_id.strip().strip('*').strip()
		if fuzzy:
			search_term = '*%s*' % search_term
		search_data = {
			'Level': 'Patient',
			'CaseSensitive': False,
			'Expand': True,
			'Query': {'PatientID': search_term}
		}
		matches = self.__run_POST(url = '%s/tools/find' % self.__server_url, data = search_data)
		# paranoia
		for match in matches:
			self.protect_patient(orthanc_id = match['ID'])
		return matches

	#--------------------------------------------------------
	def get_patients_by_name(self, name_parts=None, gender=None, dob=None, fuzzy:bool=False) -> list:
		"""Search for patients by name.

		Returns:
			List of patients matching the search term(s).
		"""
		_log.info('name parts %s, gender [%s], dob [%s], fuzzy: [%s]', name_parts, gender, dob, fuzzy)
		if len(name_parts) > 1:
			return self.get_patients_by_name_parts(name_parts = name_parts, gender = gender, dob = dob, fuzzy = fuzzy)

		search_term = name_parts[0].strip().strip('*').strip()
		if search_term == '':
			_log.debug('search term empty')
			return []

		if fuzzy:
			search_term = '*%s*' % search_term
		search_data:dict = {
			'Level': 'Patient',
			'CaseSensitive': False,
			'Expand': True
		}
		search_data['Query'] = {'PatientName': search_term}
		if gender:
			gender = _map_gender_gm2dcm[gender.casefold()]
			if gender:
				search_data['Query']['PatientSex'] = gender
		if dob:
			search_data['Query']['PatientBirthDate'] = dob.strftime('%Y%m%d')
		_log.info('server-side C-FIND SCU over REST search, mogrified search data: %s', search_data)
		matches = self.__run_POST(url = '%s/tools/find' % self.__server_url, data = search_data)
		return matches

	#--------------------------------------------------------
	def get_patients_by_name_parts(self, name_parts:list[str]=None, gender=None, dob=None, fuzzy=False):
		# fuzzy: allow partial/substring matches (but not across name part boundaries ',' or '^')
		matching_patients = []
		clean_parts = []
		for part in name_parts:
			if part.strip() == '':
				continue
			clean_parts.append(part.casefold().strip())
		_log.info('client-side patient search, scrubbed search terms: %s', clean_parts)
		pat_ids = self.__run_GET(url = '%s/patients' % self.__server_url)
		if pat_ids is False:
			_log.error('cannot retrieve patients')
			return []

		for pat_id in pat_ids:
			orthanc_pat = self.__run_GET(url = '%s/patients/%s' % (self.__server_url, pat_id))
			if orthanc_pat is False:
				_log.error('cannot retrieve patient')
				continue
			orthanc_name = orthanc_pat['MainDicomTags']['PatientName'].casefold().strip()
			if not fuzzy:
				orthanc_name = orthanc_name.replace(' ', ',').replace('^', ',').split(',')
			parts_in_orthanc_name = 0
			for part in clean_parts:
				if part in orthanc_name:
					parts_in_orthanc_name += 1
			if parts_in_orthanc_name == len(clean_parts):
				_log.debug('name match: "%s" contains all of %s', orthanc_name, clean_parts)
				if gender is not None:
					gender = _map_gender_gm2dcm[gender.casefold()]
					if gender is not None:
						if orthanc_pat['MainDicomTags']['PatientSex'].casefold() != gender:
							_log.debug('gender mismatch: dicom=[%s] gnumed=[%s], skipping', orthanc_pat['MainDicomTags']['PatientSex'], gender)
							continue
				if dob is not None:
					if orthanc_pat['MainDicomTags']['PatientBirthDate'] != dob.strftime('%Y%m%d'):
						_log.debug('dob mismatch: dicom=[%s] gnumed=[%s], skipping', orthanc_pat['MainDicomTags']['PatientBirthDate'], dob)
						continue
				matching_patients.append(orthanc_pat)
			else:
				_log.debug('name mismatch: "%s" does not contain all of %s', orthanc_name, clean_parts)
		return matching_patients

	#--------------------------------------------------------
	def search_studies_by_patient_name(self, name:str) -> list:
		"""Search for studies with the given patient name snippet.

		A study (even at the Orthanc DB metadata level) will
		contain the original patient name (unless manually
		modified) in contrast to the (artificial Orthanc DB
		metadata level) patient record. The latter contains
		the first patient name that had been associated with
		the given patient ID.

		Args:
			name: name snippet to search for

		Returns:
			The list of matching *studies* (not *patient*).
		"""
		_log.debug('search term [%s]', name)
		search_term = name.strip().strip('*').strip()
		if search_term == '':
			_log.warning('search term empty')
			return []

		search_term = '*%s*' % search_term
		search_data = {
			'Level': 'Study',
			'CaseSensitive': False,
			'Expand': True,
			'Query': {'PatientName': search_term}
		}
		matches = self.__run_POST(url = '%s/tools/find' % self.__server_url, data = search_data)
		return matches

	#--------------------------------------------------------
	def search_studies_by_patient_id(self, patient_id:str) -> list:
		"""Search for studies with the given patient ID snippet.

		This relates to the external world patient ID as
		stored in DICOM instances, not the Orthanc DB
		metadata level patient UID.

		Args:
			patient_id: patient ID snippet to search for

		Returns:
			The list of matching *studies* (not *patient*).
		"""
		_log.debug('search term >>>%s<<<', patient_id)
		search_term = patient_id.strip().strip('*').strip()
		search_term = '*%s*' % search_term
		search_data = {
			'Level': 'Study',
			'CaseSensitive': False,
			'Expand': True,
			'Query': {'PatientID': search_term}
		}
		matches = self.__run_POST(url = '%s/tools/find' % self.__server_url, data = search_data)
		return matches

	#--------------------------------------------------------
	def get_studies_list_by_patient_name(self, name_parts=None, gender=None, dob=None, fuzzy=False):
		return self.get_studies_list_by_orthanc_patient_list (
			orthanc_patients = self.get_patients_by_name(name_parts = name_parts, gender = gender, dob = dob, fuzzy = fuzzy)
		)

	#--------------------------------------------------------
	def get_studies_list_by_external_id(self, external_id=None):
		return self.get_studies_list_by_orthanc_patient_list (
			orthanc_patients = self.get_patients_by_external_id(external_id = external_id)
		)

	#--------------------------------------------------------
	def get_study_as_zip(self, study_id=None, filename=None):
		if filename is None:
			filename = gmTools.get_unique_filename(prefix = r'DCM-', suffix = r'.zip')
		_log.info('exporting study [%s] into [%s]', study_id, filename)
		f = open(filename, 'wb')
		f.write(self.__run_GET(url = '%s/studies/%s/archive' % (self.__server_url, str(study_id)), allow_cached = True))
		f.close()
		return filename

	#--------------------------------------------------------
	def get_study_as_zip_with_dicomdir(self, study_id=None, filename=None):
		if filename is None:
			filename = gmTools.get_unique_filename(prefix = r'DCM-', suffix = r'.zip')
		_log.info('exporting study [%s] into [%s]', study_id, filename)
		f = open(filename, 'wb')
		f.write(self.__run_GET(url = '%s/studies/%s/media' % (self.__server_url, str(study_id)), allow_cached = True))
		f.close()
		return filename

	#--------------------------------------------------------
	def get_studies_as_zip(self, study_ids=None, patient_id=None, filename=None):
		if filename is None:
			filename = gmTools.get_unique_filename(prefix = r'DCM-', suffix = r'.zip')
		if study_ids is None:
			_log.info('exporting all studies of patient [%s] into [%s]', patient_id, filename)
			f = open(filename, 'wb')
			f.write(self.__run_GET(url = '%s/patients/%s/archive' % (self.__server_url, str(patient_id)), allow_cached = True))
			f.close()
			return filename

	#--------------------------------------------------------
	def _manual_get_studies_with_dicomdir(self, study_ids=None, patient_id=None, target_dir=None, filename=None, create_zip=False):

		if filename is None:
			filename = gmTools.get_unique_filename(prefix = r'DCM-', suffix = r'.zip', tmp_dir = target_dir)

		# all studies
		if study_ids is None:
			_log.info('exporting all studies of patient [%s] into [%s]', patient_id, filename)
			f = open(filename, 'wb')
			url = '%s/patients/%s/media' % (self.__server_url, str(patient_id))
			_log.debug(url)
			f.write(self.__run_GET(url = url, allow_cached = True))
			f.close()
			if create_zip:
				return filename
			if target_dir is None:
				target_dir = gmTools.mk_sandbox_dir(prefix = 'dcm-')
			if not gmTools.unzip_archive(filename, target_dir = target_dir, remove_archive = True):
				return False
			return target_dir

		# a selection of studies
		dicomdir_cmd = 'gm-create_dicomdir'		# args: 1) name of DICOMDIR to create 2) base directory where to start recursing for DICOM files
		found, external_cmd = gmShellAPI.detect_external_binary(dicomdir_cmd)
		if not found:
			_log.error('[%s] not found', dicomdir_cmd)
			return False

		if create_zip:
			sandbox_dir = gmTools.mk_sandbox_dir(prefix = 'dcm-')
			_log.info('exporting studies [%s] into [%s] (sandbox [%s])', study_ids, filename, sandbox_dir)
		else:
			sandbox_dir = target_dir
			_log.info('exporting studies [%s] into [%s]', study_ids, sandbox_dir)
		_log.debug('sandbox dir: %s', sandbox_dir)
		idx = 0
		for study_id in study_ids:
			study_zip_name = gmTools.get_unique_filename(prefix = 'dcm-', suffix = '.zip')
			# getting with DICOMDIR returns DICOMDIR compatible subdirs and filenames
			study_zip_name = self.get_study_as_zip_with_dicomdir(study_id = study_id, filename = study_zip_name)
			# non-beautiful per-study dir name required by subsequent DICOMDIR generation
			idx += 1
			study_unzip_dir = os.path.join(sandbox_dir, 'STUDY%s' % idx)
			_log.debug('study [%s] -> %s -> %s', study_id, study_zip_name, study_unzip_dir)
			# need to extract into per-study subdir because get-with-dicomdir
			# returns identical-across-studies subdirs / filenames
			if not gmTools.unzip_archive(study_zip_name, target_dir = study_unzip_dir, remove_archive = True):
				return False

		# create DICOMDIR across all studies,
		# we simply ignore the already existing per-study DICOMDIR files
		target_dicomdir_name = os.path.join(sandbox_dir, 'DICOMDIR')
		gmTools.remove_file(target_dicomdir_name, log_error = False)	# better safe than sorry
		_log.debug('generating [%s]', target_dicomdir_name)
		cmd = '%(exe)s %(DICOMDIR)s %(startdir)s' % {
			'exe': external_cmd,
			'DICOMDIR': target_dicomdir_name,
			'startdir': sandbox_dir
		}
		success = gmShellAPI.run_command_in_shell (
			command = cmd,
			blocking = True
		)
		if not success:
			_log.error('problem running [gm-create_dicomdir]')
			return False
		# paranoia
		try:
			open(target_dicomdir_name)
		except Exception:
			_log.error('[%s] not generated, aborting', target_dicomdir_name)
			return False

		# return path to extracted studies
		if not create_zip:
			return sandbox_dir

		# else return ZIP of all studies
		studies_zip = shutil.make_archive (
			gmTools.fname_stem_with_path(filename),
			'zip',
			root_dir = gmTools.parent_dir(sandbox_dir),
			base_dir = gmTools.dirname_stem(sandbox_dir),
			logger = _log
		)
		_log.debug('archived all studies with one DICOMDIR into: %s', studies_zip)
		# studies can be _large_ so attempt to get rid of intermediate files
		gmTools.rmdir(sandbox_dir)
		return studies_zip

	#--------------------------------------------------------
	def get_studies_with_dicomdir(self, study_ids=None, patient_id=None, target_dir=None, filename=None, create_zip=False):

		if filename is None:
			filename = gmTools.get_unique_filename(prefix = r'DCM-', suffix = r'.zip', tmp_dir = target_dir)

		# all studies
		if study_ids is None:
			if patient_id is None:
				raise ValueError('<patient_id> must be defined if <study_ids> is None')
			_log.info('exporting all studies of patient [%s] into [%s]', patient_id, filename)
			f = open(filename, 'wb')
			url = '%s/patients/%s/media' % (self.__server_url, str(patient_id))
			_log.debug(url)
			f.write(self.__run_GET(url = url, allow_cached = True))
			f.close()
			if create_zip:
				return filename
			if target_dir is None:
				target_dir = gmTools.mk_sandbox_dir(prefix = 'dcm-')
			if not gmTools.unzip_archive(filename, target_dir = target_dir, remove_archive = True):
				return False
			return target_dir

		# selection of studies
		_log.info('exporting %s studies into [%s]', len(study_ids), filename)
		_log.debug('studies: %s', study_ids)
		f = open(filename, 'wb')
		#  You have to make a POST request against URI "/tools/create-media", with a
		#  JSON body that contains the array of the resources of interest (as Orthanc
		#  identifiers). Here is a sample command-line:
		#  curl -X POST http://localhost:8042/tools/create-media -d '["8c4663df-c3e66066-9e20a8fc-dd14d1e5-251d3d84","2cd4848d-02f0005f-812ffef6-a210bbcf-3f01a00a","6eeded74-75005003-c3ae9738-d4a06a4f-6beedeb8","8a622020-c058291c-7693b63f-bc67aa2e-0a02e69c"]' -v > /tmp/a.zip
		#  (this will not create duplicates but will also not check for single-patient-ness)
		url = '%s/tools/create-media-extended' % self.__server_url
		_log.debug(url)
		try:
			downloaded = self.__run_POST(url = url, data = study_ids, output_file = f)
			if not downloaded:
				_log.error('this Orthanc version probably does not support "create-media-extended"')
		except TypeError:
			f.close()
			_log.exception('cannot retrieve multiple studies as one archive with DICOMDIR, probably not supported by this Orthanc version')
			return False
		# retry with old URL
		if not downloaded:
			url = '%s/tools/create-media' % self.__server_url
			_log.debug('retrying: %s', url)
			try:
				downloaded = self.__run_POST(url = url, data = study_ids, output_file = f)
				if not downloaded:
					return False
			except TypeError:
				_log.exception('cannot retrieve multiple studies as one archive with DICOMDIR, probably not supported by this Orthanc version')
				return False
			finally:
				f.close()
		if create_zip:
			return filename
		if target_dir is None:
			target_dir = gmTools.mk_sandbox_dir(prefix = 'dcm-')
			_log.debug('exporting studies into [%s]', target_dir)
		if not gmTools.unzip_archive(filename, target_dir = target_dir, remove_archive = True):
			return False
		return target_dir

	#--------------------------------------------------------
	def get_instance_dicom_tags(self, instance_id, simplified=True):
		_log.debug('retrieving DICOM tags for instance [%s]', instance_id)
		if simplified:
			download_url = '%s/instances/%s/simplified-tags' % (self.__server_url, instance_id)
		else:
			download_url = '%s/instances/%s/tags' % (self.__server_url, instance_id)
		return self.__run_GET(url = download_url, allow_cached = True)

	#--------------------------------------------------------
	def get_instance_preview(self, instance_id, filename=None):
		if filename is None:
			filename = gmTools.get_unique_filename(suffix = '.png')
		_log.debug('exporting preview for instance [%s] into [%s]', instance_id, filename)
		download_url = '%s/instances/%s/preview' % (self.__server_url, instance_id)
		f = open(filename, 'wb')
		try:
			f.write(self.__run_GET(url = download_url, allow_cached = True))
		except Exception:
			_log.exception('cannot retrieve instance')
			filename = None
		finally:
			f.close()
		return filename

	#--------------------------------------------------------
	def get_instance(self, instance_id:str, filename:str=None, allow_cached:bool=True) -> str:
		if filename is None:
			filename = gmTools.get_unique_filename(suffix = '.dcm')

		_log.debug('exporting instance [%s] into [%s]', instance_id, filename)
		download_url = '%s/instances/%s/attachments/dicom/data' % (self.__server_url, instance_id)
		f = open(filename, 'wb')
		f.write(self.__run_GET(url = download_url, allow_cached = allow_cached))
		f.close()
		return filename

	#--------------------------------------------------------
	# server-side API
	#--------------------------------------------------------
	def get_patient(self, orthanc_id:str):
		patient_data_url = '%s/patients/%s' % (self.__server_url, str(orthanc_id))
		patient_data, status = self.__run_GET(patient_data_url, also_return_status = True)
		if patient_data is False:
			if status == 404:
				_log.debug('no such patient: %s', orthanc_id)
				return {}

			_log.error('cannot retrieve patient data for [%s]', orthanc_id)
			return False

		return patient_data

	#--------------------------------------------------------
	def protect_patient(self, orthanc_id:str):
		url = '%s/patients/%s/protected' % (self.__server_url, str(orthanc_id))
		if self.__run_GET(url) == 1:
			_log.debug('patient already protected: %s', orthanc_id)
			return True
		_log.warning('patient [%s] not protected against recycling, enabling protection now', orthanc_id)
		self.__run_PUT(url = url, data = '1')
		if self.__run_GET(url) == 1:
			return True
		_log.error('cannot protect patient [%s] against recycling', orthanc_id)
		return False

	#--------------------------------------------------------
	def unprotect_patient(self, orthanc_id):
		url = '%s/patients/%s/protected' % (self.__server_url, str(orthanc_id))
		if self.__run_GET(url) == 0:
			return True
		_log.info('patient [%s] protected against recycling, disabling protection now', orthanc_id)
		self.__run_PUT(url = url, data = '0')
		if self.__run_GET(url) == 0:
			return True
		_log.error('cannot unprotect patient [%s] against recycling', orthanc_id)
		return False

	#--------------------------------------------------------
	def patient_is_protected(self, orthanc_id):
		url = '%s/patients/%s/protected' % (self.__server_url, str(orthanc_id))
		return (self.__run_GET(url) == 1)

	#--------------------------------------------------------
	def verify_patient_data(self, orthanc_id):
		_log.info('verifying DICOM data of patient [%s]', orthanc_id)
		bad_data = []
		instances_url = '%s/patients/%s/instances' % (self.__server_url, orthanc_id)
		instances = self.__run_GET(instances_url)
		for instance in instances:
			instance_id = instance['ID']
			attachments_url = '%s/instances/%s/attachments' % (self.__server_url, instance_id)
			attachments = self.__run_GET(attachments_url, allow_cached = True)
			for attachment in attachments:
				verify_url = '%s/%s/verify-md5' % (attachments_url, attachment)
				# False, success = "{}"
				#2018-02-08 19:11:27  ERROR     gm.dicom      [-1211701504 MainThread]  (gmDICOM.py::__run_POST() #986): cannot POST: http://localhost:8042/instances/5a8206f4-24619e76-6650d9cd-792cdf25-039e96e6/attachments/dicom-as-json/verify-md5
				#2018-02-08 19:11:27  ERROR     gm.dicom      [-1211701504 MainThread]  (gmDICOM.py::__run_POST() #987): response: {'status': '400', 'content-length': '0'}
				if self.__run_POST(verify_url) is not False:
					continue
				_log.error('bad MD5 of DICOM file at url [%s]: patient=%s, attachment_type=%s', verify_url, orthanc_id, attachment)
				bad_data.append({'patient': orthanc_id, 'instance': instance_id, 'type': attachment, 'orthanc': '%s [%s]' % (self.server_identification, self.__server_url)})

		return bad_data

	#--------------------------------------------------------
	def modify_patient_id(self, old_patient_id, new_patient_id):
		"""Modify the patient ID stored in Orthanc.

		This changes all DICOM files of the patient,
		identified via (DICOM level) old_patient_id, to
		contain the new_patient_id. It will update the
		associated Orthanc metadata DB entries accordingly.
		"""
		if old_patient_id == new_patient_id:
			return True

		modify_data = {
			'Replace': {
				'PatientID': new_patient_id
				#,u'0010,0021': praxis.name / "GNUmed vX.X.X"
				#,u'0010,1002': series of (old) patient IDs
			}
			, 'Force': True
			# "Keep" doesn't seem to do what it suggests ATM
			#, u'Keep': True
		}
		orth_pat_defs = self.get_patients_by_external_id(external_id = old_patient_id)
		all_modified = True
		for orth_pat_def in orth_pat_defs:
			_log.info('modifying Orthanc patient [%s]: DICOM ID [%s] -> [%s]', orth_pat_def['ID'], old_patient_id, new_patient_id)
			old_pat_data = self.get_patient(orth_pat_def['ID'])
			_log.debug('to be modified: %s', old_pat_data)
			if self.patient_is_protected(orth_pat_def['ID']):
				_log.debug('patient protected: %s, unprotecting for modification', orth_pat_def['ID'])
				if not self.unprotect_patient(orth_pat_def['ID']):
					_log.error('cannot unlock patient [%s], skipping', orth_pat_def['ID'])
					all_modified = False
					continue
				was_protected = True
			else:
				was_protected = False
			pat_url = '%s/patients/%s' % (self.__server_url, orth_pat_def['ID'])
			modify_url = '%s/modify' % pat_url
			result = self.__run_POST(modify_url, data = modify_data)
			_log.debug('modify result: %s', result)
			if result is False:
				_log.error('cannot modify patient [%s]', orth_pat_def['ID'])
				all_modified = False
				continue
			newly_created_orthanc_patient_id = result['ID']
			_log.info('newly created Orthanc patient ID: %s', newly_created_orthanc_patient_id)
			mod_pat_data = self.get_patient(newly_created_orthanc_patient_id)
			_log.debug('modified pat: %s', mod_pat_data)
			_log.debug('deleting archived patient: %s', self.__run_DELETE(pat_url))
			if was_protected:
				if not self.protect_patient(newly_created_orthanc_patient_id):
					_log.error('cannot re-lock (new) patient [%s]', newly_created_orthanc_patient_id)

		return all_modified

	#--------------------------------------------------------
	# upload API
	#--------------------------------------------------------
	def upload_dicom_file(self, filename:str, check_mime_type:bool=False) -> str | None:
		"""Upload a DICOM file.

		Will silently ignore DICOMDIR files (which are
		application/dicom but Orthanc does not process them).

		Args:
			filename: DICOM file to upload
			check_mime_type: whether to check the file for being application/dicom, and to fail if not

		Returns:
			None or Orthanc patient UID
		"""
		_log.info('processing: %s', filename)
		if gmTools.fname_stem(filename) == 'DICOMDIR':
			_log.debug('ignoring, no use uploading DICOMDIR files to Orthanc')
			return None

		if check_mime_type:
			mimetype = gmMimeLib.guess_mimetype(filename)
			if mimetype != 'application/dicom':
				_log.error('not considered a DICOM (application/dicom) file: %s, not uploading', mimetype)
				return None

		try:
			f = open(filename, 'rb')
		except Exception:
			_log.exception('failed to open file')
			return None

		dcm_data = f.read()
		f.close()
		upload_url = '%s/instances' % self.__server_url
		uploaded = self.__run_POST(upload_url, data = dcm_data, content_type = 'application/dicom')
		if uploaded is False:
			_log.error('upload failed')
			return None

		# typically a 404 following the upload of a DICOM file w/o identifiers
		if uploaded == []:
			_log.error('upload failed')
			return None

		_log.debug(uploaded)
		patient = uploaded['ParentPatient']
		# paranoia, as is our custom
		verified = self.verify_instance (
			instance_id = uploaded['ID'],
			filename = filename,
			attempt_download = True
		)
		if verified:
			return patient

		return None

	#--------------------------------------------------------
	def verify_instance(self, instance_id:str, filename:str=None, attempt_download:bool=False) -> bool:

		_BINARY_ATTACHMENTS = ['dicom']

		_log.debug('verifying instance [%s] against file [%s]', instance_id, filename)
		is_valid = True

		attachments_url = '%s/instances/%s/attachments' % (self.__server_url, instance_id)
		attachments = self.__run_GET(attachments_url, allow_cached = False)
		if not attachments:
			_log.error('cannot retrieve instance attachment list')
			return False

		for attachment in attachments:
			md5_orthanc = None
			# 1) verify MD5 inside Orthanc, if available (checks Orthanc storage corruption)
			available_fields_url = '%s/instances/%s/attachments/%s' % (self.__server_url, instance_id, attachment)
			available_fields = self.__run_GET(available_fields_url, allow_cached = False)
			if 'md5' in available_fields:
				md5_url = '%s/md5' % available_fields_url
				md5_orthanc = self.__run_GET(md5_url)
				verify_url = '%s/%s/verify-md5' % (attachments_url, attachment)
				if self.__run_POST(verify_url) is False:
					_log.error('MD5 verification failed, instance [%s], attachment=%s, url [%s]', instance_id, attachment, verify_url)
					_log.error('potentially Orthanc storage corruption')
					is_valid = False
				else:
					_log.debug('MD5: Orthanc DB <-> Orthanc storage: match')
			else:
				_log.debug('MD5 of instance attachment not available in Orthanc, cannot verify backend storage status')
			# 2) verify instance attachment can be downloaded
			md5_downloaded = None
			if attempt_download:
				attachment_filename = gmTools.get_unique_filename()
				download_url = '%s/instances/%s/attachments/%s/data' % (self.__server_url, instance_id, attachment)
				attachment_data = self.__run_GET(url = download_url, allow_cached = False)
				if isinstance(attachment_data, bytes):
					attachment_file = open(attachment_filename, 'wb')
				else:
					attachment_file = open(attachment_filename, 'wt')
					attachment_data = '%s' % attachment_data
				attachment_file.write(attachment_data)
				del attachment_data
				attachment_file.close()
				_log.debug('download: Orthanc -> localhost: success')
				if attachment not in _BINARY_ATTACHMENTS:
					_log.info('attachment of type [%s] not binary, cannot verify MD5 of download or local file against MD5 in Orthanc, skipping', attachment)
					continue
				md5_downloaded = gmTools.file2md5(attachment_filename)
			else:
				_log.debug('not downloading instance for verification')
			# 3) verify MD5 of downloaded instance against Orthanc, if possible
			if md5_downloaded and md5_orthanc:
				if md5_downloaded == md5_orthanc:
					_log.debug('MD5: Orthanc DB <-> localhost: match')
				else:
					_log.error('MD5 mismatch: Orthanc DB <-> localhost')
					_log.error('download: %s', md5_downloaded)
					_log.error('Orthanc : %s', md5_orthanc)
					is_valid = False
			if filename:
				md5_local = gmTools.file2md5(filename)
			else:
				_log.debug('local file not available for verification')
				md5_local = None
			# 4) verify MD5 of download against local file
			if md5_downloaded and md5_local:
				if md5_downloaded == md5_local:
					_log.debug('MD5: downloaded <-> pre-existing: match')
				else:
					_log.error('MD5 mismatch: downloaded <-> pre-existing')
					_log.error('download: %s', md5_downloaded)
					_log.error('locally : %s', md5_local)
					is_valid = False
			# 5) verify MD5 of local file against Orthanc
			if md5_local and md5_orthanc:
				if md5_local == md5_orthanc:
					_log.debug('MD5: Orthanc DB <-> pre-existing: match')
				else:
					_log.error('MD5 mismatch: Orthanc DB <-> pre-existing')
					_log.error('locally : %s', md5_local)
					_log.error('Orthanc : %s', md5_orthanc)
					is_valid = False
			# 6) consider comparing the raw pixel data or comparing the output of exiftool etc

		_log.debug('verified: %s', is_valid)
		return is_valid

	#--------------------------------------------------------
	def upload_dicom_files(self, files:list[str]=None, check_mime_type:bool=False) -> tuple[list[str],list[str],list[str]]:
		"""Upload a list of DICOM files.

		Args:
			files: list of files to upload
			check_mime_type: see upload_dicom_file()

		Returns:
			a tuple of lists (uploaded_files, files_not_uploaded, patients)

			patients will contain a list of patients affected by uploaded files
		"""
		uploaded = []
		not_uploaded = []
		patients = []
		for filename in files:
			patient = self.upload_dicom_file(filename, check_mime_type = check_mime_type)
			if not patient:
				not_uploaded.append(filename)
				continue

			uploaded.append(filename)
			if patient not in patients:
				patients.append(patient)

		if len(not_uploaded) > 0:
			_log.error('not all files uploaded')
		return (uploaded, not_uploaded, patients)

	#--------------------------------------------------------
	def upload_from_directory(self, directory:str=None, recursive:bool=False, check_mime_type:bool=False, ignore_other_files:bool=True):
		"""Upload DICOM files for a directory

		Args:
			directory: the directory from which to upload
			recursive: whether to recurse into subdirectories
			ignore_other_files: whether to actively ignore non-DICOM files
			check_mime_type: see upload_dicom_file()

		Returns:
			a tuple of lists (uploaded_files, files_not_uploaded, patients)

			patients will contain a list of patients affected by uploaded files
		"""
		#--------------------
		def _on_error(exc):
			_log.error('DICOM (?) file not accessible: %s', exc.filename)
			_log.error(exc)
		#--------------------

		_log.debug('uploading DICOM files from [%s]', directory)
		if not recursive:
			files2try = os.listdir(directory)
			_log.debug('found %s files', len(files2try))
			if ignore_other_files:
				files2try = [ f for f in files2try if gmMimeLib.guess_mimetype(f) == 'application/dicom' ]
				_log.debug('DICOM files therein: %s', len(files2try))
			return self.upload_dicom_files(files = files2try, check_mime_type = check_mime_type)

		_log.debug('recursing for DICOM files')
		uploaded = []
		not_uploaded = []
		patients = []
		for curr_root, curr_root_subdirs, curr_root_files in os.walk(directory, onerror = _on_error):
			_log.debug('recursing into [%s]', curr_root)
			files2try = [ os.path.join(curr_root, f) for f in curr_root_files ]
			_log.debug('found %s files', len(files2try))
			if ignore_other_files:
				files2try = [ f for f in files2try if gmMimeLib.guess_mimetype(f) == 'application/dicom' ]
				_log.debug('DICOM files therein: %s', len(files2try))
			up, not_up, pats = self.upload_dicom_files (
				files = files2try,
				check_mime_type = check_mime_type
			)
			uploaded.extend(up)
			not_uploaded.extend(not_up)
			patients.extend(pats)
		return (uploaded, not_uploaded, patients)

	#--------------------------------------------------------
	# helper functions
	#--------------------------------------------------------
	def __setup_patient_dict_from_orthanc_patient(self, orthanc_patient=None) -> dict:
		pat_dict = {
			'orthanc_id': orthanc_patient['ID'],
			'name': None,
			'external_id': None,
			'date_of_birth': None,
			'gender': None,
			'studies': []
		}
		try:
			pat_dict['name'] = orthanc_patient['MainDicomTags']['PatientName'].strip()
		except KeyError:
			pass
		try:
			pat_dict['external_id'] = orthanc_patient['MainDicomTags']['PatientID'].strip()
		except KeyError:
			pass
		try:
			pat_dict['date_of_birth'] = orthanc_patient['MainDicomTags']['PatientBirthDate'].strip()
		except KeyError:
			pass
		try:
			pat_dict['gender'] = orthanc_patient['MainDicomTags']['PatientSex'].strip()
		except KeyError:
			pass
		for key in pat_dict:
			if pat_dict[key] in ['unknown', '(null)', '']:
				pat_dict[key] = None
			pat_dict[key] = cleanup_dicom_string(pat_dict[key])
		return pat_dict

	#--------------------------------------------------------
	def __get_new_study_dict(self) -> dict[str, str|list|dict]:
		return {
			'orthanc_id': None,
			'date': None,
			'time': None,
			'description': None,
			'referring_doc': None,
			'requesting_doc': None,
			'requesting_org': None,
			'performing_doc': None,
			'operator_name': None,
			'radiographer_code': None,
			'radiology_org': None,
			'radiology_dept': None,
			'radiology_org_addr': None,
			'station_name': None,
			'series': []
		}

	#--------------------------------------------------------
	def __setup_study_dict_from_orthanc_study(self, orthanc_study=None, orthanc_patient=None) -> dict:
		study_keys2hide =  ['ModifiedFrom', 'Type', 'ID', 'ParentPatient', 'Series']
		study_dict = self.__get_new_study_dict()
		study_dict['orthanc_id'] = orthanc_study['ID']
		src2target_key_map = [
			('StudyDate', 'date'),
			('StudyTime', 'time'),
			('StudyDescription', 'description'),
			('ReferringPhysicianName', 'referring_doc'),
			('RequestingPhysician', 'requesting_doc'),
			('RequestingService', 'requesting_org'),
			('InstitutionAddress', 'radiology_org_addr')
		]
		for src_key, target_key in src2target_key_map:
			try:
				study_dict[target_key] = orthanc_study['MainDicomTags'][src_key].strip()
			except KeyError:
				pass
		try:
			study_dict['radiology_org'] = orthanc_study['MainDicomTags']['InstitutionName'].strip()
			if study_dict['radiology_org_addr']:
				if study_dict['radiology_org'] in study_dict['radiology_org_addr']:
					study_dict['radiology_org'] = None
		except KeyError:
			pass
		try:
			study_dict['radiology_dept'] = orthanc_study['MainDicomTags']['InstitutionalDepartmentName'].strip()
			if study_dict['radiology_org']:
				if study_dict['radiology_dept'] in study_dict['radiology_org']:
					study_dict['radiology_dept'] = None
			if study_dict['radiology_org_addr']:
				if study_dict['radiology_dept'] in study_dict['radiology_org_addr']:
					study_dict['radiology_dept'] = None
		except KeyError:
			pass
		try:
			study_dict['station_name'] = orthanc_study['MainDicomTags']['StationName'].strip()
			if study_dict['radiology_org'] is not None:
				if study_dict['station_name'] in study_dict['radiology_org']:
					study_dict['station_name'] = None
			if study_dict['radiology_org_addr'] is not None:
				if study_dict['station_name'] in study_dict['radiology_org_addr']:
					study_dict['station_name'] = None
			if study_dict['radiology_dept'] is not None:
				if study_dict['station_name'] in study_dict['radiology_dept']:
					study_dict['station_name'] = None
		except KeyError:
			pass
		for key in study_dict:
			if study_dict[key] in ['unknown', '(null)', '']:
				study_dict[key] = None
			study_dict[key] = cleanup_dicom_string(study_dict[key])
		study_dict['all_tags'] = {}
		try:
			orthanc_study['PatientMainDicomTags']
		except KeyError:
			orthanc_study['PatientMainDicomTags'] = orthanc_patient['MainDicomTags']
		for key in orthanc_study:
			if key == 'MainDicomTags':
				for mkey in orthanc_study['MainDicomTags']:
					study_dict['all_tags'][mkey] = orthanc_study['MainDicomTags'][mkey].strip()
				continue
			if key == 'PatientMainDicomTags':
				for pkey in orthanc_study['PatientMainDicomTags']:
					study_dict['all_tags'][pkey] = orthanc_study['PatientMainDicomTags'][pkey].strip()
				continue
			study_dict['all_tags'][key] = orthanc_study[key]
		_log.debug('study: %s', list(study_dict['all_tags']))
		for key in study_keys2hide:
			try:
				del study_dict['all_tags'][key]
			except KeyError: pass
		return study_dict

	#--------------------------------------------------------
	def __get_new_series_dict(self) -> dict:
		return {
			'orthanc_id': None,
			'instances': None,
			'modality': None,
			'date': None,
			'time': None,
			'description': None,
			'body_part': None,
			'protocol': None,
			'performed_procedure_step_description': None,
			'acquisition_device_processing_description': None,
			'operator_name': None,
			'radiographer_code': None,
			'performing_doc': None
		}

	#--------------------------------------------------------
	def __setup_series_dict_from_orthanc_series(self, orthanc_series=None, study_dict:dict=None) -> dict:
		series_keys2hide = ['ModifiedFrom', 'Type', 'ID', 'ParentStudy',   'Instances']
		ordered_slices = self.__run_GET(url = '%s/series/%s/ordered-slices' % (self.__server_url, orthanc_series['ID']))
		if ordered_slices is False:
			slices = orthanc_series['Instances']
		else:
			slices = [ s[0] for s in ordered_slices['SlicesShort'] ]
		series_dict = self.__get_new_series_dict()
		series_dict['orthanc_id'] = orthanc_series['ID']
		series_dict['instances'] = slices
		src2target_key_map = [
			('Modality', 'modality'),
			('SeriesDate', 'date'),
			('SeriesTime', 'time'),
			('SeriesDescription', 'description'),
			('BodyPartExamined', 'body_part'),
			('ProtocolName', 'protocol'),
			('PerformedProcedureStepDescription', 'performed_procedure_step_description'),
			('AcquisitionDeviceProcessingDescription', 'acquisition_device_processing_description'),
			('OperatorsName', 'operator_name'),
			('RadiographersCode', 'radiographer_code'),
			('PerformingPhysicianName', 'performing_doc')
		]
		for src_key, target_key in src2target_key_map:
			try:
				series_dict[target_key] = orthanc_series['MainDicomTags'][src_key].strip()
			except KeyError:
				pass
		for key in series_dict:
			if series_dict[key] in ['unknown', '(null)', '']:
				series_dict[key] = None
		if series_dict['description'] == series_dict['protocol']:
			_log.debug('<series description> matches <series protocol>, ignoring protocol')
			series_dict['protocol'] = None
		if series_dict['performed_procedure_step_description'] in [series_dict['description'], series_dict['protocol']]:
			series_dict['performed_procedure_step_description'] = None
		if series_dict['performed_procedure_step_description']:
			# weed out "numeric" only
			if regex.match (r'[.,/\|\-\s\d]+', series_dict['performed_procedure_step_description'], flags = regex.UNICODE):
				series_dict['performed_procedure_step_description'] = None
		if series_dict['acquisition_device_processing_description'] in [series_dict['description'], series_dict['protocol']]:
			series_dict['acquisition_device_processing_description'] = None
		if series_dict['acquisition_device_processing_description']:
			# weed out "numeric" only
			if regex.match (r'[.,/\|\-\s\d]+', series_dict['acquisition_device_processing_description'], flags = regex.UNICODE):
				series_dict['acquisition_device_processing_description'] = None
		if series_dict['date'] == study_dict['date']:
			_log.debug('<series date> matches <study date>, ignoring date')
			series_dict['date'] = None
		if series_dict['time'] == study_dict['time']:
			_log.debug('<series time> matches <study time>, ignoring time')
			series_dict['time'] = None
		for key in series_dict:
			series_dict[key] = cleanup_dicom_string(series_dict[key])
		series_dict['all_tags'] = {}
		for key in orthanc_series:
			if key == 'MainDicomTags':
				for mkey in orthanc_series['MainDicomTags']:
					series_dict['all_tags'][mkey] = orthanc_series['MainDicomTags'][mkey].strip()
				continue
			series_dict['all_tags'][key] = orthanc_series[key]
		_log.debug('series: %s', list(series_dict['all_tags']))
		for key in series_keys2hide:
			try: del series_dict['all_tags'][key]
			except KeyError: pass
		return series_dict

	#--------------------------------------------------------
	def get_studies_list_by_orthanc_patient_list(self, orthanc_patients:list=None) -> list[dict]:
		studies_by_patient = []
		for orth_pat in orthanc_patients:
			pat_dict = self.__setup_patient_dict_from_orthanc_patient(orthanc_patient = orth_pat)
			studies_by_patient.append(pat_dict)
			orth_studies = self.__run_GET(url = '%s/patients/%s/studies' % (self.__server_url, orth_pat['ID']))
			if orth_studies is False:
				_log.error('cannot retrieve studies')
				return []

			for orth_study in orth_studies:
				study_dict = self.__setup_study_dict_from_orthanc_study(orthanc_study = orth_study, orthanc_patient = orth_pat)
				pat_dict['studies'].append(study_dict)
				for orth_series_id in orth_study['Series']:
					orth_series = self.__run_GET(url = '%s/series/%s' % (self.__server_url, orth_series_id))
					if orth_series is False:
						_log.error('cannot retrieve series')
						return []

					series_dict = self.__setup_series_dict_from_orthanc_series(orthanc_series = orth_series, study_dict = study_dict)
					study_dict['operator_name'] = series_dict['operator_name']			# will collapse all operators into that of the last series
					study_dict['radiographer_code'] = series_dict['radiographer_code']	# will collapse all into that of the last series
					study_dict['performing_doc'] = series_dict['performing_doc']		# will collapse all into that of the last series
					study_dict['series'].append(series_dict)

		return studies_by_patient

	#--------------------------------------------------------
	# generic REST helpers
	#--------------------------------------------------------
	def run_GET(self, url=None, data=None, allow_cached=False):
		url = '%s/%s' % (self.__server_url, url)
		return self.__run_GET(url = url, data = data, allow_cached = allow_cached)

	#--------------------------------------------------------
	def __run_GET(self, url=None, data=None, allow_cached=False, also_return_status=False):
		if data is None:
			data = {}
		headers = {}
		if not allow_cached:
			headers['cache-control'] = 'no-cache'
		params = ''
		if data:
			params = '?' + urlencode(data)
		url_with_params = url + params
		#_log.debug('URL with parameters: >>>%s<<<', url_with_params)
		try:
			response, content = self.__conn.request(url_with_params, 'GET', headers = headers)
		except (OverflowError, socket.error, http.client.ResponseNotReady, http.client.InvalidURL, http.client.RemoteDisconnected, httplib2.ServerNotFoundError):
			# http.client.RemoteDisconnected: observed during GET while Orthanc was shutting down for backup
			_log.exception('exception in GET')
			_log.debug(' url: %s', url_with_params)
			_log.debug(' headers: %s', headers)
			if also_return_status:
				return (False, -1)
			return False

		if response.status not in [ 200 ]:
			_log.error('GET returned non-OK status: %s', response.status)
			_log.debug(' url: %s', url_with_params)
			_log.debug(' headers: %s', headers)
			_log.error(' response: %s', response)
			_log.debug(' content: %s', content)
			if also_return_status:
				return (False, response.status)
			return False

		#_log.debug('response: %s', response)
		#_log.debug('type(content): %s', type(content))
		content_type = response['content-type'].strip()
		if content_type.startswith('text/plain'):
			# utf8 ?
			# urldecode ?
			# latin1 = Orthanc default = tools/default-encoding ?
			# ascii ?
			content = content.decode('utf8')
		elif content_type.startswith('application/json'):
			try:
				content = json.loads(content)
			except Exception:
				_log.exception('failed to json.loads(content) despite application/json indicated, returning content and hoping for the best')
				mime_type, charset_def = content_type.split(';')
				charset = charset_def.strip().split('=')[1]
				#content = content.decode('utf8')
				content = content.decode(charset)
			#_log.debug(content)
		else:
			_log.error('content: <%s>, not <text/plain> or <application/json> -- returning raw content', content_type)
		if also_return_status:
			return (content, response.status)

		return content

	#--------------------------------------------------------
	def __run_POST(self, url=None, data=None, content_type=None, output_file=None):
		body = data
		headers = {'content-type' : content_type}
		if isinstance(data, str):
			if content_type is None:
				headers['content-type'] = 'text/plain'
		elif isinstance(data, bytes):
			if content_type is None:
				headers['content-type'] = 'application/octet-stream'
		else:
			body = json.dumps(data)
			headers['content-type'] = 'application/json'

		try:
			try:
				response, content = self.__conn.request(url, 'POST', body = body, headers = headers)
			except BrokenPipeError:
				_log.debug('retrying after BrokenPipeError')
				response, content = self.__conn.request(url, 'POST', body = body, headers = headers)
		except (socket.error, http.client.ResponseNotReady, OverflowError):
			_log.exception('exception in POST')
			_log.debug(' url: %s', url)
			_log.debug(' headers: %s', headers)
			_log.debug(' body: %s', body[:16])
			return False

		if response.status == 404:
			_log.debug('no data, response: %s', response)
			if output_file is None:
				return []
			return False

		if response.status not in [ 200, 302 ]:
			_log.error('POST returned non-OK (not 200,302) status: %s', response.status)
			_log.debug(' url: %s', url)
			_log.debug(' headers: %s', headers)
			_log.debug(' body: %s', body[:16])
			_log.error(' response: %s', response)
			_log.debug(' content: %s', content)
			return False

		try:
			content = json.loads(content)
		except Exception:
			pass
		if output_file is None:
			return content

		output_file.write(content)
		return True

	#--------------------------------------------------------
	def __run_PUT(self, url=None, data=None, content_type=None):

		body = data
		headers = {'content-type' : content_type}
		if isinstance(data, str):
			if content_type is None:
				headers['content-type'] = 'text/plain'
		elif isinstance(data, bytes):
			if content_type is None:
				headers['content-type'] = 'application/octet-stream'
		else:
			body = json.dumps(data)
			headers['content-type'] = 'application/json'

		try:
			try:
				response, content = self.__conn.request(url, 'PUT', body = body, headers = headers)
			except BrokenPipeError:
				response, content = self.__conn.request(url, 'PUT', body = body, headers = headers)
		except (socket.error, http.client.ResponseNotReady, OverflowError):
			_log.exception('exception in PUT')
			_log.debug(' url: %s', url)
			_log.debug(' headers: %s', headers)
			_log.debug(' body: %s', body[:16])
			return False

		if response.status == 404:
			_log.debug('no data, response: %s', response)
			return []
		if response.status not in [ 200, 302 ]:
			_log.error('PUT returned non-OK status: %s', response.status)
			_log.debug(' url: %s', url)
			_log.debug(' headers: %s', headers)
			_log.debug(' body: %s', body[:16])
			_log.error(' response: %s', response)
			_log.debug(' content: %s', content)
			return False

		if response['content-type'].startswith('text/plain'):
			# utf8 ?
			# urldecode ?
			# latin1 = Orthanc default = tools/default-encoding ?
			# ascii ?
			return content.decode('utf8')

		if response['content-type'].startswith('application/json'):
			try:
				return json.loads(content)
			except Exception:
				return content

		return content

	#--------------------------------------------------------
	def __run_DELETE(self, url=None):
		try:
			response, content = self.__conn.request(url, 'DELETE')
		except (http.client.ResponseNotReady, socket.error, OverflowError):
			_log.exception('exception in DELETE')
			_log.debug(' url: %s', url)
			return False

		if response.status not in [ 200 ]:
			_log.error('DELETE returned non-OK status: %s', response.status)
			_log.debug(' url: %s', url)
			_log.error(' response: %s', response)
			_log.debug(' content: %s', content)
			return False

		if response['content-type'].startswith('text/plain'):
			# utf8 ?
			# urldecode ?
			# latin1 = Orthanc default = tools/default-encoding ?
			# ascii ?
			return content.decode('utf8')

		if response['content-type'].startswith('application/json'):
			try:
				return json.loads(content)
			except Exception:
				return content

		return content

	#--------------------------------------------------------
	def _get_server_url(self):
		return self.__server_url

	server_url = property(_get_server_url)

#------------------------------------------------------------
def cleanup_dicom_string(dicom_str) -> str:
	if not isinstance(dicom_str, str):
		return dicom_str

	dicom_str = regex.sub(r'\^+', ' ', dicom_str.strip('^'))
	#dicom_str = dicom_str.replace('\r\n', ' [CR] ')
	return dicom_str

#---------------------------------------------------------------------------
def dicomize_file(filename:str=None, title:str=None, person=None, dcm_name:str=None, verbose:bool=False, dcm_template_file:str=None, dcm_transfer_series:bool=True, content_date=None) -> str:
	"""Encapsulate a file inside a DCM file.

	Dates and times of the instance are set to 'now'.

	Works for PDF documents and images which are/can be converted to JPG.

	Args:
		filename: the file to encapsulate
		title: document title, defaults to filename
		person: a GNUmed person instance from which to derive demographics, None -> derive from *dcm_template_file*
		dcm_name: filename for the resulting DICOM file, None -> auto-create name
		verbose: passed to external converter
		dcm_template_file: DICOM file from which to derive patient demographics and study ID, None -> *person* must be defined
		dcm_transfer_series: only applies if *dcm_template_file* given
			True = derive series from *dcm_template_file*,
			False = only derive study from *dcm_template_file* and create a new series
		content_date: date/time to use for study/series/instance, as needed; None -> use now()

	Returns:
		DICOM file name or None on failure.
	"""
	assert (filename is not None), '<filename> must not be None'
	assert (not ((person is None) and (dcm_template_file is None))), '<person> or <dcm_template_file> must not be None'

	# already DCM ?
	if gmMimeLib.guess_mimetype(filename) == 'application/dicom':
		_log.error('already a DICOM file: %s', filename)
		if dcm_name is None:
			return filename

		return shutil.copy2(filename, dcm_name)

	dcm_fname = dicomize_pdf (
		pdf_name = filename,
		title = title,
		person = person,
		dcm_name = dcm_name,
		verbose = verbose,
		dcm_template_file = dcm_template_file,
		dcm_transfer_series = dcm_transfer_series,
		content_date = content_date
	)
	if dcm_fname is not None:
		return dcm_fname

	_log.debug('does not seem to be a PDF: %s', filename)
	converted_fname = gmMimeLib.convert_file(filename = filename, target_mime = 'image/jpeg')
	if converted_fname is None:
		_log.error('cannot convert to JPG: %s', filename)
		return None

	dcm_name = dicomize_jpg (
		jpg_name = converted_fname,
		title = title,
		person = person,
		dcm_name = dcm_name,
		verbose = verbose,
		dcm_template_file = dcm_template_file,
		dcm_transfer_series = dcm_transfer_series,
		content_date = content_date
	)
	return dcm_name

#---------------------------------------------------------------------------
def dicomize_pdf(pdf_name:str=None, title:str=None, person=None, dcm_name:str=None, verbose:bool=False, dcm_template_file:str=None, dcm_transfer_series:bool=True, content_date=None) -> str:
	"""Encapsulate a PDF file inside a DCM file.

	Dates and times of the instance are set to 'now'.

	Args:
		pdf_name: the PDF file to encapsulate
		title: document title, None -> *pdf_name*, also used as study/series description
		person: see *dicomize_file()*
		dcm_name: see *dicomize_file()*
		verbose: see *dicomize_file()*
		dcm_template_file: see *dicomize_file()*
		dcm_transfer_series: see *dicomize_file()*
		content_date: see *dicomize_file()*

	Returns:
		DICOM file name or None on failure.
	"""
	assert (pdf_name is not None), '<pdf_name> must not be None'
	assert (not ((person is None) and (dcm_template_file is None))), '<person> or <dcm_template_file> must not be None'

	if dcm_name is None:
		dcm_name = gmTools.get_unique_filename(suffix = '.dcm')
	_log.debug('%s -> %s', pdf_name, dcm_name)
	if title is None:
		title = gmTools.fname_stem(pdf_name)
	if content_date is None:
		content_date = gmDateTime.pydt_now_here()
	cmd_line = [
		'pdf2dcm',
		'--title', title,
		'--key', '0008,1030=%s' % title,							# StudyDescription
		'--key', '0008,103E=%s' % title,							# SeriesDescription
		'--key', '0008,0021=%s' % content_date.strftime('%Y%m%d'),	# SeriesDate
		'--key', '0008,0023=%s' % content_date.strftime('%Y%m%d'),	# ContentDate
		'--key', '0008,0031=%s' % content_date.strftime('%H%M%s.0'),# SeriesTime
		'--key', '0008,0033=%s' % content_date.strftime('%H%M%s.0')	# ContentTime
	]
	if dcm_template_file is None:
		# StudyDate
		cmd_line.append('--key')
		cmd_line.append('0008,0020=%s' % content_date.strftime('%Y%m%d'))
		# StudyTime
		cmd_line.append('--key')
		cmd_line.append('0008,0030=%s' % content_date.strftime('%H%M%s.0'))
		# PatientName
		name = person.active_name
		cmd_line.append('--patient-id')
		cmd_line.append(person.suggest_external_id(target = 'PACS'))
		cmd_line.append('--patient-name')
		cmd_line.append(('%s^%s' % (name['lastnames'], name['firstnames'])).replace(' ', '^'))
		if person['dob']:
			cmd_line.append('--patient-birthdate')
			cmd_line.append(person.get_formatted_dob(format = '%Y%m%d', honor_estimation = False))
		if person['gender']:
			cmd_line.append('--patient-sex')
			cmd_line.append(_map_gender_gm2dcm[person['gender']])
	else:
		_log.debug('DCM template file: %s', dcm_template_file)
		if dcm_transfer_series:
			cmd_line.append('--series-from')
			cmd_line.append(dcm_template_file)
		else:
			cmd_line.append('--study-from')
			cmd_line.append(dcm_template_file)
	if verbose:
		cmd_line.append('--log-level')
		cmd_line.append('trace')
	cmd_line.append(pdf_name)
	cmd_line.append(dcm_name)
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = cmd_line, encoding = 'utf8', verbose = verbose)
	if success:
		return dcm_name

	return None

#---------------------------------------------------------------------------
def dicomize_jpg(jpg_name:str=None, title:str=None, person=None, dcm_name:str=None, verbose:bool=False, dcm_template_file:str=None, dcm_transfer_series:bool=True, content_date=None) -> str:
	"""Encapsulate a JPG file inside a DCM file.

	Dates and times of the instance are set to 'now'.

	Args:
		jpg_name: the JPG file to encapsulate
		title: document title, None -> *jpg_name*, used as study/series description
		person: see *dicomize_file()*
		dcm_name: see *dicomize_file()*
		verbose: see *dicomize_file()*
		dcm_template_file: see *dicomize_file()*
		dcm_transfer_series: see *dicomize_file()*
		content_date: see *dicomize_file()*

	Returns:
		DICOM file name or None on failure.
	"""
	assert (jpg_name is not None), '<jpg_name> must not be None'
	assert (not ((person is None) and (dcm_template_file is None))), 'both <person> and <dcm_template_file> are None, but one is needed'

	if dcm_name is None:
		dcm_name = gmTools.get_unique_filename(suffix = '.dcm')
	_log.debug('%s -> %s', jpg_name, dcm_name)
	if title is None:
		title = gmTools.fname_stem(jpg_name)
	if content_date is None:
		content_date = gmDateTime.pydt_now_here()
	cmd_line = [
		'img2dcm',
		'--keep-appn',													# carry over EXIF data
		'--insist-on-jfif',												# process valid JFIF only
		'--key', '0008,1030=%s' % title,								# StudyDescription
		'--key', '0008,103E=%s' % title,								# SeriesDescription
		'--key', '0008,0021=%s' % content_date.strftime('%Y%m%d'),		# SeriesDate
		'--key', '0008,0031=%s' % content_date.strftime('%H%M%s.0'),	# SeriesTime
		'--key', '0008,0023=%s' % content_date.strftime('%Y%m%d'),		# ContentDate
		'--key', '0008,0033=%s' % content_date.strftime('%H%M%s.0')		# ContentTime
	]
	if dcm_template_file is None:
		# StudyDate
		cmd_line.append('--key')
		cmd_line.append('0008,0020=%s' % content_date.strftime('%Y%m%d'))
		# StudyTime
		cmd_line.append('--key')
		cmd_line.append('0008,0030=%s' % content_date.strftime('%H%M%s.0'))
		# PatientName
		name = person.active_name
		cmd_line.append('--key')
		cmd_line.append('0010,0010=%s' % ('%s^%s' % (
			name['lastnames'],
			name['firstnames'])
		).replace(' ', '^'))
		# PatientID
		cmd_line.append('--key')
		cmd_line.append('0010,0020=%s' % person.suggest_external_id(target = 'PACS'))
		# DOB
		cmd_line.append('--key')
		cmd_line.append('0010,0030=%s' % person.get_formatted_dob(format = '%Y%m%d', honor_estimation = False))
		# gender
		if person['gender']:
			cmd_line.append('--key')
			cmd_line.append('0010,0040=%s' % _map_gender_gm2dcm[person['gender']])
	else:
		_log.debug('DCM template file: %s', dcm_template_file)
		if dcm_transfer_series:
			cmd_line.append('--series-from')
			cmd_line.append(dcm_template_file)
		else:
			cmd_line.append('--study-from')
			cmd_line.append(dcm_template_file)
	if verbose:
		cmd_line.append('--log-level')
		cmd_line.append('trace')
	cmd_line.append(jpg_name)
	cmd_line.append(dcm_name)
	success, exit_code, stdout = gmShellAPI.run_process(cmd_line = cmd_line, encoding = 'utf8', verbose = verbose)
	if success:
		return dcm_name

	return None

#---------------------------------------------------------------------------
def run_file2dicom_tool(fname:str=None, dcm_template:str=None) -> str:
	"""Convert a file into DICOM format.

	This offers a primitive text user interface.

	Args:
		fname: the file to convert, must be image or PDF
		dcm_template: a DCM file to use as template for study/series data, optional

	Returns:
		name of the new DICOM file, or None
	"""
	if dcm_template is None:
		from Gnumed.pycommon import gmPG2
		gmPG2.request_login_params(setup_pool = True)
		from Gnumed.business import gmPersonSearch
		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			return None

	else:
		pat = None

	dt = None
	while dt is None:
		iso = input('enter date (ISO - YYYY-MM-DD): ')
		try:
			dt = pydt.datetime.fromisoformat(iso)
		except ValueError:
			if iso.strip() == '':
				return None
			dt = None

	desc = input('enter description (ASCII): ')
	if desc.strip() == '':
		desc = None

	print('patient:', pat)
	print('DCM template:', dcm_template)
	print()
	print('file to convert:', fname)
	print('series date:', dt)
	print('description:', desc)
	input('hit <ENTER> to convert')
	dcm = dicomize_file (
		filename = fname,
		person = pat,
		dcm_name = fname + '.dcm',
		verbose = True,
		content_date = dt,
		title = desc,
		dcm_template_file = dcm_template
	)
	print('DCM file:', dcm)

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) == 1:
		sys.exit()

	from Gnumed.pycommon import gmLog2
	gmLog2.print_logfile_name()

	if sys.argv[1] != 'test':
		fname = sys.argv[1]
		try: dcm_template = sys.argv[2]
		except IndexError: dcm_template = None
		run_file2dicom_tool(fname, dcm_template)
		sys.exit()

	#--------------------------------------------------------
	def orthanc_console(host, port):
		print('Please enter patient name parts, separated by SPACE.')
		while True:
			entered_name = gmTools.prompted_input(prompt = "\nEnter person search term or leave blank to exit")
			if entered_name in ['exit', 'quit', 'bye', None]:
				print("user cancelled patient search")
				break

#			pats = orthanc.get_patients_by_external_id(external_id = entered_name)
#			if len(pats) > 0:
#				print('Patients found:')
#				for pat in pats:
#					print(' -> ', pat)
#				continue

#			pats = orthanc.get_patients_by_name(name_parts = entered_name.split(), fuzzy = True)
#			print('Patients found:')
#			for pat in pats:
#				print(' -> ', pat)
#				print('  verifying ...')
#				bad_data = orthanc.verify_patient_data(pat['ID'])
#				print('  bad data:')
#				for bad in bad_data:
#					print('  -> ', bad)
#				continue

#			continue

			pats = orthanc.get_studies_list_by_patient_name(name_parts = entered_name.split(), fuzzy = True)
			print('Patients found from studies list:')
			for pat in pats:
				print(' -> ', pat['name'])
				input()
				for study in pat['studies']:
					print(' ', gmTools.format_dict_like(study, relevant_keys = ['orthanc_id', 'date', 'time'], template = 'study [%%(orthanc_id)s] at %%(date)s %%(time)s contains %s series' % len(study['series'])))
#					for series in study['series']:
#						print (
#							u'  ',
#							gmTools.format_dict_like (
#								series,
#								relevant_keys = ['orthanc_id', 'date', 'time', 'modality', 'instances', 'body_part', 'protocol', 'description', 'station'],
#								template = u'series [%(orthanc_id)s] at %(date)s %(time)s: "%(description)s" %(modality)s@%(station)s (%(protocol)s) of body part "%(body_part)s" holds images:\n%(instances)s'
#							)
#						)
#					print(orthanc.get_studies_with_dicomdir(study_ids = [study['orthanc_id']], filename = 'study_%s.zip' % study['orthanc_id'], create_zip = True))
				#print(orthanc.get_study_as_zip(study_id = study['orthanc_id'], filename = 'study_%s.zip' % study['orthanc_id']))
				#print(orthanc.get_studies_as_zip_with_dicomdir(study_ids = [ s['orthanc_id'] for s in pat['studies'] ], filename = 'studies_of_%s.zip' % pat['orthanc_id']))
				print('--------')

	#--------------------------------------------------------
	def run_console():
		orthanc_console(host, port)

	#--------------------------------------------------------
	def test_modify_patient_id():
		print('Please enter patient name parts, separated by SPACE.')
		entered_name = gmTools.prompted_input(prompt = "\nEnter person search term or leave blank to exit")
		if entered_name in ['exit', 'quit', 'bye', None]:
			print("user cancelled patient search")
			return

		pats = orthanc.get_patients_by_name(name_parts = entered_name.split(), fuzzy = True)
		if len(pats) == 0:
			print('no patient found')
			return

		pat = pats[0]
		print('test patient:')
		print(pat)
		old_id = pat['MainDicomTags']['PatientID']
		new_id = old_id + '-1'
		print('setting [%s] to [%s]:' % (old_id, new_id), orthanc.modify_patient_id(old_id, new_id))

	#--------------------------------------------------------
	def test_upload_file():
		print(orthanc.upload_dicom_file(filename = sys.argv[4], check_mime_type = True))

	#--------------------------------------------------------
	def test_upload_files():
		#orthanc.upload_dicom_file(sys.argv[2])
		print(orthanc.upload_from_directory(directory = sys.argv[4], recursive = True, check_mime_type = False, ignore_other_files = True))

	#--------------------------------------------------------
	def test_get_instance_preview():
		print(orthanc.get_instance_preview('f4f07d22-0d8265ef-112ea4e9-dc140e13-350c06d1'))
		print(orthanc.get_instance('f4f07d22-0d8265ef-112ea4e9-dc140e13-350c06d1'))

	#--------------------------------------------------------
	def test_get_instance_tags():
		instance_id = 'f4f07d22-0d8265ef-112ea4e9-dc140e13-350c06d1'
		for key, value in orthanc.get_instance_dicom_tags(instance_id, simplified = False).items():
			print(key, ':', value)
		print()
		#print(orthanc.get_instance_dicom_tags(instance_id, simplified = True))

	#--------------------------------------------------------
	def test_pdf2dcm():
		#print(pdf2dcm(filename = filename, patient_id = 'ID::abcABC', dob = '19900101'))
		#from Gnumed.business import gmPerson
		#pers = gmPerson.cPerson(12)
		from Gnumed.business import gmPersonSearch
		pers = gmPersonSearch.ask_for_patient()
		if pers is None:
			return

		print(pers)
		try:
			print(dicomize_pdf(pdf_name = sys.argv[2], person = pers, dcm_name = None, verbose = True, dcm_template_file = sys.argv[3]))#, title = 'test'))
		except IndexError:
			print(dicomize_pdf(pdf_name = sys.argv[2], person = pers, dcm_name = None, verbose = True))#, title = 'test'))

	#--------------------------------------------------------
	def test_img2dcm():
		from Gnumed.pycommon import gmPG2
		gmPG2.request_login_params(setup_pool = True)
		#print(pdf2dcm(filename = filename, patient_id = 'ID::abcABC', dob = '19900101'))
		#from Gnumed.business import gmPerson
		#pers = gmPerson.cPerson(12)
		from Gnumed.business import gmPersonSearch
		pers = gmPersonSearch.ask_for_patient()
		if pers is None:
			return

		dt = None
		while dt is None:
			iso = input('enter date: ')
			try:
				dt = pydt.datetime.fromisoformat(iso)
			except ValueError:
				if iso.strip() == '':
					return

		print(pers)
		print(iso)
		input('enter to continue')

		try:
			print(dicomize_jpg(jpg_name = sys.argv[2], person = pers, dcm_name = sys.argv[2]+'.dcm', verbose = True, dcm_template_file = sys.argv[3]))#, title = 'test'))
		except IndexError:
			print(dicomize_jpg (
				jpg_name = sys.argv[2],
				person = pers,
				dcm_name = sys.argv[2]+'.dcm',
				verbose = True,
				content_date = dt
			))#, title = 'test'))

	#--------------------------------------------------------
	def test_file2dcm():
		from Gnumed.business import gmPersonSearch
		person = gmPersonSearch.ask_for_patient()
		if person is None:
			return
		print(person)
		try:
			print(dicomize_file(filename = sys.argv[2], person = person, dcm_name = sys.argv[2]+'.dcm', verbose = True, dcm_template_file = sys.argv[3], title = sys.argv[4]))
		except IndexError:
			pass
		try:
			print(dicomize_file(filename = sys.argv[2], person = person, dcm_name = sys.argv[2]+'.dcm', verbose = True, title = sys.argv[3]))
		except IndexError:
			print(dicomize_file(filename = sys.argv[2], person = person, dcm_name = sys.argv[2]+'.dcm', verbose = True))

	#--------------------------------------------------------
	def test_patient():
		#print(orthanc.get_patients_by_name_parts(name_parts = ['Seb'], fuzzy = True))
		#return

		pat = orthanc.get_patient('bc107806-098880eb-95529338-0f54c681-c4b5ccc4')
		for key in pat:
			print(key, pat[key])
		#input()
		#print(orthanc.get_patient('1cff9d34-96047a5a-afb97dd0-33a84dc7-a710ef8f'))
		return

		#'/patients/89729867-a08815a6-37c59f5a-f1f6ea57-6c1e17cb'
		orthanc_id = '89729867-a08815a6-37c59f5a-f1f6ea57-6c1e17cb'
		instances_url = 'patients/%s/instances' % orthanc_id
		print(instances_url)
		#new_patient_id = 'xxx'
		instances = orthanc.run_GET(instances_url)
		for instance in instances:
			instance_id = instance['ID']
			tags = orthanc.get_instance_dicom_tags(instance_id, simplified = False)
			if tags['0010,0030']['Value'] != '19810416':
				continue
			#orthanc.modify_patient_id_of_instance(instance_id, new_patient_id)
			#print(tags['0010,0030']['PatientID'])
			#print(tags['0010,0030']['PatientName'])
			#continue
			for key, value in tags.items():
				print(key, ':', value)
#			instance_id = instance['ID']
#			attachments_url = '%s/instances/%s/attachments' % (self.__server_url, instance_id)
#			attachments = self.__run_GET(attachments_url, allow_cached = True)
#			for attachment in attachments:
#				verify_url = '%s/%s/verify-md5' % (attachments_url, attachment)
#				# False, success = "{}"
#				#2018-02-08 19:11:27  ERROR     gm.dicom      [-1211701504 MainThread]  (gmDICOM.py::__run_POST() #986): cannot POST: http://localhost:8042/instances/5a8206f4-24619e76-6650d9cd-792cdf25-039e96e6/attachments/dicom-as-json/verify-md5
#				#2018-02-08 19:11:27  ERROR     gm.dicom      [-1211701504 MainThread]  (gmDICOM.py::__run_POST() #987): response: {'status': '400', 'content-length': '0'}
#				if self.__run_POST(verify_url) is not False:
#					continue
#				_log.error('bad MD5 of DICOM file at url [%s]: patient=%s, attachment_type=%s', verify_url, orthanc_id, attachment)
#				bad_data.append({'patient': orthanc_id, 'instance': instance_id, 'type': attachment, 'orthanc': '%s [%s]' % (self.server_identification, self.__server_url)})

	#--------------------------------------------------------
	def test_verify_instance():
		# u'Path': u'/instances/1440110e-9cd02a98-0b1c0452-087d35db-3fd5eb05'
		#instance_id = '1440110e-9cd02a98-0b1c0452-087d35db-3fd5eb05'
		#instance_id = '5a8206f4-24619e76-6650d9cd-792cdf25-039e96e6'
		instance_id = '7e99fa76-3699ab68-7fd9d2de-c621b331-b4fe7394'
		print('verifying [%s]' % instance_id)
		result = orthanc.verify_instance (
			instance_id = instance_id
#			, filename = None
			, attempt_download = True
		)
		print(result)

	#--------------------------------------------------------
	def _connect():
		global host
		try:
			host = sys.argv[2]
		except IndexError:
			host = None
		global port
		try:
			port = sys.argv[3]
		except IndexError:
			port = '8042'

		global orthanc
		orthanc = cOrthancServer()
#		if not orthanc.connect(host, port, user = None, password = None, expected_minimal_version = '1'):		#, expected_aet = 'another AET'
#		if not orthanc.connect(host, port, user = 'any-doc', password = '?', expected_minimal_version = '1'):		#, expected_aet = 'another AET'
		if not orthanc.connect(host, port, user = None, password = None, expected_minimal_version = '1'):		#, expected_aet = 'another AET'
			print('error connecting to server:', orthanc.connect_error)
			sys.exit(-1)

		print('Connected to Orthanc server "%s" (AET [%s] - version [%s] - DB [%s])' % (
			orthanc.server_identification['Name'],
			orthanc.server_identification['DicomAet'],
			orthanc.server_identification['Version'],
			orthanc.server_identification['DatabaseVersion']
		))
		print('')

	#--------------------------------------------------------
	#test_pdf2dcm()
	#test_img2dcm()
	#test_file2dcm()
	#sys.exit

	_connect()
	run_console()
	#test_verify_instance()
	#test_modify_patient_id()
	#test_upload_files()
	#test_upload_file()
	#test_get_instance_preview()
	#test_get_instance_tags()
	#test_patient()
