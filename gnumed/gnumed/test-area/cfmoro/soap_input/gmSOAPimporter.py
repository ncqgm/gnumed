"""GnuMed SOAP importer (specification by Karsten Hilbert <Karsten.Hilbert@gmx.net>)

This script is designed for importing GnuMed SOAP input "bundle". 

    - "bundle" is list of dicts. Each "bundle" is processed one by one. The dicts
      in the list are INDEPENDANT of each other, so every dict is then taken apart
      
    - each bundle contain information for:
        - a new clin_narrative row 
        - optionally, additionally data, marked by keys "embedded" into the
          text of the narrative that are looked up, parsed out and appropiately
          imported  depending on its 'type' using the business classes.
        - additional data that does not have a key is alerted to the
          user. The same is done for keys in the text that have no entry in the
          additional data. The most likely reason for this to happen is the user
          manually editing the [:...:] embedded strings in 'text' while still
          in the soap input widget.
      
    - each dict has the keys: 'soap', 'types', 'text', 'data'
        - 'soap':            
            - relates to clin_narrative.soap_cat
        - 'types':
            - a list of strings
            - the strings must be found in clin_item_type.type
            - strings not found in clin_item_type.type are ignored during
              import and the user is warned about that
        -'text':
            - the narrative for clin_narrative.narrative, imported as is
            - substrings of the form [:...:] are remembered

        -'data':
            - this is a dictionary with additional data
            - the keys to this dictionary are the "..." parts of the [:...:]
              found in 'text' (see above)
            - the values will be dicts themselves with the keys
              'type' and 'data':
                - 'type': the type of 'data' such as 'allergy', 'vaccination',
                  set by the popup widgets inside gmSoapInput
            - 'data' is a dict of fields depending on 'type'
"""
#===============================================================
__version__ = "$Revision: 1.2 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = "GPL, details at http://www.gnu.org"

# stdlib
import sys, re

from Gnumed.pycommon import gmLog, gmCLI
if __name__ == '__main__':
    if gmCLI.has_arg('--debug'):
        gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)
    else:
        gmLog.gmDefLog.SetAllLogLevels(gmLog.lInfo)

from Gnumed.pycommon import gmCfg, gmPG, gmLoginInfo, gmExceptions, gmI18N
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.business import gmClinNarrative, gmPatient, gmVaccination

import mx.DateTime as mxDT

_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile
#===============================================================
class cSOAPImporter:
    """
    Main SOAP importer class
    """
    
    #-----------------------------------------------------------
    def __init__(self):
                        
        self._pat = gmPatient.gmCurrentPatient()
            
    #-----------------------------------------------------------
    def import_soap(self, bundle=None):
        """
        Import supplied GnuMed SOAP input "bundle". For details consult current
        module's description information.
        
        @param bundle: GnuMed SOAP input data (as described in module's information)
        @type bundle: list of dicts
        """
        
        # verify bundle
        if bundle is None or len(bundle) == 0:
            _log.Log(gmLog.lErr, 'cannot import supplied SOAP bundle: [%s]' % bundle)
            return False        
                    
        # keys in the text that have no entry in the additional data
        empty_keys = []
        # additional data that does not have a key
        lonely_data = []        
        
        # process each entry in soap bundle indepently
        for soap_entry in bundle:
            # verify clin_narrative row fields
            if not self._verify_soap_entry(soap_entry):
                _log.Log(gmLog.lErr, 'cannot import soap entry [%s]' % soap_entry)
                continue
            _log.Log(gmLog.lInfo, "soap entry verified OK: [%s]" % soap_entry)
            # create new clin_narrative row
            self._dump_soap(soap_entry)
            # verify additional embedded data
            entry_keys = self._verify_embedded_data(soap_entry)
            # cache empty keys and lonely data keys for user warning
            if len(entry_keys['empty_keys']) > 0:
            	empty_keys.extend(entry_keys['empty_keys'])
            if len(entry_keys['lonely_data']) > 0:
            	lonely_data.extend(entry_keys['empty_keys'])
            # dump parsed out additional embedded data
            self._dump_additional_data(soap_entry, entry_keys)
            
        if len(empty_keys) > 0:
            _log.Log(gmLog.lInfo, "can not dump empty keys [%s] in soap bundle [%s]" % (empty_keys, bundle))
        if len(lonely_data) > 0:
            _log.Log(gmLog.lInfo, "can not dump lonely data [%s] in soap bundle [%s]" % (lonely_data, bundle))                            
            
    #-----------------------------------------------------------
    # internal helpers
    #-----------------------------------------------------------
    def _dump_additional_data(self, soap_entry, entry_keys):
        """
        Dump valid key's embedded additional data to backend.
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'        
        
        @param entry_keys: dictionary of keys parsed from soap entry, with keys:
        	                   .text_keys: soap entry text parsed out keys
        	                   .empty_keys: soap entry text parsed out keys that
        	                                are missing from data dictionary
        	                                key set
        	                   .lonely_data: data dictionary keys missing from
        	                                 soap entry text parsed out keys
        	                   
        @type empty_keys: type dict
        """

        # FIXME unify
        # obtain active encounter and episode
        emr = self._pat.get_clinical_record()
        active_encounter = emr.get_active_encounter()
        active_episode = emr.get_active_episode()

        # extract useful key lists
        text_keys = entry_keys['text_keys']
        empty_keys = entry_keys['empty_keys']
        
        # embedded data clinical item type
        type = ''        
        # embedded data clinical item values
        data = {}        
        
        # walk through text keys scaping the empty ones and creating additional
        # clinical items
        for text_key in text_keys:
        	if text_key in empty_keys:
        		continue
        	type = soap_entry['data'][text_key]['type']
        	data = soap_entry['data'][text_key]['data']
        	if type == 'vaccination':
        		#gmVaccination.createVaccination(patient_id= self._pat.GetID(),
        		#episode_id=active_episode['pk_episode'], encounter_id=active_encounter['pk_encounter'],
        		#staff_id=data['staff_id'], vaccine=data['vaccine'])
        		print "Creating vaccination: [%s]" % data
        	else:
        		_log.Log(gmLog.lErr, 'cannot create clinical item of unknown type [%s] for soap entry [%s]' % (type,soap_entry))
        	               
    #-----------------------------------------------------------
    def _parse_embedded_keys(self, soap_entry):
        """
        Parse out and extract embedded keys for additional data contained in
        narrative text. Embedded keys are the '....' in the pattern [:....:]
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'        
        """

        # parse out embedded keys as are
        txt = soap_entry['text']    
        # key pattern: any string between [: and :]. Any of chars in '[:]'
        # are forbidden in the key string
        key_pattern = "\[:.[^:\[\]]*:\]"
        embedded_keys = re.findall(key_pattern, txt)
        print embedded_keys
        # clean pattern from embedded keys
        embedded_keys = map(lambda key: key.replace("[:","").replace(":]",""), embedded_keys)
        _log.Log(gmLog.lInfo, "parsed out embedded keys [%s] from soap entry text[%s]" % (embedded_keys, soap_entry['text']))
        
        return embedded_keys
                
    #-----------------------------------------------------------
    def _verify_embedded_data(self, soap_entry):
        """
        Perform integrity check of additional embedded data supplied in
        the SOAP entry
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'        
        """

        # keys in the text that have no entry in the additional data
        empty_keys = []
        # additional data that does not have a key
        lonely_data = []
        
        # keys embedded in text
        text_keys = self._parse_embedded_keys(soap_entry)
        # additional data
        data = soap_entry['data']
                
        # check empty keys
        for a_key in text_keys:
        	if a_key not in data.keys():
        		empty_keys.append(a_key)
        
        # check lonely data
        for a_key in data.keys():
        	if a_key not in text_keys:
        		lonely_data.append(a_key)        
            
        if len(text_keys) > 0:
        	print "text_keys: %s" % text_keys
        	print "empty_keys: %s" % empty_keys
        	print "lonely_data: %s" % lonely_data
        return {'text_keys':text_keys, 'empty_keys':empty_keys, 'lonely_data':lonely_data}
        
    #-----------------------------------------------------------    
    def _dump_soap(self, soap_entry):
        """
        Dump soap entry to GnuMed backend
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'        
        """

        # FIXME unify
        # obtain active encounter and episode
        emr = self._pat.get_clinical_record()
        active_encounter = emr.get_active_encounter()
        active_episode = emr.get_active_episode()
        
        # create narrative row
        #stat, narr = gmClinNarrative.create_clin_narrative(narrative = soap_entry['text'],
        #soap_cat = soap_entry['soap'], episode_id= active_episode['pk_episode'], encounter_id=active_encounter['pk_encounter'])
        print "Created soap row: %s - %s" % (soap_entry['text'], soap_entry['soap'])
        stat = True
        
        return stat
        	
    #-----------------------------------------------------------        
    def _verify_soap_entry(self, soap_entry):
        """
        Perform basic integrity check of a supplied SOAP entry
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'
        """
        
        must_keys = ['soap', 'types', 'text', 'data']
        
        # verify soap entry contains all must have keys
        for a_must_key in must_keys:
            if not soap_entry.has_key(a_must_key):
                _log.Log(gmLog.lErr, 'soap entry [%s] has not key [%s]' %
                (soap_entry, a_must_key))
                return False
        
        # verify basic key's values indepently
        result = True
        tmp = self._verify_soap(soap_entry)
        if not tmp:
            result = False
        tmp = self._verify_types(soap_entry)
        if not tmp:
            result = False
        tmp = self._verify_text(soap_entry)
        if not tmp:
            result = False
             
        return result

    #-----------------------------------------------------------
    def _verify_soap(self, soap_entry):
        """
        Perform soap key check of a supplied SOAP entry
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'
        """
        
        # FIXME fetch from backend
        soap_cats = ['s','o','a','p']
        if not soap_entry['soap'] in soap_cats:
            _log.Log(gmLog.lErr, 'bad clin_narrative.soap_cat in supplied soap entry [%s]' % 
            soap_entry)
            return False
        return True

    #-----------------------------------------------------------
    def _verify_types(self, soap_entry):
        """
        Perform types key check of a supplied SOAP entry
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'
        """
        
        # FIXME fetch from backend
        allowed_types = ['Hx']
        for input_type in soap_entry['types']:
            if not input_type in allowed_types:
                _log.Log(gmLog.lErr, 'bad clin_item_type.type in supplied soap entry [%s]' % 
                soap_entry)
                return False
        return True
        
    #-----------------------------------------------------------
    def _verify_text(self, soap_entry):
        """
        Perform text check of a supplied SOAP entry
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'
        """
                
        text = soap_entry['text']
        if text is None or len(text) == 0:
            _log.Log(gmLog.lErr, 'empty clin_narrative.narrative in supplied soap entry [%s]' % 
                soap_entry)
            return False
        return True
                
    #-----------------------------------------------------------
    def _verify_data(self, soap_entry):
        """
        Perform additional data check of a supplied SOAP entry
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'
        """
                
        # FIXME pending
        pass
    
#== Module convenience functions (for standalone use) =======================
def prompted_input(prompt, default=None):
    """
    Obtains entry from standard input
    
    promp - Promt text to display in standard output
    default - Default value (for user to press only intro)
    """
    usr_input = raw_input(prompt)
    if usr_input == '':
        return default
    return usr_input
    
#------------------------------------------------------------                 
def askForPatient():
    """
        Main module application patient selection function.
    """
    
    # Variable initializations
    pat_searcher = gmPatient.cPatientSearcher_SQL()

    # Ask patient
    patient_term = prompted_input("\nPatient search term (or 'bye' to exit) (eg. Kirk): ")
    
    if patient_term == 'bye':
        return None
    search_ids = pat_searcher.get_patient_ids(search_term = patient_term)
    if search_ids is None or len(search_ids) == 0:
        prompted_input("No patient matches the query term. Press any key to continue.")
        return None
    elif len(search_ids) > 1:
        prompted_input("Various patients match the query term. Press any key to continue.")
        return None
    patient_id = search_ids[0]
    patient = gmPatient.gmCurrentPatient(patient_id)
    
    return patient
    
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
    
    from Gnumed.pycommon import gmCfg

    _log.SetAllLogLevels(gmLog.lData)
    _log.Log (gmLog.lInfo, "starting SOAP importer...")

    _cfg = gmCfg.gmDefCfgFile     
    if _cfg is None:
        _log.Log(gmLog.lErr, "Cannot run without config file.")
        sys.exit("Cannot run without config file.")

    try:
        # make sure we have a db connection
        gmPG.set_default_client_encoding('latin1')
        pool = gmPG.ConnectionPool()
        
        # obtain patient
        patient = askForPatient()
        if patient is None:
            print "No patient. Exiting gracefully..."
            sys.exit(0)

        # now import
        importer = cSOAPImporter()
        bundle = [
            {'soap':'s',
             'types':['Hx'],
             'text':'Test subjective narrarive',
             'data': {}
            },
            {'soap':'o',
             'types':['Hx'],
             'text':'Test objective narrative',
             'data': {}
            },
            {'soap':'a',
             'types':['Hx'],
             'text':'Test assesment narrative',
             'data': {}
            },
            {'soap':'p',
             'types':['Hx'],
             'text':'Test plan narrarive. [:tetanus:]. [:pneumoniae:]',
             'data': {'tetanus': {
                                         'type':'vaccination',
                                         'data': {
                                                     'vaccine':'tetanus',
                                                     'staff_id':'1'
                                     }           },
                      'pneumoniae': {
                                         'type':'vaccination',
                                         'data': {
                                                     'vaccine':'pneumoniae',
                                                     'staff_id':'1'
                                     }           }
                     }
            }                                    
        ]
        importer.import_soap(bundle)
        
        # clean up
        if patient is not None:
            try:
                patient.cleanup()
            except:
                print "error cleaning up patient"
    except StandardError:
        _log.LogException("unhandled exception caught !", sys.exc_info(), 1)
        # but re-raise them
        raise
    try:
        pool.StopListeners()
    except:
        _log.LogException('unhandled exception caught', sys.exc_info(), verbose=1)
        raise

    _log.Log (gmLog.lInfo, "closing SOAP importer...")
    