"""GNUmed German XDT parsing objects.

This encapsulates some of the XDT data into
objects for easy access.
"""
#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmXdtObjects.py,v $
# $Id: gmXdtObjects.py,v 1.23 2007-01-16 13:43:10 ncq Exp $
__version__ = "$Revision: 1.23 $"
__author__ = "K.Hilbert, S.Hilbert"
__license__ = "GPL"

import os.path, sys, md5, linecache, codecs, re as regex, time, datetime as pyDT

import mx.DateTime as mxDT

if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmLog, gmDateTime
from Gnumed.business import gmXdtMappings

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
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
		'3113': 'urb'
	}
	needed_fields = (
		'3101',
		'3102',
		'3103'
	)
	interesting_fields = needed_fields + (
		'3110',
		'3106',
		'3107',
		'3112',
		'3113'
	)

	data = {}

	# try to find encoding if not given
	if encoding is None:
		f = codecs.open(filename=filename, mode='rU', encoding='utf8', errors='ignore')
		for line in f:
			field = line[3:7]
			if field in gmXdtMappings._charset_fields:
				val = line[7:8]
				encoding = gmXdtMappings._map_field2charset[field][val]
		f.close()

	xdt_file = codecs.open(filename=filename, mode='rU', encoding=encoding)

	# xDT line format: aaabbbbcccccccccccCRLF where aaa = length, bbbb = record type, cccc... = content
	for line in xdt_file:

		if len(data) == len(interesting_fields):
			break

		line = line.replace('\015','')
		line = line.replace('\012','')

		# do we care about this line ?
		field = line[3:7]
		if field in interesting_fields:
			data[_map_id2name[field]] = line[7:]

	xdt_file.close()

	# found enough data ?
	if len(data) < len(needed_fields):
		raise ValueError('insufficient patient data in XDT file [%s], found only: %s' % (filename, data))

	from Gnumed.business import gmPerson
	dto = gmPerson.cDTO_person()

	dto.firstnames = data['firstnames']
	dto.lastnames = data['lastnames']

	# FIXME: different data orders are possible
	dob = time.strptime(data['dob'], dob_format)
	dto.dob = pyDT.datetime(dob.tm_year, dob.tm_mon, dob.tm_mday, tzinfo = gmDateTime.gmCurrentLocalTimezone)

	try:
		dto.gender = gmXdtMappings.map_gender_xdt2gm[data['gender'].lower()]
	except:
		dto.gender = None

	dto.zip = None
	try:
		dto.zip = regex.match('\d{5}', data['zipurb']).group()
	except: pass
	try:
		dto.zip = data['zip']
	except: pass

	dto.urb = None
	try:
		dto.urb = regex.sub('\d{5} ', '', data['zipurb'])
	except: pass
	try:
		dto.urb = data['urb']
	except: pass

	try:
		dto.street = data['street']
	except:
		dto.street = None

	return dto
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

	_log.Log(gmLog.lData, "patients found: %s" % len(pat_ids))
	return pats
#==============================================================
def get_pat_files(aFile, ID, name, patdir = None, patlst = None):
	_log.Log(gmLog.lData, "getting files for patient [%s:%s]" % (ID, name))
	files = patlst.get(aGroup = "%s:%s" % (ID, name), anOption = "files")
	_log.Log(gmLog.lData, "%s => %s" % (patdir, files))
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
			_log.Log(gmLog.lData, "reading from%s" %str(startline)+' '+str(endline) )
			for tmp in range(startline,endline):							
				content.append(linecache.getline(aFile,tmp))
				_log.Log(gmLog.lData, "reading %s"%tmp )
			hashes = check_for_previous_records(ID,name,patlst)
			# is this new content ?
			data_hash = md5.new()
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
	import time, tempfile
	# set up temp file environment for creating unique random directory
	tempfile.tempdir = aDir
	tempfile.template = ""
	# create temp filename
	tmpname = tempfile.mktemp(suffix = time.strftime(".%Y%m%d-%H%M%S", time.localtime()))
	# extract name for dir
	path, fname = os.path.split(tmpname)
	return fname
#==============================================================
def write_xdt_pat_data(data, aDir):
	"""write record for this patient to new file"""
	pat_file = open(os.path.join(aDir, get_rand_fname(aDir)), "w")
	map(pat_file.write, data)
	pat_file.close()
	return fname
#==============================================================
def check_for_previous_records(ID, name, patlst):
	anIdentity = "%s:%s" % (ID, name)
	hashes = []
	# patient not listed yet
	if anIdentity not in patlst.getGroups():
		_log.Log(gmLog.lData, "identity not yet in list" )
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
	_log.Log(gmLog.lData, "files now there : %s" % files)
	patlst.set(aGroup=anIdentity, anOption="files", aValue = files, aComment="")
#==============================================================
# main
#--------------------------------------------------------------
if __name__ == "__main__":
	from Gnumed.pycommon import gmI18N
	from Gnumed.business import gmPerson
	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

	# test framework if run by itself
	_log.SetAllLogLevels(gmLog.lData)

	patfile = sys.argv[1]
	dobformat = sys.argv[2]
	print "reading patient data from xDT file [%s]" % patfile

	dto = read_person_from_xdt(patfile, dob_format=dobformat)
	print "DTO:", dto
	print "dto.dob:", dto.dob, type(dto.dob)
	print "dto.dob.tz:", dto.dob.tzinfo
	print "dto.zip: %s dto.urb: %s" % (dto.zip, dto.urb)
	print "dto.street", dto.street
	searcher = gmPerson.cPatientSearcher_SQL()
	print searcher.get_identities(dto=dto)

#==============================================================
# $Log: gmXdtObjects.py,v $
# Revision 1.23  2007-01-16 13:43:10  ncq
# - use gmDateTime.gmCurrentLocalTimezone for dto.dob
#
# Revision 1.22  2007/01/16 12:13:30  ncq
# - dto.dob now requires datetime.datetime
# - improve test suite
#
# Revision 1.21  2007/01/16 10:26:29  ncq
# - open xdt file in utf8 even for encoding detection since
#   it can still contain umlauts et al
# - fix zipurb vs zip + urb handling
#
# Revision 1.20  2007/01/04 23:09:38  ncq
# - support explicit DOB format in xDT files
#
# Revision 1.19  2006/12/11 18:53:43  ncq
# - make read_person_from_xdt() recognize address data
#
# Revision 1.18  2006/10/30 16:42:27  ncq
# - use more gmXdtMappings
#
# Revision 1.17  2006/10/08 10:48:28  ncq
# - teach xdt reader to derive encoding from gdt 6301 record
#
# Revision 1.16  2006/09/13 07:54:32  ncq
# - clean up imports
# - handle source encoding in read_person_from_xdt()
#
# Revision 1.15  2006/09/12 17:19:53  ncq
# - xDT files have the gender in upper or lower case, so normalize to lower
#
# Revision 1.14  2006/07/22 11:01:00  ncq
# - make gender optional
#
# Revision 1.13  2006/07/19 20:43:59  ncq
# - remove cXDTPatient
#
# Revision 1.12  2006/07/17 18:02:50  ncq
# - cleanup, improve testing
# - add read_person_from_xdt() and use gmPerson.cDTO_person()
#
# Revision 1.11  2006/07/13 21:00:32  ncq
# - cleanup gender mappings
# - streamline cXdtPatient and improve test harness
#
# Revision 1.10  2006/05/12 12:05:04  ncq
# - cleanup
#
# Revision 1.9	2004/03/20 19:45:49  ncq
# - rename gender map
#
# Revision 1.8	2004/03/18 11:05:00  shilbert
# - fixed xDT-parsing in standalone mode
#
# Revision 1.7	2004/02/25 09:46:20  ncq
# - import from pycommon now, not python-common
#
# Revision 1.6	2003/11/17 10:56:35  sjtan
#
# synced and commiting.
#
# Revision 1.1	2003/10/23 06:02:38  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.5	2003/08/28 18:54:32  shilbert
# - corrected some minor glitches
#
# Revision 1.4	2003/08/27 14:58:58  ncq
# - added helpers written by shilbert for XdtViewer
#
# Revision 1.3	2003/04/19 22:56:03  ncq
# - speed up __load_data(), better encapsulate xdt file maps
#
# Revision 1.2	2003/02/18 02:43:16  ncq
# - rearranged __getitem__ to check self.__data last
#
# Revision 1.1	2003/02/17 23:33:14  ncq
# - first version
#
