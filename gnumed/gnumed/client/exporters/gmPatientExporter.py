"""GnuMed preliminary simple ASCII EMR export tool.

"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/exporters/gmPatientExporter.py,v $
# $Id: gmPatientExporter.py,v 1.9 2004-06-23 22:06:48 ncq Exp $
__version__ = "$Revision: 1.9 $"
__author__ = "Carlos Moro"
__license__ = 'GPL'

import sys, traceback, string, types

from Gnumed.pycommon import gmLog, gmPG, gmI18N
from Gnumed.business import gmClinicalRecord, gmPatient, gmAllergy, gmVaccination, gmPathLab
from Gnumed.pycommon.gmPyCompat import *

if __name__ == "__main__":
	gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#============================================================
def prompted_input(prompt, default=None):
	usr_input = raw_input(prompt)
	if usr_input == '':
		return default
	return usr_input
#--------------------------------------------------------
class gmEmrExport:
	#--------------------------------------------------------
	"""
	Default constructor
	"""
	def __init__(self):
		lab_new_encounter = True
	#--------------------------------------------------------
	def get_vaccination_for_cell(self, vaccs, date, field, text = None):
		"""
		Checks if a cell matchs a pair vaccination indication - date. It it happends, returns the appropiate text to display
		vaccs - list of vaccination items
		date  - date to check
		text  - text to display in the cell if there's a match vaccination indication - date
		field - name of the field in vaccination item that contains the adecuate date		
		"""
		for a_vacc in vaccs:
			if  a_vacc[field].Format('%Y-%m-%d') == date:
				if text == None:
					return a_vacc['batch_no']
				if text == 'DUE':
				    if a_vacc['overdue'] == True:
				        text = 'OVERDUE  '
				    else:
				        text = 'DUE      '
				return text
		return None				
	#--------------------------------------------------------
	def get_vacc_table(self,emr):
		"""
		Retrieves string containg ASCII vaccination table
		emr - patient's electronic medical record
		"""		
		# Retrieve all patient vaccination items
		vaccinations = []
		vaccinations.extend(emr.get_vaccinations())
		due_vaccs = emr.get_missing_vaccinations()
		vaccinations.extend(due_vaccs['due'])
		vaccinations.extend(due_vaccs['boosters'])
		#print "Total vaccination items : %i" % len(vaccinations)
		
		# Retrieve all vaccination indications
		vacc_indications = []
		status, v_indications = gmVaccination.get_indications_from_vaccinations(vaccinations)
		for v_ind in v_indications:
			if v_ind[0] not in vacc_indications:
				vacc_indications.append(v_ind[0])
				#print v_ind[0]
		vacc_indications.sort()
		#print "Total vaccination indications : %i " % len(vacc_indications)
		#print ""
		
		# Get list of vaccination dates
		#print "Dates: "
		total_vacc_dates = []
		for a_vacc in vaccinations:
			try:
				a_date = a_vacc['date'].Format('%Y-%m-%d')
			except:
				a_date = a_vacc['latest_due'].Format('%Y-%m-%d')
			if not a_date in total_vacc_dates:
				total_vacc_dates.append(a_date)
				#print a_date
		total_vacc_dates.sort()
		#print "Total vaccination dates : %i " % len(total_vacc_dates)
		#print ""
		
		# Number of partial tables to display, depending on the number of dates (columns)
		table_count = int(len(total_vacc_dates) / 5)
		if len(total_vacc_dates) % 5 > 0:
			table_count += 1
		#print "Number of tables to display: %i " % table_count
		
		txt = ''
		for cont in range(table_count):
			start = cont*5
			end = (cont+1)*5
			if end > len(total_vacc_dates):
				end = len(total_vacc_dates)
			vacc_dates = total_vacc_dates[start:end]
			# Get max indication str length
			max_indication_length = -1
			for an_indication in vacc_indications:
				if len(an_indication) > max_indication_length:
					max_indication_length = len(an_indication)
			max_indication_length +=3
			# Get date field length
			column_length = len(vacc_dates[0]) 
			# Print table header (column dates)
			txt += '\n\n'
			txt += ' '*max_indication_length + '|'
			for a_date in vacc_dates:
				txt+= str(a_date) + "\t|"
			txt += '\n'
			# Print rows
			for an_indication in vacc_indications:
				row_column = 0
				txt+= an_indication + " "*(max_indication_length-len(an_indication)) + "|"
				for a_date in vacc_dates:
					cell_txt = self.get_vaccination_for_cell(emr.get_vaccinations(indications = [an_indication]), a_date, 'date')
					if cell_txt is None:
						cell_txt = self.get_vaccination_for_cell(emr.get_missing_vaccinations(indications = [an_indication])['due'], a_date, 'latest_due', 'DUE')
					if cell_txt is None:
						cell_txt = self.get_vaccination_for_cell(emr.get_missing_vaccinations(indications = [an_indication])['boosters'], a_date, 'latest_due', '*DUE    ')					
					if cell_txt is not None:
						txt += cell_txt + '\t|'									
					else:
						txt+= ' '*column_length + '\t|'
				txt += '\t\n'    		
					
		return txt
	#--------------------------------------------------------
	def get_items_for_episode(self, emr, episode):
	   """
        Retrieves all clinical items for a concrete episode
        emr - Patient's electronic clinical record
        episode - Episode whose items are  to be obtained
	   """
	   items = []
	   items.extend(emr.get_allergies(episodes = [episode['id_episode']]))
	   items.extend(emr.get_vaccinations(episodes = [episode['id_episode']]))
	   items.extend(emr.get_lab_results(episodes = [episode['id_episode']]))
	   return items
    #--------------------------------------------------------
	def get_encounters_for_items(self, emr, items):
	    """
            Extracts and retrieves encounters for a list of items
            emr - Patient's electronic clinical record
            items - Items whose  encounters are to be obtained
	    """
	    encounter_ids = []
	    for an_item in items:
	        try :
	            encounter_ids.append(an_item['id_encounter'])
	        except:
	            encounter_ids.append(an_item['pk_encounter'])
	    return emr.get_encounters(id_list = encounter_ids)
	#--------------------------------------------------------
	def dump_item_fields(self, offset, item, field_list):
	    """
            Dump information related to the fields of a clinical item
            offset - Number of left blank spaces
            item - Item of the field to dump
            fields - Fields to dump
	    """
	    txt = ''
	    for a_field in field_list:
	        txt += offset*' ' + a_field + (20-len(a_field))*' ' + ':\t' + str(item[a_field]) + '\n'
	    return txt
	#--------------------------------------------------------
	def get_allergy_output(self, allergy):
	    """
            Dumps allergy item data
            allergy - Allergy item to dump
	    """
	    txt = ''
	    txt += 12*' ' + 'Allergy: \n'
	    txt += self.dump_item_fields(15, allergy, ['allergene', 'substance', 'generic_specific','l10n_type', 'definite', 'reaction'])
	    return txt
	#--------------------------------------------------------
	def get_vaccination_output(self, vaccination):
	    """
            Dumps vaccination item data
            vaccination - Vaccination item to dump
	    """
	    txt = ''
	    txt += 12*' ' + 'Vaccination: \n'
	    txt += self.dump_item_fields(15, vaccination, ['l10n_indication', 'vaccine', 'batch_no', 'site', 'narrative'])	    
	    return txt
	#--------------------------------------------------------
	def get_lab_result_output(self, lab_result):
	    """
            Dumps lab result item data
            lab_request - Lab request item to dump
	    """
	    txt = ''
	    if self.lab_new_encounter:
	        txt += 12*' ' + 'Lab result: \n'
	    txt += 15*' ' + lab_result['unified_name'] + (20-len(lab_result['unified_name']))*' ' + ':\t' + lab_result['unified_val']+ ' ' + lab_result['val_unit'] + '(' + lab_result['material'] + ')' + '\n'
	    return txt
	#--------------------------------------------------------
	def get_item_output(self, item):
	    """
            Obtains formatted clinical item output dump
            item - The clinical item to dump
	    """
	    txt = ''
	    if isinstance(item, gmAllergy.cAllergy):
	        txt += self.get_allergy_output(item)
	    elif isinstance(item, gmVaccination.cVaccination):
	        txt += self.get_vaccination_output(item)
	    elif isinstance(item, gmPathLab.cLabResult):
	        txt += self.get_lab_result_output(item)
	        self.lab_new_encounter = False
	    return txt
	#--------------------------------------------------------
	def get_historical_tree(self, emr = None, since_val = None, until_val = None, encounters_val = None, episodes_val = None, issues_val = None):
	    """
	    Dumps patient's historical in form of a tree of health issues
	                                                    -> episodes
	                                                       -> encounters
	                                                          -> clinical items
	    emr - patient's electronic medical record
	    """
	    # FIXME filter by date range, issue, episode, encounter
	    txt = ''
	    h_issues = emr.get_health_issues()
	    for h_issue in h_issues:
	        txt += '\n' + 3*' ' + 'Health Issue: ' + h_issue['description'] + '\n'
	        for an_episode in emr.get_episodes(issues = [h_issue['id']]):
	           txt += '\n' + 6*' ' + 'Episode: ' + an_episode['description'] + '\n'
	           items = self.get_items_for_episode(emr, an_episode)
	           encounters = self.get_encounters_for_items(emr, items)
	           for an_encounter in encounters:
                    self.lab_new_encounter = True
                    txt += '\n' + 9*' ' + 'Encounter: ' + an_encounter['started'].Format('%Y-%m-%d') + ' to ' + \
                    an_encounter['last_affirmed'].Format('%Y-%m-%d') + ' ' + \
                    an_encounter['description'] + '\n'
                    for an_item  in items:
                        try:
                            if an_item['id_encounter'] == an_encounter['pk_encounter']:
                                txt += self.get_item_output(an_item)
                        except:
                            #traceback.print_exc(file=sys.stdout)
                            # FIXME unify fk field names in views
                            if an_item['pk_encounter'] == an_encounter['pk_encounter']:
                                txt += self.get_item_output(an_item)
	    return txt
	#--------------------------------------------------------
	def dump_clinical_record(self, patient, since_val = None, until_val = None, encounters_val = None, episodes_val = None, issues_val = None):
		"""
		Dumps in ASCII format patient's clinical record
		patient - patient to dump data
		since_val - filters patient EMR clinical items by initial date
		until_val - filters patient EMR clinical items by end date
		encounters_val - filters patient EMR clinical items by encounters
		episodes_val - filters patient EMR clinical items by episodes
		issues_val - filters patient EMR clinical items by health issues
		"""
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
		print txt
		
		txt = ''
		txt += "1) Allergy status (for details, see below):\n\n"
		for allergy in 	emr.get_allergies():
			txt += "   " + allergy['descriptor'] + "\n"
		txt += "\n"
		print txt
		
		txt = ''
		txt += "2) Vaccination status (* indicates booster):\n\n"
		txt += self.get_vacc_table(emr)
		print txt
		
		txt = ''
		txt += "3) Historical:\n\n"
		txt += self.get_historical_tree(emr, since_val, until_val, encounters_val, episodes_val, issues_val)
		print txt

		try:
			emr.cleanup()
		except:
			print "error cleaning up EMR"
	#--------------------------------------------------------
	def dump_demographic_record(self, all = False, patient = None):
		"""
		Dumps in ASCII format some basic patient's demographic data
		"""
		demo = patient.get_demographic_record()
		dump = demo.export_demographics(all)
		if demo is None:
			_log.Log(gmLog.lErr, 'cannot get Demographic export')
			print(_(
				'An error occurred while Demographic record export\n'
				'Please check the log file for details.'
			))
			return None

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
def run():
	patient = None
	patient_id = None
	export_tool = gmEmrExport()

	while patient_id != 'bye':
		# FIXME: ask for patient search string
		patient_id = prompted_input("Patient ID (or 'bye' to exit) [12]: ", '12')
		# FIXME: if empty: exit
		# FIXME: if none/more than one found: warn, restart loop
		# FIXME: if only one found: proceed with dump
		if patient_id == 'bye':
			break
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

		patient = gmPatient.gmCurrentPatient(patient_id)
		export_tool.dump_demographic_record(True, patient)
		export_tool.dump_clinical_record(patient, since_val=since, until_val=until ,encounters_val=encounters, episodes_val=episodes, issues_val=issues)
		# FIXME: dump document folder
		# FIXME: date/document type/doc comment plus object comments
		#print(patient.get_document_folder())

	if patient is not None:
		try:
			patient.cleanup()
		except:
			print "error cleaning up patient"
#------------------------------------------------------------
if __name__ == "__main__":
	print "Gnumed Simple EMR ASCII Export Tool"
	print "==================================="

	gmPG.set_default_client_encoding('latin1')
	# make sure we have a connection
	pool = gmPG.ConnectionPool()
	# run main loop
	try:
		run()
	except StandardError:
		_log.LogException('unhandled exception caught', sys.exc_info(), verbose=1)
	try:
		pool.StopListeners()
	except:
		_log.LogException('unhandled exception caught', sys.exc_info(), verbose=1)

#============================================================
# $Log: gmPatientExporter.py,v $
# Revision 1.9  2004-06-23 22:06:48  ncq
# - cleaner error handling
# - fit for further work by Carlos on UI interface/dumping to file
# - nice stuff !
#
# Revision 1.8  2004/06/20 18:50:53  ncq
# - some exception catching, needs more cleanup
#
# Revision 1.7  2004/06/20 18:35:07  ncq
# - more work from Carlos
#
# Revision 1.6  2004/05/12 14:34:41  ncq
# - now displays nice vaccination tables
# - work by Carlos Moro
#
# Revision 1.5  2004/04/27 18:54:54  ncq
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
