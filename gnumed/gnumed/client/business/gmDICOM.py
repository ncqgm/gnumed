# -*- coding: utf-8 -*-
#============================================================

from __future__ import print_function

__doc__ = """GNUmed DICOM handling middleware"""

__license__ = "GPL v2 or later"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


# stdlib
import sys
import io
import logging
import httplib			# needed for exception names thrown by httplib2, duh |-(
import httplib2
import json
from urllib import urlencode
import distutils.version as version


# GNUmed modules
#if __name__ == '__main__':
#	sys.path.insert(0, '../../')
#from Gnumed.pycommon import gmPG2
#from Gnumed.pycommon import gmBusinessDBObject
#from Gnumed.pycommon import gmHooks
#from Gnumed.pycommon import gmDispatcher

_log = logging.getLogger('gm.dicom')

_map_gender_gm2dcm = {
	'm': 'M',
	'f': 'F',
	'tm': 'M',
	'tf': 'F',
	'h': None
}

#============================================================
class cORTHANCServer:
	# REST API access to ORTHANC DICOM servers

#	def __init__(self):
#		self.__server_identification = None
#		self.__user = None
#		self.__password = None
#		self.__conn = None
#		self.__server_url = None

	#--------------------------------------------------------
	def connect(self, url, user, password, expected_minimal_version=None, expected_name=None, expected_aet=None):
		self.__server_url = url			# say, u'http://host:port'
		self.__user = user
		self.__password = password
		_log.info('connecting as [%s] to ORTHANC server at [%s]', self.__user, self.__server_url)
		self.__conn = httplib2.Http()
		self.__conn.add_credentials(self.__user, self.__password)
		_log.debug('connected to server: %s', self.server_identification)
		self.connect_error = u''
		if self.server_identification is False:
			self.connect_error += u'retrieving server identification failed'
			return False
		if expected_minimal_version is not None:
			if version.LooseVersion(self.server_identification['Version']) < version.LooseVersion(expected_min_version):
				_log.error('server too old, needed [%s]', expected_min_version)
				self.connect_error += u'server too old, needed version [%s]' % expected_min_version
				return False
		if expected_name is not None:
			if self.server_identification['Name'] != expected_name:
				_log.error('wrong server name, expected [%s]', expected_name)
				self.connect_error += u'wrong server name, expected [%s]' % expected_name
				return False
		if expected_aet is not None:
			if self.server_identification['DicomAet'] != expected_name:
				_log.error('wrong server AET, expected [%s]', expected_aet)
				self.connect_error += u'wrong server AET, expected [%s]' % expected_aet
				return False
		return True

	#--------------------------------------------------------
	def _get_server_identification(self):
		try:
			return self.__server_identification
		except AttributeError:
			pass
		system_data = self.__run_GET(url = '%s/system' % self.__server_url)
		if system_data is False:
			_log.error('unable to get server identification')
			return False
		self.__server_identification = system_data
		return self.__server_identification

	server_identification = property(_get_server_identification, lambda x:x)

	#--------------------------------------------------------
	# download API
	#--------------------------------------------------------
	def get_patients_by_external_id(self, external_id=None):
		matching_patients = []
		_log.info(u'searching for patients with external ID >>>%s<<<', external_id)
		search_data = {
			'Level': 'Patient',
			'CaseSensitive': False,
			'Expand': True,
			'Query': {'PatientID': external_id.strip(u'*')}
		}
		_log.info(u'server-side C-FIND SCU over REST search, mogrified search data: %s', search_data)
		matches = self.__run_POST(url = u'%s/tools/find' % self.__server_url, data = search_data)
		return matches

#		for pat_id in self.__run_GET(url = '%s/patients' % self.__server_url):
#			orthanc_pat = self.__run_GET(url = '%s/patients/%s' % (self.__server_url, pat_id))
#			orthanc_external_id = orthanc_pat['MainDicomTags']['PatientID']
#			if orthanc_external_id != external_id:
#				continue
#			_log.debug(u'match: %s (name=[%s], orthanc_id=[%s])', orthanc_external_id, orthanc_pat['MainDicomTags']['PatientName'], orthanc_pat['ID'])
#			matching_patients.append(orthanc_pat)
#		if len(matching_patients) == 0:
#			_log.debug(u'no matches')
#		return matching_patients

	#--------------------------------------------------------
	def get_patients_by_name(self, name_parts=None, gender=None, dob=None, fuzzy=False):
		_log.info(u'name parts %s, gender [%s], dob [%s], fuzzy: %s', name_parts, gender, dob, fuzzy)
		if len(name_parts) > 1:
			return self.get_patients_by_name_parts(name_parts = name_parts, gender = gender, dob = dob, fuzzy = fuzzy)
		if not fuzzy:
			search_term = name_parts[0].strip(u'*')
		else:
			search_term = name_parts[0]
			if not search_term.endswith(u'*'):
				search_term += u'*'
		search_data = {
			'Level': 'Patient',
			'CaseSensitive': False,
			'Expand': True,
			'Query': {'PatientName': search_term}
		}
		if gender is not None:
			gender = _map_gender_gm2dcm[gender.lower()]
			if gender is not None:
				search_data['Query']['PatientSex'] = gender
		if dob is not None:
			search_data['Query']['PatientBirthDate'] = dob.strftime('%Y%m%d')
		_log.info(u'server-side C-FIND SCU over REST search, mogrified search data: %s', search_data)
		matches = self.__run_POST(url = u'%s/tools/find' % self.__server_url, data = search_data)
		return matches

	#--------------------------------------------------------
	def get_patients_by_name_parts(self, name_parts=None, gender=None, dob=None, fuzzy=False):
		# fuzzy: allow partial/substring matches (but not across name part boundaries ',' or '^')
		matching_patients = []
		clean_parts = []
		for part in name_parts:
			if part.strip() == u'':
				continue
			clean_parts.append(part.lower().strip())
		_log.info(u'client-side patient search, scrubbed search terms: %s', clean_parts)
		for pat_id in self.__run_GET(url = '%s/patients' % self.__server_url):
			orthanc_pat = self.__run_GET(url = '%s/patients/%s' % (self.__server_url, pat_id))
			orthanc_name = orthanc_pat['MainDicomTags']['PatientName'].lower().strip()
			if not fuzzy:
				orthanc_name = orthanc_name.replace(u' ', u',').replace(u'^', u',').split(u',')
			parts_in_orthanc_name = 0
			for part in clean_parts:
				if part in orthanc_name:
					parts_in_orthanc_name += 1
			if parts_in_orthanc_name == len(clean_parts):
				_log.debug(u'name match: "%s" contains all of %s', orthanc_name, clean_parts)
				if gender is not None:
					gender = _map_gender_gm2dcm[gender.lower()]
					if gender is not None:
						if orthanc_pat['MainDicomTags']['PatientSex'].lower() != gender:
							_log.debug(u'gender mismatch: dicom=[%s] gnumed=[%s], skipping', orthanc_pat['MainDicomTags']['PatientSex'], gender)
							continue
				if dob is not None:
					if orthanc_pat['MainDicomTags']['PatientBirthDate'] != dob.strftime('%Y%m%d'):
						_log.debug(u'dob mismatch: dicom=[%s] gnumed=[%s], skipping', orthanc_pat['MainDicomTags']['PatientBirthDate'], dob)
						continue
				matching_patients.append(orthanc_pat)
			else:
				_log.debug(u'name mismatch: "%s" does not contain all of %s', orthanc_name, clean_parts)
		return matching_patients

	#--------------------------------------------------------
	def get_studies_list_by_patient_name(self, name_parts=None, gender=None, dob=None, fuzzy=False):
		return self.__get_studies_list_by_orthanc_patient_list (
			orthanc_patients = self.get_patients_by_name(name_parts = name_parts, gender = gender, dob = dob, fuzzy = fuzzy)
		)

	#--------------------------------------------------------
	def get_studies_list_by_external_id(self, external_id=None):
		return self.__get_studies_list_by_orthanc_patient_list (
			orthanc_patients = self.get_patients_by_external_id(external_id = external_id)
		)

	#--------------------------------------------------------
	def get_study_as_zip_with_dicomdir(self, study_id=None, filename=None):
		_log.info('exporting study [%s] into [%s]', study_id, filename)
		f = io.open(filename, 'wb')
		f.write(self.__run_GET(url = '%s/studies/%s/media' % (self.__server_url, study_id)))
		f.close()
		return filename

	#--------------------------------------------------------
	def get_studies_as_zip_with_dicomdir(self, study_ids=None, patient_id=None, filename=None):
		if study_ids is None:
			_log.info('exporting all studies of patient [%s] into [%s]', patient_id, filename)
			f = io.open(filename, 'wb')
			f.write(self.__run_GET(url = '%s/patients/%s/media' % (self.__server_url, patient_id)))
			f.close()
			return filename

		return u'get range of studies as zip with dicomdir not implemented, either all or one'

	#--------------------------------------------------------
	# on-server API
	#--------------------------------------------------------
	def modify_patient_id(self, old_patient_id, new_patient_id):
		pass

	#--------------------------------------------------------
	# upload API
	#--------------------------------------------------------
	def upload_dicom_files(self, files=None):
		pass

	#--------------------------------------------------------
	def upload_from_directory(self, directory=None, search_subdirectories=False):
		pass

	#--------------------------------------------------------
	def upload_with_DICOMDIR(self, DICOMDIR=None):
		pass

	#--------------------------------------------------------
	# helper functions
	#--------------------------------------------------------
	def __get_studies_list_by_orthanc_patient_list(self, orthanc_patients=None):
		studies_by_patient = []
		for pat in orthanc_patients:
			pat_dict = {
				'orthanc_id': pat['ID'],
				'name': pat['MainDicomTags']['PatientName'],
				'date_of_birth': pat['MainDicomTags']['PatientBirthDate'],
				'gender': pat['MainDicomTags']['PatientSex'],
				'external_id': pat['MainDicomTags']['PatientID'],
				'studies': []
			}
			studies_by_patient.append(pat_dict)
			o_studies = self.__run_GET(url = u'%s/patients/%s/studies' % (self.__server_url, pat['ID']))
			for o_study in o_studies:
				study_dict = {
					'orthanc_id': o_study['ID'],
					'date': o_study['MainDicomTags'][u'StudyDate'],
					'time': o_study['MainDicomTags'][u'StudyTime'],
					'series': []
				}
				try:
					study_dict['description'] = o_study['MainDicomTags'][u'StudyDescription']
				except KeyError:
					study_dict['description'] = None
				pat_dict['studies'].append(study_dict)
				for o_series_id in o_study['Series']:
					o_series = self.__run_GET(url = u'%s/series/%s' % (self.__server_url, o_series_id))
					series_dict = {
						'orthanc_id': o_series['ID'],
						'date': o_series['MainDicomTags']['SeriesDate'],
						'time': o_series['MainDicomTags']['SeriesTime'],
						'modality': o_series['MainDicomTags']['Modality'],
						'instances': len(o_series['Instances'])
					}
					try:
						series_dict['body_part'] = o_series['MainDicomTags']['BodyPartExamined']
					except KeyError:
						series_dict['body_part'] = None
					study_dict['series'].append(series_dict)
		return studies_by_patient

	#--------------------------------------------------------
	def __run_GET(self, url=None, data=None):
		if data is None:
			data = {}
		params = u''
		if len(data.keys()) > 0:
			params = u'?' + urlencode(data)
		full_url = url + params
		try:
			response, content = self.__conn.request(full_url, 'GET')
		except httplib.ResponseNotReady:
			_log.exception('cannot GET: %s', full_url)
			return False
		if not (response.status in [ 200 ]):
			_log.error('cannot GET: %s', full_url)
			_log.error('response: %s', response)
			return False
		try:
			return json.loads(content)
		except:
			return content

	#--------------------------------------------------------
	def __run_POST(self, url=None, data=None, contentType=u''):
		if isinstance(data, str):
			body = data
			if len(contentType) != 0:
				headers = { 'content-type' : contentType }
			else:
				headers = { 'content-type' : 'text/plain' }
		else:
			body = json.dumps(data)
			headers = { 'content-type' : 'application/json' }
		try:
			response, content = self.__conn.request(url, 'POST', body = body, headers = headers)
		except httplib.ResponseNotReady:
			_log.exception('cannot POST: %s', full_url)
			return False
		if response.status == 404:
			_log.debug('no data, response: %s', response)
			return []
		if not (response.status in [ 200, 302 ]):
			_log.error('cannot POST: %s', url)
			_log.error('response: %s', response)
			return False
		try:
			return json.loads(content)
		except:
			return content

#============================================================
# orthanc RestToolBox.py (for reference, not in use):
#============================================================
_credentials = None

def SetCredentials(username, password):
    global _credentials
    _credentials = (username, password)

def _SetupCredentials(h):
    global _credentials
    if _credentials != None:
        h.add_credentials(_credentials[0], _credentials[1])

def DoGet(uri, data = {}, interpretAsJson = True):
    d = ''
    if len(data.keys()) > 0:
        d = '?' + urlencode(data)

    h = httplib2.Http()
    _SetupCredentials(h)
    resp, content = h.request(uri + d, 'GET')
    if not (resp.status in [ 200 ]):
        raise Exception(resp.status)
    elif not interpretAsJson:
        return content
    else:
        try:
            return json.loads(content)
        except:
            return content


def _DoPutOrPost(uri, method, data, contentType):
    h = httplib2.Http()
    _SetupCredentials(h)

    if isinstance(data, str):
        body = data
        if len(contentType) != 0:
            headers = { 'content-type' : contentType }
        else:
            headers = { 'content-type' : 'text/plain' }
    else:
        body = json.dumps(data)
        headers = { 'content-type' : 'application/json' }
    
    resp, content = h.request(
        uri, method,
        body = body,
        headers = headers)

    if not (resp.status in [ 200, 302 ]):
        raise Exception(resp.status)
    else:
        try:
            return json.loads(content)
        except:
            return content


def DoDelete(uri):
    h = httplib2.Http()
    _SetupCredentials(h)
    resp, content = h.request(uri, 'DELETE')

    if not (resp.status in [ 200 ]):
        raise Exception(resp.status)
    else:
        try:
            return json.loads(content)
        except:
            return content


def DoPut(uri, data = {}, contentType = ''):
    return _DoPutOrPost(uri, 'PUT', data, contentType)


def DoPost(uri, data = {}, contentType = ''):
    return _DoPutOrPost(uri, 'POST', data, contentType)

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) == 1:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	if __name__ == '__main__':
		sys.path.insert(0, '../../')
	from Gnumed.pycommon import gmTools
	from Gnumed.pycommon import gmLog2

	#--------------------------------------------------------
	def orthanc_console(server_url):
		orthanc = cORTHANCServer()
		if not orthanc.connect(url = server_url, user = None, password = None):		#, expected_aet = 'another AET'
			print('error connecting to server:', orthanc.connect_error)
			return False
		print('Connected to ORTHANC server "%s" (AET [%s] - version [%s] - DB [%s])' % (
			orthanc.server_identification['Name'],
			orthanc.server_identification['DicomAet'],
			orthanc.server_identification['Version'],
			orthanc.server_identification['DatabaseVersion']
		))
		print('')
		print('Please enter patient name parts, separated by SPACE.')

		while True:
			entered_name = gmTools.prompted_input(prompt = "\nEnter person search term or leave blank to exit")
			if entered_name in ['exit', 'quit', 'bye', None]:
				print("user cancelled patient search")
				break

			pats = orthanc.get_patients_by_external_id(external_id = entered_name)
			if len(pats) > 0:
				for pat in pats:
					print(pat)
				continue

			pats = orthanc.get_studies_list_by_patient_name(name_parts = entered_name.split(), fuzzy = True)
			for pat in pats:
				print(pat['name'])
				for study in pat['studies']:
					print(u' ', gmTools.format_dict_like(study, relevant_keys = ['orthanc_id', 'date', 'time'], template = u'study [%%(orthanc_id)s] at %%(date)s %%(time)s contains %s series' % len(study['series'])))
					for series in study['series']:
						print(u'  ', gmTools.format_dict_like(series, relevant_keys = ['orthanc_id', 'date', 'time', 'modality', 'instances', 'body_part'], template = u'series [%(orthanc_id)s] at %(date)s %(time)s: %(modality)s of body part "%(body_part)s" holds %(instances)s images'))
				#print(orthanc.get_study_as_zip_with_dicomdir(study_id = study['orthanc_id'], filename = 'study_%s.zip' % study['orthanc_id']))
				#print(orthanc.get_studies_as_zip_with_dicomdir(patient_id = pat['orthanc_id'], filename = 'studies_of_%s.zip' % pat['orthanc_id']))
				print(u'--------')

	#--------------------------------------------------------
	try:
		server_url = sys.argv[2]
	except IndexError:
		server_url = u'http://localhost:8042'
	orthanc_console(server_url)
