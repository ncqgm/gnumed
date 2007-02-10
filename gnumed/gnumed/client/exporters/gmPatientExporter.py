"""GNUmed simple ASCII EMR export tool.

TODO:
- GUI mode:
  - post-0.1 !
  - allow user to select patient
  - allow user to pick episodes/encounters/etc from list
- output modes:
  - HTML - post-0.1 !
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/exporters/gmPatientExporter.py,v $
# $Id: gmPatientExporter.py,v 1.97 2007-02-10 23:41:38 ncq Exp $
__version__ = "$Revision: 1.97 $"
__author__ = "Carlos Moro"
__license__ = 'GPL'

import os.path, sys, traceback, string, types, time, codecs, datetime as pyDT

import mx.DateTime.Parser as mxParser
import mx.DateTime as mxDT

if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmLog, gmI18N, gmCLI, gmCfg, gmExceptions, gmNull, gmPG2, gmTools
from Gnumed.business import gmClinicalRecord, gmPerson, gmAllergy, gmMedDoc, gmDemographicRecord

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
_cfg = gmCfg.gmDefCfgFile
#============================================================
class cEmrExport:

    #--------------------------------------------------------
    def __init__(self, constraints = None, fileout = None, patient = None):
        """
        Constructs a new instance of exporter

        constraints - Exporter constraints for filtering clinical items
        fileout - File-like object as target for dumping operations
        """
        if constraints is None:
            # default constraints to None for complete emr dump
            self.__constraints = {
                'since': None,
                'until': None,
                'encounters': None,
                'episodes': None,
                'issues': None
            }
        else:
            self.__constraints = constraints
        self.__target = fileout
        self.__patient = patient
        self.lab_new_encounter = True
        self.__filtered_items = []
    #--------------------------------------------------------
    def set_constraints(self, constraints = None):
        """Sets exporter constraints.

        constraints - Exporter constraints for filtering clinical items
        """
        if constraints is None:
            # default constraints to None for complete emr dump
            self.__constraints = {
                'since': None,
                'until': None,
                'encounters': None,
                'episodes': None,
                'issues': None
            }
        else:
            self.__constraints = constraints
        return True
    #--------------------------------------------------------
    def get_constraints(self):
        """
        Retrieve exporter constraints
        """
        return self.__constraints
    #--------------------------------------------------------
    def set_patient(self, patient=None):
        """
            Sets exporter patient
            
            patient - Patient whose data are to be dumped
        """
        if patient is None:
            _log.Log(gmLog.lErr, "can't set None patient for exporter")
            return
        self.__patient = patient
    #--------------------------------------------------------
    def set_output_file(self, file_name=None):
        """
            Sets exporter output file
            
            @param file_name - The file to dump the EMR to
            @type file_name - FileType
        """
        if not isinstance(file_name, types.FileType) :
            _log.Log(gmLog.lErr, "can't set output file [%s] for exporter" % file_name)
            return
        self.__target = file_name
    #--------------------------------------------------------
    def get_patient(self):
        """
            Retrieves patient whose data are to be dumped
        """
        return self.__patient
    #--------------------------------------------------------
    def cleanup(self):
        """
            Exporter class cleanup code
        """
        pass
    #--------------------------------------------------------
    def __dump_vacc_table(self, vacc_regimes):
        """
        Retrieves string containg ASCII vaccination table
        """
        emr = self.__patient.get_emr()
        # patient dob
        
        #patient_dob = mxParser.DateFromString(self.__patient.get_identity().getDOB(aFormat = 'YYYY-MM-DD'), formats= ['iso']) 
        patient_dob = self.__patient.get_identity()['dob']
        date_length = len(patient_dob.strftime('%Y-%m-%d')) + 2 # (YYYY-mm-dd)

        # dictionary of pairs indication : scheduled vaccination
        vaccinations4regimes = {}
        for a_vacc_regime in vacc_regimes:
            indication = a_vacc_regime['indication']
            vaccinations4regimes[indication] = emr.get_scheduled_vaccinations(indications=[indication])
        # vaccination regimes count
        chart_columns = len(vacc_regimes)
        # foot headers
        foot_headers = ['last booster', 'next booster']           
        # string for both: ending of vaccinations; non boosters needed
        ending_str = '='

        # chart row count, columns width and vaccination dictionary of pairs indication : given shot
        column_widths = []
        chart_rows = -1
        vaccinations = {}         
        temp = -1
        for foot_header in foot_headers: # first column width
            if len(foot_header) > temp:
                temp = len(foot_header)
        column_widths.append(temp)          
        for a_vacc_regime in vacc_regimes:
            if a_vacc_regime['shots'] > chart_rows: # max_seq  -> row count 
                chart_rows = a_vacc_regime['shots']
            if (len(a_vacc_regime['l10n_indication'])) > date_length: # l10n indication -> column width
                column_widths.append(len(a_vacc_regime['l10n_indication'])) 
            else:
                column_widths.append(date_length)  # date -> column width at least
            vaccinations[a_vacc_regime['indication']] = emr.get_vaccinations(indications=[a_vacc_regime['indication']]) # given shots 4 indication
                
        # patient dob in top of vaccination chart 
        txt = '\nDOB: %s' %(patient_dob.strftime('%Y-%m-%d')) + '\n'         

        # vacc chart table headers
        # top ---- header line
        for column_width in column_widths: 
            txt += column_width * '-' + '-'
        txt += '\n'                   
        # indication names header line
        txt += column_widths[0] * ' ' + '|'
        col_index = 1
        for a_vacc_regime in vacc_regimes:
            txt +=    a_vacc_regime['l10n_indication'] + (column_widths[col_index] - len(a_vacc_regime['l10n_indication'])) * ' ' + '|'
            col_index += 1
        txt +=    '\n'
        # bottom ---- header line
        for column_width in column_widths:
            txt += column_width * '-' + '-'
        txt += '\n'           

        # vacc chart data
        due_date = None           
        # previously displayed date list
        prev_displayed_date = [patient_dob]
        for a_regime in vacc_regimes:
            prev_displayed_date.append(patient_dob) # initialice with patient dob (useful for due first shot date calculation)
        # iterate data rows
        for row_index in range(0, chart_rows):              
            row_header = '#%s' %(row_index+1)
            txt += row_header + (column_widths[0] - len(row_header)) * ' ' + '|'

            for col_index in range(1, chart_columns+1):
                indication =vacc_regimes[col_index-1]['indication']
                seq_no = vacc_regimes[col_index-1]['shots']
                if row_index == seq_no: # had just ended scheduled vaccinations
                     txt += ending_str * column_widths[col_index] + '|'
                elif row_index < seq_no: # vaccination scheduled
                    try:
                        vacc_date = vaccinations[indication][row_index]['date'] # vaccination given                           
                        vacc_date_str = vacc_date.strftime('%Y-%m-%d')                        
                        txt +=    vacc_date_str + (column_widths[col_index] - len(vacc_date_str)) * ' ' + '|'                           
                        prev_displayed_date[col_index] = vacc_date                                                  
                    except:
                        if row_index == 0: # due first shot
                            due_date = prev_displayed_date[col_index] + vaccinations4regimes[indication][row_index]['age_due_min'] # FIXME 'age_due_min' not properly retrieved
                        else: # due any other than first shot
                            due_date = prev_displayed_date[col_index] + vaccinations4regimes[indication][row_index]['min_interval']
                        txt += '('+ due_date.strftime('%Y-%m-%d') + ')' + (column_widths[col_index] - date_length) * ' ' + '|'
                        prev_displayed_date[col_index] = due_date
                else: # not scheduled vaccination at that position
                    txt += column_widths[col_index] * ' ' + '|'
            txt += '\n' # end of scheduled vaccination dates display
            for column_width in column_widths: # ------ separator line
                txt += column_width * '-' + '-'
            txt += '\n'

        # scheduled vaccination boosters (date retrieving)
        all_vreg_boosters = []                  
        for a_vacc_regime in vacc_regimes:
            vaccs4indication = vaccinations[a_vacc_regime['indication']] # iterate over vaccinations by indication
            given_boosters = [] # will contain given boosters for current indication
            for a_vacc in vaccs4indication:
                try:
                     if a_vacc['is_booster']:
                         given_boosters.append(a_vacc)
                except:
                    # not a booster
                    pass
            if len(given_boosters) > 0:
                all_vreg_boosters.append(given_boosters[len(given_boosters)-1]) # last of given boosters
            else:
                all_vreg_boosters.append(None)

        # next booster in schedule
        all_next_boosters = []
        for a_booster in all_vreg_boosters:
            all_next_boosters.append(None)
        # scheduled vaccination boosters (displaying string)
        cont = 0
        for a_vacc_regime in vacc_regimes:
            vaccs = vaccinations4regimes[a_vacc_regime['indication']]         
            if vaccs[len(vaccs)-1]['is_booster'] == False: # booster is not scheduled/needed
                all_vreg_boosters[cont] = ending_str * column_widths[cont+1]
                all_next_boosters[cont] = ending_str * column_widths[cont+1]
            else:
                indication = vacc_regimes[cont]['indication']
                if len(vaccinations[indication]) > vacc_regimes[cont]['shots']: # boosters given
                    all_vreg_boosters[cont] = vaccinations[indication][len(vaccinations[indication])-1]['date'].strftime('%Y-%m-%d') # show last given booster date
                    scheduled_booster = vaccinations4regimes[indication][len(vaccinations4regimes[indication])-1]
                    booster_date = vaccinations[indication][len(vaccinations[indication])-1]['date'] + scheduled_booster['min_interval']                                        
                    if booster_date < mxDT.today():
                        all_next_boosters[cont] = '<(' + booster_date.strftime('%Y-%m-%d') + ')>' # next booster is due
                    else:
                        all_next_boosters[cont] = booster_date.strftime('%Y-%m-%d')
                elif len(vaccinations[indication]) == vacc_regimes[cont]['shots']: # just finished vaccinations, begin boosters
                    all_vreg_boosters[cont] = column_widths[cont+1] * ' '
                    scheduled_booster = vaccinations4regimes[indication][len(vaccinations4regimes[indication])-1]
                    booster_date = vaccinations[indication][len(vaccinations[indication])-1]['date'] + scheduled_booster['min_interval']                    
                    if booster_date < mxDT.today():
                        all_next_boosters[cont] = '<(' + booster_date.strftime('%Y-%m-%d') + ')>' # next booster is due
                    else:
                        all_next_boosters[cont] = booster_date.strftime('%Y-%m-%d')
                else:
                    all_vreg_boosters[cont] = column_widths[cont+1] * ' '  # unfinished schedule
                    all_next_boosters[cont] = column_widths[cont+1] * ' '
            cont += 1

        # given boosters
        foot_header = foot_headers[0]
        col_index = 0
        txt += foot_header + (column_widths[0] - len(foot_header)) * ' ' + '|'
        col_index += 1
        for a_vacc_regime in vacc_regimes:
            txt +=    str(all_vreg_boosters[col_index-1]) + (column_widths[col_index] - len(str(all_vreg_boosters[col_index-1]))) * ' ' + '|'
            col_index += 1
        txt +=    '\n'
        for column_width in column_widths:              
            txt += column_width * '-' + '-'
        txt += '\n' 

        # next booster
        foot_header = foot_headers[1]
        col_index = 0
        txt += foot_header + (column_widths[0] - len(foot_header)) * ' ' + '|'
        col_index += 1
        for a_vacc_regime in vacc_regimes:
            txt +=    str(all_next_boosters[col_index-1]) + (column_widths[col_index] - len(str(all_next_boosters[col_index-1]))) * ' ' + '|'
            col_index += 1
        txt +=    '\n'
        for column_width in column_widths:
            txt += column_width * '-' + '-'
        txt += '\n'                   

        self.__target.write(txt)        
    #--------------------------------------------------------
    def get_vacc_table(self):
        """
        Iterate over patient scheduled regimes preparing vacc tables dump
        """           
        
        emr = self.__patient.get_emr()
        
        # vaccination regimes
        all_vacc_regimes = emr.get_scheduled_vaccination_regimes()
        # Configurable: vacc regimes per displayed table
        # FIXME: option, post 0.1 ?
        max_regs_per_table = 4

        # Iterate over patient scheduled regimes dumping in tables of 
        # max_regs_per_table regimes per table
        reg_count = 0
        vacc_regimes = []
        for total_reg_count in range(0,len(all_vacc_regimes)):
            if reg_count%max_regs_per_table == 0:
                if len(vacc_regimes) > 0:
                    self.__dump_vacc_table(vacc_regimes)
                vacc_regimes = []
                reg_count = 0
            vacc_regimes.append(all_vacc_regimes[total_reg_count])
            reg_count += 1
        if len(vacc_regimes) > 0:
            self.__dump_vacc_table(vacc_regimes)        

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
            if type(a_field) is not types.UnicodeType:
                a_field = unicode(a_field, encoding='latin1', errors='replace')
            txt += u'%s%s%s' % ((offset * u' '), a_field, gmTools.coalesce(item[a_field], u'', template = u': %s\n'))
        return txt
    #--------------------------------------------------------
    def get_allergy_output(self, allergy, left_margin = 0):
        """
            Dumps allergy item data
            allergy - Allergy item to dump
            left_margin - Number of spaces on the left margin
        """
        txt = ''
        txt += left_margin*' ' + _('Allergy')  + ': \n'
        txt += self.dump_item_fields((left_margin+3), allergy, ['allergene', 'substance', 'generic_specific','l10n_type', 'definite', 'reaction'])
        return txt
    #--------------------------------------------------------
    def get_vaccination_output(self, vaccination, left_margin = 0):
        """
            Dumps vaccination item data
            vaccination - Vaccination item to dump
            left_margin - Number of spaces on the left margin
        """
        txt = ''
        txt += left_margin*' ' + _('Vaccination') + ': \n'
        txt += self.dump_item_fields((left_margin+3), vaccination, ['l10n_indication', 'vaccine', 'batch_no', 'site', 'narrative'])           
        return txt
    #--------------------------------------------------------
    def get_lab_result_output(self, lab_result, left_margin = 0):
        """
            Dumps lab result item data
            lab_request - Lab request item to dump
            left_margin - Number of spaces on the left margin             
        """
        txt = ''
        if self.lab_new_encounter:
            txt += (left_margin)*' ' + _('Lab result') + ': \n'
        txt += (left_margin+3) * ' ' + lab_result['unified_name']  + ': ' + lab_result['unified_val']+ ' ' + lab_result['val_unit'] + ' (' + lab_result['material'] + ')' + '\n'
        return txt
    #--------------------------------------------------------
    def get_item_output(self, item, left_margin = 0):
        """
            Obtains formatted clinical item output dump
            item - The clinical item to dump
            left_margin - Number of spaces on the left margin             
        """
        txt = ''
        if isinstance(item, gmAllergy.cAllergy):
            txt += self.get_allergy_output(item, left_margin)
#        elif isinstance(item, gmVaccination.cVaccination):
 #           txt += self.get_vaccination_output(item, left_margin)
#        elif isinstance(item, gmPathLab.cLabResult):
 #           txt += self.get_lab_result_output(item, left_margin)
  #          self.lab_new_encounter = False
        return txt
    #--------------------------------------------------------
    def __fetch_filtered_items(self):
        """
            Retrieve patient clinical items filtered by multiple constraints
        """
        if not self.__patient.is_connected():
            return False
        emr = self.__patient.get_emr()
        filtered_items = []
        filtered_items.extend(emr.get_allergies(
            since=self.__constraints['since'],
            until=self.__constraints['until'],
            encounters=self.__constraints['encounters'],
            episodes=self.__constraints['episodes'],
            issues=self.__constraints['issues']))
#        try:
 #               filtered_items.extend(emr.get_vaccinations(
  #                  since=self.__constraints['since'],
   #                 until=self.__constraints['until'],
    #                encounters=self.__constraints['encounters'],
     #               episodes=self.__constraints['episodes'],
      #              issues=self.__constraints['issues']))
       # except:
        #        _log.Error("vaccination error? outside regime")

#        filtered_items.extend(emr.get_lab_results(
 #           since=self.__constraints['since'],
  #          until=self.__constraints['until'],
   #         encounters=self.__constraints['encounters'],
    #        episodes=self.__constraints['episodes'],
     #       issues=self.__constraints['issues']))
        self.__filtered_items = filtered_items
        return True
    #--------------------------------------------------------
    def get_allergy_summary(self, allergy, left_margin = 0):
        """
            Dumps allergy item data summary
            allergy - Allergy item to dump
            left_margin - Number of spaces on the left margin
        """
        txt = left_margin*' ' + _('Allergy') + ': ' + allergy['descriptor'] + ', ' + \
            gmTools.coalesce(allergy['reaction'], _('unknown reaction')) + '\n'
        return txt
    #--------------------------------------------------------
    def get_vaccination_summary(self, vaccination, left_margin = 0):
        """
            Dumps vaccination item data summary
            vaccination - Vaccination item to dump
            left_margin - Number of spaces on the left margin
        """
        txt = left_margin*' ' + _('Vaccination') + ': ' + vaccination['l10n_indication'] + ', ' + \
            vaccination['narrative'] + '\n'
        return txt
    #--------------------------------------------------------
    def get_lab_result_summary(self, lab_result, left_margin = 0):
        """
            Dumps lab result item data summary
            lab_request - Lab request item to dump
            left_margin - Number of spaces on the left margin             
        """
        txt = ''
        if self.lab_new_encounter:
            txt += (left_margin+3)*' ' + _('Lab') + ': '  + \
                lab_result['unified_name'] + '-> ' + lab_result['unified_val'] + \
                ' ' + lab_result['val_unit']+ '\n' + '(' + lab_result['req_when'].strftime('%Y-%m-%d') + ')'
        return txt
    #--------------------------------------------------------
    def get_item_summary(self, item, left_margin = 0):
        """
            Obtains formatted clinical item summary dump
            item - The clinical item to dump
            left_margin - Number of spaces on the left margin             
        """
        txt = ''
        if isinstance(item, gmAllergy.cAllergy):
            txt += self.get_allergy_summary(item, left_margin)
#        elif isinstance(item, gmVaccination.cVaccination):
 #           txt += self.get_vaccination_summary(item, left_margin)
#        elif isinstance(item, gmPathLab.cLabResult) and \
#	    True: 
 #           #(item['relevant'] == True or item['abnormal'] == True):
  #          txt += self.get_lab_result_summary(item, left_margin)
   #         self.lab_new_encounter = False
        return txt
    #--------------------------------------------------------             
    def refresh_historical_tree(self, emr_tree):
        """
        checks a emr_tree constructed with this.get_historical_tree() 
        and sees if any new items need to be inserted.
        """
        #TODO , caching eliminates tree update time, so don't really need this
        self._traverse_health_issues( emr_tree, self._update_health_issue_branch)
	
    #--------------------------------------------------------             
    def get_historical_tree( self, emr_tree):
        self._traverse_health_issues( emr_tree, self._add_health_issue_branch)
    #--------------------------------------------------------             
    def _traverse_health_issues(self, emr_tree, health_issue_action):
        """
        Retrieves patient's historical in form of a wx tree of health issues
                                                                                        -> episodes
                                                                                           -> encounters
        Encounter object is associated with item to allow displaying its information
        """
        # variable initialization
        # this protects the emrBrowser from locking up in a paint event, e.g. in
        # some configurations which want to use emrBrowser, but don't stop tabbing
        # to emr browser when no patient selected. the effect is to displace a cNull instance
        # which is a sane representation when no patient is selected.
        if not self.__fetch_filtered_items():
            return
        emr = self.__patient.get_emr()
        unlinked_episodes = emr.get_episodes(issues = [None])
        h_issues = []
        h_issues.extend(emr.get_health_issues(id_list = self.__constraints['issues']))
        # build the tree
        # unlinked episodes
        if len(unlinked_episodes) > 0:
            h_issues.insert(0, {
                'description': _('free-standing episodes'),
                'pk': None
            })
        # existing issues        
        for a_health_issue in h_issues:
		health_issue_action( emr_tree, a_health_issue)

    #--------------------------------------------------------             
    def _add_health_issue_branch( self, emr_tree, a_health_issue):
            """appends to a wx emr_tree  , building wx treenodes from the health_issue  make this reusable for non-collapsing tree updates"""
            emr = self.__patient.get_emr()
            root_node = emr_tree.GetRootItem()
            issue_node =  emr_tree.AppendItem(root_node, a_health_issue['description'])
            emr_tree.SetPyData(issue_node, a_health_issue)
            episodes = emr.get_episodes(id_list=self.__constraints['episodes'], issues = [a_health_issue['pk']])
            for an_episode in episodes:
	       self._add_episode_to_tree( emr, emr_tree, issue_node,a_health_issue,  an_episode)


    #--------------------------------------------------------             
    def _add_episode_to_tree( self, emr , emr_tree, issue_node, a_health_issue, an_episode):
               episode_node =  emr_tree.AppendItem(issue_node, an_episode['description'])
               emr_tree.SetPyData(episode_node, an_episode)
#	       encounters = self._get_encounters( a_health_issue, an_episode, emr )
	       encounters = self._get_encounters( an_episode, emr )
	       self._add_encounters_to_tree( encounters,  emr_tree, episode_node )
	       return episode_node
	       
    #--------------------------------------------------------             
    def _add_encounters_to_tree( self, encounters, emr_tree, episode_node):
               for an_encounter in encounters:
                    label = '%s:%s' % (an_encounter['l10n_type'], an_encounter['started'].strftime('%Y-%m-%d'))
                    encounter_node = emr_tree.AppendItem(episode_node, label)
		    #import threading
		    #def added():
		    #	print "added ", label
		    #threading.Timer(2, added).start() 
                    emr_tree.SetPyData(encounter_node, an_encounter)
		   
		   
    #--------------------------------------------------------             
#    def _get_encounters ( self, a_health_issue, an_episode, emr ):
    def _get_encounters ( self, an_episode, emr ):
               encounters = emr.get_encounters (
                   since = self.__constraints['since'],
                   until = self.__constraints['until'],
                   id_list = self.__constraints['encounters'],
                   episodes = [an_episode['pk_episode']]
#                   ,issues = [a_health_issue['pk']]
               )
               return encounters
	       
    #--------------------------------------------------------             
    def  _update_health_issue_branch(self, emr_tree, a_health_issue):
            emr = self.__patient.get_emr()
            root_node = emr_tree.GetRootItem()
	    id, cookie = emr_tree.GetFirstChild( root_node)
	    found = False
	    while id.IsOk():
	        #try:
	    	#  _log.Log(gmLog.lErr, "emr_tree.GetItemText(id)  a_health_issue['description']\n\t\t: %s %s\n" % ( emr_tree.GetItemText(id)  , a_health_issue['description'] ) )
		#except:
		#  print sys.exc_info()[0], sys.exc_info()[1]
		#  traceback.print_tb( sys.exc_info()[2])

	    	if emr_tree.GetItemText(id)  ==  a_health_issue['description'] :
			found = True
			break
		id,cookie = emr_tree.GetNextChild( root_node, cookie)
	    
	    if not found:
	    	_log.Log(gmLog.lErr, "health issue %s should exist in tree already" %  a_health_issue['description'] )
		return
	    issue_node= id
	    episodes = emr.get_episodes(id_list=self.__constraints['episodes'], issues = [a_health_issue['pk']])
	    
	    #check for removed episode and update tree
	    tree_episodes = {} 
	    id_episode, cookie = emr_tree.GetFirstChild(issue_node)
	    while id_episode.IsOk():
		    	tree_episodes[ emr_tree.GetPyData(id_episode)['pk_episode'] ]= id_episode
			id_episode,cookie = emr_tree.GetNextChild( issue_node, cookie)
	
	    existing_episode_pk = [ e['pk_episode'] for e in episodes]
	    missing_tree_pk = [ pk for pk in tree_episodes.keys() if pk not in existing_episode_pk]
	    for pk in missing_tree_pk:
		emr_tree.Remove( tree_episodes[pk] )
	
	    added_episode_pk = [pk for pk in existing_episode_pk if pk not in tree_episodes.keys()]
	    add_episodes = [ e for e in episodes if e['pk_episode'] in added_episode_pk]
	   
	    #check for added episodes and update tree
	    for an_episode in add_episodes:
			node = self._add_episode_to_tree( emr, emr_tree, issue_node, a_health_issue, an_episode)
			tree_episodes[an_episode['pk_episode']] = node
			
			
            for an_episode in episodes:
			# found episode, check for encounter change
			try:
			  #print "getting id_episode of ", an_episode['pk_episode']
			  id_episode = tree_episodes[an_episode['pk_episode']]	
			except:
			  import pdb
			  pdb.set_trace()
			# get a map of encounters in the tree by pk_encounter as key
			tree_enc = {}
			id_encounter, cookie = emr_tree.GetFirstChild(id_episode)
			while id_encounter.IsOk():
				tree_enc[ emr_tree.GetPyData(id_encounter)['pk_encounter'] ] = id_encounter
				id_encounter,cookie = emr_tree.GetNextChild(id_episode, cookie)
				
			# remove encounters in tree not in existing encounters in episode
#			encounters = self._get_encounters( a_health_issue, an_episode, emr )
			encounters = self._get_encounters( an_episode, emr )
			existing_enc_pk = [ enc['pk_encounter'] for enc in encounters]
			missing_enc_pk = [ pk  for pk in tree_enc.keys() if pk not in existing_enc_pk]
			for pk in missing_enc_pk:
				emr_tree.Remove( tree_enc[pk] )
					
			# check for added encounter
			added_enc_pk = [ pk for pk in existing_enc_pk if pk not in tree_enc.keys() ]
			add_encounters = [ enc for enc in encounters if enc['pk_encounter'] in added_enc_pk]
			if add_encounters != []:
				#print "DEBUG found encounters to add"
				self._add_encounters_to_tree( add_encounters, emr_tree, id_episode)
				

				
    	
    #--------------------------------------------------------  
    def get_summary_info(self, left_margin = 0):
        """
        Dumps patient EMR summary
        """
        txt = ''
        for an_item in self.__filtered_items:
            txt += self.get_item_summary(an_item, left_margin)
        return txt                      
    #--------------------------------------------------------
    def get_issue_info(self, issue=None, left_margin=0):
        """Dumps health issue specific data
        """
        # dummy issue for unlinked episodes ?
        # FIXME: turn into "proper" dummy episode
        if issue['pk'] is None:
            txt = _('Active health issue "%s"') % issue['description']
            return txt

        if issue['is_active']:
            status = _('Active health issue')
        else:
            status = _('Inactive health issue')
        txt = _('%s "%s" noted at age %s\n') % (
            status,
            issue['description'],
            issue['age_noted']
        )
        if issue['clinically_relevant']:
            txt += _('clinically relevant: yes\n')
        else:
            txt += _('clinically relevant: no\n')
        if issue['is_cause_of_death']:
            txt += _('health issue caused death of patient\n')
        if issue['is_confidential']:
            txt += _('\n***** CONFIDENTIAL *****\n\n')

        emr = self.__patient.get_emr()
        epis = emr.get_episodes(issues=[issue['pk']])
        if epis is None:
            txt += left_margin * ' ' + _('Error retrieving episodes for health issue\n%s') % str(issue)
            return txt
        no_epis = len(epis)
        if no_epis == 0:
            txt += left_margin * ' ' + _('There are no episodes for this health issue.\n')
            return txt

        first_encounter = emr.get_first_encounter(issue_id = issue['pk'])
        last_encounter = emr.get_last_encounter(issue_id = issue['pk'])
        if first_encounter is None or last_encounter is None:
            txt += _('%s%s episode(s)\n\n%sNo encounters found for this health issue.\n') % (
                left_margin * ' ' +
                str(no_epis),
                left_margin * ' ')
            return txt
        txt += _('%s%s episode(s) between %s and %s\n') % (
            left_margin * ' ',
            str(no_epis),
            first_encounter['started'].strftime('%m/%Y'),
            last_encounter['last_affirmed'].strftime('%m/%Y')
        )
        txt += _('%sLast seen: %s\n\n') % (left_margin * ' ', last_encounter['last_affirmed'].strftime('%Y-%m-%d %H:%M'))
        # FIXME: list each episode with range of time
        return txt
    #--------------------------------------------------------
    def get_episode_summary (self, episode, left_margin = 0):
        """Dumps episode specific data"""
        emr = self.__patient.get_emr()
        encs = emr.get_encounters(episodes = [episode['pk_episode']])
        if encs is None:
            txt = left_margin * ' ' + _('Error retrieving encounters for episode\n%s') % str(episode)
            return txt
        no_encs = len(encs)
        if no_encs == 0:
            txt = left_margin * ' ' + _('There are no encounters for this episode.')
            return txt
        if episode['episode_open']:
            status = _('active')
        else:
            status = _('finished')
        first_encounter = emr.get_first_encounter(episode_id = episode['pk_episode'])
        last_encounter = emr.get_last_encounter(episode_id = episode['pk_episode'])
        txt = _(
            '%sEpisode "%s" [%s]\n'
            '%sEncounters: %s (%s - %s)\n'
            '%sLast worked on: %s\n'
        ) % (
            left_margin * ' ', episode['description'], status,
            left_margin * ' ', no_encs, first_encounter['started'].strftime('%m/%Y'), last_encounter['last_affirmed'].strftime('%m/%Y'),
            left_margin * ' ', last_encounter['last_affirmed'].strftime('%Y-%m-%d %H:%M')
        )
        return txt
    #--------------------------------------------------------
    def get_encounter_info(self, episode, encounter, left_margin = 0):
        """
        Dumps encounter specific data (rfe, aoe and soap)
        """
        emr = self.__patient.get_emr()
        # general
        txt = (' ' * left_margin) + '%s - %s: %s' % (
            encounter['started'].strftime('%Y-%m-%d  %H:%M'),
            encounter['last_affirmed'].strftime('%H:%M'),
            encounter['l10n_type']
        )
        if (encounter['assessment_of_encounter'] is not None) and (len(encounter['assessment_of_encounter']) > 0):
            txt += ' (%s)' % encounter['assessment_of_encounter']
        txt += '\n\n'

        # rfe/aoe
        txt += (' ' * left_margin) + '%s: %s\n' % (_('RFE'), encounter['reason_for_encounter'])
        txt += (' ' * left_margin) + '%s: %s\n' % (_('AOE'), encounter['assessment_of_encounter'])

        # soap
        soap_cat_labels = {
            's': _('Subjective'),
            'o': _('Objective'),
            'a': _('Assessment'),
            'p': _('Plan'),
        }
        eol_w_margin = '\n' + (' ' * (left_margin+3))
        for soap_cat in 'soap':
            soap_cat_narratives = emr.get_clin_narrative (
                episodes = [episode['pk_episode']],
                encounters = [encounter['pk_encounter']],
                soap_cats = [soap_cat]
            )
            if soap_cat_narratives is None:
                continue
            if len(soap_cat_narratives) == 0:
                continue
            txt += (' ' * left_margin) + soap_cat_labels[soap_cat] + ':\n'
            for soap_entry in soap_cat_narratives:
                txt += gmTools.wrap (
                    '%s %.8s: %s\n' % (
                        soap_entry['date'].strftime('%H:%M'),
                        soap_entry['provider'],
                        soap_entry['narrative']
                    ), 75
                )

#                txt += (
 #                   (' ' * (left_margin+3)) +
  #                  soap_entry['date'].strftime('%H:%M %.8s: ') % soap_entry['provider'] +
   #                 soap_entry['narrative'].replace('\n', eol_w_margin) +
    #                '\n'
     #           )
		#FIXME: add diagnoses

        # items
        for an_item in self.__filtered_items:
            if an_item['pk_encounter'] == encounter['pk_encounter']:
                txt += self.get_item_output(an_item, left_margin)
        return txt      
    #--------------------------------------------------------  
    def dump_historical_tree(self):
        """Dumps patient's historical in form of a tree of health issues
                                                        -> episodes
                                                           -> encounters
                                                              -> clinical items
                                                              
        """

        # fecth all values
        self.__fetch_filtered_items()
        emr = self.__patient.get_emr()

        # dump clinically relevant items summary
        for an_item in self.__filtered_items:
            self.__target.write(self.get_item_summary(an_item, 3))
                
        # begin with the tree
        h_issues = []
        h_issues.extend(emr.get_health_issues(id_list = self.__constraints['issues']))
        # unlinked episodes
        unlinked_episodes = emr.get_episodes(issues = [None])
        if len(unlinked_episodes) > 0:
            h_issues.insert(0, {'description':_('free-standing episodes'), 'pk':None})        
        for a_health_issue in h_issues:
            self.__target.write('\n' + 3*' ' + 'Health Issue: ' + a_health_issue['description'] + '\n')
            episodes = emr.get_episodes(id_list=self.__constraints['episodes'], issues = [a_health_issue['pk']])
            for an_episode in episodes:
               self.__target.write('\n' + 6*' ' + 'Episode: ' + an_episode['description'] + '\n')
               if a_health_issue['pk'] is None:
                  issues = None
               else:
                  issues = [a_health_issue['pk']]
               encounters = emr.get_encounters (
                  since = self.__constraints['since'],
                  until = self.__constraints['until'],
                  id_list = self.__constraints['encounters'],
                  episodes = [an_episode['pk_episode']],
                  issues = issues
               )
               for an_encounter in encounters:
                    # title
                    self.lab_new_encounter = True
                    self.__target.write(
                        '\n            %s %s: %s - %s (%s)\n' % (
                            _('Encounter'),
                            an_encounter['l10n_type'],
                            an_encounter['started'].strftime('%A, %Y-%m-%d %H:%M'),
                            an_encounter['last_affirmed'].strftime('%m-%d %H:%M'),
                            an_encounter['assessment_of_encounter']
                        )
                    )
                    self.__target.write(self.get_encounter_info(an_episode, an_encounter, 12))
    #--------------------------------------------------------
    def dump_clinical_record(self):
        """
        Dumps in ASCII format patient's clinical record
        
        """
        emr = self.__patient.get_emr()
        if emr is None:
            _log.Log(gmLog.lErr, 'cannot get EMR text dump')
            print(_(
                'An error occurred while retrieving a text\n'
                'dump of the EMR for the active patient.\n\n'
                'Please check the log file for details.'
            ))
            return None
        self.__target.write('\nOverview\n')
        self.__target.write('--------\n')
        self.__target.write("1) Allergy status (for details, see below):\n\n")
        for allergy in       emr.get_allergies():
            self.__target.write("    " + allergy['descriptor'] + "\n\n")
        self.__target.write("2) Vaccination status (* indicates booster):\n")
#        self.get_vacc_table()
        self.__target.write("\n3) Historical:\n\n")
        self.dump_historical_tree()

        try:
            emr.cleanup()
        except:
            print "error cleaning up EMR"
    #--------------------------------------------------------
    def dump_med_docs(self):
        """
            Dumps patient stored medical documents

        """
        doc_folder = self.__patient.get_document_folder()

        self.__target.write('\n4) Medical documents: (date) reference - type "comment"\n')
        self.__target.write('                          object - comment')

        docs = doc_folder.get_documents()
        for doc in docs:
            self.__target.write('\n\n    (%s) %s - %s "%s"' % (
                doc['date'].strftime('%Y-%m-%d'),
                doc['ext_ref'],
                doc['l10n_type'],
                doc['comment'])
            )
            parts = doc.get_parts()
            for part in parts:
                self.__target.write('\n         %s - %s' % (
                    part['seq_idx'],
                    part['obj_comment'])
                )
        self.__target.write('\n\n')
    #--------------------------------------------------------     
    def dump_demographic_record(self, all = False):
        """
            Dumps in ASCII format some basic patient's demographic data
        """
        ident = self.__patient.get_identity()
        if ident is None:
            _log.Log(gmLog.lErr, 'cannot get Demographic export')
            print(_(
                'An error occurred while Demographic record export\n'
                'Please check the log file for details.'
            ))
            return None

        self.__target.write('\n\n\nDemographics')
        self.__target.write('\n------------\n')
        self.__target.write('    Id: %s \n' % ident.getId())
        cont = 0
        for name in ident.get_all_names():
            if cont == 0:
                self.__target.write('    Name (Active): %s, %s\n' % (name['first'], name['last']) )
            else:
                self.__target.write('    Name %s: %s, %s\n' % (cont, name['first'], name['last']))
            cont += 1
        self.__target.write('    Gender: %s\n' % ident['gender'])
        self.__target.write('    Title: %s\n' % ident['title'])
        self.__target.write('    Dob: %s\n' % ident['dob'].strftime('%Y-%m-%d'))
        self.__target.write('    Medical age: %s\n' % gmPerson.dob2medical_age(ident['dob']))
    #--------------------------------------------------------
    def dump_constraints(self):
        """
            Dumps exporter filtering constraints
        """
        self.__first_constraint = True
        if not self.__constraints['since'] is None:
            self.dump_constraints_header()
            self.__target.write('\nSince: %s' % self.__constraints['since'].strftime('%Y-%m-%d'))

        if not self.__constraints['until'] is None:
            self.dump_constraints_header()
            self.__target.write('\nUntil: %s' % self.__constraints['until'].strftime('%Y-%m-%d'))

        if not self.__constraints['encounters'] is None:
            self.dump_constraints_header()
            self.__target.write('\nEncounters: ')
            for enc in self.__constraints['encounters']:
                self.__target.write(str(enc) + ' ')

        if not self.__constraints['episodes'] is None:
            self.dump_constraints_header()
            self.__target.write('\nEpisodes: ')
            for epi in self.__constraints['episodes']:
                self.__target.write(str(epi) + ' ')

        if not self.__constraints['issues'] is None:
            self.dump_constraints_header()
            self.__target.write('\nIssues: ')
            for iss in self.__constraints['issues']:
                self.__target.write(str(iss) + ' ')
    #--------------------------------------------------------
    def dump_constraints_header(self):
        """
            Dumps constraints header
        """
        if self.__first_constraint == True:
            self.__target.write('\nClinical items dump constraints\n')
            self.__target.write('-'*(len(head_txt)-2))
            self.__first_constraint = False
#============================================================
class cEMRJournalExporter:
	"""Exports patient EMR into a simple chronological journal.

	Note that this export will emit u'' strings only.
	"""
	def __init__(self):
		self.__part_len = 72
		self.__tx_soap = {
			u's': _('S'),
			u'o': _('O'),
			u'a': _('A'),
			u'p': _('P')
		}
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def export_to_file(self, filename=None, patient=None):
		"""
		Export medical record into a file.

		@type filename: None (creates filename by itself) or string
		@type patient: None (use currently active patient) or <gmPerson.cPerson> instance
		"""
		if patient is None:
			patient = gmPerson.gmCurrentPatient().patient
			if not patient.is_connected():
				raise ValueError('[%s].export_to_file(): no active patient' % self.__class__.__name__)

		if filename is None:
			ident = patient.get_identity()
			path = os.path.expanduser(os.path.join('~', 'gnumed', 'export'))
			filename = u'%s-%s-%s-%s.txt' % (
				os.path.join(path, _('emr-journal')),
				ident['lastnames'].replace(u' ', u'-'),
				ident['firstnames'].replace(u' ', u'_'),
				ident['dob'].strftime('%Y-%m-%d')
			)

		f = codecs.open(filename = filename, mode = 'w+b', encoding = 'utf8')
		self.export(target = f, patient = patient)
		f.close()

		return filename
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def export(self, target=None, patient=None):
		"""
		Export medical record into a Python object.

		@type target: a python object supporting the write() API
		@type patient: None (use currently active patient) or <gmPerson.cPerson> instance
		"""
		if patient is None:
			patient = gmPerson.gmCurrentPatient().patient
			if not patient.is_connected():
				raise ValueError('[%s].export(): no active patient' % self.__class__.__name__)

		ident = patient.get_identity()
		# write header
		txt = _('Chronological EMR Journal\n')
		target.write(txt)
		target.write(u'=' * (len(txt)-1))
		target.write('\n')
		target.write(_('Patient: %s (%s), No: %s\n') % (ident['description'], ident['gender'], patient['ID']))
		target.write(_('Born   : %s, age: %s\n\n') % (ident['dob'].strftime('%Y-%m-%d'), ident.get_medical_age()))
		target.write(u'.-%10.10s---%9.9s-------%72.72s\n' % (u'-' * 10, u'-' * 9, u'-' * self.__part_len))
		target.write(u'| %10.10s | %9.9s |   | %s\n' % (_('Date'), _('Doc'), _('Narrative')))
		target.write(u'|-%10.10s---%9.9s-------%72.72s\n' % (u'-' * 10, u'-' * 9, u'-' * self.__part_len))
		# get data
		cmd = u"""
select
	to_char(vemrj.clin_when, 'YYYY-MM-DD') as date,
	vemrj.*,
	(select rank from clin.soap_cat_ranks where soap_cat=vemrj.soap_cat) as scr
from clin.v_emr_journal vemrj
where pk_patient=%s order by date, pk_episode, scr"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [patient['ID']]}], get_col_idx = True)
		# write data
		prev_date = u''
		prev_doc = u''
		for row in rows:
			# narrative
			if row[idx['narrative']] is None:
				continue
			txt = row[idx['narrative']].replace(u'\n', u' ').replace(u'\r', u' ')
			no_parts = (len(txt) / self.__part_len) + 1
			# doc
			curr_doc = row[idx['modified_by']]
			if curr_doc != prev_doc:
				prev_doc = curr_doc
			else:
				curr_doc = u''
			# date
			curr_date = row[idx['date']]
			if curr_date != prev_date:
				prev_date = curr_date
				curr_doc = row[idx['modified_by']]
			else:
				curr_date = u''
			# display first part
			target.write(u'| %10.10s | %9.9s | %s | %s\n' % (
				curr_date,
				curr_doc,
				self.__tx_soap[row[idx['soap_cat']]],
				txt[0:self.__part_len]
			))
			# more parts ?
			if no_parts == 1:
				continue
			template = u'| %10.10s | %9.9s | %s | %s\n'
			for part in range(1, no_parts):
				soap_cat = self.__tx_soap[row[idx['soap_cat']]]
				msg = txt[(part * self.__part_len):((part+1) * self.__part_len)]
				line = template % (u'', u'', soap_cat, msg)
				target.write(line)
		# write footer
		target.write(u'`-%10.10s---%9.9s-------%72.72s\n\n' % (u'-' * 10, u'-' * 9, u'-' * self.__part_len))
		target.write(_('Exported: %s\n') % pyDT.datetime.now().strftime('%c'))

		return
#============================================================
class cMedistarSOAPExporter:
	"""Export SOAP data per encounter into Medistar import format."""
	def __init__(self, patient=None):
		if patient is None:
			self.__pat = gmPerson.gmCurrentPatient()
		else:
			if not isinstance(patient, gmPerson.cPerson):
				raise gmExceptions.ConstructorError, '<patient> argument must be instance of <cPerson>, but is: %s' % type(gmPerson.cPerson)
			self.__pat = patient
		self.__tx_soap = {
			's': 'A',
			'o': 'B',
			'a': 'D',
			'p': 'T'
		}
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def export_to_file(self, filename=None):
		if not self.__pat.is_connected():
			return (False, 'no active patient')
		if filename is None:
			ident = self.__pat.get_identity()
			path = os.path.abspath(os.path.expanduser('~/gnumed/export'))
			filename = '%s-%s-%s-%s-%s.txt' % (
				os.path.join(path, 'Medistar-MD'),
				time.strftime('%Y-%m-%d',time.localtime()),
				ident['lastnames'].replace(' ', '-'),
				ident['firstnames'].replace(' ', '_'),
				ident['dob'].strftime('%Y-%m-%d')
			)
		f = codecs.open(filename = filename, mode = 'w+b', encoding = 'utf8')
		status = self.__export(target = f)
		f.close()
		return (status, filename)
	#--------------------------------------------------------
	def export(self, target):
		return self.__export(target)
	#--------------------------------------------------------
	# interal API
	#--------------------------------------------------------
	def __export(self, target = None, encounter = None):
		if not self.__pat.is_connected():
			return False
		emr = self.__pat.get_emr()
		if encounter is None:
			encounter = emr.get_active_encounter()
		# get data
		cmd = u"select narrative from clin.v_emr_journal where pk_patient=%s and pk_encounter=%s and soap_cat=%s"
		for soap_cat in 'soap':
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': (self.__pat['ID'], encounter['pk_encounter'], soap_cat)}])
			target.write('*MD%s*\n' % self.__tx_soap[soap_cat])
			for row in rows:
				text = row[0]
				if text is not None:
					target.write('%s\n' % gmTools.wrap(text, 64))
		return True
#============================================================
# main
#------------------------------------------------------------
def usage():
    """
        Prints application usage options to stdout.
    """
    print 'usage: python gmPatientExporter [--fileout=<outputfilename>] [--conf-file=<file>] [--text-domain=<textdomain>]'
    sys.exit(0)
#------------------------------------------------------------
def parse_constraints():
    """
        Obtains, parses and normalizes config file options
    """
    if isinstance(_cfg, gmNull.cNull):
        usage()

    # Retrieve options
    cfg_group = 'constraints'
    constraints = {
        'since': _cfg.get(cfg_group, 'since'),
        'until': _cfg.get(cfg_group, 'until'),
        'encounters': _cfg.get(cfg_group, 'encounters'),
        'episodes': _cfg.get(cfg_group, 'episodes'),
        'issues': _cfg.get(cfg_group, 'issues')
    }

    # Normalize null constraints (None is interpreted as non existing constraint along all methods)
    for a_constraint in constraints.keys():
        if len(constraints[a_constraint]) == 0:
            constraints[a_constraint] = None

    # Cast existing constraints to correct type
    if not constraints['since'] is None:
        constraints['since'] = mxParser.DateFromString(constraints['since'], formats= ['iso'])
    if not constraints['until'] is None:
        constraints['until'] = mxParser.DateFromString(constraints['until'], formats= ['iso'])
    if not constraints['encounters'] is None:
        constraints['encounters'] = map(lambda encounter: int(encounter), constraints['encounters'])
    if not constraints['episodes'] is None:
        constraints['episodes'] = map(lambda episode: int(episode), constraints['episodes'])
    if not constraints['issues'] is None:
        constraints['issues'] = map(lambda issue: int(issue), constraints['issues'])
    return constraints
#------------------------------------------------------------                 
def run():
    """
        Main module application execution loop.
    """
    # Check that output file name is defined and create an instance of exporter
#    if gmCLI.has_arg('--fileout'):
#        outFile = open(gmCLI.arg['--fileout'], 'wb')
#    else:
#        usage()
#    export_tool = cEmrExport(parse_constraints(), outFile)

#    export_tool.get_episode_summary()

    # More variable initializations
    patient = None
    patient_id = None
    patient_term = None
    pat_searcher = gmPerson.cPatientSearcher_SQL()

    # App execution loop
    while patient_term != 'bye':
        patient = gmPerson.ask_for_patient()
        if patient is None:
            break
        # FIXME: needed ?
#        gmPerson.set_active_patient(patient=patient)
        exporter = cEMRJournalExporter()
        exporter.export_to_file(patient=patient)
#        export_tool.set_patient(patient)
        # Dump patient EMR sections
#        export_tool.dump_constraints()
#        export_tool.dump_demographic_record(True)
#        export_tool.dump_clinical_record()
#        export_tool.dump_med_docs()

    # Clean ups
#    outFile.close()
#    export_tool.cleanup()
    if patient is not None:
        try:
            patient.cleanup()
        except:
            print "error cleaning up patient"
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":
	gmI18N.activate_locale()
	gmI18N.install_domain()

	gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)

	#--------------------------------------------------------
	def export_journal():

		print "Exporting EMR journal(s) ..."
		pat_searcher = gmPerson.cPatientSearcher_SQL()
		while True:
			patient = gmPerson.ask_for_patient()
			if patient is None:
				break

			exporter = cEMRJournalExporter()
			print "exported into file:", exporter.export_to_file(patient=patient)

			if patient is not None:
				try:
					patient.cleanup()
				except:
					print "error cleaning up patient"
		print "Done."
	#--------------------------------------------------------
	print "\n\nGNUmed ASCII EMR Export"
	print     "======================="

	if gmCLI.has_arg('--help'):
		usage()

	# run main loop
	export_journal()

#============================================================
# $Log: gmPatientExporter.py,v $
# Revision 1.97  2007-02-10 23:41:38  ncq
# - fix loading of GNUmed python modules
# - cleaned up journal exporter
# - fixed bug in journal exporter where it expected is_connected()
#   in non-gmCurrentPatient-using context, too
# - when run standalone: export journal
#
# Revision 1.96  2007/01/18 22:03:58  ncq
# - a bit of cleanup
#
# Revision 1.95  2007/01/15 20:20:03  ncq
# - move wrap() to gmTools
#
# Revision 1.94  2007/01/13 22:17:40  ncq
# - wrap narrative to 75 characters per line
#
# Revision 1.93  2006/12/13 00:31:24  ncq
# - export into unicode files
# - fix use of get_encounters()
#
# Revision 1.92  2006/11/26 15:44:34  ncq
# - strftime() does not accept u''
#
# Revision 1.91  2006/11/24 14:16:20  ncq
# - unicode-robustify dump_item_fields()
#
# Revision 1.90  2006/11/19 11:05:38  ncq
# - cleanup
#
# Revision 1.89  2006/11/09 17:48:05  ncq
# - ever more careful handling of NULLs
#
# Revision 1.88  2006/11/07 00:25:19  ncq
# - make journal exporter emit strictly u''
#
# Revision 1.87  2006/11/05 17:54:17  ncq
# - don't use issue pk in get_encounters()
# - gmPG -> gmPG2
#
# Revision 1.86  2006/11/05 17:02:54  ncq
# - comment out lab results access, not in use yet
#
# Revision 1.85  2006/10/25 07:46:44  ncq
# - Format() -> strftime() since datetime.datetime does not have .Format()
#
# Revision 1.84  2006/10/25 07:18:12  ncq
# - no more gmPG
#
# Revision 1.83  2006/10/23 13:21:50  ncq
# - vaccs/path lab not yet converted to gmPG2
#
# Revision 1.82  2006/09/03 14:46:26  ncq
# - robustify regarding encoding issues
# - improve test suite
#
# Revision 1.81  2006/07/19 20:25:48  ncq
# - gmPyCompat.py is history
#
# Revision 1.80  2006/06/09 14:39:23  ncq
# - comment out vaccination handling for now
#
# Revision 1.79  2006/05/30 13:36:35  ncq
# - properly use get_encounters()
#
# Revision 1.78  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.77  2006/02/27 22:38:36  ncq
# - spell out rfe/aoe as per Richard's request
#
# Revision 1.76  2005/12/25 13:24:30  sjtan
#
# schema changes in names .
#
# Revision 1.75  2005/12/10 23:02:05  ncq
# - tables are in clin.* now
#
# Revision 1.74  2005/10/30 15:48:56  ncq
# - slightly enlarge space for provider signum display
#
# Revision 1.73  2005/10/19 09:06:39  ncq
# - resolve merge conflict: just whitespace diff
#
# Revision 1.72  2005/10/18 13:34:01  sjtan
# after running; small diffs
#
# Revision 1.71  2005/10/15 18:16:24  ncq
# - encounter['description'] is gone, use 'aoe'
#
# Revision 1.70  2005/10/11 21:51:07  ncq
# - rfe/aoe handling changes so adapt to that
#
# Revision 1.69  2005/10/08 12:33:09  sjtan
# tree can be updated now without refetching entire cache; done by passing emr object to create_xxxx methods and calling emr.update_cache(key,obj);refresh_historical_tree non-destructively checks for changes and removes removed nodes and adds them if cache mismatch.
#
# Revision 1.68  2005/10/04 19:22:37  sjtan
# allow a refetch of part of the cache, so that don't have to completely collapse tree view to view after change.
#
# Revision 1.67  2005/10/04 00:04:45  sjtan
# convert to wx.; catch some transitional errors temporarily
#
# Revision 1.66  2005/10/03 13:49:21  sjtan
# using new wx. temporary debugging to stdout(easier to read). where is rfe ?
#
# Revision 1.65  2005/09/11 17:28:20  ncq
# - tree widget now display provider sign, not database account
#
# Revision 1.64  2005/09/09 13:50:07  ncq
# - detail improvements in tree widget progress note output
#
# Revision 1.63  2005/09/08 16:57:06  ncq
# - improve progress note display in tree widget
#
# Revision 1.62  2005/09/05 15:56:27  ncq
# - sort journal by episode within encounters
#
# Revision 1.61  2005/09/04 07:28:51  ncq
# - better naming of dummy health issue for unassociated episodes
# - display time of entry in front of SOAP notes
#
# Revision 1.60  2005/07/04 11:14:36  ncq
# - improved episode summary yet again
#
# Revision 1.59  2005/07/02 18:18:26  ncq
# - improve EMR tree right side info pane according to user
#   testing and ideas gleaned from TransHIS
#
# Revision 1.58  2005/06/30 16:11:55  cfmoro
# Bug fix: multiple episode w/o issue when refreshing tree
#
# Revision 1.57  2005/06/30 11:42:05  cfmoro
# Removed debug print
#
# Revision 1.56  2005/06/30 11:30:10  cfmoro
# Minor fix on issue info when no encounters attached
#
# Revision 1.55  2005/06/20 13:03:38  cfmoro
# Relink encounter to another episode
#
# Revision 1.54  2005/06/12 22:09:39  ncq
# - better encounter formatting yet
#
# Revision 1.53  2005/06/07 09:04:45  ncq
# - cleanup, better encounter data display
#
# Revision 1.52  2005/05/17 18:11:41  ncq
# - dob2medical_age is in gmPerson
#
# Revision 1.51  2005/05/12 15:08:31  ncq
# - add Medistar SOAP exporter and wrap(text, width) convenience function
#
# Revision 1.50  2005/04/27 19:59:19  ncq
# - deal with narrative rows that are empty
#
# Revision 1.49  2005/04/12 16:15:36  ncq
# - improve journal style exporter
#
# Revision 1.48  2005/04/12 10:00:19  ncq
# - add cEMRJournalExporter class
#
# Revision 1.47  2005/04/03 20:08:18  ncq
# - GUI stuff does not belong here (eg move to gmEMRBrowser which is to become gmEMRWidgets, eventually)
#
# Revision 1.46  2005/04/03 09:27:25  ncq
# - better wording
#
# Revision 1.45  2005/04/02 21:37:27  cfmoro
# Unlinked episodes displayes in EMR tree and dump
#
# Revision 1.44  2005/04/02 20:45:12  cfmoro
# Implementated  exporting emr from gui client
#
# Revision 1.43  2005/03/30 21:14:31  cfmoro
# Using cIdentity recent changes
#
# Revision 1.42  2005/03/29 07:24:07  ncq
# - tabify
#
# Revision 1.41     2005/03/20 17:48:38  ncq
# - add two sanity checks by Syan
#
# Revision 1.40     2005/02/20 08:32:51  sjtan
#
# indentation syntax error.
#
# Revision 1.39     2005/02/03 20:19:16  ncq
# - get_demographic_record() -> get_identity()
#
# Revision 1.38     2005/01/31 13:01:23  ncq
# - use ask_for_patient() in gmPerson
#
# Revision 1.37     2005/01/31 10:19:11  ncq
# - gmPatient -> gmPerson
#
# Revision 1.36     2004/10/26 12:52:56  ncq
# - Carlos: fix conceptual bug by building top-down (eg. issue -> episode
#    -> item) instead of bottom-up
#
# Revision 1.35     2004/10/20 21:43:45  ncq
# - cleanup
# - use allergy['descriptor']
# - Format() dates
#
# Revision 1.34     2004/10/20 11:14:55  sjtan
# restored import for unix. get_historical_tree may of changed, but mainly should
# be guards in gmClinicalRecord for changing [] to None when functions expecting None, and client
# functions passing [].
#
# Revision 1.33     2004/10/12 10:52:40  ncq
# - improve vaccinations handling
#
# Revision 1.32     2004/10/11 19:53:41  ncq
# - document classes are now VOs
#
# Revision 1.31     2004/09/29 19:13:37  ncq
# - cosmetical fixes as discussed with our office staff
#
# Revision 1.30     2004/09/29 10:12:50  ncq
# - Carlos added intuitive vaccination table - muchos improvos !
#
# Revision 1.29     2004/09/10 10:39:01  ncq
# - fixed assignment that needs to be comparison == in lambda form
#
# Revision 1.28     2004/09/06 18:55:09  ncq
# - a bunch of cleanups re get_historical_tree()
#
# Revision 1.27     2004/09/01 21:59:01  ncq
# - python classes can only have one single __init__
# - add in Carlos' code for displaying episode/issue summaries
#
# Revision 1.26     2004/08/23 09:08:53  ncq
# - improve output
#
# Revision 1.25     2004/08/11 09:45:28  ncq
# - format SOAP notes, too
#
# Revision 1.24     2004/08/09 18:41:08  ncq
# - improved ASCII dump
#
# Revision 1.23     2004/07/26 00:02:30  ncq
# - Carlos introduces export of RFE/AOE and dynamic layouting (left margin)
#
# Revision 1.22     2004/07/18 10:46:30  ncq
# - lots of cleanup by Carlos
#
# Revision 1.21     2004/07/09 22:39:40  ncq
# - write to file like object passed to __init__
#
# Revision 1.20     2004/07/06 00:26:06  ncq
# - fail on _cfg is_instance of cNull(), not on missing conf-file option
#
# Revision 1.19     2004/07/03 17:15:59  ncq
# - decouple contraint/patient/outfile handling
#
# Revision 1.18     2004/07/02 00:54:04  ncq
# - constraints passing cleanup by Carlos
#
# Revision 1.17     2004/06/30 12:52:36  ncq
# - cleanup
#
# Revision 1.16     2004/06/30 12:43:10  ncq
# - read opts from config file, cleanup
#
# Revision 1.15     2004/06/29 08:16:35  ncq
# - take output file from command line
# - *search* for patients, don't require knowledge of their ID
#
# Revision 1.14     2004/06/28 16:15:56  ncq
# - still more faulty id_ found
#
# Revision 1.13     2004/06/28 15:52:00  ncq
# - some comments
#
# Revision 1.12     2004/06/28 12:18:52  ncq
# - more id_* -> fk_*
#
# Revision 1.11     2004/06/26 23:45:50  ncq
# - cleanup, id_* -> fk/pk_*
#
# Revision 1.10     2004/06/26 06:53:25  ncq
# - id_episode -> pk_episode
# - constrained by date range from Carlos
# - dump documents folder, too, by Carlos
#
# Revision 1.9    2004/06/23 22:06:48     ncq
# - cleaner error handling
# - fit for further work by Carlos on UI interface/dumping to file
# - nice stuff !
#
# Revision 1.8    2004/06/20 18:50:53     ncq
# - some exception catching, needs more cleanup
#
# Revision 1.7    2004/06/20 18:35:07     ncq
# - more work from Carlos
#
# Revision 1.6    2004/05/12 14:34:41     ncq
# - now displays nice vaccination tables
# - work by Carlos Moro
#
# Revision 1.5    2004/04/27 18:54:54     ncq
# - adapt to gmClinicalRecord
#
# Revision 1.4    2004/04/24 13:35:33     ncq
# - vacc table update
#
# Revision 1.3    2004/04/24 12:57:30     ncq
# - stop db listeners on exit
#
# Revision 1.2    2004/04/20 13:00:22     ncq
# - recent changes by Carlos to use VO API
#
# Revision 1.1    2004/03/25 23:10:02     ncq
# - gmEmrExport -> gmPatientExporter by Carlos' suggestion
#
# Revision 1.2    2004/03/25 09:53:30     ncq
# - added log keyword
#
