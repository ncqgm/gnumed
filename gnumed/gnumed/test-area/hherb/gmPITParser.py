# This module parses PIT files
# The PIT format is an Australian quasi-standard for Pathology
# result transfer. PIT is aiming at visual representation of
# test results and is mostly useless for automatized processing.
#
# This module has a helper function to translate PIT rich text tags
# into corresponding HTML tags
# This software is free software, released under the terms of the
# GPL v2 or later license. Details see http://gnu.org/
# (c) by Dr. Horst Herb <hherb@gnumed.net>
#------------------------------------------------------------------------
# Usage:
# import gmPitParser
# pit=gmPitParser.PitParser(filename)
# result = pit.nextResult() ....
# pit.nextResult returns a single PIT formatted result (line codes 001-999)
# as a "dictionary" object (key:value pairs).
# The "key" is the report section (=line number in PIT),
# the value a list of dictionaries containing key:value pairs
#
# The example in the "__main__" section demonstrates how to access the
# parsed  pit information via Python dictionaries, and the
# "pit" dictionary at the beginning of the code lists all the key words.
#=========================================================================

__version__ = "0.1"
__author__ = "Horst Herb"

pit = {} #parsing information: line/section headers and information character positions
pit['001']=('SourceLabHeading', {'text':(5,61), 'FormatVersionNumber':(64,65), 'DateOfVersion':(67,76)})
pit['003']=('ReportRunDetail1', {'RunNumber':(24,27), 'RunDate':(40,49), 'RunTime':(61,68) })
pit['004']=('ReportRunDetail2', {'SurgeryID':(14,18), 'ReportFromDate':(30,39), 'ReportFromTime':(41,48), 'ReportToDate':(55,64), 'ReportToTime':(66,73), 'RerunIndicator': (76,81)})
pit['006']=('HospitalRunDetail', {'HospitalCode':(17,22), 'HospitalName':(32,64)})
pit['010']=('SurgeryDoctor', {'DoctorName':(5,36), 'DoctorCode':(40,45), 'ProviderNumber':(50,58)})
pit['020']=('PatientHeading', {'YourRef':(5,16), 'PatientName':(17,47), 'LabRef':(48,63), 'Test':(64,-1)})
pit['021']=('PatientDetail', {'YourRef':(5,16), 'PatientName':(17,47), 'LabRef':(48,63), 'Test':(64,-1)})
pit['100']=('PatientName', {'PatientName':(27,-1)})
pit['101']=('PatientAddress', {'AddressDetails':(27,-1)})
pit['104']=('BirthDetails', {'BirthDate':(38,48), 'AgePrefix':(57,58), 'Age':(58,60), 'Sex':(69,70)})
pit['105']=('PatientPhoneNumber', {'TelephoneNumber': (38,38+16)})
pit['110']=('SurgeryOrHospitalReference', {'ReferenceNumber' : (27, 27+16)})
pit['111']=('LabReference', {'LabReference':(5,26), 'ReferenceNumber' : (27, 27+16)})
pit['112']=('MedicareNumber', {'MedicareNumber' : (27, 27+10)})
pit['115']=('PhoneEnquiries', {'ConsultingPathologist' : (27, 27+32), 'PhoneNumber':(60, 60+12)})
pit['121']=('ReferredBy', {'DoctorName': (27,27+32)})
pit['122']=('CopyDoctor', {'DoctorName': (27,27+32)})
pit['123']=('ReceivingDoctor', {'DoctorName': (27,27+32), 'ProviderNumber':(61,8)})
pit['130']=('HospitalWard', {'Ward':(27,27+32)})
pit['131']=('AutommaticWardPrint', {'AutoWardPrint':(27,28)})
pit['201']=('SpecimenType', {'Specimen':(27,-1)})
pit['203']=('RequestDate', {'RequestDate':(27,27+10)})
pit['204']=('CollectionDate', {'CollectionDate':(27,37), 'CollectionTime':(39,44)})
pit['205']=('TestName', {'TestName':(27,-1)})
pit['206']=('ReportDateTime', {'ReportDate':(27,37), 'ReportTime':(39,44)})
pit['207']=('ConfidentialityIndicator', {'Confidential':(27,28)})
pit['208']=('TestCategory', {'TestCategory':(27,28)})
pit['210']=('NormalResultIndicator', {'Normal':(27,28)})
pit['211']=('RequestedTests', {'Tests':(27,-1)})
pit['212']=('RequestCompleteIndicator', {'Complete':(27,28)})
pit['301']=('ResultLine', {'Results':(5,-1)})
pit['311']=('CumulativeResultLine', {'Results':(5,-1)})
pit['EOR']='390'	#end of report data section
pit['EOF']='999'	#end of report

html={} #translation dictionary PIT tags -> HTML
html['SBLD'] = '<b>'
html['EBLD'] = '</b>'
html['SUND'] = '<u>'
html['EUND'] = '</u>'
html['SBLK'] = '<b>'
html['EBLK'] = '</b>'
html['FG00'] = '<span style="color: black;">'
html['FG01'] = '<span style="color: blue;">'
html['FG02'] = '<span style="color: green;">'
html['FG03'] = '<span style="color: cyan;">'
html['FG04'] = '<span style="color: red;">'
html['FG05'] = '<span style="color: magenta;">'
html['FG06'] = '<span style="color: brown;">'
html['FG07'] = '<span style="color: lightgrey;">'
html['FG08'] = '<span style="color: darkgrey;">'
html['FG09'] = '<span style="color: lightblue;">'
html['FG10'] = '<span style="color: lightgreen;">'
html['FG11'] = '<span style="color: lightcyan;">'
html['FG12'] = '<span style="color: red;">'
html['FG13'] = '<span style="color: magenta;">'
html['FG14'] = '<span style="color: yellow;">'
html['FG15'] = '<span style="color: white;">'
html['FG99'] = '</span>'
#TODO: still a few formatting codes missing (font, pitch)
#TODO: specs don't mention whether PIT allows nested formatting codes


class PitParser:
	"""parse a PIT file and return a dictionary of 'sections' (= PIT line numbers),
	containing a list of dictionaries of 'subsections' (= PIT attributes).
	Key names see 'pit' dictionary in source file"""

	def __init__(self, filename):
		"""filename is the name of the PIT formatted text
		file (incl. path if required)"""
		self. _fname = filename
		self._file = open(filename)


	def depitify(self, line):
		"""parses a single PIT formatted line and tries to
		put the information into Python dictionary format
		(key:value pairs)"""
		depitified = {}
		if (line is None) or (len(line)<1):
			return ("EOF", ())
		try:
			lineno = line[0:3]
			if lineno == pit["EOF"]: #end of report file, not necessarily of physical file
				return ("EOF", ())
			elif lineno == pit["EOR"]: #end of report
				return ("EOR", ())
			heading, info = pit[lineno] #get line heading and info re subsections from pit dictionary
			for item in info.keys(): #traverse through all subsections of that line
				frompos = int(info[item][0])-1
				topos = int(info[item][1])-1
				if topos<0:
					depitified[item] =  line[frompos:].strip()
				else:
					depitified[item] =  line[frompos:topos].strip()
			return (heading, depitified)
		except KeyError:
			return None


	def nextResult(self):
		"""Delivers the next available result from the already opened file
		Returns a dictionary of headings:[{subsections:} ...]
		or None, if no valid results found
		"""
		result = {}
		line=''
		while line is not None:
			try:
				line = self._file.readline()
				if line == '':
					return None
			except:
				return None
			depitted =  self.depitify(line)
			if depitted is None:
				continue
			elif (depitted[0] == "EOR"):
				return result
			try:
				result[depitted[0]].append(depitted[1])
			except:
				result[depitted[0]]=[depitted[1]]
		if (result == {}):
			result = None
		return result


def Pit2HTML(line):
	"""converts PIT rich text tags into HTML tags
	accepts a line of text as parameter, and returns a line of converted text.
	Will throw an exception for  unknown tags"""
	newline = line
	pos = line.find('~')
	while pos>=0:
		endpos = line.find('~', pos+1)
		if endpos < 0:
			break
		tags = line[pos+1:endpos]
		pittag = line[pos:endpos+1]
		htmltag=''
		for i in range(0, len(tags), 4):
			tag= tags[i:i+4]
			htmltag+=html[tag]
		newline = newline.replace(pittag, htmltag, 1)
		pos = line.find('~', endpos+1)
	return newline

def Result2HTML(result):
	print "<h2>Patient: %s, d.o.b.: %s</h2><hr>" % (result['PatientName'][0]['PatientName'], result['BirthDetails'][0]['BirthDate'])
	print "Requested by: %s on %s, collected %s, reported %s %s <br>" % (result['ReferredBy'][0]['DoctorName'], \
		result['RequestDate'][0]['RequestDate'], \
		result['CollectionDate'][0]['CollectionDate'], \
		result['ReportDateTime'][0]['ReportDate'], \
		result['ReportDateTime'][0]['ReportTime'])
	print '<pre><span style="font-family: monospace;">'
	for line in result['ResultLine']:
		print Pit2HTML(line['Results'])
	print '</span></pre>'
	print "<hr>"


if __name__=="__main__":
	import sys

	usagestr = """
-------------------------------------------------
pit2html Version %s, author: %s
This is free software, released under GPL v2 or later license

usage: pit2html <pitfilename>

-------------------------------------------------
All output goes to stdout (= screen)
You can redirect output into a file as usual,
e.g. pitimporter download.pit > download.html""" % (__version__, __author__)

	def usage():
		print usagestr

	try:
		filename = sys.argv[1]
	except:
		usage()
		sys.exit(0)
	pi = PitParser(filename)
	#output a nicely HTML formatted page to stdout - redirect into file if needed
	print "<html><head><title>%s</title></head><body>" % filename
	while 1:
		#run through the whole file, result by result
		result = pi.nextResult()
		if (not result) : #or (len(result.keys())<1):
			break
#		for tmp in result.keys():
#			print tmp, "=", result[tmp]
		Result2HTML(result)
	print "</body></html>"





