"""GnuMed XDT data handling library.

This lib provides fuctions for working with XDT-files.
"""
#==============================================================
__version__ = "$Revision: 1.1 $"
__author__ = "S.Hilbert, K.Hilbert"
__license__ = "GPL"

import fileinput,string,tempfile,time,os,sys
import gmLog, gmCfg
_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile

#get export-dir
pat_dir=_cfg.get("xdt-viewer", "export-dir")
pat_lst_fname=_cfg.get("xdt-viewer", "patient-list")
# is there a patient list already ?
_patlst = gmCfg.cCfgFile(aPath = pat_dir ,aFile = pat_lst_fname, flags = 2)
#==============================================================

def getXdtStats(aFile):
	xDTFile = fileinput.input(aFile)
	patientIDList = []
	patientNameList = []
	patientIdentity = {}
	# read patient data
	patients_found = 0
	# xDT line format: aaabbbbcccccccccccCRLF where aaa = length, bbbb = record type, cccc... = content
	for line in xDTFile:
		# remove trailing CR and/or LF
		line = string.replace(line,'\015','')
		line = string.replace(line,'\012','')
		
		# do we care about this line ?
		field = line[3:7]
		# extract patient id
		if field == '3000':
			apatientID = line[7:]
			if apatientID not in patientIDList:
				patientIDList.append(apatientID)
				patients_found = patients_found + 1
		# extract patient name
		elif field == '3101':
			apatientName = line [7:]
			if apatientName not in patientNameList:
				patientNameList.append(apatientName)
				patientIdentity[apatientID]=apatientName					
	_log.Log(gmLog.lData, "patients found: %s" % patients_found)
	return patientIdentity
	# cleanup
	fileinput.close()

#=================================================================
def getPatientContent(aFile,anIdentity):
	_log.Log(gmLog.lData, "looking for patient: %s" % anIdentity)
	split2singleRecords(aFile,anIdentity)
	_patlst.store()
#==================================================================	
def split2singleRecords(aFile,anIdentity):
	idflag=''
	nameflag=''
	content=[]	
	Identity=string.split(anIdentity,':')
	anID=Identity[0]
	aName=Identity[1]
	xDTFile = fileinput.input(aFile)
	#patientIDList = []
	#patientNameList = []
	# xDT line format: aaabbbbcccccccccccCRLF where aaa = length, bbbb = record type, cccc... = content
	for line in xDTFile:
		# remove trailing CR and/or LF
		strippedline = string.replace(line,'\015','')
		strippedline = string.replace(strippedline,'\012','')
		# do we care about this line ?
		field = strippedline[3:7]
		# extract patient id
		if field == '3000':
			if len(content)== 0:	
				apatientID = strippedline[7:]
				if apatientID == anID:
					idflag = 'true'
					#_log.Log(gmLog.lData, "id flags true")
					# memorize this line
				else:
					idflag = 'false'
					#_log.Log(gmLog.lData, "id flags false")	
					#patientIDList.append(apatientID)
					#patients_found = patients_found + 1
					# extract patient name
			else:
				# ahh , there list 'content' is not empty
				dump2individualFile(anIdentity,content)
				_log.Log(gmLog.lData, "dumped content to new file")
				# now we need to empty it before next record starts
				content=[]
		if field == '3101' and idflag == 'true':
			apatientName = strippedline [7:]
			if apatientName == aName:
				nameflag = 'true'
				_log.Log(gmLog.lData, "both flags true")
			else: 
				nameflag = 'false'
				_log.Log(gmLog.lData, "name flag false")
		# both flags set to true ? lets add the line then
		if idflag and nameflag == 'true':
			content.append(line)		
			
	
			#if apatientName not in patientNameList:
			#	patientNameList.append(apatientName)					
	#_log.Log(gmLog.lData, "patients found: %s" % patients_found)
	#return patientNameList
	# cleanup
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
def dump2individualFile(anIdentity,content):
	# write record for this patient to new file
	pat_dir=_cfg.get("xdt-viewer", "export-dir")
	# create unique filname
	fname = get_random_ID(aDir=pat_dir)
	pat_fname = os.path.join(pat_dir,fname)
	# open the file
	pat_file = open(pat_fname, "w")
	map(pat_file.write, content)
	# done
	pat_file.close()
	# file has been written , we need to add it to the patient list
	aRecord = fname
	check_for_previous_records(anIdentity,aRecord)
#=====================================================================
def check_for_previous_records(anIdentity,aRecord):
	
	try:
		# patient already in list ?
		if anIdentity in _patlst.getGroups():
			_log.Log(gmLog.lData, "identity already in list" )
			
		else:
			# no, we will add him/her then 
			_log.Log(gmLog.lData, "identity not yet in list" )
			_patlst.set(aGroup=anIdentity,aComment="list of filenames for patient's records")
			print 'ouch'
		# update list of records for this patient
		_patlst.set(aGroup=anIdentity,anOption="files",aValue = aRecord, aComment="list of filenames for patient's records")
	except:
		#_log.LogException('Cannot read records for selected patient from patient list: [%s].' %pat_lst_fname, sys.exc_info())
		#__show_error(
		#	aMessage = _('Cannot load record from patient list\n[%s].') %pat_lst_fname,
		#	aTitle = _('loading record from patient list')
		#)
		return None
	
	#_log.Log(gmLog.lData, _patlst )
	return None
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
# Revision 1.1  2003-08-18 20:34:57  shilbert
# - provides fuctions for splitting xdt-files into individual records
#.
