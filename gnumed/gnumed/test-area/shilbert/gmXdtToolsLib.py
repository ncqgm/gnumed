"""GnuMed XDT data handling library.

This lib provides functions for working with XDT-files.

MERGE INTO business/gmXdtObjects.py !!
"""
#=====================================================================
__version__ = "$Revision: 1.9 $"
__author__ = "S.Hilbert, K.Hilbert"
__license__ = "GPL"

import fileinput,string,tempfile,time,os,sys,linecache,md5
import gmLog
_log = gmLog.gmDefLog

#=====================================================================
def xdt_get_pats(aFile):
	pat_ids = []
	pat_names = []
	pats = {}
	# xDT line format: aaabbbbcccccccccccCRLF where aaa = length, bbbb = record type, cccc... = content
	# read patient dat
	for line in fileinput.input(aFile):
		# remove trailing CR and/or LF
		line = string.replace(line,'\015','')
		line = string.replace(line,'\012','')
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
#=====================================================================
def get_pat_data(aFile,ID,name,patdir = None ,patlst = None ):
	_log.Log(gmLog.lData, "looking for patient: %s" % ID+':'+name)
	# return list of filenames for selected patient
	data = [patdir,patlst.get(aGroup=ID+':'+name,anOption="files")]
	_log.Log(gmLog.lData, "data: %s" % data)
	return data
#=====================================================================
def split_xdt_file(aFile,patlst,cfg):
	content=[]
	lineno = []

	# xDT line format: aaabbbbcccccccccccCRLF where aaa = length, bbbb = record type, cccc... = content

	content = []
	record_start_lines = []

	# find record starts
	for line in fileinput.input(aFile):
		strippedline = string.replace(line,'\015','')
		strippedline = string.replace(strippedline,'\012','')
		# do we care about this line ? (records start with 8000)
		if strippedline[3:7] == '8000':
			record_start_lines.append(fileinput.filelineno())

	# loop over patient records
	for aline in record_start_lines:
		# WHY +2 ?!? 
		line = linecache.getline(aFile,aline+2)	
		# remove trailing CR and/or LF
		strippedline = string.replace(line,'\015','')
		strippedline = string.replace(strippedline,'\012','')
		# do we care about this line ?
		field = strippedline[3:7]
		# extract patient id
		if field == '3000':	
			ID = strippedline[7:]
			line = linecache.getline(aFile,aline+3)
			# remove trailing CR and/or LF
			strippedline = string.replace(line,'\015','')
			strippedline = string.replace(strippedline,'\012','')
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
			#_log.Log(gmLog.lData, "hashes %s"%hashes )
			# is this new content ?
			ahash = data2md5(content)
			if ahash not in hashes:
				pat_dir = cfg.get("xdt-viewer", "export-dir")
				file_lst = write_xdt_pat_data(content, pat_dir)
				content = [] 
				add_file_to_patlst(ID,name,patlst,file_lst,ahash)
			else:
				#_log.Log(gmLog.lData, "hashes match, not adding file %s"%ahash)
				content = []
			
		else:
			continue
	# cleanup
	fileinput.close()
	patlst.store()
	return 1
#=====================================================================	
def data2md5(content):
	data_hash = md5.new()
	map(data_hash.update, content)
#	for element in content:
#		ahash.update(element)
	return data_hash.hexdigest()
#=====================================================================
def get_rand_fname(aDir):
	# set up temp file environment for creating unique random directory
	tempfile.tempdir = aDir
	tempfile.template = ""
	# create temp filename
	tmpname = tempfile.mktemp(suffix = time.strftime(".%Y%m%d-%H%M%S", time.localtime()))
	# extract name for dir
	path, fname = os.path.split(tmpname)
	return fname
#=====================================================================
def write_xdt_pat_data(data, aDir):
	"""write record for this patient to new file"""
	pat_file = open(os.path.join(aDir, get_rand_fname(aDir)), "w")
	map(pat_file.write, data)
	pat_file.close()
	return fname
#=====================================================================
def check_for_previous_records(ID,name,patlst):
	anIdentity = str(ID)+':'+str(name)
	hashes = []
	# patient already in list ?
	if anIdentity in patlst.getGroups():
		_log.Log(gmLog.lData, "identity already in list")
		files = patlst.get(aGroup=anIdentity,anOption="files")
		#file already in list ?
		for line in files:
			file,ahash=string.split(line,':')
			hashes.append(ahash)
	else:
		# no, we will add him/her then 
		_log.Log(gmLog.lData, "identity not yet in list" )
		patlst.set(aGroup = anIdentity, anOption = 'files', aValue = [], aComment = '')
	return hashes
#=====================================================================
def add_file_to_patlst(ID,name,patlst,file_lst,ahash):
	anIdentity = str(ID)+':'+str(name)
	#_patlst = patlst
	files = patlst.get(aGroup=anIdentity,anOption="files")
	#_log.Log(gmLog.lData, "files already there : %s" %files )
	for file in file_lst:
		files.append(file + ':' + ahash)
		_log.Log(gmLog.lData, "files now there : %s" %files )
	patlst.set(aGroup=anIdentity,anOption="files",aValue = files, aComment="")
#=====================================================================
# $Log: gmXdtToolsLib.py,v $
# Revision 1.9  2003-08-24 11:58:50  ncq
# - more renaming
#
# Revision 1.8  2003/08/24 10:19:21  shilbert
# - does not dump to file any more if content exist in file from previous sessions
#
# Revision 1.7  2003/08/23 16:32:42  ncq
# - removed some extraneous assignments
#
# Revision 1.6  2003/08/23 13:20:34  shilbert
# - freed the lib from gmCfg dependency as proposed by ncq
#
# Revision 1.5  2003/08/21 21:38:11  shilbert
# - make it work again after heavy refactoring by ncq
#
# Revision 1.4  2003/08/20 22:57:11  shilbert
# - removed junk comments
# - basically cleanup
#
# Revision 1.3  2003/08/20 22:53:21  shilbert
# - better patient record detection routine
# - fixed some obvious bugs
#
# Revision 1.2  2003/08/18 23:34:28  ncq
# - cleanup, somewhat restructured to show better way of going about things
#
# Revision 1.1  2003/08/18 20:34:57  shilbert
# - provides fuctions for splitting xdt-files into individual records
#.
