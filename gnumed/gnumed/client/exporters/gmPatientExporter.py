"""GnuMed preliminary simple ASCII EMR export tool.

"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/exporters/gmPatientExporter.py,v $
# $Id: gmPatientExporter.py,v 1.2 2004-04-20 13:00:22 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "Carlos Moro"
__license__ = 'GPL'

import sys, string

from Gnumed.pycommon import gmLog, gmPG, gmI18N
from Gnumed.business import gmClinicalRecord, gmPatient
if __name__ == "__main__":
	gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)

#============================================================
def prompted_input(prompt, default=None):
	usr_input = raw_input(prompt)
	if usr_input == '':
		return default
	return usr_input
#--------------------------------------------------------
class gmEmrExport:

	def __init__(self):
		pass
	#--------------------------------------------------------
	def dump_clinical_record(self, patient, since_val = None, until_val = None, encounters_val = None, episodes_val = None, issues_val = None):
		emr = patient.get_clinical_record()
		if emr is None:
			_log.Log(gmLog.lErr, 'cannot get EMR text dump')
			print(_(
				'An error occurred while retrieving a text\n'
				'dump of the EMR for the active patient.\n\n'
				'Please check the log file for details.'
			))
			return None
		txt =''
		txt += "Overview:\n"
		txt += "--------\n"
		txt += "1) Allergy status (*for details, see below):\n"
		for allergy in 	emr.get_allergies():
			txt += "   -" + allergy['descriptor'] + "\n"
		txt += "\n"
		txt += "2)Vaccination status:\n"
		txt += "   .Vaccination indications:\n"
		vaccinations, idx = emr.get_vaccinations()
		for a_vacc in vaccinations:
			txt += "      "
			txt += str(a_vacc[idx['date']]) + ", "
			txt += a_vacc[idx['indication']] + ", "
			txt += a_vacc[idx['vaccine']] + "\n"
			due_vaccinations = emr.get_due_vaccinations()
			txt += "   .Due vaccinations:\n"
			for a_vacc in due_vaccinations['due']:
				if a_vacc is not None:
					txt += str(a_vacc) + "\n"
			txt += "   .Overdue vaccinations:\n"
			for a_vacc in due_vaccinations['overdue']:
				if a_vacc is not None:
					txt += str(a_vacc) + "\n"
		print(txt)
	#--------------------------------------------------------
	def dump_demographic_record(self, all = False):
		demo = patient.get_demographic_record()
		dump = demo.export_demographics(all)
		if demo is None:
			_log.Log(gmLog.lErr, 'cannot get Demographic export')
			print(_(
				'An error occurred while Demographic record export\n'
				'Please check the log file for details.'
			))
			return None
		#print(dump)
		txt = 'DEMOGRAPHICS for patient:\n'
		txt += '   ID: ' + dump['id'] + '\n'
		for name in dump['names']:
			if dump['names'].index(name) == 0:
				txt += '   NAME (Active): ' + name['first'] + ', ' + name['last'] + '\n'
			else:
				txt += '   NAME ' + dump['names'].index(name) + ': ' + name['first'] + ', ' +  name['last'] + '\n'
		txt += '   GENDER: ' + dump['gender'] + '\n'
		txt += '   TITLE: ' + dump['title'] + '\n'
		txt += '   DOB: ' + dump['dob'] + '\n'
		txt += '   MEDICAL AGE: ' + dump['mage'] + '\n'
		addr_types = dump['addresses'].keys()
		for addr_t in addr_types:
			addr_lst = dump['addresses'][addr_t]
			for address in addr_lst:
				txt += '   ADDRESS (' + addr_t + '): ' + address + '\n'
		print(txt)
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":
	print "Gnumed Simple EMR ASCII Export Tool"
	print "==============================="

	print "Info and confirmation (PENDING)"

	gmPG.set_default_client_encoding('latin1')
	gmPG.ConnectionPool()
	export_tool = gmEmrExport()

	while 1:
		patient_id = prompted_input("Patient ID (or 'bye' to exit) [14]: ", '14')
		if patient_id == 'bye':
			print "Normally exited, bye"
			gmPG.ConnectionPool().StopListeners()
			sys.exit(0)
		patient = gmPatient.gmCurrentPatient(patient_id)
		since = prompted_input("Since (eg. 2001-01-01): ")
		until = prompted_input("Until (eg. 2003-01-01): ")
		encounters = prompted_input("Encounters (eg. 1,2): ")
		episodes = prompted_input("Episodes (eg. 3,4): ")
		issues = prompted_input("Issues (eg. 5,6): ")
		if not encounters is None:
			encounters = string.split(encounters, ',')
		if not episodes is None:
			episodes = string.split(episodes, ',')
		if not issues is None:
			issues = string.split(issues,',')
		export_tool.dump_demographic_record(True)
		export_tool.dump_clinical_record(patient, since_val=since, until_val=until ,encounters_val=encounters, episodes_val=episodes, issues_val=issues)
		print(patient.get_document_folder())
#============================================================
# $Log: gmPatientExporter.py,v $
# Revision 1.2  2004-04-20 13:00:22  ncq
# - recent changes by Carlos to use VO API
#
# Revision 1.1  2004/03/25 23:10:02  ncq
# - gmEmrExport -> gmPatientExporter by Carlos' suggestion
#
# Revision 1.2  2004/03/25 09:53:30  ncq
# - added log keyword
#
