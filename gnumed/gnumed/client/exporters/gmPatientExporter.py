"""GnuMed preliminary simple ASCII EMR export tool.

"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/exporters/gmPatientExporter.py,v $
# $Id: gmPatientExporter.py,v 1.5 2004-04-27 18:54:54 ncq Exp $
__version__ = "$Revision: 1.5 $"
__author__ = "Carlos Moro"
__license__ = 'GPL'

import sys, traceback, string

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
	def get_vacc_table(self,emr):
		vaccinations = emr.get_vaccinations()
		vacc_indications = emr.get_vaccinated_indications()[1]
		# Order indications by name
		vacc_indications.sort()
		# Vaccination items are fetched ordered by date
		# Get list of vaccination dates
		vacc_dates = []
		for a_vacc in vaccinations:
			a_date = a_vacc['date'].Format('%Y-%m-%d')
			if not a_date in vacc_dates:
				vacc_dates.append(a_date)
				print str(a_date)
		# Dictionary date_position_index -> vaccination_vo
		txt= '\t|'
		for a_date in vacc_dates:
			txt+= str(a_date) + "\t|"
		txt += '\n'
		for an_indication in vacc_indications:
			vaccs4ind = emr.get_vaccinations(indication_list = [an_indication[1]])
			#print "indications: " + str(an_indication) + "\nvaccs: " + str(vaccs4ind)
			row_column = 0
			txt+= an_indication[1] + "\t|"
			for a_shot in vaccs4ind:
				shot_column = vacc_dates.index(a_shot['date'].Format('%Y-%m-%d'))
				txt += '\t|'*(shot_column - row_column) + str(a_shot['batch_no']) + '\t|'
				row_column = shot_column
			txt += '\n'
		return txt
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
		txt += self.get_vacc_table(emr)

		#due_vaccinations = emr.get_due_vaccinations()
		#txt += "   .Due vaccinations:\n"
		#for a_vacc in due_vaccinations['due']:
		#	if a_vacc is not None:
		#		txt += str(a_vacc) + "\n"

		#txt += "   .Overdue vaccinations:\n"
		#for a_vacc in due_vaccinations['overdue']:
		#	if a_vacc is not None:
		#		txt += str(a_vacc) + "\n"
		#		pass
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

	try:
		while 1:
			patient_id = prompted_input("Patient ID (or 'bye' to exit) [14]: ", '14')
			if patient_id == 'bye':
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
			#export_tool.dump_demographic_record(True)
			export_tool.dump_clinical_record(patient, since_val=since, until_val=until ,encounters_val=encounters, episodes_val=episodes, issues_val=issues)
			#print(patient.get_document_folder())
	
		gmPG.ConnectionPool().StopListeners()
	except SystemExit:
		print "Normally exited, bye"
	except:
		traceback.print_exc(file=sys.stdout)
		gmPG.ConnectionPool().StopListeners()
		sys.exit(1)
#============================================================
# $Log: gmPatientExporter.py,v $
# Revision 1.5  2004-04-27 18:54:54  ncq
# - adapt to gmClinicalRecord
#
# Revision 1.4  2004/04/24 13:35:33  ncq
# - vacc table update
#
# Revision 1.3  2004/04/24 12:57:30  ncq
# - stop db listeners on exit
#
# Revision 1.2  2004/04/20 13:00:22  ncq
# - recent changes by Carlos to use VO API
#
# Revision 1.1  2004/03/25 23:10:02  ncq
# - gmEmrExport -> gmPatientExporter by Carlos' suggestion
#
# Revision 1.2  2004/03/25 09:53:30  ncq
# - added log keyword
#
