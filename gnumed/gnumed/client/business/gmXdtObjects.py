"""GNUmed German XDT parsing objects.

This encapsulates some of the XDT data into
objects for easy access.
"""
#==============================================================
__version__ = "$Revision: 1.33 $"
__author__ = "K.Hilbert, S.Hilbert"
__license__ = "GPL"

import os.path, sys, linecache, io, re as regex, time, datetime as pyDT, logging, io


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDateTime, gmTools
from Gnumed.business import gmXdtMappings, gmPerson


_log = logging.getLogger('gm.xdt')
_log.info(__version__)

#==============================================================
class cDTO_xdt_person(gmPerson.cDTO_person):

	def store(self):
		pass
#==============================================================
def determine_xdt_encoding(filename=None, default_encoding=None):

	f = io.open(filename, mode = 'rt', encoding = 'utf8', errors = 'ignore')

	file_encoding = None
	for line in f:
		field = line[3:7]
		if field in gmXdtMappings._charset_fields:
			_log.debug('found charset field [%s] in <%s>', field, filename)
			val = line[7:8]
			file_encoding = gmXdtMappings._map_field2charset[field][val]
			_log.debug('encoding in file is "%s" (%s)', file_encoding, val)
			break
	f.close()

	if file_encoding is None:
		_log.debug('no encoding found in <%s>, assuming [%s]', filename, default_encoding)
		return default_encoding

	return file_encoding
#==============================================================
def read_person_from_xdt(filename=None, encoding=None, dob_format=None):

	_map_id2name = {
		'3101': 'lastnames',
		'3102': 'firstnames',
		'3103': 'dob',
		'3110': 'gender',
		'3106': 'zipurb',
		'3107': 'street',
		'3112': 'zip',
		'3113': 'urb',
		'8316': 'source'
	}

	needed_fields = (
		'3101',
		'3102'
	)

	interesting_fields = list(_map_id2name)

	data = {}

	# try to find encoding if not given
	if encoding is None:
		encoding = determine_xdt_encoding(filename=filename)

	xdt_file = io.open(filename, mode = 'rt', encoding = encoding)

	for line in xdt_file:

#		# can't use more than what's interesting ... ;-)
#		if len(data) == len(interesting_fields):
#			break

		line = line.replace('\015','')
		line = line.replace('\012','')

		# xDT line format: aaabbbbcccccccccccCRLF where aaa = length, bbbb = record type, cccc... = content
		field = line[3:7]
		# do we care about this line ?
		if field in interesting_fields:
			try:
				already_seen = data[_map_id2name[field]]
				break
			except KeyError:
				data[_map_id2name[field]] = line[7:]

	xdt_file.close()

	# found enough data ?
	if len(data) < len(needed_fields):
		raise ValueError('insufficient patient data in XDT file [%s], found only: %s' % (filename, data))

	from Gnumed.business import gmPerson
	dto = gmPerson.cDTO_person()

	dto.firstnames = data['firstnames']
	dto.lastnames = data['lastnames']

	# CAVE: different data orders are possible, so configuration may be needed
	# FIXME: detect xDT version and use default from the standard when dob_format is None
	try:
		dob = time.strptime(data['dob'], gmTools.coalesce(dob_format, '%d%m%Y'))
		dto.dob = pyDT.datetime(dob.tm_year, dob.tm_mon, dob.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)
	except KeyError:
		dto.dob = None

	try:
		dto.gender = gmXdtMappings.map_gender_xdt2gm[data['gender'].lower()]
	except KeyError:
		dto.gender = None

	dto.zip = None
	try:
		dto.zip = regex.match('\d{5}', data['zipurb']).group()
	except KeyError: pass
	try:
		dto.zip = data['zip']
	except KeyError: pass

	dto.urb = None
	try:
		dto.urb = regex.sub('\d{5} ', '', data['zipurb'])
	except KeyError: pass
	try:
		dto.urb = data['urb']
	except KeyError: pass

	try:
		dto.street = data['street']
	except KeyError:
		dto.street = None

	try:
		dto.source = data['source']
	except KeyError:
		dto.source = None

	return dto
#==============================================================
class cLDTFile(object):

	def __init__(self, filename=None, encoding=None, override_encoding=False):

		file_encoding = determine_xdt_encoding(filename=filename)
		if file_encoding is None:
			_log.warning('LDT file <%s> does not specify encoding', filename)
			if encoding is None:
				raise ValueError('no encoding specified in file <%s> or method call' % filename)

		if override_encoding:
			if encoding is None:
				raise ValueError('no encoding specified in method call for overriding encoding in file <%s>' % filename)
			self.encoding = encoding
		else:
			if file_encoding is None:
				self.encoding = encoding
			else:
				self.encoding = file_encoding

		self.filename = filename

		self.__header = None
		self.__tail = None
	#----------------------------------------------------------
	def _get_header(self):

		if self.__header is not None:
			return self.__header

		ldt_file = io.open(self.filename, mode = 'rt', encoding = self.encoding)
		self.__header = []
		for line in ldt_file:
			length, field, content = line[:3], line[3:7], line[7:].replace('\015','').replace('\012','')
			# loop until found first LG-Bericht
			if field == '8000':
				if content in ['8202']:
					break
			self.__header.append(line)

		ldt_file.close()
		return self.__header

	header = property(_get_header, lambda x:x)
	#----------------------------------------------------------
	def _get_tail(self):

		if self.__tail is not None:
			return self.__tail

		ldt_file = io.open(self.filename, mode = 'rt', encoding = self.encoding)
		self.__tail = []
		in_tail = False
		for line in ldt_file:
			if in_tail:
				self.__tail.append(line)
				continue

			length, field, content = line[:3], line[3:7], line[7:].replace('\015','').replace('\012','')

			# loop until found tail
			if field == '8000':
				if content not in ['8221']:
					continue
				in_tail = True
				self.__tail.append(line)

		ldt_file.close()
		return self.__tail

	tail = property(_get_tail, lambda x:x)
	#----------------------------------------------------------
	def split_by_patient(self, dir=None, file=None):

		ldt_file = io.open(self.filename, mode = 'rt', encoding = self.encoding)
		out_file = None

		in_patient = False
		for line in ldt_file:

			if in_patient:
				out_file.write(line)
				continue

			length, field, content = line[:3], line[3:7], line[7:].replace('\015','').replace('\012','')

			# start of record
			if field == '8000':
				# start of LG-Bericht
				if content == '8202':
					in_patient = True
					if out_file is not None:
						out_file.write(''.join(self.tail))
						out_file.close()
					#out_file = io.open(filename=filename_xxxx, mode=xxxx_'rU', encoding=self.encoding)
					out_file.write(''.join(self.header))
				else:
					in_patient = False
					if out_file is not None:
						out_file.write(''.join(self.tail))
						out_file.close()

		if out_file is not None:
			if not out_file.closed:
				out_file.write(''.join(self.tail))
				out_file.close()

		ldt_file.close()
#==============================================================
# FIXME: the following *should* get wrapped in class XdtFile ...
#--------------------------------------------------------------
def xdt_get_pats(aFile):
	pat_ids = []
	pat_names = []
	pats = {}
	# xDT line format: aaabbbbcccccccccccCRLF where aaa = length, bbbb = record type, cccc... = content
	# read patient dat
	for line in fileinput.input(aFile):
		# remove trailing CR and/or LF
		line = line.replace('\015','')
		line = line.replace('\012','')
		# do we care about this line ?
		field = line[3:7]
		# yes, if type = patient id
		if field == '3000':
			pat_id = line[7:]
			if pat_id not in pat_ids:
				pat_ids.append(pat_id)
			continue
		# yes, if type = patient name
		if field == '3101':
			pat_name = line [7:]
			if pat_name not in pat_names:
				pat_names.append(pat_name)
				pats[pat_id] = pat_name
			continue
	fileinput.close()

	_log.debug("patients found: %s" % len(pat_ids))
	return pats
#==============================================================
def get_pat_files(aFile, ID, name, patdir = None, patlst = None):
	_log.debug("getting files for patient [%s:%s]" % (ID, name))
	files = patlst.get(aGroup = "%s:%s" % (ID, name), anOption = "files")
	_log.debug("%s => %s" % (patdir, files))
	return [patdir, files]
#==============================================================
def split_xdt_file(aFile,patlst,cfg):
	content=[]
	lineno = []

	# xDT line format: aaabbbbcccccccccccCRLF where aaa = length, bbbb = record type, cccc... = content

	content = []
	record_start_lines = []

	# find record starts
	for line in fileinput.input(aFile):
		strippedline = line.replace('\015','')
		strippedline = strippedline.replace('\012','')
		# do we care about this line ? (records start with 8000)
		if strippedline[3:7] == '8000':
			record_start_lines.append(fileinput.filelineno())

	# loop over patient records
	for aline in record_start_lines:
		# WHY +2 ?!? 
		line = linecache.getline(aFile,aline+2) 
		# remove trailing CR and/or LF
		strippedline = line.replace('\015','')
		strippedline = strippedline.replace('\012','')
		# do we care about this line ?
		field = strippedline[3:7]
		# extract patient id
		if field == '3000': 
			ID = strippedline[7:]
			line = linecache.getline(aFile,aline+3)
			# remove trailing CR and/or LF
			strippedline = line.replace('\015','')
			strippedline = strippedline.replace('\012','')
			# do we care about this line ?
			field = strippedline[3:7]
			if field == '3101':
				name = strippedline [7:]
			startline=aline
			endline=record_start_lines[record_start_lines.index(aline)+1]
			_log.debug("reading from%s" %str(startline)+' '+str(endline) )
			for tmp in range(startline,endline):							
				content.append(linecache.getline(aFile,tmp))
				_log.debug("reading %s"%tmp )
			hashes = check_for_previous_records(ID,name,patlst)
			# is this new content ?
			data_hash = md5.new()			# FIXME: use hashlib
			map(data_hash.update, content)
			digest = data_hash.hexdigest()
			if digest not in hashes:
				pat_dir = cfg.get("xdt-viewer", "export-dir")
				file = write_xdt_pat_data(content, pat_dir)
				add_file_to_patlst(ID, name, patlst, file, ahash)
			content = []
		else:
			continue
	# cleanup
	fileinput.close()
	patlst.store()
	return 1
#==============================================================
def get_rand_fname(aDir):
	tmpname = gmTools.get_unique_filename(prefix='', suffix = time.strftime(".%Y%m%d-%H%M%S", time.localtime()), tmp_dir=aDir)
	path, fname = os.path.split(tmpname)
	return fname
#==============================================================
def write_xdt_pat_data(data, aDir):
	"""write record for this patient to new file"""
	pat_file = io.open(os.path.join(aDir, get_rand_fname(aDir)), mode = "wt", encoding = 'utf8')
	map(pat_file.write, data)
	pat_file.close()
	return fname
#==============================================================
def check_for_previous_records(ID, name, patlst):
	anIdentity = "%s:%s" % (ID, name)
	hashes = []
	# patient not listed yet
	if anIdentity not in patlst.getGroups():
		_log.debug("identity not yet in list" )
		patlst.set(aGroup = anIdentity, anOption = 'files', aValue = [], aComment = '')
	# file already listed ?
	file_defs = patlst.get(aGroup = anIdentity, anOption = "files")
	for line in file_defs:
		file, ahash = line.split(':')
		hashes.append(ahash)

	return hashes
#==============================================================
def add_file_to_patlst(ID, name, patlst, new_file, ahash):
	anIdentity = "%s:%s" % (ID, name)
	files = patlst.get(aGroup = anIdentity, anOption = "files")
	for file in new_files:
		files.append("%s:%s" % (file, ahash))
	_log.debug("files now there : %s" % files)
	patlst.set(aGroup=anIdentity, anOption="files", aValue = files, aComment="")
#==============================================================
# main
#--------------------------------------------------------------
if __name__ == "__main__":
	from Gnumed.pycommon import gmI18N, gmLog2

	root_log = logging.getLogger()
	root_log.setLevel(logging.DEBUG)
	_log = logging.getLogger('gm.xdt')

	#from Gnumed.business import gmPerson
	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

	ldt = cLDTFile(filename = sys.argv[1])
	print("header:")
	for line in ldt.header:
		print(line.encode('utf8', 'replace'))
	print("tail:")
	for line in ldt.tail:
		print(line.encode('utf8', 'replace'))

#	# test framework if run by itself
#	patfile = sys.argv[1]
#	dobformat = sys.argv[2]
#	encoding = sys.argv[3]
#	print "reading patient data from xDT file [%s]" % patfile

#	dto = read_person_from_xdt(patfile, dob_format=dobformat, encoding=encoding)
#	print "DTO:", dto
#	print "dto.dob:", dto.dob, type(dto.dob)
#	print "dto.dob.tz:", dto.dob.tzinfo
#	print "dto.zip: %s dto.urb: %s" % (dto.zip, dto.urb)
#	print "dto.street", dto.street
#	searcher = gmPersonSearch.cPatientSearcher_SQL()
#	ident = searcher.get_identities(dto=dto)[0]
#	print ident
##	print ident.get_medical_age()

#==============================================================
