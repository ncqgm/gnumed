"""GnuMed XDT data handling library.

This lib provides functions for working with XDT-files.

MERGE INTO business/gmXdtObjects.py !!
"""
#==============================================================
__version__ = "$Revision: 1.3 $"
__author__ = "S.Hilbert, K.Hilbert"
__license__ = "GPL"

import fileinput,string,tempfile,time,os,sys,linecache
import gmLog, gmCfg
_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile

# get export-dir
pat_dir = _cfg.get("xdt-viewer", "export-dir")
pat_lst_fname = _cfg.get("xdt-viewer", "patient-list")
# is there a patient list already ?
_patlst = gmCfg.cCfgFile(aPath = pat_dir ,aFile = pat_lst_fname, flags = 2)
#==============================================================
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
#=================================================================
def get_pat_data(aFile,ID,name):
	_log.Log(gmLog.lData, "looking for patient: %s" % ID+':'+name)
	split2singleRecords(aFile,ID,name)
	_patlst.store()
	# return list of filenames for selected patient
	data = [pat_dir,_patlst.get(aGroup=ID+':'+name,anOption="files")]
	_log.Log(gmLog.lData, "data: %s" % data)
	return data
#=================================================================
def split2singleRecords(aFile,ID,name):
	idflag='false'
	nameflag='false'
	content=[]
	lineno = []
	aline = '0'
	# xDT line format: aaabbbbcccccccccccCRLF where aaa = length, bbbb = record type, cccc... = content
	for line in fileinput.input(aFile):
		# remove trailing CR and/or LF
		strippedline = string.replace(line,'\015','')
		strippedline = string.replace(strippedline,'\012','')
		# do we care about this line ?
		field = strippedline[3:7]
		# record starts with 8000
		if field == '8000':			
			curr_line=fileinput.filelineno()
			#lineno.append(aline+':'+curr_line)
			lineno.append(curr_line)	
			#curr_line=aline
			
	# is it a patient record or some other block ?	
	for aline in lineno:
		line = linecache.getline(aFile,aline+2)	
		# remove trailing CR and/or LF
		strippedline = string.replace(line,'\015','')
		strippedline = string.replace(strippedline,'\012','')
		# do we care about this line ?
		field = strippedline[3:7]
		# extract patient id
		if field == '3000':
			# clear idflag
			idflag='false' 
			#if len(content)== 0:	
			apatientID = strippedline[7:]
			if apatientID == ID:
				idflag = 'true'
				_log.Log(gmLog.lData, "id matches")
				# check the name
				line = linecache.getline(aFile,aline+3)
				# remove trailing CR and/or LF
				strippedline = string.replace(line,'\015','')
				strippedline = string.replace(strippedline,'\012','')
				# do we care about this line ?
				field = strippedline[3:7]
				if field == '3101':
					pat_name = strippedline [7:]
					if pat_name == name:
						nameflag = 'true'
						_log.Log(gmLog.lData, "name matches")
						# both match , will add all lines between two 'Satzidentifikationen' (8000)
						_log.Log(gmLog.lData, len(lineno))
						#for i in range(len(lineno)-1):
						startline=aline
						endline=lineno[lineno.index(aline)+1]
						_log.Log(gmLog.lData, "reading from%s" %str(startline)+' '+str(endline) )
						for tmp in range(startline,endline):							
								content.append(linecache.getline(aFile,tmp))
								_log.Log(gmLog.lData, "reading %s"%tmp )
						dump2individualFile(content,ID,name)
						content = []
					else:
						continue
				else:
					continue
					
			else:
				continue
		else:
			continue
			"""
				#idflag = 'false'
				_log.Log(gmLog.lData, "id flag false")	
					#pat_ids.append(apatientID)
					#patients_found = patients_found + 1
					# extract patient name
			#else:
			if len(content) != '0' and idflag == 'true' and nameflag == 'true':
				# ahh , list 'content' is not empty
				dump2individualFile(content,ID,name)
				_log.Log(gmLog.lData, "dumped content %s to new file" % content)
				# now we need to empty it before next record starts
				content=[]
		
		
				
		if field == '3101' and idflag == 'true':
			# clear nameflag
			nameflag = 'false'
			pat_name = strippedline [7:]
			if pat_name == name:
				nameflag = 'true'
				_log.Log(gmLog.lData, "both flags true")
			else: 
				#nameflag = 'false'
				_log.Log(gmLog.lData, "name flag false")
		# both flags set to true ? lets add the line then
		if idflag and nameflag == 'true':
			content.append(line)		
			
			#if pat_name not in pat_names:
			#	pat_names.append(pat_name)					
	#_log.Log(gmLog.lData, "patients found: %s" % patients_found)
	#return pat_names
	# cleanup
	"""
	fileinput.close()
#====================================================================
def get_random_ID(aDir):
	# set up temp file environment for creating unique random directory
	tempfile.tempdir = aDir
	tempfile.template = ""
	# create temp filename
	tmpname = tempfile.mktemp(suffix = time.strftime(".%Y%m%d-%H%M%S", time.localtime()))
	# extract name for dir
	path, doc_ID = os.path.split(tmpname)
	return doc_ID
#====================================================================
def dump2individualFile(content,ID,name):
	fname = []
	# write record for this patient to new file
	pat_dir=_cfg.get("xdt-viewer", "export-dir")
	# create unique filname and add it to a list
	fname.append(get_random_ID(aDir=pat_dir))
	pat_fname = os.path.join(pat_dir,fname[0])
	# open the file
	pat_file = open(pat_fname, "w")
	map(pat_file.write,content)
	# done
	pat_file.close()
	# file has been written , we need to add it to the patient list
	aRecord = fname
	check_for_previous_records(ID,name,aRecord)
#=====================================================================
def check_for_previous_records(ID,name,aRecord):
	anIdentity = str(ID)+':'+str(name)
	# patient already in list ?
	if anIdentity in _patlst.getGroups():
		_log.Log(gmLog.lData, "identity already in list" )
		files = _patlst.get(aGroup=anIdentity,anOption="files")
		_log.Log(gmLog.lData, "files already there : %s" %files )
		files.append(aRecord[0])
		_log.Log(gmLog.lData, "files now there : %s" %files )
		_patlst.set(aGroup=anIdentity,anOption="files",aValue = files, aComment="")	
	else:
		# no, we will add him/her then 
		_log.Log(gmLog.lData, "identity not yet in list" )
		#_patlst.set(aGroup=anIdentity,aComment="list of filenames for patient's records")
		print 'ouch'
		files = aRecord
		# update list of records for this patient
		_patlst.set(aGroup=anIdentity,anOption="files",aValue = files, aComment="")
	
	#except:
		#_log.LogException('Cannot read records for selected patient from patient list: [%s].' %pat_lst_fname, sys.exc_info())
		#__show_error(
		#	aMessage = _('Cannot load record from patient list\n[%s].') %pat_lst_fname,
		#	aTitle = _('loading record from patient list')
		#)
	#	return None
	
	#_log.Log(gmLog.lData, _patlst )
	return 1
#----------------------------------------
# error handling
#----------------------------------------
def __show_error(aMessage = None, aTitle = ''):
	# sanity checks
	tmp = aMessage
	if aMessage is None:
		tmp = _('programmer forgot to specify error message')

	tmp = tmp + _("\n\nPlease consult the error log for further information !")

	dlg = wxMessageDialog(
		NULL,
		tmp,
		aTitle,
		wxOK | wxICON_ERROR
	)
	dlg.ShowModal()
	dlg.Destroy()
	return 1
#==============================================================
# $Log: gmXdtToolsLib.py,v $
# Revision 1.3  2003-08-20 22:53:21  shilbert
# - better patient record detection routine
# - fixed some obvious bugs
#
# Revision 1.2  2003/08/18 23:34:28  ncq
# - cleanup, somewhat restructured to show better way of going about things
#
# Revision 1.1  2003/08/18 20:34:57  shilbert
# - provides fuctions for splitting xdt-files into individual records
#.
